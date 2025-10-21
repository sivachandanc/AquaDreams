import os, time, json, ssl
import paho.mqtt.client as mqtt

ENDPOINT = "ar1b3cylu99rl-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "pi-aqua-dreams"
TOPIC = f"devices/{CLIENT_ID}/telemetry"

CERT_DIR = "/home/sivachandan/aws_iot"
CA = os.path.join(CERT_DIR, "AmazonRootCA1.pem")
CERT = os.path.join(
    CERT_DIR,
    "5ddb201d4ac939508f608bc9d497e59eeb18c5741f08945a1dbc6ed8c50afc87-certificate.pem.crt",
)
KEY = os.path.join(
    CERT_DIR,
    "5ddb201d4ac939508f608bc9d497e59eeb18c5741f08945a1dbc6ed8c50afc87-private.pem.key",
)

# Preflight checks
for p in (CA, CERT, KEY):
    if not os.path.isfile(p):
        raise FileNotFoundError(f"Missing file: {p}")

client = mqtt.Client(
    client_id=CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)


def on_connect(client, userdata, flags, reason_code, properties):
    print("✅ Connected" if reason_code == 0 else f"❌ Connect failed: {reason_code}")


client.on_connect = on_connect
client.tls_set(
    ca_certs=CA, certfile=CERT, keyfile=KEY, tls_version=ssl.PROTOCOL_TLSv1_2
)

print(f"Connecting to {ENDPOINT} ...")
client.connect(ENDPOINT, port=8883, keepalive=60)
client.loop_start()

while True:
    payload = {"timestamp": int(time.time()), "temperature_c": 25.4, "oxygen_mgL": 6.8}
    client.publish(TOPIC, json.dumps(payload), qos=1).wait_for_publish()
    print("📤 Sent:", payload)
    time.sleep(5)
