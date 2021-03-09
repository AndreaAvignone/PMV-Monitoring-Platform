
class MRT_calculator(object):
    def __init__(self):
        parameters=["temperature","temperature_g","emissivity","diameter","wind"]

    def MRT_calculation(self,temperature,temp_g, wind,eg,d):
        MRT=(((temp_g+273.15)**4+(1.335*(10**8)*(wind**0.71))/(eg*(d**0.4))*(temp_g-temperature))**0.25)-273.15
        return MRT

    def MRT_JSON(self,body):
        temperature=body['temperature']
        temp_g=body['temperature_g']
        wind=body['wind']/3.6
        print(wind)
        emissivity=body['emissivity']
        diameter=body['diameter']
        return self.MRT_calculation(temperature,temperature_g,wind,emissivity,diameter)



    