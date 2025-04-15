#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Direct Import

This script tests directly importing the opentronsClient class from opentronsHTTPAPI_clientBuilder.py.
"""

import sys
import os
import importlib.util

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Try to import using importlib
try:
    print("Attempting to import using importlib...")
    spec = importlib.util.spec_from_file_location("opentronsHTTPAPI_clientBuilder", "opentronsHTTPAPI_clientBuilder.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    print(f"Module imported successfully. Contents: {dir(module)}")
    
    if hasattr(module, 'opentronsClient'):
        print("opentronsClient class found in module")
        
        # Try to create an instance
        client = module.opentronsClient(strRobotIP="100.67.89.154")
        print(f"Successfully created client instance with run ID: {client.runID}")
    else:
        print("opentronsClient class NOT found in module")
        
        # Check if the file exists and has content
        if os.path.exists("opentronsHTTPAPI_clientBuilder.py"):
            with open("opentronsHTTPAPI_clientBuilder.py", "r") as f:
                content = f.read()
                print(f"File exists and has {len(content)} characters")
                print(f"First 100 characters: {content[:100]}")
                print(f"Contains 'class opentronsClient': {'class opentronsClient' in content}")
        else:
            print("File does not exist")
except Exception as e:
    print(f"Error importing module: {str(e)}")
    import traceback
    traceback.print_exc()
