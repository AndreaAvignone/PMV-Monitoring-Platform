import cherrypy
import json
import requests
import time
import sys

class DriversCatalogREST():
	exposed=True

	def __init__(self,db_filename):
		#configure the service catalog according to information stored inside database
		self.db_filename=db_filename
		self.driversCatalog=json.load(open(self.db_filename,"r")) #store the database as a variable
		self.serviceCatalogAddress=self.driversCatalog['service_catalog']
		self.requestResult=requests.get(self.serviceCatalogAddress+"/drivers_catalog").json()
		self.driversCatalogIP=self.requestResult.get('IP_address')
		self.driversCatalogPort=self.requestResult.get('port')
		self.service=self.requestResult.get('service')
		
	def GET(self,*uri):
		if len(uri)==1:
			try:
				output=self.driversCatalog[uri[0]]
			except:
				raise cherrypy.HTTPError(404,"Information: Not found")
		elif len(uri)==2:
			try:
				drivers_list=self.driversCatalog[uri[0]]
	
				notFound=1
				for drivers in drivers_list:
					if drivers['device_ID']==uri[1]:
						output=drivers
						notFound=0
						break
				if notFound==1:
					raise cherrypy.HTTPError(404,"Drivers Not found")
			except:
				raise cherrypy.HTTPError(404,"Information: Not found")

		else:
			output=self.driversCatalog['description'] #if no resource is found, it return a general description about database

		return json.dumps(output,indent=4) 

if __name__ == '__main__':
    settings=sys.argv[1]
    driversCatalog=DriversCatalogREST(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(driversCatalog, driversCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': driversCatalog.driversCatalogIP})
    cherrypy.config.update({'server.socket_port': driversCatalog.driversCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()
