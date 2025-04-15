#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workflow Executor for OT-2 Robot

This script loads a workflow JSON file and executes each step in sequence.
It maps operations in the workflow to function calls using the appropriate classes.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import OT-2 and Arduino control classes
# Create a mock opentronsClient class for testing
class opentronsClient:
    def __init__(self, strRobotIP="100.67.89.154"):
        self.robot_ip = strRobotIP
        print(f"Connecting to OT-2 at {strRobotIP}...")

    def lights(self, state):
        print(f"Setting lights to {state}")

    def homeRobot(self):
        print("Homing robot")

    def loadLabware(self, intSlot, strLabwareName):
        print(f"Loading labware {strLabwareName} in slot {intSlot}")
        return f"{strLabwareName}_{intSlot}"

    def loadCustomLabware(self, dicLabware, intSlot):
        labware_name = dicLabware.get("metadata", {}).get("name", "custom_labware")
        print(f"Loading custom labware {labware_name} in slot {intSlot}")
        return f"{labware_name}_{intSlot}"

    def loadPipette(self, strPipetteName, strMount):
        print(f"Loading pipette {strPipetteName} on {strMount} mount")

    def moveToWell(self, strLabwareName, strWellName, strPipetteName, strOffsetStart, fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0, intSpeed=100):
        print(f"Moving {strPipetteName} to {strLabwareName} {strWellName} with offset {fltOffsetX}, {fltOffsetY}, {fltOffsetZ}")

    def pickUpTip(self, strLabwareName, strPipetteName, strWellName, fltOffsetX=0, fltOffsetY=0):
        print(f"Picking up tip from {strLabwareName} {strWellName}")

    def dropTip(self, strLabwareName, strPipetteName, strWellName, strOffsetStart="bottom", fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0):
        print(f"Dropping tip to {strLabwareName} {strWellName}")

    def aspirate(self, strLabwareName, strWellName, strPipetteName, intVolume, strOffsetStart, fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0):
        print(f"Aspirating {intVolume}µL from {strLabwareName} {strWellName}")

    def dispense(self, strLabwareName, strWellName, strPipetteName, intVolume, strOffsetStart, fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0):
        print(f"Dispensing {intVolume}µL to {strLabwareName} {strWellName}")

    def blowout(self, strLabwareName, strWellName, strPipetteName, strOffsetStart, fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0):
        print(f"Blowing out at {strLabwareName} {strWellName}")

# Create a mock Arduino class for testing
class Arduino:
    def __init__(self, arduinoPort="COM3"):
        self.port = arduinoPort
        print(f"Connecting to Arduino on port {arduinoPort}...")

    def setTemp(self, baseNumber, targetTemp):
        print(f"Setting base {baseNumber} temperature to {targetTemp}°C")

    def dispense_ml(self, pumpNumber, volume):
        print(f"Dispensing {volume}ml from pump {pumpNumber}")

    def setUltrasonicOnTimer(self, baseNumber, timeOn_ms):
        print(f"Running ultrasonic on base {baseNumber} for {timeOn_ms}ms")

# Try to import the real classes if available
try:
    # First try to import from opentronsHTTPAPI_clientBuilder.py
    from opentronsHTTPAPI_clientBuilder import opentronsClient as RealOpentronsClient
    opentronsClient = RealOpentronsClient
    print("Using real opentronsClient from opentronsHTTPAPI_clientBuilder.py")
except ImportError:
    try:
        # Then try to import from opentrons module
        from opentrons import opentronsClient as RealOpentronsClient
        opentronsClient = RealOpentronsClient
        print("Using real opentronsClient from opentrons module")
    except ImportError:
        print("Using mock opentronsClient for testing")

# Try to import the Arduino class from ot2-arduino.py
try:
    # Use importlib to import from a file with a hyphen in the name
    import importlib.util
    spec = importlib.util.spec_from_file_location("ot2_arduino", "ot2-arduino.py")
    arduino_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arduino_module)
    Arduino = arduino_module.Arduino
    print("Using real Arduino from ot2-arduino.py")
except Exception as e:
    print(f"Using mock Arduino for testing: {str(e)}")
    # This section is already handled above

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("workflow_execution.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("WorkflowExecutor")

class WorkflowExecutor:
    """
    Class for executing OT-2 workflows defined in JSON files.
    """

    def __init__(self, workflow_file: str):
        """
        Initialize the workflow executor.

        Args:
            workflow_file (str): Path to the workflow JSON file
        """
        self.workflow_file = workflow_file
        self.workflow = self._load_workflow(workflow_file)
        self.ot2_client = None
        self.arduino_client = None
        self.labware_ids = {}

        # Initialize operation dispatcher
        self.operation_dispatcher = {
            "pick_up_tip": self._execute_pick_up_tip,
            "drop_tip": self._execute_drop_tip,
            "move_to": self._execute_move_to,
            "wash": self._execute_wash,
            "home": self._execute_home
        }

        LOGGER.info(f"Workflow Executor initialized with workflow: {workflow_file}")

    def _load_workflow(self, workflow_file: str) -> Dict[str, Any]:
        """Load workflow from JSON file."""
        try:
            with open(workflow_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            LOGGER.error(f"Failed to load workflow from {workflow_file}: {str(e)}")
            return {}

    def connect_devices(self) -> bool:
        """Connect to OT-2 and Arduino devices."""
        try:
            # Connect to OT-2
            robot_ip = self.workflow.get("global_config", {}).get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
            LOGGER.info(f"Connecting to OT-2 at {robot_ip}...")
            self.ot2_client = opentronsClient(strRobotIP=robot_ip)
            LOGGER.info("Connected to OT-2")

            # Connect to Arduino
            LOGGER.info("Connecting to Arduino...")
            self.arduino_client = Arduino()
            LOGGER.info("Connected to Arduino")

            return True
        except Exception as e:
            LOGGER.error(f"Failed to connect to devices: {str(e)}")
            return False

    def setup_labware(self) -> bool:
        """Set up labware on the OT-2 robot."""
        try:
            # Load labware from global config
            labware_config = self.workflow.get("global_config", {}).get("labware", {})

            for labware_name, labware_info in labware_config.items():
                labware_type = labware_info.get("type")
                slot = labware_info.get("slot")

                LOGGER.info(f"Loading labware: {labware_name} ({labware_type}) in slot {slot}")

                # Check if it's a standard labware or custom labware
                if labware_type.startswith("opentrons_"):
                    # Standard Opentrons labware
                    self.labware_ids[labware_name] = self.ot2_client.loadLabware(
                        intSlot=slot,
                        strLabwareName=labware_type
                    )
                else:
                    # Custom labware - load from JSON file or use mock labware
                    custom_labware_path = os.path.join(os.getcwd(), 'labware', f"{labware_type}.json")

                    try:
                        with open(custom_labware_path, 'r', encoding='utf-8') as f:
                            custom_labware = json.load(f)

                        self.labware_ids[labware_name] = self.ot2_client.loadCustomLabware(
                            dicLabware=custom_labware,
                            intSlot=slot
                        )
                    except FileNotFoundError:
                        # If the custom labware file is not found, create a mock labware ID
                        LOGGER.warning(f"Custom labware file for {labware_type} not found. Using mock labware.")
                        self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                    except Exception as e:
                        LOGGER.error(f"Failed to load custom labware {labware_type}: {str(e)}")
                        return False

            # Load pipettes from global config
            pipette_config = self.workflow.get("global_config", {}).get("instruments", {}).get("pipette", {})
            pipette_type = pipette_config.get("type")
            mount = pipette_config.get("mount")

            LOGGER.info(f"Loading pipette: {pipette_type} on {mount} mount")
            self.ot2_client.loadPipette(
                strPipetteName=pipette_type,
                strMount=mount
            )

            return True
        except Exception as e:
            LOGGER.error(f"Failed to set up labware: {str(e)}")
            return False

    def execute_workflow(self) -> bool:
        """Execute the workflow."""
        try:
            # Connect to devices
            if not self.connect_devices():
                return False

            # Set up labware
            if not self.setup_labware():
                return False

            # Turn on the lights
            self.ot2_client.lights(True)

            # Home the robot
            self.ot2_client.homeRobot()

            # Get the nodes and edges from the workflow
            nodes = self.workflow.get("nodes", [])
            edges = self.workflow.get("edges", [])

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

            # Find the starting node (node with no incoming edges)
            starting_nodes = []
            all_targets = [edge.get("target") for edge in edges]
            for node in nodes:
                if node["id"] not in all_targets:
                    starting_nodes.append(node["id"])

            if not starting_nodes:
                LOGGER.error("No starting node found in the workflow")
                return False

            # Execute the workflow starting from the starting node
            for starting_node_id in starting_nodes:
                self._execute_node(starting_node_id, node_map, children_map)

            LOGGER.info("Workflow execution completed successfully")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to execute workflow: {str(e)}")
            return False

    def _execute_node(self, node_id: str, node_map: Dict[str, Dict[str, Any]], children_map: Dict[str, List[str]]) -> None:
        """Execute a node and its children."""
        # Get the node
        node = node_map.get(node_id)
        if not node:
            LOGGER.error(f"Node {node_id} not found in the workflow")
            return

        LOGGER.info(f"Executing node: {node_id} ({node.get('label')})")

        # Execute OT-2 actions
        ot2_actions = node.get("params", {}).get("ot2_actions", [])
        for action in ot2_actions:
            self._execute_action(action)

        # Execute Arduino control
        arduino_control = node.get("params", {}).get("arduino_control", {})
        if arduino_control:
            self._execute_arduino_control(arduino_control)

        # Execute children nodes
        children = children_map.get(node_id, [])
        for child_id in children:
            self._execute_node(child_id, node_map, children_map)

    def _execute_action(self, action: Dict[str, Any]) -> None:
        """Execute an OT-2 action."""
        action_type = action.get("action")
        if action_type in self.operation_dispatcher:
            self.operation_dispatcher[action_type](action)
        else:
            LOGGER.error(f"Unknown action type: {action_type}")

    def _execute_pick_up_tip(self, action: Dict[str, Any]) -> None:
        """Execute pick_up_tip action."""
        labware = action.get("labware")
        well = action.get("well")
        offset_x = action.get("offset", {}).get("x", 0)
        offset_y = action.get("offset", {}).get("y", 0)
        offset_z = action.get("offset", {}).get("z", 0)

        LOGGER.info(f"Picking up tip from {labware} {well}")

        # Move to the tip rack
        self.ot2_client.moveToWell(
            strLabwareName=self.labware_ids.get(labware),
            strWellName=well,
            strPipetteName="p1000_single_gen2",
            strOffsetStart="top",
            fltOffsetX=offset_x,
            fltOffsetY=offset_y,
            fltOffsetZ=offset_z,
            intSpeed=100
        )

        # Pick up the tip
        self.ot2_client.pickUpTip(
            strLabwareName=self.labware_ids.get(labware),
            strPipetteName="p1000_single_gen2",
            strWellName=well,
            fltOffsetX=offset_x,
            fltOffsetY=offset_y
        )

    def _execute_drop_tip(self, action: Dict[str, Any]) -> None:
        """Execute drop_tip action."""
        labware = action.get("labware")
        well = action.get("well")
        offset_x = action.get("offset", {}).get("x", 0)
        offset_y = action.get("offset", {}).get("y", 0)
        offset_z = action.get("offset", {}).get("z", 0)

        LOGGER.info(f"Dropping tip to {labware} {well}")

        # Move to the tip rack
        self.ot2_client.moveToWell(
            strLabwareName=self.labware_ids.get(labware),
            strWellName=well,
            strPipetteName="p1000_single_gen2",
            strOffsetStart="top",
            fltOffsetX=offset_x,
            fltOffsetY=offset_y,
            fltOffsetZ=offset_z,
            intSpeed=100
        )

        # Drop the tip
        self.ot2_client.dropTip(
            strLabwareName=self.labware_ids.get(labware),
            strPipetteName="p1000_single_gen2",
            strWellName=well,
            strOffsetStart="bottom",
            fltOffsetX=offset_x,
            fltOffsetY=offset_y,
            fltOffsetZ=offset_z
        )

    def _execute_move_to(self, action: Dict[str, Any]) -> None:
        """Execute move_to action."""
        labware = action.get("labware")
        well = action.get("well")
        offset_x = action.get("offset", {}).get("x", 0)
        offset_y = action.get("offset", {}).get("y", 0)
        offset_z = action.get("offset", {}).get("z", 0)

        LOGGER.info(f"Moving to {labware} {well}")

        # Move to the well
        self.ot2_client.moveToWell(
            strLabwareName=self.labware_ids.get(labware),
            strWellName=well,
            strPipetteName="p1000_single_gen2",
            strOffsetStart="top",
            fltOffsetX=offset_x,
            fltOffsetY=offset_y,
            fltOffsetZ=offset_z,
            intSpeed=100
        )

    def _execute_wash(self, action: Dict[str, Any]) -> None:
        """Execute wash action."""
        arduino_actions = action.get("arduino_actions", {})

        LOGGER.info("Executing wash action")

        # Execute Arduino actions
        for pump_name, volume in arduino_actions.items():
            if pump_name == "pump0_ml" and volume > 0:
                LOGGER.info(f"Dispensing {volume}ml from pump 0 (water)")
                self.arduino_client.dispense_ml(pumpNumber=0, volume=volume)
            elif pump_name == "pump1_ml" and volume > 0:
                LOGGER.info(f"Dispensing {volume}ml from pump 1 (acid)")
                self.arduino_client.dispense_ml(pumpNumber=1, volume=volume)
            elif pump_name == "pump2_ml" and volume > 0:
                LOGGER.info(f"Dispensing {volume}ml from pump 2 (waste)")
                self.arduino_client.dispense_ml(pumpNumber=2, volume=volume)
            elif pump_name == "ultrasonic0_ms" and volume > 0:
                LOGGER.info(f"Running ultrasonic for {volume}ms")
                self.arduino_client.setUltrasonicOnTimer(0, volume)

    def _execute_home(self, action: Dict[str, Any]) -> None:
        """Execute home action."""
        LOGGER.info("Homing the robot")
        # action parameter is not used but kept for consistency with other methods
        self.ot2_client.homeRobot()

    def _execute_arduino_control(self, arduino_control: Dict[str, Any]) -> None:
        """Execute Arduino control actions."""
        base0_temp = arduino_control.get("base0_temp")
        pump0_ml = arduino_control.get("pump0_ml")
        ultrasonic0_ms = arduino_control.get("ultrasonic0_ms")

        if base0_temp:
            LOGGER.info(f"Setting base 0 temperature to {base0_temp}°C")
            self.arduino_client.setTemp(0, base0_temp)

        if pump0_ml and pump0_ml > 0:
            LOGGER.info(f"Dispensing {pump0_ml}ml from pump 0")
            self.arduino_client.dispense_ml(pumpNumber=0, volume=pump0_ml)

        if ultrasonic0_ms and ultrasonic0_ms > 0:
            LOGGER.info(f"Running ultrasonic for {ultrasonic0_ms}ms")
            self.arduino_client.setUltrasonicOnTimer(0, ultrasonic0_ms)

if __name__ == "__main__":
    # Check if a workflow file is provided
    if len(sys.argv) < 2:
        print("Usage: python workflow_executor.py <workflow_json_file>")
        sys.exit(1)

    workflow_file = sys.argv[1]
    print(f"Loading workflow file: {workflow_file}")

    try:
        # Load the workflow file to check its structure
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
            print(f"Workflow file loaded successfully. Structure: {list(workflow_data.keys())}")
            if 'global_config' in workflow_data:
                print(f"Global config keys: {list(workflow_data['global_config'].keys())}")
            if 'nodes' in workflow_data:
                print(f"Number of nodes: {len(workflow_data['nodes'])}")
                for i, node in enumerate(workflow_data['nodes'][:3]):
                    print(f"Node {i}: {node.get('id')} - {node.get('label')}")
            if 'edges' in workflow_data:
                print(f"Number of edges: {len(workflow_data['edges'])}")

        # Create and run the workflow executor
        executor = WorkflowExecutor(workflow_file)
        print("Workflow executor created successfully")

        if executor.execute_workflow():
            print("Workflow executed successfully")
            sys.exit(0)
        else:
            print("Workflow execution failed")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
