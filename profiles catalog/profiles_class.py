import json

class ProfilesCatalog():
	def __init__(self, db_filename):
		self.db_filename=db_filename
		self.profilesContent=json.load(open(self.db_filename,"r")) #store the database as a variable
		self.ProfilesListCreate()

	def ProfilesListCreate(self):
		self.profilesList=[]
		for profile in self.profilesContent['profiles_list']:
			self.profilesList.append(profile['platform_ID'])
		return self.profilesList

	def RetrieveProfileInfo(self,platform_ID):
		notFound=1
		for profile in self.profilesContent['profiles_list']:
			if profile['platform_ID']==platform_ID:
				notFound=0
				return profile
		if notFound==1:
			return False

	def RetrieveProfileParameter(self,platform_ID,parameter):
		profile=self.RetrieveProfileInfo(platform_ID)
		try:
			result= profile[parameter]
		except:
			result=False
		return result




