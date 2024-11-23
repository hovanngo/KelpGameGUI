#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <Adafruit_NeoPixel.h>


#define LED_PIN 3 // Neopixel 
#define NUMPIXELS 16 // P


#define SS_PIN2 10          // SDA pin for RFID1
#define RST_PIN2 9          // RST pin for RFID1
#define SS_PIN1 8           // SDA pin for RFID2
#define RST_PIN1 7          // RST pin for RFID2

#define BUTTON_PIN 4       // Pin for the button
#define SERVO1_PIN 6       // Signal pin for first Servo
#define SERVO2_PIN 5       // Signal pin for second Servo

MFRC522 rfid1(SS_PIN1, RST_PIN1);     // Create MFRC522 instance for reader 1
MFRC522 rfid2(SS_PIN2, RST_PIN2);     // Create MFRC522 instance for reader 2

Servo servo1;                       // Create first Servo instance
Servo servo2;                       // Create second Servo instance

Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN, NEO_RGBW + NEO_KHZ800);


void setup() {
  Serial.begin(9600);               // Start serial communication
  SPI.begin();                      // Start SPI bus
  rfid1.PCD_Init();                 // Initialize first RFID reader
  rfid2.PCD_Init();                 // Initialize second RFID reader

  // Attach servos to their respective pins
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);

  // Set initial positions of servos to 0 degrees (closed position)
  servo1.write(90);
  servo2.write(90);

  pinMode(BUTTON_PIN, INPUT_PULLUP); // Set button pin as input with pull-up resistor
  pixels.begin();                   // Initialize NeoPixel strip
  pixels.clear();                   // Clear NeoPixel colors
  pixels.show();                    // Ensure no LEDs are lit
}

void loop() {
  if (Serial.available() > 0) { // Check if data is available
    String command = Serial.readStringUntil('\n'); // Read the command
    command.trim(); // Remove whitespace/newline
    if (command == "ON") {
      pixels.fill(pixels.Color(50, 221, 0, 0)); // Orange: RGB(255, 165, 0)
      pixels.show();
      Serial.println("LEDs are orange");
    } else if (command == "OFF") {
    pixels.clear();                   // Clear NeoPixel colors
    pixels.show();  
    }
  }


  


  // Check for button press
  if (digitalRead(BUTTON_PIN) == LOW) {
    Serial.println("Button");
    delay(1000); // Debounce delay
  }

  
  if (rfid1.PICC_IsNewCardPresent()) {
    Serial.println("rfid1");
    rfid1.PICC_HaltA();  // Halt communication with the card
    actuateServos();      // Actuate servos if card is detected
  }

  // Check RFID reader 2
  if (rfid2.PICC_IsNewCardPresent()) {
    Serial.println("rfid2");
    rfid2.PICC_HaltA();  // Halt communication with the card
    actuateServos();      // Actuate servos if card is detected
  }

  // Reset the SS pins to high to disable both readers
  digitalWrite(SS_PIN1, HIGH);
  digitalWrite(SS_PIN2, HIGH);
}

// Function to get the UID from an RFID reader

// Function to actuate the servos
void actuateServos() {
  //Serial.println("Servo Actuated");
  servo1.write(0);   // Open door 1
  servo2.write(0);   // Open door 2
  blinkGreenLEDs();      // Blink the NeoPixel LEDs green
  servo1.write(90);    // Close door 1
  servo2.write(90);    // Close door 2
}

void blinkGreenLEDs() {
  pixels.fill(pixels.Color(255, 0, 0));
  pixels.show();   // Send the updated pixel colors to the hardware.
  delay(1000);
  pixels.clear();
  pixels.show();
}
