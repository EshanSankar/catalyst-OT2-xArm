#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Experiment dispatch module for electrochemical experiments.

This module handles the dispatching of experiments to their respective backend modules
based on the experiment type (uo_type).
"""

import logging
from typing import Dict, Any, Optional
import importlib
from datetime import datetime
import uuid
import os
from abc import ABC, abstractmethod
import sys
import json

from parsing import parse_experiment_parameters
from backends import BaseBackend, CVABackend, PEISBackend, OCVBackend, CPBackend, LSVBackend

LOGGER = logging.getLogger(__name__)

class ResultUploader(ABC):
    """Abstract base class for result uploaders."""

    @abstractmethod
    def upload(self, results: Dict[str, Any], experiment_id: str) -> bool:
        """
        Upload experiment results to storage.

        Args:
            results: Experiment results to upload
            experiment_id: Unique experiment identifier

        Returns:
            bool: True if upload successful, False otherwise
        """
        pass

class LocalResultUploader(ResultUploader):
    """Save results to local filesystem."""

    def __init__(self, base_dir: str = "results"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def upload(self, results: Dict[str, Any], experiment_id: str) -> bool:
        try:
            # Create experiment directory
            exp_dir = os.path.join(self.base_dir, experiment_id)
            os.makedirs(exp_dir, exist_ok=True)

            # Save results as JSON
            result_path = os.path.join(exp_dir, "results.json")
            with open(result_path, 'w') as f:
                json.dump(results, f, indent=2)

            LOGGER.info(f"Saved results to {result_path}")
            return True

        except Exception as e:
            LOGGER.error(f"Failed to save results: {str(e)}")
            return False

class S3ResultUploader(ResultUploader):
    """Upload results to S3."""

    def __init__(self, bucket: str, prefix: str = "experiments"):
        # Import boto3 only when S3 uploader is used
        import boto3
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.prefix = prefix

    def upload(self, results: Dict[str, Any], experiment_id: str) -> bool:
        try:
            # Convert results to JSON string
            results_json = json.dumps(results, indent=2)

            # Upload to S3
            key = f"{self.prefix}/{experiment_id}/results.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=results_json
            )

            LOGGER.info(f"Uploaded results to s3://{self.bucket}/{key}")
            return True

        except Exception as e:
            LOGGER.error(f"Failed to upload results to S3: {str(e)}")
            return False

class ExperimentDispatcher:
    """
    Dispatcher class for handling electrochemical experiments.

    This class manages the routing of experiment requests to their appropriate
    backend modules and handles the execution flow.
    """

    # Backend classes are imported directly from the backends package

    def __init__(
        self,
        config_path: Optional[str] = None,
        result_uploader: Optional[ResultUploader] = None
    ):
        """
        Initialize the experiment dispatcher.

        Args:
            config_path: Path to global configuration file
            result_uploader: Optional result uploader instance
        """
        self.config_path = config_path
        self.backend_instances = {}
        self.result_uploader = result_uploader or LocalResultUploader()

    def _generate_experiment_id(self, uo_type: str) -> str:
        """
        Generate a unique experiment ID.

        Args:
            uo_type: Type of experiment (e.g., "CVA", "PEIS")

        Returns:
            str: Unique experiment ID in format: {timestamp}_{uo_type}_{uuid}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
        return f"{timestamp}_{uo_type}_{unique_id}"

    def _get_backend_instance(self, uo_type: str):
        """
        Get or create a backend instance for the given experiment type.

        Args:
            uo_type: Type of experiment (e.g., "CVA", "PEIS")

        Returns:
            Backend instance for the experiment type

        Raises:
            ValueError: If backend type is unknown or cannot be instantiated
        """
        # Map of experiment types to their backend classes
        backend_classes = {
            "CVA": CVABackend,
            "PEIS": PEISBackend,
            "OCV": OCVBackend,
            "CP": CPBackend,
            "LSV": LSVBackend
        }

        if uo_type not in backend_classes:
            raise ValueError(f"Unknown experiment type: {uo_type}")

        if uo_type not in self.backend_instances:
            try:
                backend_class = backend_classes[uo_type]
                self.backend_instances[uo_type] = backend_class(
                    config_path=self.config_path,
                    result_uploader=self.result_uploader
                )
                LOGGER.info(f"Created new {uo_type} backend instance")
            except Exception as e:
                LOGGER.error(f"Failed to create backend for {uo_type}: {str(e)}")
                raise ValueError(f"Failed to create backend for {uo_type}: {str(e)}")

        return self.backend_instances[uo_type]

    def execute_experiment(self, uo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an experiment based on the provided unit operation.

        Args:
            uo: Unit operation dictionary containing experiment parameters

        Returns:
            Dict[str, Any]: Results of the experiment

        Example:
            dispatcher = ExperimentDispatcher()
            result = dispatcher.execute_experiment({
                "uo_type": "CVA",
                "parameters": {
                    "start_voltage": "0.0V",
                    "end_voltage": "1.0V",
                    "scan_rate": 0.05,
                    "cycles": 3,
                    "arduino_control": {
                        "base0_temp": 25.0,
                        "pump0_ml": 2.5,
                        "ultrasonic0_ms": 3000
                    }
                }
            })
        """
        try:
            # Parse and validate parameters
            parsed_uo = parse_experiment_parameters(uo)
            uo_type = parsed_uo["uo_type"]

            # Generate experiment ID
            experiment_id = self._generate_experiment_id(uo_type)
            parsed_uo["experiment_id"] = experiment_id

            # Get backend instance
            backend = self._get_backend_instance(uo_type)

            # Execute experiment
            LOGGER.info(f"Executing {uo_type} experiment (ID: {experiment_id})")
            result = backend.execute_experiment(parsed_uo)

            # Add metadata to result
            result.update({
                "experiment_id": experiment_id,
                "uo_type": uo_type,
                "timestamp": datetime.now().isoformat()
            })

            # Upload results
            if not self.result_uploader.upload(result, experiment_id):
                LOGGER.warning(f"Failed to upload results for experiment {experiment_id}")

            return result

        except Exception as e:
            LOGGER.error(f"Error executing experiment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def cleanup(self) -> None:
        """
        Clean up resources used by backend instances.
        Should be called when the dispatcher is no longer needed.
        """
        for uo_type, backend in self.backend_instances.items():
            try:
                backend.disconnect_devices()
                LOGGER.info(f"Cleaned up {uo_type} backend")
            except Exception as e:
                LOGGER.error(f"Error cleaning up {uo_type} backend: {str(e)}")

def validate_workflow_json(workflow_file, schema_file="workflow_schema.json"):
    """
    Validate a workflow JSON file against schema.

    Args:
        workflow_file (str): Path to workflow JSON file
        schema_file (str): Path to schema JSON file

    Returns:
        bool: True if valid, False otherwise

    Raises:
        ValueError: If validation fails with details of the error
    """
    try:
        from jsonschema import validate, ValidationError

        # Load schema
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
        except FileNotFoundError:
            LOGGER.warning(f"Schema file {schema_file} not found. Skipping validation.")
            return True
        except json.JSONDecodeError as e:
            LOGGER.warning(f"Invalid JSON in schema file {schema_file}: {e}. Skipping validation.")
            return True

        # Load workflow
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Workflow file {workflow_file} not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in workflow file {workflow_file}: {e}")

        # Validate
        validate(instance=workflow, schema=schema)
        LOGGER.info(f"Workflow file {workflow_file} is valid!")
        return True

    except ValidationError as e:
        error_message = f"Validation error: {e.message}"
        if e.path:
            path_str = " -> ".join([str(p) for p in e.path])
            error_message += f" at: {path_str}"
        raise ValueError(error_message)
    except ImportError:
        LOGGER.warning("jsonschema library not installed. Skipping validation.")
        return True

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Execute a workflow defined in a JSON file")
    parser.add_argument("workflow_file", help="Path to the workflow JSON file")
    parser.add_argument("--schema", default="workflow_schema.json", help="Path to the schema JSON file")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no real devices)")
    parser.add_argument("--ip_ot2", type=str, help="IP address of the OT-2 robot (default: from workflow or 100.67.89.154)")
    parser.add_argument("--ip_xarm", type=str, help="IP address of the xArm robot (default: from workflow or 192.168.1.233)")
    parser.add_argument("--port", type=str, help="Serial port of the Arduino (default: COM3 on Windows, /dev/ttyUSB0 on Linux)")
    args = parser.parse_args()

    workflow_file = args.workflow_file
    schema_file = args.schema
    use_mock = args.mock

    LOGGER.info(f"Starting workflow execution with file: {workflow_file}")
    LOGGER.info(f"Mock mode: {use_mock}")

    if args.ip_ot2:
        LOGGER.info(f"Using custom OT-2 IP: {args.ip_ot2}")

    if args.ip_xarm:
        LOGGER.info(f"Using custom xArm IP: {args.ip_xarm}")

    if args.port:
        LOGGER.info(f"Using custom Arduino port: {args.port}")

    # Validate workflow JSON
    try:
        if not validate_workflow_json(workflow_file, schema_file):
            sys.exit(1)  # Exit if validation fails
    except ValueError as e:
        LOGGER.error(str(e))
        sys.exit(1)

    # Load workflow file
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
    except Exception as e:
        LOGGER.error(f"Error loading workflow file: {str(e)}")
        sys.exit(1)

    # Process workflow using the workflow_executor.py
    try:
        # Import the WorkflowExecutor class
        from workflow_executor import WorkflowExecutor
        LOGGER.info("Successfully imported WorkflowExecutor")

        # Create the workflow executor
        LOGGER.info(f"Creating WorkflowExecutor with workflow file: {workflow_file}")
        executor = WorkflowExecutor(workflow_file)
        LOGGER.info("WorkflowExecutor created successfully")

        # Check if we should use mock mode
        if use_mock:
            LOGGER.info("Running in mock mode - using mock clients")

        # If not in mock mode, try to import and use real device classes
        if not use_mock:
            try:
                # Try to import the opentronsClient class
                try:
                    # Try multiple approaches to import the opentronsClient class
                    LOGGER.info("Trying multiple approaches to import opentronsClient class...")

                    # Approach 1: Direct import
                    try:
                        LOGGER.info("Approach 1: Direct import...")
                        from opentronsHTTPAPI_clientBuilder import opentronsClient
                        LOGGER.info("Successfully imported opentronsClient using direct import")
                    except ImportError as e:
                        LOGGER.warning(f"Direct import failed: {str(e)}")

                        # Approach 2: Using sys.path.append
                        try:
                            LOGGER.info("Approach 2: Using sys.path.append...")
                            import sys
                            current_dir = os.getcwd()
                            LOGGER.info(f"Current directory: {current_dir}")
                            if current_dir not in sys.path:
                                sys.path.append(current_dir)
                                LOGGER.info(f"Added {current_dir} to sys.path")
                            from opentronsHTTPAPI_clientBuilder import opentronsClient
                            LOGGER.info("Successfully imported opentronsClient using sys.path.append")
                        except ImportError as e:
                            LOGGER.warning(f"sys.path.append approach failed: {str(e)}")

                            # Approach 3: Using exec
                            try:
                                LOGGER.info("Approach 3: Using exec...")
                                file_path = os.path.join(current_dir, "opentronsHTTPAPI_clientBuilder.py")
                                LOGGER.info(f"File path: {file_path}")

                                # Read the file content
                                with open(file_path, "r") as f:
                                    file_content = f.read()

                                # Create a namespace
                                namespace = {}

                                # Execute the file content in the namespace
                                exec(file_content, namespace)

                                # Check if opentronsClient is in the namespace
                                if 'opentronsClient' in namespace:
                                    opentronsClient = namespace['opentronsClient']
                                    LOGGER.info("Successfully imported opentronsClient using exec")
                                else:
                                    LOGGER.error("opentronsClient class not found in namespace after exec")
                                    raise ImportError("opentronsClient class not found in namespace after exec")
                            except Exception as e:
                                LOGGER.error(f"All import approaches failed: {str(e)}")
                                raise ImportError(f"Failed to import opentronsClient: {str(e)}")

                    # Create an OT2 client instance
                    if args.ip_ot2:
                        robot_ip = args.ip_ot2
                    else:
                        robot_ip = workflow.get("global_config", {}).get("hardware", {}).get("ot2", {}).get("ip_ot2", "100.67.89.154")
                    LOGGER.info(f"Creating OT-2 client with IP: {robot_ip}")
                    ot2_client = opentronsClient(strRobotIP=robot_ip)
                    LOGGER.info(f"Successfully created OT-2 client with run ID: {ot2_client.runID}")

                    # Replace the OT-2 client in the executor
                    executor.ot2_client = ot2_client
                    LOGGER.info("Using real OT-2 client")
                except Exception as e:
                    LOGGER.warning(f"Failed to import and use real OT-2 client: {str(e)}")
                
                # Try to import the xArm class
                try:
                    from xarm.wrapper import XArmAPI as xArmAPI
                    LOGGER.info("Successfully imported xArmAPI from xarm.wrapper")
                except Exception as e:
                    LOGGER.warning(f"Failed to import xArmAPI: {str(e)}")
                    xArmAPI = None
                if xArmAPI:
                    # Create an xarmClient instance
                    if args.ip_xarm:
                        robot_ip = args.ip_xarm
                    else:
                        robot_ip = workflow.get("global_config", {}).get("hardware", {}).get("xarm", {}).get("ip_xarm", "192.168.1.233")
                    LOGGER.info(f"Creating xArm client with IP: {robot_ip}")
                    xarm_client = xArmAPI(robot_ip)
                    LOGGER.info(f"Successfully created xArm client")
                    # Replace the xarmClient in the executor
                    executor.xarm_client = xarm_client
                    LOGGER.info("Using real xArm client")

                # Try to import the Arduino class
                try:
                    # Try to import from ot2_arduino.py
                    from ot2_arduino import Arduino
                    LOGGER.info("Successfully imported Arduino from ot2_arduino.py")
                except ImportError:
                    try:
                        # Try to import from ot2-arduino.py using importlib
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("Arduino", "ot2-arduino.py")
                        arduino_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(arduino_module)
                        Arduino = arduino_module.Arduino
                        LOGGER.info("Successfully imported Arduino from ot2-arduino.py")
                    except Exception as e:
                        LOGGER.warning(f"Failed to import Arduino: {str(e)}")
                        Arduino = None

                if Arduino:
                    # Create an Arduino instance
                    try:
                        if args.port:
                            arduino_port = args.port
                        else:
                            # Default port based on OS
                            if os.name == 'nt':  # Windows
                                arduino_port = "COM3"
                            else:  # Linux/Mac
                                arduino_port = "/dev/ttyUSB0"
                        LOGGER.info(f"Creating Arduino client with port: {arduino_port}")

                        # Close any existing connections to the port
                        try:
                            import serial
                            ser = serial.Serial(arduino_port)
                            ser.close()
                            LOGGER.info(f"Closed existing connection to {arduino_port}")
                        except Exception as e:
                            LOGGER.info(f"No existing connection to close: {str(e)}")

                        # Try to create the Arduino client
                        try:
                            arduino_client = Arduino(arduinoPort=arduino_port)
                            LOGGER.info("Successfully created Arduino client")

                            # Replace the Arduino client in the executor
                            executor.arduino_client = arduino_client
                            LOGGER.info("Using real Arduino client")
                        except PermissionError as e:
                            LOGGER.warning(f"Permission error connecting to Arduino: {str(e)}")
                            LOGGER.warning("Using mock Arduino client instead")
                        except Exception as e:
                            LOGGER.warning(f"Error creating Arduino client: {str(e)}")
                            LOGGER.warning("Using mock Arduino client instead")
                    except Exception as e:
                        LOGGER.warning(f"Failed to create Arduino client: {str(e)}")
            except Exception as e:
                LOGGER.warning(f"Failed to set up real devices: {str(e)}")
                LOGGER.info("Falling back to mock mode")

        # Execute the workflow
        LOGGER.info("Executing workflow...")
        result = executor.execute_workflow()

        if result:
            LOGGER.info("Workflow executed successfully")
            print("\nWorkflow Execution: ✓")
            print("Workflow executed successfully!")
        else:
            LOGGER.error("Workflow execution failed")
            print("\nWorkflow Execution: ✗")
            print("Workflow execution failed.")
            print("\nTroubleshooting Tips:")
            print("- Check if all devices are properly connected")
            print("- Verify the OT-2 IP address and Arduino port are correct")
            print("- Make sure the workflow file is valid")
            print("- Check the log file for detailed error messages")
            sys.exit(1)
    except Exception as e:
        LOGGER.error(f"Failed to execute workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)