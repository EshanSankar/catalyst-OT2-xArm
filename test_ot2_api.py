#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for checking the OT2 robot's API endpoints.
This script sends HTTP requests to the OT2 robot's API endpoints.
"""

import sys
import os
import logging
import json
import time
import argparse
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("APITest")

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

def test_health_endpoint(ip_address, timeout=5):
    """Test the health endpoint of the OT2 robot."""
    base_url = f"http://{ip_address}:31950"
    health_endpoint = f"{base_url}/health"
    headers = {"opentrons-version": "3"}
    
    logger.info(f"Testing health endpoint at {health_endpoint}...")
    
    try:
        response = requests.get(health_endpoint, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            logger.info("Health endpoint test PASSED")
            return response.json()
        else:
            logger.error(f"Health endpoint test FAILED: Status code {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Health endpoint test FAILED: {str(e)}")
        return None

def test_pipettes_endpoint(ip_address, timeout=5):
    """Test the pipettes endpoint of the OT2 robot."""
    base_url = f"http://{ip_address}:31950"
    pipettes_endpoint = f"{base_url}/pipettes"
    headers = {"opentrons-version": "3"}
    
    logger.info(f"Testing pipettes endpoint at {pipettes_endpoint}...")
    
    try:
        response = requests.get(pipettes_endpoint, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            logger.info("Pipettes endpoint test PASSED")
            return response.json()
        else:
            logger.error(f"Pipettes endpoint test FAILED: Status code {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Pipettes endpoint test FAILED: {str(e)}")
        return None

def test_modules_endpoint(ip_address, timeout=5):
    """Test the modules endpoint of the OT2 robot."""
    base_url = f"http://{ip_address}:31950"
    modules_endpoint = f"{base_url}/modules"
    headers = {"opentrons-version": "3"}
    
    logger.info(f"Testing modules endpoint at {modules_endpoint}...")
    
    try:
        response = requests.get(modules_endpoint, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            logger.info("Modules endpoint test PASSED")
            return response.json()
        else:
            logger.error(f"Modules endpoint test FAILED: Status code {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Modules endpoint test FAILED: {str(e)}")
        return None

def display_robot_info(health_info, pipettes_info, modules_info):
    """Display detailed information about the OT2 robot."""
    print("\n" + "="*50)
    print("OT2 ROBOT INFORMATION")
    print("="*50)
    
    if health_info:
        print("\nBASIC INFORMATION:")
        print(f"  Robot Name: {health_info.get('name', 'N/A')}")
        print(f"  Robot Model: {health_info.get('robot_model', 'N/A')}")
        print(f"  Serial Number: {health_info.get('robot_serial', 'N/A')}")
        print(f"  API Version: {health_info.get('api_version', 'N/A')}")
        print(f"  Firmware Version: {health_info.get('fw_version', 'N/A')}")
        print(f"  System Version: {health_info.get('system_version', 'N/A')}")
    
    if pipettes_info:
        print("\nPIPETTES:")
        left = pipettes_info.get('left', {})
        right = pipettes_info.get('right', {})
        
        if left:
            print("  Left Mount:")
            print(f"    Model: {left.get('model', 'N/A')}")
            print(f"    Name: {left.get('name', 'N/A')}")
            print(f"    ID: {left.get('id', 'N/A')}")
        else:
            print("  Left Mount: No pipette attached")
        
        if right:
            print("  Right Mount:")
            print(f"    Model: {right.get('model', 'N/A')}")
            print(f"    Name: {right.get('name', 'N/A')}")
            print(f"    ID: {right.get('id', 'N/A')}")
        else:
            print("  Right Mount: No pipette attached")
    
    if modules_info:
        print("\nATTACHED MODULES:")
        if isinstance(modules_info, list) and modules_info:
            for module in modules_info:
                if isinstance(module, dict):
                    print(f"  {module.get('displayName', 'Unknown Module')}:")
                    print(f"    Model: {module.get('model', 'N/A')}")
                    print(f"    Serial: {module.get('serial', 'N/A')}")
                    print(f"    Status: {module.get('status', 'N/A')}")
                else:
                    print(f"  Module: {module}")
        else:
            print("  No modules attached or invalid module data")
            print(f"  Raw data: {modules_info}")
    
    print("\n" + "="*50)

def main():
    """Main function to test OT2 API endpoints."""
    parser = argparse.ArgumentParser(description="Test OT2 robot API endpoints")
    parser.add_argument("--ip", help="IP address of the OT2 robot")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout for API requests in seconds")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Get OT-2 IP address from config or command line
    ip_address = args.ip or config.get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
    
    logger.info(f"Starting OT2 API endpoint tests for robot at {ip_address}...")
    
    # Test API endpoints
    health_info = test_health_endpoint(ip_address, args.timeout)
    pipettes_info = test_pipettes_endpoint(ip_address, args.timeout)
    modules_info = test_modules_endpoint(ip_address, args.timeout)
    
    # Display robot information if health check passed
    if health_info:
        display_robot_info(health_info, pipettes_info, modules_info)
    
    # Determine overall test result
    overall_success = health_info is not None
    
    # Print summary
    print("\nAPI TEST SUMMARY:")
    print(f"  Health API: {'PASSED' if health_info else 'FAILED'}")
    print(f"  Pipettes API: {'PASSED' if pipettes_info else 'FAILED'}")
    print(f"  Modules API: {'PASSED' if modules_info else 'FAILED'}")
    print(f"\nOVERALL RESULT: {'PASSED' if overall_success else 'FAILED'}")
    
    # Exit with appropriate status code
    if overall_success:
        logger.info("OT2 API tests PASSED")
        sys.exit(0)
    else:
        logger.error("OT2 API tests FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
