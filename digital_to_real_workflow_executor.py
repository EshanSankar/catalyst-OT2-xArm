#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workflow Executor for OT2 Robot

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

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int8
from sensor_msgs.msg import JointState

# Import OT2 and Arduino control classes
# Create a mock opentronsClient class for testing
class opentronsClient:
    def __init__(self, strRobotIP="169.254.197.90"):
        self.robot_ip = strRobotIP
        print(f"Connecting to OT2 at {strRobotIP}...")

    def lights(self, state):
        print(f"Setting lights to {state}")

    def homeRobot(self):
        print("Homing OT2")

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

# Don't need to do anything for xArm

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

# Don't need to import anything for xArm

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

class WorkflowExecutor(Node):
    """
    Class for executing OT2 workflows defined in JSON files.

    This class supports two execution modes:
    1. Direct execution (legacy mode)
    2. Prefect-based execution (new mode)
    """

    def __init__(self, workflow_file: str, use_prefect: bool = False, mock_mode: bool = False):
        """
        Initialize the workflow executor.

        Args:
            workflow_file (str): Path to the workflow JSON file
            use_prefect (bool): Whether to use Prefect for workflow execution
            mock_mode (bool): Whether to use mock mode (no real devices)
        """
        super().__init__("workflow_executor")
        # We don't need self.publisher_ot2 for the real thing
        self.publisher_digital_ot2 = self.create_publisher(JointState, "/sim_ot2/target_joint_states", 10)
        self.publisher_digital_xarm = self.create_publisher(JointState, "/sim_xarm/target_joint_states", 10)
        self.publisher_xarm = self.create_publisher(String, "/orchestrator/xarm/action", 10)
        self.publisher_target_asset_ot2 = self.create_publisher(String, "/sim_ot2/target_asset")
        self.publisher_target_asset_xarm = self.create_publisher(String, "/sim_xarm/target_asset")
        self.workflow_file = workflow_file
        self.workflow = self._load_workflow(workflow_file)
        self.ot2_client = None
        self.arduino_client = None
        self.labware_ids = {}
        self.use_prefect = use_prefect
        self.mock_mode = mock_mode
        self.prefect_executor = None
        
        self.LABWARE_SLOTS = {}
        self.LABWARE_TYPES = {}

        self.XARM_JOINTS = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]
        self.XARM_GRIPPER = ["left_finger", "right_finger"]
        self.prev_gripper_position = 500
        self.state, self.state_resolution = 1, 0
        # 1 = continue with next action; 0 = continue with current action, -1 = don't continue
        self.state_sub = self.create_subscription(Int8, "safety_checker/status_int", self.state_cb, 10)
        self.OT2_COORDS = {
            1: (0.0, 0.0), 2: (0.13, 0.0), 3: (0.26, 0.0),
            4: (0.0, 0.09), 5: (0.13, 0.09), 6: (0.26, 0.09),
            7: (0.0, 0.18), 8: (0.13, 0.18), 9: (0.26, 0.18),
            10: (0.0, 0.27), 11: (0.13, 0.27), 12: (0.26, 0.27)}
        self.OT2_JOINTS = ["PrismaticJointMiddleBar", "PrismaticJointPipetteHolder", "PrismaticJointRightPipette"]

        # Initialize operation dispatchers
        self.operation_dispatcher_digital_ot2 = {
            #"pick_up_tip": self._execute_pick_up_tip_digital_ot2,
            #"drop_tip": self._execute_drop_tip_digital_ot2,
            "move_to": self._execute_move_to_digital_ot2#,
            #"wash": self._execute_wash_digital_ot2,
            #"home": self._execute_home_digital_ot2
        }
        self.operation_dispatcher_ot2 = {
            "pick_up_tip": self._execute_pick_up_tip_ot2,
            "drop_tip": self._execute_drop_tip_ot2,
            "move_to": self._execute_move_to_ot2,
            "wash": self._execute_wash_ot2,
            "home": self._execute_home_ot2
        }

        self.operation_dispatcher_digital_xarm = {
            #"set_position": self._execute_set_position_digital_xarm,
            "set_servo_angle": self._execute_set_servo_angle_digital_xarm
        }
        self.operation_dispatcher_xarm = {
            #"set_position": self._execute_set_position_xarm,
            "set_servo_angle": self._execute_set_servo_angle_xarm
        }

        # Initialize Prefect executor if needed
        if self.use_prefect:
            try:
                from prefect_workflow_executor import PrefectWorkflowExecutor
                self.prefect_executor = PrefectWorkflowExecutor(
                    workflow_file=workflow_file,
                    mock_mode=mock_mode
                )
                LOGGER.info("Prefect workflow executor initialized")
            except ImportError as e:
                LOGGER.error(f"Failed to import Prefect workflow executor: {str(e)}")
                LOGGER.warning("Falling back to direct execution mode")
                self.use_prefect = False

        LOGGER.info(f"Workflow Executor initialized with workflow: {workflow_file} (Prefect: {self.use_prefect}, Mock: {self.mock_mode})")

    def _load_workflow(self, workflow_file: str) -> Dict[str, Any]:
        """Load workflow from JSON file."""
        try:
            with open(workflow_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            LOGGER.error(f"Failed to load workflow from {workflow_file}: {str(e)}")
            return {}

    def connect_devices(self) -> bool:
        """Connect to OT2, xArm, and Arduino devices."""
        success = True

        try:
            # Connect to OT2
            robot_ip = self.workflow.get("global_config", {}).get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
            LOGGER.info(f"Connecting to OT2 at {robot_ip}...")
            self.ot2_client = opentronsClient(strRobotIP=robot_ip)
            LOGGER.info("Connected to OT2")
        except Exception as e:
            LOGGER.error(f"Failed to connect to OT2: {str(e)}")
            success = False
        # try:
        #     # Enable xArm
        #     LOGGER.info(f"Enabling xArm")
        #     self.publisher_xarm.publish(String(data="motion_enable"))
        #     time.sleep(3)
        #     self.publisher_xarm.publish(String(data="set_mode"))
        #     time.sleep(3)
        #     self.publisher_xarm.publish(String(data="set_state"))
        #     time.sleep(3)
        #     LOGGER.info("Enabled xArm")
        # except Exception as e:
        #     LOGGER.error(f"Failed to enable xArm: {str(e)}")
        #     success = False
        try:
            # Connect to Arduino
            LOGGER.info("Connecting to Arduino...")
            self.arduino_client = Arduino()
            LOGGER.info("Connected to Arduino")
        except Exception as e:
            LOGGER.warning(f"Failed to connect to Arduino: {str(e)}")
            LOGGER.warning("Some functionality may be limited")
            # Don't set success to False here, as we can still proceed without Arduino
        time.sleep(3)
        return success

    def setup_labware(self) -> bool:
        """Set up labware on the OT2 robot."""
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
                    try:
                        labware_id = self.ot2_client.loadLabware(
                            intSlot=slot,
                            strLabwareName=labware_type
                        )

                        # Check if the labware_id is a valid string
                        if isinstance(labware_id, str) and labware_id:
                            self.labware_ids[labware_name] = labware_id
                            LOGGER.info(f"Successfully loaded standard labware {labware_type} in slot {slot} with ID: {labware_id}")
                            self.LABWARE_SLOTS[labware_name] = slot
                            self.LABWARE_TYPES[labware_name] = labware_type
                            LOGGER.info(f"Labware {labware_name} is assigned to slot {slot}")
                        else:
                            # If the labware_id is not valid, use a mock ID
                            self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                            LOGGER.warning(f"Invalid labware ID returned. Using mock labware ID: {self.labware_ids[labware_name]}")
                    except Exception as e:
                        # If there's an exception, use a mock ID
                        self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                        LOGGER.warning(f"Exception loading standard labware. Using mock labware ID: {self.labware_ids[labware_name]}")
                        LOGGER.debug(f"Exception details: {str(e)}")
                else:
                    # Custom labware - load from JSON file or use mock labware
                    custom_labware_path = os.path.join(os.getcwd(), 'labware', f"{labware_type}.json")
                    LOGGER.info(f"Looking for custom labware at: {custom_labware_path}")

                    if os.path.exists(custom_labware_path):
                        try:
                            with open(custom_labware_path, 'r', encoding='utf-8') as f:
                                custom_labware = json.load(f)

                            LOGGER.info(f"Successfully loaded custom labware definition from {custom_labware_path}")
                            try:
                                # Load custom labware
                                try:
                                    labware_id = self.ot2_client.loadCustomLabware(
                                        dicLabware=custom_labware,
                                        intSlot=slot
                                    )

                                    # Check if the labware_id is a valid string
                                    if isinstance(labware_id, str) and labware_id:
                                        self.labware_ids[labware_name] = labware_id
                                        LOGGER.info(f"Successfully loaded custom labware {labware_type} in slot {slot} with ID: {labware_id}")
                                        self.LABWARE_SLOTS[labware_name] = slot
                                        self.LABWARE_TYPES[labware_name] = labware_type
                                        LOGGER.info(f"Labware {labware_name} is assigned to slot {slot}")
                                    else:
                                        # If the labware_id is not valid, use a mock ID
                                        self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                                        LOGGER.warning(f"Invalid labware ID returned. Using mock labware ID: {self.labware_ids[labware_name]}")
                                except Exception as e:
                                    # If there's an exception, use a mock ID
                                    import traceback
                                    LOGGER.error(f"Exception loading custom labware: {e}")
                                    LOGGER.error(traceback.format_exc())
                                    self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                                    LOGGER.warning(f"Exception loading custom labware. Using mock labware ID: {self.labware_ids[labware_name]}")
                                    LOGGER.debug(f"Exception details: {str(e)}")
                            except Exception as e:
                                LOGGER.error(f"Failed to load custom labware {labware_type} in slot {slot}: {str(e)}")
                                # Fall back to mock labware
                                self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                                LOGGER.warning(f"Using mock labware ID: {self.labware_ids[labware_name]}")
                        except Exception as e:
                            LOGGER.error(f"Failed to parse custom labware file {custom_labware_path}: {str(e)}")
                            # Fall back to mock labware
                            self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                            LOGGER.warning(f"Using mock labware ID: {self.labware_ids[labware_name]}")
                    else:
                        # If the custom labware file is not found, create a mock labware ID
                        LOGGER.warning(f"Custom labware file for {labware_type} not found at {custom_labware_path}. Using mock labware.")
                        self.labware_ids[labware_name] = f"{labware_type}_{slot}"
                        LOGGER.warning(f"Using mock labware ID: {self.labware_ids[labware_name]}")

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

    def state_cb(self, msg) -> None:
        self.state = int(msg.data)
        print(self.state)

    def execute_workflow(self) -> bool:
        """
        Execute the workflow.

        Returns:
            bool: True if execution was successful, False otherwise
        """
        # If using Prefect, delegate to the Prefect executor
        if self.use_prefect and self.prefect_executor:
            LOGGER.info("Executing workflow using Prefect")
            try:
                result = self.prefect_executor.execute()
                if result["status"] == "success":
                    LOGGER.info("Prefect workflow execution completed successfully")
                    return True
                else:
                    LOGGER.error(f"Prefect workflow execution failed: {result.get('message', 'Unknown error')}")
                    return False
            except Exception as e:
                LOGGER.error(f"Failed to execute workflow with Prefect: {str(e)}")
                LOGGER.warning("Falling back to direct execution mode")
                # Fall back to direct execution
                self.use_prefect = False

        # Direct execution (legacy mode)
        LOGGER.info("Executing workflow using direct execution mode")
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
            #self.publisher_xarm.publish(String(data="set_servo_angle 2.865 -0.0861 -0.4979 4.3559 1.318 1.021 0 100 500 0 False"))

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

        # Execute OT2 actions
        ot2_actions = node.get("params", {}).get("ot2_actions", [])
        for action in ot2_actions:
            if node_id == "0":
                self._execute_action_ot2(action)
                continue
            self._execute_action_digital_ot2(action)
            time.sleep(0.1)
            self.state = 0
            while self.state != 1:
                rclpy.spin_once(self, timeout_sec=0.1)
                if self.state == 1:
                    self.state_resolution = 1
                    break
                elif self.state == -1:
                    LOGGER.error("Digital OT2 UNSAFE!")
                else:
                    LOGGER.info("Digital OT2 moving...")
            if self.state_resolution == 1:
                LOGGER.info("Continuing next OT2 action...")
                self.state_resolution = 0
                continue
            LOGGER.info("Continuing current OT2 action...")
            self._execute_action_ot2(action)            
        
        # Execute xArm actions
        xarm_actions = node.get("params", {}).get("xarm_actions", [])
        for action in xarm_actions:
            if node_id == "0":
                self._execute_action_xarm(action)
                continue
            self._execute_action_digital_xarm(action)
            self.state = 0
            while self.state != 1:
                rclpy.spin_once(self, timeout_sec=0.01)
                if self.state == 1:
                    self.state_resolution = 1
                    break
                elif self.state == -1:
                    LOGGER.error("Digital xArm UNSAFE!")
                else:
                    LOGGER.info("Digital xArm moving...")
            if self.state_resolution == 1:
                LOGGER.info("Continuing next xArm action...")
                self.state_resolution = 0
                continue
            LOGGER.info("Continuing current xArm action...")
            self._execute_action_xarm(action)            

        # Execute Arduino control
        arduino_control = node.get("params", {}).get("arduino_control", {})
        if arduino_control:
            self._execute_arduino_control(arduino_control)

        # Execute children nodes
        children = children_map.get(node_id, [])
        for child_id in children:
            self._execute_node(child_id, node_map, children_map)

    def _execute_action_digital_ot2(self, action: Dict[str, Any]) -> None:
        """Execute a digital OT2 action."""
        action_type = action.get("action")
        if action_type in self.operation_dispatcher_digital_ot2:
            self.operation_dispatcher_digital_ot2[action_type](action)
        else:
            LOGGER.error(f"Unknown digital OT2 action type: {action_type}")

    def _execute_action_ot2(self, action: Dict[str, Any]) -> None:
        """Execute an OT2 action."""
        action_type = action.get("action")
        if action_type in self.operation_dispatcher_ot2:
            self.operation_dispatcher_ot2[action_type](action)
        else:
            LOGGER.error(f"Unknown OT2 action type: {action_type}")

    def _execute_action_ot2(self, action: Dict[str, Any]) -> None:
        """Execute an OT2 action."""
        action_type = action.get("action")
        if action_type in self.operation_dispatcher_ot2:
            self.operation_dispatcher_ot2[action_type](action)
        else:
            LOGGER.error(f"Unknown OT2 action type: {action_type}")

    def _execute_pick_up_tip_ot2(self, action: Dict[str, Any]) -> None:
        """Execute pick_up_tip action."""
        labware = action.get("labware")
        well = action.get("well")
        offset_x = action.get("offset", {}).get("x", 0)
        offset_y = action.get("offset", {}).get("y", 0)
        offset_z = action.get("offset", {}).get("z", 0)

        LOGGER.info(f"Picking up tip from {labware} {well}")

        # Check if the labware exists
        if labware not in self.labware_ids:
            LOGGER.error(f"Labware {labware} not found in labware_ids")
            LOGGER.info(f"Available labware: {list(self.labware_ids.keys())}")
            LOGGER.warning(f"Skipping pick_up_tip action for {labware} {well}")
            return

        # Move to the tip rack
        try:
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
            self.ot2_client.current_labware = labware
        except Exception as e:
            LOGGER.error(f"Failed to pick up tip: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return

    def _execute_drop_tip_ot2(self, action: Dict[str, Any]) -> None:
        """Execute drop_tip action."""
        labware = action.get("labware")
        well = action.get("well")
        offset_x = action.get("offset", {}).get("x", 0)
        offset_y = action.get("offset", {}).get("y", 0)
        offset_z = action.get("offset", {}).get("z", 0)

        LOGGER.info(f"Dropping tip to {labware} {well}")

        # Check if the labware exists
        if labware not in self.labware_ids:
            LOGGER.error(f"Labware {labware} not found in labware_ids")
            LOGGER.info(f"Available labware: {list(self.labware_ids.keys())}")
            LOGGER.warning(f"Skipping drop_tip action for {labware} {well}")
            return

        # Move to the tip rack
        try:
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
            self.ot2_client.current_labware = labware
        except Exception as e:
            LOGGER.error(f"Failed to drop tip: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return

    def _execute_move_to_digital_ot2(self, action: Dict[str, Any]) -> None:
        """Execute move_to action."""
        labware = action.get("labware")
        well = action.get("well")
        offset_x = action.get("offset", {}).get("x", 0)
        offset_y = action.get("offset", {}).get("y", 0)
        offset_z = action.get("offset", {}).get("z", 0)

        LOGGER.info(f"Moving to {labware} {well}")

        # Check if the labware exists
        if labware not in self.labware_ids:
            LOGGER.error(f"Labware {labware} not found in labware_ids")
            LOGGER.info(f"Available labware: {list(self.labware_ids.keys())}")
            LOGGER.warning(f"Skipping move_to action for {labware} {well}")
            return

        try:
            slot = self.LABWARE_SLOTS.get(labware)
            labware_type = self.LABWARE_TYPES.get(labware)
            # Compute exact joint states based on labware .json and coordinate transformations
            cell_coords = self.OT2_COORDS[slot]
            well_x, well_y, well_z = 0.0, 0.0, 0.0
            with open(f"labware/{labware_type}.json", "r") as f:
                lw = json.load(f)
                for coord, _ in lw["wells"][well]:
                    well_x, well_y, well_z = coord["x"], coord["y"], coord["z"] # TODO: need to fix well_z?
            computed_joint_states = [(cell_coords[0] + offset_x + well_x) / 150 - 0.08,
                                     (cell_coords[1] + offset_y + well_y) / 150 - 0.08,
                                     ((offset_z + well_z)/ 150 - 0.08) * -1]
            msg = JointState(name=self.OT2_JOINTS,
                             position=[computed_joint_states[0], computed_joint_states[1], computed_joint_states[2]])
            self.publisher_target_asset_ot2.publish(String(data=labware))
            self.publisher_digital_ot2.publish(msg)
        except Exception as e:
            LOGGER.error(f"Failed to move to well: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return
    
    def _execute_move_to_ot2(self, action: Dict[str, Any]) -> None:
        """Execute move_to action."""
        labware = action.get("labware")
        well = action.get("well")
        offset_x = action.get("offset", {}).get("x", 0)
        offset_y = action.get("offset", {}).get("y", 0)
        offset_z = action.get("offset", {}).get("z", 0)

        LOGGER.info(f"Moving to {labware} {well}")

        # Check if the labware exists
        if labware not in self.labware_ids:
            LOGGER.error(f"Labware {labware} not found in labware_ids")
            LOGGER.info(f"Available labware: {list(self.labware_ids.keys())}")
            LOGGER.warning(f"Skipping move_to action for {labware} {well}")
            return

        # Move to the well
        try:
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
            self.ot2_client.current_labware = labware
        except Exception as e:
            LOGGER.error(f"Failed to move to well: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return

    def _execute_wash_ot2(self, action: Dict[str, Any]) -> None:
        """Execute wash action."""
        arduino_actions = action.get("arduino_actions", {})

        LOGGER.info("Executing wash action")

        # Check if Arduino client is available
        if not hasattr(self, 'arduino_client') or self.arduino_client is None:
            LOGGER.warning("Arduino client not available. Skipping wash action.")
            return

        # Execute Arduino actions
        try:
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
        except Exception as e:
            LOGGER.error(f"Failed to execute wash action: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return

    def _execute_home_ot2(self, action: Dict[str, Any]) -> None:
        """Execute home action."""
        LOGGER.info("Homing the OT2")
        # action parameter is not used but kept for consistency with other methods
        try:
            self.ot2_client.homeRobot()
        except Exception as e:
            LOGGER.error(f"Failed to home OT2: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return
        
    def _execute_action_digital_xarm(self, action: Dict[str, Any]) -> None:
        """Execute a digital xArm action."""
        action_type = action.get("action")
        if action_type in self.operation_dispatcher_digital_xarm:
            self.operation_dispatcher_digital_xarm[action_type](action)
        else:
            LOGGER.error(f"Unknown digital xArm action type: {action_type}")
    
    def _execute_action_xarm(self, action: Dict[str, Any]) -> None:
        """Execute an xArm action."""
        action_type = action.get("action")
        if action_type in self.operation_dispatcher_xarm:
            self.operation_dispatcher_xarm[action_type](action)
        else:
            LOGGER.error(f"Unknown xArm action type: {action_type}")
    
    def _execute_set_position_xarm(self, action: Dict[str, Any]) -> None:
        """Execute xArm motion_enable."""
        pose = action.get("pose", [])
        speed = action.get("speed", 100)
        acc = action.get("acc", 500)
        mvtime = action.get("mvtime", 0)
        LOGGER.info(f"Moving xArm to position: {pose} with speed {speed}, acc {acc}, mvtime {mvtime}")
        try:
            self.publisher_xarm.publish(String(data=f"set_position {pose[0]} {pose[1]} {pose[2]} {pose[3]} {pose[4]} {pose[5]} {speed} {acc} {mvtime}"))
        except Exception as e:
            LOGGER.error(f"Failed to set xArm position: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return
    
    def _execute_set_servo_angle_digital_xarm(self, action: Dict[str, Any]) -> None:
        """Execute xArm set_servo_angle (digital)."""
        angles = action.get("angles", [])
        speed = action.get("speed", 100)
        acc = action.get("acc", 500)
        mvtime = action.get("mvtime", 0)
        relative = action.get("relative", True)
        LOGGER.info(f"Setting xArm servo angles: {angles} with speed {speed}, acc {acc}, mvtime {mvtime}, relative {relative}")
        try:
            angles.append(1.0 if relative else 0.0)
            msg = JointState(name=self.XARM_JOINTS, position=angles)
            self.publisher_digital_xarm.publish(msg)
        except Exception as e:
            LOGGER.error(f"Failed to set xArm servo angles: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return

    def _execute_set_servo_angle_xarm(self, action: Dict[str, Any]) -> None:
        """Execute xArm set_servo_angle."""
        angles = action.get("angles", [])
        speed = action.get("speed", 100)
        acc = action.get("acc", 500)
        mvtime = action.get("mvtime", 0)
        relative = action.get("relative", True)
        LOGGER.info(f"Setting xArm servo angles: {angles} with speed {speed}, acc {acc}, mvtime {mvtime}, relative {relative}")
        try:
            self.publisher_xarm.publish(String(data=f"set_servo_angle {angles[0]} {angles[1]} {angles[2]} {angles[3]} {angles[4]} {angles[5]} {angles[6]} {speed} {acc} {mvtime} {relative}"))
        except Exception as e:
            LOGGER.error(f"Failed to set xArm servo angles: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return
        
    def _execute_set_gripper_position_digital_xarm(self, action: Dict[str, Any]) -> None:
        """Execute xArm set_gripper_position (digital)."""
        pos = action.get("pos", 500)/1000 # Isaac Sim joint_dof limit
        labware = action.get("labware", "")
        try:
            msg = JointState(name=self.XARM_GRIPPER, position=[pos, pos])
            if pos > self.prev_gripper_position: # if the gripper is opening
                LOGGER.info(f"Setting xArm gripper position: {pos} to release labware {labware}")
                self.publisher_target_asset_xarm.publish(String(data=""))
            else: # if the gripper is closing
                LOGGER.info(f"Setting xArm gripper position: {pos} to grip labware {labware}")
                self.publisher_target_asset_xarm.publish(String(data=f"{labware}"))
            self.publisher_digital_xarm.publish(msg)
        except Exception as e:
            LOGGER.error(f"Failed to set xArm gripper position: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return

    def _execute_set_gripper_position_xarm(self, action: Dict[str, Any]) -> None:
        """Execute xArm set_gripper_position (digital)."""
        pos = action.get("pos", 500)
        LOGGER.info(f"Setting xArm gripper position: {pos}")
        try:
            self.publisher_xarm.publish(String(data=f"set_gripper_position {pos}"))
        except Exception as e:
            LOGGER.error(f"Failed to set xArm gripper position: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return
    
    def _execute_arduino_control(self, arduino_control: Dict[str, Any]) -> None:
        """Execute Arduino control actions."""
        # Check if Arduino client is available
        if not hasattr(self, 'arduino_client') or self.arduino_client is None:
            LOGGER.warning("Arduino client not available. Skipping Arduino control actions.")
            return

        base0_temp = arduino_control.get("base0_temp")
        pump0_ml = arduino_control.get("pump0_ml")
        ultrasonic0_ms = arduino_control.get("ultrasonic0_ms")

        try:
            if base0_temp:
                LOGGER.info(f"Setting base 0 temperature to {base0_temp}°C")
                self.arduino_client.setTemp(0, base0_temp)

            if pump0_ml and pump0_ml > 0:
                LOGGER.info(f"Dispensing {pump0_ml}ml from pump 0")
                self.arduino_client.dispense_ml(pumpNumber=0, volume=pump0_ml)

            if ultrasonic0_ms and ultrasonic0_ms > 0:
                LOGGER.info(f"Running ultrasonic for {ultrasonic0_ms}ms")
                self.arduino_client.setUltrasonicOnTimer(0, ultrasonic0_ms)
        except Exception as e:
            LOGGER.error(f"Failed to execute Arduino control actions: {str(e)}")
            LOGGER.warning(f"Continuing with workflow execution...")
            return

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Execute a workflow defined in a JSON file")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("--prefect", action="store_true", help="Use Prefect for workflow execution")
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no real devices)")
    parser.add_argument("--register", action="store_true", help="Register workflow with Prefect server")
    parser.add_argument("--project", default="电化学实验", help="Prefect project name for registration")
    args = parser.parse_args()

    workflow_file = args.workflow_file
    print(f"Loading workflow file: {workflow_file}")

    rclpy.init()

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

        # Create the workflow executor
        executor = WorkflowExecutor(
            workflow_file=workflow_file,
            use_prefect=args.prefect,
            mock_mode=args.mock
        )
        print(f"Workflow executor created successfully (Prefect: {args.prefect}, Mock: {args.mock})")

        # Register with Prefect if requested
        if args.register and args.prefect:
            if hasattr(executor, 'prefect_executor') and executor.prefect_executor:
                try:
                    result = executor.prefect_executor.register(project_name=args.project)
                    print(f"Workflow registration result: {result}")
                    sys.exit(0)
                except Exception as e:
                    print(f"Failed to register workflow: {str(e)}")
                    sys.exit(1)
            else:
                print("Prefect executor not available. Cannot register workflow.")
                sys.exit(1)

        # Execute the workflow
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