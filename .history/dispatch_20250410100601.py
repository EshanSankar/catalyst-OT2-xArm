#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Experiment dispatch module for electrochemical experiments.

This module handles the dispatching of experiments to their respective backend modules
based on the experiment type (uo_type).
"""

import logging
from typing import Dict, Any, Optional, Type
import importlib
from datetime import datetime

from parsing import parse_experiment_parameters

LOGGER = logging.getLogger(__name__)

class ExperimentDispatcher:
    """
    Dispatcher class for handling electrochemical experiments.
    
    This class manages the routing of experiment requests to their appropriate
    backend modules and handles the execution flow.
    """
    
    # Mapping of experiment types to their backend module and class names
    BACKEND_MAPPING = {
        "CVA": ("cva_backend", "CVABackend"),
        "PEIS": ("peis_backend", "PEISBackend"),
        "OCV": ("ocv_backend", "OCVBackend"),
        "CP": ("cp_backend", "CPBackend"),
        "LSV": ("lsv_backend", "LSVBackend")
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the experiment dispatcher.
        
        Args:
            config_path (Optional[str]): Path to global configuration file
        """
        self.config_path = config_path
        self.backend_instances = {}
    
    def _get_backend_instance(self, uo_type: str):
        """
        Get or create a backend instance for the given experiment type.
        
        Args:
            uo_type (str): Type of experiment (e.g., "CVA", "PEIS")
            
        Returns:
            Backend instance for the experiment type
            
        Raises:
            ValueError: If backend module cannot be found or instantiated
        """
        if uo_type not in self.BACKEND_MAPPING:
            raise ValueError(f"Unknown experiment type: {uo_type}")
        
        if uo_type not in self.backend_instances:
            try:
                module_name, class_name = self.BACKEND_MAPPING[uo_type]
                module = importlib.import_module(module_name)
                backend_class = getattr(module, class_name)
                self.backend_instances[uo_type] = backend_class(config_path=self.config_path)
                LOGGER.info(f"Created new {uo_type} backend instance")
            except Exception as e:
                LOGGER.error(f"Failed to create backend for {uo_type}: {str(e)}")
                raise ValueError(f"Failed to create backend for {uo_type}: {str(e)}")
        
        return self.backend_instances[uo_type]
    
    def execute_experiment(self, uo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an experiment based on the provided unit operation.
        
        Args:
            uo (Dict[str, Any]): Unit operation dictionary containing experiment parameters
            
        Returns:
            Dict[str, Any]: Results of the experiment
            
        Example:
            dispatcher = ExperimentDispatcher()
            result = dispatcher.execute_experiment({
                "uo_type": "CVA",
                "parameters": {
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
            })
        """
        try:
            # Parse and validate parameters
            parsed_uo = parse_experiment_parameters(uo)
            uo_type = parsed_uo["uo_type"]
            
            # Get backend instance
            backend = self._get_backend_instance(uo_type)
            
            # Execute experiment
            LOGGER.info(f"Executing {uo_type} experiment")
            result = backend.execute_experiment(parsed_uo)
            
            # Add metadata to result
            result.update({
                "uo_type": uo_type,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
        
        except Exception as e:
            LOGGER.error(f"Error executing experiment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup(self) -> None:
        """
        Clean up resources used by backend instances.
        Should be called when the dispatcher is no longer needed.
        """
        for uo_type, backend in self.backend_instances.items():
            try:
                backend.disconnect_devices()
                LOGGER.info(f"Cleaned up {uo_type} backend")
            except Exception as e:
                LOGGER.error(f"Error cleaning up {uo_type} backend: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Example experiment
    example_uo = {
        "uo_type": "CVA",
        "parameters": {
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
    }
    
    # Create dispatcher and run experiment
    dispatcher = ExperimentDispatcher()
    result = dispatcher.execute_experiment(example_uo)
    print(f"Experiment result: {result}")
    
    # Clean up
    dispatcher.cleanup() 
