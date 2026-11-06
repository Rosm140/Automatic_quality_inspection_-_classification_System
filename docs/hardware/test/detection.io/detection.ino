#define IR_SENSOR 4
#define BUZZER 18

void setup() {

  Serial.begin(115200);

  pinMode(IR_SENSOR, INPUT);

  ledcAttach(BUZZER, 2000, 8);
}

void loop() {

  int sensorValue = digitalRead(IR_SENSOR);

  if (sensorValue == LOW) {

    Serial.println("Object Detected!");

    ledcWriteTone(BUZZER, 1000);

  } else {

    Serial.println("No Object");

    ledcWriteTone(BUZZER, 0);
  }

  delay(200);
}