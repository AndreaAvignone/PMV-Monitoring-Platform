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
        
    def jsonify(self):
        profile={'platform_ID':self.platform_ID,'platform_name':self.platform_name,'inactiveTime':self.inactiveTime,'preferences':self.preferences,'location':self.location,'last_update':self.lastUpdate}
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

	def removeProfile(self,platform_ID):
		notFound=1
		for i in range(len(self.profilesContent['profiles_list'])): 
			if self.profilesContent['profiles_list'][i]['platform_ID']==platform_ID:
				notFound=0
				self.profilesContent['profiles_list'].pop(i) 
				return True
		if notFound==1:
			return False

	def setParameter(self, platform_ID, parameter, parameter_value):
		notFound=1
		if parameter != "platform_ID":
			for i in range(len(self.profilesContent['profiles_list'])):
				if self.profilesContent['profiles_list'][i]['platform_ID']==platform_ID:
					notFound=0
					pos=i
					break
			if notFound == 0:
				self.profilesContent['profiles_list'][pos][parameter]=parameter_value
				return True
			else:
				return False
		else:
			return False

	def save(self,db_filename):
		with open(db_filename,'w') as file:
			json.dump(self.profilesContent,file, indent=4)









