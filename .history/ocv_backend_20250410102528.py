#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OCV (Open Circuit Voltage) Backend Module

This module handles the execution of open circuit voltage experiments using the OT-2 robot
and Arduino control system. It processes parameters from the Canvas UI and executes
the corresponding experimental procedures.
"""

import logging
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import required modules
from OT_Arduino_Client import Arduino
from OT2_control import opentronsClient
from utils import execute_arduino_actions

# Configure logging
LOGGER = logging.getLogger(__name__)

class OCVBackend:
    """
    Backend class for Open Circuit Voltage experiments.
    
    This class handles the execution of OCV experiments, including:
    1. Parameter validation and processing
    2. Arduino control (temperature, pumps, ultrasonic)
    3. OT-2 robot control (pipetting, washing)
    4. Data collection and storage
    """
    
    def __init__(self, config_path: Optional[str] = None, result_uploader: Optional[Any] = None):
        """
        Initialize the OCV backend.
        
        Args:
            config_path (Optional[str]): Path to configuration file
            result_uploader (Optional[Any]): Result uploader instance
        """
        self.config = self._load_config(config_path) if config_path else {}
        self.arduino = None
        self.ot2_client = None
        self.result_uploader = result_uploader
        LOGGER.info("OCV Backend initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            LOGGER.error(f"Failed to load config from {config_path}: {str(e)}")
            return {}
    
    def connect_devices(self) -> bool:
        """
        Connect to Arduino and OT-2 devices.
        
        Returns:
            bool: True if connections successful, False otherwise
        """
        try:
            # Connect to Arduino
            self.arduino = Arduino()
            LOGGER.info("Connected to Arduino")
            
            # Connect to OT-2
            robot_ip = self.config.get("robot_ip", "100.67.89.154")
            self.ot2_client = opentronsClient(strRobotIP=robot_ip)
            LOGGER.info("Connected to OT-2")
            
            return True
        except Exception as e:
            LOGGER.error(f"Failed to connect to devices: {str(e)}")
            return False
    
    def disconnect_devices(self) -> None:
        """Disconnect from Arduino and OT-2 devices."""
        if self.arduino:
            self.arduino.disconnect()
            LOGGER.info("Disconnected from Arduino")
        
        # Disconnect from OT-2 if needed
        LOGGER.info("Disconnected from OT-2")
    
    def execute_experiment(self, uo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an OCV experiment based on the provided UO (Unit Operation).
        
        Args:
            uo (Dict[str, Any]): Unit operation dictionary containing experiment parameters
            
        Returns:
            Dict[str, Any]: Results of the experiment
        """
        LOGGER.info(f"Executing OCV experiment with parameters: {uo}")
        
        # Validate UO type
        if uo.get("uo_type") != "OCV":
            LOGGER.error(f"Invalid UO type: {uo.get('uo_type')}, expected OCV")
            return {"status": "error", "message": "Invalid UO type"}
        
        # Extract parameters
        params = uo.get("parameters", {})
        
        # Connect to devices if not already connected
        if not self.arduino or not self.ot2_client:
            if not self.connect_devices():
                return {"status": "error", "message": "Failed to connect to devices"}
        
        try:
            # Execute Arduino actions if specified
            if "arduino_control" in params:
                execute_arduino_actions(params["arduino_control"], self.arduino)
            
            # Execute OT-2 actions
            # Note: Replace with actual OT-2 control code
            # self._execute_ot2_actions(params)
            
            # Execute OCV measurement
            results = self._execute_ocv_measurement(params)
            
            # Save results
            self._save_results(results, uo)
            
            return {"status": "success", "results": results}
        
        except Exception as e:
            LOGGER.error(f"Error executing OCV experiment: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_ocv_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the OCV measurement.
        
        Args:
            params (Dict[str, Any]): Experiment parameters
            
        Returns:
            Dict[str, Any]: Measurement results
        """
        # Extract OCV-specific parameters
        duration = params.get("duration", 60)  # Duration in seconds
        sample_interval = params.get("sample_interval", 1.0)  # Sampling interval in seconds
        
        LOGGER.info(f"Executing OCV measurement: duration {duration}s, "
                   f"sampling interval {sample_interval}s")
        
        # Simulate measurement (replace with actual measurement code)
        time.sleep(2)  # Simulate measurement time
        
        # Generate simulated time points
        num_points = int(duration / sample_interval)
        time_points = [i * sample_interval for i in range(num_points)]
        
        # Return simulated results
        return {
            "time": time_points,
            "voltage": [0.5 + 0.01 * (i % 10) for i in range(num_points)],  # Simulated voltage data
            "timestamp": datetime.now().isoformat()
        }
    
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
        filename = f"ocv_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)
        
        # Save results
        with open(filepath, 'w') as f:
            json.dump({
                "uo": uo,
                "results": results,
                "timestamp": timestamp
            }, f, indent=2)
        
        LOGGER.info(f"Results saved to {filepath}")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Example UO
    example_uo = {
        "uo_type": "OCV",
        "parameters": {
            "duration": 60,
            "sample_interval": 1.0,
            "arduino_control": {
                "base0_temp": 25.0,
                "pump0_ml": 2.5,
                "ultrasonic0_ms": 3000
            }
        }
    }
    
    # Create and run backend
    backend = OCVBackend()
    result = backend.execute_experiment(example_uo)
    print(f"Experiment result: {result}") 
