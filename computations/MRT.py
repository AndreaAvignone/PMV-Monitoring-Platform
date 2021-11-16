import json
import requests
import sys
import time

class MRT_calculator(object):
	def __init__(self,filename,clientID):
		self.filename=filename
        self.subContent=json.load(open(filename,"r"))
        self.serviceCatalogAddress=self.subContent['service_catalog']

    def configuration(self):
        print("Retrieving server information...")
        try:
            self.drivers_IP,self.drivers_port,self.drivers_service=self.retrieveService('drivers')
            print("Drivers info obtained.")
            time.sleep(0.5)
            self.server_IP,self.server_port,self.server_service=self.retrieveService('server_catalog')
            print("Resources service info obtained.")
            return True
        except:
            print("Configuration info not obtained.")
            return False

    def retrieveParams(self,global_thermo_ID,room_ID):
        if self.subContent['emissivity']==None or self.subContent['diameter']==None:
            request=requests.get(self.buildAddress(self.drivers_IP,self.drivers_port,self.drivers_service)+'/drivers_list'+global_thermo_ID).json()
            self.subContent['emissivity']=request['emissivity']
            self.subContent['diameter']=request['diameter']
            #save option
            r=requests.get(self.buildAddress(self.server_IP,self.server_port,self.server_service)+'/'+room_ID+'?parameter=temperature').json()
            temperature=r['value']
            r=requests.get(self.buildAddress(self.server_IP,self.server_port,self.server_service)+'/'+room_ID+'?parameter=temperature_g').json()
            temperature_g=r['value']
            r=requests.get(self.buildAddress(self.server_IP,self.server_port,self.server_service)+'/'+room_ID+'?parameter=wind').json()
            if r['unit']="KmH":
                wind=r['value']/3.6
            return temperature,temperature_g,wind


    def retrieveService(self,service):
            request=requests.get(self.serviceCatalogAddress+'/'+service).json()
            IP=request[0].get('IP_address')
            port=request[0].get('port')
            service=request[0].get('service')
            return IP,port,service

    def buildAddress(self,IP,port, service):
        finalAddress='http://'+IP+':'+str(port)+service
        return finalAddress

    def MRT_calculation(self,temperature,temp_g, wind,eg,d):
        MRT=(((temp_g+273.15)**4+(1.335*(10**8)*(wind**0.71))/(eg*(d**0.4))*(temp_g-temperature))**0.25)-273.15
        return MRT
        
if __name__ == '__main__':
    filename=sys.argv[1]
    