### Resource catalog:
It stores basic information about the system and measurments (for example, only room_ID is present, discarding room_name and secondary information). For clarity, ServerClass is based on a rooms catalog and a devices catalog for insert or delete devices and rooms. Instead, retrieving information is performed directly. When it is running, it waits a specific amount of time before checking if some sensors inside some rooms should be considered dead. Therefore, it sends a requests to *profiles catalog* to know the inactive_time for the desired room. It is in charge of the main database. For each room, MRT, Icl_clo, M_met, W_met, PMV, PPD values (after computation - *computation.py*) are stored as well as the list of devices.
Command:

```
python3 resources_server.py etc/db.json
```
