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
		self.service=self.requestResult[0].get("service")

	def GET(self,*uri):
		uriLen=len(uri)
		if uriLen!=0:
			profile= self.profilesCatalog.retrieveProfileInfo(uri[0])
			if profile is not False:
				if uriLen>1:
					profileInfo= self.profilesCatalog.retrieveProfileParameter(uri[0],uri[1])
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
		if command=='insertProfile':
			platform_ID=json_body['platform_ID']
			platform_name=json_body['platform_name']
			inactiveTime=json_body['inactiveTime']
			preferences=json_body['preferences']
			location=json_body['location'] 
			newProfile=self.profilesCatalog.insertProfile(platform_ID,platform_name,inactiveTime,preferences,location)
			if newProfile==True:
				output="Profile '{}' has been added to Profiles Database".format(platform_ID)
			else:
				output="'{}' already exists!".format(platform_ID)
			print(output)
		else:
			raise cherrypy.HTTPError(501, "No operation!")
		

	def POST(self, *uri):
		body=cherrypy.request.body.read()
		json_body=json.loads(body.decode('utf-8'))
		command=str(uri[0])
		if command=='setParameter':
			platform_ID=json_body['platform_ID']
			parameter=json_body['parameter']
			parameter_value=json_body['parameter_value']
			newSetting=self.profilesCatalog.setParameter(platform_ID,parameter,parameter_value)
			if newSetting==True:
				output="Platform '{}': {} is now {}".format(platform_ID, parameter,parameter_value)
			else:
				output="Platform '{}': Can't change {} ".format(platform_ID, parameter)
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