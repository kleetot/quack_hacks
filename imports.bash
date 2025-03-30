#!/bin/bash

# Update package list
sudo apt-get update
sudo apt-get install pip

# Install espeak
sudo apt-get install -y espeak

# Install Python dependencies
python3 -m pip install --upgrade pip
sudo python3 -m pip install flask phonemizer requests

echo "Setup complete."
