import asyncio
from bleak import BleakClient
import paho.mqtt.client as mqtt
import time
import json
import os

"""
    V-Guard VGInverter Bluetooth to MQTT Script
    
    Copyright 2025 Mathews Sunny
    
    This program is free software: you can redistribute it and/or modify it under the terms 
    of the GNU General Public License as published by the Free Software Foundation, 
    either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. 
    If not, see <https://www.gnu.org/licenses/>.

"""

"""

    Changelog:
    1.0: Initial release
    1.1: Initial release was broken, mqtt port fix
    1.2: Round battery level value before sending
    1.3: Revamped poll_ups()
    1.4: Added UPS offline mqtt topic 

"""

# === CONFIGURATION ===
UPS_ADDRESS = os.getenv("UPS_ADDRESS")  # Replace in vginverter.env file 
WRITE_UUID = "0003cdd2-0000-1000-8000-00805f9b0131"
NOTIFY_UUID = "0003cdd1-0000-1000-8000-00805f9b0131"

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")  # Edit vginverter.env file 
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC_PREFIX = "home/ups"
POLL_INTERVAL = 20  # seconds
AVAILABILITY_TOPIC = f"{MQTT_TOPIC_PREFIX}/status"

# === SENSOR DEFINITIONS ===
sensor_requests = {
    bytes.fromhex("FFFFFF080C01"): {
        "name": "Mains Voltage",
        "divisor": 10,
        "unit": "V",
        "device_class": "voltage"
    },
    bytes.fromhex("FFFFFF060C01"): {
        "name": "Battery Voltage",
        "divisor": 100,
        "unit": "V",
        "device_class": "voltage"
    },
    bytes.fromhex("FFFFFF100C01"): {
        "name": "Charge Current",
        "divisor": 10,
        "unit": "A",
        "device_class": "current"
    },
    bytes.fromhex("FFFFFF0C0C01"): {
        "name": "Discharge Current",
        "divisor": 10,
        "unit": "A",
        "device_class": "current"
    },
    bytes.fromhex("FFFFFF2C0C01"): {
        "name": "Load Percentage",
        "divisor": 1,
        "unit": "%",
        "device_class": "power_factor"  # closest match, optional
    },
    bytes.fromhex("FFFFFF3C0C01"): {
        "name": "Battery Charge Level",
        "divisor": 297,  # 300 means 100% is reported as 30000
        "unit": "%",
        "device_class": "battery"
    }
}


# Add FFFF suffix to build write command
full_requests = {prefix: prefix + b'\xFF\xFF' for prefix in sensor_requests}

# === GLOBALS ===
received_data = {}
mqtt_client = mqtt.Client()

def publish_discovery_configs():
    print("📡 Publishing MQTT discovery configs...")

    device_info = {
        "identifiers": ["home-ups"],
        "name": "VGInverter",
        "manufacturer": "V-Guard",
        "model": "SOLSMART 1450"
    }

    for prefix, info in sensor_requests.items():
        name = info["name"]
        unit = info["unit"]
        device_class = info["device_class"]

        key = name.replace(" ", "_").lower()
        topic = f"{MQTT_TOPIC_PREFIX}/{key}"
        discovery_topic = f"homeassistant/sensor/home_ups_{key}/config"

        payload = {
            "name": name,
            "state_topic": topic,
            "unit_of_measurement": unit,
            "device_class": device_class,
            "state_class": "measurement",
            "unique_id": f"home_ups_{key}",
            "device": device_info
        }

        mqtt_client.publish(discovery_topic, json.dumps(payload), retain=True)
        print(f"✅ Discovery config sent for: {name}")
        
    status_payload = {
        "name": "UPS Availability",
        "state_topic": AVAILABILITY_TOPIC,
        "payload_on": "online",
        "payload_off": "offline",
        "device_class": "connectivity",
        "unique_id": "home_ups_status",
        "device": device_info
    }

    mqtt_client.publish("homeassistant/binary_sensor/home_ups_status/config", json.dumps(status_payload), retain=True)
    print(f"✅ Discovery config sent for: UPS Availability")

def notification_handler(sender, data):
    prefix = bytes(data[:6])
    value_bytes = data[-2:]

    if prefix in sensor_requests:
        info = sensor_requests[prefix]
        name = info["name"]
        divisor = info["divisor"]
        value = int.from_bytes(value_bytes, "little") / divisor
        received_data[name] = round(value, 2)
        #print(f"📡 {name}: {value:.2f}")
    else:
        print(f"❓ Unknown data: {data.hex()}")

async def poll_ups():
    client = BleakClient(UPS_ADDRESS)

    while True:
        try:
            print(f"\n🔄 Polling UPS at {time.strftime('%H:%M:%S')}...")

            if not client.is_connected:
                print("🔌 Connecting to UPS...")
                await client.connect()

                if not client.is_connected:
                    print("❌ Failed to connect to UPS.")
                    raise RuntimeError("Could not connect to UPS")

                mqtt_client.publish(AVAILABILITY_TOPIC, "online", retain=True)
                print("✅ Published UPS availability: online")

                await client.start_notify(NOTIFY_UUID, notification_handler)
                print("✅ BLE notifications enabled")

            received_data.clear()

            for prefix, request in full_requests.items():
                name = sensor_requests[prefix]["name"]
                print(f"📤 Requesting {name}...")
                await client.write_gatt_char(WRITE_UUID, request)
                await asyncio.sleep(0.25)

            await asyncio.sleep(2.0)  # Wait for all notifications

            # Publish all received values to MQTT
            for name, value in received_data.items():
                topic = f"{MQTT_TOPIC_PREFIX}/{name.replace(' ', '_').lower()}"
                mqtt_client.publish(topic, value)
                print(f"📤 MQTT: {topic} = {value}")

        except Exception as e:
            print(f"⚠️ Error during polling: {e}")

            try:
                if client.is_connected:
                    await client.stop_notify(NOTIFY_UUID)
                    await client.disconnect()
                    print("🔌 Disconnected from UPS after error")
            except Exception:
                pass

            mqtt_client.publish(AVAILABILITY_TOPIC, "offline", retain=True)
            print("✅ Published UPS availability: offline")
            print("⏳ Waiting 10s before retrying...")
            await asyncio.sleep(10)

        await asyncio.sleep(POLL_INTERVAL)


def main():
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            publish_discovery_configs()  # 👈 send discovery when connected
        else:
            print(f"❌ MQTT connection failed with code {rc}")

    def on_disconnect(client, userdata, rc):
        print("⚠️ MQTT disconnected. Reconnecting in 5 seconds...")
        time.sleep(5)
        try:
            client.reconnect()
        except Exception as e:
            print(f"❌ MQTT reconnect failed: {e}")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"❌ Initial MQTT connect failed: {e}")
        return

    mqtt_client.loop_start()  # run MQTT network loop in background
    print(f"🚀 Starting UPS monitor (poll every {POLL_INTERVAL}s)")
    asyncio.run(poll_ups())


if __name__ == "__main__":
    main()
