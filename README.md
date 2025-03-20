# HA-VGINV

This script reads the VGInverter/SolSmart 1450 (possibly others) over Bluetooth 
and sends the data to Home Assistant over MQTT. 

## Installation:

To install on a Raspberry Pi/Pi Zero W:

1. Install dependencies: 
   
    **sudo apt install python3 python3-bleak python3-paho-mqtt**

2. Clone repo. 

3. Edit the example files with your data. You might need to use the OEM app or a Bluetooth scanner to find the MAC address of your inverter/ups. 

5. Copy the service file to something like **/etc/systemd/system/vginverter.service**
   
6. Create the service:

   **sudo systemctl daemon-reload**    
   **sudo systemctl enable --now vginverter.service**

## License
Copyright 2025 Mathews Sunny
Licensed under GNU GPL V3 or later. 
