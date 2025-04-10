#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parameter parsing and validation module for electrochemical experiments.

This module provides parameter parsing and validation functions for different
types of electrochemical experiments (CVA, PEIS, OCV, etc.).
"""

import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime

LOGGER = logging.getLogger(__name__)

# Common parameter validation functions
def validate_voltage(value: Union[str, float], param_name: str) -> float:
    """
    Validate and normalize voltage values.
    
    Args:
        value: Voltage value (can be string with unit or float)
        param_name: Name of the parameter for error messages
    
    Returns:
        float: Normalized voltage value in V
    
    Raises:
        ValueError: If voltage value is invalid
    """
    if isinstance(value, str):
        # Remove spaces and convert to uppercase
        value = value.replace(" ", "").upper()
        # Handle units
        if value.endswith("V"):
            try:
                return float(value[:-1])
            except ValueError:
                raise ValueError(f"Invalid voltage format for {param_name}: {value}")
        elif value.endswith("MV"):
            try:
                return float(value[:-2]) / 1000
            except ValueError:
                raise ValueError(f"Invalid voltage format for {param_name}: {value}")
    
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid voltage value for {param_name}: {value}")

def validate_frequency(value: Union[str, float], param_name: str) -> float:
    """
    Validate and normalize frequency values.
    
    Args:
        value: Frequency value (can be string with unit or float)
        param_name: Name of the parameter for error messages
    
    Returns:
        float: Normalized frequency value in Hz
    
    Raises:
        ValueError: If frequency value is invalid
    """
    if isinstance(value, str):
        value = value.replace(" ", "").upper()
        if value.endswith("HZ"):
            try:
                return float(value[:-2])
            except ValueError:
                raise ValueError(f"Invalid frequency format for {param_name}: {value}")
        elif value.endswith("KHZ"):
            try:
                return float(value[:-3]) * 1000
            except ValueError:
                raise ValueError(f"Invalid frequency format for {param_name}: {value}")
    
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid frequency value for {param_name}: {value}")

def validate_time(value: Union[str, float], param_name: str) -> float:
    """
    Validate and normalize time values.
    
    Args:
        value: Time value (can be string with unit or float)
        param_name: Name of the parameter for error messages
    
    Returns:
        float: Normalized time value in seconds
    
    Raises:
        ValueError: If time value is invalid
    """
    if isinstance(value, str):
        value = value.replace(" ", "").lower()
        if value.endswith("s"):
            try:
                return float(value[:-1])
            except ValueError:
                raise ValueError(f"Invalid time format for {param_name}: {value}")
        elif value.endswith("ms"):
            try:
                return float(value[:-2]) / 1000
            except ValueError:
                raise ValueError(f"Invalid time format for {param_name}: {value}")
        elif value.endswith("min"):
            try:
                return float(value[:-3]) * 60
            except ValueError:
                raise ValueError(f"Invalid time format for {param_name}: {value}")
    
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid time value for {param_name}: {value}")

# Experiment-specific parameter parsing

def parse_cva_parameters(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate CVA (Cyclic Voltammetry Analysis) parameters.
    
    Args:
        raw: Raw parameter dictionary from frontend
    
    Returns:
        Dict[str, Any]: Validated and normalized parameters
    
    Example input:
        {
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
    """
    try:
        params = {
            "start_voltage": validate_voltage(raw.get("start_voltage", 0.0), "start_voltage"),
            "end_voltage": validate_voltage(raw.get("end_voltage", 1.0), "end_voltage"),
            "scan_rate": float(raw.get("scan_rate", 0.05)),
            "cycles": int(raw.get("cycles", 1)),
        }
        
        # Copy Arduino control parameters if present
        if "arduino_control" in raw:
            params["arduino_control"] = raw["arduino_control"]
        
        LOGGER.info(f"Parsed CVA parameters: {params}")
        return params
    
    except Exception as e:
        LOGGER.error(f"Error parsing CVA parameters: {str(e)}")
        raise ValueError(f"Invalid CVA parameters: {str(e)}")

def parse_peis_parameters(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate PEIS parameters.
    
    Args:
        raw: Raw parameter dictionary from frontend
    
    Returns:
        Dict[str, Any]: Validated and normalized parameters
    
    Example input:
        {
            "start_freq": "100kHz",
            "end_freq": "1Hz",
            "amplitude": "5mV",
            "dc_voltage": "0.5V",
            "arduino_control": {
                "base0_temp": 60,
                "pump0_ml": 2.5,
                "ultrasonic0_ms": 3000
            }
        }
    """
    try:
        params = {
            "start_freq": validate_frequency(raw.get("start_freq", 100000), "start_freq"),
            "end_freq": validate_frequency(raw.get("end_freq", 1), "end_freq"),
            "amplitude": validate_voltage(raw.get("amplitude", 0.005), "amplitude"),
            "dc_voltage": validate_voltage(raw.get("dc_voltage", 0.5), "dc_voltage"),
        }
        
        if "arduino_control" in raw:
            params["arduino_control"] = raw["arduino_control"]
        
        LOGGER.info(f"Parsed PEIS parameters: {params}")
        return params
    
    except Exception as e:
        LOGGER.error(f"Error parsing PEIS parameters: {str(e)}")
        raise ValueError(f"Invalid PEIS parameters: {str(e)}")

def parse_ocv_parameters(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate OCV (Open Circuit Voltage) parameters.
    
    Args:
        raw: Raw parameter dictionary from frontend
    
    Returns:
        Dict[str, Any]: Validated and normalized parameters
    """
    try:
        params = {
            "duration": validate_time(raw.get("duration", 60), "duration"),
            "sample_interval": validate_time(raw.get("sample_interval", 1), "sample_interval"),
        }
        
        if "arduino_control" in raw:
            params["arduino_control"] = raw["arduino_control"]
        
        LOGGER.info(f"Parsed OCV parameters: {params}")
        return params
    
    except Exception as e:
        LOGGER.error(f"Error parsing OCV parameters: {str(e)}")
        raise ValueError(f"Invalid OCV parameters: {str(e)}")

def parse_cp_parameters(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate CP (Chronopotentiometry) parameters.
    
    Args:
        raw: Raw parameter dictionary from frontend
    
    Returns:
        Dict[str, Any]: Validated and normalized parameters
    """
    try:
        params = {
            "current": float(raw.get("current", 0.001)),
            "duration": validate_time(raw.get("duration", 60), "duration"),
            "sample_interval": validate_time(raw.get("sample_interval", 1), "sample_interval"),
        }
        
        if "arduino_control" in raw:
            params["arduino_control"] = raw["arduino_control"]
        
        LOGGER.info(f"Parsed CP parameters: {params}")
        return params
    
    except Exception as e:
        LOGGER.error(f"Error parsing CP parameters: {str(e)}")
        raise ValueError(f"Invalid CP parameters: {str(e)}")

def parse_lsv_parameters(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate LSV (Linear Sweep Voltammetry) parameters.
    
    Args:
        raw: Raw parameter dictionary from frontend
    
    Returns:
        Dict[str, Any]: Validated and normalized parameters
    """
    try:
        params = {
            "start_voltage": validate_voltage(raw.get("start_voltage", 0.0), "start_voltage"),
            "end_voltage": validate_voltage(raw.get("end_voltage", 1.0), "end_voltage"),
            "scan_rate": float(raw.get("scan_rate", 0.05)),
        }
        
        if "arduino_control" in raw:
            params["arduino_control"] = raw["arduino_control"]
        
        LOGGER.info(f"Parsed LSV parameters: {params}")
        return params
    
    except Exception as e:
        LOGGER.error(f"Error parsing LSV parameters: {str(e)}")
        raise ValueError(f"Invalid LSV parameters: {str(e)}")

# Parameter parser mapping
PARAMETER_PARSERS = {
    "CVA": parse_cva_parameters,
    "PEIS": parse_peis_parameters,
    "OCV": parse_ocv_parameters,
    "CP": parse_cp_parameters,
    "LSV": parse_lsv_parameters,
}

def parse_experiment_parameters(uo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for parsing experiment parameters.
    
    Args:
        uo: Unit operation dictionary containing experiment type and parameters
    
    Returns:
        Dict[str, Any]: Validated and normalized parameters
    
    Raises:
        ValueError: If experiment type is invalid or parameters are invalid
    """
    uo_type = uo.get("uo_type")
    if not uo_type:
        raise ValueError("Missing uo_type in experiment parameters")
    
    if uo_type not in PARAMETER_PARSERS:
        raise ValueError(f"Unknown experiment type: {uo_type}")
    
    raw_params = uo.get("parameters", {})
    parsed_params = PARAMETER_PARSERS[uo_type](raw_params)
    
    return {
        "uo_type": uo_type,
        "parameters": parsed_params,
        "timestamp": datetime.now().isoformat()
    } 
