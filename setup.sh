#!/bin/bash
sudo apt update
sudo apt install python3 python3-pip git python3-rpi.gpio
pip3 install -r requirements.txt
pip3 install pyserial w1thermsensor
sudo raspi-config nonint do_serial 0  # Enable UART
sudo raspi-config nonint do_onewire 1  # Enable 1-Wire for DS18B20
echo "Setup complete. Reboot and run: python3 src/main.py"