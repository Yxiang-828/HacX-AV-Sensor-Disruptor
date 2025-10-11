import RPi.GPIO as GPIO
from temp_monitor import get_temperature

FAN_PIN = 24  # Fan control
FUSE_PIN = 25  # Fuse status (active low if blown)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(FUSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def check_safety():
    """Check temp and fuse; control fan"""
    temp = get_temperature()
    if temp and temp > 40:
        GPIO.output(FAN_PIN, GPIO.HIGH)  # Fan on
    else:
        GPIO.output(FAN_PIN, GPIO.LOW)   # Fan off

    if temp and temp > 50:
        print("Critical overheat: Shutting down")
        return False

    if GPIO.input(FUSE_PIN) == GPIO.LOW:
        print("Fuse blown: Shutting down")
        return False

    return True