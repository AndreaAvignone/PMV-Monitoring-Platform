import json
import requests
import conf.MyMQTT
from subscriber_influxpy import *
import sys
import time

class MRT_subscriber(DataCollector):
	def __init__(self,filename,clientID):
		self.room_filename=room_filename
		DataCollector.__init__(self.room_filename,clientID)
		self.emissivity=self.subContent['emissivity']
		self.diameter=self.subContent['diameter']

    def MRT_calculation(self,temperature,temp_g, wind,eg,d):
        MRT=(((temp_g+273.15)**4+(1.335*(10**8)*(wind**0.71))/(eg*(d**0.4))*(temp_g-temperature))**0.25)-273.15
        
if __name__ == '__main__':
    filename=sys.argv[1]
    collection=MRT_subscriber(filename)
    if collection.configuration():
        print("Connection performed.")
        time.sleep(0.5)
        collection.run()
        while True:
            platform_list,unfollowing_list=collection.updateList()
            for platform in platform_list:
                collection.follow(platform+'/#')
                time.sleep(1)
            for platform in unfollowing_list:
                collection.client.unsubscribe()
                time.sleep(0.5)
            time.sleep(1)
        collection.end()
    else:
        print("Connection failed.")