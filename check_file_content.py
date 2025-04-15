#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Check File Content

This script checks the content of the opentronsHTTPAPI_clientBuilder.py file.
"""

import os

# Check if the file exists
if os.path.exists("opentronsHTTPAPI_clientBuilder.py"):
    print("File exists")
    
    # Get the file size
    file_size = os.path.getsize("opentronsHTTPAPI_clientBuilder.py")
    print(f"File size: {file_size} bytes")
    
    # Read the file content
    with open("opentronsHTTPAPI_clientBuilder.py", "r") as f:
        content = f.read()
        
    # Check if the file contains the opentronsClient class
    if "class opentronsClient" in content:
        print("File contains 'class opentronsClient'")
        
        # Find the line number where the class is defined
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "class opentronsClient" in line:
                print(f"Class defined on line {i+1}: {line}")
                break
    else:
        print("File does NOT contain 'class opentronsClient'")
        
    # Print the first 100 characters of the file
    print(f"First 100 characters: {content[:100]}")
    
    # Print the number of lines in the file
    print(f"Number of lines: {len(content.split(chr(10)))}")
    
    # Check for BOM (Byte Order Mark)
    if content.startswith("\ufeff"):
        print("File starts with BOM (Byte Order Mark)")
    else:
        print("File does NOT start with BOM")
else:
    print("File does NOT exist")
