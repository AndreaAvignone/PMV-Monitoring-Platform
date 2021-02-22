from conf.Generic_Sensor import *
import time
import Adafruit_DHT
import sys

class DHT11(SensorPublisher):
    def __init__(self,configuration_filename='dht11_settings.json',room_filename='room_settings.json',pin=4):
        SensorPublisher.__init__(self,configuration_filename,room_filename)
        self.DHT11 = Adafruit_DHT.DHT11                                  
        self.DHT11_PIN = pin
                    
    def sendData(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.DHT11, self.DHT11_PIN, retries=2, delay_seconds=3)
        outputResult=[{'parameter':'humidity','value':humidity},{'parameter':'temperature','value':temperature}]
        self.PublishData(outputResult)
            
if __name__ == '__main__':
    settingFile=sys.argv[1]
    roomFile=sys.argv[2]
    pin=sys.argv[3]
    try:
        sensor=DHT11(settingFile,roomFile,pin)
        sensor.start()
        sensor.pingCatalog()
        start_time=time.time()
        while True:
            sensor.sendData()
            actual_time=time.time()
            if actual_time-start_time >(sensor.inactiveTime-30):
                sensor.pingCatalog()
                start_time=actual_time
            time.sleep(5)
    except:
        print("Error: connection failed")

