#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON Schema Validator for workflow files.

This script validates workflow JSON files against a defined schema to
ensure they have the correct structure and data types.
"""

import json
import sys
import logging
from jsonschema import validate, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

def load_json_file(file_path):
    """Load JSON from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        LOGGER.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        LOGGER.error(f"Invalid JSON in {file_path}: {e}")
        return None

def validate_workflow(workflow_file, schema_file="workflow_schema.json"):
    """
    Validate a workflow JSON file against schema.
    
    Args:
        workflow_file (str): Path to workflow JSON file
        schema_file (str): Path to schema JSON file
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Load schema
    schema = load_json_file(schema_file)
    if schema is None:
        return False
        
    # Load workflow
    workflow = load_json_file(workflow_file)
    if workflow is None:
        return False
    
    # Validate
    try:
        validate(instance=workflow, schema=schema)
        LOGGER.info(f"Workflow file {workflow_file} is valid!")
        return True
    except ValidationError as e:
        LOGGER.error(f"Validation error: {e.message}")
        # Print more context about where the error occurred
        if e.path:
            path_str = " -> ".join([str(p) for p in e.path])
            LOGGER.error(f"Error location: {path_str}")
        return False

def validate_workflow_json(workflow_file, schema_file="workflow_schema.json"):
    """
    Validate a workflow JSON file against schema.
    
    Args:
        workflow_file (str): Path to workflow JSON file
        schema_file (str): Path to schema JSON file
    
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValueError: If validation fails with details of the error
    """
    try:
        # Load schema
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
        except FileNotFoundError:
            LOGGER.warning(f"Schema file {schema_file} not found. Skipping validation.")
            return True
        except json.JSONDecodeError as e:
            LOGGER.warning(f"Invalid JSON in schema file {schema_file}: {e}. Skipping validation.")
            return True
            
        # Load workflow
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Workflow file {workflow_file} not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in workflow file {workflow_file}: {e}")
        
        # Validate
        validate(instance=workflow, schema=schema)
        LOGGER.info(f"Workflow file {workflow_file} is valid!")
        return True
        
    except ValidationError as e:
        error_message = f"Validation error: {e.message}"
        if e.path:
            path_str = " -> ".join([str(p) for p in e.path])
            error_message += f" at: {path_str}"
        raise ValueError(error_message)
    except ImportError:
        LOGGER.warning("jsonschema library not installed. Skipping validation.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_workflow.py <workflow_json_file> [schema_json_file]")
        sys.exit(1)
        
    workflow_file = sys.argv[1]
    schema_file = sys.argv[2] if len(sys.argv) > 2 else "workflow_schema.json"
    
    if validate_workflow(workflow_file, schema_file):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
