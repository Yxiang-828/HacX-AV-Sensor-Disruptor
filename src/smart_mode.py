import RPi.GPIO as GPIO
import time
from utils import detect_signal
from drivers import EmitterDriver
from temp_monitor import check_overheat
from safety import check_safety

# GPIO pins
LIDAR_PIN = 18
CAM_PIN = 19
MANUAL_TRIGGER_PIN = 26  # Manual trigger if detection fails
GPIO.setup([LIDAR_PIN, CAM_PIN], GPIO.OUT)
GPIO.setup(MANUAL_TRIGGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def smart_obstacle_mode():
    """Targeted spoofing to mimic obstacles"""
    MODE_PIN = 21
    laser = EmitterDriver(LIDAR_PIN)
    cam = EmitterDriver(CAM_PIN)
    while GPIO.input(MODE_PIN) == GPIO.LOW:
        if not check_safety() or check_overheat():
            print("Stopping due to safety/overheat")
            return
        # Detection or manual trigger (GPIO 26 button)
        if detect_signal() or GPIO.input(MANUAL_TRIGGER_PIN) == GPIO.LOW:
            laser.pulse(0.15, duty=80)  # Fake wall at 15m
            time.sleep(0.05)
            cam.pulse(0.08, duty=60)   # Dazzle
            time.sleep(0.4)  # Low duty cycle