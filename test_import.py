#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Import

This script tests importing the opentronsClient class from opentronsHTTPAPI_clientBuilder.py.
"""

import sys
import os

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Print files in current directory
print("Files in current directory:")
for file in os.listdir():
    print(f"  {file}")

# Try to import the opentronsClient class
try:
    print("Attempting to import opentronsHTTPAPI_clientBuilder...")
    import opentronsHTTPAPI_clientBuilder
    print(f"Module imported successfully. Contents: {dir(opentronsHTTPAPI_clientBuilder)}")
    
    if hasattr(opentronsHTTPAPI_clientBuilder, 'opentronsClient'):
        print("opentronsClient class found in module")
        
        # Try to create an instance
        client = opentronsHTTPAPI_clientBuilder.opentronsClient(strRobotIP="100.67.89.154")
        print(f"Successfully created client instance with run ID: {client.runID}")
    else:
        print("opentronsClient class NOT found in module")
except Exception as e:
    print(f"Error importing module: {str(e)}")
    import traceback
    traceback.print_exc()
