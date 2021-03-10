

class Calculator(MRT_calculator,PMV_calculator):
    def __init__(self):
        pass

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
        self.PMV_parameters=[]

    def PMV_calculation(self,temperature,temp_g, wind,eg,d):
        

    def PMV_dict(self,body):
        