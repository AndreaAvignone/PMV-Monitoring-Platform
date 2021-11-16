from conf.Generic_Sensor import*
import time
import serial
import sys

class revC(SensorPublisher):
    def __init__(self,configuration_filename,device_ID='revC',serialPort='/dev/ttyACM0'):
        self.device_ID=device_ID
        SensorPublisher.__init__(self,configuration_filename,device_ID)
        self.ser = serial.Serial(serialPort, 9600, timeout=1)
       
    def retrieveData(self):
        self.ser.flush()
        try:
            data=self.ser.readline().decode('utf-8').rstrip()
            if len(data)>0 and data[0]=='{':
                try:
                    data=json.loads(data)
                    if data['sensor']==self.device_ID:
                        wind=data['wind']
                        if wind is not None and wind != 1000:
                            outputResult=[{'parameter':'wind','value':wind}]
                            return outputResult
                except:
                    time.sleep(1)
        except:
            time.sleep(1)
