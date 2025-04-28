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
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

from backends.base import BaseBackend

# Configure logging
LOGGER = logging.getLogger(__name__)

class CVABackend(BaseBackend):
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
        super().__init__(config_path, result_uploader, experiment_type="CVA")
    
    def _execute_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
        
        self.logger.info(f"Executing CVA measurement: start voltage {start_voltage}V, "
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
            self.logger.info(f"Executing cycle {cycle + 1}/{cycles}")
            
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
    
    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """
        Validate CVA-specific parameters.
        
        Args:
            params (Dict[str, Any]): Parameters to validate
            
        Returns:
            List[str]: List of validation error messages (empty if valid)
        """
        errors = super().validate_parameters(params)
        
        # Validate CVA-specific parameters
        start_voltage = params.get("start_voltage")
        end_voltage = params.get("end_voltage")
        scan_rate = params.get("scan_rate")
        cycles = params.get("cycles")
        
        if start_voltage is not None and (start_voltage < -2.0 or start_voltage > 2.0):
            errors.append("Start voltage must be between -2.0V and 2.0V")
            
        if end_voltage is not None and (end_voltage < -2.0 or end_voltage > 2.0):
            errors.append("End voltage must be between -2.0V and 2.0V")
            
        if scan_rate is not None and (scan_rate <= 0 or scan_rate > 1.0):
            errors.append("Scan rate must be between 0 and 1.0 V/s")
            
        if cycles is not None and (not isinstance(cycles, int) or cycles <= 0):
            errors.append("Cycles must be a positive integer")
            
        return errors
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """
        Get default parameters for CVA experiments.
        
        Returns:
            Dict[str, Any]: Default parameters
        """
        params = super().get_default_parameters()
        params.update({
            "start_voltage": 0.0,
            "end_voltage": 1.0,
            "scan_rate": 0.05,
            "cycles": 1,
            "sample_interval": 0.1,
            "reference": {
                "type": "RE",
                "enabled": True
            }
        })
        return params


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
