import cherrypy
import json
import os
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
        self.clientsCatalogIP=self.MyClientsCatalog.clientsContent['IP_address']
        self.clientsCatalogPort=self.MyClientsCatalog.clientsContent['port']
        self.service=self.registerRequest()
        self.flagNew=False

    def registerRequest(self):
        msg={"service":"clients_catalog","IP_address":self.clientsCatalogIP,"port":self.clientsCatalogPort}
        try:
            service=requests.put(f'{self.serviceCatalogAddress}/register',json=msg).json()
            return service
        except:
            print("Failure in registration.")
            return False

    def GET(self,*uri,**params):
        if (len(uri))>0 and uri[0]=="reg":
            return open('etc/reg.html')

        elif (len(uri)>0 and uri[0]=="reg_results"):
            for user in self.MyClientsCatalog.clientsContent.get("users_list"):
                if user['user_ID']==params['userID']:
                    return open("etc/fail_reg_user.html") 
            if params['psw']!=params['psw-repeat']:
                return open("etc/fail_reg_pass.html") 

            else:
                self.MyClientsCatalog.clientsContent["users_list"].append({
                    "user_ID":params['userID'],
                    "catalog_list":[],
                    "password":params['psw']
                    })
                self.MyClientsCatalog.save()
                self.checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(self.MyClientsCatalog.userpassdict)
                self.flagNew=True
                return open("etc/correct_reg.html")
        elif(len(uri))>0 and uri[0]=="login":
        
            data=self.MyClientsCatalog.find(str(cherrypy.request.login)).copy()
            print(data)
            del data['password']
            return json.dumps(data)
    def PUT(self,*uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        if command=='insertProfile':
            user=str(cherrypy.request.login)
            outputFlag=self.MyClientsCatalog.addPlatform(user,json_body['platform_ID'])
            if outputFlag:
                output="'{}' added to user '{}'".format(json_body['platform_ID'],user)
                self.MyClientsCatalog.save()
                
            else:
                output="'{}' cannot be added to user '{}'".format(json_body['platform_ID'],user)
        else:
            raise cherrypy.HTTPError(501,"No operation!")
        print(output)
        result={"result":outputFlag}
        return json.dumps(result)
    def DELETE(self,*uri):
        command=str(uri[0])
        if command=='removePlatform':
            platform_ID=uri[1]
            user=str(cherrypy.request.login)
            outputFlag=self.MyClientsCatalog.removePlatform(user,platform_ID)
            if outputFlag==True:
                output="Platform '{}' removed".format(platform_ID)
                self.MyClientsCatalog.save()
            else:
                output="Platform '{}' not found ".format(platform_ID)
        
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        print(output)
        result={"result":outputFlag}
        return json.dumps(result)
        
if __name__ == '__main__':
    clients_db=sys.argv[1]
    clientsCatalog=Registration_deployer(clients_db)
    get_ha1 = cherrypy.lib.auth_digest.get_ha1_dict_plain(clientsCatalog.MyClientsCatalog.userpassdict)
    clientsCatalog.checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(clientsCatalog.MyClientsCatalog.userpassdict)
    conf = {
      'global' : {
        'server.socket_host' : clientsCatalog.clientsCatalogIP,
        'server.socket_port' : clientsCatalog.clientsCatalogPort,
        #'server.thread_pool' : 8
      },
      '/' : {
        # HTTP verb dispatcher
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.staticdir.root': os.path.abspath(os.getcwd()),
        'tools.sessions.on': True,
        # Basic Auth
        'tools.auth_basic.on'      : True,
        'tools.auth_basic.realm'   : 'Francis Drake',
        'tools.auth_basic.checkpassword' : clientsCatalog.checkpassword
        # Digest Auth
        #'tools.auth_digest.on'      : True,
        #'tools.auth_digest.realm'   : 'Francis Drake',
        #'tools.auth_digest.get_ha1' : get_ha1,
        #'tools.auth_digest.key'     : 'f565c27146793cfb',
      }
    }
    
    cherrypy.tree.mount(clientsCatalog, clientsCatalog.service, conf)
    cherrypy.config.update({'server.socket_host':clientsCatalog.clientsCatalogIP})
    cherrypy.config.update({'server.socket_port':clientsCatalog.clientsCatalogPort})
    cherrypy.engine.start()
    while True:
        if clientsCatalog.flagNew:
            clientsCatalog.flagNew=False
            cherrypy.engine.stop()
            cherrypy.server.httpserver=None
            clientsCatalog.MyClientsCatalog.createDict()
            conf = {
              'global' : {
                'server.socket_host' : clientsCatalog.clientsCatalogIP,
                'server.socket_port' : clientsCatalog.clientsCatalogPort,
                #'server.thread_pool' : 8
              },
              '/' : {
                # HTTP verb dispatcher
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.sessions.on': True,
                # Basic Auth
                'tools.auth_basic.on'      : True,
                'tools.auth_basic.realm'   : 'Francis Drake',
                'tools.auth_basic.checkpassword' : clientsCatalog.checkpassword
                # Digest Auth
                #'tools.auth_digest.on'      : True,
                #'tools.auth_digest.realm'   : 'Francis Drake',
                #'tools.auth_digest.get_ha1' : get_ha1,
                #'tools.auth_digest.key'     : 'f565c27146793cfb',
              }
            }
            
            cherrypy.tree.mount(clientsCatalog, clientsCatalog.service, conf)
            cherrypy.config.update({'server.socket_host':clientsCatalog.clientsCatalogIP})
            cherrypy.config.update({'server.socket_port':clientsCatalog.clientsCatalogPort})
            cherrypy.engine.start()
        time.sleep(1)
        
    cherrypy.engine.block()
