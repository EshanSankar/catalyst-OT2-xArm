#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Single Experiment Runner

This script runs a single experiment using the ExperimentDispatcher.
"""

import argparse
import json
import logging
import sys
from typing import Dict, Any

from dispatch import ExperimentDispatcher, LocalResultUploader
import sys
import os

# Add necessary modules to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Create mock classes for testing
class MockOT2Client:
    def __init__(self, *args, **kwargs):
        pass

class MockArduino:
    def __init__(self, *args, **kwargs):
        pass

# Monkey patch the imports in backend modules
import builtins
original_import = builtins.__import__

def mock_import(name, *args, **kwargs):
    if name == 'OT_Arduino_Client':
        module = type('MockModule', (), {})
        module.OT_Arduino_Client = MockOT2Client
        return module
    return original_import(name, *args, **kwargs)

builtins.__import__ = mock_import

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

def main():
    """Main function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a single experiment")
    parser.add_argument("experiment_file", help="Path to the experiment JSON file")
    parser.add_argument("--results-dir", default="results", help="Directory to store results")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no real devices)")
    args = parser.parse_args()

    # Load experiment file
    try:
        with open(args.experiment_file, 'r') as f:
            experiment = json.load(f)
    except Exception as e:
        LOGGER.error(f"Failed to load experiment file: {str(e)}")
        sys.exit(1)

    # Create result uploader
    result_uploader = LocalResultUploader(base_dir=args.results_dir)

    # Create experiment dispatcher
    dispatcher = ExperimentDispatcher(result_uploader=result_uploader)

    # Execute experiment
    try:
        LOGGER.info(f"Executing {experiment.get('uo_type')} experiment...")
        result = dispatcher.execute_experiment(experiment)

        if result.get("status") == "error":
            LOGGER.error(f"Experiment failed: {result.get('message')}")
            print(f"Experiment failed: {result.get('message')}")
            sys.exit(1)
        else:
            LOGGER.info("Experiment executed successfully")
            print(f"Experiment executed successfully!")
            print(f"Results saved to: {args.results_dir}/{result.get('experiment_id')}")
    except Exception as e:
        LOGGER.error(f"Error executing experiment: {str(e)}")
        sys.exit(1)
    finally:
        # Clean up resources
        dispatcher.cleanup()

if __name__ == "__main__":
    main()
