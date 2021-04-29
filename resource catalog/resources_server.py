import cherrypy
import json
import requests
import time
import sys
from serverClass import *

class ResourcesServerREST(object):
    exposed=True
    def __init__(self,db_filename):
        self.serverCatalog=Server(db_filename)
        self.serviceCatalogAddress=self.serverCatalog.serverContent['service_catalog']
        self.serverCatalogIP=self.serverCatalog.serverContent['IP_address']
        self.serverCatalogPort=self.serverCatalog.serverContent['port']
        self.service=self.registerRequest()

    def registerRequest(self):
        msg={"service":"server_catalog","IP_address":self.serverCatalogIP,"port":self.serverCatalogPort}
        try:
            service=requests.put(f'{self.serviceCatalogAddress}/register',json=msg).json()
            return service
        except:
            print("Failure in registration.")
            return False

    def buildAddress(self,IP,port, service):
        finalAddress='http://'+IP+':'+str(port)+service
        return finalAddress

    def GET(self,*uri,**params):
        uriLen=len(uri)
        if uriLen!=0:
            info=uri[0]
            platform= self.serverCatalog.retrievePlatform(info)
            if platform is not False:
                if uriLen>1:
                    roomInfo= self.serverCatalog.retrieveRoomInfo(info,uri[1])
                    if roomInfo is not False:
                        if uriLen>2:
                            deviceInfo=self.serverCatalog.retrieveDeviceInfo(info,uri[1],uri[2])
                            if deviceInfo is not False:
                                if uriLen>3:
                                    output=deviceInfo.get(uri[3])
                                elif len(params)!=0:
                                    parameter=str(params['parameter'])
                                    parameterInfo=self.serverCatalog.retrieveParameterInfo(info,uri[1],uri[2],parameter)
                                    if parameterInfo is False:
                                        output=None
                                    else:
                                        output=parameterInfo
                                else:
                                    output=deviceInfo

                            else:
                                output=roomInfo.get(uri[2])

                        elif len(params)!=0:
                            parameter=str(params['parameter'])
                            parameterInfo=self.serverCatalog.findParameter(info,uri[1],parameter)
                            if parameterInfo is False:
                                output=None
                            else:
                                output=parameterInfo

                        else:
                            output=roomInfo
                    else:
                        output=platform.get(uri[1])
                else:
                    output=platform
            else:
                output=self.serverCatalog.serverContent.get(info)
            if output==None:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.serverCatalog.serverContent['description']

        return json.dumps(output) 

    def PUT(self,*uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        saveFlag=False
        res=[]
        if command=='insertPlatform':
            requestProfiles=requests.get(self.serviceCatalogAddress+"/profiles_catalog").json()
            IP=requestProfiles.get('IP_address')
            port=requestProfiles.get('port')
            service=requestProfiles.get('service')
            platform_ID=json_body['platform_ID']
            if(requests.get(self.buildAddress(IP,port,service)+'/checkRegistered/'+platform_ID)):
                rooms=[]
                newPlatform=self.serverCatalog.insertPlatform(platform_ID,rooms)
                if newPlatform==True:
                    output="Platform '{}' has been added to Server\n".format(platform_ID)
                    self.requestInflux=requests.get(self.serviceCatalogAddress+"/influx_db").json()
                    self.influx_IP=self.requestInflux.get('IP_address')
                    self.influx_port=self.requestInflux.get('port')
                    
                    if self.serverCatalog.createDB(self.influx_IP,self.influx_port,platform_ID):
                        output=output+"Influx database created\n"
                        requestGrafana=requests.get(self.serviceCatalogAddress+"/grafana_catalog").json()
                        print(requestGrafana)
                        self.grafana_IP=requestGrafana.get('IP_address')
                        self.grafana_port=requestGrafana.get('port')
                        self.grafana_service=requestGrafana.get('service')
                        org_body={"platform_ID":platform_ID}
                        newOrg=requests.put(self.buildAddress(self.grafana_IP,self.grafana_port,self.grafana_service)+"/insertOrganization",json=org_body)
                        print(newOrg)
                        if newOrg:
                            output=output+"Grafana organizion created"
                            saveFlag=True
                        
                else:
                    output="'{}' already exists!".format(platform_ID)
            else:
                output="'{}' cannot be connected".format(platform_ID)
        elif command=='insertRoom':
            platform_ID=uri[1]
            room_ID=json_body['room_ID']
            room_name=json_body['room_name']
            platformFlag,newRoom=self.serverCatalog.insertRoom(platform_ID,room_ID,json_body)
            if platformFlag is False:
                raise cherrypy.HTTPError(404,"Platform Not found")
            else:
                if newRoom==True:
                    requestGrafana=requests.get(self.serviceCatalogAddress+"/grafana_catalog").json()
                    self.grafana_IP=requestGrafana.get('IP_address')
                    self.grafana_port=requestGrafana.get('port')
                    self.grafana_service=requestGrafana.get('service')
                    dash_body={"room_ID":room_ID,"dashboard_title":room_name}
                    newDash=requests.put(self.buildAddress(self.grafana_IP,self.grafana_port,self.grafana_service)+"/insertDashboard/",json=dash_body)
                    if newDash:
                        output="Platform '{}' - Room '{}' has been added to Server".format(platform_ID, room_ID)
                        saveFlag=True
                    else:
                        output="Dashboard creation error"
                        self.serverCatalog.removeRoom(platform_ID,room_ID)
                        res.append("false")
                else:
                    output="Platform '{}' - Room '{}' already exists. Resetting...".format(platform_ID,room_ID)
        elif command=='insertDevice':
            platform_ID=uri[1]
            room_ID=uri[2]
            device_ID=json_body['device_ID']
            platformFlag, roomFlag, newDevice=self.serverCatalog.insertDevice(platform_ID,room_ID,device_ID,json_body)
            if platformFlag is False:
                raise cherrypy.HTTPError(404,"Platform Not found")
            if roomFlag is False:
                raise cherrypy.HTTPError(404,"Room Not found")
            else:
                if newDevice==True:
                    output="Platform '{}' - Room '{}' - Device '{}' has been added to Server".format(platform_ID, room_ID,device_ID)
                    self.serverCatalog.dateUpdate(self.serverCatalog.retrieveRoomInfo(platform_ID,room_ID))
                    saveFlag=True
                else:
                    output="Platform '{}' - Room '{}' - Device '{}' already exists. Updating...".format(platform_ID,room_ID,device_ID)
        elif command=='insertValue':
            platform_ID=uri[1]
            room_ID=uri[2]
            device_ID=uri[3]
            try:
                newValue=self.serverCatalog.insertDeviceValue(platform_ID, room_ID, device_ID,json_body)
                output="Platform '{}' - Room '{}' - Device '{}': parameters updated".format(platform_ID, room_ID, device_ID)
                
                for index in self.serverCatalog.comfort_values:
                    p=self.serverCatalog.findParameter(platform_ID,room_ID,index)
                    res.append({"parameter":p['parameter'],"value":p['value']})
            except:
                output=None
            saveFlag=True


        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.serverCatalog.save()
        if output is not None:
            print(output)
        return json.dumps(res)



    def POST(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        saveFlag=False
        if command=='setParameter':
            platform_ID=uri[1]
            room_ID=str(uri[2])
            parameter=json_body['parameter']
            parameter_value=json_body['parameter_value']
            newSetting=self.serverCatalog.setRoomParameter(platform_ID,room_ID,parameter,parameter_value)
            if newSetting==True:
                output="Platform '{}' - Room '{}': {} is now {}".format(platform_ID, room_ID, parameter,parameter_value)
                self.serverCatalog.compute_PMV(platform_ID,room_ID)
                self.serverCatalog.compute_PPD(platform_ID,room_ID)
                saveFlag=True
            else:
                output="Platform '{}' - Room '{}': Can't change {} ".format(platform_ID, room_ID,parameter)
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.serverCatalog.save()
        print(output)


    def DELETE(self,*uri):
        saveFlag=False
        uriLen=len(uri)
        if uriLen>0:
            platform_ID=uri[0]
            if uriLen>1:
                room_ID=uri[1]
                if uriLen>2:
                    device_ID=uri[2]
                    removedDevice=self.serverCatalog.removeDevice(platform_ID,room_ID,device_ID)
                    if removedDevice==True:
                        output="Platform '{}' - Room '{}' - Device '{}' removed".format(platform_ID,room_ID,device_ID)
                        self.serverCatalog.dateUpdate(self.serverCatalog.retrieveRoomInfo(platform_ID,room_ID))
                        saveFlag=True
                    else:
                        output="Platform '{}'- Room '{}' - Device '{}' not found ".format(platform_ID,room_ID,device_ID)
                else:
                    self.grafana_IP=requestGrafana.get('IP_address')
                    self.grafana_port=requestGrafana.get('port')
                    self.grafana_service=requestGrafana.get('service')
                    removedDash=requests.delete(self.buildAddress(self.grafana_IP,self.grafana_port,self.grafana_service)+"/deleteDashboard/"+platform_ID+"/"+room_ID)
                    if removedDash['result']:
                        removedRoom=self.serverCatalog.removeRoom(platform_ID,room_ID)
                        if removedRoom==True:

                            output="Platform '{}' - Room '{}' removed".format(platform_ID,room_ID)
                            saveFlag=True
                        else:
                            output="Platform '{}'- Room '{}' not found ".format(platform_ID,room_ID)
                    else:
                        output="Error in removing dashboard"
            else:
                removedPlatform=self.serverCatalog.removePlatform(platform_ID) 
                if removedPlatform==True:
                    output="Platform '{}' removed".format(platform_ID)
                    saveFlag=True
                else:
                    output="Platform '{}' not found ".format(platform_ID)
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.serverCatalog.save()
        print(output)


if __name__ == '__main__':
    db=sys.argv[1]
    server=ResourcesServerREST(db)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(server, server.service, conf)
    cherrypy.config.update({'server.socket_host': server.serverCatalogIP})
    cherrypy.config.update({'server.socket_port': server.serverCatalogPort})
    cherrypy.engine.start()
    while True:
        for platform in server.serverCatalog.serverContent['platforms_list']:
            try:
                requestProfiles=requests.get(server.serviceCatalogAddress+"/profiles_catalog").json()
                IP=requestProfiles.get('IP_address')
                port=requestProfiles.get('port')
                service=requestProfiles.get('service')
                try:
                    inactiveTime=requests.get(server.buildAddress(IP,port,service)+'/'+platform['platform_ID']+'/inactive_time').json()
                    for room in platform['rooms']:
                        try:
                            result=server.serverCatalog.removeInactive(room['devices'],inactiveTime)
                            if result is not False:
                                output="Room {} - Platform {}".format(room['room_ID'],platform['platform_ID'])
                                print(output)
                                server.serverCatalog.dateUpdate(room)
                                server.serverCatalog.save()

                        except:
                            pass
                except:
                    print(f"Impossible to reach profile for platform {platform['platform_ID']}")

            except:
                print("Services communication is not working")

            

        time.sleep(30)
    cherrypy.engine.block()

