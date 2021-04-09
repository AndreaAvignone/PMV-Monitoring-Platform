import cherrypy
import json
import requests
import time
import sys
from feedback_class import *

class feedbackREST():
    exposed=True

    def __init__(self,db_filename):
        #configure the service catalog according to information stored inside database
        self.feedbackCatalog=FeedbackCatalog(db_filename)
        self.serviceCatalogAddress=self.feedbackCatalog.feedbackContent['service_catalog']
        self.requestResult=requests.get(self.serviceCatalogAddress+"/feedback_catalog").json()
        self.feedbackCatalogIP=self.requestResult.get("IP_address")
        self.feedbackCatalogPort=self.requestResult.get("port")
        self.service=self.requestResult.get("service")
        
    def GET(self,*uri):
        uriLen=len(uri)
        if uriLen!=0:
            info=uri[0]
            platform= self.feedbackCatalog.retrieveProfileInfo(info)
            if platform is not False:
                if uriLen>1:
                    roomInfo= self.feedbackCatalog.retrieveRoomInfo(info,uri[1])
                    if roomInfo is not False:
                        output=roomInfo
                    else:
                        output=platform.get(uri[1])
                else:
                    output=platform
            else:
                output=self.feedbackCatalog.feedbackContent.get(info)
            if output==None:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.feedbackCatalog.feedbackContent['description']

        return json.dumps(output) 


    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        if command=='newFeedback':
            platform_ID=uri[1]
            room_ID=uri[2]
            value=json_body['feedback']
            parameter="feedback"
            newSetting=self.feedbackCatalog.setRoomParameter(platform_ID,room_ID,parameter,value)
            if newSetting==True:
                output="Platform '{}' - Room '{}': feedback updated".format(platform_ID,room_ID)
                self.feedbackCatalog.save()
                self.feedbackCatalog.updateDB(platform_ID,room_ID,parameter,value)
            else:
                output="Something wrong..."
            print(output)
            
        else:
            raise cherrypy.HTTPError(501, "No operation!")

if __name__ == '__main__':
    settings=sys.argv[1]
    feedbackCatalog=feedbackREST(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(feedbackCatalog, feedbackCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': feedbackCatalog.feedbackCatalogIP})
    cherrypy.config.update({'server.socket_port': feedbackCatalog.feedbackCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()
