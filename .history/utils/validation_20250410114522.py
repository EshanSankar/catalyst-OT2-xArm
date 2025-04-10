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

LOGGER = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def load_limits(config_path: Optional[str] = None) -> Dict[str, Dict[str, float]]:
    """
    Load parameter limits from configuration.
    
    Args:
        config_path (Optional[str]): Path to config file
        
    Returns:
        Dict[str, Dict[str, float]]: Parameter limits
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__), 
            '../config/default_config.json'
        )
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('limits', {})
    except Exception as e:
        LOGGER.error(f"Failed to load limits from {config_path}: {str(e)}")
        return {}

def validate_voltage(value: float, limits: Optional[Dict[str, float]] = None) -> List[str]:
    """
    Validate voltage value.
    
    Args:
        value (float): Voltage value
        limits (Optional[Dict[str, float]]): Voltage limits
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    if limits is None:
        limits = load_limits().get('voltage', {'min': -2.0, 'max': 2.0})
    
    if value < limits['min']:
        errors.append(f"Voltage {value}V is below minimum {limits['min']}V")
    if value > limits['max']:
        errors.append(f"Voltage {value}V is above maximum {limits['max']}V")
    
    return errors

def validate_current(value: float, limits: Optional[Dict[str, float]] = None) -> List[str]:
    """
    Validate current value.
    
    Args:
        value (float): Current value
        limits (Optional[Dict[str, float]]): Current limits
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    if limits is None:
        limits = load_limits().get('current', {'min': -1.0, 'max': 1.0})
    
    if value < limits['min']:
        errors.append(f"Current {value}A is below minimum {limits['min']}A")
    if value > limits['max']:
        errors.append(f"Current {value}A is above maximum {limits['max']}A")
    
    return errors

def validate_temperature(value: float, limits: Optional[Dict[str, float]] = None) -> List[str]:
    """
    Validate temperature value.
    
    Args:
        value (float): Temperature value
        limits (Optional[Dict[str, float]]): Temperature limits
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    if limits is None:
        limits = load_limits().get('temperature', {'min': 0.0, 'max': 100.0})
    
    if value < limits['min']:
        errors.append(f"Temperature {value}°C is below minimum {limits['min']}°C")
    if value > limits['max']:
        errors.append(f"Temperature {value}°C is above maximum {limits['max']}°C")
    
    return errors

def validate_frequency(value: float) -> List[str]:
    """
    Validate frequency value.
    
    Args:
        value (float): Frequency value
        
    Returns:
        List[str]: Validation error messages
    """
    errors = []
    
    if value <= 0:
        errors.append(f"Frequency must be positive, got {value}Hz")
    if value > 1e6:
        errors.append(f"Frequency {value}Hz is above maximum 1MHz")
    
    return errors

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
            errors.extend(validate_frequency(params['start_frequency']))
        if 'end_frequency' in params:
            errors.extend(validate_frequency(params['end_frequency']))
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
