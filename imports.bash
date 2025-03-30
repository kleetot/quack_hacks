#!/bin/bash

# Update package list
sudo apt-get update

# Install espeak-ng
sudo apt-get install -y espeak-ng

# Install Python dependencies
python3 -m pip install --upgrade pip
sudo python3 -m pip install phonemizer requests

echo "Setup complete."
