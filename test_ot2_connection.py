#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to check if the OT2 robot is reachable.
This script sends a simple GET request to the OT2's API endpoint
to verify connectivity before running more complex operations.
"""

import requests
import argparse
import sys
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OT2ConnectionTest")

def test_ot2_connection(ip_address, max_retries=3, retry_delay=2):
    """
    Test if the OT2 robot is reachable by sending a GET request to its API endpoint.
    
    Args:
        ip_address (str): The IP address of the OT2 robot
        max_retries (int): Maximum number of connection attempts
        retry_delay (int): Delay in seconds between retries
        
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
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    logger.error(f"Failed to connect to OT2 after {max_retries} attempts")
    return False

def test_opentrons_client(ip_address):
    """
    Test if the OT2 robot is reachable using the opentronsClient class.
    
    Args:
        ip_address (str): The IP address of the OT2 robot
        
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Import the opentronsClient class
        from opentrons import opentronsClient
        
        logger.info(f"Testing connection using opentronsClient at {ip_address}...")
        
        # Initialize the client
        client = opentronsClient(strRobotIP=ip_address)
        
        # If we get here without exceptions, the connection was successful
        logger.info(f"Successfully initialized opentronsClient with OT2 at {ip_address}")
        logger.info(f"Run ID: {client.runID}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect using opentronsClient: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test connection to OT2 robot")
    parser.add_argument("--ip", default="100.67.89.154", help="IP address of the OT2 robot")
    parser.add_argument("--use-client", action="store_true", help="Use opentronsClient for testing")
    parser.add_argument("--retries", type=int, default=3, help="Number of connection attempts")
    args = parser.parse_args()
    
    logger.info("Starting OT2 connection test")
    
    if args.use_client:
        success = test_opentrons_client(args.ip)
    else:
        success = test_ot2_connection(args.ip, args.retries)
    
    if success:
        logger.info("Connection test PASSED")
        sys.exit(0)
    else:
        logger.error("Connection test FAILED")
        sys.exit(1)
