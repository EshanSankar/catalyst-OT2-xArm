#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OT2 Connectivity Test Script

This script performs a comprehensive test of the OT2 robot connectivity:
1. Ping test to check basic network connectivity
2. Health endpoint test to verify the API is responding
3. Pipettes endpoint test to check attached pipettes
4. Modules endpoint test to check attached modules

Usage:
  python ot2_connectivity_test.py [--ip IP_ADDRESS] [--timeout SECONDS]
"""

import requests
import sys
import logging
import json
import os
import time
import argparse
import subprocess
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OT2ConnectivityTest")

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

def ping_test(ip_address, count=3):
    """
    Test basic network connectivity to the OT2 robot using ping.
    
    Args:
        ip_address (str): The IP address of the OT2 robot
        count (int): Number of ping packets to send
        
    Returns:
        bool: True if ping is successful, False otherwise
    """
    logger.info(f"Performing ping test to {ip_address}...")
    
    # Determine the ping command based on the operating system
    if platform.system().lower() == "windows":
        ping_cmd = ["ping", "-n", str(count), ip_address]
    else:
        ping_cmd = ["ping", "-c", str(count), ip_address]
    
    try:
        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            logger.info("Ping test PASSED")
            return True
        else:
            logger.error("Ping test FAILED")
            logger.error(result.stderr)
            return False
    except Exception as e:
        logger.error(f"Ping test FAILED: {str(e)}")
        return False

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
        if isinstance(modules_info, dict) and 'data' in modules_info:
            modules_data = modules_info.get('data', [])
            if modules_data:
                for module in modules_data:
                    if isinstance(module, dict):
                        print(f"  {module.get('displayName', 'Unknown Module')}:")
                        print(f"    Model: {module.get('model', 'N/A')}")
                        print(f"    Serial: {module.get('serial', 'N/A')}")
                        print(f"    Status: {module.get('status', 'N/A')}")
                    else:
                        print(f"  Module: {module}")
            else:
                print("  No modules attached")
        else:
            print("  Invalid module data format")
    
    print("\n" + "="*50)

def display_troubleshooting_tips(ping_success, health_success, pipettes_success, modules_success):
    """Display troubleshooting tips based on test results."""
    print("\nTROUBLESHOOTING TIPS:")
    
    if not ping_success:
        print("  Network Connectivity Issues:")
        print("  - Check if the OT2 robot is powered on")
        print("  - Verify the IP address is correct")
        print("  - Ensure your computer is on the same network as the OT2")
        print("  - Check network cables or Wi-Fi connection")
    
    if ping_success and not health_success:
        print("  API Service Issues:")
        print("  - The OT2 robot is reachable but the API service may not be running")
        print("  - Try restarting the OT2 robot")
        print("  - Check if the robot's software needs to be updated")
    
    if health_success and not (pipettes_success and modules_success):
        print("  API Endpoint Issues:")
        print("  - The OT2 API is running but some endpoints are not responding")
        print("  - This may indicate a software issue on the robot")
        print("  - Try restarting the robot's API service")
    
    print("\nFor more help, contact Opentrons support or refer to the documentation.")

def main():
    """Main function to test OT2 connectivity."""
    parser = argparse.ArgumentParser(description="Test OT2 robot connectivity")
    parser.add_argument("--ip", help="IP address of the OT2 robot")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout for API requests in seconds")
    parser.add_argument("--skip-ping", action="store_true", help="Skip the ping test")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    ip_address = args.ip or config.get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
    
    logger.info(f"Starting OT2 connectivity test for robot at {ip_address}")
    
    # Track test results
    ping_success = True
    health_success = False
    pipettes_success = False
    modules_success = False
    
    # Perform ping test
    if not args.skip_ping:
        ping_success = ping_test(ip_address)
    
    # Only proceed with API tests if ping is successful or skipped
    if ping_success or args.skip_ping:
        # Test API endpoints
        health_info = test_health_endpoint(ip_address, args.timeout)
        health_success = health_info is not None
        
        pipettes_info = test_pipettes_endpoint(ip_address, args.timeout)
        pipettes_success = pipettes_info is not None
        
        modules_info = test_modules_endpoint(ip_address, args.timeout)
        modules_success = modules_info is not None
        
        # Display robot information if health check passed
        if health_success:
            display_robot_info(health_info, pipettes_info, modules_info)
    
    # Determine overall test result
    overall_success = ping_success and health_success
    
    # Display summary
    print("\nCONNECTIVITY TEST SUMMARY:")
    print(f"  Ping Test: {'PASSED' if ping_success else 'FAILED'}")
    print(f"  Health API: {'PASSED' if health_success else 'FAILED'}")
    print(f"  Pipettes API: {'PASSED' if pipettes_success else 'FAILED'}")
    print(f"  Modules API: {'PASSED' if modules_success else 'FAILED'}")
    print(f"\nOVERALL RESULT: {'PASSED' if overall_success else 'FAILED'}")
    
    # Display troubleshooting tips if any test failed
    if not (ping_success and health_success and pipettes_success and modules_success):
        display_troubleshooting_tips(ping_success, health_success, pipettes_success, modules_success)
    
    # Exit with appropriate status code
    if overall_success:
        logger.info("OT2 connectivity test PASSED")
        sys.exit(0)
    else:
        logger.error("OT2 connectivity test FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
