#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Runner for Real Hardware

This script runs a workflow using real hardware connections to the OT-2 and Arduino.
It ensures that the OT-2 head actually moves to the specified positions.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, Any, List

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("workflow_real_hardware.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowRealHardware")

def run_workflow_real_hardware(workflow_file: str, robot_ip: str = None, arduino_port: str = None):
    """Run a workflow using real hardware connections."""
    # Import necessary modules
    from workflow_executor import WorkflowExecutor
    
    # Create the workflow executor
    LOGGER.info(f"Creating WorkflowExecutor with workflow file: {workflow_file}")
    executor = WorkflowExecutor(workflow_file)
    LOGGER.info("WorkflowExecutor created successfully")
    
    # Load the workflow
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        LOGGER.error(f"Failed to load workflow file: {str(e)}")
        return False
    
    # Try to import the opentronsClient class
    try:
        LOGGER.info("Importing opentronsClient...")
        from opentronsHTTPAPI_clientBuilder import opentronsClient
        LOGGER.info("Successfully imported opentronsClient")
        
        # Create a client instance
        if robot_ip:
            ot2_ip = robot_ip
        else:
            ot2_ip = workflow.get("global_config", {}).get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
        
        LOGGER.info(f"Creating OT-2 client with IP: {ot2_ip}")
        ot2_client = opentronsClient(strRobotIP=ot2_ip)
        LOGGER.info(f"Successfully created OT-2 client with run ID: {ot2_client.runID}")
        
        # Replace the OT-2 client in the executor
        executor.ot2_client = ot2_client
        LOGGER.info("Using real OT-2 client")
    except Exception as e:
        LOGGER.error(f"Failed to create OT-2 client: {str(e)}")
        return False
    
    # Try to import the Arduino class
    try:
        LOGGER.info("Importing Arduino...")
        
        # Try to import from ot2_arduino.py
        try:
            from ot2_arduino import Arduino
            LOGGER.info("Successfully imported Arduino from ot2_arduino.py")
        except ImportError:
            # Try to import from ot2-arduino.py using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location("Arduino", "ot2-arduino.py")
            arduino_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(arduino_module)
            Arduino = arduino_module.Arduino
            LOGGER.info("Successfully imported Arduino from ot2-arduino.py")
        
        # Create an Arduino instance
        if arduino_port:
            port = arduino_port
        else:
            # Default port based on OS
            if os.name == 'nt':  # Windows
                port = "COM3"
            else:  # Linux/Mac
                port = "/dev/ttyUSB0"
        
        LOGGER.info(f"Creating Arduino client with port: {port}")
        
        # Close any existing connections to the port
        try:
            import serial
            ser = serial.Serial(port)
            ser.close()
            LOGGER.info(f"Closed existing connection to {port}")
        except Exception as e:
            LOGGER.info(f"No existing connection to close: {str(e)}")
        
        # Create the Arduino client
        arduino_client = Arduino(arduinoPort=port)
        LOGGER.info("Successfully created Arduino client")
        
        # Replace the Arduino client in the executor
        executor.arduino_client = arduino_client
        LOGGER.info("Using real Arduino client")
    except Exception as e:
        LOGGER.error(f"Failed to create Arduino client: {str(e)}")
        return False
    
    # Execute the workflow
    LOGGER.info("Executing workflow with real hardware...")
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

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a workflow with real hardware")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("--ip", type=str, help="IP address of the OT-2 robot")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino")
    args = parser.parse_args()
    
    success = run_workflow_real_hardware(args.workflow_file, args.ip, args.port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
