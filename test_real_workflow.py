#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Real Workflow Execution

This script tests the execution of a workflow using real devices.
It connects to the OT-2 robot and Arduino using the real device classes.
"""

import sys
import os
import logging
import json
import argparse
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("real_workflow_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("RealWorkflowTest")

def test_device_connections(robot_ip="100.67.89.154", arduino_port=None):
    """Test connections to all devices."""
    LOGGER.info("Testing device connections...")
    
    # Test OT-2 connection
    try:
        from opentronsHTTPAPI_clientBuilder import opentronsClient
        LOGGER.info(f"Connecting to OT-2 at {robot_ip}...")
        ot2_client = opentronsClient(strRobotIP=robot_ip)
        LOGGER.info(f"Successfully connected to OT-2 with run ID: {ot2_client.runID}")
        ot2_connected = True
    except Exception as e:
        LOGGER.error(f"Failed to connect to OT-2: {str(e)}")
        ot2_connected = False
        ot2_client = None
    
    # Test Arduino connection
    try:
        # Find Arduino port if not specified
        if arduino_port is None:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            arduino_ports = [p.device for p in ports if "CH340" in p.description or "Arduino" in p.description]
            
            if not arduino_ports:
                LOGGER.warning("No Arduino found in port descriptions")
                if os.name == 'nt':  # Windows
                    arduino_port = "COM3"
                else:  # Linux/Mac
                    arduino_port = "/dev/ttyUSB0"
            else:
                arduino_port = arduino_ports[0]
        
        # Import Arduino class
        try:
            from ot2_arduino import Arduino
            LOGGER.info("Using Arduino from ot2_arduino.py")
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location("Arduino", "ot2-arduino.py")
            arduino_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(arduino_module)
            Arduino = arduino_module.Arduino
            LOGGER.info("Using Arduino from ot2-arduino.py")
        
        LOGGER.info(f"Connecting to Arduino on port {arduino_port}...")
        arduino_client = Arduino(arduinoPort=arduino_port)
        LOGGER.info("Successfully connected to Arduino")
        arduino_connected = True
    except Exception as e:
        LOGGER.error(f"Failed to connect to Arduino: {str(e)}")
        arduino_connected = False
        arduino_client = None
    
    return ot2_connected, arduino_connected, ot2_client, arduino_client

def execute_real_workflow(workflow_file, robot_ip="100.67.89.154", arduino_port=None):
    """Execute a workflow using real devices."""
    try:
        # Check if the workflow file exists
        if not os.path.isfile(workflow_file):
            LOGGER.error(f"Workflow file {workflow_file} does not exist")
            return False
        
        # Load the workflow file
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
            LOGGER.info(f"Workflow file loaded successfully. Structure: {list(workflow_data.keys())}")
            if 'global_config' in workflow_data:
                LOGGER.info(f"Global config keys: {list(workflow_data['global_config'].keys())}")
            if 'nodes' in workflow_data:
                LOGGER.info(f"Number of nodes: {len(workflow_data['nodes'])}")
                for i, node in enumerate(workflow_data['nodes'][:3]):
                    LOGGER.info(f"Node {i}: {node.get('id')} - {node.get('label')}")
            if 'edges' in workflow_data:
                LOGGER.info(f"Number of edges: {len(workflow_data['edges'])}")
        
        # Test device connections
        ot2_connected, arduino_connected, ot2_client, arduino_client = test_device_connections(robot_ip, arduino_port)
        
        if not ot2_connected:
            LOGGER.error("Cannot execute workflow without OT-2 connection")
            return False
        
        if not arduino_connected:
            LOGGER.warning("Arduino not connected - some functionality may be limited")
        
        # Import the WorkflowExecutor class
        from workflow_executor import WorkflowExecutor
        
        # Create the workflow executor
        LOGGER.info(f"Creating WorkflowExecutor with workflow file: {workflow_file}")
        executor = WorkflowExecutor(workflow_file)
        LOGGER.info("WorkflowExecutor created successfully")
        
        # Replace the client instances with real instances
        if ot2_client:
            executor.ot2_client = ot2_client
            LOGGER.info("Using real OT-2 client")
        
        if arduino_client:
            executor.arduino_client = arduino_client
            LOGGER.info("Using real Arduino client")
        
        # Execute the workflow
        LOGGER.info("Executing workflow with real devices...")
        result = executor.execute_workflow()
        
        if result:
            LOGGER.info("Real workflow executed successfully")
            return True
        else:
            LOGGER.error("Real workflow execution failed")
            return False
    except Exception as e:
        LOGGER.error(f"Error during real workflow execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test execution of a workflow using real devices")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("--ip", type=str, default="100.67.89.154", help="IP address of the OT-2 robot")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)")
    args = parser.parse_args()
    
    LOGGER.info(f"Starting real workflow execution test with file: {args.workflow_file}")
    
    success = execute_real_workflow(args.workflow_file, args.ip, args.port)
    
    if success:
        print("\nReal Workflow Execution Test: ✓")
        print("Workflow executed successfully on real devices!")
    else:
        print("\nReal Workflow Execution Test: ✗")
        print("Workflow execution on real devices failed.")
        print("\nTroubleshooting Tips:")
        print("- Check if all devices are properly connected")
        print("- Verify the OT-2 IP address and Arduino port are correct")
        print("- Make sure the workflow file is valid")
        print("- Check the log file for detailed error messages")
    
    return success

if __name__ == "__main__":
    main()
