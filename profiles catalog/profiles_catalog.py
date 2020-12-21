import cherrypy
import json
import requests
import time
import sys

class ServiceCatalog():
	exposed=True

	def __init__(self,db_filename):
		self.db_filename=db_filename
		self.MyServiceCatalog=json.load(open(self.db_filename,"r")) #store the database as a variable
		self.serviceCatalogIP=self.MyServiceCatalog['service_catalog'][0].get('IP_address')
		self.serviceCatalogPort=self.MyServiceCatalog['service_catalog'][0].get('port')

	def retrieveInfo(self,catalog,service):
		serviceAddress='http://'+catalog[service][0].get("IP_address")+':'+str(catalog[service][0].get("port"))
		return serviceAddress

	def GET(self,*uri):
		if len(uri)!=0:
			try:
				output= self.retrieveInfo(self.MyServiceCatalog,str(uri[0]))
			except:
				raise cherrypy.HTTPError(404,"Service: Not found")
		else:
			output=self.MyServiceCatalog['description']

		return json.dumps(output,indent=4) 




if __name__ == '__main__':
    settings=sys.argv[1]
    serviceCatalog=ServiceCatalog(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(serviceCatalog, '/Monitoring-Platform/services', conf)
    cherrypy.config.update({'server.socket_host': serviceCatalog.serviceCatalogIP})
    cherrypy.config.update({'server.socket_port': serviceCatalog.serviceCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()