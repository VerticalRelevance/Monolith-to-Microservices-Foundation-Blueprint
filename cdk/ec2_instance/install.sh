#!/usr/bin/env bash

sudo apt update
sudo apt install -y python3-pip

pip3 install -r requirements.txt


nohup python3 -m flask --app app run --host=0.0.0.0 &

