import RPi.GPIO as GPIO
import time
from utils import detect_signal

# GPIO pins
LIDAR_PIN = 18
CAM_PIN = 19
RADAR_PIN = 20
GPIO.setup([LIDAR_PIN, CAM_PIN, RADAR_PIN], GPIO.OUT)

def smart_obstacle_mode():
    """Targeted spoofing to mimic obstacles, low power"""
    MODE_PIN = 21
    while GPIO.input(MODE_PIN) == GPIO.LOW:
        if detect_signal():  # AV sensor detected
            # Sequence pulses to spoof obstacles
            GPIO.output(LIDAR_PIN, GPIO.HIGH); time.sleep(0.15); GPIO.output(LIDAR_PIN, GPIO.LOW)  # Fake wall at 15m
            time.sleep(0.05)
            GPIO.output(CAM_PIN, GPIO.HIGH); time.sleep(0.08); GPIO.output(CAM_PIN, GPIO.LOW)  # Dazzle
            time.sleep(0.05)
            GPIO.output(RADAR_PIN, GPIO.HIGH); time.sleep(0.2); GPIO.output(RADAR_PIN, GPIO.LOW)  # Echo barrier
        time.sleep(0.4)  # Low duty cycle for efficiency