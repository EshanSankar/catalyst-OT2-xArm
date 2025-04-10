#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PEIS (Potentio Electrochemical Impedance Spectroscopy) Backend Module

This module handles the execution of electrochemical impedance spectroscopy experiments 
using the OT-2 robot and Arduino control system. It processes parameters from the Canvas UI 
and executes the corresponding experimental procedures.
"""

import logging
import time
import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Import required modules
from OT_Arduino_Client import Arduino
from OT2_control import opentronsClient
from utils import execute_arduino_actions

# Configure logging
LOGGER = logging.getLogger(__name__)

class PEISBackend:
    """
    Backend class for Potentio Electrochemical Impedance Spectroscopy experiments.
    
    This class handles the execution of PEIS experiments, including:
    1. Parameter validation and processing
    2. Arduino control (temperature, pumps, ultrasonic)
    3. OT-2 robot control (pipetting, washing)
    4. Frequency sweep and impedance measurement
    5. Data collection and storage
    """
    
    def __init__(self, config_path: Optional[str] = None, result_uploader: Optional[Any] = None):
        """
        Initialize the PEIS backend.
        
        Args:
            config_path (Optional[str]): Path to configuration file
            result_uploader (Optional[Any]): Result uploader instance
        """
        self.config = self._load_config(config_path) if config_path else {}
        self.arduino = None
        self.ot2_client = None
        self.result_uploader = result_uploader
        LOGGER.info("PEIS Backend initialized")
    
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
        Execute a PEIS experiment based on the provided UO (Unit Operation).
        
        Args:
            uo (Dict[str, Any]): Unit operation dictionary containing experiment parameters
            
        Returns:
            Dict[str, Any]: Results of the experiment
        """
        LOGGER.info(f"Executing PEIS experiment with parameters: {uo}")
        
        # Validate UO type
        if uo.get("uo_type") != "PEIS":
            LOGGER.error(f"Invalid UO type: {uo.get('uo_type')}, expected PEIS")
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
            
            # Execute PEIS measurement
            results = self._execute_peis_measurement(params)
            
            # Save results
            self._save_results(results, uo)
            
            return {"status": "success", "results": results}
        
        except Exception as e:
            LOGGER.error(f"Error executing PEIS experiment: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_frequency_points(self, params: Dict[str, Any]) -> List[float]:
        """
        Generate frequency points for the EIS measurement.
        
        Args:
            params (Dict[str, Any]): Experiment parameters
            
        Returns:
            List[float]: List of frequencies in Hz
        """
        start_freq = params.get("start_frequency", 0.1)  # Hz
        end_freq = params.get("end_frequency", 100000)  # Hz
        points_per_decade = params.get("points_per_decade", 10)
        
        # Calculate number of decades
        num_decades = np.log10(end_freq / start_freq)
        total_points = int(num_decades * points_per_decade)
        
        # Generate logarithmically spaced frequencies
        return list(np.logspace(
            np.log10(start_freq),
            np.log10(end_freq),
            total_points
        ))
    
    def _execute_peis_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the PEIS measurement.
        
        Args:
            params (Dict[str, Any]): Experiment parameters
            
        Returns:
            Dict[str, Any]: Measurement results
        """
        # Extract PEIS-specific parameters
        dc_voltage = params.get("dc_voltage", 0.0)  # DC bias voltage in V
        ac_amplitude = params.get("ac_amplitude", 0.01)  # AC amplitude in V
        
        # Reference electrode configuration
        reference = params.get("reference", {
            "type": "RE",  # RE or CE
            "enabled": True  # Use reference electrode
        })
        
        LOGGER.info(f"Executing PEIS measurement: DC voltage {dc_voltage}V, "
                   f"AC amplitude {ac_amplitude}V, reference: {reference}")
        
        # Generate frequency points
        frequencies = self._generate_frequency_points(params)
        LOGGER.info(f"Frequency sweep from {frequencies[0]:.2f} Hz to {frequencies[-1]:.2f} Hz")
        
        # Lists to store results
        impedance_real = []
        impedance_imag = []
        phase_angles = []
        
        # Simulate measurement at each frequency
        for freq in frequencies:
            # Simulate measurement (replace with actual measurement code)
            time.sleep(0.1)  # Simulate measurement time
            
            # Generate simulated impedance response
            # In real EIS, these would be measured values
            z_real, z_imag = self._simulate_impedance_response(
                freq, dc_voltage, ac_amplitude, reference
            )
            phase = np.arctan2(z_imag, z_real)  # Phase angle in radians
            
            impedance_real.append(z_real)
            impedance_imag.append(z_imag)
            phase_angles.append(phase)
        
        # Calculate magnitude
        impedance_magnitude = [np.sqrt(r**2 + i**2) 
                             for r, i in zip(impedance_real, impedance_imag)]
        
        # Return results
        return {
            "frequencies": frequencies,
            "impedance_real": impedance_real,
            "impedance_imag": impedance_imag,
            "impedance_magnitude": impedance_magnitude,
            "phase_angles": phase_angles,
            "dc_voltage": dc_voltage,
            "ac_amplitude": ac_amplitude,
            "reference": reference,
            "timestamp": datetime.now().isoformat()
        }
    
    def _simulate_impedance_response(
        self,
        frequency: float,
        dc_voltage: float,
        ac_amplitude: float,
        reference: Dict[str, Any]
    ) -> Tuple[float, float]:
        """
        Simulate impedance response for a given frequency.
        Replace this with actual measurement code.
        
        Args:
            frequency (float): Frequency in Hz
            dc_voltage (float): DC bias voltage
            ac_amplitude (float): AC voltage amplitude
            reference (Dict[str, Any]): Reference electrode configuration
            
        Returns:
            Tuple[float, float]: Real and imaginary components of impedance
        """
        # Simple equivalent circuit simulation (R + RC parallel)
        # Replace with actual measurement
        R1 = 100.0  # Series resistance (Ω)
        R2 = 1000.0  # Charge transfer resistance (Ω)
        C = 1e-6  # Double layer capacitance (F)
        
        # Calculate impedance components
        omega = 2 * np.pi * frequency
        z_c = 1 / (1j * omega * C)  # Capacitor impedance
        z_parallel = (R2 * z_c) / (R2 + z_c)  # Parallel RC
        z_total = R1 + z_parallel  # Total impedance
        
        return float(z_total.real), float(z_total.imag)
    
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
        filename = f"peis_{timestamp}.json"
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
        "uo_type": "PEIS",
        "parameters": {
            "dc_voltage": 0.0,
            "ac_amplitude": 0.01,
            "start_frequency": 0.1,
            "end_frequency": 100000,
            "points_per_decade": 10,
            "arduino_control": {
                "base0_temp": 25.0,
                "pump0_ml": 2.5,
                "ultrasonic0_ms": 3000
            }
        }
    }
    
    # Create and run backend
    backend = PEISBackend()
    result = backend.execute_experiment(example_uo)
    print(f"Experiment result: {result}") 
