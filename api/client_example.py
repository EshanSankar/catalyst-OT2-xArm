#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example client for sending experiment configurations to the API server.

This script demonstrates how to send JSON experiment configurations to the
Litestar API server from a remote source.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List
import aiohttp
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExperimentClient:
    """Client for interacting with the Catalyst OT-2 Experiment API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def submit_experiment(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a single experiment."""
        url = f"{self.base_url}/experiments"
        
        async with self.session.post(url, json=experiment_data) as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"Experiment submitted successfully: {result.get('experiment_id')}")
                return result
            else:
                error_text = await response.text()
                logger.error(f"Failed to submit experiment: {response.status} - {error_text}")
                raise Exception(f"API error: {response.status} - {error_text}")
    
    async def submit_batch_experiments(self, experiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit multiple experiments in batch."""
        url = f"{self.base_url}/experiments/batch"
        
        async with self.session.post(url, json=experiments) as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"Batch experiments submitted: {len(result.get('data', {}).get('experiment_ids', []))}")
                return result
            else:
                error_text = await response.text()
                logger.error(f"Failed to submit batch experiments: {response.status} - {error_text}")
                raise Exception(f"API error: {response.status} - {error_text}")
    
    async def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get the status of an experiment."""
        url = f"{self.base_url}/experiments/{experiment_id}"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                logger.error(f"Failed to get experiment status: {response.status} - {error_text}")
                raise Exception(f"API error: {response.status} - {error_text}")
    
    async def list_experiments(self) -> Dict[str, Any]:
        """List all experiments."""
        url = f"{self.base_url}/experiments"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                logger.error(f"Failed to list experiments: {response.status} - {error_text}")
                raise Exception(f"API error: {response.status} - {error_text}")
    
    async def wait_for_experiment_completion(self, experiment_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for an experiment to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_response = await self.get_experiment_status(experiment_id)
            status_data = status_response.get('data', {})
            status = status_data.get('status')
            
            if status in ['completed', 'failed']:
                logger.info(f"Experiment {experiment_id} finished with status: {status}")
                return status_response
            
            logger.info(f"Experiment {experiment_id} status: {status}")
            await asyncio.sleep(5)  # Wait 5 seconds before checking again
        
        raise TimeoutError(f"Experiment {experiment_id} did not complete within {timeout} seconds")

# Example experiment configurations
EXAMPLE_CVA_EXPERIMENT = {
    "uo_type": "CVA",
    "parameters": {
        "start_voltage": "-0.2V",
        "end_voltage": "1.0V",
        "scan_rate": 0.05,
        "cycles": 3,
        "arduino_control": {
            "base0_temp": 25.0,
            "pump0_ml": 0.0,
            "ultrasonic0_ms": 0
        },
        "ot2_actions": [
            {
                "action": "pick_up_tip",
                "labware": "electrode_tip_rack",
                "well": "A1"
            },
            {
                "action": "move_to",
                "labware": "reactor_plate",
                "well": "B2",
                "offset": {"z": -20}
            }
        ]
    },
    "metadata": {
        "researcher": "example_user",
        "project": "catalyst_testing",
        "notes": "Example CVA experiment"
    }
}

EXAMPLE_PEIS_EXPERIMENT = {
    "uo_type": "PEIS",
    "parameters": {
        "frequency_range": [0.1, 100000],
        "amplitude": 0.01,
        "dc_voltage": 0.0,
        "arduino_control": {
            "base0_temp": 30.0,
            "pump0_ml": 1.0,
            "ultrasonic0_ms": 2000
        }
    },
    "metadata": {
        "researcher": "example_user",
        "project": "impedance_study"
    }
}

async def run_single_experiment_example(client: ExperimentClient):
    """Example: Submit and monitor a single experiment."""
    logger.info("=== Single Experiment Example ===")
    
    # Submit experiment
    result = await client.submit_experiment(EXAMPLE_CVA_EXPERIMENT)
    experiment_id = result.get('experiment_id')
    
    # Wait for completion
    final_result = await client.wait_for_experiment_completion(experiment_id)
    logger.info(f"Final result: {json.dumps(final_result, indent=2)}")

async def run_batch_experiment_example(client: ExperimentClient):
    """Example: Submit batch experiments."""
    logger.info("=== Batch Experiment Example ===")
    
    experiments = [EXAMPLE_CVA_EXPERIMENT, EXAMPLE_PEIS_EXPERIMENT]
    
    # Submit batch
    result = await client.submit_batch_experiments(experiments)
    experiment_ids = result.get('data', {}).get('experiment_ids', [])
    
    # Monitor all experiments
    for exp_id in experiment_ids:
        try:
            final_result = await client.wait_for_experiment_completion(exp_id, timeout=60)
            logger.info(f"Experiment {exp_id} completed")
        except TimeoutError:
            logger.warning(f"Experiment {exp_id} timed out")

async def run_status_monitoring_example(client: ExperimentClient):
    """Example: Monitor experiment status."""
    logger.info("=== Status Monitoring Example ===")
    
    # List all experiments
    experiments_list = await client.list_experiments()
    logger.info(f"Total experiments: {len(experiments_list.get('data', {}).get('experiments', []))}")
    
    # Show recent experiments
    for exp in experiments_list.get('data', {}).get('experiments', [])[-5:]:
        logger.info(f"Experiment {exp['experiment_id']}: {exp['status']}")

async def main():
    """Main function with examples."""
    parser = argparse.ArgumentParser(description="Experiment API Client Example")
    parser.add_argument("--url", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--example", choices=["single", "batch", "status", "all"], 
                       default="single", help="Which example to run")
    args = parser.parse_args()
    
    async with ExperimentClient(args.url) as client:
        try:
            if args.example == "single":
                await run_single_experiment_example(client)
            elif args.example == "batch":
                await run_batch_experiment_example(client)
            elif args.example == "status":
                await run_status_monitoring_example(client)
            elif args.example == "all":
                await run_single_experiment_example(client)
                await asyncio.sleep(2)
                await run_batch_experiment_example(client)
                await asyncio.sleep(2)
                await run_status_monitoring_example(client)
                
        except Exception as e:
            logger.error(f"Error running example: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
