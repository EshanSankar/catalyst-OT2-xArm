#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for checking functionality of OT-2 robot and Arduino.
This script tests basic functionality of both devices.
"""

import sys
import os
import logging
import json
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("device_functionality_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DeviceFunctionalityTest")

def load_config():
    """Load configuration from default_config.json."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'config', 'default_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        return {
            "hardware": {
                "arduino": {
                    "port": "COM3",
                    "baudrate": 9600,
                    "timeout": 1.0
                },
                "ot2": {
                    "ip": "100.67.89.154",
                    "port": 31950
                }
            }
        }

def test_ot2_api_endpoints():
    """Test the OT-2 robot's API endpoints."""
    logger.info("Testing OT-2 API endpoints...")
    
    try:
        # Get the robot IP from config or use default
        config = load_config()
        robot_ip = config.get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
        
        logger.info(f"Connecting to OT-2 at {robot_ip}...")
        
        # Test if the OT-2 is reachable by sending a GET request to its health endpoint
        import requests
        health_endpoint = f"http://{robot_ip}:31950/health"
        headers = {"opentrons-version": "3"}
        
        logger.info(f"Testing health endpoint at {health_endpoint}...")
        response = requests.get(health_endpoint, headers=headers, timeout=5)
        
        if response.status_code == 200:
            health_info = response.json()
            logger.info("Health endpoint test PASSED")
            logger.info(f"Robot Name: {health_info.get('name', 'N/A')}")
            logger.info(f"Robot Model: {health_info.get('robot_model', 'N/A')}")
            logger.info(f"Serial Number: {health_info.get('robot_serial', 'N/A')}")
            logger.info(f"API Version: {health_info.get('api_version', 'N/A')}")
            logger.info(f"Firmware Version: {health_info.get('fw_version', 'N/A')}")
            logger.info(f"System Version: {health_info.get('system_version', 'N/A')}")
            
            # Test pipettes endpoint
            pipettes_endpoint = f"http://{robot_ip}:31950/pipettes"
            logger.info(f"Testing pipettes endpoint at {pipettes_endpoint}...")
            response = requests.get(pipettes_endpoint, headers=headers, timeout=5)
            
            if response.status_code == 200:
                pipettes_info = response.json()
                logger.info("Pipettes endpoint test PASSED")
                
                left = pipettes_info.get('left', {})
                right = pipettes_info.get('right', {})
                
                if left:
                    logger.info(f"Left Mount: {left.get('name', 'N/A')}")
                else:
                    logger.info("Left Mount: No pipette attached")
                
                if right:
                    logger.info(f"Right Mount: {right.get('name', 'N/A')}")
                else:
                    logger.info("Right Mount: No pipette attached")
            
            # Test modules endpoint
            modules_endpoint = f"http://{robot_ip}:31950/modules"
            logger.info(f"Testing modules endpoint at {modules_endpoint}...")
            response = requests.get(modules_endpoint, headers=headers, timeout=5)
            
            if response.status_code == 200:
                modules_info = response.json()
                logger.info("Modules endpoint test PASSED")
                
                if isinstance(modules_info, dict) and 'data' in modules_info:
                    modules_data = modules_info.get('data', [])
                    if modules_data:
                        logger.info("Attached modules:")
                        for module in modules_data:
                            logger.info(f"  {module.get('displayName', 'Unknown Module')}")
                    else:
                        logger.info("No modules attached")
                else:
                    logger.info(f"Unexpected modules data format: {modules_info}")
            
            logger.info("OT-2 API endpoints test PASSED")
            return True
        else:
            logger.error(f"Health endpoint test FAILED: Status code {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"OT-2 API endpoints test FAILED: {str(e)}")
        return False

def test_arduino_functionality():
    """Test the Arduino's functionality."""
    logger.info("Testing Arduino functionality...")
    
    try:
        # List available serial ports
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        logger.info("Available serial ports:")
        for p in ports:
            logger.info(f"{p}")
        
        # Look for Arduino ports
        arduino_ports = [p.device for p in ports if "CH340" in p.description or "Arduino" in p.description]
        
        if not arduino_ports:
            logger.error("No Arduino found")
            return False
        
        if len(arduino_ports) > 1:
            logger.warning("Multiple Arduinos found - using the first")
        
        arduino_port = arduino_ports[0]
        logger.info(f"Arduino found on port: {arduino_port}")
        
        # Try to open the serial port to test connectivity
        import serial
        ser = serial.Serial(port=arduino_port, baudrate=115200, timeout=3)
        
        if ser.is_open:
            logger.info(f"Successfully opened serial connection to Arduino on {arduino_port}")
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Send a simple command to test communication
            logger.info("Sending test command to Arduino...")
            ser.write(b"get_base_temp 0\n")
            
            # Read the response
            time.sleep(1)
            response = ser.readline().decode().strip()
            logger.info(f"Arduino response: {response}")
            
            # Close the connection
            ser.close()
            logger.info("Arduino functionality test PASSED")
            return True
        else:
            logger.error(f"Failed to open serial connection to Arduino on {arduino_port}")
            return False
        
    except Exception as e:
        logger.error(f"Arduino functionality test FAILED: {str(e)}")
        return False

def main():
    """Main function to test device functionality."""
    logger.info("Starting device functionality tests...")
    
    # Test OT-2 API endpoints
    ot2_api_success = test_ot2_api_endpoints()
    
    # Test Arduino functionality
    arduino_functionality_success = test_arduino_functionality()
    
    # Print summary
    print("\nDevice Functionality Test Summary:")
    print("----------------------------------")
    print(f"OT-2 API Endpoints: {'✓' if ot2_api_success else '✗'}")
    print(f"Arduino Functionality: {'✓' if arduino_functionality_success else '✗'}")
    
    if not (ot2_api_success and arduino_functionality_success):
        print("\nTroubleshooting Tips:")
        if not ot2_api_success:
            print("- Check if OT-2 is powered on and connected to the network")
            print("- Verify the OT-2 IP address is correct")
            print("- Try pinging the OT-2 IP address")
        if not arduino_functionality_success:
            print("- Check if Arduino is properly connected via USB")
            print("- Verify the Arduino port is correct")
            print("- Check if you have necessary permissions to access the port")
            print("- Verify the Arduino firmware is correctly installed")
        return False
    
    print("\nAll device functionality tests PASSED!")
    return True

if __name__ == "__main__":
    main()
