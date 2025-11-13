from awscrt import mqtt
from awsiot import mqtt_connection_builder
import os, glob, time, json
from mqtt_client import mqtt_client
from utils.get_pi_serial import get_pi_serial
import datetime as dt


class TemperaturePublisher:
    def __init__(self, topic="pi-aqua-dreams/temperature", ttl_days=90):
        self.base_dir = "/sys/bus/w1/devices/"
        self.device_folder = glob.glob(self.base_dir + "28-*")[0]
        self.device_file = self.device_folder + "/w1_slave"

        # MQTT Connection
        self.mqtt_connection = mqtt_client()
        self.topic = topic

        # Device metadata
        self.cpu_id = get_pi_serial()
        if self.cpu_id is None:
            raise RuntimeError("❌ Error getting CPU ID")

        self.pk = f"{self.cpu_id}#temperature"
        self.device_id = self.cpu_id
        self.metric_type = "temperature"
        self.ttl_days = ttl_days


    def read_temp(self):
        """Reads raw temperature from DS18B20 1-wire sensor."""
        with open(self.device_file) as f:
            lines = f.readlines()

        # Wait until CRC = YES
        while lines[0].strip()[-3:] != "YES":
            time.sleep(0.2)
            with open(self.device_file) as f:
                lines = f.readlines()

        equals_pos = lines[1].find("t=")
        if equals_pos != -1:
            return float(lines[1][equals_pos + 2:]) / 1000.0

        return None


    def build_payload(self, value: float) -> str:
        """Construct JSON payload."""
        date_ymd = dt.datetime.utcnow().strftime("%Y-%m-%d")
        ttl_ts = int((dt.datetime.utcnow() + dt.timedelta(days=self.ttl_days)).timestamp())

        payload = {
            "pk": self.pk,
            "ts": int(time.time() * 1000),
            "value": value,
            "unit": "C",
            "device_id": self.device_id,
            "metric_type": self.metric_type,
            "date_ymd": date_ymd,
            "quality": "ok",
            "ttl": ttl_ts,
        }

        return json.dumps(payload)


    def publish_once(self):
        """Reads temperature, builds payload, and publishes one message."""
        temp_c = self.read_temp()
        payload = self.build_payload(temp_c)

        self.mqtt_connection.publish(
            topic=self.topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

        print("Published:", payload)
        return temp_c


    def run(self, interval_seconds=5):
        """Infinite loop publishing temperature."""
        print("📡 Temperature publisher started... press Ctrl+C to stop.")
        try:
            while True:
                self.publish_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("🛑 Stopped by user.")


# Optional: Run directly if executed as script
if __name__ == "__main__":
    pub = TemperaturePublisher()
    pub.run()
