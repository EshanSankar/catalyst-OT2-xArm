"""
Test script for Catalyst OT2-Arduino System device control.
This script tests the basic functionality of the OT-2 robot and Arduino control.
"""

import sys
import time
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("device_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("DeviceTest")

def test_arduino_connection():
    """Test Arduino connection and basic functionality."""
    try:
        logger.info("Testing Arduino connection...")
        
        # Import Arduino client
        try:
            from OT_Arduino_Client import ArduinoClient
            logger.info("Successfully imported ArduinoClient")
        except ImportError as e:
            logger.error(f"Failed to import ArduinoClient: {e}")
            return False
        
        # Try to connect to Arduino
        try:
            # Try different common COM ports
            ports = ["COM3", "COM4", "COM5", "COM6"]
            arduino = None
            
            for port in ports:
                try:
                    logger.info(f"Trying to connect to Arduino on {port}")
                    arduino = ArduinoClient(port=port)
                    logger.info(f"Successfully connected to Arduino on {port}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to connect on {port}: {e}")
            
            if arduino is None:
                logger.error("Could not connect to Arduino on any port")
                return False
            
            # Test basic Arduino functions
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
            
        except Exception as e:
            logger.error(f"Arduino test failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in Arduino test: {e}")
        return False

def test_ot2_connection():
    """Test OT-2 connection and basic functionality."""
    try:
        logger.info("Testing OT-2 connection...")
        
        # Import OT-2 client
        try:
            from opentrons import OT2Control
            logger.info("Successfully imported OT2Control")
        except ImportError as e:
            logger.error(f"Failed to import OT2Control: {e}")
            return False
        
        # Try to connect to OT-2
        try:
            # Try to get IP from config or use default
            ip = "100.67.89.154"  # Default from API reference
            logger.info(f"Trying to connect to OT-2 at {ip}")
            
            ot2 = OT2Control(ip=ip)
            connected = ot2.connect()
            
            if not connected:
                logger.error("Failed to connect to OT-2")
                return False
                
            logger.info("Successfully connected to OT-2")
            
            # Test basic OT-2 functions
            logger.info("Testing OT-2 home function...")
            ot2.home()
            
            # Disconnect
            ot2.disconnect()
            logger.info("OT-2 test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"OT-2 test failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in OT-2 test: {e}")
        return False

def main():
    """Run all device tests."""
    logger.info("Starting device control tests...")
    
    # Test Arduino
    arduino_result = test_arduino_connection()
    logger.info(f"Arduino test {'PASSED' if arduino_result else 'FAILED'}")
    
    # Test OT-2
    ot2_result = test_ot2_connection()
    logger.info(f"OT-2 test {'PASSED' if ot2_result else 'FAILED'}")
    
    # Overall result
    if arduino_result and ot2_result:
        logger.info("All device tests PASSED")
        return 0
    else:
        logger.error("Some device tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
