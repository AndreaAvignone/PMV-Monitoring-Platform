import json
import requests
import time
from conf.MyMQTT import *
import sys

class DataCollector():
    def __init__(self,configuration_filename):
        self.roomContent=json.load(open(configuration_filename,"r"))
        self.room_ID=self.roomContent['room_info']['room_ID']
        self.hubAddress=self.roomContent['hub_catalog']
    def configuration(self):
        r=requests.get(self.hubAddress) #ping
        if r.status_code==200:
            self.hub_ID=requests.get(self.hubAddress+'/hub_ID').json()
            broker=requests.get(self.hubAddress+'/broker').json()
            self.broker_IP=broker[0].get('addressIP')
            self.broker_port=broker[0].get('port')
            self.server_catalog=requests.get(f'{self.hubAddress}/server_catalog').json()
            self.client=MyMQTT(self.hub_ID,self.broker_IP,self.broker_port,self)
            return True
            
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



