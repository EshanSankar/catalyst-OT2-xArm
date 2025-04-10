#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parameter Validation Utilities

This module provides functions for validating experiment parameters and configurations.
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for parameter validation errors."""
    pass

def load_limits(config_path: str = "config/parameter_limits.json") -> Dict[str, Any]:
    """
    Load parameter limits from a configuration file.
    
    Args:
        config_path (str): Path to the configuration file containing parameter limits.
        
    Returns:
        Dict[str, Any]: Dictionary containing parameter limits.
        
    Raises:
        FileNotFoundError: If the configuration file is not found.
        json.JSONDecodeError: If the configuration file is not valid JSON.
    """
    try:
        with open(config_path, 'r') as f:
            limits = json.load(f)
        return limits
    except FileNotFoundError:
        logger.warning(f"Parameter limits file not found at {config_path}. Using default limits.")
        return {
            "voltage": {"min": -10.0, "max": 10.0},
            "current": {"min": -2.0, "max": 2.0},
            "temperature": {"min": 10.0, "max": 80.0},
            "frequency": {"min": 0.1, "max": 1000000.0}
        }
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing parameter limits file: {e}")
        raise

def validate_voltage(voltage: float, limits: Optional[Dict[str, float]] = None) -> None:
    """
    Validate voltage parameter.
    
    Args:
        voltage (float): Voltage value to validate.
        limits (Optional[Dict[str, float]]): Dictionary containing min and max voltage limits.
        
    Raises:
        ValidationError: If voltage is outside valid range.
    """
    if limits is None:
        limits = load_limits()["voltage"]
    
    if not isinstance(voltage, (int, float)):
        raise ValidationError(f"Voltage must be a number, got {type(voltage)}")
    
    if voltage < limits["min"] or voltage > limits["max"]:
        raise ValidationError(
            f"Voltage {voltage}V is outside valid range [{limits['min']}, {limits['max']}]V"
        )

def validate_current(current: float, limits: Optional[Dict[str, float]] = None) -> None:
    """
    Validate current parameter.
    
    Args:
        current (float): Current value to validate.
        limits (Optional[Dict[str, float]]): Dictionary containing min and max current limits.
        
    Raises:
        ValidationError: If current is outside valid range.
    """
    if limits is None:
        limits = load_limits()["current"]
    
    if not isinstance(current, (int, float)):
        raise ValidationError(f"Current must be a number, got {type(current)}")
    
    if current < limits["min"] or current > limits["max"]:
        raise ValidationError(
            f"Current {current}A is outside valid range [{limits['min']}, {limits['max']}]A"
        )

def validate_temperature(temperature: float, limits: Optional[Dict[str, float]] = None) -> None:
    """
    Validate temperature parameter.
    
    Args:
        temperature (float): Temperature value to validate in Celsius.
        limits (Optional[Dict[str, float]]): Dictionary containing min and max temperature limits.
        
    Raises:
        ValidationError: If temperature is outside valid range.
    """
    if limits is None:
        limits = load_limits()["temperature"]
    
    if not isinstance(temperature, (int, float)):
        raise ValidationError(f"Temperature must be a number, got {type(temperature)}")
    
    if temperature < limits["min"] or temperature > limits["max"]:
        raise ValidationError(
            f"Temperature {temperature}°C is outside valid range [{limits['min']}, {limits['max']}]°C"
        )

def validate_frequency(frequency: float, limits: Optional[Dict[str, float]] = None) -> None:
    """
    Validate frequency parameter.
    
    Args:
        frequency (float): Frequency value to validate in Hz.
        limits (Optional[Dict[str, float]]): Dictionary containing min and max frequency limits.
        
    Raises:
        ValidationError: If frequency is outside valid range.
    """
    if limits is None:
        limits = load_limits()["frequency"]
    
    if not isinstance(frequency, (int, float)):
        raise ValidationError(f"Frequency must be a number, got {type(frequency)}")
    
    if frequency < limits["min"] or frequency > limits["max"]:
        raise ValidationError(
            f"Frequency {frequency}Hz is outside valid range [{limits['min']}, {limits['max']}]Hz"
        )

def validate_scan_rate(value: float) -> List[str]:
    """
    Validate scan rate value.
    
    Args:
        value (float): Scan rate value
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    if value <= 0:
        errors.append(f"Scan rate must be positive, got {value}V/s")
    if value > 10.0:
        errors.append(f"Scan rate {value}V/s is above maximum 10V/s")
    
    return errors

def validate_cycles(value: int) -> List[str]:
    """
    Validate number of cycles.
    
    Args:
        value (int): Number of cycles
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    if not isinstance(value, int):
        errors.append(f"Number of cycles must be an integer, got {type(value)}")
    elif value < 1:
        errors.append(f"Number of cycles must be positive, got {value}")
    elif value > 1000:
        errors.append(f"Number of cycles {value} is above maximum 1000")
    
    return errors

def validate_arduino_params(params: Dict[str, Any]) -> List[str]:
    """
    Validate Arduino control parameters.
    
    Args:
        params (Dict[str, Any]): Arduino parameters
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    # Temperature validation
    if 'base0_temp' in params:
        errors.extend(validate_temperature(params['base0_temp']))
    
    # Pump volume validation
    if 'pump0_ml' in params:
        volume = params['pump0_ml']
        if volume < 0:
            errors.append(f"Pump volume must be non-negative, got {volume}mL")
        if volume > 10:
            errors.append(f"Pump volume {volume}mL is above maximum 10mL")
    
    # Ultrasonic timing validation
    if 'ultrasonic0_ms' in params:
        timing = params['ultrasonic0_ms']
        if timing < 0:
            errors.append(f"Ultrasonic timing must be non-negative, got {timing}ms")
        if timing > 10000:
            errors.append(f"Ultrasonic timing {timing}ms is above maximum 10000ms")
    
    return errors

def validate_reference_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate reference electrode configuration.
    
    Args:
        config (Dict[str, Any]): Reference configuration
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    if 'type' not in config:
        errors.append("Reference type not specified")
    elif config['type'] not in ['RE', 'CE']:
        errors.append(f"Invalid reference type: {config['type']}")
    
    if 'enabled' not in config:
        errors.append("Reference enabled flag not specified")
    elif not isinstance(config['enabled'], bool):
        errors.append(f"Reference enabled must be boolean, got {type(config['enabled'])}")
    
    return errors

def validate_experiment_params(
    uo_type: str,
    params: Dict[str, Any],
    config_path: Optional[str] = None
) -> List[str]:
    """
    Validate experiment parameters based on UO type.
    
    Args:
        uo_type (str): Unit operation type
        params (Dict[str, Any]): Experiment parameters
        config_path (Optional[str]): Path to config file
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    # Load limits
    limits = load_limits(config_path)
    
    # Common validations
    if 'arduino_control' in params:
        errors.extend(validate_arduino_params(params['arduino_control']))
    
    if 'reference' in params:
        errors.extend(validate_reference_config(params['reference']))
    
    # Type-specific validations
    if uo_type == 'CVA':
        # Validate CV parameters
        if 'start_voltage' in params:
            errors.extend(validate_voltage(params['start_voltage'], limits.get('voltage')))
        if 'end_voltage' in params:
            errors.extend(validate_voltage(params['end_voltage'], limits.get('voltage')))
        if 'scan_rate' in params:
            errors.extend(validate_scan_rate(params['scan_rate']))
        if 'cycles' in params:
            errors.extend(validate_cycles(params['cycles']))
    
    elif uo_type == 'PEIS':
        # Validate PEIS parameters
        if 'start_frequency' in params:
            errors.extend(validate_frequency(params['start_frequency'], limits.get('frequency')))
        if 'end_frequency' in params:
            errors.extend(validate_frequency(params['end_frequency'], limits.get('frequency')))
        if 'dc_voltage' in params:
            errors.extend(validate_voltage(params['dc_voltage'], limits.get('voltage')))
    
    elif uo_type == 'CP':
        # Validate CP parameters
        if 'current' in params:
            errors.extend(validate_current(params['current'], limits.get('current')))
    
    elif uo_type == 'LSV':
        # Validate LSV parameters
        if 'start_voltage' in params:
            errors.extend(validate_voltage(params['start_voltage'], limits.get('voltage')))
        if 'end_voltage' in params:
            errors.extend(validate_voltage(params['end_voltage'], limits.get('voltage')))
        if 'scan_rate' in params:
            errors.extend(validate_scan_rate(params['scan_rate']))
    
    return errors 
