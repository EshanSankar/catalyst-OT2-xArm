# Device Connectivity Testing

This document provides instructions for testing connectivity to the OT-2 robot and Arduino.

## Prerequisites

- Python 3.6 or higher
- Virtual environment with required dependencies installed
- OT-2 robot connected to the network
- Arduino connected via USB (if applicable)

## Setting Up the Environment

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     source ./venv/Scripts/activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required dependencies:
   ```bash
   pip install --only-binary=:all: numpy pandas scipy matplotlib scikit-learn
   pip install pyserial pyyaml requests websockets boto3 python-dotenv aiohttp asyncio seaborn
   ```

## Test Scripts

Three test scripts are provided:

1. **test_connections.py**: Tests basic connectivity to the OT-2 robot and Arduino.
2. **test_ot2_api.py**: Tests the OT-2 robot's API endpoints.
3. **mock_opentrons.py**: Provides mock implementations for testing without actual hardware.

## Running the Tests

### Basic Connectivity Test

```bash
python test_connections.py
```

This script tests basic connectivity to the OT-2 robot and Arduino. If the actual hardware is not available, it will fall back to using the mock implementations.

To explicitly use the mock implementations:
```bash
python test_connections.py --mock
```

### API Endpoint Test

```bash
python test_ot2_api.py
```

This script tests the OT-2 robot's API endpoints and displays detailed information about the robot.

## Configuration

The test scripts use the IP address and COM port specified in `config/default_config.json`. You can override these by using command-line arguments:

```bash
python test_connections.py --ot2-ip 192.168.1.100 --arduino-port COM4
python test_ot2_api.py --ip 192.168.1.100
```

## Troubleshooting

If the tests fail, check the following:

1. **OT-2 Connectivity Issues**:
   - Ensure the OT-2 robot is powered on
   - Verify the IP address is correct
   - Check that your computer is on the same network as the OT-2
   - Try pinging the OT-2 IP address

2. **Arduino Connectivity Issues**:
   - Check if the Arduino is properly connected via USB
   - Verify the COM port is correct
   - Check if you have necessary permissions to access the port

3. **API Endpoint Issues**:
   - If the robot is reachable but the API endpoints are not responding, try restarting the OT-2 robot
   - Check if the robot's software needs to be updated

## Next Steps

After confirming basic connectivity, you can proceed to test more complex functionality:

1. **Running Simple Protocols**: Try running simple protocols on the OT-2 robot
2. **Testing Specific Hardware Features**: Test specific features of the OT-2 robot and Arduino
3. **Integration Testing**: Test the integration between the OT-2 robot, Arduino, and other components
