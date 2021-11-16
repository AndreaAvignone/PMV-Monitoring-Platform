from conf.Generic_Sensor import*
import time
import serial
import sys

class Mq5(SensorPublisher):
    def __init__(self,configuration_filename='mq5_settings.json',room_filename='room_settings.son',serialPort='/dev/ttyACM0'):
        SensorPublisher.__init__(self,configuration_filename,room_filename)
        self.ser = serial.Serial(serialPort, 9600, timeout=0.5)
       
    def sendData(self):
        try:
            self.ser.flush()
            gas=int(self.ser.readline().decode('utf-8').rstrip())
            #print(gas) 
        except:
            gas=None     
        outputResult=[{'parameter':'AQI','value':gas}]
        self.PublishData(outputResult)
           
if __name__ == '__main__':
    settingFile=sys.argv[1]
    roomFile=sys.argv[2]
    serialPort=sys.argv[3]
    try:
        sensor=Mq5(settingFile,roomFile,serialPort)
        sensor.start()
        sensor.pingCatalog()
        start_time=time.time()
        while True:
            sensor.sendData()
            actual_time=time.time()
            if actual_time-start_time >(sensor.inactiveTime-30):
                sensor.pingCatalog()
                start_time=actual_time
            
            time.sleep(0.5)
    except:
        print("Error: Connection failed.\n")
