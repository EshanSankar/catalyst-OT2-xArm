#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Workflow Execution

This script tests the execution of a workflow using the WorkflowExecutor class.
"""

import sys
import os
import logging
import json
import argparse
from typing import Dict, Any

# Import the WorkflowExecutor class
from workflow_executor import WorkflowExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("workflow_execution_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowExecutionTest")

def test_workflow_execution(workflow_file: str) -> bool:
    """Test the execution of a workflow."""
    try:
        # Check if the workflow file exists
        if not os.path.isfile(workflow_file):
            LOGGER.error(f"Workflow file {workflow_file} does not exist")
            return False
        
        # Load the workflow file to check its structure
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
        
        # Create and run the workflow executor
        LOGGER.info(f"Creating WorkflowExecutor with workflow file: {workflow_file}")
        executor = WorkflowExecutor(workflow_file)
        LOGGER.info("WorkflowExecutor created successfully")
        
        # Execute the workflow
        LOGGER.info("Executing workflow...")
        result = executor.execute_workflow()
        
        if result:
            LOGGER.info("Workflow executed successfully")
            return True
        else:
            LOGGER.error("Workflow execution failed")
            return False
    except Exception as e:
        LOGGER.error(f"Error during workflow execution test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to test workflow execution."""
    parser = argparse.ArgumentParser(description="Test workflow execution")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    args = parser.parse_args()
    
    LOGGER.info(f"Starting workflow execution test with file: {args.workflow_file}")
    
    # Test workflow execution
    success = test_workflow_execution(args.workflow_file)
    
    # Print summary
    print("\nWorkflow Execution Test Summary:")
    print("--------------------------------")
    print(f"Workflow Execution: {'✓' if success else '✗'}")
    
    if not success:
        print("\nTroubleshooting Tips:")
        print("- Check if the workflow file is valid JSON")
        print("- Verify that all required devices are connected")
        print("- Check the log file for detailed error messages")
        return False
    
    print("\nWorkflow executed successfully!")
    return True

if __name__ == "__main__":
    main()
