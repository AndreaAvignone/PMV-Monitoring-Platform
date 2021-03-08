from conf.Generic_Sensor import *
import time
from w1thermsensor import W1ThermSensor

class ds18b20(SensorPublisher):
    def __init__(self,configuration_filename,device_ID='ds18b20',pin=4):
        SensorPublisher.__init__(self,configuration_filename,device_ID)
        self.DS18B20= W1ThermSensor()                                  
                    
    def retrieveData(self):
        try:
            temperature=self.DS18B20.get_temperature()
            outputResult=[{'parameter':'temperature','value':temperature}]
            return outputResult
        except:
            time.sleep(3)