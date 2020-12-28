# Monitoring-Platform
For each service, a folder called '/etc' exists, containing JSON-like configuration files.
## Services catalog: 
Availabe services are stored into databases and exposed through REST protocol - e.g. broker, profile databases, server -. In particular, for each service, IP, port and basic path to start the service are provided (dictionary).\
**Situation:** basic functionalities implemented (retrieve data + error for bad requests).\
**Improvements:** update the list of services according to the necessary ones.
## Registration/clients catalog:
Create the database format to store information about registred users and include the html page for the registration phase (customized).\
**Situation:** The service is working with some adaptions similar to the other services.\
**Improvements:** It should be completely adapted to the system (see issue). /
## Profiles catalog:
The server stores information about the profile of each user in a specific database, exposed by the correlated service running on  a different port.\
**Situation:** Basic functionalities clearly implemented for GET requests. Specficic errors depending if a wrong command or a wrong parameter is requested.\
**Improvements:** 1. deeper analysis about useful information, preferences and parameters that should be stored into profiles db to be consistent. 2. Integrate all necessary POST/PUT functionalities to handle the catalog.
