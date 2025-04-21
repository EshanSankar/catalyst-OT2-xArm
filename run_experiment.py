#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Experiment Runner Script

This script uses the ExperimentDispatcher to run individual electrochemical experiments.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Any

# Import the necessary modules
from dispatch import ExperimentDispatcher, LocalResultUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("experiment_execution.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("ExperimentRunner")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Execute an electrochemical experiment")
    parser.add_argument("experiment_file", help="Path to the experiment JSON file")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no real devices)")
    parser.add_argument("--ip", type=str, help="IP address of the OT-2 robot")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino")
    parser.add_argument("--results-dir", type=str, default="results", help="Directory to store results")
    return parser.parse_args()

def run_experiment(args):
    """Run a single experiment using the dispatcher."""
    experiment_file = args.experiment_file
    use_mock = args.mock
    results_dir = args.results_dir

    LOGGER.info(f"Starting experiment execution with file: {experiment_file}")
    LOGGER.info(f"Mock mode: {use_mock}")
    LOGGER.info(f"Results directory: {results_dir}")

    if args.ip:
        LOGGER.info(f"Using custom OT-2 IP: {args.ip}")

    if args.port:
        LOGGER.info(f"Using custom Arduino port: {args.port}")

    # Load experiment file
    try:
        with open(experiment_file, 'r', encoding='utf-8') as f:
            experiment = json.load(f)
            LOGGER.info(f"Experiment file loaded successfully")
    except Exception as e:
        LOGGER.error(f"Error loading experiment file: {str(e)}")
        return False

    # Create the experiment dispatcher
    try:
        result_uploader = LocalResultUploader(base_dir=results_dir)
        dispatcher = ExperimentDispatcher(result_uploader=result_uploader)
        LOGGER.info("Experiment dispatcher created successfully")
    except Exception as e:
        LOGGER.error(f"Failed to create experiment dispatcher: {str(e)}")
        return False

    # Execute the experiment
    try:
        LOGGER.info(f"Executing {experiment.get('uo_type', 'unknown')} experiment...")
        result = dispatcher.execute_experiment(experiment)

        if result.get("status") == "error":
            LOGGER.error(f"Experiment execution failed: {result.get('message', 'Unknown error')}")
            print("\nExperiment Execution: ✗")
            print(f"Experiment execution failed: {result.get('message', 'Unknown error')}")
            return False
        else:
            LOGGER.info("Experiment executed successfully")
            print("\nExperiment Execution: ✓")
            print("Experiment executed successfully!")
            print(f"Results saved to: {os.path.join(results_dir, result.get('experiment_id', 'unknown'))}")
            return True
    except Exception as e:
        LOGGER.error(f"Error executing experiment: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up resources
        try:
            dispatcher.cleanup()
            LOGGER.info("Cleaned up dispatcher resources")
        except Exception as e:
            LOGGER.warning(f"Error cleaning up resources: {str(e)}")

def main():
    """Main function."""
    args = parse_arguments()
    success = run_experiment(args)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
