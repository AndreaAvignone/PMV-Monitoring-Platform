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
		self.service=self.requestResult[0].get("service")

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
		if command=='insertPlatform':
			platform_ID=json_body['platform_ID']
			rooms=json_body['rooms'] 
			newPlatform=self.serverCatalog.insertPlatform(platform_ID,rooms)
			if newPlatform==True:
				output="Platform '{}' has been added to Server".format(platform_ID)
			else:
				output="'{}' already exists!".format(platform_ID)
		elif command=='insertRoom':
			platform_ID=uri[1]
			room_ID=json_body['room_ID']
			platformFlag,newRoom=self.serverCatalog.insertRoom(platform_ID,room_ID,json_body)
			if platformFlag is False:
				raise cherrypy.HTTPError(404,"Platform Not found")
			else:
				if newRoom==True:
					output="Platform '{}' - Room '{}' has been added to Server".format(platform_ID, room_ID)
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
				else:
					output="Platform '{}' - Room '{}' - Device '{}' already exists. Updating...".format(platform_ID,room_ID.device_ID)

		else:
			raise cherrypy.HTTPError(501, "No operation!")
		print(output)


	def POST(self, *uri):
		body=cherrypy.request.body.read()
		json_body=json.loads(body.decode('utf-8'))
		command=str(uri[0])
		if command=='setParameter':
			platform_ID=uri[1]
			room_ID=json_body['room_ID']
			parameter=json_body['parameter']
			parameter_value=json_body['parameter_value']
			newSetting=self.serverCatalog.setRoomParameter(platform_ID,room_ID,parameter,parameter_value)
			if newSetting==True:
				output="Platform '{}' - Room '{}': {} is now {}".format(platform_ID, room_ID, parameter,parameter_value)
			else:
				output="Platform '{}' - Room '{}': Can't change {} ".format(platform_ID, room_ID,parameter)
		elif command=='insertValue':
			platform_ID=uri[1]
			room_ID=uri[2]
			device_ID=uri[3]
			newValue=self.serverCatalog.insertDeviceValue(platform_ID, room_ID, device_ID,json_body)
			output=output="Platform '{}' - Room '{}' - Device '{}': parameters updated".format(platform_ID, room_ID, device_ID)
		else:
			raise cherrypy.HTTPError(501, "No operation!")
		print(output)


	def DELETE(self,*uri):
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
					else:
						output="Platform '{}'- Room '{}' - Device '{}' not found ".format(platform_ID,room_ID,device_ID)
				else:
					removedRoom=self.serverCatalog.removeRoom(platform_ID,room_ID)
					if removedRoom==True:
						output="Platform '{}' - Room '{}' removed".format(platform_ID,room_ID)
					else:
						output="Platform '{}'- Room '{}' not found ".format(platform_ID,room_ID)
			else:
				removedPlatform=self.serverCatalog.removePlatform(platform_ID) 
				if removedPlatform==True:
					output="Platform '{}' removed".format(platform_ID)
				else:
					output="Platform '{}' not found ".format(platform_ID)
		else:
			raise cherrypy.HTTPError(501, "No operation!")
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
				requestProfiles=requests.get(server.serviceCatalogAddress+"/services/profiles_catalog").json()
				IP=requestProfiles[0].get('IP_address')
				port=requestProfiles[0].get('port')
				service=requestProfiles[0].get('service')
				inactiveTime=requests.get(server.buildAddress(IP,port,service)+'/'+platform['platform_ID']+'/inactive_time').json()
				for room in platform['rooms']:
					try:
						result=server.serverCatalog.removeInactive(room['devices'],inactiveTime)
						if result is not False:
							server.serverCatalog.dateUpdate(room)
					except:
						pass

			except:
				print("Services communication is not working")

			

		time.sleep(5)
	cherrypy.engine.block()