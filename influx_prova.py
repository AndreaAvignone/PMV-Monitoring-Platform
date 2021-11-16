from influxdb import InfluxDBClient

if __name__=='__main__':
    client=InfluxDBClient(host='localhost',port=8086)
    client.create_database('esempio')
    s=client.get_list_database()
    print(s)