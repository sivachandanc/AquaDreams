from awscrt import mqtt
from awsiot import mqtt_connection_builder
import os, glob, time, json
from mqtt_client import mqtt_client
from utils.get_pi_serial import get_pi_serial
import time, datetime as dt

"""
{ "pk": "tank-01#temperature",
"ts": 1739999123456,
"value": 24.6,
"unit": "C",
"device_id": "tank-01",
"metric_type": "temperature",
"date_ymd": "2025-10-20",
"quality": "ok",
"ttl": 1766534400 }
"""


base_dir = "/sys/bus/w1/devices/"
device_folder = glob.glob(base_dir + "28-*")[0]
device_file = device_folder + "/w1_slave"


def read_temp():

    with open(device_file) as f:
        lines = f.readlines()
    while lines[0].strip()[-3:] != "YES":
        time.sleep(0.2)
        with open(device_file) as f:
            lines = f.readlines()
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        return float(lines[1][equals_pos + 2 :]) / 1000.0


mqtt_connection = mqtt_client()
topic = "pi-aqua-dreams/temperature"
cpu_id = get_pi_serial()
if cpu_id is None:
    print("❌ Error getting CPU ID")
    exit(1)

pk = f"{cpu_id}#temperature"
device_id = cpu_id
metric_type = "temperature"


while True:
    date_ymd = dt.datetime.utcnow().strftime("%Y-%m-%d")
    temp_c = read_temp()
    payload = json.dumps(
        {
            "pk": pk,
            "ts": int(time.time() * 1000),
            "value": temp_c,
            "unit": "C",
            "device_id": device_id,
            "metric_type": metric_type,
            "date_ymd": date_ymd,
            "quality": "ok",
            "ttl": int((dt.datetime.utcnow() + dt.timedelta(days=90)).timestamp())
        }
    )
    mqtt_connection.publish(topic=topic, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published:", payload)
    time.sleep(5)
