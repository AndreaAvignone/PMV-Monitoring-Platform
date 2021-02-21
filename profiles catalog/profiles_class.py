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
        self.room_cnt=1
        
    def jsonify(self):
        profile={'platform_ID':self.platform_ID,'platform_name':self.platform_name,'room_cnt':self.room_cnt,'inactiveTime':self.inactiveTime,'preferences':self.preferences,'location':self.location,'last_update':self.lastUpdate}
        return profile

class ProfilesCatalog():
	def __init__(self, db_filename):
		self.db_filename=db_filename
		self.profilesContent=json.load(open(self.db_filename,"r")) #store the database as a variable
		#self.profilesListCreate()

	def profilesListCreate(self):
		self.profilesList=[]
		for profile in self.profilesContent['profiles_list']:
			self.profilesList.append(profile['platform_ID'])
		return self.profilesList

	def findPos(self,platform_ID):
		notFound=1
		for i in range(len(self.profilesContent['profiles_list'])): 
			if self.profilesContent['profiles_list'][i]['platform_ID']==platform_ID:
				notFound=0
				return i
		if notFound==1:
			return False

	def retrieveProfileInfo(self,platform_ID):
		notFound=1
		for profile in self.profilesContent['profiles_list']:
			if profile['platform_ID']==platform_ID:
				notFound=0
				return profile
		if notFound==1:
			return False

	def retrieveProfileParameter(self,platform_ID,parameter):
		profile=self.retrieveProfileInfo(platform_ID)
		try:
			result= profile[parameter]
		except:
			result=False
		return result

	def insertProfile(self,platform_ID,platform_name,inactiveTime,preferences, location):
		notExisting=1
		now=datetime.now()
		timestamp=now.strftime("%d/%m/%Y %H:%M")
		profile=self.retrieveProfileInfo(platform_ID)
		if profile is False:
			createdProfile=NewProfile(platform_ID,platform_name,inactiveTime,preferences,location,timestamp).jsonify()
			self.profilesContent['profiles_list'].append(createdProfile)
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
			for room in self.profilesContent['profiles_list'][pos]['preferences']:
				if room['room_name']==room_info['room_name']:
					roomNotFound=0
					break
			if roomNotFound==1:
				self.profilesContent['profiles_list'][pos]['preferences'].append(room_info)
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
			for pref in self.profilesContent['profiles_list'][pos]['preferences']:
				if pref['connection_flag'] is False and (request_timestamp-pref['connection_timestamp'])<60:
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
			self.profilesContent['profiles_list'].pop(i) 
			return True
		else:
			return False

	def setParameter(self, platform_ID, parameter, parameter_value):
		pos=self.findPos(platform_ID)
		if pos is not False:
			self.profilesContent['profiles_list'][pos][parameter]=parameter_value
			return True
		else:
			return False

	def save(self):
		with open(self.db_filename,'w') as file:
			json.dump(self.profilesContent,file, indent=4)









