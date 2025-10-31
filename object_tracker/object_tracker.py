import cv2

drawing = False
ix, iy = -1, -1
bbox = None
tracker = None
tracking = False
temp_frame = None

def mouse_handler(event, x, y, flags, param):
    global drawing, ix, iy, bbox, tracker, tracking, temp_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        temp_frame = param.copy()

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        frame_copy = temp_frame.copy()
        cv2.rectangle(frame_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('Camera', frame_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x0, y0 = min(ix, x), min(iy, y)
        w, h = abs(x - ix), abs(y - iy)
        if w > 1 and h > 1:
            bbox = (x0, y0, w, h)
            frame_copy = temp_frame.copy()
            cv2.rectangle(frame_copy, (x0, y0), (x0 + w, y0 + h), (0, 255, 0), 2)
            cv2.imshow('Camera', frame_copy)
            tracker = cv2.TrackerMIL_create()  # Using MIL tracker which is available in this OpenCV version
            tracker.init(temp_frame, bbox)
            tracking = True
            print(f'Tracker initialized at ({x0}, {y0}, {w}, {h})')
        else:
            print("[ERROR] Bounding box too small, select a larger area.")

cap = cv2.VideoCapture(0)
cv2.namedWindow('Camera')

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Could not read frame from camera.")
        break

    # For annotation, send a fresh frame copy on each loop to the callback
    cv2.setMouseCallback('Camera', mouse_handler, param=frame)

    if tracking and tracker is not None and bbox is not None:
        ok, bbox = tracker.update(frame)
        if ok:
            x, y, w, h = [int(i) for i in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            tracking = False
            print("[INFO] Lost track of object.")

    cv2.imshow('Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()









