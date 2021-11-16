import json
import time
import requests
import sys

class RoomConfiguration(object):
    def __init__(self, db_filename):
        self.db_filename=db_filename
        self.roomContent=json.load(open(self.db_filename,"r"))
        self.room_ID=self.roomContent['room_info']['room_ID']
        self.room_name=self.roomContent['room_info']['room_name']
        self.hubAddress=self.roomContent['hub_catalog']
        self.timestamp=time.time()

    def run(self):
        try:
            print("Connecting to Central HUB...")
            time.sleep(1)
            r=requests.get(self.hubAddress+'/hub_ID')
            if r.status_code==200:
                print("Connection performed.")
                self.hub_ID=r.json()
                self.serviceCatalogAddress=requests.get(self.hubAddress+'/service_catalog').json()
            else:
                print("Central HUB connection failed.\n")
        except:
            print("No Central HUB connection available.\n")
            
        
    def findService(self,service):
        r=requests.get(self.serviceCatalogAddress+'/public/'+service).json()
        return self.buildAddress(r.get('IP_address'),r.get('port'),r.get('service'))


    def buildAddress(self,IP,port,service):
        finalAddress=IP+service
        return finalAddress

    def association(self):
        try:
            profilesAddress=self.findService('profiles_catalog')
            json_body={'platform_ID':self.hub_ID,'timestamp':self.timestamp}
            r=requests.put(f'{profilesAddress}/associateRoom/{self.hub_ID}',json=json_body).json()
            if r is not False:
                self.roomContent['room_info']=r
                self.room_ID=self.roomContent['room_info']['room_ID']
                self.room_name=self.roomContent['room_info']['room_name']
                return True
            else:
                return False
        except:
            return False
        
    def connection(self):
        try:
            resourcesAddress=self.findService('server_catalog')
            server_msg={"room_ID":self.room_ID,"room_name":self.room_name,"MRT":None,"Icl_clo":None,"M_met":None,"W_met":None,"devices":self.roomContent['room_info']['devices']}
            requests.put(f'{resourcesAddress}/insertRoom/{self.hub_ID}',json=server_msg)
            return True
        except:
            return False
        
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.roomContent,file,indent=4)

if __name__ == '__main__':
    settings=sys.argv[1]
    room=RoomConfiguration(settings)
    room.run()
    if room.association():
        print(f"Association performed - {room.room_ID}: {room.room_name}")
        if room.connection():
        print("Server connection performed. Saving...")
        room.save()
        else:
            print("Error connection.")
    else:
        print("Association failed.")

   

