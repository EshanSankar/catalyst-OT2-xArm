#!/usr/bin/env python3

import sys
import os
import json
import logging
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardware.OT_Arduino_Client import Arduino
from hardware.OT2_control import OT2Control

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load configuration from default_config.json."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'config', 'default_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        return {}

def test_arduino_connection(config: Dict[str, Any]) -> bool:
    """
    Test connection to Arduino.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        arduino = Arduino(port=config.get('hardware', {}).get('arduino', {}).get('port'))
        logger.info("Successfully connected to Arduino")
        
        # Test temperature reading
        temp = arduino.read_temperature()
        logger.info(f"Current temperature: {temp}°C")
        
        arduino.close()
        return True
        
    except Exception as e:
        logger.error(f"Arduino connection failed: {str(e)}")
        return False

def test_ot2_connection(config: Dict[str, Any]) -> bool:
    """
    Test connection to OT-2.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        ot2_config = config.get('hardware', {}).get('ot2', {})
        ot2 = OT2Control(strRobotIP=ot2_config.get('ip'))
        
        # Test connection
        if ot2.is_connected():
            logger.info("Successfully connected to OT-2")
            ot2.disconnect()
            return True
        else:
            logger.error("Failed to connect to OT-2")
            return False
            
    except Exception as e:
        logger.error(f"OT-2 connection failed: {str(e)}")
        return False

def main():
    """Main function to test connections."""
    logger.info("Starting connection tests...")
    
    # Load configuration
    config = load_config()
    if not config:
        logger.error("Failed to load configuration")
        sys.exit(1)
    
    # Test Arduino connection
    arduino_success = test_arduino_connection(config)
    
    # Test OT-2 connection
    ot2_success = test_ot2_connection(config)
    
    # Print summary
    print("\nConnection Test Summary:")
    print("------------------------")
    print(f"Arduino Connection: {'✓' if arduino_success else '✗'}")
    print(f"OT-2 Connection: {'✓' if ot2_success else '✗'}")
    
    if not (arduino_success and ot2_success):
        print("\nTroubleshooting Tips:")
        if not arduino_success:
            print("- Check if Arduino is properly connected via USB")
            print("- Verify Arduino port in config/default_config.json")
            print("- Check if you have necessary permissions to access the port")
        if not ot2_success:
            print("- Verify OT-2 IP address in config/default_config.json")
            print("- Ensure OT-2 is powered on and connected to the network")
            print("- Check if you can ping the OT-2 IP address")
        sys.exit(1)
    
    print("\nAll connections successful!")

if __name__ == "__main__":
    main() 
