import json
import time
from datetime import datetime

class NewProfile():
    def __init__(self,platform_ID,platform_name,inactiveTime,preferences, location, lastUpdate):
        self.platform_ID=platform_ID
        self.platform_name=platform_name
        self.inactiveTime=inactiveTime
        self.preferences=preferences
        self.location=location
        self.lastUpdate=lastUpdate
        self.warning="no"
        self.room_cnt=0
        
    def jsonify(self):
        profile={'platform_ID':self.platform_ID,'platform_name':self.platform_name,'warning':self.warning,'room_cnt':self.room_cnt,'inactive_time':self.inactiveTime,'preferences':self.preferences,'location':self.location,'last_update':self.lastUpdate}
        return profile

class ProfilesCatalog():
    def __init__(self, db_filename):
        self.db_filename=db_filename
        self.profilesContent=json.load(open(self.db_filename,"r")) #store the database as a variable
        self.delta=self.profilesContent['delta']
        #self.profilesListCreate()

    def profilesListCreate(self):
        self.profilesList=[]
        for profile in self.profilesContent['profiles']:
            self.profilesList.append(profile['platform_ID'])
        return self.profilesList
    def checkExisting(self,plat_ID,name_list):
        output=False
        for plat in self.profilesContent[name_list]:
            if plat==plat_ID:
                output=True
                break
        return output

    def findPos(self,platform_ID):
        notFound=1
        for i in range(len(self.profilesContent['profiles'])): 
            if self.profilesContent['profiles'][i]['platform_ID']==platform_ID:
                notFound=0
                return i
        if notFound==1:
            return False
    def findRoomPos(self,rooms,room_ID):
        notFound=1
        for i in range(len(rooms)): 
            if rooms[i]['room_ID']==room_ID:
                notFound=0
                return i
        if notFound==1:
            return False

    def retrieveProfileInfo(self,platform_ID):
        notFound=1
        for profile in self.profilesContent['profiles']:
            if profile['platform_ID']==platform_ID:
                notFound=0
                return profile
        if notFound==1:
            return False
    def buildWeatherURL(self,city):
        basic_url=self.profilesContent["weather_api"]
        api_key=self.profilesContent['weather_key']
        url=basic_url+"?q="+city+"&appid="+api_key+"&units=metric"
        return url
    def createBody(self,platform_ID,city,input_body):
        lat=input_body['coord'].get('lat')
        long=input_body['coord'].get('lon')
        condition=input_body['weather'][0].get('main')
        temp=float(input_body['main'].get('temp'))
        temp_feel=float(input_body['main'].get('feels_like'))
        hum=int(input_body['main'].get('humidity'))
        wind_speed=float(input_body['wind'].get('speed'))
        wind_deg=int(input_body['wind'].get('deg'))
        
        final_dict={"lat":lat,"lon":long,"condition":condition,"temp_ext":temp,"temp_ext_feel":temp_feel,"hum_ext":hum,"wind_speed":wind_speed,"wind_deg":wind_deg,"city":city}
        
        rfc=datetime.fromtimestamp(time.time())
        rfc=rfc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        json_body = [{"measurement":"external","tags":{"user":platform_ID},"time":rfc,"fields":final_dict}]
        return json_body

    def retrieveProfileParameter(self,platform_ID,parameter):
        profile=self.retrieveProfileInfo(platform_ID)
        try:
            result= profile[parameter]
        except:
            result=False
        return result

    def insertProfile(self,platform_ID,platform_name,inactiveTime,preferences,location):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is False:
            createdProfile=NewProfile(platform_ID,platform_name,inactiveTime,preferences,location,timestamp).jsonify()
            self.profilesContent['profiles'].append(createdProfile)
            self.profilesContent['profiles_list'].append(platform_ID)
            return True
        else:
            return False

    def insertRoom(self,platform_ID,room_ID,room_info):
        pos=self.findPos(platform_ID)
        roomNotFound=1
        if pos is not False:
            room_cnt=self.retrieveProfileParameter(platform_ID,'room_cnt')+1
            room_info['room_ID']=room_ID+str(room_cnt)
            room_info['connection_flag']=False
            room_info['devices']=[]
            timestamp=time.time()
            room_info['connection_timestamp']=timestamp
            for room in self.profilesContent['profiles'][pos]['preferences']:
                if room['room_name']==room_info['room_name']:
                    roomNotFound=0
                    break
            if roomNotFound==1:
                self.profilesContent['profiles'][pos]['preferences'].append(room_info)
                self.setParameter(platform_ID,'room_cnt',room_cnt)
                return True,room_info
            else:
                return False,False
        else:
            return False,False

    def associateRoom(self,platform_ID,request_timestamp):
        pos=self.findPos(platform_ID)
        notFound=1
        if pos is not False:
            for pref in self.profilesContent['profiles'][pos]['preferences']:
                if pref['connection_flag'] is False and (request_timestamp-pref['connection_timestamp'])<300:
                    pref['connection_flag']=True
                    notFound=0
                    return True,pref
            if notFound==1:
                return False,False
        else:
            return False,False


    def removeProfile(self,platform_ID):
        pos=self.findPos(platform_ID)
        if pos is not False:
            self.profilesContent['profiles_list'].remove(platform_ID)
            self.profilesContent['profiles'].pop(pos) 
            return True
        else:
            return False
    def removeRoom(self,platform_ID,room_ID):
        pos=self.findPos(platform_ID)
        if pos is not False:
            posRoom=self.findRoomPos(self.profilesContent['profiles'][pos]['preferences'],room_ID)
            if posRoom is not False:
                self.profilesContent['profiles'][pos]['preferences'].pop(posRoom)
                return True
            else:
                return False
        else:
            return False
        
        

    def setParameter(self, platform_ID, parameter, parameter_value):
        pos=self.findPos(platform_ID)
        if pos is not False:
            self.profilesContent['profiles'][pos][parameter]=parameter_value
            return True
        else:
            return False
        
    def retrieveRoomInfo(self,rooms,room_ID):
        notFound=1
        for room in rooms:
            if room['room_ID']==room_ID:
                notFound=0
                return room
        if notFound==1:
            return False
    def setRoomParameter(self,platform_ID,room_ID,parameter,parameter_value):
        pos=self.findPos(platform_ID)
        if pos is not False:
            rooms=self.profilesContent['profiles'][pos]["preferences"]
            room=self.retrieveRoomInfo(rooms,room_ID)
            if room is not False:
                room[parameter]=parameter_value
                return True
            else:
                return False
    def createDevicesList(self,platform_ID,room_ID,devices_list):
        pos=self.findPos(platform_ID)
        if pos is not False:
            rooms=self.profilesContent['profiles'][pos]["preferences"]
            room=self.retrieveRoomInfo(rooms,room_ID)
            room["devices"]=[]
            if room is not False:
                for device in devices_list:
                    device_new={}
                    device_new["device_ID"]=device["device_ID"]
                    device_new["last_update"]=(device["timestamp"])
                    device_new["parameters"]=[]
                    for parameter in device['parameters']:
                        parameter_new={}
                        parameter_new["parameter"]=(parameter['parameter'])
                        parameter_new["unit"]=(parameter['unit'])
                        device_new["parameters"].append(parameter_new)
                    room["devices"].append(device_new)
                
                return True
            else:
                return False
        
        
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.profilesContent,file, indent=4)









