import cherrypy
import json
import sys
import requests
import time

class Registration_deployer(object):
    exposed=True
    def __init__(self,db_filename):
        self.db_filename=db_filename
        self.MyClientsCatalog=json.load(open(self.db_filename,"r"))
        self.serviceCatalogAddress=self.MyClientsCatalog['service_catalog']
        self.requestResult=requests.get(self.serviceCatalogAddress+"/clients_catalog").json()
        self.clientsCatalogIP=self.requestResult[0].get("IP_address")
        self.clientsCatalogPort=self.requestResult[0].get("port")
        self.service=self.requestResult[0].get("service")

    def GET(self,*uri,**params):
        if (len(uri))>0 and uri[0]=="reg.html":
            return open('etc/reg.html')

        elif (len(uri)>0 and uri[0]=="reg_results"):
            users=json.load(open(self.db_filename))
            for user in users.get("users_list"):
                if user['user_ID']==params['userID']:
                    return open("etc/fail_reg_user.html") 
            if params['psw']!=params['psw-repeat']:
                return open("etc/fail_reg_pass.html") 

            else:
                users["users_list"].append({
                    "user_ID":params['userID'],
                    "catalog_list":[],
                    "password":params['psw']
                    })
                for i in range(len(users["users_list"])):
                    if users["users_list"][i]['user_ID']==params['userID']:
                        users["users_list"][i]['catalog_list'].append({'catalog_ID':params['catalogID'],'connection_flag':False})


                with open(self.db_filename, 'w') as outfile:
                    json.dump(users, outfile, indent=4)
            
                return open("etc/correct_reg.html")

if __name__ == '__main__':
    clients_db=sys.argv[1]
    clientsCatalog=Registration_deployer(clients_db)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    
    cherrypy.tree.mount(clientsCatalog, clientsCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': clientsCatalog.clientsCatalogIP})
    cherrypy.config.update({'server.socket_port': clientsCatalog.clientsCatalogPort}) 
    cherrypy.engine.start()
    while True:
        time.sleep(1)
    cherrypy.engine.block()
