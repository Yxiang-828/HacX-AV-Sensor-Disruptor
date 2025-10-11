import RPi.GPIO as GPIO
import time

class EmitterDriver:
    def __init__(self, pin, freq=1000):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, freq)
        self.pwm.start(0)  # Duty cycle 0-100

    def set_power(self, duty_cycle):
        self.pwm.ChangeDutyCycle(duty_cycle)

    def pulse(self, duration, duty=50):
        self.set_power(duty)
        time.sleep(duration)
        self.set_power(0)

# In modes: e.g., laser = EmitterDriver(18); laser.pulse(0.15, 80)  # 80% for 15m range