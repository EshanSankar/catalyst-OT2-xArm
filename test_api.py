#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for the Catalyst OT-2 Experiment API.

This script tests the basic functionality of the API server to ensure
it can receive and process experiment configurations correctly.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any
import aiohttp
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APITester:
    """Test class for the Catalyst OT-2 Experiment API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✓" if success else "✗"
        logger.info(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    async def test_health_check(self) -> bool:
        """Test the health check endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result("Health Check", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_test_result("Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Health Check", False, f"Error: {str(e)}")
            return False
    
    async def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result("Root Endpoint", True, f"API: {data.get('name')}")
                    return True
                else:
                    self.log_test_result("Root Endpoint", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Root Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_submit_experiment(self) -> str:
        """Test submitting a single experiment."""
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
                "description": "API test experiment"
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/experiments",
                json=experiment_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    experiment_id = data.get('experiment_id')
                    self.log_test_result("Submit Experiment", True, f"ID: {experiment_id}")
                    return experiment_id
                else:
                    error_text = await response.text()
                    self.log_test_result("Submit Experiment", False, f"HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test_result("Submit Experiment", False, f"Error: {str(e)}")
            return None
    
    async def test_get_experiment_status(self, experiment_id: str) -> bool:
        """Test getting experiment status."""
        if not experiment_id:
            self.log_test_result("Get Experiment Status", False, "No experiment ID provided")
            return False
        
        try:
            async with self.session.get(
                f"{self.base_url}/experiments/{experiment_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('data', {}).get('status', 'unknown')
                    self.log_test_result("Get Experiment Status", True, f"Status: {status}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test_result("Get Experiment Status", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test_result("Get Experiment Status", False, f"Error: {str(e)}")
            return False
    
    async def test_list_experiments(self) -> bool:
        """Test listing all experiments."""
        try:
            async with self.session.get(f"{self.base_url}/experiments") as response:
                if response.status == 200:
                    data = await response.json()
                    experiments = data.get('data', {}).get('experiments', [])
                    count = len(experiments)
                    self.log_test_result("List Experiments", True, f"Found {count} experiments")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test_result("List Experiments", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test_result("List Experiments", False, f"Error: {str(e)}")
            return False
    
    async def test_batch_experiments(self) -> bool:
        """Test submitting batch experiments."""
        experiments = [
            {
                "uo_type": "CVA",
                "parameters": {
                    "start_voltage": "-0.1V",
                    "end_voltage": "0.5V",
                    "scan_rate": 0.1,
                    "cycles": 1
                },
                "metadata": {"batch_test": True, "experiment": 1}
            },
            {
                "uo_type": "OCV",
                "parameters": {
                    "duration": 10,
                    "sampling_rate": 1.0
                },
                "metadata": {"batch_test": True, "experiment": 2}
            }
        ]
        
        try:
            async with self.session.post(
                f"{self.base_url}/experiments/batch",
                json=experiments
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    experiment_ids = data.get('data', {}).get('experiment_ids', [])
                    count = len(experiment_ids)
                    self.log_test_result("Batch Experiments", True, f"Submitted {count} experiments")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test_result("Batch Experiments", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test_result("Batch Experiments", False, f"Error: {str(e)}")
            return False
    
    async def test_invalid_experiment(self) -> bool:
        """Test submitting an invalid experiment."""
        invalid_data = {
            "uo_type": "INVALID_TYPE",
            "parameters": {}
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/experiments",
                json=invalid_data
            ) as response:
                if response.status == 400 or response.status == 500:
                    self.log_test_result("Invalid Experiment", True, "Correctly rejected invalid data")
                    return True
                else:
                    self.log_test_result("Invalid Experiment", False, f"Unexpected status: {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Invalid Experiment", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests."""
        logger.info("Starting API tests...")
        
        # Basic connectivity tests
        await self.test_health_check()
        await self.test_root_endpoint()
        
        # Experiment submission tests
        experiment_id = await self.test_submit_experiment()
        
        # Status and listing tests
        await self.test_get_experiment_status(experiment_id)
        await self.test_list_experiments()
        
        # Batch and error handling tests
        await self.test_batch_experiments()
        await self.test_invalid_experiment()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"\nTest Summary:")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\nFailed tests:")
            for result in self.test_results:
                if not result['success']:
                    logger.info(f"  - {result['test']}: {result['message']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": self.test_results
        }

async def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for the server to be available."""
    logger.info(f"Waiting for server at {url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health") as response:
                    if response.status == 200:
                        logger.info("Server is ready!")
                        return True
        except:
            pass
        
        await asyncio.sleep(1)
    
    logger.error(f"Server not available after {timeout} seconds")
    return False

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the Catalyst OT-2 Experiment API")
    parser.add_argument("--url", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--wait", action="store_true", help="Wait for server to be available")
    parser.add_argument("--timeout", type=int, default=30, help="Server wait timeout in seconds")
    args = parser.parse_args()
    
    # Wait for server if requested
    if args.wait:
        if not await wait_for_server(args.url, args.timeout):
            sys.exit(1)
    
    # Run tests
    async with APITester(args.url) as tester:
        results = await tester.run_all_tests()
        
        # Exit with error code if tests failed
        if results['failed'] > 0:
            sys.exit(1)
        else:
            logger.info("All tests passed! 🎉")
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
