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
        notFound=1
        for i in range(len(self.clientsContent['users_list'])):
            if self.clientsContent['users_list'][i]['user_ID']==username:
                notFound=0
                break
        if notFound==1:
            return False
        else:
            return self.clientsContent['users_list'][i]
    def addPlatform(self,username,platform_ID):
        user=self.find(username)
        if user is not False:
            if platform_ID not in user['catalog_list']:
                user['catalog_list'].append(platform_ID)
                return True
            else:
                return False
        else:
            return False
    def removePlatform(self,username,platform_ID):
        user=self.find(username)
        if user is not False:
            if platform_ID in user['catalog_list']:
                user['catalog_list'].remove(platform_ID)
                return True
            else:
                return False
        else:
            return False
        

    def save(self):
        self.createDict()
        with open(self.db_filename,'w') as file:
            json.dump(self.clientsContent,file, indent=4)









