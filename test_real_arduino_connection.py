#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Real Arduino Connection

This script tests the connection to a real Arduino using the ot2-arduino.py file.
It performs basic operations to verify the connection is working properly.
"""

import sys
import logging
import argparse
import time
import importlib.util
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("real_arduino_connection_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("RealArduinoConnectionTest")

def import_arduino_class():
    """Import the Arduino class from ot2-arduino.py or ot2_arduino.py."""
    try:
        # First try to import from ot2_arduino.py
        LOGGER.info("Trying to import Arduino from ot2_arduino.py...")
        from ot2_arduino import Arduino
        LOGGER.info("Successfully imported Arduino from ot2_arduino.py")
        return Arduino
    except ImportError:
        try:
            # Then try to import from ot2-arduino.py using importlib
            LOGGER.info("Trying to import Arduino from ot2-arduino.py...")
            spec = importlib.util.spec_from_file_location("Arduino", "ot2-arduino.py")
            arduino_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(arduino_module)
            Arduino = arduino_module.Arduino
            LOGGER.info("Successfully imported Arduino from ot2-arduino.py")
            return Arduino
        except Exception as e:
            LOGGER.error(f"Failed to import Arduino: {str(e)}")
            raise ImportError("Could not import Arduino class from either ot2_arduino.py or ot2-arduino.py")

def list_serial_ports():
    """List available serial ports."""
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        LOGGER.info("Available serial ports:")
        for p in ports:
            LOGGER.info(f"  {p}")
        return ports
    except Exception as e:
        LOGGER.error(f"Failed to list serial ports: {str(e)}")
        return []

def find_arduino_port():
    """Find the Arduino port."""
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        # Look for Arduino ports
        arduino_ports = [p.device for p in ports if "CH340" in p.description or "Arduino" in p.description]
        
        if not arduino_ports:
            LOGGER.warning("No Arduino found in port descriptions")
            # If no Arduino is found in the descriptions, try to use COM3 as a fallback
            if os.name == 'nt':  # Windows
                LOGGER.info("Trying COM3 as a fallback...")
                return "COM3"
            else:  # Linux/Mac
                LOGGER.info("Trying /dev/ttyUSB0 as a fallback...")
                return "/dev/ttyUSB0"
        
        if len(arduino_ports) > 1:
            LOGGER.warning(f"Multiple Arduinos found - using the first one: {arduino_ports[0]}")
        
        LOGGER.info(f"Arduino found on port: {arduino_ports[0]}")
        return arduino_ports[0]
    except Exception as e:
        LOGGER.error(f"Failed to find Arduino port: {str(e)}")
        # Return a default port as fallback
        if os.name == 'nt':  # Windows
            return "COM3"
        else:  # Linux/Mac
            return "/dev/ttyUSB0"

def test_real_arduino_connection(port=None):
    """Test connection to a real Arduino."""
    try:
        # List available serial ports
        list_serial_ports()
        
        # Find Arduino port if not specified
        if port is None:
            port = find_arduino_port()
        
        # Import the Arduino class
        Arduino = import_arduino_class()
        
        # Create an Arduino instance
        LOGGER.info(f"Connecting to Arduino on port {port}...")
        arduino = Arduino(arduinoPort=port)
        LOGGER.info("Successfully connected to Arduino")
        
        # Test temperature control
        LOGGER.info("Testing temperature control...")
        
        # Get current temperature
        try:
            temp = arduino.getTemp(0)
            LOGGER.info(f"Current temperature of base 0: {temp}°C")
        except Exception as e:
            LOGGER.warning(f"Could not get temperature: {str(e)}")
        
        # Set temperature
        try:
            target_temp = 25.0
            LOGGER.info(f"Setting temperature of base 0 to {target_temp}°C...")
            arduino.setTemp(0, target_temp)
            LOGGER.info(f"Temperature set successfully")
            
            # Wait for a moment and get the temperature again
            time.sleep(2)
            temp = arduino.getTemp(0)
            LOGGER.info(f"Temperature after setting: {temp}°C")
        except Exception as e:
            LOGGER.warning(f"Could not set temperature: {str(e)}")
        
        # Test pump control
        LOGGER.info("Testing pump control...")
        
        try:
            # Dispense a small amount of water
            volume = 0.5  # 0.5 ml
            LOGGER.info(f"Dispensing {volume} ml from pump 0...")
            arduino.dispense_ml(0, volume)
            LOGGER.info("Dispensing completed")
        except Exception as e:
            LOGGER.warning(f"Could not dispense from pump: {str(e)}")
        
        # Test ultrasonic control
        LOGGER.info("Testing ultrasonic control...")
        
        try:
            # Run ultrasonic for a short time
            duration = 1000  # 1 second
            LOGGER.info(f"Running ultrasonic for {duration} ms...")
            arduino.setUltrasonicOnTimer(0, duration)
            LOGGER.info("Ultrasonic completed")
        except Exception as e:
            LOGGER.warning(f"Could not run ultrasonic: {str(e)}")
        
        LOGGER.info("Arduino connection test completed successfully")
        return True
    except Exception as e:
        LOGGER.error(f"Arduino connection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test connection to a real Arduino")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)")
    args = parser.parse_args()
    
    LOGGER.info(f"Starting Arduino connection test" + (f" with port: {args.port}" if args.port else ""))
    
    success = test_real_arduino_connection(args.port)
    
    if success:
        print("\nArduino Connection Test: ✓")
        print("Connection to the real Arduino was successful!")
    else:
        print("\nArduino Connection Test: ✗")
        print("Connection to the real Arduino failed.")
        print("\nTroubleshooting Tips:")
        print("- Check if the Arduino is properly connected via USB")
        print("- Verify the Arduino port is correct")
        print("- Make sure the Arduino has the correct firmware installed")
        print("- Check if you have necessary permissions to access the port")
        print("- Check the log file for detailed error messages")
    
    return success

if __name__ == "__main__":
    main()
