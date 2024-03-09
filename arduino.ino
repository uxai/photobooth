/*
 * Matthew Talebi
 * March 7, 2024
 * Photo booth lights and trigger.
 * Only will trigger when the face is detected and button is pressed
 */

char inChar;  // character we will use for messages from the RPi
int green_led = 4;
int red_led = 6;
int yellow_led = 8;
int white_led = 3;
int button = 2;

void setup() {
  Serial.begin(9600);
  pinMode(button, INPUT);
  pinMode(green_led, OUTPUT);
  pinMode(red_led, OUTPUT);
  pinMode(yellow_led, OUTPUT);
  pinMode(white_led, OUTPUT);
  digitalWrite(green_led, LOW);
  digitalWrite(red_led, LOW);
  digitalWrite(yellow_led, LOW);
}

void loop() {
    // read the character we recieve on the serial port from the RPi
    if(Serial.available()) {
      inChar = (char)Serial.read();
    }
    if(inChar == 'T') {
      digitalWrite(green_led, HIGH);
    } else {
      digitalWrite(green_led, LOW);
    }
    // Checks if the face is detected and button is pressed, counts down
    if(digitalRead(green_led) == HIGH && digitalRead(button) == HIGH) {
      digitalWrite(red_led, HIGH);
      digitalWrite(green_led, HIGH);
      digitalWrite(yellow_led, HIGH);
      delay(1000);
      digitalWrite(red_led, LOW);
      delay(1000);
      digitalWrite(yellow_led, LOW);
      delay(1000);
      digitalWrite(green_led, LOW);
      delay(1000);
      Serial.println("S");
      for (int i = 0; i <= 255; i++) {
        analogWrite(white_led, i);
        delay(1);
      }
      for (int i = 255; i >= 0; i--) {
        analogWrite(white_led, i);
        delay(1);
      }
      delay(1000);
      Serial.flush();
    }
}
