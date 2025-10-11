import RPi.GPIO as GPIO
import time
from utils import detect_signal
from drivers import EmitterDriver

GPIO.setmode(GPIO.BCM)
PINS = [18, 19, 20, 21, 22]  # Laser, LED, RF, Switch, Photodiode
GPIO.setup([PINS[-2], PINS[-1]], GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Switch + photodiode in

# Initialize drivers for emitters
laser = EmitterDriver(PINS[0])
led = EmitterDriver(PINS[1])
rf = EmitterDriver(PINS[2])

print("Testing emitters...")
laser.set_power(100); time.sleep(1); laser.set_power(0)
led.set_power(100); time.sleep(1); led.set_power(0)
rf.set_power(100); time.sleep(1); rf.set_power(0)

print("Switch state:", GPIO.input(21))
print("Photodiode state:", GPIO.input(22))

print("Testing detection...")
if detect_signal():
    print("AV signal detected!")
else:
    print("No detection.")

GPIO.cleanup()