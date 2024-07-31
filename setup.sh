#!/usr/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3-kms++ python3-libcamera python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg 

pip3 install picamera2 adafruit-circuitpython-neopixel numpy opencv-python argparse gpiozero pillow adafruit-blinka