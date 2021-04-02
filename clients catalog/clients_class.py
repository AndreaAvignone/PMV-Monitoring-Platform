import json


class ClientsCatalog():
    def __init__(self, db_filename):
        self.db_filename=db_filename
        self.clientsContent=json.load(open(self.db_filename,"r"))
        self.createDict()

    def createDict(self):
        d = self.clientsContent['users_list']
        self.userpassdict = dict((i["user_ID"],i["password"]) for i in d)
        
    def find(self,username):
        for i in range(len(self.clientsContent['users_list'])):
            if self.clientsContent['users_list'][i]['user_ID']==username:
                return self.clientsContent['users_list'][i]
        

    def save(self):
        self.createDict()
        with open(self.db_filename,'w') as file:
            json.dump(self.profilesContent,file, indent=4)









