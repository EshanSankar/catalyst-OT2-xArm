#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Mock Workflow Execution

This script tests the execution of a workflow using the WorkflowExecutor class with mock device classes.
"""

import sys
import os
import logging
import json
import argparse
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mock_workflow_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("MockWorkflowTest")

# Create mock classes for testing
class MockOpentronsClient:
    def __init__(self, strRobotIP="100.67.89.154"):
        self.robot_ip = strRobotIP
        LOGGER.info(f"Mock OT-2: Connecting to OT-2 at {strRobotIP}...")
    
    def lights(self, state):
        LOGGER.info(f"Mock OT-2: Setting lights to {state}")
    
    def homeRobot(self):
        LOGGER.info("Mock OT-2: Homing robot")
    
    def loadLabware(self, intSlot, strLabwareName):
        LOGGER.info(f"Mock OT-2: Loading labware {strLabwareName} in slot {intSlot}")
        return f"{strLabwareName}_{intSlot}"
    
    def loadCustomLabware(self, dicLabware, intSlot):
        labware_name = dicLabware.get("metadata", {}).get("name", "custom_labware")
        LOGGER.info(f"Mock OT-2: Loading custom labware {labware_name} in slot {intSlot}")
        return f"{labware_name}_{intSlot}"
    
    def loadPipette(self, strPipetteName, strMount):
        LOGGER.info(f"Mock OT-2: Loading pipette {strPipetteName} on {strMount} mount")
    
    def moveToWell(self, strLabwareName, strWellName, strPipetteName, strOffsetStart, fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0, intSpeed=100):
        LOGGER.info(f"Mock OT-2: Moving {strPipetteName} to {strLabwareName} {strWellName} with offset {fltOffsetX}, {fltOffsetY}, {fltOffsetZ}")
    
    def pickUpTip(self, strLabwareName, strPipetteName, strWellName, fltOffsetX=0, fltOffsetY=0):
        LOGGER.info(f"Mock OT-2: Picking up tip from {strLabwareName} {strWellName}")
    
    def dropTip(self, strLabwareName, strPipetteName, strWellName, strOffsetStart="bottom", fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0):
        LOGGER.info(f"Mock OT-2: Dropping tip to {strLabwareName} {strWellName}")

class MockArduino:
    def __init__(self, arduinoPort="COM3"):
        self.port = arduinoPort
        LOGGER.info(f"Mock Arduino: Connecting to Arduino on port {arduinoPort}...")
    
    def setTemp(self, baseNumber, targetTemp):
        LOGGER.info(f"Mock Arduino: Setting base {baseNumber} temperature to {targetTemp}°C")
    
    def dispense_ml(self, pumpNumber, volume):
        LOGGER.info(f"Mock Arduino: Dispensing {volume}ml from pump {pumpNumber}")
    
    def setUltrasonicOnTimer(self, baseNumber, timeOn_ms):
        LOGGER.info(f"Mock Arduino: Running ultrasonic on base {baseNumber} for {timeOn_ms}ms")

def create_simple_workflow():
    """Create a simple workflow for testing."""
    workflow = {
        "global_config": {
            "labware": {
                "reactor_plate": {
                    "type": "nis_15_wellplate_3895ul",
                    "slot": 9
                },
                "wash_station": {
                    "type": "nis_2_wellplate_30000ul",
                    "slot": 3
                },
                "tip_rack": {
                    "type": "opentrons_96_tiprack_1000ul",
                    "slot": 1
                }
            },
            "instruments": {
                "pipette": {
                    "type": "p1000_single_gen2",
                    "mount": "right"
                }
            },
            "arduino_control": {
                "pumps": {
                    "water": 0,
                    "acid": 1,
                    "out": 2
                },
                "temperature": {
                    "default": 25.0
                }
            }
        },
        "nodes": [
            {
                "id": "node1",
                "label": "Pick Up Tip",
                "params": {
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
                "id": "node2",
                "label": "Move to Well",
                "params": {
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "reactor_plate",
                            "well": "B2",
                            "offset": {
                                "z": -20
                            }
                        }
                    ],
                    "arduino_control": {
                        "base0_temp": 25.0
                    }
                }
            },
            {
                "id": "node3",
                "label": "Wash",
                "params": {
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
                                "ultrasonic0_ms": 5000,
                                "pump2_ml": 6.0
                            }
                        }
                    ]
                }
            },
            {
                "id": "node4",
                "label": "Drop Tip",
                "params": {
                    "ot2_actions": [
                        {
                            "action": "drop_tip",
                            "labware": "tip_rack",
                            "well": "A1"
                        },
                        {
                            "action": "home"
                        }
                    ],
                    "arduino_control": {
                        "base0_temp": 25.0
                    }
                }
            }
        ],
        "edges": [
            {
                "source": "node1",
                "target": "node2"
            },
            {
                "source": "node2",
                "target": "node3"
            },
            {
                "source": "node3",
                "target": "node4"
            }
        ]
    }
    return workflow

def test_mock_workflow():
    """Test the execution of a workflow with mock classes."""
    try:
        # Create a simple workflow
        workflow = create_simple_workflow()
        
        # Save the workflow to a temporary file
        temp_workflow_file = "temp_mock_workflow.json"
        with open(temp_workflow_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        LOGGER.info(f"Created temporary workflow file: {temp_workflow_file}")
        
        # Import the WorkflowExecutor class
        from workflow_executor import WorkflowExecutor
        
        # Create and run the workflow executor
        LOGGER.info(f"Creating WorkflowExecutor with workflow file: {temp_workflow_file}")
        executor = WorkflowExecutor(temp_workflow_file)
        LOGGER.info("WorkflowExecutor created successfully")
        
        # Replace the client instances with mock instances
        executor.ot2_client = MockOpentronsClient()
        executor.arduino_client = MockArduino()
        
        # Execute the workflow
        LOGGER.info("Executing workflow with mock devices...")
        result = executor.execute_workflow()
        
        # Clean up the temporary file
        os.remove(temp_workflow_file)
        
        if result:
            LOGGER.info("Mock workflow executed successfully")
            return True
        else:
            LOGGER.error("Mock workflow execution failed")
            return False
    except Exception as e:
        LOGGER.error(f"Error during mock workflow execution test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to test mock workflow execution."""
    LOGGER.info("Starting mock workflow execution test")
    
    # Test mock workflow execution
    success = test_mock_workflow()
    
    # Print summary
    print("\nMock Workflow Execution Test Summary:")
    print("------------------------------------")
    print(f"Mock Workflow Execution: {'✓' if success else '✗'}")
    
    if not success:
        print("\nTroubleshooting Tips:")
        print("- Check the log file for detailed error messages")
        return False
    
    print("\nMock workflow executed successfully!")
    return True

if __name__ == "__main__":
    main()
