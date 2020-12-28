import cherrypy
import json
import requests
import time
import sys

class ServiceCatalogREST():
	exposed=True

	def __init__(self,db_filename):
		#configure the service catalog according to information stored inside database
		self.db_filename=db_filename
		self.MyServiceCatalog=json.load(open(self.db_filename,"r")) #store the database as a variable
		self.serviceCatalogIP=self.MyServiceCatalog['service_catalog'][0].get('IP_address')
		self.serviceCatalogPort=self.MyServiceCatalog['service_catalog'][0].get('port')
		self.service=self.MyServiceCatalog['service_catalog'][0].get('service')
		
	#a method to retrieve information concerning the requested resource. It returns a valid url, since until now only IP+port address are used
	def retrieveInfo(self,catalog,service):
		serviceAddress='http://'+catalog[service][0].get("IP_address")+':'+str(catalog[service][0].get("port"))
		return serviceAddress

	def GET(self,*uri):
		if len(uri)!=0:
			try:
				#output= self.retrieveInfo(self.MyServiceCatalog,str(uri[0]))
				output=self.MyServiceCatalog[str(uri[0])]
			except:
				raise cherrypy.HTTPError(404,"Service: Not found")
		else:
			output=self.MyServiceCatalog['description'] #if no resource is found, it return a general description about database

		return json.dumps(output,indent=4) 

if __name__ == '__main__':
    settings=sys.argv[1]
    serviceCatalog=ServiceCatalogREST(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(serviceCatalog, serviceCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': serviceCatalog.serviceCatalogIP})
    cherrypy.config.update({'server.socket_port': serviceCatalog.serviceCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()
