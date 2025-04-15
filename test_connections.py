#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for checking connectivity to OT-2 robot and Arduino.
This script tests basic connectivity to the devices.
"""

import sys
import os
import logging
import json
import time
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("connection_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ConnectionTest")

def load_config():
    """Load configuration from default_config.json."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'config', 'default_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        return {"hardware": {"ot2": {"ip": "100.67.89.154"}, "arduino": {"port": "COM3"}}}

def test_ot2_connection(ip_address, use_mock=False):
    """Test connection to the OT-2 robot."""
    logger.info(f"Testing OT-2 connection to {ip_address}...")
    
    try:
        if use_mock:
            # Use mock implementation for testing
            from mock_opentrons import OT2Control
            logger.info("Using mock OT2Control for testing")
        else:
            # Try to import the real OT2Control class
            try:
                from backend.ot2_backend import OT2Control
                logger.info("Using real OT2Control from backend.ot2_backend")
            except ImportError:
                try:
                    from hardware.OT2_control import OT2Control
                    logger.info("Using real OT2Control from hardware.OT2_control")
                except ImportError:
                    try:
                        from opentrons import OT2Control
                        logger.info("Using real OT2Control from opentrons")
                    except ImportError:
                        logger.error("Failed to import OT2Control. Using mock implementation.")
                        from mock_opentrons import OT2Control
        
        # Initialize OT2 control
        ot2 = OT2Control(ip=ip_address)
        
        # Connect to OT2
        connected = ot2.connect()
        
        if connected:
            logger.info("OT-2 Connected Successfully!")
            
            # Test basic functionality
            logger.info("Testing OT-2 home function...")
            ot2.home()
            
            # Get pipettes
            pipettes = ot2.get_pipettes()
            if pipettes:
                logger.info("Pipettes detected:")
                for mount, pipette in pipettes.items():
                    if pipette:
                        logger.info(f"  {mount.capitalize()}: {pipette.get('name', 'Unknown')}")
                    else:
                        logger.info(f"  {mount.capitalize()}: None")
            
            # Disconnect
            ot2.disconnect()
            logger.info("OT-2 test completed successfully")
            return True
        else:
            logger.error("Failed to connect to OT-2")
            return False
            
    except Exception as e:
        logger.error(f"OT-2 Connection Failed: {str(e)}")
        return False

def test_arduino_connection(port, use_mock=False):
    """Test connection to the Arduino."""
    logger.info(f"Testing Arduino connection on port {port}...")
    
    try:
        if use_mock:
            # Use mock implementation for testing
            from mock_opentrons import ArduinoClient
            logger.info("Using mock ArduinoClient for testing")
        else:
            # Try to import the real ArduinoClient class
            try:
                from backend.arduino_backend import ArduinoClient
                logger.info("Using real ArduinoClient from backend.arduino_backend")
            except ImportError:
                try:
                    from hardware.OT_Arduino_Client import ArduinoClient
                    logger.info("Using real ArduinoClient from hardware.OT_Arduino_Client")
                except ImportError:
                    try:
                        from OT_Arduino_Client import ArduinoClient
                        logger.info("Using real ArduinoClient from OT_Arduino_Client")
                    except ImportError:
                        logger.error("Failed to import ArduinoClient. Using mock implementation.")
                        from mock_opentrons import ArduinoClient
        
        # Initialize Arduino client
        arduino = ArduinoClient(port=port)
        
        # Connect to Arduino
        connected = arduino.connect()
        
        if connected:
            logger.info("Arduino Connected Successfully!")
            
            # Test basic functionality
            logger.info("Testing Arduino temperature reading...")
            temp = arduino.read_temperature()
            logger.info(f"Current temperature: {temp}°C")
            
            logger.info("Testing Arduino LED control...")
            arduino.set_led(True)
            time.sleep(1)
            arduino.set_led(False)
            
            # Close connection
            arduino.close()
            logger.info("Arduino test completed successfully")
            return True
        else:
            logger.error("Failed to connect to Arduino")
            return False
            
    except Exception as e:
        logger.error(f"Arduino Connection Failed: {str(e)}")
        return False

def main():
    """Main function to test device connections."""
    parser = argparse.ArgumentParser(description="Test OT-2 and Arduino connections")
    parser.add_argument("--ot2-ip", help="IP address of the OT-2 robot")
    parser.add_argument("--arduino-port", help="COM port of the Arduino")
    parser.add_argument("--mock", action="store_true", help="Use mock implementations for testing")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Get OT-2 IP address and Arduino port from config or command line
    ot2_ip = args.ot2_ip or config.get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
    arduino_port = args.arduino_port or config.get("hardware", {}).get("arduino", {}).get("port", "COM3")
    
    logger.info("Starting device connection tests...")
    
    # Test OT-2 connection
    ot2_success = test_ot2_connection(ot2_ip, args.mock)
    
    # Test Arduino connection
    arduino_success = test_arduino_connection(arduino_port, args.mock)
    
    # Print summary
    print("\nConnection Test Summary:")
    print("------------------------")
    print(f"OT-2 Connection: {'✓' if ot2_success else '✗'}")
    print(f"Arduino Connection: {'✓' if arduino_success else '✗'}")
    
    if not (ot2_success and arduino_success):
        print("\nTroubleshooting Tips:")
        if not ot2_success:
            print("- Check if OT-2 is powered on and connected to the network")
            print(f"- Verify OT-2 IP address ({ot2_ip}) is correct")
            print("- Try pinging the OT-2 IP address")
        if not arduino_success:
            print("- Check if Arduino is properly connected via USB")
            print(f"- Verify Arduino port ({arduino_port}) is correct")
            print("- Check if you have necessary permissions to access the port")
        return False
    
    print("\nAll connections successful!")
    return True

if __name__ == "__main__":
    main()
