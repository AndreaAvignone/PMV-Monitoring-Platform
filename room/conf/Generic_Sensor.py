from conf.simplePublisher import *
import sys
import time
import json
from datetime import datetime
import requests

class Sensor():
    def __init__(self, configuration_filename,device_ID):
        self.roomContent=json.load(open(configuration_filename,"r"))
        self.room_ID=self.roomContent['room_info']['room_ID']
        self.device_ID=device_ID
        self.hubAddress=self.roomContent['hub_catalog']
        self.message=[]
    
    def configuration(self):
        r=requests.get(self.hubAddress) #ping
        if r.status_code==200:
            self.hub_ID=requests.get(self.hubAddress+'/hub_ID').json()
            broker=requests.get(self.hubAddress+'/broker').json()
            self.broker_IP=broker[0].get('IP_address')
            self.broker_port=broker[0].get('port')
            self.server_catalog=requests.get(f'{self.hubAddress}/server_catalog').json()
            self.settings=requests.get(f'{self.hubAddress}/drivers/{self.device_ID}').json()
            self.time_sleep=self.settings['time_sleep']
            self.parameters=self.settings['parameters']
            for parameter in self.parameters:
                message={'platform_ID': self.hub_ID, 'room_ID':self.room_ID, 'device_ID': self.device_ID, 'parameter':parameter.get('parameter'), 'value': None,'time':'','timestamp':'','unit':parameter.get('unit')}
                self.message.append(message)
        
    
class SensorPublisher(MyPublisher,Sensor):
    def __init__(self, configuration_filename, device_ID):
        Sensor.__init__(self,configuration_filename,device_ID)
        self.configuration()
        self.topic='/'.join([self.hub_ID,self.room_ID,self.device_ID])
        MyPublisher.__init__(self,device_ID+"_publisher",self.topic,self.broker_IP,self.broker_port)
            
    def publishData(self,mylist):
        now=datetime.now()
        dt_string=now.strftime("%H:%M")
        actualTime=time.time()
        for message in self.message:
            for result in mylist:
                if message['parameter']==result['parameter'] and result['value'] is not None and result['value']>=0:
                    message['value']=result['value']
                    message['time']=dt_string
                    message['timestamp']=actualTime
                    #print(message)
                    topic=self.topic+'/'+message['parameter']
                    self.myPublish(topic,json.dumps(message))
                    print (str(result['value'])+' '+ message['unit'])
                    
                    
    def setup(self):
        try:
            requests.put(f'{self.server_catalog}/insertDevice/{self.hub_ID}/{self.room_ID}',json=self.settings)
            return True
        except:
            return False
        