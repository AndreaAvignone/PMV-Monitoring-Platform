import json
from datetime import datetime
import time
from influxdb import InfluxDBClient
from rooms_catalog import RoomsCatalog
from devices_catalog import DevicesCatalog
from computations import *

class NewPlatform():
    def __init__(self,platform_ID,rooms,last_update,local_IP):
        self.platform_ID=platform_ID
        self.rooms=rooms
        self.local_IP=local_IP
        self.lastUpdate=last_update
        
    def jsonify(self):
        platform={'platform_ID':self.platform_ID,"local_IP":self.local_IP,'rooms':self.rooms,'creation_date':self.lastUpdate}
        return platform
    
class Server():
    def __init__(self,db_filename):
        self.db_filename=db_filename
        self.serverContent=json.load(open(self.db_filename,"r"))
        self.myCalculator=Calculator()
        self.comfort_values=["PMV","MRT","PPD","Icl_clo","M_met"]
        
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

    def findParameter(self,platform_ID,room_ID,parameter_name):
        notFound=1
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        try:
            p=room[parameter_name]
            parameter={"parameter":parameter_name,"value":p}
            return parameter
        except:
            for device in room['devices']:
                parameter=self.retrieveParameterInfo(platform_ID,room_ID,device['device_ID'],parameter_name)
                if parameter is not False:
                    notFound=0
                    new_parameter=parameter.copy()
                    new_parameter['device_ID']=device['device_ID']
                    return parameter
            if notFound==1:
                return False

        
    def insertPlatform(self,platform_ID,rooms,local_IP):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        platform=self.retrievePlatform(platform_ID)
        if platform is False:
            createdPlatform=NewPlatform(platform_ID,rooms,timestamp,local_IP).jsonify()
            self.serverContent['platforms_list'].append(createdPlatform)
            return True
        else:
            return False
    def createDB(self, influx_IP,influx_port,platform_ID):
        client=InfluxDBClient(host=influx_IP,port=influx_port)
        client.create_database(platform_ID)
        return True

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
            self.compute_MRT(platform_ID,room_ID)
            self.compute_PMV(platform_ID,room_ID)
            self.compute_PPD(platform_ID,room_ID)

    def compute_MRT(self,platform_ID,room_ID):
        body={}
        errFlag=0
        for p in self.myCalculator.MRT_parameters:
            req=self.findParameter(platform_ID,room_ID,p)
            try:
                body[req['parameter']]=req['value']
            except:
                errFlag=1
        if errFlag!=1:
            mrt=self.myCalculator.MRT_dict(body)
            self.setRoomParameter(platform_ID,room_ID,'MRT',mrt)

    def compute_PMV(self,platform_ID,room_ID):
        body={}
        errFlag=0
        for p in self.myCalculator.PMV_parameters:
            req=self.findParameter(platform_ID,room_ID,p)
            try:
                body[req['parameter']]=req['value']
            except:
                errFlag=1
        if errFlag!=1:
            pmv=self.myCalculator.PMV_dict(body)
            self.setRoomParameter(platform_ID,room_ID,'PMV',pmv)

    def compute_PPD(self,platform_ID,room_ID):
        body={}
        errFlag=0
        for p in self.myCalculator.PPD_parameters:
            req=self.findParameter(platform_ID,room_ID,p)
            try:
                body[req['parameter']]=req['value']
            except:
                errFlag=1
        if errFlag!=1:
        
            ppd=self.myCalculator.PPD_dict(body)
            self.setRoomParameter(platform_ID,room_ID,'PPD',ppd)
    def parse_warning(self,platform_ID,room_ID):
        
        req=self.findParameter(platform_ID,room_ID,"PMV")
        hot_flag=False
        suggestion="TIP: "
        cold_flag=False
        if req['value']<=-2:
            status="COLD"
            cold_flag=True
        elif req['value']>-2 and req['value'] <=-1:
            status="COOL"
            cold_flag=True
        elif req['value']>-1 and req['value']<-0.5:
            status="SLIGHTLY COOL"
            cold_flag=True
        elif req['value']>0.5 and req['value']<1:
            status="SLIGHTLY WARM"
            hot_flag=True
        elif req['value']>=1 and req['value']<2:
            status="WARM"
            hot_flag=True
        elif req['value']>=2:
            status="HOT"
            hot_flag=True
        if hot_flag:
            req_c=self.findParameter(platform_ID,room_ID,"Icl_clo")
            req_w=self.findParameter(platform_ID,room_ID,"wind")
            if req_c['value']>0.5:
                suggestion=suggestion+"Your actual clothing may be not suitable " + "("+str(req_c['value'])+" clo)"+". Try lighter clothes!"
            elif req_w['value']<1:
                suggestion=suggestion+"Air flow speed is low " + "("+str(req_w['value'])+" Km/H)"+". Try opening windows!"
            else:
                suggestion=suggestion+"You should use your cooling system"
                
        if cold_flag:
            req_c=self.findParameter(platform_ID,room_ID,"Icl_clo")
            req_w=self.findParameter(platform_ID,room_ID,"wind")
            req_h=self.findParameter(platform_ID,room_ID,"humidity")
            if req_c['value']<1 and req_w['value']<3 :
                suggestion=suggestion+"Your actual clothing may be not suitable " + "("+str(req_c['value'])+" clo)"+". try warmer clothes!"
            elif req_w['value']>1.5:
                suggestion=suggestion+"Air flow speed is high " + "("+str(req_w['value'])+" Km/H)"+". Check for air currents sources! "
            elif req_h['value']>65:
                 suggestion=suggestion+"Humidity level is high " + "("+str(req_h['value'])+"%)"+". Use a dehumidifier or open the window!"
            else:
                suggestion=suggestion+"You should use your heating system"
                
        return status,suggestion
        

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
        new_date=now.strftime("%d/%m/%Y/%H/%M")
        element['last_update']=new_date

    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.serverContent,file, indent=4)
