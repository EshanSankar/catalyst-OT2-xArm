#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Workflow Runner

This script runs a workflow using only the standard labware that we know works.
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
        logging.FileHandler("workflow_final.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowFinal")

def run_workflow_final(workflow_file: str, robot_ip: str = None, arduino_port: str = None):
    """Run a workflow using only the standard labware that we know works."""
    # Import necessary modules
    from workflow_executor import WorkflowExecutor

    # Load the workflow
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        LOGGER.error(f"Failed to load workflow file: {str(e)}")
        return False

    # Create a new workflow with only standard labware that we know works
    LOGGER.info("Creating a new workflow with only standard labware that we know works...")

    final_workflow = {
        "name": "Extensive Movement Workflow",
        "version": "1.0.0",
        "description": "A workflow with extensive OT-2 head movements for video content",
        "global_config": {
            "labware": {
                "tip_rack_1": {
                    "type": "opentrons_96_tiprack_1000ul",
                    "slot": 1
                },
                "tip_rack_2": {
                    "type": "opentrons_96_tiprack_1000ul",
                    "slot": 2
                },
                "tip_rack_3": {
                    "type": "opentrons_96_tiprack_1000ul",
                    "slot": 3
                },
                "plate_4": {
                    "type": "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
                    "slot": 4
                },
                "plate_5": {
                    "type": "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
                    "slot": 5
                },
                "plate_6": {
                    "type": "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
                    "slot": 6
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
                            "labware": "tip_rack_1",
                            "well": "A1"
                        }
                    ]
                }
            },
            {
                "id": "move_to_rack_2_a1",
                "type": "OCV",
                "label": "Move to Rack 2 A1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "tip_rack_2",
                            "well": "A1",
                            "offset": {
                                "z": 20
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_rack_2_h12",
                "type": "OCV",
                "label": "Move to Rack 2 H12",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "tip_rack_2",
                            "well": "H12",
                            "offset": {
                                "z": 20
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_rack_3_a1",
                "type": "OCV",
                "label": "Move to Rack 3 A1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "tip_rack_3",
                            "well": "A1",
                            "offset": {
                                "z": 20
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_rack_3_h12",
                "type": "OCV",
                "label": "Move to Rack 3 H12",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "tip_rack_3",
                            "well": "H12",
                            "offset": {
                                "z": 20
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_4_a1",
                "type": "CVA",
                "label": "Move to Plate 4 A1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "plate_4",
                            "well": "A1",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_4_d6",
                "type": "CVA",
                "label": "Move to Plate 4 D6",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "plate_4",
                            "well": "D6",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_5_a1",
                "type": "PEIS",
                "label": "Move to Plate 5 A1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "plate_5",
                            "well": "A1",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_5_d6",
                "type": "PEIS",
                "label": "Move to Plate 5 D6",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "plate_5",
                            "well": "D6",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_6_a1",
                "type": "LSV",
                "label": "Move to Plate 6 A1",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "plate_6",
                            "well": "A1",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_6_d6",
                "type": "LSV",
                "label": "Move to Plate 6 D6",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "move_to",
                            "labware": "plate_6",
                            "well": "D6",
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
                            "labware": "tip_rack_1",
                            "well": "A1"
                        },
                        {
                            "action": "drop_tip",
                            "labware": "tip_rack_1",
                            "well": "A1"
                        }
                    ]
                }
            },
            {
                "id": "pickup_tip_2",
                "type": "OCV",
                "label": "Pick Up Tip from Rack 2",
                "params": {
                    "duration_s": 5,
                    "sample_rate": 1,
                    "arduino_control": {
                        "base0_temp": 25.0
                    },
                    "ot2_actions": [
                        {
                            "action": "pick_up_tip",
                            "labware": "tip_rack_2",
                            "well": "A1"
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_6_b2",
                "type": "OCV",
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
                            "labware": "plate_6",
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
                "type": "OCV",
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
                            "labware": "plate_5",
                            "well": "B2",
                            "offset": {
                                "z": 5
                            }
                        }
                    ]
                }
            },
            {
                "id": "move_to_plate_4_b2",
                "type": "OCV",
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
                            "labware": "plate_4",
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
                            "labware": "tip_rack_2",
                            "well": "A1"
                        },
                        {
                            "action": "drop_tip",
                            "labware": "tip_rack_2",
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
            {"source": "home_robot", "target": "pickup_tip_1"},
            {"source": "pickup_tip_1", "target": "move_to_rack_2_a1"},
            {"source": "move_to_rack_2_a1", "target": "move_to_rack_2_h12"},
            {"source": "move_to_rack_2_h12", "target": "move_to_rack_3_a1"},
            {"source": "move_to_rack_3_a1", "target": "move_to_rack_3_h12"},
            {"source": "move_to_rack_3_h12", "target": "move_to_plate_4_a1"},
            {"source": "move_to_plate_4_a1", "target": "move_to_plate_4_d6"},
            {"source": "move_to_plate_4_d6", "target": "move_to_plate_5_a1"},
            {"source": "move_to_plate_5_a1", "target": "move_to_plate_5_d6"},
            {"source": "move_to_plate_5_d6", "target": "move_to_plate_6_a1"},
            {"source": "move_to_plate_6_a1", "target": "move_to_plate_6_d6"},
            {"source": "move_to_plate_6_d6", "target": "drop_tip"},
            {"source": "drop_tip", "target": "pickup_tip_2"},
            {"source": "pickup_tip_2", "target": "move_to_plate_6_b2"},
            {"source": "move_to_plate_6_b2", "target": "move_to_plate_5_b2"},
            {"source": "move_to_plate_5_b2", "target": "move_to_plate_4_b2"},
            {"source": "move_to_plate_4_b2", "target": "final_drop_tip"}
        ]
    }

    # Save the final workflow to a temporary file
    temp_workflow_file = "final_workflow.json"
    with open(temp_workflow_file, 'w') as f:
        json.dump(final_workflow, f, indent=2)

    LOGGER.info(f"Saved final workflow to {temp_workflow_file}")

    # Create the workflow executor
    LOGGER.info(f"Creating WorkflowExecutor with final workflow file: {temp_workflow_file}")
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
    LOGGER.info("Executing final workflow...")
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
    parser = argparse.ArgumentParser(description="Run a workflow with only standard labware")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file (used only for reference)")
    parser.add_argument("--ip", type=str, help="IP address of the OT-2 robot")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino")
    args = parser.parse_args()

    success = run_workflow_final(args.workflow_file, args.ip, args.port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
