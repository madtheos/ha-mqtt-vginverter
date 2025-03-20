This script reads the VGInverter/SolSmart 1450 (possibly others) over Bluetooth 
and sends the data to Home Assistant over MQTT. 

To install on a Raspberry Pi/Pi Zero W:

1. Install dependencies: 
   python3
   python3-bleak
   python3-paho-mqtt

2. Clone repo. 

3. Edit the example files with your data.

4. Copy the service file to something like /etc/systemd/system/vginverter.service
   
5. Create the service:
   sudo systemctl daemon-reload
   sudo systemctl enable --now vginverter.service


