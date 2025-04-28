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
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

from backends.base import BaseBackend

# Configure logging
LOGGER = logging.getLogger(__name__)

class OCVBackend(BaseBackend):
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
        super().__init__(config_path, result_uploader, experiment_type="OCV")
    
    def _execute_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Reference electrode configuration
        reference = params.get("reference", {
            "type": "RE",  # RE or CE
            "enabled": True  # Use reference electrode
        })
        
        self.logger.info(f"Executing OCV measurement: duration {duration}s, "
                       f"sample interval {sample_interval}s, reference: {reference}")
        
        # Calculate number of data points
        num_points = int(duration / sample_interval) + 1
        
        # Lists to store results
        times = []
        voltages = []
        
        # Simulate measurement
        start_time = time.time()
        for i in range(num_points):
            # Calculate current time
            current_time = i * sample_interval
            
            # Simulate voltage measurement (replace with actual measurement)
            voltage = self._simulate_voltage_measurement(current_time, reference)
            
            times.append(current_time)
            voltages.append(voltage)
            
            # Wait until next sample time
            next_sample_time = start_time + (i + 1) * sample_interval
            sleep_time = max(0, next_sample_time - time.time())
            if sleep_time > 0 and i < num_points - 1:
                time.sleep(sleep_time)
        
        return {
            "time": times,
            "voltage": voltages,
            "parameters": {
                "duration": duration,
                "sample_interval": sample_interval,
                "reference": reference
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _simulate_voltage_measurement(self, time_point: float, reference: Dict[str, Any]) -> float:
        """
        Simulate voltage measurement at a given time point.
        Replace this with actual measurement code.
        
        Args:
            time_point (float): Time point in seconds
            reference (Dict[str, Any]): Reference electrode configuration
            
        Returns:
            float: Simulated voltage
        """
        # Simple simulation of OCV curve
        # Replace with actual measurement
        
        # Initial voltage
        initial_voltage = 1.2
        
        # Exponential decay
        decay_rate = 0.01
        steady_state = 0.8
        
        # Calculate voltage
        voltage = steady_state + (initial_voltage - steady_state) * np.exp(-decay_rate * time_point)
        
        # Add some noise
        noise_level = 0.005  # 5 mV noise
        voltage += noise_level * (np.random.random() - 0.5)
        
        return voltage
    
    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """
        Validate OCV-specific parameters.
        
        Args:
            params (Dict[str, Any]): Parameters to validate
            
        Returns:
            List[str]: List of validation error messages (empty if valid)
        """
        errors = super().validate_parameters(params)
        
        # Validate OCV-specific parameters
        duration = params.get("duration")
        sample_interval = params.get("sample_interval")
        
        if duration is not None and (not isinstance(duration, (int, float)) or duration <= 0):
            errors.append("Duration must be a positive number")
            
        if sample_interval is not None and (not isinstance(sample_interval, (int, float)) or sample_interval <= 0):
            errors.append("Sample interval must be a positive number")
            
        if duration is not None and sample_interval is not None and sample_interval > duration:
            errors.append("Sample interval cannot be greater than duration")
            
        return errors
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """
        Get default parameters for OCV experiments.
        
        Returns:
            Dict[str, Any]: Default parameters
        """
        params = super().get_default_parameters()
        params.update({
            "duration": 60,
            "sample_interval": 1.0,
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
