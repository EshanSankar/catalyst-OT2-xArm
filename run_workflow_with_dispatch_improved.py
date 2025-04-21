#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improved Workflow Runner with Dispatch

This script runs a workflow using both the workflow executor and the experiment dispatcher.
It properly simulates OT-2 movements and imports the necessary backend modules.
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
        logging.FileHandler("workflow_dispatch_improved.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowDispatcher")

# Create a better mock OT-2 client for visualization
class MockOT2Client:
    def __init__(self, strRobotIP="100.67.89.154"):
        self.robot_ip = strRobotIP
        self.current_position = {"x": 0, "y": 0, "z": 0}
        self.has_tip = False
        self.labware = {}
        self.runID = "mock-run-id"
        LOGGER.info(f"Mock OT-2 client initialized with IP: {strRobotIP}")
    
    def lights(self, state):
        LOGGER.info(f"OT-2 lights turned {'ON' if state else 'OFF'}")
    
    def homeRobot(self):
        LOGGER.info("OT-2 robot homing...")
        time.sleep(0.5)  # Simulate homing time
        self.current_position = {"x": 0, "y": 0, "z": 0}
        LOGGER.info("OT-2 robot homed successfully")
    
    def loadLabware(self, intSlot, strLabwareName):
        labware_id = f"{strLabwareName}_{intSlot}"
        self.labware[labware_id] = {
            "name": strLabwareName,
            "slot": intSlot,
            "wells": {}
        }
        LOGGER.info(f"Loaded labware {strLabwareName} in slot {intSlot}")
        return labware_id
    
    def loadCustomLabware(self, dicLabware, intSlot):
        labware_name = dicLabware.get("metadata", {}).get("name", "custom_labware")
        labware_id = f"{labware_name}_{intSlot}"
        self.labware[labware_id] = {
            "name": labware_name,
            "slot": intSlot,
            "wells": {}
        }
        LOGGER.info(f"Loaded custom labware {labware_name} in slot {intSlot}")
        return labware_id
    
    def loadPipette(self, strPipetteName, strMount):
        LOGGER.info(f"Loaded pipette {strPipetteName} on {strMount} mount")
    
    def moveToWell(self, strLabwareName, strWellName, strPipetteName, strOffsetStart, fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0, intSpeed=100):
        # Simulate movement
        LOGGER.info(f"OT-2 moving to {strLabwareName} {strWellName}...")
        time.sleep(0.3)  # Simulate movement time
        
        # Update position (simplified)
        slot = int(strLabwareName.split('_')[-1])
        self.current_position = {
            "x": (slot % 3) * 100 + 50 + fltOffsetX,
            "y": (slot // 3) * 100 + 50 + fltOffsetY,
            "z": 50 + fltOffsetZ
        }
        
        LOGGER.info(f"OT-2 moved to {strLabwareName} {strWellName} at position {self.current_position}")
    
    def pickUpTip(self, strLabwareName, strPipetteName, strWellName, fltOffsetX=0, fltOffsetY=0):
        if self.has_tip:
            LOGGER.warning("OT-2 already has a tip! Dropping it first.")
            self.dropTip(strLabwareName, strPipetteName, strWellName)
        
        LOGGER.info(f"OT-2 picking up tip from {strLabwareName} {strWellName}...")
        time.sleep(0.5)  # Simulate pick up time
        self.has_tip = True
        LOGGER.info(f"OT-2 picked up tip from {strLabwareName} {strWellName}")
    
    def dropTip(self, strLabwareName, strPipetteName, strWellName, strOffsetStart="bottom", fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0):
        if not self.has_tip:
            LOGGER.warning("OT-2 has no tip to drop!")
            return
        
        LOGGER.info(f"OT-2 dropping tip to {strLabwareName} {strWellName}...")
        time.sleep(0.3)  # Simulate drop time
        self.has_tip = False
        LOGGER.info(f"OT-2 dropped tip to {strLabwareName} {strWellName}")

# Create a better mock Arduino client for visualization
class MockArduino:
    def __init__(self, arduinoPort="COM3"):
        self.port = arduinoPort
        self.current_temp = 25.0
        self.pumps = {0: "water", 1: "acid", 2: "waste"}
        LOGGER.info(f"Mock Arduino initialized on port: {arduinoPort}")
    
    def setTemp(self, baseNumber, targetTemp):
        LOGGER.info(f"Arduino setting base {baseNumber} temperature from {self.current_temp}°C to {targetTemp}°C...")
        time.sleep(0.2)  # Simulate temperature change time
        self.current_temp = targetTemp
        LOGGER.info(f"Arduino set base {baseNumber} temperature to {targetTemp}°C")
    
    def dispense_ml(self, pumpNumber, volume):
        pump_name = self.pumps.get(pumpNumber, f"pump{pumpNumber}")
        LOGGER.info(f"Arduino dispensing {volume}ml from {pump_name} (pump {pumpNumber})...")
        time.sleep(0.3)  # Simulate dispensing time
        LOGGER.info(f"Arduino dispensed {volume}ml from {pump_name} (pump {pumpNumber})")
    
    def setUltrasonicOnTimer(self, baseNumber, timeOn_ms):
        LOGGER.info(f"Arduino running ultrasonic on base {baseNumber} for {timeOn_ms}ms...")
        time.sleep(0.2)  # Simulate a fraction of the ultrasonic time
        LOGGER.info(f"Arduino ran ultrasonic on base {baseNumber} for {timeOn_ms}ms")

def run_workflow_with_dispatch(workflow_file: str, mock: bool = True, results_dir: str = "results"):
    """Run a workflow using both the executor and dispatcher with improved visualization."""
    # Import necessary modules
    from dispatch import ExperimentDispatcher, LocalResultUploader, validate_workflow_json
    from workflow_executor import WorkflowExecutor
    
    # Validate the workflow
    try:
        if not validate_workflow_json(workflow_file):
            LOGGER.error("Workflow validation failed")
            return False
    except ValueError as e:
        LOGGER.error(f"Workflow validation error: {str(e)}")
        return False
    
    # Load the workflow
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        LOGGER.error(f"Failed to load workflow file: {str(e)}")
        return False
    
    # Create result uploader
    result_uploader = LocalResultUploader(base_dir=results_dir)
    
    # Create experiment dispatcher
    dispatcher = ExperimentDispatcher(result_uploader=result_uploader)
    
    # Create the workflow executor
    executor = WorkflowExecutor(workflow_file)
    
    # Replace the OT-2 and Arduino clients with our improved mock clients if in mock mode
    if mock:
        LOGGER.info("Using improved mock clients for better visualization")
        executor.ot2_client = MockOT2Client()
        executor.arduino_client = MockArduino()
    
    # Execute the workflow
    LOGGER.info("Executing workflow...")
    result = executor.execute_workflow()
    
    if not result:
        LOGGER.error("Workflow execution failed")
        return False
    
    # Extract nodes from the workflow
    nodes = workflow.get("nodes", [])
    edges = workflow.get("edges", [])
    
    # Create a dictionary to map node IDs to nodes
    node_map = {node["id"]: node for node in nodes}
    
    # Create a dictionary to map node IDs to their children
    children_map = {}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in children_map:
            children_map[source] = []
        children_map[source].append(target)
    
    # Find the starting nodes (nodes with no incoming edges)
    starting_nodes = []
    all_targets = [edge.get("target") for edge in edges]
    for node in nodes:
        if node["id"] not in all_targets:
            starting_nodes.append(node["id"])
    
    if not starting_nodes:
        LOGGER.error("No starting node found in the workflow")
        return False
    
    # Create a list to store the execution order
    execution_order = []
    
    # Function to traverse the workflow graph
    def traverse_graph(node_id):
        execution_order.append(node_id)
        children = children_map.get(node_id, [])
        for child_id in children:
            traverse_graph(child_id)
    
    # Traverse the graph starting from each starting node
    for starting_node_id in starting_nodes:
        traverse_graph(starting_node_id)
    
    # Execute each node in order using the dispatcher
    LOGGER.info(f"Dispatching {len(execution_order)} nodes to backend modules...")
    
    for i, node_id in enumerate(execution_order):
        node = node_map.get(node_id)
        if not node:
            LOGGER.error(f"Node {node_id} not found in the workflow")
            continue
        
        LOGGER.info(f"Dispatching node {i+1}/{len(execution_order)}: {node_id} ({node.get('label')})")
        
        # Convert the node to an experiment format for the dispatcher
        experiment = {
            "uo_type": node.get("type"),
            "parameters": {}
        }
        
        # Extract parameters from the node
        params = node.get("params", {})
        
        # Map common parameters
        parameter_mapping = {
            "duration_s": "duration",
            "sample_rate": "sample_interval",
            "current_mA": "current",
            "start_voltage_V": "start_voltage",
            "end_voltage_V": "end_voltage",
            "scan_rate_mV_s": "scan_rate",
            "cycles": "cycles",
            "start_freq_Hz": "start_freq",
            "end_freq_Hz": "end_freq",
            "amplitude_mV": "amplitude"
        }
        
        for node_param, dispatch_param in parameter_mapping.items():
            if node_param in params:
                experiment["parameters"][dispatch_param] = params[node_param]
        
        # Add Arduino control parameters
        if "arduino_control" in params:
            experiment["parameters"]["arduino_control"] = params["arduino_control"]
        
        # Add OT-2 actions
        if "ot2_actions" in params:
            experiment["parameters"]["ot2_actions"] = params["ot2_actions"]
        
        # Execute the experiment
        try:
            LOGGER.info(f"Dispatching {experiment['uo_type']} experiment to backend...")
            
            # In mock mode, just log the experiment details
            if mock:
                LOGGER.info(f"Mock execution of {experiment['uo_type']} experiment")
                LOGGER.info(f"Parameters: {experiment['parameters']}")
                time.sleep(0.5)  # Simulate execution time
                LOGGER.info(f"Mock execution of {experiment['uo_type']} completed successfully")
            else:
                # Real execution using the dispatcher
                result = dispatcher.execute_experiment(experiment)
                
                if result.get("status") == "error":
                    LOGGER.error(f"Experiment failed: {result.get('message')}")
                    LOGGER.warning("Continuing with next experiment...")
                else:
                    LOGGER.info(f"Experiment executed successfully: {result.get('experiment_id')}")
        except Exception as e:
            LOGGER.error(f"Error executing experiment: {str(e)}")
            LOGGER.warning("Continuing with next experiment...")
    
    # Clean up resources
    dispatcher.cleanup()
    
    LOGGER.info("Workflow execution with dispatch completed successfully")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a workflow with improved visualization")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no real devices)", default=True)
    parser.add_argument("--results-dir", default="results", help="Directory to store results")
    args = parser.parse_args()
    
    success = run_workflow_with_dispatch(args.workflow_file, args.mock, args.results_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
