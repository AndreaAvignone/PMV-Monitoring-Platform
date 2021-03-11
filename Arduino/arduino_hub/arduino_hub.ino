#include <MAX6675_Thermocouple.h>

//pin definition for thermocuple
#define SCK_PIN 10
#define CS_PIN 9
#define SO_PIN 8

#define thermocoupleSensor "max76675"
#define thermocoupleUnit "C"

//pin definition for wind sensor
#define analogPinForRV    1   
#define analogPinForTMP   0

#define windSensor "revC"
#define windUnit "KmH"

// to calibrate your sensor, put a glass over it, but the sensor should not be
// touching the desktop surface however.
// adjust the zeroWindAdjustment until your sensor reads about zero with the glass over it. 

const float zeroWindAdjustment =  .4; // negative numbers yield smaller wind speeds and vice versa.

int TMP_Therm_ADunits;  //temp termistor value from wind sensor
float RV_Wind_ADunits;    //RV output from wind sensor 
float RV_Wind_Volts;
unsigned long lastMillis;
int TempCtimes100;
float zeroWind_ADunits;
float zeroWind_volts;
float WindSpeed_MPH;
float WindSpeed_KmH;

MAX6675_Thermocouple thermocouple=MAX6675_Thermocouple(SCK_PIN, CS_PIN, SO_PIN);

void setup() {
  Serial.begin(9600);

}

void loop() {
  //print mrt information
  double temp_celsius= thermocouple.readCelsius();
  if (isnan(temp_celsius)){
     temp_celsius=1000;
  }
  String jsonMRT="{\"sensor\":";
  jsonMRT += " \"" thermocoupleSensor"\"";
  jsonMRT += ",";
  jsonMRT += "\"temperature_g\":";
  jsonMRT +=temp_celsius;
  jsonMRT += ",";
  jsonMRT += "\"unit\":";
  jsonMRT +="\"" thermocoupleUnit"\"";
  jsonMRT += "}";
  Serial.println(jsonMRT);
  delay(500);
    
  TMP_Therm_ADunits = analogRead(analogPinForTMP);
  RV_Wind_ADunits = analogRead(analogPinForRV);
  RV_Wind_Volts = (RV_Wind_ADunits *  0.0048828125);
  TempCtimes100 = (0.005 *((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits)) - (16.862 * (float)TMP_Therm_ADunits) + 9075.4;  
  zeroWind_ADunits = -0.0006*((float)TMP_Therm_ADunits * (float)TMP_Therm_ADunits) + 1.0727 * (float)TMP_Therm_ADunits + 47.172;  //  13.0C  553  482.39
  zeroWind_volts = (zeroWind_ADunits * 0.0048828125) - zeroWindAdjustment;  
  WindSpeed_MPH =  pow(((RV_Wind_Volts - zeroWind_volts) /.2300) , 2.7265);   
  WindSpeed_KmH=(float)WindSpeed_MPH*1.609344;
  if (isnan(WindSpeed_KmH)){
     WindSpeed_KmH=1000;
  }

  String jsonWind="{\"sensor\":";
  jsonWind += "\"" windSensor"\"";
  jsonWind += ",";
  jsonWind += "\"wind\":";
  jsonWind +=(float)WindSpeed_KmH;
  jsonWind += ",";
  jsonWind += "\"unit\":";
  jsonWind +=  "\"" windUnit"\"";
  jsonWind += "}";
  Serial.println(jsonWind);
  delay(3000);   
   

  


}
