import json
from datetime import datetime

class DevicesList():
    def __init__(self,filename):
        fileContent=json.load(open(filename))
        self.fileContent=fileContent
        self.devicesList=[]
        for device in self.fileContent['devices']:
            self.devicesList.append(Device(device.get('sensorID'),device.get('end_points'),device.get('parameters'),device.get('timestamp')).jsonify())
    def show(self):
        for device in self.devicesList:
            print(device)


class Device():
    def __init__(self,sensorID,endPoints,parameters,timestamp):
        self.sensorID=sensorID
        self.endPoints=endPoints
        self.parameters=parameters
        self.timestamp=timestamp
    
    def jsonify(self):
        device={'sensorID':self.sensorID,'end_points':self.endPoints,'parameters':self.parameters,'timestamp':self.timestamp}
        return device
