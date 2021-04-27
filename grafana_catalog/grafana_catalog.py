import cherrypy
import json
import requests
import time
import sys
from grafana_class import GrafanaCatalog

class GrafanaCatalogREST():
    exposed=True
    def  __init__(self, org_db_filename):
        self.grafanaCatalog=GrafanaCatalog(org_db_filename)
        self.serviceCatalogAddress=self.grafanaCatalog.orgContent['service_catalog']
        self.grafanaCatalogIP=self.grafanaCatalog.orgContent['IP_address']
        self.grafanaCatalogPort=self.grafanaCatalog.orgContent['port']
        self.service=self.registerRequest()

    def registerRequest(self):
        msg={"service":"grafana_catalog","IP_address":self.grafanaCatalogIP,"port":self.grafanaCatalogPort}
        try:
            service=requests.put(f'{self.serviceCatalogAddress}/register',json=msg).json()
            return service
        except:
            print("Failure in registration.")
            return False
    def getServer(self):
        requestResult=requests.get(self.serviceCatalogAddress+"/server_catalog").json()
        self.serverCatalogIP=requestResult.get("IP_address")
        self.serverCatalogPort=requestResult.get("port")
        self.serverService=requestResult.get("service")
        self.serverURL=self.buildAddress(self.serverCatalogIP,self.serverCatalogPort,self.serverService)
    def buildAddress(self,IP,port, service):
        finalAddress='http://'+IP+':'+str(port)+service
        return finalAddress
   
    def GET(self, *uri):
        uriLen=len(uri)
        if uriLen!=0:
            cmd=str(uri[0])
            if cmd=='organization':
                org=self.grafanaCatalog.retrieveOrgInfo(uri[1])
                if org is not False:
                    output=org
                else:
                    output=self.grafanaCatalog.orgContent.get(uri[1])
                if output==None:
                    raise cherrypy.HTTPError(404, "Information not found")
            if cmd=='user':
                user=self.grafanaCatalog.retrieveUserInfo(uri[1])
                if user is not False:
                    output=user
                else:
                    output=self.grafanaCatalog.usersContent.get(uri[1])
                if output==None:
                    raise cherrypy.HTTPError(404, "Information not found")
            if cmd=='dashboard':
                dashboard_url=self.grafanaCatalog.retrieveDashInfo(uri[1], uri[2])
                if dashboard_url is not False:
                    output=dashboard_url
                else:
                    ouput=None
                if output==None:
                    raise cherrypy.HTTPError(404, "Information not found")
            if cmd=='home':
                home_url=self.grafanaCatalog.getHomeURL(uri[1])
                if home_url is not False:
                    output=home_url
                else:
                    ouput=None
                if output==None:
                    raise cherrypy.HTTPError(404, "Information not found")
        else:
            output=self.grafanaCatalog.orgContent['description']

        return json.dumps(output)

    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        ack=False
        saveFlag=False
        if command=='insertOrganization':
            platform_ID=json_body['platform_ID']
            newOrg=self.grafanaCatalog.insertOrg(platform_ID)
            if newOrg==True:
                output="Organization '{}' has been added to Organization Database".format(platform_ID)
                saveFlag=True
                ack=True
            else:
                output="'{}' already exists!".format(platform_ID)
        elif command=='insertDashboard':
            platform_ID=uri[1]
            room_ID=json_body['room_ID']
            dashboard_title=json_body['dashboard_title']
            newDash=self.grafanaCatalog.insertDashboard(platform_ID,room_ID,json_body)
            if newDash==True:
                output="Dashboard '{}' has been added to Organization '{}'".format(dashboard_title,platform_ID)
                saveFlag=True
                ack=newDash
            else:
                output="Dashboard '{}' cannot be added to Organization '{}'".format(dashboard_title,platform_ID)
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag==True:
            self.grafanaCatalog.save()
        print(output)
        return json.dumps(ack)

    def DELETE(self, *uri):
        command=str(uri[0])
        if command=='deleteDashboard':
            platform_ID=uri[1]
            room_ID=uri[2]
            deleatedDashboard=self.grafanaCatalog.deleteDashboard(platform_ID,room_ID)
            if deleatedDashboard==True:
                output="Dashboard '{}' from Platform '{}' removed".format(room_ID,platform_ID)
                result={"result":True}
            else:
                output="Dashboard '{}' from Platform '{}' not removed ".format(room_ID,platform_ID)
                result={"result":False}
            print(output)
            return json.dumps(result)  
        else:
            raise cherrypy.HTTPError(501, "No operation!")
                
                


if __name__=='__main__':
    org_db=sys.argv[1]
    grafanaCatalog=GrafanaCatalogREST(org_db)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(grafanaCatalog, grafanaCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': grafanaCatalog.grafanaCatalogIP})
    cherrypy.config.update({'server.socket_port': grafanaCatalog.grafanaCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()



