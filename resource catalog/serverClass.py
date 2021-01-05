import json
from datetime import datetime
import time
import requests
from rooms_catalog import RoomsCatalog
from devices_catalog import DevicesCatalog

class NewPlatform():
    def __init__(self,platform_ID,rooms,last_update):
        self.platform_ID=platform_ID
        self.rooms=rooms
        self.lastUpdate=last_update
        
    def jsonify(self):
        platform={'platform_ID':self.platform_ID,'rooms':self.rooms,'creation_date':self.lastUpdate}
        return platform
    
class Server():
    def __init__(self,db_filename):
        self.db_filename=db_filename
        self.serverContent=json.load(open(self.db_filename,"r"))
        
    def findPos(self,platform_ID):
        notFound=1
        for i in range(len(self.serverContent['platforms_list'])): 
            if self.serverContent['platforms_list'][i]['platform_ID']==platform_ID:
                notFound=0
                return i
        if notFound==1:
            return False

    def retrievePlatformsList(self):
        platformsList=[]
        for platform in self.serverContent['platforms_list']:
            platformsList.append(platform['platform_ID'])
        return platformsList
    
    def retrievePlatform(self,platform_ID):
        notFound=1
        for platform in self.serverContent['platforms_list']:
            if platform['platform_ID']==platform_ID:
                notFound=0
                return platform
        if notFound==1:
            return False

    def retrieveRoomInfo(self,platform_ID,room_ID):
        notFound=1
        platform=self.retrievePlatform(platform_ID)
        for room in platform['rooms']:
            if room['room_ID']==room_ID:
                notFound=0
                return room
        if notFound==1:
            return False

    def retrieveDeviceInfo(self,platform_ID,room_ID,device_ID):
        notFound=1
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        for device in room['devices']:
            if device['device_ID']==device_ID:
                notFound=0
                return device
        if notFound==1:
            return False

    def retrieveParameterInfo(self,platform_ID,room_ID,device_ID,parameter_name):
        notFound=1
        device=self.retrieveDeviceInfo(platform_ID,room_ID,device_ID)
        for parameter in device['parameters']:
            if parameter['parameter']==parameter_name:
                notFound=0
                return parameter
        if notFound==1:
            return False
        
    def insertPlatform(self,platform_ID,rooms):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        platform=self.retrievePlatform(platform_ID)
        if platform is False:
            createdPlatform=NewPlatform(platform_ID,rooms,timestamp).jsonify()
            self.serverContent['platforms_list'].append(createdPlatform)
            return True
        else:
            return False

    def insertRoom(self,platform_ID,room_ID,room):
        i=self.findPos(platform_ID)
        existingFlag=False
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.serverContent['platforms_list'][i]['rooms'])
            existingFlag=self.roomsCatalog.insertRoom(room_ID,room)
            i=True
        return i,existingFlag

    def insertDevice(self,platform_ID,room_ID,device_ID,device):
        i=self.findPos(platform_ID)
        existingFlag=False
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.serverContent['platforms_list'][i]['rooms'])
            j=self.roomsCatalog.findPos(room_ID)
            self.devicesCatalog=DevicesCatalog(self.serverContent['platforms_list'][i]['rooms'][j]['devices'])
            existingFlag=self.devicesCatalog.insertDevice(device_ID,device)
        i=True
        return i,j,existingFlag


    def insertDeviceValue(self, platform_ID, room_ID, device_ID, dictionary):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.serverContent['platforms_list'][i]['rooms'])
            j=self.roomsCatalog.findPos(room_ID)
            self.devicesCatalog=DevicesCatalog(self.serverContent['platforms_list'][i]['rooms'][j]['devices'])
            self.devicesCatalog.insertValue(device_ID,dictionary)


    def setRoomParameter(self,platform_ID,room_ID,parameter,parameter_value):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.serverContent['platforms_list'][i]['rooms'])
            result=self.roomsCatalog.setParameter(room_ID,parameter,parameter_value)
            return result
        else:
            return False


    def removePlatform(self,platform_ID):
        i=self.findPos(platform_ID)
        if i is not False:
            self.serverContent['platforms_list'].pop(i) 
            return True
        else:
            return i

    def removeRoom(self,platform_ID,room_ID):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.serverContent['platforms_list'][i]['rooms'])
            result=self.roomsCatalog.removeRoom(room_ID)
            return result
        else:
            return False

    def removeDevice(self,platform_ID,room_ID,device_ID):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.serverContent['platforms_list'][i]['rooms'])
            j=self.roomsCatalog.findPos(room_ID)
            self.devicesCatalog=DevicesCatalog(self.serverContent['platforms_list'][i]['rooms'][j]['devices'])
            result=self.devicesCatalog.removeDevice(device_ID)
            return result
        else:
            return False

    def removeInactive(self,devices,inactiveTime):
        self.devicesCatalog=DevicesCatalog(devices)
        if self.devicesCatalog.removeInactive(inactiveTime):
            return True
        else:
            return False

    def dateUpdate(self,element):
        now=datetime.now()
        new_date=now.strftime("%d/%m/%Y %H:%M")
        element['last_update']=new_date

    def save(self,db_filename):
        with open(db_filename,'w') as file:
            json.dump(self.serverContent,file, indent=4)
