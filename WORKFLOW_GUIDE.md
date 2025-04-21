# Electrochemical Workflow System Guide

This guide explains how to use the JSON workflow system, dispatch mechanism, and workflow executor to run electrochemical experiments.

## Components

1. **JSON Workflow Files**: Define experiments, their parameters, and execution flow
2. **Dispatch Mechanism**: Routes experiments to appropriate backend modules
3. **Workflow Executor**: Executes the workflow by processing nodes and edges

## Files

- `electrochemical_workflow.json`: Complete workflow definition with multiple experiments
- `cva_experiment.json`: Sample individual experiment definition
- `run_workflow.py`: Script to run a complete workflow
- `run_experiment.py`: Script to run an individual experiment

## Usage

### Running a Complete Workflow

```bash
python run_workflow.py electrochemical_workflow.json [options]
```

Options:
- `--schema`: Path to the schema JSON file (default: workflow_schema.json)
- `--mock`: Run in mock mode without connecting to real devices
- `--ip`: IP address of the OT-2 robot
- `--port`: Serial port of the Arduino
- `--results-dir`: Directory to store results (default: results)

### Running an Individual Experiment

```bash
python run_experiment.py cva_experiment.json [options]
```

Options:
- `--mock`: Run in mock mode without connecting to real devices
- `--ip`: IP address of the OT-2 robot
- `--port`: Serial port of the Arduino
- `--results-dir`: Directory to store results (default: results)

## Workflow JSON Structure

The workflow JSON file has the following structure:

```json
{
  "name": "Workflow Name",
  "version": "1.0.0",
  "description": "Workflow description",
  "global_config": {
    "labware": { ... },
    "instruments": { ... },
    "solutions": { ... },
    "arduino_control": { ... },
    "biologic_control": { ... }
  },
  "nodes": [
    {
      "id": "node1",
      "type": "OCV",
      "label": "Node Label",
      "params": {
        "duration_s": 300,
        "sample_rate": 1,
        ...
        "arduino_control": { ... },
        "ot2_actions": [ ... ]
      }
    },
    ...
  ],
  "edges": [
    {
      "source": "node1",
      "target": "node2"
    },
    ...
  ]
}
```

## Experiment JSON Structure

The individual experiment JSON file has the following structure:

```json
{
  "uo_type": "CVA",
  "parameters": {
    "start_voltage": "-0.2V",
    "end_voltage": "1.0V",
    "scan_rate": 0.05,
    "cycles": 3,
    "arduino_control": { ... },
    "ot2_actions": [ ... ]
  }
}
```

## Supported Experiment Types

- `OCV`: Open Circuit Voltage
- `CVA`: Cyclic Voltammetry Analysis
- `PEIS`: Potentiostatic Electrochemical Impedance Spectroscopy
- `CP`: Chronopotentiometry
- `LSV`: Linear Sweep Voltammetry

## How It Works

### Workflow Execution Process

1. The workflow JSON file is loaded and validated
2. The workflow executor processes the nodes and edges
3. For each node:
   - OT-2 actions are executed
   - Arduino control parameters are applied
   - The experiment is dispatched to the appropriate backend
   - Results are collected and stored

### Dispatch Mechanism

The dispatch mechanism:
1. Parses and validates experiment parameters
2. Generates a unique experiment ID
3. Routes the experiment to the appropriate backend module
4. Executes the experiment
5. Collects and uploads results

### Backend Modules

Each experiment type has a dedicated backend module that:
1. Connects to the required devices
2. Executes the specific experiment
3. Processes and returns the results

## Troubleshooting

If you encounter issues:

1. Check device connections
2. Verify IP addresses and port numbers
3. Validate JSON files against the schema
4. Check log files for detailed error messages

## Example Workflow

The provided `electrochemical_workflow.json` file contains a complete workflow with:
1. Initial OCV measurement
2. Cyclic Voltammetry Analysis
3. Electrochemical Impedance Spectroscopy
4. Linear Sweep Voltammetry
5. Cleanup and finalization

This workflow demonstrates the full capabilities of the system, including:
- Sequential experiment execution
- OT-2 robot control for electrode positioning
- Arduino control for temperature and pump operations
- Comprehensive parameter configuration
