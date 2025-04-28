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
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from backends.base import BaseBackend

# Configure logging
LOGGER = logging.getLogger(__name__)

class PEISBackend(BaseBackend):
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
        super().__init__(config_path, result_uploader, experiment_type="PEIS")
    
    def _execute_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
        
        self.logger.info(f"Executing PEIS measurement: DC voltage {dc_voltage}V, "
                       f"AC amplitude {ac_amplitude}V, reference: {reference}")
        
        # Generate frequency points
        frequencies = self._generate_frequency_points(params)
        self.logger.info(f"Frequency sweep from {frequencies[0]:.2f} Hz to {frequencies[-1]:.2f} Hz")
        
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
            
        # Calculate impedance magnitude
        impedance_mag = [np.sqrt(r**2 + i**2) for r, i in zip(impedance_real, impedance_imag)]
        
        # Convert phase to degrees
        phase_degrees = [np.degrees(phase) for phase in phase_angles]
        
        return {
            "frequencies": frequencies.tolist(),
            "impedance_real": impedance_real,
            "impedance_imag": impedance_imag,
            "impedance_magnitude": impedance_mag,
            "phase_angle": phase_degrees,
            "parameters": {
                "dc_voltage": dc_voltage,
                "ac_amplitude": ac_amplitude,
                "reference": reference,
                "frequency_range": [frequencies[0], frequencies[-1]],
                "points_per_decade": params.get("points_per_decade", 10)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_frequency_points(self, params: Dict[str, Any]) -> np.ndarray:
        """
        Generate frequency points for EIS measurement.
        
        Args:
            params (Dict[str, Any]): Experiment parameters
            
        Returns:
            np.ndarray: Array of frequency points
        """
        # Extract frequency parameters
        f_start = params.get("frequency_start", 0.1)  # Hz
        f_end = params.get("frequency_end", 100000)  # Hz
        points_per_decade = params.get("points_per_decade", 10)
        
        # Calculate number of decades
        decades = np.log10(f_end / f_start)
        total_points = int(decades * points_per_decade)
        
        # Generate logarithmically spaced frequency points
        return np.logspace(np.log10(f_start), np.log10(f_end), total_points)
    
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
            ac_amplitude (float): AC amplitude
            reference (Dict[str, Any]): Reference electrode configuration
            
        Returns:
            Tuple[float, float]: Real and imaginary parts of impedance
        """
        # Simple simulation of EIS response
        # Replace with actual measurement
        
        # Simulate a simple RC circuit
        R = 1000  # Resistance in ohms
        C = 1e-6  # Capacitance in F
        
        # Calculate impedance components
        omega = 2 * np.pi * frequency
        z_real = R / (1 + (omega * R * C)**2)
        z_imag = -omega * R**2 * C / (1 + (omega * R * C)**2)
        
        # Add some noise
        noise_level = 0.05  # 5% noise
        z_real *= (1 + noise_level * (np.random.random() - 0.5))
        z_imag *= (1 + noise_level * (np.random.random() - 0.5))
        
        return z_real, z_imag
    
    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """
        Validate PEIS-specific parameters.
        
        Args:
            params (Dict[str, Any]): Parameters to validate
            
        Returns:
            List[str]: List of validation error messages (empty if valid)
        """
        errors = super().validate_parameters(params)
        
        # Validate PEIS-specific parameters
        dc_voltage = params.get("dc_voltage")
        ac_amplitude = params.get("ac_amplitude")
        f_start = params.get("frequency_start")
        f_end = params.get("frequency_end")
        
        if dc_voltage is not None and (dc_voltage < -2.0 or dc_voltage > 2.0):
            errors.append("DC voltage must be between -2.0V and 2.0V")
            
        if ac_amplitude is not None and (ac_amplitude <= 0 or ac_amplitude > 0.1):
            errors.append("AC amplitude must be between 0 and 0.1V")
            
        if f_start is not None and f_start <= 0:
            errors.append("Start frequency must be positive")
            
        if f_end is not None and f_end <= 0:
            errors.append("End frequency must be positive")
            
        if f_start is not None and f_end is not None and f_start >= f_end:
            errors.append("Start frequency must be less than end frequency")
            
        return errors
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """
        Get default parameters for PEIS experiments.
        
        Returns:
            Dict[str, Any]: Default parameters
        """
        params = super().get_default_parameters()
        params.update({
            "dc_voltage": 0.0,
            "ac_amplitude": 0.01,
            "frequency_start": 0.1,
            "frequency_end": 100000,
            "points_per_decade": 10,
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
        "uo_type": "PEIS",
        "parameters": {
            "dc_voltage": 0.5,
            "ac_amplitude": 0.01,
            "frequency_start": 1.0,
            "frequency_end": 10000,
            "points_per_decade": 5,
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
