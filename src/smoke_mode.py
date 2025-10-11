import RPi.GPIO as GPIO
import time
import numpy as np
from drivers import EmitterDriver
from temp_monitor import check_overheat

# GPIO pins
LIDAR_PIN = 18  # IR laser
CAM_PIN = 19    # LED array
GPIO.setup([LIDAR_PIN, CAM_PIN], GPIO.OUT)

def smoke_bomb_mode():
    """Chaotic emissions to overwhelm AV sensors"""
    MODE_PIN = 21
    laser = EmitterDriver(LIDAR_PIN)
    cam = EmitterDriver(CAM_PIN)
    while GPIO.input(MODE_PIN) == GPIO.HIGH:
        if check_overheat():
            print("Stopping due to overheat")
            return
        for driver in [laser, cam]:
            driver.pulse(np.random.uniform(0.1, 0.5), duty=80)  # Random pulse, high power
            time.sleep(0.05)