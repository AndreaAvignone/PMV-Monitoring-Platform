import json
from datetime import datetime
import time

#it could be useless if a specific structure is not imposed.
class Device():
    def __init__(self,sensorID,endPoints,parameters,timestamp):
        self.sensorID=sensorID
        self.endPoints=endPoints
        self.parameters=parameters
        self.timestamp=timestamp
    
    def jsonify(self):
        device={'sensorID':self.sensorID,'end_points':self.endPoints,'parameters':self.parameters,'timestamp':self.timestamp}
        return device

class DevicesCatalog():
    def __init__(self,devices_list):
        self.devices=devices_list
        self.timestamp=time.time()
        self.now=datetime.now()
        self.actualTime=self.now.strftime("%d/%m/%Y %H:%M")

    def findPos(self,device_ID):
        notFound=1
        for i in range(len(self.devices)): 
            if self.devices[i]['device_ID']==device_ID:
                notFound=0
                return i
        if notFound==1:
            return False
        
    def insertValue(self,device_ID,device_valueDict):
        i=self.findPos(device_ID)
        for j in range(len(self.devices[i])):
            if self.devices[i]['parameters'][j].get('parameter')==device_valueDict['parameter']:
                self.devices[i]['parameters'][j]=device_valueDict
                self.devices[i]['timestamp']=device_valueDict['timestamp']
                break

    """
    def insertDevice(self, device_ID, endPoints, availableResources):
        i=self.findPos(device_ID)
        if i is not False:
            #update the device if it exists
            self.devices[i]['end_points']=endPoints
            self.devices[i]['timestamp']=self.timestamp
            output=False
        else:
            #otherwise create the device
            newDevice=Device(device_ID,endPoints,availableResources,self.timestamp).jsonify()
            self.devices.append(newDevice)
            output=True
        return output
    """
    def insertDevice(self, device_ID, device):
        i=self.findPos(device_ID)
        if i is not False:
            #update the device if it exists
            self.devices[i]['timestamp']=self.timestamp
            output=False
        else:
            #otherwise create the device
            device['timestamp']=self.timestamp
            self.devices.append(device)
            output=True
        return output
        
    def removeInactive(self,timeInactive):
        output=False
        for device in self.devices:
            device_ID=device['device_ID']
            if self.timestamp - device['timestamp']>timeInactive:
                self.devices.remove(device)
                #self.devices['last_update']=self.actualTime
                print(f'Device {device_ID} removed')
                output=True
        return output


    def removeDevice(self,device_ID):
        i=self.findPos(device_ID)
        if i is not False:
            self.devices.pop(i) 
            return True
        else:
            return i

    
