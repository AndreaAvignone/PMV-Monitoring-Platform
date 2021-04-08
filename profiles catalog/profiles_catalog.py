import cherrypy
import json
import requests
import time
import sys
from profiles_class import ProfilesCatalog
class ProfilesCatalogREST():
    exposed=True
    def __init__(self,db_filename):
        self.profilesCatalog=ProfilesCatalog(db_filename)
        self.serviceCatalogAddress=self.profilesCatalog.profilesContent['service_catalog']
        self.requestResult=requests.get(self.serviceCatalogAddress+"/profiles_catalog").json()
        self.profilesCatalogIP=self.requestResult.get("IP_address")
        self.profilesCatalogPort=self.requestResult.get("port")
        self.service=self.requestResult.get("service")
    def getServer(self):
        requestResult=requests.get(self.serviceCatalogAddress+"/server_catalog").json()
        self.serverCatalogIP=requestResult.get("IP_address")
        self.serverCatalogPort=requestResult.get("port")
        self.serverService=requestResult.get("service")
        self.serverURL=self.buildAddress(self.serverCatalogIP,self.serverCatalogPort,self.serverService)
    def buildAddress(self,IP,port, service):
        finalAddress='http://'+IP+':'+str(port)+service
        return finalAddress
    def serverRequest(self,platform_ID,room_ID,info):
        self.getServer()
        result=requests.get(self.serverURL+'/'+platform_ID+'/'+room_ID+'/'+info).json()
        return result
    def GET(self,*uri):
        uriLen=len(uri)
        if uriLen!=0:
            profile= self.profilesCatalog.retrieveProfileInfo(uri[0])
            if profile is not False:
                if uriLen>1:
                    if uri[1]=="preferences":
                        for room in profile["preferences"]:
                            try:
                                devices=self.serverRequest(uri[0],room["room_ID"],"devices")
                                self.profilesCatalog.createDevicesList(uri[0],room["room_ID"],devices)
                            except:
                                pass
                    profileInfo= self.profilesCatalog.retrieveProfileParameter(uri[0],uri[1])
                    if uriLen==3:
                        try:
                            pos=self.profilesCatalog.findRoomPos(profileInfo,uri[2])
                            profileInfo=profileInfo[pos]
                        except:
                            pass
                    if profileInfo is not False:
                        output=profileInfo
                    else:
                        output=profile.get(uri[1])
                else:
                    output=profile
            else:
                output=self.profilesCatalog.profilesContent.get(uri[0])
            if output==None:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.profilesCatalog.profilesContent['description']

        return json.dumps(output) 

    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        ack=False
        saveFlag=False
        if command=='insertProfile':
            platform_ID=json_body['platform_ID']
            platform_name=json_body['platform_name']
            inactiveTime=json_body['inactiveTime']
            preferences=json_body['preferences']
            location=json_body['location'] 
            newProfile=self.profilesCatalog.insertProfile(platform_ID,platform_name,inactiveTime,preferences,location)
            if newProfile==True:
                output="Profile '{}' has been added to Profiles Database".format(platform_ID)
                saveFlag=True
                ack=True
            else:
                output="'{}' already exists!".format(platform_ID)
        #from app
        elif command=='insertRoom':
            platform_ID=uri[1]
            room_ID=json_body['room_ID']
            room_name=json_body['room_name']
            newRoomFlag,newRoom=self.profilesCatalog.insertRoom(platform_ID,room_ID,json_body)
            if newRoomFlag==True:
                output="Room '{}' has been added to platform '{}'".format(room_name,platform_ID)
                saveFlag=True
                ack=newRoom
            else:
                output="Room '{}' cannot be added to platform '{}'".format(room_name,platform_ID)
        elif command=='associateRoom':
            platform_ID=uri[1]
            associatedRoomFlag,associatedRoom=self.profilesCatalog.associateRoom(platform_ID,json_body['timestamp'])
            if associatedRoomFlag==True:
                output="Room '{}' has been assoicated in platform '{}'".format(associatedRoom['room_name'],platform_ID)
                ack=associatedRoom
                saveFlag=True
            else:
                output="Association failed in platform '{}'".format(platform_ID)


        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag==True:
            self.profilesCatalog.save()
        print(output)
        return json.dumps(ack)
		

    def POST(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        if command=='setParameter':
            platform_ID=uri[1]
            parameter=json_body['parameter']
            parameter_value=json_body['parameter_value']
            newSetting=self.profilesCatalog.setParameter(platform_ID,parameter,parameter_value)
            if newSetting==True:
                output="Platform '{}': {} is now {}".format(platform_ID, parameter,parameter_value)
                self.profilesCatalog.save()
            else:
                output="Platform '{}': Can't change {} ".format(platform_ID, parameter)
            print(output)
        elif command=='setRoomParameter':
            platform_ID=uri[1]
            room_ID=uri[2]
            parameter=json_body['parameter']
            parameter_value=json_body['parameter_value']
            newSetting=self.profilesCatalog.setRoomParameter(platform_ID,room_ID,parameter,parameter_value)
            if newSetting==True:
                output="Platform '{}' - Room '{}': {} is now {}".format(platform_ID,room_ID, parameter,parameter_value)
                self.profilesCatalog.save()
            else:
                output="Platform '{}' Room '{}': Can't change {} ".format(platform_ID, room_ID,parameter)
            print(output)

            
        else:
            raise cherrypy.HTTPError(501, "No operation!")

    def DELETE(self,*uri):
        command=str(uri[0])
        if command=='removeProfile':
            platform_ID=uri[1]
            removedProfile=self.profilesCatalog.removeProfile(platform_ID) 
            if removedProfile==True:
                output="Profile '{}' removed".format(platform_ID)
                self.profilesCatalog.save()
            else:
                output="Profile '{}' not found ".format(platform_ID)
            print(output)
        else:
            raise cherrypy.HTTPError(501, "No operation!")

        
if __name__ == '__main__':
    db=sys.argv[1]
    profilesCatalog=ProfilesCatalogREST(db)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(profilesCatalog, profilesCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': profilesCatalog.profilesCatalogIP})
    cherrypy.config.update({'server.socket_port': profilesCatalog.profilesCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()