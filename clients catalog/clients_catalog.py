import cherrypy
import json
import sys
import requests
import time
from clients_class import *

class Registration_deployer(object):
    exposed=True
    def __init__(self,db_filename):
        self.db_filename=db_filename
        self.MyClientsCatalog=ClientsCatalog(self.db_filename)
        self.serviceCatalogAddress=self.MyClientsCatalog.clientsContent['service_catalog']
        self.requestResult=requests.get(self.serviceCatalogAddress+"/clients_catalog").json()
        self.clientsCatalogIP=self.requestResult.get("IP_address")
        self.clientsCatalogPort=self.requestResult.get("port")
        self.service=self.requestResult.get("service")

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


                self.MyClientsCatalog.save()
                return open("etc/correct_reg.html")
        elif(len(uri))>0 and uri[0]=="login":
            
            data=self.MyClientsCatalog.find(str(cherrypy.request.login))
            del data['password']
            return data

            
if __name__ == '__main__':
    clients_db=sys.argv[1]
    clientsCatalog=Registration_deployer(clients_db)
    get_ha1 = cherrypy.lib.auth_digest.get_ha1_dict_plain(clientsCatalog.MyClientsCatalog.userpassdict)
    checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(clientsCatalog.MyClientsCatalog.userpassdict)
    conf = {
      'global' : {
        'server.socket_host' : clientsCatalog.clientsCatalogIP,
        'server.socket_port' : clientsCatalog.clientsCatalogPort
        #'server.thread_pool' : 8
      },
      '/' : {
        # HTTP verb dispatcher
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        # JSON response
        'tools.json_out.on' : True,
        # Digest Auth
        'tools.auth_digest.on'      : True,
        'tools.auth_digest.realm'   : 'Francis Drake',
        'tools.auth_digest.get_ha1' : get_ha1,
        'tools.auth_digest.key'     : 'f565c27146793cfb',
      }
    }
    
    cherrypy.tree.mount(clientsCatalog, clientsCatalog.service, conf)
    cherrypy.config.update({'server.socket_host':clientsCatalog.clientsCatalogIP})
    cherrypy.config.update({'server.socket_port':clientsCatalog.clientsCatalogPort})
    cherrypy.engine.start()
    while True:
        time.sleep(1)
    cherrypy.engine.block()
