#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Processing Utilities

This module provides functions for processing and analyzing experimental data.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import json
import os
from datetime import datetime
import pandas as pd
from scipy import signal
import logging

logger = logging.getLogger(__name__)

def smooth_data(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Smooth data using a moving average filter.
    
    Args:
        data (np.ndarray): Input data array
        window_size (int): Size of the moving average window
        
    Returns:
        np.ndarray: Smoothed data
    """
    return pd.Series(data).rolling(window=window_size, center=True).mean().fillna(method='bfill').fillna(method='ffill').values

def calculate_derivatives(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate first and second derivatives using central differences.
    
    Args:
        x (np.ndarray): Independent variable array
        y (np.ndarray): Dependent variable array
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: First and second derivatives
    """
    first_deriv = np.gradient(y, x)
    second_deriv = np.gradient(first_deriv, x)
    return first_deriv, second_deriv

def find_peaks(data: np.ndarray, height: Optional[float] = None, 
               distance: Optional[int] = None) -> Dict[str, np.ndarray]:
    """
    Find peaks in data using scipy's find_peaks function.
    
    Args:
        data (np.ndarray): Input data array
        height (Optional[float]): Minimum peak height
        distance (Optional[int]): Minimum distance between peaks
        
    Returns:
        Dict[str, np.ndarray]: Dictionary containing peak indices and properties
    """
    peaks, properties = signal.find_peaks(data, height=height, distance=distance)
    return {"peaks": peaks, "properties": properties}

def calculate_area(x: List[float], y: List[float]) -> float:
    """
    Calculate area under curve using trapezoidal rule.
    
    Args:
        x (List[float]): X values
        y (List[float]): Y values
        
    Returns:
        float: Area under curve
    """
    return float(np.trapz(y, x))

def process_cv_data(voltage: np.ndarray, current: np.ndarray, 
                   scan_rate: float) -> Dict[str, Any]:
    """
    Process cyclic voltammetry data.
    
    Args:
        voltage (np.ndarray): Voltage data array
        current (np.ndarray): Current data array
        scan_rate (float): Scan rate in V/s
        
    Returns:
        Dict[str, Any]: Processed data including peaks and calculated parameters
    """
    # Smooth the current data
    current_smooth = smooth_data(current)
    
    # Find peaks
    peaks_forward = find_peaks(current_smooth, distance=20)
    peaks_reverse = find_peaks(-current_smooth, distance=20)
    
    # Calculate derivatives
    didt, d2idt2 = calculate_derivatives(voltage, current_smooth)
    
    return {
        "voltage": voltage,
        "current": current_smooth,
        "didt": didt,
        "d2idt2": d2idt2,
        "peaks_forward": peaks_forward,
        "peaks_reverse": peaks_reverse,
        "scan_rate": scan_rate
    }

def process_eis_data(frequency: np.ndarray, z_real: np.ndarray, 
                     z_imag: np.ndarray) -> Dict[str, Any]:
    """
    Process electrochemical impedance spectroscopy data.
    
    Args:
        frequency (np.ndarray): Frequency data array
        z_real (np.ndarray): Real impedance data array
        z_imag (np.ndarray): Imaginary impedance data array
        
    Returns:
        Dict[str, Any]: Processed data including magnitude and phase
    """
    # Calculate impedance magnitude and phase
    z_mag = np.sqrt(z_real**2 + z_imag**2)
    z_phase = np.arctan2(z_imag, z_real)
    
    return {
        "frequency": frequency,
        "z_real": z_real,
        "z_imag": z_imag,
        "z_magnitude": z_mag,
        "z_phase": z_phase
    }

def calculate_charge_capacity(time: np.ndarray, current: np.ndarray) -> float:
    """
    Calculate charge capacity from chronopotentiometry data.
    
    Args:
        time (np.ndarray): Time data array in seconds
        current (np.ndarray): Current data array in amperes
        
    Returns:
        float: Charge capacity in coulombs
    """
    return np.trapz(current, time)

def analyze_lsv_data(voltage: np.ndarray, current: np.ndarray) -> Dict[str, Any]:
    """
    Analyze linear sweep voltammetry data.
    
    Args:
        voltage (np.ndarray): Voltage data array
        current (np.ndarray): Current data array
        
    Returns:
        Dict[str, Any]: Analysis results including onset potential and peak current
    """
    # Smooth the current data
    current_smooth = smooth_data(current)
    
    # Calculate derivatives
    didt, _ = calculate_derivatives(voltage, current_smooth)
    
    # Find onset potential (point of maximum slope)
    onset_idx = np.argmax(didt)
    onset_potential = voltage[onset_idx]
    
    # Find peak current
    peak_idx = np.argmax(current_smooth)
    peak_current = current_smooth[peak_idx]
    peak_potential = voltage[peak_idx]
    
    return {
        "onset_potential": onset_potential,
        "peak_current": peak_current,
        "peak_potential": peak_potential,
        "voltage": voltage,
        "current_smooth": current_smooth,
        "didt": didt
    }

def export_to_csv(data: Dict[str, Any], filepath: str) -> None:
    """
    Export data to CSV file.
    
    Args:
        data (Dict[str, Any]): Data to export
        filepath (str): Output file path
    """
    import pandas as pd
    
    # Convert data to DataFrame
    if all(k in data for k in ['time', 'voltage', 'current']):
        # Time series data (CV, LSV, etc.)
        df = pd.DataFrame({
            'Time (s)': data['time'],
            'Voltage (V)': data['voltage'],
            'Current (A)': data['current']
        })
    elif all(k in data for k in ['frequencies', 'impedance_real', 'impedance_imag']):
        # EIS data
        df = pd.DataFrame({
            'Frequency (Hz)': data['frequencies'],
            'Z_real (Ω)': data['impedance_real'],
            'Z_imag (Ω)': data['impedance_imag']
        })
    else:
        raise ValueError("Unsupported data format for CSV export")
    
    # Save to file
    df.to_csv(filepath, index=False)

def load_experiment_data(filepath: str) -> Dict[str, Any]:
    """
    Load experiment data from JSON file.
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        Dict[str, Any]: Loaded data
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def save_experiment_data(data: Dict[str, Any], filepath: str) -> None:
    """
    Save experiment data to JSON file.
    
    Args:
        data (Dict[str, Any]): Data to save
        filepath (str): Output file path
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Add metadata
    data['metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    }
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2) 
