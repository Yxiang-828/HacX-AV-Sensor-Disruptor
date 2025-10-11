#!/bin/bash
sudo apt update
sudo apt install python3 python3-pip git
pip3 install -r requirements.txt
pip3 install pyserial  # For mmWave UART
sudo raspi-config nonint do_serial 0  # Enable UART
echo "Setup complete. Reboot and run: python3 src/main.py"