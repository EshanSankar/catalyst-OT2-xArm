#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Runner with Dispatch

This script runs a workflow using both the workflow executor and the experiment dispatcher.
It first executes the workflow using the executor, then extracts each experiment and runs it
using the dispatcher.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Any, List

# Import the necessary modules
from dispatch import ExperimentDispatcher, LocalResultUploader, validate_workflow_json
from workflow_executor import WorkflowExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("workflow_dispatch.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowDispatcher")

def convert_node_to_experiment(node: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a workflow node to an experiment format for the dispatcher."""
    experiment = {
        "uo_type": node["type"],
        "parameters": {}
    }
    
    # Extract parameters from the node
    params = node.get("params", {})
    
    # Map common parameters
    parameter_mapping = {
        "duration_s": "duration",
        "sample_rate": "sample_rate",
        "current_mA": "current",
        "start_voltage_V": "start_voltage",
        "end_voltage_V": "end_voltage",
        "scan_rate_mV_s": "scan_rate",
        "cycles": "cycles",
        "start_freq_Hz": "frequency_high",
        "end_freq_Hz": "frequency_low",
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
    
    return experiment

def run_workflow_with_dispatch(workflow_file: str, mock: bool = False, results_dir: str = "results"):
    """Run a workflow using both the executor and dispatcher."""
    # First, validate the workflow
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
    LOGGER.info(f"Executing {len(execution_order)} nodes in sequence")
    
    for i, node_id in enumerate(execution_order):
        node = node_map.get(node_id)
        if not node:
            LOGGER.error(f"Node {node_id} not found in the workflow")
            continue
        
        LOGGER.info(f"Executing node {i+1}/{len(execution_order)}: {node_id} ({node.get('label')})")
        
        # Convert the node to an experiment
        experiment = convert_node_to_experiment(node)
        
        # Execute the experiment
        try:
            LOGGER.info(f"Dispatching {experiment['uo_type']} experiment...")
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
    
    LOGGER.info("Workflow execution with dispatch completed")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a workflow with dispatch")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no real devices)")
    parser.add_argument("--results-dir", default="results", help="Directory to store results")
    args = parser.parse_args()
    
    success = run_workflow_with_dispatch(args.workflow_file, args.mock, args.results_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
