import cv2
import numpy as np

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

while True:
    ret, frame = cap.read()
    if not ret: break
    if tracking and bbox and tracker:
        ok, bbox = tracker.update(frame)
        if ok:
            x, y, w, h = [int(v) for v in bbox]
            cx, cy = x + w//2, y + h//2
            measurement = np.array([[cx], [cy]], dtype=np.float32)
            kalman.correct(measurement)
            prediction = kalman.predict()
            pred_x, pred_y = int(prediction[0]), int(prediction[1])
            x_show, y_show = pred_x - w//2, pred_y - h//2
            cv2.rectangle(frame, (x_show, y_show), (x_show + w, y_show + h), (0, 255, 255), 2)
        else:
            tracking = False
    cv2.imshow('Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

























