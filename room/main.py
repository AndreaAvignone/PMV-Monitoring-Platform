from conf.Generic_Sensor import *
import time
import sys

if __name__ == '__main__':
    settingFile=sys.argv[1]
    device_ID=sys.argv[2]
    pin=sys.argv[3]
    class_imported=__import__(device_ID+'_class')
    sensor_class=getattr(class_imported,device_ID)
    sensor=sensor_class(settingFile,device_ID,pin)
    sensor.start()
    print(f"Installing device {device_ID}...")
    if not sensor.setup():
        print("Server connection failed.")
    else:
        print("Server connection performed.")
    time.sleep(1)
    while True:
        output=sensor.retrieveData()
        try:
            sensor.publishData(output)
            time.sleep(sensor.time_sleep)
        except:
            time.sleep(1)

