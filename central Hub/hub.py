import cherrypy
import json
import sys
import time
import requests

class HUB():
    def __init__(self,db_filename):
        self.db_filename=db_filename
        self.hubContent=json.load(open(self.db_filename,"r"))
        self.service=self.hubContent['service']
        self.serviceCatalogAddress=self.hubContent['service_catalog']
        self.hub_ID=self.hubContent['hub_ID']
        self.rooms=self.hubContent['rooms']
        self.retrieveBroker()
        time.sleep(0.5)
        self.setup()

    def retrieveBroker(self):
        print("Retrieving broker information...")
        try:
            requestBroker=requests.get(self.serviceCatalogAddress+'/broker').json()
            IP=requestBroker.get('IP_address')
            port=requestBroker.get('port')
            msg={"IP_address":IP,"port":int(port)}
            self.hubContent["broker"].append(msg)
            print("Broker info obtained.")
        except:
            print("Broker info not obtained.")
            
    def setup(self):
        print("Connecting...")
        try:
            requestResourcesCatalog=requests.get(self.serviceCatalogAddress+'/server_catalog').json()
            IP=requestResourcesCatalog.get('IP_address')
            port=requestResourcesCatalog.get('port')
            service=requestResourcesCatalog.get('service')
            self.hubContent['server_catalog']=self.buildAddress(IP,port,service)
            json_body={'platform_ID':self.hub_ID,'rooms':self.rooms}
            requests.put(self.hubContent['server_catalog']+'/insertPlatform',json=json_body)
            print("Connection performed")
        except:
            print("Connection failed.")
            return False


    def retrieveInfo(self,parameter):
        try:
            result= self.hubContent[parameter]
        except:
            result=False
        return result

    def retrieveDrivers(self,device_ID):
        notFound=1
        try:
            drivers_list=self.hubContent['drivers']
            for drivers in drivers_list:
                if drivers['device_ID']==device_ID:
                    notFound=0
                    return drivers
            if notFound==1:
                print(f'Drivers for device {device_ID} not found. Downloading...')
                drivers=self.downloadDrivers(device_ID)
                self.hubContent['drivers'].append(drivers)
                print(f'Drivers for device {device_ID} installed.')
                return drivers
        except:
            return False

    def downloadDrivers(self,device_ID):
        try:
            requestDriversCatalog=requests.get(self.serviceCatalogAddress+'/drivers_catalog').json()
            IP=requestDriversCatalog.get('IP_address')
            port=requestDriversCatalog.get('port')
            service=requestDriversCatalog.get('service')
            drivers=requests.get(self.buildAddress(IP,port,service)+'/drivers_list/'+device_ID).json()
            return drivers
        except:
            return False



    def buildAddress(self,IP,port, service):
        finalAddress='http://'+IP+':'+str(port)+service
        return finalAddress


class HUB_REST():
    exposed=True
    def __init__(self,db_filename, IP, port):
        self.hubCatalog=HUB(db_filename)
        self.IP=IP
        self.port=port

    def GET(self, *uri):
        if len(uri)>0:
            parameter=uri[0]
            info=self.hubCatalog.retrieveInfo(parameter)
            if len(uri)>1 and uri[0]=='drivers':
                    device_ID=uri[1]
                    drivers= self.hubCatalog.retrieveDrivers(device_ID)
                    if drivers is not False:
                        output=drivers
                    else:
                        raise cherrypy.HTTPError(404,"Drivers Not found")


            elif len(uri)==1 and uri[0]=='drivers':
                raise cherrypy.HTTPError(405,"You can't!")
            else:
                if info is not False:
                    output=info
                else:
                    raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.hubCatalog.retrieveInfo('description')
        return json.dumps(output) 

if __name__ == '__main__':
    db=sys.argv[1]
    hub=HUB_REST(db,self.hubContent['IP_address'],self.hubContent['port'])
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(hub, hub.hubCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': hub.IP})
    cherrypy.config.update({'server.socket_port': hub.port})
    cherrypy.engine.start()
    while True:
        time.sleep(1)
    cherrypy.engine.block()

