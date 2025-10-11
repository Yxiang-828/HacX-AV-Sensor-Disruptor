import RPi.GPIO as GPIO
import time
from utils import detect_signal
from drivers import EmitterDriver
from temp_monitor import check_overheat

# GPIO pins
LIDAR_PIN = 18
CAM_PIN = 19
GPIO.setup([LIDAR_PIN, CAM_PIN], GPIO.OUT)

def smart_obstacle_mode():
    """Targeted spoofing to mimic obstacles"""
    MODE_PIN = 21
    laser = EmitterDriver(LIDAR_PIN)
    cam = EmitterDriver(CAM_PIN)
    while GPIO.input(MODE_PIN) == GPIO.LOW:
        if check_overheat():
            print("Stopping due to overheat")
            return
        if detect_signal():
            laser.pulse(0.15, duty=80)  # Fake wall at 15m
            time.sleep(0.05)
            cam.pulse(0.08, duty=60)   # Dazzle
            time.sleep(0.4)  # Low duty cycle