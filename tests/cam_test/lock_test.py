import cv2
import serial
import time

# Initialize Arduino serial connection
# Change 'COM3' to your Arduino's COM port
try:
    arduino = serial.Serial('COM9', 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print("✓ Connected to Arduino on COM9")
except:
    print("ERROR: Could not connect to Arduino. Check COM port!")
    print("Find your COM port in Arduino IDE under Tools > Port")
    exit()

# Tracking variables
drawing = False
ix, iy = -1, -1
bbox = None
tracker = None
tracking = False
temp_frame = None

# Servo settings
TILT_MIN, TILT_MAX = 0, 180  # Pin 5 - Vertical
PAN_MIN, PAN_MAX = 0, 180    # Pin 6 - Horizontal

# Smoothing
prev_tilt = 90
prev_pan = 90
smooth_factor = 0.3  # Lower = smoother but slower

def map_range(value, in_min, in_max, out_min, out_max):
    """Map value from one range to another"""
    value = max(in_min, min(in_max, value))
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def smooth_angle(current, target, factor):
    """Smooth servo movement"""
    return int(current + (target - current) * factor)

def send_servo_command(tilt, pan):
    """Send command to Arduino in T##P## format"""
    command = f"T{tilt}P{pan}\n"
    arduino.write(command.encode())

def mouse_handler(event, x, y, flags, param):
    global drawing, ix, iy, bbox, tracker, tracking, temp_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        temp_frame = param.copy()

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        frame_copy = temp_frame.copy()
        cv2.rectangle(frame_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.putText(frame_copy, "Release to lock target", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Object Tracking - Servo Control', frame_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x0, y0 = min(ix, x), min(iy, y)
        w, h = abs(x - ix), abs(y - iy)
        if w > 1 and h > 1:
            bbox = (x0, y0, w, h)
            frame_copy = temp_frame.copy()
            cv2.rectangle(frame_copy, (x0, y0), (x0 + w, y0 + h), (0, 255, 0), 2)
            cv2.imshow('Object Tracking - Servo Control', frame_copy)
            tracker = cv2.TrackerMIL_create()
            tracker.init(temp_frame, bbox)
            tracking = True
            print(f'✓ Tracker locked on target at ({x0}, {y0}, {w}, {h})')
        else:
            print("[ERROR] Bounding box too small, select a larger area.")

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

cv2.namedWindow('Object Tracking - Servo Control')

print("\n=== Object Tracking Servo Control ===")
print("1. Draw a box around the object you want to track")
print("2. Servos will follow the tracked object")
print("3. Press 'r' to RESET tracking and select new object")
print("4. Press 'q' to QUIT\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Could not read frame from camera.")
        break

    # Flip frame for mirror effect
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Set mouse callback with current frame
    cv2.setMouseCallback('Object Tracking - Servo Control', mouse_handler, param=frame)

    if tracking and tracker is not None and bbox is not None:
        ok, bbox = tracker.update(frame)
        if ok:
            x, y, w_box, h_box = [int(i) for i in bbox]
            
            # Calculate center of tracked object
            cx = x + w_box // 2
            cy = y + h_box // 2
            
            # Draw tracking box
            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            
            # Map object position to servo angles
            target_pan = map_range(cx, 0, w, PAN_MIN, PAN_MAX)
            target_tilt = map_range(cy, 0, h, TILT_MAX, TILT_MIN)  # Inverted
            
            # Smooth the movement
            prev_pan = smooth_angle(prev_pan, target_pan, smooth_factor)
            prev_tilt = smooth_angle(prev_tilt, target_tilt, smooth_factor)
            
            # Send to Arduino
            send_servo_command(prev_tilt, prev_pan)
            
            # Display tracking info
            cv2.putText(frame, f"Tilt: {prev_tilt}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Pan: {prev_pan}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Tracking at ({cx}, {cy})", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, "LOCKED ON TARGET", (10, h - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            tracking = False
            tracker = None
            bbox = None
            print("[INFO] Lost track of object. Draw a new box to retrack.")
            cv2.putText(frame, "LOST TARGET - Draw new box", (10, h - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        # Not tracking - show instructions
        cv2.putText(frame, "CLICK and DRAG to select target", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Servos will follow the tracked object", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Draw crosshair at center
    cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), (255, 0, 0), 2)
    cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), (255, 0, 0), 2)
    
    # Instructions
    cv2.putText(frame, "r=Reset | q=Quit", (10, h - 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Object Tracking - Servo Control', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        tracking = False
        tracker = None
        bbox = None
        print("Tracking reset. Select a new target.")

# Cleanup
cap.release()
cv2.destroyAllWindows()
arduino.close()
print("\nProgram ended")