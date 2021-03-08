from conf.Generic_Sensor import*
import time
import serial
import sys

class max76675(SensorPublisher):
    def __init__(self,configuration_filename,device_ID='max76675',serialPort='/dev/ttyACM0'):
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
                        temp_g=data['temperature_g']
                        if temp_g is not None and temp_g != 1000:
                            outputResult=[{'parameter':'temperature_g','value':temp_g}]
                            return outputResult
                except:
                    time.sleep(1)
        except:
            pass 


