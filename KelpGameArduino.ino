#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

#define SS_PIN 10          // SDA pin for RFID
#define RST_PIN 9          // RST pin for RFID
#define BUTTON_PIN 7       // Pin for the button
#define SERVO1_PIN 6       // Signal pin for first Servo
#define SERVO2_PIN 5       // Signal pin for second Servo

MFRC522 rfid(SS_PIN, RST_PIN);   // Create MFRC522 instance
Servo servo1;                    // Create first Servo instance
Servo servo2;                    // Create second Servo instance

void setup() 
{
  Serial.begin(9600);   // Initiate a serial communication
  SPI.begin();          // Initiate SPI bus
  rfid.PCD_Init();      // Initiate MFRC522

  // Attach servos to their respective pins
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);

  // Set initial positions of servos to 90 degrees
  servo1.write(90);
  servo2.write(90);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {

  bool buttonState = digitalRead(BUTTON_PIN) == LOW;
  if (digitalRead(BUTTON_PIN) == LOW) {
    Serial.println("button");
    delay(1000);
  }
  // Check if a new RFID card is present
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  // Select the detected card
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Print UID to the serial monitor
  String content = "";
  for (byte i = 0; i < rfid.uid.size; i++) 
  {
    // Print each byte in hexadecimal with leading zeros if needed
    if (rfid.uid.uidByte[i] < 0x10) Serial.print(" 0");
    Serial.print(rfid.uid.uidByte[i], HEX);

    // Append to the UID content string for later use if needed
    content += String(rfid.uid.uidByte[i] < 0x10 ? " 0" : "");
    content += String(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();  // Move to a new line after printing UID
  
  // Optionally convert content to uppercase for consistency
  content.toUpperCase();
  servo1.write(0);            // Rotate first servo to 90 degrees
  servo2.write(0);            // Rotate second servo to 90 degrees
  delay(1000);                 // Hold position for 1 second

  // Return both servos to 0 degrees
  servo1.write(90);             
  servo2.write(90);

  // Halt PICC reading and prepare for the next card
  rfid.PICC_HaltA();
}
