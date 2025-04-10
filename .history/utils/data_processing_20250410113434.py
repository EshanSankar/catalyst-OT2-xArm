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

def smooth_data(data: List[float], window_size: int = 5) -> List[float]:
    """
    Apply moving average smoothing to data.
    
    Args:
        data (List[float]): Input data
        window_size (int): Size of moving average window
        
    Returns:
        List[float]: Smoothed data
    """
    return list(np.convolve(data, np.ones(window_size)/window_size, mode='valid'))

def calculate_derivative(x: List[float], y: List[float]) -> List[float]:
    """
    Calculate numerical derivative dy/dx.
    
    Args:
        x (List[float]): X values
        y (List[float]): Y values
        
    Returns:
        List[float]: Derivative values
    """
    return list(np.gradient(y, x))

def find_peaks(data: List[float], height: Optional[float] = None, 
              distance: Optional[int] = None) -> Tuple[List[int], List[float]]:
    """
    Find peaks in data.
    
    Args:
        data (List[float]): Input data
        height (Optional[float]): Minimum peak height
        distance (Optional[int]): Minimum distance between peaks
        
    Returns:
        Tuple[List[int], List[float]]: Peak indices and heights
    """
    from scipy.signal import find_peaks as sp_find_peaks
    
    peaks, properties = sp_find_peaks(data, height=height, distance=distance)
    return list(peaks), list(properties['peak_heights'])

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

def process_cv_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process cyclic voltammetry data.
    
    Args:
        data (Dict[str, Any]): Raw CV data
        
    Returns:
        Dict[str, Any]: Processed data including peaks and areas
    """
    voltage = data['voltage']
    current = data['current']
    
    # Find oxidation and reduction peaks
    pos_peaks, pos_heights = find_peaks(current, height=0)
    neg_peaks, neg_heights = find_peaks([-c for c in current], height=0)
    
    # Calculate areas
    pos_area = calculate_area(voltage[:len(voltage)//2], current[:len(current)//2])
    neg_area = calculate_area(voltage[len(voltage)//2:], current[len(current)//2:])
    
    return {
        'oxidation_peaks': [{'voltage': voltage[i], 'current': current[i]} 
                           for i in pos_peaks],
        'reduction_peaks': [{'voltage': voltage[i], 'current': current[i]} 
                          for i in neg_peaks],
        'oxidation_area': pos_area,
        'reduction_area': neg_area,
        'peak_separation': abs(voltage[pos_peaks[0]] - voltage[neg_peaks[0]]) 
                          if pos_peaks and neg_peaks else None
    }

def process_eis_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process electrochemical impedance spectroscopy data.
    
    Args:
        data (Dict[str, Any]): Raw EIS data
        
    Returns:
        Dict[str, Any]: Processed data including circuit parameters
    """
    from scipy.optimize import curve_fit
    
    # Extract data
    frequencies = np.array(data['frequencies'])
    z_real = np.array(data['impedance_real'])
    z_imag = np.array(data['impedance_imag'])
    
    # Simple Randles circuit fitting
    def randles_circuit(f, Rs, Rct, Cdl):
        omega = 2 * np.pi * f
        Z_cdl = 1 / (1j * omega * Cdl)
        Z = Rs + (Rct * Z_cdl) / (Rct + Z_cdl)
        return np.concatenate([Z.real, Z.imag])
    
    # Fit circuit parameters
    try:
        popt, _ = curve_fit(
            randles_circuit, 
            frequencies, 
            np.concatenate([z_real, z_imag]),
            p0=[100, 1000, 1e-6]
        )
        Rs, Rct, Cdl = popt
    except:
        Rs = Rct = Cdl = None
    
    return {
        'circuit_parameters': {
            'Rs': Rs,  # Solution resistance
            'Rct': Rct,  # Charge transfer resistance
            'Cdl': Cdl  # Double layer capacitance
        },
        'nyquist_data': {
            'z_real': z_real.tolist(),
            'z_imag': z_imag.tolist()
        },
        'bode_data': {
            'frequencies': frequencies.tolist(),
            'magnitude': np.sqrt(z_real**2 + z_imag**2).tolist(),
            'phase': np.arctan2(z_imag, z_real).tolist()
        }
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
