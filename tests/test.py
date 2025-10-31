#!/usr/bin/env python3
"""
Laptop Testing Version - Click-to-Track Laser Targeting System
Test on laptop before deploying to Raspberry Pi
"""

from flask import Flask, render_template, Response, request, jsonify
import cv2
import time
import numpy as np
from threading import Thread, Lock
import json

# Configuration - LAPTOP MODE
USE_ARDUINO = False  # Set to True if Arduino is connected
ARDUINO_PORT = 'COM5'  # Windows: COM5, Linux/Mac: /dev/ttyACM0
ARDUINO_BAUD = 9600
CAMERA_INDEX = 0  # Laptop webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Servo limits
TILT_MIN, TILT_MAX = 0, 180
PAN_MIN, PAN_MAX = 0, 180

# Tracking parameters
SMOOTH_FACTOR = 0.3
TRACKER_TYPE = 'CSRT'  # Options: CSRT, KCF, MOSSE, MEDIANFLOW

app = Flask(__name__)

class LaserTracker:
    def __init__(self):
        # Initialize Arduino (optional for testing)
        self.arduino = None
        if USE_ARDUINO:
            try:
                import serial
                self.arduino = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
                time.sleep(2)
                print(f"✓ Connected to Arduino on {ARDUINO_PORT}")
            except Exception as e:
                print(f"⚠ Arduino not connected: {e}")
                print("  Running in SIMULATION mode")
        else:
            print("⚠ Arduino disabled - Running in SIMULATION mode")

        # Initialize camera
        self.camera = cv2.VideoCapture(CAMERA_INDEX)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        # Verify camera opened
        if not self.camera.isOpened():
            print("ERROR: Could not open camera!")
            raise Exception("Camera initialization failed")

        # Tracking state
        self.tracker = None
        self.tracking = False
        self.bbox = None
        self.frame = None
        self.lock = Lock()

        # Servo positions
        self.prev_pan = 90
        self.prev_tilt = 90

        print("✓ Laptop camera initialized")
        print(f"✓ Tracker type: {TRACKER_TYPE}")
        print(f"✓ Resolution: {FRAME_WIDTH}x{FRAME_HEIGHT}")

    def create_tracker(self):
        """Create OpenCV tracker based on type"""
        try:
            if TRACKER_TYPE == 'CSRT':
                return cv2.TrackerCSRT_create()
            elif TRACKER_TYPE == 'KCF':
                return cv2.TrackerKCF_create()
            elif TRACKER_TYPE == 'MOSSE':
                return cv2.TrackerMOSSE_create()
            elif TRACKER_TYPE == 'MEDIANFLOW':
                return cv2.TrackerMedianFlow_create()
            else:
                print(f"Warning: Unknown tracker type {TRACKER_TYPE}, using CSRT")
                return cv2.TrackerCSRT_create()
        except Exception as e:
            print(f"Error creating tracker: {e}")
            return cv2.TrackerCSRT_create()

    def start_tracking(self, x, y, width=80, height=80):
        """Initialize tracking at clicked position"""
        with self.lock:
            if self.frame is None:
                return False

            # Define bounding box around click point
            h, w = self.frame.shape[:2]
            x1 = max(0, x - width//2)
            y1 = max(0, y - height//2)
            x2 = min(w, x + width//2)
            y2 = min(h, y + height//2)

            self.bbox = (x1, y1, x2-x1, y2-y1)

            # Initialize tracker
            self.tracker = self.create_tracker()
            success = self.tracker.init(self.frame, self.bbox)

            if success:
                self.tracking = True
                print(f"✓ Tracking started at ({x}, {y})")
                return True
            else:
                print("✗ Failed to initialize tracker")
                return False

    def stop_tracking(self):
        """Stop tracking"""
        with self.lock:
            self.tracking = False
            self.tracker = None
            self.bbox = None
            print("✓ Tracking stopped")

    def map_range(self, value, in_min, in_max, out_min, out_max):
        """Map value from one range to another"""
        value = max(in_min, min(in_max, value))
        return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def smooth_angle(self, current, target, factor):
        """Smooth servo movement"""
        return int(current + (target - current) * factor)

    def send_servo_command(self, tilt, pan):
        """Send servo angles to Arduino"""
        if self.arduino and self.arduino.is_open:
            try:
                command = f"T{tilt}P{pan}\n"
                self.arduino.write(command.encode())
                print(f"→ Sent: {command.strip()}")
            except Exception as e:
                print(f"Error sending command: {e}")
        else:
            # Simulation mode - just print
            print(f"🎯 SIMULATED: Tilt={tilt}° Pan={pan}°")

    def process_frame(self):
        """Main processing loop for each frame"""
        ret, frame = self.camera.read()
        if not ret:
            return None

        frame = cv2.flip(frame, 1)  # Mirror for intuitive control
        h, w = frame.shape[:2]

        with self.lock:
            self.frame = frame.copy()

            if self.tracking and self.tracker:
                # Update tracker
                success, bbox = self.tracker.update(frame)

                if success:
                    # Draw bounding box
                    x, y, width, height = [int(v) for v in bbox]
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)

                    # Calculate center
                    cx = x + width // 2
                    cy = y + height // 2
                    cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)
                    cv2.circle(frame, (cx, cy), 15, (0, 255, 0), 2)

                    # Draw line from center to target
                    cv2.line(frame, (w//2, h//2), (cx, cy), (0, 255, 0), 2)

                    # Map to servo angles
                    target_pan = self.map_range(cx, 0, w, PAN_MIN, PAN_MAX)
                    target_tilt = self.map_range(cy, 0, h, TILT_MAX, TILT_MIN)

                    # Smooth movement
                    self.prev_pan = self.smooth_angle(self.prev_pan, target_pan, SMOOTH_FACTOR)
                    self.prev_tilt = self.smooth_angle(self.prev_tilt, target_tilt, SMOOTH_FACTOR)

                    # Send to Arduino
                    self.send_servo_command(self.prev_tilt, self.prev_pan)

                    # Display info
                    cv2.putText(frame, f"🎯 TRACKING", (10, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                    cv2.putText(frame, f"Pan: {self.prev_pan}° | Tilt: {self.prev_tilt}°", (10, 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Target: ({cx}, {cy})", (10, 110),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Size: {width}x{height}", (10, 140),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Mode indicator
                    mode_text = "ARDUINO" if self.arduino else "SIMULATION"
                    cv2.putText(frame, mode_text, (w - 180, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    # Tracking failed
                    cv2.putText(frame, "⚠ TRACKING LOST", (10, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                    cv2.putText(frame, "Click to re-track", (10, 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                    self.tracking = False
            else:
                # Not tracking
                cv2.putText(frame, "Click on object to track", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                cv2.putText(frame, "Laptop Camera Mode", (10, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Draw crosshair at center
        cv2.line(frame, (w//2 - 30, h//2), (w//2 + 30, h//2), (255, 0, 0), 2)
        cv2.line(frame, (w//2, h//2 - 30), (w//2, h//2 + 30), (255, 0, 0), 2)
        cv2.circle(frame, (w//2, h//2), 5, (255, 0, 0), -1)

        return frame

    def generate_frames(self):
        """Generator for video streaming"""
        while True:
            frame = self.process_frame()
            if frame is None:
                continue

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def cleanup(self):
        """Release resources"""
        self.camera.release()
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        print("✓ Resources released")

# Global tracker instance
tracker = LaserTracker()

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(tracker.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/click', methods=['POST'])
def handle_click():
    """Handle click events from web interface"""
    data = request.json
    x = int(data.get('x', 0))
    y = int(data.get('y', 0))

    # Start tracking at clicked position
    success = tracker.start_tracking(x, y)

    return jsonify({'success': success, 'x': x, 'y': y})

@app.route('/stop', methods=['POST'])
def stop_tracking():
    """Stop tracking"""
    tracker.stop_tracking()
    return jsonify({'success': True})

@app.route('/center', methods=['POST'])
def center_servos():
    """Center the servos"""
    tracker.send_servo_command(90, 90)
    tracker.prev_pan = 90
    tracker.prev_tilt = 90
    return jsonify({'success': True})

if __name__ == '__main__':
    try:
        print("\n" + "="*50)
        print("🎯 LAPTOP TESTING MODE - Laser Tracker")
        print("="*50)
        print(f"\n📹 Using: Laptop Webcam (Camera {CAMERA_INDEX})")
        print(f"🤖 Arduino: {'CONNECTED' if USE_ARDUINO else 'SIMULATION MODE'}")
        print(f"\n🌐 Access at: http://localhost:5000")
        print(f"   Or from phone: http://<your-laptop-ip>:5000")
        print("\nPress Ctrl+C to stop\n")
        print("="*50 + "\n")

        # Run Flask server
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    finally:
        tracker.cleanup()
        print("✓ Goodbye!")