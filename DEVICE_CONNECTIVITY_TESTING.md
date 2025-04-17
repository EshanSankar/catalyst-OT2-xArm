# Device Connectivity and Functionality Testing

This document provides instructions for testing connectivity and functionality of the OT-2 robot, Arduino, and Biologic potentiostat.

## Prerequisites

- Python 3.6 or higher
- Virtual environment with required dependencies installed
- OT-2 robot connected to the network
- Arduino connected via USB
- Biologic potentiostat connected via USB (if applicable)

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
   pip install requests pyserial
   ```

## Test Scripts

Two test scripts are provided:

1. **test_device_connectivity.py**: Tests basic connectivity to the OT-2 robot, Arduino, and Biologic potentiostat.
2. **test_device_functionality.py**: Tests the functionality of the OT-2 robot and Arduino.

## Running the Tests

### Basic Connectivity Test

```bash
python test_device_connectivity.py
```

This script tests basic connectivity to the OT-2 robot, Arduino, and Biologic potentiostat. It checks if the devices are reachable and responding to basic commands.

### Functionality Test

```bash
python test_device_functionality.py
```

This script tests the functionality of the OT-2 robot and Arduino. It checks if the devices are functioning correctly by sending more complex commands and verifying the responses.

## Configuration

The test scripts use the configuration from `config/default_config.json`. You can modify this file to change the IP address of the OT-2 robot or the port of the Arduino.

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
   - Verify the Arduino firmware is correctly installed

3. **Biologic Connectivity Issues**:
   - Check if the Biologic potentiostat is properly connected via USB
   - Verify the Biologic drivers are installed
   - Check if you have necessary permissions to access the device

## Next Steps

After confirming basic connectivity and functionality, you can proceed to test more complex operations:

1. **Running Simple Protocols**: Try running simple protocols on the OT-2 robot
2. **Testing Specific Hardware Features**: Test specific features of the OT-2 robot and Arduino
3. **Integration Testing**: Test the integration between the OT-2 robot, Arduino, and Biologic potentiostat
