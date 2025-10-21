from awscrt import mqtt
from awsiot import mqtt_connection_builder
import os


def mqtt_client():
    try:
        CERT_DIR = "/home/sivachandan/AquaSensors/certs"
        CA = os.path.join(CERT_DIR, "AmazonRootCA1.pem")
        CERT = os.path.join(
            CERT_DIR,
            "5ddb201d4ac939508f608bc9d497e59eeb18c5741f08945a1dbc6ed8c50afc87-certificate.pem.crt",
        )
        KEY = os.path.join(
            CERT_DIR,
            "5ddb201d4ac939508f608bc9d497e59eeb18c5741f08945a1dbc6ed8c50afc87-private.pem.key",
        )

        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint="ar1b3cylu99rl-ats.iot.us-east-1.amazonaws.com",
            cert_filepath=CERT,
            pri_key_filepath=KEY,
            ca_filepath=CA,
            client_id="pi-aqua-dreams",
            keep_alive_secs=60,
        )

        mqtt_connection.connect().result()
        print("✅ Connected to AWS IoT Core")
        return mqtt_connection
    except Exception as e:
        print(f"❌ Error connecting to AWS IoT Core: {e}")
        return None
