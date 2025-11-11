import cv2
import numpy as np
import urllib.request
import serial
import time

url = 'http://172.20.10.3:8000/stream.mjpg'  # Picamera2 MJPEG server endpoint

# ---- Arduino setup ----
try:
    arduino = serial.Serial('COM9', 9600, timeout=1)  # Edit port for Windows/Linux as needed
    time.sleep(2)
    print("✓ Connected to Arduino.")
except:
    print("ERROR: Could not connect to Arduino. Check COM port!")
    arduino = None

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
    if arduino:
        command = f"T{tilt}P{pan}\n"
        arduino.write(command.encode())

cv2.namedWindow('Camera')
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
        if param is not None:
            tracker.init(param, bbox)
        kalman.statePre = np.array([[x], [y], [0], [0]], dtype=np.float32)
        kalman.statePost = np.array([[x], [y], [0], [0]], dtype=np.float32)

cv2.setMouseCallback('Camera', mouse_handler)

stream = urllib.request.urlopen(url)
bytes_data = b''
frame = None  # Global var for mouse_handler

while True:
    # --- MJPEG HTTP Stream Parsing ---
    while True:
        bytes_data += stream.read(1024)
        a = bytes_data.find(b'\xff\xd8')
        b = bytes_data.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            break
    if frame is None: continue

    # Let mouse handler access current frame for tracker init
    cv2.setMouseCallback('Camera', mouse_handler, param=frame)

    h, w, c = frame.shape
    if tracking and bbox and tracker:
        ok, bbox = tracker.update(frame)
        if ok:
            x, y, w_box, h_box = [int(v) for v in bbox]
            cx, cy = x + w_box // 2, y + h_box // 2
            measurement = np.array([[cx], [cy]], dtype=np.float32)
            kalman.correct(measurement)
            prediction = kalman.predict()
            pred_x, pred_y = int(prediction[0]), int(prediction[1])
            x_show, y_show = pred_x - w_box//2, pred_y - h_box//2
            cv2.rectangle(frame, (x_show, y_show), (x_show + w_box, y_show + h_box), (0, 255, 255), 2)
            # --- Servo logic ---
            target_pan = map_range(pred_x, 0, w, PAN_MIN, PAN_MAX)
            target_tilt = map_range(pred_y, 0, h, TILT_MAX, TILT_MIN)
            prev_pan = smooth_angle(prev_pan, target_pan, smooth_factor)
            prev_tilt = smooth_angle(prev_tilt, target_tilt, smooth_factor)
            send_servo_command(prev_tilt, prev_pan)
            cv2.putText(frame, f"Tilt: {prev_tilt} Pan: {prev_pan}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Tracking ({pred_x}, {pred_y})", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            tracking = False

    cv2.imshow('Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
if arduino:
    arduino.close()
print("\nProgram ended (Remote MJPEG tracking + Arduino)")




























