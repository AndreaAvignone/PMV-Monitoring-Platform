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
    def __init__(self,configuration_filename):
        self.subContent=json.load(open(configuration_filename,"r"))
        self.serviceCatalogAddress=self.subContent['service_catalog']
        self.newTime=time.time()

    def configuration(self):
        self.retrieveBroker()
        self.client=MyMQTT(self.hub_ID,self.broker_IP,self.broker_port,self)
        

    def retrieveBroker(self):
        print("Retrieving broker information...")
        try:
            requestBroker=requests.get(self.serviceCatalogAddress+'/broker').json()
            self.broker_IP=requestBroker[0].get('IP_address')
            self.broker_port=requestBroker[0].get('port')
            print("Broker info obtained.")
        except:
            print("Broker info not obtained.")
            
    def run(self):
        self.client.start()
        print('{} has started'.format(self.hub_ID))
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.hub_ID))
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
            influx_Body={"measurement":parameter,"tags":{"user":self.hub_ID,"roomID":self.room_ID},"time":timestamp,"fileds":{"value":value}}
            self.clientDB.write_points(json_body)
            self.newTime=actual_time


if __name__ == '__main__':
    room_filename=sys.argv[1]
    collection=DataCollector(room_filename)
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



