#PROBLEMS: - transform the two putbody in one single, so adapt the server to deal with it.

import json
import requests
import time
import datetime
from conf.MyMQTT import *
import sys
from influxdb import InfluxDBClient

class DataCollector():
    def __init__(self,configuration_filename,clientID="SubscriberClient"):
        self.clientID=clientID
        self.subContent=json.load(open(configuration_filename,"r"))
        self.serviceCatalogAddress=self.subContent['service_catalog']
        self.platformList=[]
        self.lastCheck=None
        self.delta=self.subContent['delta']

    def configuration(self):
        print("Retrieving broker information...")
        try:
            self.broker_IP,self.broker_port,self.broker_service=self.retrieveService('broker')
            print("Broker info obtained.")
            self.client=MyMQTT(self.clientID,self.broker_IP,self.broker_port,self)
            time.sleep(0.5)
            self.profiles_IP,self.profiles_port,self.profiles_service=self.retrieveService('profiles_catalog')
            print("Profiles service info obtained.")
            time.sleep(0.5)
            self.server_IP,self.server_port,self.server_service=self.retrieveService('server_catalog')
            print("Resources service info obtained.")
            time.sleep(0.5)
            self.influx_IP,self.influx_port,self.influx_service=self.retrieveService('influx_db')
            print("Influx DB info obtained")
            return True
        except:
            print("Configuration info not obtained.")
            return False
        
    def retrieveService(self,service):
            request=requests.get(self.serviceCatalogAddress+'/'+service).json()
            IP=request[0].get('IP_address')
            port=request[0].get('port')
            service=request[0].get('service')
            return IP,port,service

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
        room_ID=payload['room_ID']
        device_ID=payload['device_ID']
        platform_ID=payload['platform_ID']
        value=payload['value']
        unit=payload['unit']
        parameter=payload['parameter']
        timestamp=payload['timestamp']
        rfc=datetime.datetime.fromtimestamp(timestamp)
        rfc=rfc.strftime("%Y-%m-%dT%H:%M:%SZ")
        t=payload['time']
        putBody={'parameter':parameter,'value':value,'unit':unit,'timestamp':timestamp}
        print(f'At {room_ID} ({platform_ID}) ({t})\nSensor {device_ID} - {parameter}: {value} {unit}\n')
        try:
            myResult=requests.put(self.buildAddress(self.server_IP,self.server_port,self.server_service)+'/insertValue/'+platform_ID+'/'+room_ID+'/'+device_ID, json=putBody).json()
        except:
            print("Error detected in server communication.")
            myResult=[]
        self.clientDB=InfluxDBClient(self.influx_IP,self.influx_port,'root','root',platform_ID)
        if self.last_meas(parameter,room_ID,rfc):
            try:
                json_body = [{"measurement":parameter,"tags":{"user":platform_ID,"roomID":room_ID},"time":rfc,"fields":{"value":value}}]
                self.clientDB.write_points(json_body)
            except:
                print("InfluxDB connection lost.")
        for p in myResult:
            if self.last_meas(p['parameter'],room_ID,rfc):
                new_json_body = [{"measurement":p['parameter'],"tags":{"user":platform_ID,"roomID":room_ID},"time":rfc,"fields":{"value":p['value']}}]
                self.clientDB.write_points(new_json_body)

    
    def last_meas(self,parameter,room_ID,rfc):
        q="show measurements;"
        r=self.clientDB.query(q).get_points()
        flag=False
        for point in r:
            if point['name']==parameter:
                flag=True
                break
        if flag==False:
            return True
        query="select last(value), time from {} where roomID='{}';".format(parameter,room_ID)
        result=self.clientDB.query(query).get_points()
        for point in result:
            a = time.strptime(point['time'], '%Y-%m-%dT%H:%M:%SZ')
            a=(time.mktime(a))
        b = time.strptime(rfc, '%Y-%m-%dT%H:%M:%SZ')
        b=(time.mktime(b))
        if b-a>=self.delta:
            return True
        
    def updateList(self):
        missingList=[]
        try:
            last_creation=requests.get(self.buildAddress(self.profiles_IP,self.profiles_port,self.profiles_service)+'/last_creation').json()
            if self.lastCheck is None or last_creation>self.lastCheck:
                profilesList=requests.get(self.buildAddress(self.profiles_IP,self.profiles_port,self.profiles_service)+'/profiles_list').json()
                newList=[platform for platform in profilesList if platform not in self.platformList]
                self.platformList=profilesList
                missingList=[platform for platform in self.platformList if platform not in profilesList]
                return newList,missingList
            else:
                return missingList,missingList
           
        except:
            print("Profiles catalog - connection lost.")
            return missingList,missingList



if __name__ == '__main__':
    filename=sys.argv[1]
    collection=DataCollector(filename)
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




