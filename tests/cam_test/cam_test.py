import cv2
import numpy as np
import serial
import time

# Initialize Arduino serial connection
# Change 'COM3' to your Arduino's COM port
try:
    arduino = serial.Serial('COM5', 9600, timeout=1)
    time.sleep(2)
    print("✓ Connected to Arduino on COM5")
except:
    print("ERROR: Could not connect to Arduino!")
    print("Check COM port in Arduino IDE under Tools > Port")
    exit()

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\n=== Color Tracking Servo Control ===")
print("1. Show a COLORED OBJECT to the camera")
print("2. Press 's' to SELECT the color")
print("3. Move the object - servos will follow!")
print("4. Press 'r' to RESET color selection")
print("5. Press 'q' to QUIT\n")

# Servo settings
TILT_MIN, TILT_MAX = 0, 180
PAN_MIN, PAN_MAX = 0, 180

# Smoothing
prev_tilt = 90
prev_pan = 90
smooth_factor = 0.3

# Color range (will be set when user presses 's')
lower_color = None
upper_color = None
color_selected = False

def map_range(value, in_min, in_max, out_min, out_max):
    """Map value from one range to another"""
    value = max(in_min, min(in_max, value))
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def smooth_angle(current, target, factor):
    """Smooth servo movement"""
    return int(current + (target - current) * factor)

def select_color(frame, x, y):
    """Select color from clicked position"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    color = hsv[y, x]

    # Create color range with tolerance
    tolerance = 20
    lower = np.array([max(0, color[0] - tolerance), 100, 100])
    upper = np.array([min(179, color[0] + tolerance), 255, 255])

    return lower, upper

# Mouse callback for color selection
click_x, click_y = -1, -1
def mouse_callback(event, x, y, flags, param):
    global click_x, click_y
    if event == cv2.EVENT_LBUTTONDOWN:
        click_x, click_y = x, y

cv2.namedWindow('Color Tracking - Servo Control')
cv2.setMouseCallback('Color Tracking - Servo Control', mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Handle mouse click for color selection
    if click_x != -1 and click_y != -1:
        lower_color, upper_color = select_color(frame, click_x, click_y)
        color_selected = True
        print(f"✓ Color selected at ({click_x}, {click_y})")
        click_x, click_y = -1, -1

    if color_selected and lower_color is not None:
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask for selected color
        mask = cv2.inRange(hsv, lower_color, upper_color)

        # Remove noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 500:  # Minimum area threshold
                # Get center of contour
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Draw contour and center
                    cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                    # Map position to servo angles
                    target_pan = map_range(cx, 0, w, PAN_MIN, PAN_MAX)
                    target_tilt = map_range(cy, 0, h, TILT_MAX, TILT_MIN)

                    # Smooth movement
                    prev_pan = smooth_angle(prev_pan, target_pan, smooth_factor)
                    prev_tilt = smooth_angle(prev_tilt, target_tilt, smooth_factor)

                    # Send to Arduino
                    command = f"T{prev_tilt}P{prev_pan}\n"
                    arduino.write(command.encode())

                    # Display info
                    cv2.putText(frame, f"Tilt: {prev_tilt}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Pan: {prev_pan}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Tracking at ({cx}, {cy})", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, "TRACKING", (10, h - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Object too small", (10, h - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Color not detected", (10, h - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Show mask in corner
        mask_small = cv2.resize(mask, (160, 120))
        mask_color = cv2.cvtColor(mask_small, cv2.COLOR_GRAY2BGR)
        frame[10:130, w-170:w-10] = mask_color
    else:
        cv2.putText(frame, "Click on a COLORED OBJECT or press 's'", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, "to select color to track", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Draw crosshair
    cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), (255, 0, 0), 2)
    cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), (255, 0, 0), 2)

    # Instructions
    cv2.putText(frame, "s=Select | r=Reset | q=Quit", (10, h - 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('Color Tracking - Servo Control', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Select color at center of frame
        lower_color, upper_color = select_color(frame, w//2, h//2)
        color_selected = True
        print("✓ Color selected at center")
    elif key == ord('r'):
        color_selected = False
        lower_color = None
        upper_color = None
        print("Color selection reset")

# Cleanup
cap.release()
cv2.destroyAllWindows()
arduino.close()
print("\nProgram ended")