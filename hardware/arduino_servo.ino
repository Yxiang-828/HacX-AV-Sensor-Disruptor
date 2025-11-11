/*
 * Arduino Servo Controller for Laser Tracker
 * Receives commands from Raspberry Pi via Serial
 * Format: T<tilt>P<pan>\n
 * Example: T90P120\n (Tilt=90°, Pan=120°)
 */

#include <Servo.h>

// Servo objects
Servo tiltServo;
Servo panServo;

// Pin assignments
const int TILT_PIN = 9;
const int PAN_PIN = 10;
const int LASER_PIN = 13; // Optional laser control

// Servo limits (adjust based on your hardware)
const int TILT_MIN = 0;
const int TILT_MAX = 180;
const int PAN_MIN = 0;
const int PAN_MAX = 180;

// Current positions
int currentTilt = 90;
int currentPan = 90;

// Serial communication
String inputString = "";
boolean stringComplete = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Attach servos
  tiltServo.attach(TILT_PIN);
  panServo.attach(PAN_PIN);
  
  // Initialize laser pin (optional)
  pinMode(LASER_PIN, OUTPUT);
  digitalWrite(LASER_PIN, HIGH); // Turn on laser
  
  // Center servos
  tiltServo.write(90);
  panServo.write(90);
  
  // Reserve space for input string
  inputString.reserve(50);
  
  Serial.println("Arduino Servo Controller Ready");
  Serial.println("Format: T<tilt>P<pan>");
  Serial.println("Example: T90P120");
}

void loop() {
  // Check for serial commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

// Serial event handler (called automatically when data is received)
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

// Process incoming command
void processCommand(String cmd) {
  // Parse command: T<tilt>P<pan>
  int tiltIndex = cmd.indexOf('T');
  int panIndex = cmd.indexOf('P');
  
  if (tiltIndex >= 0 && panIndex > tiltIndex) {
    // Extract tilt value
    String tiltStr = cmd.substring(tiltIndex + 1, panIndex);
    int tiltValue = tiltStr.toInt();
    
    // Extract pan value
    String panStr = cmd.substring(panIndex + 1);
    int panValue = panStr.toInt();
    
    // Constrain values to safe range
    tiltValue = constrain(tiltValue, TILT_MIN, TILT_MAX);
    panValue = constrain(panValue, PAN_MIN, PAN_MAX);
    
    // Move servos
    moveServos(tiltValue, panValue);
    
    // Send acknowledgment
    Serial.print("OK: T");
    Serial.print(tiltValue);
    Serial.print(" P");
    Serial.println(panValue);
  } else {
    Serial.println("ERROR: Invalid command format");
  }
}

// Move servos to specified positions
void moveServos(int tilt, int pan) {
  // Smooth movement (optional - prevents jerky motion)
  int steps = 10;
  
  for (int i = 1; i <= steps; i++) {
    int intermediateTilt = currentTilt + ((tilt - currentTilt) * i) / steps;
    int intermediatePan = currentPan + ((pan - currentPan) * i) / steps;
    
    tiltServo.write(intermediateTilt);
    panServo.write(intermediatePan);
    
    delay(5); // Small delay for smooth motion
  }
  
  // Update current positions
  currentTilt = tilt;
  currentPan = pan;
}

// Optional: Function to toggle laser
void toggleLaser() {
  digitalWrite(LASER_PIN, !digitalRead(LASER_PIN));
}

// Optional: Function to center servos
void centerServos() {
  moveServos(90, 90);
  Serial.println("Servos centered");
}