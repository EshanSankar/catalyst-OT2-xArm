#!/bin/bash

# Exit on error
set -e

echo "Installing Catalyst OT2-Arduino System..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p results
mkdir -p config

# Copy default config files if they don't exist
if [ ! -f "config/default_config.json" ]; then
    echo "Copying default configuration files..."
    cp config.default/default_config.json config/
fi

if [ ! -f "config/logging_config.yaml" ]; then
    cp config.default/logging_config.yaml config/
fi

if [ ! -f "config/parameter_limits.json" ]; then
    cp config.default/parameter_limits.json config/
fi

# Set up udev rules for Arduino (Linux only)
if [ "$(uname)" == "Linux" ]; then
    echo "Setting up udev rules for Arduino..."
    sudo cp scripts/99-arduino.rules /etc/udev/rules.d/
    sudo udevadm control --reload-rules
    sudo udevadm trigger
fi

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

echo "Installation complete!"
echo "Please make sure to:"
echo "1. Configure your OT-2 robot IP in config/default_config.json"
echo "2. Connect your Arduino device"
echo "3. Run 'python scripts/test_connection.py' to verify the setup" 
