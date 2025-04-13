# HA-VGINV

This script reads status information from the VGInverter/SolSmart 1450 (possibly others) over Bluetooth, 
and sends the data to Home Assistant over MQTT. 

Information such as battery level, load percentage, charge/discharge current, mains voltage, etc. 

## Caveat: 

On the VGuard Solsmart 1450 this was tested on, there is a bug in the inverter that causes the "smart" features to crash in a day or two. 

No vital functions are disrupted by this, only the ESP32 in the device seems to be crashing, not the main controller. 

I was able to restore function only by disconnecting and reconnecting the storage battery. It seems this script is not practical until VGuard fixes the bug and updates the firmware. Which is likely never. YMMV. 

On the other hand, you can crash SolSmart inverters without physical access if you bring a bluetooth-capable device near them running this script or a phone app making constant bluetooth LE requests. 

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
## License
Copyright 2025 Mathews Sunny

Licensed under GNU GPL V3 or later. 
