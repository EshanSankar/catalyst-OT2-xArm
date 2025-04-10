#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CVA (Cyclic Voltammetry Analysis) Backend Module

This module handles the execution of cyclic voltammetry experiments using the OT-2 robot
and Arduino control system. It processes parameters from the Canvas UI and executes
the corresponding experimental procedures.
"""

import logging
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np

# Import required modules
from OT_Arduino_Client import Arduino
from OT2_control import opentronsClient
from utils import execute_arduino_actions

# Configure logging
LOGGER = logging.getLogger(__name__)

class CVABackend:
    """
    Backend class for Cyclic Voltammetry Analysis experiments.
    
    This class handles the execution of CVA experiments, including:
    1. Parameter validation and processing
    2. Arduino control (temperature, pumps, ultrasonic)
    3. OT-2 robot control (pipetting, washing)
    4. Data collection and storage
    """
    
    def __init__(self, config_path: Optional[str] = None, result_uploader: Optional[Any] = None):
        """
        Initialize the CVA backend.
        
        Args:
            config_path (Optional[str]): Path to configuration file
            result_uploader (Optional[Any]): Result uploader instance
        """
        self.config = self._load_config(config_path) if config_path else {}
        self.arduino = None
        self.ot2_client = None
        self.result_uploader = result_uploader
        LOGGER.info("CVA Backend initialized")
    
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
        Execute a CVA experiment based on the provided UO (Unit Operation).
        
        Args:
            uo (Dict[str, Any]): Unit operation dictionary containing experiment parameters
            
        Returns:
            Dict[str, Any]: Results of the experiment
        """
        LOGGER.info(f"Executing CVA experiment with parameters: {uo}")
        
        # Validate UO type
        if uo.get("uo_type") != "CVA":
            LOGGER.error(f"Invalid UO type: {uo.get('uo_type')}, expected CVA")
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
            
            # Execute CVA measurement
            results = self._execute_cva_measurement(params)
            
            # Save results
            self._save_results(results, uo)
            
            return {"status": "success", "results": results}
        
        except Exception as e:
            LOGGER.error(f"Error executing CVA experiment: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_cva_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the CVA measurement.
        
        Args:
            params (Dict[str, Any]): Experiment parameters
            
        Returns:
            Dict[str, Any]: Measurement results
        """
        # Extract CVA-specific parameters
        start_voltage = params.get("start_voltage", 0.0)  # Starting voltage in V
        end_voltage = params.get("end_voltage", 1.0)  # Ending voltage in V
        scan_rate = params.get("scan_rate", 0.01)  # Scan rate in V/s
        cycles = params.get("cycles", 1)  # Number of cycles
        sample_interval = params.get("sample_interval", 0.1)  # Sampling interval in seconds
        
        # Reference electrode configuration
        reference = params.get("reference", {
            "type": "RE",  # RE or CE
            "enabled": True  # Use reference electrode
        })
        
        # Nested loop configuration (optional)
        nested_loop = params.get("nested_loop", None)
        
        LOGGER.info(f"Executing CVA measurement: start voltage {start_voltage}V, "
                   f"end voltage {end_voltage}V, scan rate {scan_rate}V/s, "
                   f"cycles {cycles}, reference: {reference}")
        
        all_results = []
        
        # Handle nested loop if specified
        if nested_loop:
            variable = nested_loop.get("variable")
            values = nested_loop.get("values", [])
            
            for value in values:
                # Update the parameter being looped
                loop_params = params.copy()
                loop_params[variable] = value
                
                # Execute measurement with updated parameter
                cycle_results = self._execute_cycles(
                    start_voltage, end_voltage, scan_rate, 
                    cycles, sample_interval, reference
                )
                
                all_results.append({
                    "loop_value": value,
                    "variable": variable,
                    "results": cycle_results
                })
        else:
            # Execute single set of cycles
            all_results = self._execute_cycles(
                start_voltage, end_voltage, scan_rate,
                cycles, sample_interval, reference
            )
        
        return {
            "type": "nested" if nested_loop else "single",
            "results": all_results,
            "parameters": {
                "start_voltage": start_voltage,
                "end_voltage": end_voltage,
                "scan_rate": scan_rate,
                "cycles": cycles,
                "sample_interval": sample_interval,
                "reference": reference,
                "nested_loop": nested_loop
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_cycles(
        self, 
        start_voltage: float,
        end_voltage: float,
        scan_rate: float,
        cycles: int,
        sample_interval: float,
        reference: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple CV cycles.
        
        Args:
            start_voltage (float): Starting voltage
            end_voltage (float): Ending voltage
            scan_rate (float): Scan rate
            cycles (int): Number of cycles
            sample_interval (float): Sampling interval
            reference (Dict[str, Any]): Reference electrode configuration
            
        Returns:
            List[Dict[str, Any]]: Results for each cycle
        """
        cycle_results = []
        
        for cycle in range(cycles):
            LOGGER.info(f"Executing cycle {cycle + 1}/{cycles}")
            
            # Calculate points for forward and reverse scans
            voltage_range = abs(end_voltage - start_voltage)
            points_per_scan = int(voltage_range / (scan_rate * sample_interval))
            
            # Forward scan (start_voltage -> end_voltage)
            forward_voltages = np.linspace(start_voltage, end_voltage, points_per_scan)
            forward_currents = [
                self._simulate_current_response(v, scan_rate) 
                for v in forward_voltages
            ]
            
            # Reverse scan (end_voltage -> start_voltage)
            reverse_voltages = np.linspace(end_voltage, start_voltage, points_per_scan)
            reverse_currents = [
                self._simulate_current_response(v, -scan_rate)
                for v in reverse_voltages
            ]
            
            # Combine scans
            voltages = list(forward_voltages) + list(reverse_voltages)
            currents = forward_currents + reverse_currents
            times = [i * sample_interval for i in range(len(voltages))]
            
            cycle_results.append({
                "cycle": cycle + 1,
                "time": times,
                "voltage": voltages,
                "current": currents
            })
            
            # Small delay between cycles
            if cycle < cycles - 1:
                time.sleep(0.5)
        
        return cycle_results
    
    def _simulate_current_response(self, voltage: float, scan_rate: float) -> float:
        """
        Simulate current response for a given voltage and scan rate.
        Replace this with actual measurement code.
        
        Args:
            voltage (float): Applied voltage
            scan_rate (float): Scan rate (positive for forward, negative for reverse)
            
        Returns:
            float: Simulated current response
        """
        # Simple simulation of CV curve
        # Replace with actual measurement
        base_current = 1e-6  # Base current in A
        peak_voltage = 0.5  # Peak position
        peak_width = 0.2  # Peak width
        
        # Simulate peaks
        peak_current = base_current * (
            1 + 5 * np.exp(-(voltage - peak_voltage)**2 / peak_width)
        )
        
        # Add hysteresis effect based on scan direction
        hysteresis = 0.2 * np.sign(scan_rate) * peak_current
        
        return peak_current + hysteresis
    
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
        filename = f"cva_{timestamp}.json"
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
        "uo_type": "CVA",
        "parameters": {
            "start_voltage": 0.0,
            "end_voltage": 1.0,
            "scan_rate": 0.05,
            "cycles": 3,
            "arduino_control": {
                "base0_temp": 25.0,
                "pump0_ml": 2.5,
                "ultrasonic0_ms": 3000
            }
        }
    }
    
    # Create and run backend
    backend = CVABackend()
    result = backend.execute_experiment(example_uo)
    print(f"Experiment result: {result}") 
