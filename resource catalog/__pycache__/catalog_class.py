import json
from datetime import datetime
import time
from rooms_catalog import RoomsCatalog
        
class CatalogManager():
    def __init__(self,myCatalog):
        self.myCatalog=myCatalog
        self.roomsCatalog=RoomsCatalog(self.myCatalog['rooms'])
        
    def retrieveClientID(self):
        clientID=self.myCatalog["clientID"]
        return clientID
    def retrieveInactiveTime(self):
        inactiveTime=self.myCatalog["inactiveTime"]
        return inactiveTime
    
    def retrieveCatalogID(self):
        catalogID=self.myCatalog["catalogID"]
        return catalogID
        
    def retrieveBroker(self):
        broker=self.myCatalog["broker"]
        return broker

    def changeClientID(self,newClientID):
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        clientID=self.myCatalog['clientID']
        self.myCatalog['clientID']=newClientID
        self.dateUpload(timestamp)
        result="'{}' changed to '{}'".format(clientID,newClientID) 
        return result
   
    def retrieveAllCatalog(self):
        return self.myCatalog
    
    def dateUpload(self,dt_string):
        self.myCatalog['last_update']=dt_string

