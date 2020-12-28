# Monitoring-Platform
For each service, a folder called '/etc' exists, containing JSON-like configuration files.
## Main services
### Service catalog: 
Availabe services are stored into databases and exposed through REST protocol - e.g. broker, profile databases, server -. In particular, for each service, IP, port and basic path to start the service are provided (dictionary).\
**Situation:** basic functionalities implemented (retrieve data + error for bad requests).\
**Improvements:** update the list of services according to the necessary ones. Also POST/PUT functionalities can be integrated to modify information rather than manually with the json file.\
**How to run**: python3 service_catalog.py etc/service_catalog.json
### Registration/clients catalog:
Create the database format to store information about registred users and include the html page for the registration phase (customized).\
**Situation:** The service is working with some adaptions similar to the other services.\
**Improvements:** It should be completely adapted to the system (see issue).\
### Profiles catalog:
The server stores information about the profile of each user in a specific database, exposed by the correlated service running on  a different port.\
**Situation:** Basic functionalities clearly implemented for GET requests. Specficic errors depending if a wrong command or a wrong parameter is requested.\
**Improvements:** 1. deeper analysis about useful information, preferences and parameters that should be stored into profiles db to be consistent. 2. Integrate all necessary POST/PUT functionalities to handle the catalog.\
**How to run**: python3 profiles_catalog.py etc/profiles_db.json\
**Update**: The system now includes also PUT for inserting new profile, POST to set the value of a specific parameter, DELETE for removing profiles. Basic errors for bad requests. Integration with server catalog is working according to the microservice approach.\
### Server catalog:
It stores everything about rooms measurments. The structure is complex and it is based on rooms catalog and devices catalog. It is in charge of the main database. For each room, MRT value and list of devices are present.\
**Situation**: Structure is well organized, with all needed functionalities. See issues for doubts.\
**Improvements**: More tests are expected to find errors. All useful information to store should be defined (e.g. MRT, thermal comfort, PMV...).\
**How to run**: python3 resources_server.py etc/db.json

## Description
Each back-end service presents a similar structure. The basic path is /Monitoring-Platform + /specific_service (e.g. http://127.0.0.1:8083/Monitoring-Platform/server, http://127.0.0.1:8081/Monitoring-Platform/profiles). The crucial one is the **service catalog**. It is based on a json file storing also its own address (http://127.0.0.1:8080/Monitoring-Platform/services).\
When **profiles catalog** is launched, it asks the service catalog about the proper address and the basic path to use. Also the list of information about rooms is present. Therefore the client sends requests to change name and parameters directly to this catalog.\
**Server/resources catalog** instead collects basic information about the system and measurments (for example, only room_ID is present, discarding room_name and secondary information). For clarity, ServerClass is based on a rooms catalog and a devices catalog for insert or delete devices and rooms. Instead, retrieving information is performed directly. When it is running, it waits a specific amount of time before checking if some sensors inside some rooms should be considered dead. Therefore, it sends a requests to profiles catalog to know the inactive_time for the desired room. If profiles catalog is down, the system keeps trying, printing "services communication is not working" until everything is restored.\
