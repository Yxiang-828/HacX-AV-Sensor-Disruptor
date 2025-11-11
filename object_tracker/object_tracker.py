import cv2
import numpy as np
import serial
import time

# Initialize Arduino serial connection
try:
    arduino = serial.Serial('COM9', 9600, timeout=1)
    time.sleep(2)
    print("✓ Connected to Arduino on COM9")
except:
    print("ERROR: Could not connect to Arduino. Check COM port!")
    #exit()

TILT_MIN, TILT_MAX = 0, 180
PAN_MIN, PAN_MAX = 0, 180
prev_tilt, prev_pan = 90, 90
smooth_factor = 0.3

def map_range(value, in_min, in_max, out_min, out_max):
    value = max(in_min, min(in_max, value))
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def smooth_angle(current, target, factor):
    return int(current + (target - current) * factor)

def send_servo_command(tilt, pan):
    command = f"T{tilt}P{pan}\n"
    arduino.write(command.encode())

# Tracking & Kalman settings
cap = cv2.VideoCapture(0)
cv2.namedWindow('Camera')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

tracking = False
tracker = None
bbox = None

kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.eye(2,4, dtype=np.float32)
kalman.transitionMatrix = np.array([[1,0,1,0],
                                   [0,1,0,1],
                                   [0,0,1,0],
                                   [0,0,0,1]], dtype=np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.10
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1.5

def mouse_handler(event, x, y, flags, param):
    global bbox, tracking, tracker
    if event == cv2.EVENT_LBUTTONDOWN:
        w, h = 80, 80
        bbox = (x - w//2, y - h//2, w, h)
        tracking = True
        tracker = cv2.legacy.TrackerCSRT.create()
        ret, frame = cap.read()
        if ret:
            tracker.init(frame, bbox)
        kalman.statePre = np.array([[x], [y], [0], [0]], dtype=np.float32)
        kalman.statePost = np.array([[x], [y], [0], [0]], dtype=np.float32)

cv2.setMouseCallback('Camera', mouse_handler)

print("\n=== Object Tracking Servo Control: CSRT + Kalman ===")
print("1. Click to select the object to track (a yellow box will appear)")
print("2. Servos will follow the Kalman-predicted position")
print("3. Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret: break
    h, w, c = frame.shape

    if tracking and bbox and tracker:
        ok, bbox = tracker.update(frame)
        if ok:
            x, y, bw, bh = [int(v) for v in bbox]
            cx, cy = x + bw//2, y + bh//2
            measurement = np.array([[cx], [cy]], dtype=np.float32)
            kalman.correct(measurement)
            prediction = kalman.predict()
            pred_x, pred_y = int(prediction[0]), int(prediction[1])
            x_show, y_show = pred_x - bw//2, pred_y - bh//2
            # Draw Kalman-predicted rectangle
            cv2.rectangle(frame, (x_show, y_show), (x_show + bw, y_show + bh), (0, 255, 255), 2)
            # Draw predicted center
            cv2.circle(frame, (pred_x, pred_y), 6, (0,255,255), -1)
            # Map predicted position to servo angles
            target_pan = map_range(pred_x, 0, w, PAN_MIN, PAN_MAX)
            target_tilt = map_range(pred_y, 0, h, TILT_MAX, TILT_MIN)
            prev_pan = smooth_angle(prev_pan, target_pan, smooth_factor)
            prev_tilt = smooth_angle(prev_tilt, target_tilt, smooth_factor)
            send_servo_command(prev_tilt, prev_pan)
            # Display servo info
            cv2.putText(frame, f"Tilt: {prev_tilt} Pan: {prev_pan}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Tracking ({pred_x}, {pred_y})", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            tracking = False
            tracker = None
            bbox = None
            cv2.putText(frame, "LOST TARGET - Click on new location", (10, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "Click to select target", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Servos will follow Kalman prediction", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Draw crosshair at center
    cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), (255, 0, 0), 2)
    cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), (255, 0, 0), 2)
    cv2.imshow('Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
print("\nProgram ended (CSRT + Kalman tracking)")


























