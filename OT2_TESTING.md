# OT2 Robot Connectivity Testing

This document provides instructions for testing connectivity to the OT2 robot using the provided test scripts.

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - requests
  - argparse

## Test Scripts

Three test scripts are provided with increasing levels of detail:

1. **simple_ot2_test.py**: Basic connectivity test that checks if the OT2 robot is reachable.
2. **comprehensive_ot2_test.py**: More detailed test that checks multiple API endpoints.
3. **ot2_connectivity_test.py**: Complete test suite with ping test, API endpoint tests, and troubleshooting tips.

## Configuration

The test scripts use the IP address specified in `config/default_config.json`. The default IP address is `100.67.89.154`. You can override this by using the `--ip` command-line argument.

## Running the Tests

### Basic Connectivity Test

```bash
python simple_ot2_test.py
```

This script sends a GET request to the OT2's health endpoint to check if it's reachable.

### Comprehensive Test

```bash
python comprehensive_ot2_test.py
```

This script tests multiple API endpoints and displays detailed information about the robot.

### Complete Test Suite

```bash
python ot2_connectivity_test.py
```

This script performs a ping test, tests multiple API endpoints, and provides troubleshooting tips if any test fails.

#### Command-line Arguments

- `--ip IP_ADDRESS`: Specify the IP address of the OT2 robot
- `--timeout SECONDS`: Specify the timeout for API requests in seconds (default: 5)
- `--skip-ping`: Skip the ping test

Example:
```bash
python ot2_connectivity_test.py --ip 192.168.1.100 --timeout 10 --skip-ping
```

## Interpreting Results

The test scripts will display detailed information about the OT2 robot if the tests are successful, including:

- Basic information (name, model, serial number, etc.)
- Attached pipettes
- Attached modules

If any test fails, the scripts will display error messages and troubleshooting tips.

## Troubleshooting

If the tests fail, check the following:

1. **Network Connectivity Issues**:
   - Ensure the OT2 robot is powered on
   - Verify the IP address is correct
   - Check that your computer is on the same network as the OT2
   - Check network cables or Wi-Fi connection

2. **API Service Issues**:
   - If the robot is reachable but the API service is not responding, try restarting the OT2 robot
   - Check if the robot's software needs to be updated

3. **API Endpoint Issues**:
   - If some API endpoints are not responding, this may indicate a software issue on the robot
   - Try restarting the robot's API service

For more help, contact Opentrons support or refer to the documentation.
