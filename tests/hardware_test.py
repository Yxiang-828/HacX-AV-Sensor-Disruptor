import RPi.GPIO as GPIO
import time
from utils import detect_signal

GPIO.setmode(GPIO.BCM)
PINS = [18, 19, 20, 21, 22]  # Laser, LED, RF, Switch, Photodiode
GPIO.setup(PINS[:-2], GPIO.OUT)  # Emitters out
GPIO.setup([PINS[-2], PINS[-1]], GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Switch + photodiode in

print("Testing emitters...")
for pin in PINS[:3]:
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pin, GPIO.LOW)

print("Switch state:", GPIO.input(21))
print("Photodiode state:", GPIO.input(22))

print("Testing detection...")
if detect_signal():
    print("AV signal detected!")
else:
    print("No detection.")

GPIO.cleanup()