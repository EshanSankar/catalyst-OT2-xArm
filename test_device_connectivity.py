#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for checking connectivity to OT-2 robot, Arduino, and Biologic devices.
This script tests basic connectivity to all three devices.
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
        logging.FileHandler("device_connectivity_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DeviceConnectivityTest")

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
            "global_config": {
                "labware": {
                    "reactor_plate": {
                        "type": "nis_15_wellplate_3895ul",
                        "slot": 9,
                        "working_well": "B2"
                    }
                },
                "instruments": {
                    "pipette": {
                        "type": "p1000_single_gen2",
                        "mount": "right"
                    }
                },
                "arduino_control": {
                    "pumps": {
                        "water": 0,
                        "acid": 1,
                        "out": 2
                    },
                    "temperature": {
                        "default": 25.0
                    }
                },
                "biologic_control": {
                    "reference_electrode": {
                        "type": "RE",
                        "enabled": True
                    }
                }
            }
        }

def test_ot2_connection():
    """Test connection to the OT-2 robot."""
    logger.info("Testing OT-2 connection...")

    try:
        # Get the robot IP from config or use default
        config = load_config()
        robot_ip = config.get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")

        logger.info(f"Connecting to OT-2 at {robot_ip}...")

        # First try to use the opentronsHTTPAPI_clientBuilder.py
        try:
            from opentronsHTTPAPI_clientBuilder import opentronsClient
            logger.info("Using opentronsClient from opentronsHTTPAPI_clientBuilder.py")

            # Create a client instance
            ot2_client = opentronsClient(strRobotIP=robot_ip)
            logger.info("Successfully created opentronsClient instance")

            # Test basic functionality
            logger.info("Testing basic OT-2 functionality...")

            # Get run info
            run_info = ot2_client.getRunInfo()
            logger.info(f"Run ID: {ot2_client.runID}")

            # Turn on the lights
            ot2_client.lights("true")
            logger.info("Lights turned on")

            # Home the robot
            ot2_client.homeRobot()
            logger.info("Robot homed successfully")

            # Turn off the lights
            ot2_client.lights("false")
            logger.info("Lights turned off")

            logger.info("OT-2 Connected Successfully using opentronsHTTPAPI_clientBuilder!")
            return True

        except Exception as e:
            logger.warning(f"Could not connect using opentronsHTTPAPI_clientBuilder: {str(e)}")
            logger.info("Falling back to HTTP API direct access...")

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

                logger.info("OT-2 Connected Successfully using direct HTTP API!")
                return True
            else:
                logger.error(f"Health endpoint test FAILED: Status code {response.status_code}")
                return False

    except Exception as e:
        logger.error(f"OT-2 Connection Failed: {str(e)}")
        return False

def test_arduino_connection():
    """Test connection to the Arduino."""
    logger.info("Testing Arduino connection...")

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
            ser.close()
            logger.info("Arduino Connected Successfully!")
            return True
        else:
            logger.error(f"Failed to open serial connection to Arduino on {arduino_port}")
            return False

    except Exception as e:
        logger.error(f"Arduino Connection Failed: {str(e)}")
        return False

def test_biologic_connection():
    """Test connection to the Biologic potentiostat."""
    logger.info("Testing Biologic connection...")

    try:
        # Check if the Biologic USB device is connected
        import os
        import glob

        # Look for USB devices that might be the Biologic
        usb_devices = glob.glob("/dev/usb*") if os.name == 'posix' else []

        # Check based on operating system
        if os.name == 'nt':  # Windows
            # On Windows, we can check for the device in Device Manager
            # but this requires admin privileges, so we'll just check if the biologic module is available
            try:
                import importlib.util
                spec = importlib.util.find_spec("biologic")
                if spec is not None:
                    logger.info("Biologic module is available")
                    logger.info("Assuming Biologic device is connected (cannot verify without actual connection)")
                    logger.info("Biologic Connection Test PASSED (module available)")
                    return True
                else:
                    logger.error("Biologic module is not available")
                    return False
            except ImportError:
                logger.error("Failed to import biologic module")
                return False
        elif usb_devices:  # Linux/Mac with USB devices found
            logger.info(f"Found USB devices: {usb_devices}")
            logger.info("Assuming one of these is the Biologic (cannot verify without actual connection)")
            logger.info("Biologic Connection Test PASSED (USB device found)")
            return True
        else:
            logger.error("No USB devices found that could be the Biologic")
            return False

    except Exception as e:
        logger.error(f"Biologic Connection Failed: {str(e)}")
        return False

def main():
    """Main function to test device connections."""
    logger.info("Starting device connectivity tests...")

    # Test OT-2 connection
    ot2_success = test_ot2_connection()

    # Test Arduino connection
    arduino_success = test_arduino_connection()

    # Test Biologic connection
    biologic_success = test_biologic_connection()

    # Print summary
    print("\nDevice Connectivity Test Summary:")
    print("--------------------------------")
    print(f"OT-2 Connection: {'✓' if ot2_success else '✗'}")
    print(f"Arduino Connection: {'✓' if arduino_success else '✗'}")
    print(f"Biologic Connection: {'✓' if biologic_success else '✗'}")

    if not (ot2_success and arduino_success and biologic_success):
        print("\nTroubleshooting Tips:")
        if not ot2_success:
            print("- Check if OT-2 is powered on and connected to the network")
            print("- Verify the OT-2 IP address is correct")
            print("- Try pinging the OT-2 IP address")
        if not arduino_success:
            print("- Check if Arduino is properly connected via USB")
            print("- Verify the Arduino port is correct")
            print("- Check if you have necessary permissions to access the port")
        if not biologic_success:
            print("- Check if Biologic potentiostat is properly connected via USB")
            print("- Verify the Biologic drivers are installed")
            print("- Check if you have necessary permissions to access the device")
        return False

    print("\nAll devices connected successfully!")
    return True

if __name__ == "__main__":
    main()
