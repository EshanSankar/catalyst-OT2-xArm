#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base Backend Module

This module defines the base class for all electrochemical experiment backends.
It provides common functionality and interface definitions that all backend
implementations must follow.
"""

import logging
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from hardware.OT_Arduino_Client import Arduino
from hardware.OT2_control import OT2Control
from hardware.xArm_control import xArmControl

# Configure logging
LOGGER = logging.getLogger(__name__)

class BaseBackend(ABC):
    """
    Base class for all experiment backends.

    This class defines the interface and common functionality that all
    experiment backend implementations must provide.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        result_uploader: Optional[Any] = None,
        experiment_type: str = "UNKNOWN"
    ):
        """
        Initialize the experiment backend.

        Args:
            config_path (Optional[str]): Path to configuration file
            result_uploader (Optional[Any]): Result uploader instance
            experiment_type (str): Type of experiment (e.g., 'CVA', 'PEIS')
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = self._load_config(config_path) if config_path else {}
        self.arduino: Optional[Arduino] = None
        self.ot2_client: Optional[OT2Control] = None
        self.xarm_client: Optional[xArmControl] = None
        self.result_uploader = result_uploader
        self.experiment_type = experiment_type
        self.logger.info(f"{experiment_type} Backend initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            config_path (str): Path to configuration file

        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config from {config_path}: {str(e)}")
            return {}

    def connect_devices(self) -> bool:
        """
        Connect to Arduino and OT-2 devices.

        Returns:
            bool: True if connections successful, False otherwise
        """
        try:
            # Connect to Arduino
            if not self.arduino:
                self.arduino = Arduino()
                self.logger.info("Connected to Arduino")

            # Connect to OT-2
            if not self.ot2_client:
                robot_ip = self.config.get("ot2_ip", "100.67.89.154")
                self.ot2_client = OT2Control(strRobotIP=robot_ip)
                self.logger.info("Connected to OT-2")
            
            # Connect to xArm
            if not self.xarm_client:
                robot_ip = self.config.get("xarm_ip", "192.168.1.233")
                self.xarm_client = xArmControl(strRobotIP=robot_ip)
                self.logger.info("Connected to xArm")

            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to devices: {str(e)}")
            return False

    def disconnect_devices(self) -> None:
        """
        Disconnect from all devices.
        """
        if self.arduino:
            try:
                self.arduino.disconnect()
                self.logger.info("Disconnected from Arduino")
            except Exception as e:
                self.logger.error(f"Error disconnecting Arduino: {str(e)}")
            finally:
                self.arduino = None

        if self.ot2_client:
            try:
                self.ot2_client.disconnect()
                self.logger.info("Disconnected from OT-2")
            except Exception as e:
                self.logger.error(f"Error disconnecting OT-2: {str(e)}")
            finally:
                self.ot2_client = None
        
        if self.xarm_client:
            try:
                self.xarm_client.disconnect()
                self.logger.info("Disconnected from xArm")
            except Exception as e:
                self.logger.error(f"Error disconnecting xArm: {str(e)}")
            finally:
                self.xarm_client = None

    def execute_experiment(self, uo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an experiment based on the provided UO (Unit Operation).

        Args:
            uo (Dict[str, Any]): Unit operation dictionary containing experiment parameters

        Returns:
            Dict[str, Any]: Results of the experiment
        """
        self.logger.info(f"Executing {self.experiment_type} experiment with parameters: {uo}")

        # Validate UO type
        if uo.get("uo_type") != self.experiment_type:
            self.logger.error(f"Invalid UO type: {uo.get('uo_type')}, expected {self.experiment_type}")
            return {"status": "error", "message": "Invalid UO type"}

        # Extract parameters
        params = uo.get("parameters", {})

        # Validate parameters
        validation_errors = self.validate_parameters(params)
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            self.logger.error(f"Parameter validation failed: {error_msg}")
            return {"status": "error", "message": error_msg}

        # Connect to devices if not already connected
        if not self.arduino or not self.ot2_client or not self.xarm_client:
            if not self.connect_devices():
                return {"status": "error", "message": "Failed to connect to devices"}

        try:
            # Execute Arduino actions if specified
            if "arduino_control" in params:
                from utils.utils import execute_arduino_actions
                execute_arduino_actions(params["arduino_control"], self.arduino)

            # Execute measurement
            results = self._execute_measurement(params)

            # Save results
            self._save_results(results, uo)

            # Upload results if uploader is configured
            if self.result_uploader:
                try:
                    self.result_uploader.upload_results(results)
                except Exception as e:
                    self.logger.error(f"Failed to upload results: {str(e)}")

            return {"status": "success", "results": results}

        except Exception as e:
            self.logger.error(f"Error executing {self.experiment_type} experiment: {str(e)}")
            return {"status": "error", "message": str(e)}

        finally:
            # Optionally disconnect devices
            if self.config.get("auto_disconnect", False):
                self.disconnect_devices()

    def _save_results(self, results: Dict[str, Any], uo: Dict[str, Any]) -> None:
        """
        Save experiment results to file.

        Args:
            results (Dict[str, Any]): Experiment results
            uo (Dict[str, Any]): Unit operation dictionary
        """
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(results_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.experiment_type.lower()}_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)

        # Save results
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "uo": uo,
                    "results": results,
                    "timestamp": timestamp,
                    "experiment_type": self.experiment_type
                }, f, indent=2)
            self.logger.info(f"Results saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save results to {filepath}: {str(e)}")
            raise

    @abstractmethod
    def _execute_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the actual measurement. Must be implemented by subclasses.

        Args:
            params (Dict[str, Any]): Experiment parameters

        Returns:
            Dict[str, Any]: Measurement results
        """
        raise NotImplementedError("Subclasses must implement _execute_measurement")

    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """
        Validate experiment parameters. Can be overridden by subclasses.

        Args:
            params (Dict[str, Any]): Parameters to validate

        Returns:
            List[str]: List of validation error messages (empty if valid)
        """
        errors = []

        # Common parameter validation
        if "arduino_control" in params:
            arduino_params = params["arduino_control"]

            # Validate temperature
            temp = arduino_params.get("base0_temp")
            if temp is not None and (temp < 0 or temp > 100):
                errors.append("Temperature must be between 0 and 100°C")

            # Validate pump volume
            volume = arduino_params.get("pump0_ml")
            if volume is not None and volume <= 0:
                errors.append("Pump volume must be positive")

            # Validate ultrasonic timing
            timing = arduino_params.get("ultrasonic0_ms")
            if timing is not None and timing < 0:
                errors.append("Ultrasonic timing must be non-negative")

        return errors

    def get_default_parameters(self) -> Dict[str, Any]:
        """
        Get default parameters for the experiment type.
        Can be overridden by subclasses.

        Returns:
            Dict[str, Any]: Default parameters
        """
        return {
            "arduino_control": {
                "base0_temp": 25.0,
                "pump0_ml": 0.0,
                "ultrasonic0_ms": 0
            }
        }