import paho.mqtt.client as PahoMQTT
import time

class MyPublisher:
    def __init__(self, clientID,topic,broker,port):
        self.clientID = clientID

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        #self.messageBroker = 'iot.eclipse.org'
        self.messageBroker = broker
        self.port=port

    def start (self):
        #manage connection to broker
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop (self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish(self,topic,message):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, message, 2)
        print(topic)

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.messageBroker, rc))
