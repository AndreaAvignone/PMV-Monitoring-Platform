import cherrypy
import json
import requests
import time
import sys

class ServiceCatalogREST():
    exposed=True

    def __init__(self,db_filename):
        #configure the service catalog according to information stored inside database
        self.db_filename=db_filename
        self.MyServiceCatalog=json.load(open(self.db_filename,"r")) #store the database as a variable
        self.serviceCatalogIP=self.MyServiceCatalog['service_catalog'][0].get('IP_address')
        self.serviceCatalogPort=self.MyServiceCatalog['service_catalog'][0].get('port')
        self.service=self.MyServiceCatalog['service_catalog'][0].get('service')
        self.ngrok=self.MyServiceCatalog['ngrok_api']
		
    #a method to retrieve information concerning the requested resource. It returns a valid url, since until now only IP+port address are used
    def retrieveInfo(self,catalog,service):
        serviceAddress='http://'+catalog[service][0].get("IP_address")+':'+str(catalog[service][0].get("port"))
        return serviceAddress
    def findService(self,name):
        if name in self.MyServiceCatalog:
            return True
        else:
            return False
    def register(self,name,IP,port):
        try:
            self.MyServiceCatalog[name][0]["IP_address"]=IP
            self.MyServiceCatalog[name][0]["port"]=port
            return self.MyServiceCatalog[name][0]["service"]
        except:
            return False
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.MyServiceCatalog,file, indent=4)


    def GET(self,*uri):
        if len(uri)!=0:
            if uri[0]=="public":
                r=requests.get(self.ngrok+'/api/tunnels/'+uri[1]).json()
                output=self.MyServiceCatalog[str(uri[1])][0].copy()
                output["IP_address"]=r["public_url"]
                del output["port"]
            else:
                
                try:
                    output=self.MyServiceCatalog[str(uri[0])][0]
                except:
                    raise cherrypy.HTTPError(404,"Service: Not found")
        else:
            output=self.MyServiceCatalog['description'] #if no resource is found, it return a general description about database

        return json.dumps(output,indent=4) 

    def PUT(self,*uri):
        myflag=0
        if len(uri)!=0:
            if uri[0]=="register":
                try:
                    body=cherrypy.request.body.read()
                    json_body=json.loads(body.decode('utf-8'))
                    if self.findService(json_body['service']):
                        new_service=self.register(json_body['service'],json_body['IP_address'],json_body['port'])
                        if new_service is not False:
                            output="Service '{}' registered".format(new_service)
                            self.save()
                            myflag=1
                        else:
                            output="Service '{}'- Registration failed".format(json_body['service'])
                    else:
                        raise cherrypy.HTTPError(404,"Service: Not found")
                except IndexError as e:
                    print(e)
                    output="Error request."
            else:
                raise cherrypy.HTTPError(501, "No operation!")
        print(output)
        if myflag==1:
            return json.dumps(new_service,indent=4) 


if __name__ == '__main__':
    settings=sys.argv[1]
    serviceCatalog=ServiceCatalogREST(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(serviceCatalog, serviceCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': serviceCatalog.serviceCatalogIP})
    cherrypy.config.update({'server.socket_port': serviceCatalog.serviceCatalogPort})
    cherrypy.engine.start()
    while True:
    	time.sleep(1)
    cherrypy.engine.block()
