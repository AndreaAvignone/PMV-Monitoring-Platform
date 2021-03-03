from conf.Generic_Sensor import *
import time
import Adafruit_DHT

class dht11(SensorPublisher):
    def __init__(self,configuration_filename,device_ID='dht11',pin=17):
        SensorPublisher.__init__(self,configuration_filename,device_ID)
        self.DHT11 = Adafruit_DHT.DHT11                                  
        self.DHT11_PIN = pin
                    
    def retrieveData(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.DHT11, self.DHT11_PIN, retries=2, delay_seconds=3)
        #outputResult=[{'parameter':'humidity','value':humidity},{'parameter':'temperature','value':temperature}]
        outputResult=[{'parameter':'humidity','value':humidity}]
        return outputResult
            
