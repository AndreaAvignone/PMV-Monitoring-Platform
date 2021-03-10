import numpy as np


class MRT_calculator(object):
    def __init__(self):
        self.MRT_parameters=["temperature","temperature_g","emissivity","diameter","wind"]

    def MRT_calculation(self,temperature,temp_g, wind,eg,d):
        MRT=(((temp_g+273.15)**4+(1.335*(10**8)*(wind**0.71))/(eg*(d**0.4))*(temp_g-temperature))**0.25)-273.15
        return round(MRT,4)

    def MRT_dict(self,body):
        temperature=body['temperature']
        temp_g=body['temperature_g']
        wind=round(body['wind']/3.6,5)
        emissivity=body['emissivity']
        diameter=body['diameter']
        if temperature is not None and temp_g is not None and wind is not None:
            return self.MRT_calculation(temperature,temp_g,wind,emissivity,diameter)

class PMV_calculator(object):
    def __init__(self):
        self.PMV_parameters=["M_met","W_met","Icl_clo","temperature","MRT","wind","humidity"]


    def PMV_calculation(self,M_met,W_met,Icl_clo,temperature,MRT,wind,humidity):
        M=M_met*58.2 #convert met in W/m^2
        W=W_met*58.2 
        Icl=Icl_clo*0.155 #convert clo in m^2°C/W
        #SATURATED VAPOUR PRESSURE OF WATER #ta in °C and P_sat in Pa
        P_sat=np.exp(20.386-(5132/(temperature+273)))*133.322
        # WATER VAPOUR PARTIAL PRESSURE [0 Pa, 2700 Pa]
        pa= humidity/100*P_sat
        tsk=35.7-0.028*(M-W) #SKIN EXTERNAL TEMPRATURE
        #fcl is CLOTHING SURFACE AREA FACTOR ~[1.05, 1.31]
        if Icl<=0.0775: #in mK/W (it's the same number!) =0.5clo
            fcl=1+1.29*Icl
        else:
            fcl=1.05+0.645*Icl
        #tcl is CLOTHING SURFACE TEMPERATURE to be calculated iteratively
        tcl=(temperature+tsk)/2 #starting value for iteration
        #hc is convection coefficient
        #first evaluation of hc with starting value of tcl
        B=2.38*abs(tcl-temperature)**0.25
        if B>np.sqrt(wind)*12.1:
            hc=B
        else:
            hc=12.1*np.sqrt(wind)
        diff=10
        #iteration to evaluate tcl till convergence of solution
        while diff>0.0001:
            tcl_new=tsk-Icl*3.96*10**(-8)*fcl*((tcl+273)**4-(MRT+273)**4)-Icl*fcl*hc*(tcl-temperature)
            diff=abs(tcl-tcl_new)
            tcl=(tcl_new+tcl)/2
        #evaluate again hc with optimal value found for tcl
        B=2.38*abs(tcl-temperature)**0.25
        if B>np.sqrt(wind)*12.1:
            hc=B
        else:
            hc=12.1*np.sqrt(wind)
        #SENSITIVE HEAT LOSSES
        H1=3.96*(10**(-8))*fcl*((tcl+273)**4-(MRT+273)**4) #RADIATION
        H2=fcl*hc*(tcl-temperature) #CONVECTION
        #HEAT EXCHANGE BY EVAPORATION ON THE SKIN
        Ec1=3.05*(10**(-3))*(5733-6.99*(M-W)-pa) #PERSPIRATION
        Ec2=0.42*((M-W)-58.15) #SWEATING
        #HEAT EXCHANGE BY CONVECTION IN BREATHING
        Cres=0.0014*M*(34-temperature)
        #EVAPORATIVE HEAT EXCHANGE IN BREATHING
        Eres=1.7*10**(-5)*M*(5867-pa)
        #SUM OF EXCHANGES WITH SURROUNDING ENVIRONMENT
        Q=H1+H2+Ec1+Ec2+Cres+Eres
        #(M-W-Q) is the heat balance of human body where M-W is the heat produced 
        PMV=(0.303*np.exp(-0.036*M)+0.028)*(M-W-Q)
        return round(PMV,4)

    def PMV_dict(self,body):
        temperature=body['temperature']
        wind=round(body['wind']/3.6,5)
        humidity=body['humidity']
        MRT=body['MRT']
        M_met=body['M_met']
        W_met=body['W_met']
        Icl_clo=body['Icl_clo']
        if temperature is not None and wind is not None and humidity is not None and MRT is not None and M_met is not None and W_met is not None and Icl_clo is not None:
            pmv=self.PMV_calculation(M_met,W_met,Icl_clo,temperature,MRT,wind,humidity)
            return pmv
                

class PPD_calculator(object):
    def __init__(self):
        self.PPD_parameters=["PMV"]

    def PPD_calculation(self, PMV):
        PPD=100-95*np.exp(-(0.03353*(PMV**4)+0.2179*(PMV**2)))
        return round(PPD,2)

    def PPD_dict(self, body):
        PMV=body['PMV']
        if PMV is not None:
            return self.PPD_calculation(PMV)
        
class Calculator(MRT_calculator,PMV_calculator,PPD_calculator):
    def __init__(self):
        MRT_calculator.__init__(self)
        PMV_calculator.__init__(self)
        PPD_calculator.__init__(self)
        

        