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
		self.requestResult=requests.get(self.serviceCatalogAddress+"/services/server_catalog").json()
		self.serverCatalogIP=self.requestResult[0].get("IP_address")
		self.serverCatalogPort=self.requestResult[0].get("port")

	def GET(self,*uri):
		if len(uri)!=0:
			try:
				info=uri[0]
				try:
					room=uri[1]
					try:
						roomInfo=uri[2]
						output=self.serverCatalog.RetrieveRoomInfo(info,room).get(roomInfo)
					except:
						output=self.serverCatalog.RetrieveRoomInfo(info,room)

				except:
					output= self.serverCatalog.RetrievePlatform(info)
					if output==False:
						output=self.serverCatalog.serverContent[info]
					
			except:
				raise cherrypy.HTTPError(404,"Information Not found")

			if output==False:
					raise cherrypy.HTTPError(404,"Room Not found")
		else:
			output=self.serverCatalog.serverContent['description']

		return json.dumps(output) 


if __name__ == '__main__':
    db=sys.argv[1]
    serverCatalog=ResourcesServerREST(db)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(serverCatalog, '/Monitoring-Platform/platforms', conf)
    cherrypy.config.update({'server.socket_host': serverCatalog.serverCatalogIP})
    cherrypy.config.update({'server.socket_port': serverCatalog.serverCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()