#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Runner with Fixed Deck Positions

This script runs a workflow using only standard labware and avoids problematic deck positions.
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
        logging.FileHandler("workflow_fixed_deck.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowFixedDeck")

def run_workflow_fixed_deck(workflow_file: str, robot_ip: str = None, arduino_port: str = None):
    """Run a workflow with fixed deck positions."""
    # Import necessary modules
    from workflow_executor import WorkflowExecutor
    
    # Load the workflow
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        LOGGER.error(f"Failed to load workflow file: {str(e)}")
        return False
    
    # Create a new workflow with only standard labware and proper deck positions
    LOGGER.info("Creating a new workflow with standard labware and proper deck positions...")
    
    fixed_workflow = {
        "name": "Fixed Deck Workflow",
        "version": "1.0.0",
        "description": "A workflow using only standard labware and proper deck positions",
        "global_config": {
            "labware": {
                "reactor_plate": {
                    "type": "corning_24_wellplate_3.4ml_flat",
                    "slot": 3,
                    "working_well": "B2"
                },
                "wash_station": {
                    "type": "nest_12_reservoir_15ml",
                    "slot": 6
                },
                "tip_rack": {
                    "type": "opentrons_96_tiprack_1000ul",
                    "slot": 1
                },
                "solution_rack": {
                    "type": "nest_12_reservoir_15ml",
                    "slot": 2
                }
            },
            "instruments": {
                "pipette": {
                    "type": "p1000_single_gen2",
                    "mount": "right"
                }
            }
        },
        "nodes": [
            {
                "id": "pickup_tip",
                "type": "OCV",
                "label": "Pick Up Tip",
                "params": {
                    "duration_s": 10,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "pick_up_tip",
                            "labware": "tip_rack",
                            "well": "A1"
                        }
                    ]
                }
            },
            {
                "id": "move_to_reactor",
                "type": "OCV",
                "label": "Move to Reactor",
                "params": {
                    "duration_s": 10,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "reactor_plate",
                            "well": "B2",
                            "offset": {
                                "z": -5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_wash",
                "type": "OCV",
                "label": "Move to Wash Station",
                "params": {
                    "duration_s": 10,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0,
                        "pump0_ml": 5.0,
                        "ultrasonic0_ms": 1000
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "wash_station",
                            "well": "A1"
                        },
                        {
                            "action": "wash",
                            "arduino_actions": {
                                "pump0_ml": 5.0,
                                "ultrasonic0_ms": 1000,
                                "pump2_ml": 6.0
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_solution",
                "type": "OCV",
                "label": "Move to Solution Rack",
                "params": {
                    "duration_s": 10,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "solution_rack",
                            "well": "A1"
                        }
                    ]
                }
            },
            {
                "id": "drop_tip",
                "type": "OCV",
                "label": "Drop Tip",
                "params": {
                    "duration_s": 10,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "tip_rack",
                            "well": "A1"
                        },
                        {
                            "action": "drop_tip",
                            "labware": "tip_rack",
                            "well": "A1"
                        },
                        {
                            "action": "home",
                            "labware": "robot",
                            "well": "home"
                        }
                    ]
                }
            }
        ],
        "edges": [
            {
                "source": "pickup_tip",
                "target": "move_to_reactor"
            },
            {
                "source": "move_to_reactor",
                "target": "move_to_wash"
            },
            {
                "source": "move_to_wash",
                "target": "move_to_solution"
            },
            {
                "source": "move_to_solution",
                "target": "drop_tip"
            }
        ]
    }
    
    # Save the fixed workflow to a temporary file
    temp_workflow_file = "fixed_workflow.json"
    with open(temp_workflow_file, 'w') as f:
        json.dump(fixed_workflow, f, indent=2)
    
    LOGGER.info(f"Saved fixed workflow to {temp_workflow_file}")
    
    # Create the workflow executor
    LOGGER.info(f"Creating WorkflowExecutor with fixed workflow file: {temp_workflow_file}")
    executor = WorkflowExecutor(temp_workflow_file)
    LOGGER.info("WorkflowExecutor created successfully")
    
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
    LOGGER.info("Executing workflow with fixed deck positions...")
    result = executor.execute_workflow()
    
    # Clean up the temporary file
    try:
        os.remove(temp_workflow_file)
        LOGGER.info(f"Removed temporary workflow file: {temp_workflow_file}")
    except Exception as e:
        LOGGER.warning(f"Failed to remove temporary workflow file: {str(e)}")
    
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
    parser = argparse.ArgumentParser(description="Run a workflow with fixed deck positions")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file (used only for reference)")
    parser.add_argument("--ip", type=str, help="IP address of the OT-2 robot")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino")
    args = parser.parse_args()
    
    success = run_workflow_fixed_deck(args.workflow_file, args.ip, args.port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
