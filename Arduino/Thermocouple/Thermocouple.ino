#include <MAX6675_Thermocouple.h>

#define SCK_PIN 10
#define CS_PIN 9
#define SO_PIN 8

MAX6675_Thermocouple thermocouple=MAX6675_Thermocouple(SCK_PIN, CS_PIN, SO_PIN);

void setup() {
  Serial.begin(9600);

}

void loop() {
  
  double temp_celsius= thermocouple.readCelsius();
  String jsonString="{\"temperature\":";
  jsonString +=temp_celsius;
  jsonString += "}";
  Serial.println(jsonString);
  delay(500);

}
