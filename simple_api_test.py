#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple API test script using only requests library.
This is easier to run on Windows without complex async dependencies.
"""

import json
import logging
import requests
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_api(base_url="http://127.0.0.1:8000"):
    """Test the API endpoints."""
    logger.info(f"Testing API at {base_url}")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            logger.info("✓ Health check passed")
            print(f"Health check response: {response.json()}")
        else:
            logger.error(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Health check failed: {str(e)}")
        return False
    
    # Test 2: Root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            logger.info("✓ Root endpoint passed")
            print(f"API info: {response.json()['name']}")
        else:
            logger.error(f"✗ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Root endpoint failed: {str(e)}")
        return False
    
    # Test 3: Submit experiment
    experiment_data = {
        "uo_type": "CVA",
        "parameters": {
            "start_voltage": "-0.2V",
            "end_voltage": "1.0V",
            "scan_rate": 0.05,
            "cycles": 1,
            "arduino_control": {
                "base0_temp": 25.0,
                "pump0_ml": 0.0,
                "ultrasonic0_ms": 0
            }
        },
        "metadata": {
            "test": True,
            "description": "Simple API test"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/experiments",
            json=experiment_data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            experiment_id = result.get('experiment_id')
            logger.info(f"✓ Experiment submitted: {experiment_id}")
            print(f"Experiment ID: {experiment_id}")
        else:
            logger.error(f"✗ Experiment submission failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"✗ Experiment submission failed: {str(e)}")
        return False
    
    # Test 4: Get experiment status
    if experiment_id:
        try:
            response = requests.get(f"{base_url}/experiments/{experiment_id}", timeout=10)
            if response.status_code == 200:
                result = response.json()
                status = result.get('data', {}).get('status', 'unknown')
                logger.info(f"✓ Experiment status retrieved: {status}")
                print(f"Experiment status: {status}")
            else:
                logger.error(f"✗ Get experiment status failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Get experiment status failed: {str(e)}")
            return False
    
    # Test 5: List experiments
    try:
        response = requests.get(f"{base_url}/experiments", timeout=10)
        if response.status_code == 200:
            result = response.json()
            count = len(result.get('data', {}).get('experiments', []))
            logger.info(f"✓ List experiments passed: {count} experiments found")
            print(f"Total experiments: {count}")
        else:
            logger.error(f"✗ List experiments failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ List experiments failed: {str(e)}")
        return False
    
    logger.info("🎉 All tests passed!")
    return True

def wait_for_server(base_url="http://127.0.0.1:8000", timeout=30):
    """Wait for the server to be available."""
    logger.info(f"Waiting for server at {base_url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Server is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print()
    logger.error(f"Server not available after {timeout} seconds")
    return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple API test")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="API server URL")
    parser.add_argument("--wait", action="store_true", help="Wait for server to be available")
    parser.add_argument("--timeout", type=int, default=30, help="Server wait timeout")
    
    args = parser.parse_args()
    
    if args.wait:
        if not wait_for_server(args.url, args.timeout):
            sys.exit(1)
    
    if test_api(args.url):
        print("\n✅ All API tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some API tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
