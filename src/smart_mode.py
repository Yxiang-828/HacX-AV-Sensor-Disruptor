import RPi.GPIO as GPIO
import time
from utils import detect_signal
from drivers import EmitterDriver

# GPIO pins
LIDAR_PIN = 18
CAM_PIN = 19
RADAR_PIN = 20
MODE_PIN = 21

# Initialize drivers
laser = EmitterDriver(LIDAR_PIN)
led = EmitterDriver(CAM_PIN)
rf = EmitterDriver(RADAR_PIN)

def smart_obstacle_mode():
    """Targeted spoofing to mimic obstacles, low power"""
    while GPIO.input(MODE_PIN) == GPIO.LOW:
        if detect_signal():  # AV sensor detected
            # Sequence pulses to spoof obstacles
            laser.pulse(0.15, 80)  # Fake wall at 15m, 80% duty
            time.sleep(0.05)
            led.pulse(0.08, 60)  # Dazzle, 60% duty
            time.sleep(0.05)
            rf.pulse(0.2, 70)  # Echo barrier, 70% duty
        time.sleep(0.4)  # Low duty cycle for efficiency