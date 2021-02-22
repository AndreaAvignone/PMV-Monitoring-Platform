import json
import requests
import conf.MyMQTT
from subscriber import *
import sys
import time

class MRT_subscriber(DataCollector):
    
    def MRT_calculation(self,temperature,temp_g, wind):
        pass
        
if __name__ == '__main__':
    room_filename=sys.argv[1]
    collection=MRT_subscriber(room_filename)
    if collection.configuration():
        print("Connection performed.")
    time.sleep(1)
    collection.run()