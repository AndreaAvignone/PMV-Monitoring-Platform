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
		self.requestResult=requests.get(self.serviceCatalogAddress+"/services/profiles_catalog").json()
		self.profilesCatalogIP=self.requestResult[0].get("IP_address")
		self.profilesCatalogPort=self.requestResult[0].get("port")

	def GET(self,*uri):
		if len(uri)!=0:
			try:
				resource=uri[0]
				try:
					parameter=uri[1]
					output=self.profilesCatalog.RetrieveProfileParameter(resource,parameter)	
				except:
					output=self.profilesCatalog.RetrieveProfileInfo(resource)
					if output==False:
						output= self.profilesCatalog.profilesContent[resource]

			except:
				raise cherrypy.HTTPError(404,"Information Not found")

			if output==False:
					raise cherrypy.HTTPError(404,"Parameter Not found")
		else:
			output=self.profilesCatalog.profilesContent['description']

		return json.dumps(output) 

if __name__ == '__main__':
    db=sys.argv[1]
    profilesCatalog=ProfilesCatalogREST(db)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(profilesCatalog, '/Monitoring-Platform/profiles', conf)
    cherrypy.config.update({'server.socket_host': profilesCatalog.profilesCatalogIP})
    cherrypy.config.update({'server.socket_port': profilesCatalog.profilesCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()