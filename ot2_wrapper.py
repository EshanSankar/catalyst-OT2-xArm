#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OT-2 Wrapper

This module provides a wrapper for the opentronsClient class from opentronsHTTPAPI_clientBuilder.py.
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ot2_wrapper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("OT2Wrapper")

# Import the opentronsClient class from opentronsHTTPAPI_clientBuilder.py
try:
    # Import directly from the module
    from opentronsHTTPAPI_clientBuilder import opentronsClient
    LOGGER.info("Successfully imported opentronsClient from opentronsHTTPAPI_clientBuilder.py")
except ImportError as e:
    LOGGER.error(f"Failed to import opentronsClient: {str(e)}")
    
    # Try to import using importlib
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("opentronsHTTPAPI_clientBuilder", "opentronsHTTPAPI_clientBuilder.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        opentronsClient = module.opentronsClient
        LOGGER.info("Successfully imported opentronsClient using importlib")
    except Exception as e:
        LOGGER.error(f"Failed to import opentronsClient using importlib: {str(e)}")
        
        # Define a mock class as a fallback
        class opentronsClient:
            def __init__(self, strRobotIP="100.67.89.154"):
                self.robotIP = strRobotIP
                self.runID = "mock-run-id"
                LOGGER.warning(f"Using mock opentronsClient with IP: {strRobotIP}")
            
            def getRunInfo(self):
                LOGGER.warning("Mock getRunInfo called")
                return {"data": {"id": self.runID}}
            
            def lights(self, state):
                LOGGER.warning(f"Mock lights called with state: {state}")
            
            def homeRobot(self):
                LOGGER.warning("Mock homeRobot called")
            
            def loadLabware(self, intSlot, strLabwareName, strNamespace="opentrons", intVersion=1, strIntent="setup"):
                LOGGER.warning(f"Mock loadLabware called with labware: {strLabwareName} in slot: {intSlot}")
                return f"{strLabwareName}_{intSlot}"
            
            def loadPipette(self, strPipetteName, strMount):
                LOGGER.warning(f"Mock loadPipette called with pipette: {strPipetteName} on mount: {strMount}")
            
            def moveToWell(self, strLabwareName, strWellName, strPipetteName, strOffsetStart="top", fltOffsetX=0, fltOffsetY=0, fltOffsetZ=0, intSpeed=100):
                LOGGER.warning(f"Mock moveToWell called with labware: {strLabwareName}, well: {strWellName}")

# Test the wrapper
if __name__ == "__main__":
    try:
        client = opentronsClient(strRobotIP="100.67.89.154")
        print(f"Created opentronsClient with run ID: {client.runID}")
    except Exception as e:
        print(f"Failed to create opentronsClient: {str(e)}")
