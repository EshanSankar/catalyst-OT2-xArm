#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Runner Script

This script combines the dispatch mechanism and workflow executor to run
electrochemical experiments defined in a JSON workflow file.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Any

# Import the necessary modules
from dispatch import ExperimentDispatcher, validate_workflow_json
from workflow_executor import WorkflowExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("workflow_execution.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowRunner")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Execute an electrochemical workflow")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("--schema", default="workflow_schema.json", help="Path to the schema JSON file")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no real devices)")
    parser.add_argument("--ip_ot2", type=str, help="IP address of the OT-2 robot")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino")
    parser.add_argument("--results-dir", type=str, default="results", help="Directory to store results")
    return parser.parse_args()

def run_workflow(args):
    """Run the workflow using the executor and dispatcher."""
    workflow_file = args.workflow_file
    schema_file = args.schema
    use_mock = args.mock
    results_dir = args.results_dir

    LOGGER.info(f"Starting workflow execution with file: {workflow_file}")
    LOGGER.info(f"Mock mode: {use_mock}")
    LOGGER.info(f"Results directory: {results_dir}")

    if args.ip_ot2:
        LOGGER.info(f"Using custom OT-2 IP: {args.ip_ot2}")

    if args.port:
        LOGGER.info(f"Using custom Arduino port: {args.port}")

    # Validate workflow JSON
    try:
        if not validate_workflow_json(workflow_file, schema_file):
            LOGGER.error("Workflow validation failed")
            return False
    except ValueError as e:
        LOGGER.error(f"Workflow validation error: {str(e)}")
        return False

    # Load workflow file
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
            LOGGER.info(f"Workflow file loaded successfully")
    except Exception as e:
        LOGGER.error(f"Error loading workflow file: {str(e)}")
        return False

    # Create the experiment dispatcher
    try:
        from dispatch import LocalResultUploader
        result_uploader = LocalResultUploader(base_dir=results_dir)
        dispatcher = ExperimentDispatcher(result_uploader=result_uploader)
        LOGGER.info("Experiment dispatcher created successfully")
    except Exception as e:
        LOGGER.error(f"Failed to create experiment dispatcher: {str(e)}")
        return False

    # Create the workflow executor
    try:
        executor = WorkflowExecutor(workflow_file)
        LOGGER.info("Workflow executor created successfully")

        # If not in mock mode, try to use real devices
        if not use_mock:
            try:
                # Configure OT-2 client
                if args.ip_ot2:
                    robot_ip = args.ip_ot2
                else:
                    robot_ip = workflow.get("global_config", {}).get("hardware", {}).get("ot2", {}).get("ip_ot2", "100.67.89.154")
                
                # Configure Arduino client
                if args.port:
                    arduino_port = args.port
                else:
                    # Default port based on OS
                    if os.name == 'nt':  # Windows
                        arduino_port = "COM3"
                    else:  # Linux/Mac
                        arduino_port = "/dev/ttyUSB0"
                
                LOGGER.info(f"Using OT-2 IP: {robot_ip}")
                LOGGER.info(f"Using Arduino port: {arduino_port}")
            except Exception as e:
                LOGGER.warning(f"Error configuring devices: {str(e)}")
                LOGGER.info("Falling back to mock mode")
                use_mock = True
    except Exception as e:
        LOGGER.error(f"Failed to create workflow executor: {str(e)}")
        return False

    # Execute the workflow
    try:
        LOGGER.info("Executing workflow...")
        result = executor.execute_workflow()

        if result:
            LOGGER.info("Workflow executed successfully")
            print("\nWorkflow Execution: ✓")
            print("Workflow executed successfully!")
            return True
        else:
            LOGGER.error("Workflow execution failed")
            print("\nWorkflow Execution: ✗")
            print("Workflow execution failed.")
            print("\nTroubleshooting Tips:")
            print("- Check if all devices are properly connected")
            print("- Verify the OT-2 IP address and Arduino port are correct")
            print("- Make sure the workflow file is valid")
            print("- Check the log file for detailed error messages")
            return False
    except Exception as e:
        LOGGER.error(f"Error executing workflow: {str(e)}")
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
    success = run_workflow(args)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
