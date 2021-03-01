#PROBLEMS: - transform the two putbody in one single, so adapt the server to deal with it.
          #- Consider if create one database for room or it is not necessary. Change this client since now the broker is
          #  is located inside the server (self.roomID is not correct)

import json
import requests
import time
from conf.MyMQTT import *
import sys
from influxdb import InfluxDBClient

class DataCollector():
    def __init__(self,configuration_filename,clientID="SubscriberClient"):
        self.clientID=clientID
        self.subContent=json.load(open(configuration_filename,"r"))
        self.serviceCatalogAddress=self.subContent['service_catalog']
        self.newTime=time.time()
        self.platformList=[]
        self.lastCheck=None

    def configuration(self):
        print("Retrieving broker information...")
        try:
            self.broker_IP,self.broker_port=self.retrieveService('broker')
            print("Broker info obtained.")
            self.client=MyMQTT(self.clientID,self.broker_IP,self.broker_port,self)
            time.sleep(0.5)
            self.profiles_IP,self.broker_port=self.retrieveService('profiles_catalog')
            print("Profiles service info obtained.")
            return True
        except:
            print("Configuration info not obtained.")
            return False
        
    def retrieveService(self,service):
            request=requests.get(self.serviceCatalogAddress+'/'+service).json()
            IP=request[0].get('IP_address')
            port=request[0].get('port')
            return IP,port

    def buildAddress(self,IP,port, service):
        finalAddress='http://'+IP+':'+str(port)+service
        return finalAddress

            
    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))
    def follow(self,topic):
        self.client.mySubscribe(topic)
    def notify(self,topic,msg):
        payload=json.loads(msg)
        device_ID=payload['device_ID']
        value=payload['value']
        unit=payload['unit']
        parameter=payload['parameter']
        timestamp=payload['timestamp']
        t=payload['time']
        putBody={'parameter':parameter,'value':str(value),'unit':unit,'timestamp':timestamp}
        print(f'At {self.room_ID} ({t})\nSensor {device_ID} - {parameter}: {value} {unit}\n')
        try:
            requests.put(self.server_catalog+'/insertValue/'+self.hub_ID+'/'+self.room_ID+'/'+device_ID, json=putBody)
        except:
            print("Error detected in server communication.")
        actual_time=time.time()
        if self.newTime-actual_time>=60:
            try:
                influx_Body={"measurement":parameter,"tags":{"user":self.hub_ID,"roomID":self.room_ID},"time":timestamp,"fileds":{"value":value}}
                self.clientDB.write_points(json_body)
                self.newTime=actual_time
            except:
                print("InfluxDB connection lost.")
    
    def updateList(self):
        try:
            last_creation=requests.get(server.buildAddress(IP,port,"profiles_catalog")+'/last_creation').json()
            if self.lastCheck is None or last_creation>self.lastCheck:
                newList=requests.get(server.buildAddress(IP,port,"profiles_catalog")+'/profiles_list').json()
        except:
            print("Profiles catalog - connection lost.")



if __name__ == '__main__':
    filename=sys.argv[1]
    collection=DataCollector(filename)
    if collection.configuration():
        print("Connection performed.")
        time.sleep(1)
        collection.run()       
        while True:

            collection.follow(collection.hub_ID+'/#')
            time.sleep(3)
            collection.client.unsubscribe()
            time.sleep(1)
        collection.end()
    else:
        print("Connection failed.")



