"""
AquaDreams Temperature Reader Module

This module provides functionality for reading temperature data from DS18B20 1-wire sensors
on Raspberry Pi and publishing the readings to an MQTT broker for the AquaDreams aquarium
monitoring system.

The module interfaces with the Linux kernel's 1-wire subsystem (/sys/bus/w1/devices/)
to read temperature data and formats it into structured JSON payloads with metadata
including device identification, timestamps, and TTL for data retention.

Classes:
    TemperaturePublisher: Main class for reading sensor data and publishing via MQTT.

Typical Usage:
    Direct execution for continuous monitoring:
        $ python -m AquaSensors.aqua_dream_temp_reader
    
    Programmatic usage:
        from AquaSensors.aqua_dream_temp_reader import TemperaturePublisher
        
        publisher = TemperaturePublisher(topic="my-topic", ttl_days=30)
        publisher.publish_once()  # Single reading
        # or
        publisher.run(interval_seconds=10)  # Continuous monitoring

Hardware Requirements:
    - Raspberry Pi with 1-wire interface enabled
    - DS18B20 temperature sensor connected to GPIO (typically GPIO4)
    - Sensor device should appear as /sys/bus/w1/devices/28-*

Dependencies:
    - awscrt: AWS CRT library for MQTT communication
    - mqtt_client: Local module for MQTT connection management
    - utils.get_pi_serial: Utility for retrieving Raspberry Pi serial number
"""

import datetime as dt
import glob
import time
import json
from awscrt import mqtt
from .mqtt_client import mqtt_client
from .utils.get_pi_serial import get_pi_serial


class TemperaturePublisher:
    """
    A publisher for reading and transmitting temperature data from DS18B20 sensor via MQTT.

    This class interfaces with a DS18B20 1-wire temperature sensor connected to a Raspberry Pi
    and publishes the readings to an MQTT broker. Each reading includes metadata such as device ID,
    timestamp, and configurable TTL for data retention.

    Attributes:
        base_dir (str): Base directory for 1-wire devices (/sys/bus/w1/devices/).
        device_folder (str): Path to the detected DS18B20 sensor device.
        device_file (str): Full path to the sensor's w1_slave file for reading temperature.
        mqtt_connection: MQTT connection instance for publishing data.
        topic (str): MQTT topic where temperature data is published.
        cpu_id (str): Unique CPU serial number of the Raspberry Pi.
        pk (str): Primary key for the data record (format: {cpu_id}#temperature).
        device_id (str): Identifier for the device (same as cpu_id).
        metric_type (str): Type of metric being measured (always "temperature").
        ttl_days (int): Number of days before the data record expires.

    Args:
        topic (str, optional): MQTT topic for publishing temperature data. 
            Defaults to "pi-aqua-dreams/temperature".
        ttl_days (int, optional): Time-to-live in days for published data records.
            Defaults to 90.

    Raises:
        RuntimeError: If the CPU ID cannot be retrieved from the Raspberry Pi.
        IndexError: If no DS18B20 sensor (28-* device) is found in /sys/bus/w1/devices/.

    Example:
        >>> publisher = TemperaturePublisher(topic="my-topic", ttl_days=30)
        >>> publisher.run(interval_seconds=10)  # Publish every 10 seconds
    """
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
        with open(self.device_file, encoding='utf-8') as f:
            lines = f.readlines()

        # Wait until CRC = YES
        while lines[0].strip()[-3:] != "YES":
            time.sleep(0.2)
            with open(self.device_file, encoding='utf-8') as f:
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
    pass