#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script to check if the OT2 robot is reachable.
This script sends a GET request to the OT2's health endpoint.
"""

import requests
import sys
import logging
import json
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SimpleOT2Test")

def load_config():
    """Load configuration from default_config.json."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'config', 'default_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        return {"hardware": {"ot2": {"ip": "100.67.89.154"}}}

def test_ot2_connection(ip_address, max_retries=3):
    """
    Test if the OT2 robot is reachable by sending a GET request to its health endpoint.
    
    Args:
        ip_address (str): The IP address of the OT2 robot
        max_retries (int): Maximum number of connection attempts
        
    Returns:
        bool: True if connection is successful, False otherwise
    """
    base_url = f"http://{ip_address}:31950"
    health_endpoint = f"{base_url}/health"
    headers = {"opentrons-version": "3"}
    
    logger.info(f"Testing connection to OT2 at {ip_address}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connection attempt {attempt}/{max_retries}")
            response = requests.get(health_endpoint, headers=headers, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Connection successful! OT2 is reachable at {ip_address}")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.warning(f"Received status code {response.status_code}")
                logger.warning(f"Response: {response.text}")
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error. OT2 not reachable at {ip_address}")
        except requests.exceptions.Timeout:
            logger.warning(f"Connection timed out. OT2 not responding at {ip_address}")
        except Exception as e:
            logger.warning(f"Unexpected error: {str(e)}")
        
        if attempt < max_retries:
            logger.info(f"Retrying in 2 seconds...")
            time.sleep(2)
    
    logger.error(f"Failed to connect to OT2 after {max_retries} attempts")
    return False

def main():
    """Main function to test OT2 connection."""
    # Load configuration
    config = load_config()
    ip_address = config.get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
    
    logger.info("Starting OT2 connection test")
    success = test_ot2_connection(ip_address)
    
    if success:
        logger.info("Connection test PASSED")
        sys.exit(0)
    else:
        logger.error("Connection test FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
