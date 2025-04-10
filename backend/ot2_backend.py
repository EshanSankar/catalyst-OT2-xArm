#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OT2 Backend Module

This module handles the execution of OT-2 robot operations, including:
- Pipetting
- Plate/tip handling
- Washing
- Custom protocols
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from OT2_control import opentronsClient

# Configure logging
LOGGER = logging.getLogger(__name__)

class OT2Backend:
    """
    Backend class for OT-2 robot operations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the OT2 backend.
        
        Args:
            config_path (Optional[str]): Path to configuration file
        """
        self.config = self._load_config(config_path) if config_path else {}
        self.ot2_client = None
        LOGGER.info("OT2 Backend initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            LOGGER.error(f"Failed to load config from {config_path}: {str(e)}")
            return {}
    
    def connect_device(self) -> bool:
        """Connect to OT-2 device."""
        try:
            robot_ip = self.config.get("robot_ip", "100.67.89.154")
            self.ot2_client = opentronsClient(strRobotIP=robot_ip)
            LOGGER.info("Connected to OT-2")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to connect to OT-2: {str(e)}")
            return False
    
    def execute_operation(self, uo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an OT-2 operation based on the provided UO.
        
        Args:
            uo (Dict[str, Any]): Unit operation dictionary containing:
                - operation_type: str (pipette/wash/custom)
                - parameters: Dict[str, Any]
                
        Returns:
            Dict[str, Any]: Operation results
        """
        LOGGER.info(f"Executing OT2 operation: {uo}")
        
        # Connect if not connected
        if not self.ot2_client:
            if not self.connect_device():
                return {"status": "error", "message": "Failed to connect to OT-2"}
        
        try:
            operation_type = uo.get("operation_type", "")
            params = uo.get("parameters", {})
            
            if operation_type == "pipette":
                return self._execute_pipette(params)
            elif operation_type == "wash":
                return self._execute_wash(params)
            elif operation_type == "custom":
                return self._execute_custom_protocol(params)
            else:
                return {"status": "error", "message": f"Unknown operation type: {operation_type}"}
                
        except Exception as e:
            LOGGER.error(f"Error executing OT2 operation: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _execute_pipette(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipetting operation."""
        source = params.get("source", {})
        destination = params.get("destination", {})
        volume = params.get("volume", 0.0)
        
        LOGGER.info(f"Pipetting {volume}µL from {source} to {destination}")
        
        # Add actual pipetting code here
        # self.ot2_client.transfer(...)
        
        return {
            "status": "success",
            "operation": "pipette",
            "details": {
                "source": source,
                "destination": destination,
                "volume": volume
            }
        }
    
    def _execute_wash(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute washing operation."""
        target = params.get("target", {})
        cycles = params.get("cycles", 1)
        wash_volume = params.get("wash_volume", 0.0)
        
        LOGGER.info(f"Washing {target} with {wash_volume}µL for {cycles} cycles")
        
        # Add actual washing code here
        # self.ot2_client.wash(...)
        
        return {
            "status": "success",
            "operation": "wash",
            "details": {
                "target": target,
                "cycles": cycles,
                "wash_volume": wash_volume
            }
        }
    
    def _execute_custom_protocol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom protocol."""
        protocol_name = params.get("protocol_name", "")
        protocol_params = params.get("protocol_params", {})
        
        LOGGER.info(f"Executing custom protocol: {protocol_name}")
        
        # Add custom protocol execution code here
        # self.ot2_client.run_custom(...)
        
        return {
            "status": "success",
            "operation": "custom",
            "details": {
                "protocol": protocol_name,
                "parameters": protocol_params
            }
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Example pipetting operation
    example_uo = {
        "operation_type": "pipette",
        "parameters": {
            "source": {
                "labware": "plate_96_well",
                "position": "A1"
            },
            "destination": {
                "labware": "plate_96_well",
                "position": "B1"
            },
            "volume": 100.0  # µL
        }
    }
    
    # Create and run backend
    backend = OT2Backend()
    result = backend.execute_operation(example_uo)
    print(f"Operation result: {result}") 
