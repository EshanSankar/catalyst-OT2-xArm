#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo Workflow Runner

This script runs a workflow with extensive OT-2 head movements for demonstration purposes.
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
        logging.FileHandler("demo_workflow.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("DemoWorkflow")

def run_demo_workflow(robot_ip: str = None, arduino_port: str = None):
    """Run a demo workflow with extensive OT-2 head movements."""
    # Import necessary modules
    from workflow_executor import WorkflowExecutor
    
    # Create a demo workflow with extensive OT-2 head movements
    LOGGER.info("Creating a demo workflow with extensive OT-2 head movements...")
    
    demo_workflow = {
        "global_config": {
            "labware": {
                "strID_pipetteTipRack": {
                    "type": "opentrons_96_tiprack_1000ul",
                    "slot": 1
                },
                "strID_vialRack_2": {
                    "type": "nest_12_reservoir_15ml",
                    "slot": 2
                },
                "strID_washStation": {
                    "type": "nest_12_reservoir_15ml",
                    "slot": 3
                },
                "strID_plate_4": {
                    "type": "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
                    "slot": 4
                },
                "strID_plate_5": {
                    "type": "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
                    "slot": 5
                },
                "strID_plate_6": {
                    "type": "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
                    "slot": 6
                },
                "strID_NISreactor": {
                    "type": "corning_24_wellplate_3.4ml_flat",
                    "slot": 9
                },
                "strID_electrodeTipRack": {
                    "type": "opentrons_96_tiprack_300ul",
                    "slot": 10
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
                "id": "home_robot",
                "type": "OCV",
                "label": "Home Robot",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "home",
                            "labware": "robot",
                            "well": "home"
                        }
                    ]
                }
            },
            {
                "id": "pickup_tip_1",
                "type": "OCV",
                "label": "Pick Up Tip from Rack 1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "pick_up_tip",
                            "labware": "strID_electrodeTipRack",
                            "well": "B1"
                        }
                    ]
                }
            },
            {
                "id": "move_to_rack_2_b1",
                "type": "OCV",
                "label": "Move to Rack 2 B1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_vialRack_2",
                            "well": "B1",
                            "offset": {
                                "z": 20
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_rack_2_b2",
                "type": "OCV",
                "label": "Move to Rack 2 B2",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_vialRack_2",
                            "well": "B2",
                            "offset": {
                                "z": 20
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_wash_station",
                "type": "OCV",
                "label": "Move to Wash Station",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_washStation",
                            "well": "B1",
                            "offset": {
                                "z": 20
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_4_b2",
                "type": "CVA",
                "label": "Move to Plate 4 B2",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_plate_4",
                            "well": "B2",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_5_b2",
                "type": "PEIS",
                "label": "Move to Plate 5 B2",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_plate_5",
                            "well": "B2",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_6_b2",
                "type": "LSV",
                "label": "Move to Plate 6 B2",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_plate_6",
                            "well": "B2",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_reactor",
                "type": "CP",
                "label": "Move to Reactor",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_NISreactor",
                            "well": "B2",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "drop_tip",
                "type": "OCV",
                "label": "Drop Tip",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_electrodeTipRack",
                            "well": "B1"
                        },
                        {
                            "action": "drop_tip",
                            "labware": "strID_electrodeTipRack",
                            "well": "B1"
                        }
                    ]
                }
            },
            {
                "id": "pickup_tip_2",
                "type": "OCV",
                "label": "Pick Up Tip from Rack 1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "pick_up_tip",
                            "labware": "strID_pipetteTipRack",
                            "well": "B1"
                        }
                    ]
                }
            },
            {
                "id": "move_to_reactor_again",
                "type": "OCV",
                "label": "Move to Reactor Again",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_NISreactor",
                            "well": "B2",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "final_drop_tip",
                "type": "OCV",
                "label": "Final Drop Tip",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "strID_pipetteTipRack",
                            "well": "B1"
                        },
                        {
                            "action": "drop_tip",
                            "labware": "strID_pipetteTipRack",
                            "well": "B1"
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
            {"source": "home_robot", "target": "pickup_tip_1"},
            {"source": "pickup_tip_1", "target": "move_to_rack_2_b1"},
            {"source": "move_to_rack_2_b1", "target": "move_to_rack_2_b2"},
            {"source": "move_to_rack_2_b2", "target": "move_to_wash_station"},
            {"source": "move_to_wash_station", "target": "move_to_plate_4_b2"},
            {"source": "move_to_plate_4_b2", "target": "move_to_plate_5_b2"},
            {"source": "move_to_plate_5_b2", "target": "move_to_plate_6_b2"},
            {"source": "move_to_plate_6_b2", "target": "move_to_reactor"},
            {"source": "move_to_reactor", "target": "drop_tip"},
            {"source": "drop_tip", "target": "pickup_tip_2"},
            {"source": "pickup_tip_2", "target": "move_to_reactor_again"},
            {"source": "move_to_reactor_again", "target": "final_drop_tip"}
        ]
    }
    
    # Save the demo workflow to a temporary file
    temp_workflow_file = "demo_workflow.json"
    with open(temp_workflow_file, 'w') as f:
        json.dump(demo_workflow, f, indent=2)
    
    LOGGER.info(f"Saved demo workflow to {temp_workflow_file}")
    
    # Create the workflow executor
    LOGGER.info(f"Creating WorkflowExecutor with demo workflow file: {temp_workflow_file}")
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
            ot2_ip = "100.67.89.154"  # Default IP
        
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
    LOGGER.info("Executing demo workflow...")
    result = executor.execute_workflow()
    
    # Clean up the temporary file
    try:
        os.remove(temp_workflow_file)
        LOGGER.info(f"Removed temporary workflow file: {temp_workflow_file}")
    except Exception as e:
        LOGGER.warning(f"Failed to remove temporary workflow file: {str(e)}")
    
    if result:
        LOGGER.info("Demo workflow executed successfully")
        print("\nDemo Workflow Execution: ✓")
        print("Demo workflow executed successfully!")
        return True
    else:
        LOGGER.error("Demo workflow execution failed")
        print("\nDemo Workflow Execution: ✗")
        print("Demo workflow execution failed.")
        print("\nTroubleshooting Tips:")
        print("- Check if all devices are properly connected")
        print("- Verify the OT-2 IP address and Arduino port are correct")
        print("- Make sure the workflow file is valid")
        print("- Check the log file for detailed error messages")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a demo workflow with extensive OT-2 head movements")
    parser.add_argument("--ip", type=str, help="IP address of the OT-2 robot")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino")
    args = parser.parse_args()
    
    success = run_demo_workflow(args.ip, args.port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
