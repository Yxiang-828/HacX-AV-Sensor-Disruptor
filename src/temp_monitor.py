import w1thermsensor
import time

def get_temperature():
    """Read DS18B20 temperature (GPIO 23, 1-Wire)"""
    try:
        sensor = w1thermsensor.W1ThermSensor()
        temp = sensor.get_temperature()
        return temp
    except Exception as e:
        print(f"Temp sensor error: {e}")
        return None

def check_overheat(threshold=50):
    """Check if temp exceeds threshold"""
    temp = get_temperature()
    if temp and temp > threshold:
        print(f"Overheat detected: {temp}°C")
        return True
    return False