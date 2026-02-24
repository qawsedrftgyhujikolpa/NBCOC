#!/bin/bash

# NVIDIA API Proxy Setup Script for WSL2 Ubuntu

echo "Setting up NVIDIA API Proxy..."

# Check for python3-venv
if ! dpkg -l | grep -q python3-venv; then
    echo "python3-venv is required. Please install it with: sudo apt update && sudo apt install python3-venv"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo "To start the proxy:"
echo "1. Edit config.yaml and add your NVIDIA API Key."
echo "2. Run: source venv/bin/activate && python3 main.py"
echo ""
echo "The proxy will be available at http://localhost:8000/v1"
