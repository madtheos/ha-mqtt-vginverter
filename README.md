# HA-VGINV

This script reads status information from the V-Guard SolSmart 1450 (possibly others) over Bluetooth LE, 
and sends the data to Home Assistant over MQTT. 

Information includes battery level, load percentage, charge/discharge current, mains voltage, etc. 

## Installation:

To install on a Raspberry Pi/Pi Zero W:

1. Install dependencies: 
```bash
sudo apt install python3 python3-bleak python3-paho-mqtt
```

2. Clone repo.
```bash
git clone https://github.com/madtheos/ha-mqtt-vginverter.git
```

3. Find the MAC address of your inverter/ups using the OEM app or a Bluetooth scanner app such as nRF Connect. 

4. - Add the MAC address directly to the script and then run it directly, skipping the rest of the steps. 
   - OR
   - Edit the example files for the systemd service with your data. 

5. Copy the service file to something like **/etc/systemd/system/vginverter.service**
   
6. Create the service:
```bash
sudo systemctl daemon-reload 
sudo systemctl enable --now vginverter.service
```

## Firmware Bug and Crashes: 

An earlier version of this script opened and closed a BLE connection each time, and this caused the "smart" features to crash within a day or two. Likely because of a memory leak. This was tested on the VGuard Solsmart 1450. 

No vital functions are disrupted by this, as only the ESP32 inside the inverter crashes, not the main controller. 

I was able to restore function only by disconnecting and reconnecting the storage battery.

On the other hand, you can crash affected SolSmart inverters without physical access if you bring a bluetooth-capable device near them running that version of the script or perhaps a phone app making constant bluetooth LE connections. Don't do this. 

## License

Copyright 2025 Mathews Sunny

Licensed under GNU GPL V3 or later. 
