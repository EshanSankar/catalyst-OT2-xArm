#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Experiment dispatch module for electrochemical experiments.

This module handles the dispatching of experiments to their respective backend modules
based on the experiment type (uo_type).
"""

import logging
from typing import Dict, Any, Optional, Type, Callable
import importlib
from datetime import datetime
import uuid
import os
from abc import ABC, abstractmethod

from parsing import parse_experiment_parameters

LOGGER = logging.getLogger(__name__)

class ResultUploader(ABC):
    """Abstract base class for result uploaders."""
    
    @abstractmethod
    def upload(self, results: Dict[str, Any], experiment_id: str) -> bool:
        """
        Upload experiment results to storage.
        
        Args:
            results: Experiment results to upload
            experiment_id: Unique experiment identifier
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        pass

class LocalResultUploader(ResultUploader):
    """Save results to local filesystem."""
    
    def __init__(self, base_dir: str = "results"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def upload(self, results: Dict[str, Any], experiment_id: str) -> bool:
        try:
            # Create experiment directory
            exp_dir = os.path.join(self.base_dir, experiment_id)
            os.makedirs(exp_dir, exist_ok=True)
            
            # Save results as JSON
            import json
            result_path = os.path.join(exp_dir, "results.json")
            with open(result_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            LOGGER.info(f"Saved results to {result_path}")
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to save results: {str(e)}")
            return False

class S3ResultUploader(ResultUploader):
    """Upload results to S3."""
    
    def __init__(self, bucket: str, prefix: str = "experiments"):
        # Import boto3 only when S3 uploader is used
        import boto3
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.prefix = prefix
    
    def upload(self, results: Dict[str, Any], experiment_id: str) -> bool:
        try:
            # Convert results to JSON string
            import json
            results_json = json.dumps(results, indent=2)
            
            # Upload to S3
            key = f"{self.prefix}/{experiment_id}/results.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=results_json
            )
            
            LOGGER.info(f"Uploaded results to s3://{self.bucket}/{key}")
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to upload results to S3: {str(e)}")
            return False

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
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        result_uploader: Optional[ResultUploader] = None
    ):
        """
        Initialize the experiment dispatcher.
        
        Args:
            config_path: Path to global configuration file
            result_uploader: Optional result uploader instance
        """
        self.config_path = config_path
        self.backend_instances = {}
        self.result_uploader = result_uploader or LocalResultUploader()
    
    def _generate_experiment_id(self, uo_type: str) -> str:
        """
        Generate a unique experiment ID.
        
        Args:
            uo_type: Type of experiment (e.g., "CVA", "PEIS")
            
        Returns:
            str: Unique experiment ID in format: {timestamp}_{uo_type}_{uuid}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
        return f"{timestamp}_{uo_type}_{unique_id}"
    
    def _get_backend_instance(self, uo_type: str):
        """
        Get or create a backend instance for the given experiment type.
        
        Args:
            uo_type: Type of experiment (e.g., "CVA", "PEIS")
            
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
                self.backend_instances[uo_type] = backend_class(
                    config_path=self.config_path,
                    result_uploader=self.result_uploader
                )
                LOGGER.info(f"Created new {uo_type} backend instance")
            except Exception as e:
                LOGGER.error(f"Failed to create backend for {uo_type}: {str(e)}")
                raise ValueError(f"Failed to create backend for {uo_type}: {str(e)}")
        
        return self.backend_instances[uo_type]
    
    def execute_experiment(self, uo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an experiment based on the provided unit operation.
        
        Args:
            uo: Unit operation dictionary containing experiment parameters
            
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
            
            # Generate experiment ID
            experiment_id = self._generate_experiment_id(uo_type)
            parsed_uo["experiment_id"] = experiment_id
            
            # Get backend instance
            backend = self._get_backend_instance(uo_type)
            
            # Execute experiment
            LOGGER.info(f"Executing {uo_type} experiment (ID: {experiment_id})")
            result = backend.execute_experiment(parsed_uo)
            
            # Add metadata to result
            result.update({
                "experiment_id": experiment_id,
                "uo_type": uo_type,
                "timestamp": datetime.now().isoformat()
            })
            
            # Upload results
            if not self.result_uploader.upload(result, experiment_id):
                LOGGER.warning(f"Failed to upload results for experiment {experiment_id}")
            
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
    
    # Create dispatcher with local result uploader
    dispatcher = ExperimentDispatcher(
        result_uploader=LocalResultUploader("experiment_results")
    )
    
    # Run experiment
    result = dispatcher.execute_experiment(example_uo)
    print(f"Experiment result: {result}")
    
    # Clean up
    dispatcher.cleanup() 
