import asyncio
from bleak import BleakClient

UPS_ADDRESS = os.getenv("UPS_ADDRESS", "aa:bb:cc:dd:ee:ff")  # Edit in vginverter.env file or edit here
WRITE_UUID = "0003cdd2-0000-1000-8000-00805f9b0131"
NOTIFY_UUID = "0003cdd1-0000-1000-8000-00805f9b0131"

# This script reads all the codes I got from snooping bluetooth
# For further development purposes

# Mapping: command prefix → (friendly name, divisor)
sensor_requests = {
    bytes.fromhex("ff0100340c00"): ("value", 1),
    bytes.fromhex("ff0b00220c00"): ("value", 1),
    bytes.fromhex("ff8a8f360c00"): ("value", 1),
    bytes.fromhex("ffffff060c01"): ("value", 1),
    bytes.fromhex("ffffff080c01"): ("value", 1),
    bytes.fromhex("ffffff0c0c01"): ("value", 1),
    bytes.fromhex("ffffff100c01"): ("value", 1),
    bytes.fromhex("ffffff160c01"): ("value", 1),
    bytes.fromhex("ffffff1c0c01"): ("value", 1),
    bytes.fromhex("ffffff1e0c01"): ("value", 1),
    bytes.fromhex("ffffff280c01"): ("value", 1),
    bytes.fromhex("ffffff2c0c01"): ("value", 1),
    bytes.fromhex("ffffff300c01"): ("value", 1),
    bytes.fromhex("ffffff320c01"): ("value", 1),
    bytes.fromhex("ffffff380c01"): ("value", 1),
    bytes.fromhex("ffffff3c0c01"): ("value", 1),
    bytes.fromhex("ffffff740c01"): ("value", 1),
    bytes.fromhex("ffffff760c01"): ("value", 1),
    bytes.fromhex("ffffff8a0c01"): ("value", 1),
    bytes.fromhex("ffffff900c01"): ("value", 1),
    bytes.fromhex("ffffff960c01"): ("value", 1),
    bytes.fromhex("ffffffb00b01"): ("value", 1),
    bytes.fromhex("ffffffc80b01"): ("value", 1),
    bytes.fromhex("ffffffca0b01"): ("value", 1),
    bytes.fromhex("ffffffcc0b01"): ("value", 1),
}

# Pad with FFFF at end to make full write command
full_requests = {prefix: prefix + b'\xFF\xFF' for prefix in sensor_requests}

def notification_handler(sender, data):
    print(f"{data.hex()}")

    prefix = bytes(data[:6])
    value_bytes = data[-2:]

    if prefix in sensor_requests:
        name, divisor = sensor_requests[prefix]
        raw_value = int.from_bytes(value_bytes, byteorder='little')
        value = raw_value / divisor
        print(f"{value:.0f}")
    else:
        print(f"❓ Unknown response: {data.hex()}")

async def main():
    async with BleakClient(UPS_ADDRESS) as client:
        if not client.is_connected:  # ✅ No longer a coroutine!
            print("❌ Not connected.")
            return

        #print("✅ Connected...")
        await client.start_notify(NOTIFY_UUID, notification_handler)

        for prefix, request in full_requests.items():
            name = sensor_requests[prefix][0]
            #print(f"📤 Requesting {name}...")
            await client.write_gatt_char(WRITE_UUID, request)
            await asyncio.sleep(0.5)  # Short pause between writes

        await asyncio.sleep(2.0)  # Allow time for all responses
        await client.stop_notify(NOTIFY_UUID)
        #print("✅ Done.")

asyncio.run(main())
