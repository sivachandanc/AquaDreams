from awscrt import mqtt
from awsiot import mqtt_connection_builder
import os, glob, time, json
from mqtt_client import mqtt_client

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28-*')[0]
device_file = device_folder + '/w1_slave'

def read_temp():
    with open(device_file) as f:
        lines = f.readlines()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        with open(device_file) as f:
            lines = f.readlines()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        return float(lines[1][equals_pos+2:]) / 1000.0


mqtt_connection = mqtt_client()
topic = "pi-aqua-dreams/temp"

while True:
    temp_c = read_temp()
    payload = json.dumps({"temperature_c": temp_c, "timestamp": int(time.time())})
    mqtt_connection.publish(topic=topic, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published:", payload)
    time.sleep(5)

