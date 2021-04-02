import json


class ClientsCatalog():
	def __init__(self, db_filename):
		self.db_filename=db_filename
		self.clientsContent=json.load(open(self.db_filename,"r"))
	
	def createDict(self):
		d = self.clientsContent['users_list']
		self.userpassdict = dict((i["user_ID"],i["password"]) for i in d)

	def save(self):
		with open(self.db_filename,'w') as file:
			json.dump(self.profilesContent,file, indent=4)









