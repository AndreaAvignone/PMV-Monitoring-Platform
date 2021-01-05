from catalog_class import * 
import cherrypy
import json
from datetime import datetime
import sys
from catalog_class import CatalogManager
from devices_catalog import DevicesCatalog
from rooms_catalog import RoomsCatalog
from serverClass import Server

class DatabaseManager(object):
    exposed=True
    
    def __init__(self,databaseFileName):
            self.databaseFileName=databaseFileName
            self.jsonFile = open(self.databaseFileName, "r") # Open the JSON file for reading 
            self.myDatabase = json.load(self.jsonFile) # Read the JSON into the buffer
            #self.jsonFile.close() # Close the JSON file
            self.addressIP=self.myDatabase['server'][0].get('addressIP')
            self.port=self.myDatabase['server'][0].get('port')
            self.server= Server(self.myDatabase,self.databaseFileName)
            print("\n%% Running Server %%\n")
            
    def GET(self,*uri,**params):
        result=False
        if len(uri)!=0:
            if uri[0]=='owner':
                result=self.server.retrieveOwner()
            elif uri[0]=='clientsList':
                result=self.server.retrieveClientsList()
            elif uri[0]=='catalogs':
                try:
                    catalogID=str(uri[1])
                    self.actualCatalog=self.server.retrieveCatalogID(catalogID)
                    try:
                        self.c=CatalogManager(self.actualCatalog)
                        resource= str(uri[2])
                        if resource=='clientID':
                            result=self.c.retrieveClientID()
                        elif resource=='catalogID':
                            result=self.c.retrieveCatalogID()
                        elif resource=='inactiveTime':
                            result=self.c.retrieveInactiveTime()
                        elif resource=='broker':
                            result=self.c.retrieveBroker()
                        elif resource=='roomsList':
                            result=self.c.roomsCatalog.retrieveRoomsList()
                        elif resource=='rooms':  
                            try:
                                roomID=str(uri[3])
                                self.actualRoom=self.c.roomsCatalog.retrieveRoomID(roomID)
                                try:
                                    self.d=DevicesCatalog(self.actualRoom)
                                    if str(uri[4])=="devices":
                                        try:
                                            deviceID=str(uri[5])
                                            try:
                                                parameter=str(params['parameter'])
                                                try:
                                                    result=self.d.retrieveValue(deviceID,parameter)
                                                except:
                                                    result=False
                                            except:
                                                result=self.d.retrieveDeviceID(deviceID)
                                            
                                        except:
                                            result=self.d.retrieveAllDevices()
                                
                                except:
                                    result=self.actualRoom

                            except:
                                result=self.c.roomsCatalog.retrieveAllRooms()
                    except:
                        result=self.actualCatalog
                except:
                    result=self.server.retrieveAllClients()

            else:
                raise cherrypy.HTTPError(501, "No operation!")
            if result==False:
                raise cherrypy.HTTPError(404,"Not found")
            else:
                return json.dumps(result,indent=4) 
            
    def PUT (self, *uri, ** params):
        # UNDERSTAND REQUEST BODY
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        #print(json_body)
        command=str(uri[0])
        if command=='insertCatalog':
            newCatalogID=json_body['catalogID']
            inactiveTime=json_body['inactiveTime']
            clientID=json_body['clientID']
            broker=json_body['broker']
            rooms=json_body['rooms']  
            newCatalog=self.server.insertCatalog(newCatalogID,inactiveTime,clientID,broker,rooms)
            if newCatalog==True:
                output="Catalog '{}' has been added to Database".format(newCatalogID)
            else:
                output="'{}' already exists! Resetting...".format(newCatalogID)

        else:
            catalogID= str(uri[1])
            now=datetime.now()
            timestamp=now.strftime("%d/%m/%Y %H:%M")
            self.actualCatalog=self.server.retrieveCatalogID(catalogID)
            self.c=CatalogManager(self.actualCatalog)
            
            if command=='insertRoom':
                roomID=json_body['roomID']
                roomName=json_body['roomName']
                thingSpeakURL=json_body['thingSpeakURL']
                devices=json_body['devices']
                newRoom=self.c.roomsCatalog.insertRoom(roomID,roomName,devices,thingSpeakURL)
                if newRoom==True:
                    output="Room '{}' has been added to Catalogue".format(roomID)
                    self.c.dateUpload(timestamp)
                else:
                    output="'{}' already exists-updated".format(roomID)
                
            elif command=='changeRoomName':     
                roomID=json_body['roomID']
                newRoomName=json_body['newRoomName']
                output=self.c.roomsCatalog.changeRoomName(roomID,newRoomName)

            elif command=='changeClientID':
                newClientID=json_body['newClientID']
                output=self.c.changeClientID(newClientID)
            
            elif command=='insertDevice':
                roomID=str(params['room'])
                self.actualRoom=self.c.roomsCatalog.retrieveRoomID(roomID)
                if self.actualRoom is not False:
                    self.d=DevicesCatalog(self.actualRoom)
                    newDev=self.d.insertDevice(json_body['sensorID'], json_body['end_points'], json_body['parameters'])
                    if newDev==True:
                        output="Device {} in {} has been added to Catalogue".format(json_body['sensorID'],roomID)
                    else:
                        output="Catalog updated: {}-{}".format(json_body['sensorID'],roomID)
                    self.c.roomsCatalog.dateRoomUpdate(roomID,timestamp)
                else:
                    output=False 
            
            elif command=='insertValue':
                roomID=json_body['roomID']
                self.actualRoom=self.c.roomsCatalog.retrieveRoomID(roomID)
                if self.actualRoom is not False:
                    self.d=DevicesCatalog(self.actualRoom)
                    output=self.d.insertValue(json_body['sensorID'],json_body['parameter'],json_body['value'])
                    self.c.roomsCatalog.dateRoomUpdate(roomID,timestamp)
                else:
                    output=False
        
        self.server.save(self.databaseFileName)
        if output is not False:
            print(output)
        else:
            print("Room not found")


    def DELETE(self, *uri, ** params):
        command=str(uri[0])
        catalogID=str(uri[1])
        self.actualCatalog=self.server.retrieveCatalogID(catalogID)
        self.c=CatalogManager(self.actualCatalog)
        if command== 'removeDevice':
            roomID=str(params['room'])
            deviceID=str(params['device'])
            self.actualRoom=self.c.roomsCatalog.retrieveRoomID(roomID)
            self.d=DevicesCatalog(self.actualRoom)
            result=self.d.removeDevice(deviceID)
            if result==True:
                output=f"Device with ID {deviceID} has been removed"
                print (output)
            else:
                raise cherrypy.HTTPError(404,"Not found")
            
        elif command=='removeRoom':
            roomID=str(params['room'])
            result=self.c.roomsCatalog.removeRoom(roomID)
            if result==True:
                output=f"Room with ID {roomID} has been removed"
                now=datetime.now()
                timestamp=now.strftime("%d/%m/%Y %H:%M")
                self.c.dateUpload(timestamp)
                print (output)
            else:
                raise cherrypy.HTTPError(404,"Not found") 
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        self.server.save(self.databaseFileName)


if __name__ == '__main__':
    settings=sys.argv[1]
    database=DatabaseManager(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(database, '/leaf', conf)
    cherrypy.config.update({'server.socket_host': database.addressIP })
    cherrypy.config.update({'server.socket_port': database.port})
    cherrypy.engine.start()
    while True:
        for catalog in database.myDatabase['clients']:
            for room in catalog['rooms']:
                d=DevicesCatalog(room)
                d.removeInactive(catalog['inactiveTime'])
            time.sleep(2)
        database.server.save(settings)
    cherrypy.engine.block()


