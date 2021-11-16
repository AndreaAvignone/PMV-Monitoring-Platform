# Thermal Comfort Monitoring-Platform
![](http://www.politocomunica.polito.it/var/politocomunica/storage/images/media/images/marchio_logotipo_politecnico/1371-1-ita-IT/marchio_logotipo_politecnico_large.jpg) 

> **Master course in ICT FOR SMART SOCIETIES**

> **Interdisciplinary projects 2020-2021**

*Considering the high price solutions for indoor thermal comfort monitoring, this project proposes a low-cost IoT sensor network (exploiting Raspberry Pi and Arduino platforms) for collecting real-time data and evaluating specific thermal comfort indicators (PMV and PPD). The overall architecture was accordingly designed, implementing the hardware setup, the back-end and the Android user interface. Eventually, three distinct platforms were deployed for testing the general system and analyzing the obtained results in different places and seasons, based on collected data and users’ preferences.*

The software is composed of three main parts:
- Back-end
- Platform and sensor network
- Android Application

The repostiory for setup a new platform is retrievable here:

> [https://github.com/AndreaAvignone/Monitoring-Platform-kit](url)

The source code for the Android Application:

> [https://github.com/AndreaAvignone/myComfort](url)

## Architecture overview


## Getting Started

The project was mainly developed within a **Python 3** environment. In particular, the back-end was hosted by a **Raspberry Pi 4**.\
Main required elements:
* CherryPy
* MQTT
* InfluxDB
* Grafana
* ngrok

To install the specific requirements:

``
pip3 install -r requirements.txt
``

### REST Server

The general architecture is based on the micro-services approach.\ Availabe services are stored into databases and exposed through REST protocol - e.g. broker, profile databases, server -. In particular, for each service, IP, port and basic path to start the service are provided (dictionary).

For each service, the JSON-like configuration file is present under the folder:
> /etc 

Using this file, it is possible to edit the configuration of each back-end, like **IP address** and **Port number**. \
Services present a similar structure. The basic path is */Monitoring-Platform + /specific_service* (e.g. http://127.0.0.1:8083/Monitoring-Platform/server, http://127.0.0.1:8081/Monitoring-Platform/profiles). \
Given the educational reason behind the project, each service is expected to be individually launched. The expected command has been reported in each specific folder.

**Remark**\
The *service catalog* is crucial to orchestrate the whole system, therefore it must be the first one to run. All the other services will both register to the *service catalog* and retrieve the required information about other entities.\
All the services follow the same command structure. Starting from the *service catalog*:

``
python3 service_catalog.py etc/service_catalog.json
``


### MQTT 
The communication sensor-server is based on the MQTT protocol. In this implementation, the back-end is hosting also the broker. Each sensor publishes its own value and the server subscriber retrieves the information. In addition to the real-time values provided to the final user, measurements are stored in a specific historical database (*InfluxDB*).

A similar approach is also employed by the *resource catalog* for notifications and warnings.

### ngrok
To enable tunneling, ngrok (https://ngrok.com) was exploited, with proper configuration.

## Features

## Description
Each back-end service presents a similar structure. The basic path is /Monitoring-Platform + /specific_service (e.g. http://127.0.0.1:8083/Monitoring-Platform/server, http://127.0.0.1:8081/Monitoring-Platform/profiles). The crucial one is the **service catalog**. It is based on a json file storing also its own address (http://127.0.0.1:8080/Monitoring-Platform/services).\
When **profiles catalog** is launched, it asks the service catalog about the proper address and the basic path to use. Also the list of information about rooms is present. Therefore the client sends requests to change name and parameters directly to this catalog.\
**Server/resources catalog** instead collects basic information about the system and measurments (for example, only room_ID is present, discarding room_name and secondary information). For clarity, ServerClass is based on a rooms catalog and a devices catalog for insert or delete devices and rooms. Instead, retrieving information is performed directly. When it is running, it waits a specific amount of time before checking if some sensors inside some rooms should be considered dead. Therefore, it sends a requests to profiles catalog to know the inactive_time for the desired room. If profiles catalog is down, the system keeps trying, printing "services communication is not working" until everything is restored. \

## Configuration
When all services are up, new platforms can be installed. Each platform is composed by a central HUB, locally exposed for the REST communication with present rooms. It actually ping the Server to be added to the catalog. Then, a room can be configured.\
**IMPORTANT**: the idea is that a virtual instance is created from the client (i.e. the mobile application), appended to the profiles catalog of the specific platform with a connection_flag=False. When the physical room is plugged, it retrieves information about service catalog from the central hub, then it sends a requests to profiles catalog (put insertRoom). In this way, the profiles server check if there is any room previously created, with the connection_flag equal to false and a  less than 1 minute timestamp. Association is therefore performed. Moreover, for each profile a room counter is set. In fact, room is "blind" also about itself, avoiding needs for any kind of a-priori identification. It just knows the IP address of the central HUB (expected to be always the same, so set by default) and the basic room_ID it is expected to assume (e.g. room_X). When the association is correclty performed, profiles service returns the complete configuration, including the ID based on counter (e.g. room_X2 if it is the second associated room) and name set by client. Room updates its own configuration file so that connected sensors can retrieve all information.\
For the **sensor installation**, main.py script is used, independently on the sensor. In fact, when main script is run, it automatically imports the class according to sensor_ID. Sensor_ID is specified as argument, toghether with the room configuration file and the related pin (python3 main.py room_setup.json dht11 17). Again, the sensor requests configuration drivers from central HUB with a GET request. If central HUB has not already the drivers inside its own memory, it contacts the **drivers service** to download. Sensor can now be configured, publishing on the broker messages. Eventually, subscriber collects information among all sensors and continusoly updates stored information inside the server catalog.

## Links

## License
[GPL-3.0](./LICENSE)


