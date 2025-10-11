import RPi.GPIO as GPIO
import time
from smoke_mode import smoke_bomb_mode
from smart_mode import smart_obstacle_mode

# GPIO setup
GPIO.setmode(GPIO.BCM)
MODE_PIN = 21  # Toggle switch
GPIO.setup(MODE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    current_mode = 'smart'  # Default
    print("Starting Dual-Mode AV Disruptor...")
    while True:
        if GPIO.input(MODE_PIN) == GPIO.HIGH:  # Smoke mode
            if current_mode != 'smoke':
                print("Switching to Smoke Bomb Mode")
                current_mode = 'smoke'
            smoke_bomb_mode()
        else:  # Smart mode
            if current_mode != 'smart':
                print("Switching to Smart Obstacle Mode")
                current_mode = 'smart'
            smart_obstacle_mode()
        time.sleep(0.1)  # Poll switch

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down...")
        GPIO.cleanup()