import requests
import json
import time

#server_url="587f7d3d617a.ngrok.io"

class GrafanaCatalog():
    def __init__(self, org_db_filename):
        self.org_db_filename=org_db_filename #org_db.json
        self.orgContent=json.load(open(self.org_db_filename,"r"))
        self.usersContent=json.load(open("etc/users_db.json","r"))

        self.serviceCatalogAddress=self.orgContent['service_catalog']
        
        self.requestResult=requests.get(self.serviceCatalogAddress+"/influx_db").json()
        self.influxIP=self.requestResult.get("IP_address")
        self.influxPort=self.requestResult.get("port")

        self.db_url="http://"+self.influxIP+":"+str(self.influxPort)

        self.requestResult2=requests.get(self.serviceCatalogAddress+"/public"+"/grafana").json()
        self.server_url=self.requestResult2.get("IP_address")

        self.requestResult3=requests.get(self.serviceCatalogAddress+"/public"+"/server_catalog").json()
        self.server_warningIP=self.requestResult3.get("IP_address")
        self.server_warningPort=self.requestResult3.get("port")
        self.server_warningService=self.requestResult3.get("service")
        self.server_warning_url=self.server_warningIP+self.server_warningService+"/warning"

    #platformID=org_name
    def createOrg(self, platformID):
        self.headers= {
        "Content-Type":"application/json",
        "Accept":"application/json"}
        #create org
        self.body={"name":platformID}
        self.url=self.server_url+"/api/orgs" #need admin authentication
        r=requests.post(url=self.url, auth=('admin','menez30lode'),headers=self.headers, data=json.dumps(self.body), verify=False)
        print(r.json())
        #save org ID of new org
        self.orgID=str(r.json()["orgId"])
        #add admin to new org
        self.body2={"loginOrEmail":"admin", "role": "Admin"}
        self.url2=self.url+"/"+self.orgID+"/users"
        r2=requests.post(url=self.url2, headers=self.headers, data=json.dumps(self.body2), verify=False)
        #print(r2.json())
        #swith active org
        self.url3=self.server_url+"/api/user/using/"+self.orgID
        r3=requests.post(url=self.url3, auth=('admin','menez30lode'),verify=False)
        #print(r3.json())
        #create api key
        self.body4={"name":platformID+"_key", "role":"Admin"}
        self.url4=self.server_url+"/api/auth/keys"
        r4=requests.post(url=self.url4, auth=('admin','menez30lode'), headers=self.headers, data=json.dumps(self.body4), verify=False)
        #print(r4.json())
        #add new organization to json file
        new_org={
            "org_name":platformID,
            "orgId":self.orgID,
            "key_name":r4.json()["name"],
            "keyId":r4.json()["id"],
            "key":r4.json()["key"],
            "dashboards":[]
            }

        return new_org
        
    def orgListCreate(self):
        self.orgList=[]
        for org in self.orgContent["organizations"]:
            self.orgList.append(org["org_name"])
        return self.orgList

    def retrieveOrgInfo(self, platformID):
        notFound=1
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                notFound=0
                return org
        if notFound==1:
            return False

    #def retrieveOrgParameter(self, platformID, parameter):
        org=self.retrieveOrgInfo(platformID)
        try:
            result=org[parameter]
        except:
            result=False
        return result

    def insertOrg(self, platformID):
        notExisting=1
        org=self.retrieveOrgInfo(platformID)
        if org is False:
            createdOrg=self.createOrg(platformID)
            self.orgContent["organizations"].append(createdOrg)
            self.orgContent["organizations_list"].append(platformID)
            self.save()
            #create datasource associated to organization
            self.createDatasource(platformID)
            #create user associated to organization for login
            self.insertUser(platformID, int(self.orgID))
            return True
        else:
            return False

    def findPos(self,platform_ID):
        notFound=1
        for i in range(len(self.orgContent['organizations'])): 
            if self.orgContent['organizations'][i]['org_name']==platform_ID:
                notFound=0
                return i
        if notFound==1:
            return False

    def findRoomPos(self,dashboards,room_ID):
        notFound=1
        for i in range(len(dashboards)): 
            if dashboards[i]['room_ID']==room_ID:
                notFound=0
                return i
        if notFound==1:
            return False


    def createDashboard(self, platformID, roomID, dash_info):
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                self.key=org["key"]
        self.headers= {
        "Authorization": "Bearer "+self.key,
        "Content-Type":"application/json",
        "Accept":"application/json"}

        self.url=self.server_url+"/api/dashboards/db"
        self.new_dashboard_data=json.load(open('etc/myDash.json'))
        self.new_dashboard_data["dashboard"]["title"]=platformID+"_"+roomID
        self.new_dashboard_data["dashboard"]["id"]=None
        self.new_dashboard_data["dashboard"]["uid"]=platformID+roomID
        self.new_dashboard_data["dashboard"]["title"]=dash_info["dashboard_title"]
        for panel in self.new_dashboard_data["dashboard"]["panels"]:
            if panel["type"]!="row" and panel["type"]!="text":
                panel["datasource"]=platformID
                for target in panel["targets"]:
                    if target["measurement"]!="external":
                        for tag in target["tags"]:
                            tag["value"]=roomID
                    try:
                        if target["rawQuery"]:
                            s1=target["query"]
                            s2=s1.split("'")[0]
                            s3=s1.split("'")[2]
                            s4=s2+"'"+roomID+"'"+s3
                            target["query"]=s4
                    except:
                        pass
            if panel["type"]=="graph":
                for channel in panel["alert"]["notifications"]:
                    channel["uid"]=platformID+roomID
        r=requests.post(url=self.url, headers=self.headers, data=json.dumps(self.new_dashboard_data), verify=False)
        #print(r.json())
        return self.new_dashboard_data

    def deleteDashboard(self, platformID, roomID):
        pos=self.findPos(platformID)
        if pos is not False:
            key=self.orgContent['organizations'][pos]['key']
            headers= {
                "Authorization": "Bearer "+key,
                "Content-Type":"application/json",
                "Accept":"application/json"}
            url=self.server_url+"/api/dashboards/uid/"+platformID+roomID
            r=requests.delete(url=url, headers=headers, verify=False)
            posRoom=self.findRoomPos(self.orgContent['organizations'][pos]['dashboards'],roomID)
            if posRoom is not False:
                self.orgContent['organizations'][pos]['dashboards'].pop(posRoom)
                headers= {
                        "Authorization": "Bearer "+key,
                        "Content-Type":"application/json",
                        "Accept":"application/json"}
                url=self.server_url+"/api/dashboards/uid/"+platformID+roomID
                r=requests.delete(url=url, headers=headers, verify=False)
                return True
            else:
                return False
        else:
            return False

    def getDashboard(self, platformID, roomID):
        notFound=1
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                self.key=org["key"]
                for dash in org["dashboards"]:
                    if dash["room_ID"]==roomID:
                        notFound=0
                        self.headers= {
                        "Authorization": "Bearer "+self.key,
                        "Content-Type":"application/json",
                        "Accept":"application/json"}
                        self.url=self.server_url+"/api/dashboards/uid/"+platformID+roomID
                        r=requests.get(url=self.url, headers=self.headers, verify=False)
                        dashboard_data=r.json()
                        return dashboard_data
        if notFound==1:
            return False

    def changeDashboardName(self, platformID, roomID, new_name):
        dashboard_data=self.getDashboard(platformID, roomID)
        if dashboard_data!=False:
            for org in self.orgContent["organizations"]:
                if org["org_name"]==platformID:
                    self.key=org["key"]
                    for dash in org["dashboards"]:
                        if dash["room_ID"]==roomID:
                            dash["title"]=new_name
            self.headers= {
            "Authorization": "Bearer "+self.key,
            "Content-Type":"application/json",
            "Accept":"application/json"}
            self.url=self.server_url+"/api/dashboards/db"
            dashboard_data["dashboard"]["title"]=new_name
            r=requests.post(url=self.url, headers=self.headers, data=json.dumps(dashboard_data), verify=False)
            return True
        else:
            return False


    def retrieveDashInfo(self, platformID, roomID):
        notFound=1
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                for dash in org["dashboards"]:
                    if dash["uid"]==platformID+roomID:
                        notFound=0
                        dash_url=self.getDashboardURL(platformID, roomID)
                        return dash_url
        if notFound==1:
            return False

    def getDashboardURL(self, platformID, roomID):
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                self.key=org["key"]
                self.orgID=str(org["orgId"])
        self.headers= {
        "Authorization": "Bearer "+self.key,
        "Content-Type":"application/json",
        "Accept":"application/json"}
        self.uid=platformID+roomID
        self.url=self.server_url+"/api/dashboards/uid/"+self.uid
        r=requests.get(url=self.url, headers=self.headers, verify=False)
        self.data=r.json()
        #print(data)
        self.dash_url=self.server_url+self.data["meta"]["url"]+"?orgId="+self.orgID
        return self.dash_url
    def getHomeURL(self, platformID):
        notFound=1
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                self.key=org["key"]
                self.orgID=str(org["orgId"])
                notFound=0
                break
        if notFound==0:
            self.home_url=self.server_url+"?orgId="+self.orgID
            return self.home_url
        else:
            return False

    def insertDashboard(self, platformID, roomID, dash_info):
        notExisting=1
        dash=self.retrieveDashInfo(platformID, roomID)
        if dash is False:
            createdDashboard=self.createDashboard(platformID, roomID, dash_info)
            self.createNotificationChannel(platformID, roomID)
            dash_info={"room_ID":roomID, "uid":createdDashboard["dashboard"]["uid"], "title":createdDashboard["dashboard"]["title"]}
            for org in self.orgContent["organizations"]:
                if org["org_name"]==platformID:
                    org["dashboards"].append(dash_info)
                    return True
        else:
            return False


    def createDatasource(self, platformID):
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                self.key=org["key"]
        self.headers= {
        "Authorization": "Bearer "+self.key,
        "Content-Type":"application/json",
        "Accept":"application/json"}

        self.url=self.server_url+'/api/datasources'

        self.new_datasource_data=json.load(open('etc/myDatares.json'))
        self.new_datasource_data["name"]=platformID
        self.new_datasource_data["database"]=platformID
        self.new_datasource_data["url"]=self.db_url
        r2=requests.post(url=self.url, headers=self.headers, data=json.dumps(self.new_datasource_data), verify=False)
        #print(r2.json())

    def createNotificationChannel(self, platformID, roomID):
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                key=org["key"]
        headers= {
        "Authorization": "Bearer "+key,
        "Content-Type":"application/json",
        "Accept":"application/json"}
        url=self.server_url+"/api/alert-notifications"
        body={"uid":platformID+roomID,
        "name":platformID+roomID,
        "type":"webhook",
        "settings":{
        "url":self.server_warning_url+"/"+platformID+"/"+roomID,
        "addresses": self.server_warning_url+"/"+platformID+"/"+roomID
        }}
        r=requests.post(url=url, headers=headers, data=json.dumps(body))
        print(r.json())

        return True

    def userListCreate(self):
        self.userList=[]
        for user in self.usersContent["users"]:
            self.userList.append(user["name"])
        return self.userList

    def retrieveUserInfo(self, platformID):
        notFound=1
        for user in self.usersContent["users"]:
            if user["name"]==platformID:
                notFound=0
                return users
        if notFound==1:
            return False

    def createUser(self, platformID, orgID):
        self.headers= {
        "Content-Type":"application/json",
        "Accept":"application/json"}
        self.url=self.server_url+"/api/admin/users"
        self.body={"name":platformID, "login":platformID, "password":platformID, "OrgId":orgID}
        r=requests.post(url=self.url, auth=('admin','menez30lode'),headers=self.headers, data=json.dumps(self.body), verify=False)
        #print(r.json())
        return self.body
        
    def insertUser(self, platformID, orgID):
        notExisting=1
        user=self.retrieveUserInfo(platformID)
        if user is False:
            createdUser=self.createUser(platformID, orgID)
            self.usersContent["users"].append(createdUser)
            self.usersContent["users_list"].append(platformID)
            with open('etc/users_db.json','w') as file:
                json.dump(self.usersContent,file, indent=4)
            return True
        else:
            return False


    def save(self):
        with open(self.org_db_filename,'w') as file:
            json.dump(self.orgContent,file, indent=4)
