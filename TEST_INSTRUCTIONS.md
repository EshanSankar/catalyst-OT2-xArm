# Testing Instructions for Catalyst OT2-Arduino System

This document provides instructions for testing the device control functionality of the Catalyst OT2-Arduino System.

## Prerequisites

Before running the tests, ensure you have:

1. Python 3.8 or higher installed
2. OT-2 robot connected to the network
3. Arduino board connected via USB
4. All required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

## Device Connection Tests

The `test_device_control.py` script tests basic connectivity and functionality of the OT-2 robot and Arduino devices.

### Running the Device Tests

1. Connect the Arduino to your computer via USB
2. Ensure the OT-2 is powered on and connected to the network
3. Run the device test script:
   ```bash
   python test_device_control.py
   ```
4. Check the console output and the `device_test.log` file for results

### Expected Results

- The script will attempt to connect to the Arduino on common COM ports
- It will test basic Arduino functionality (temperature reading, LED control)
- It will attempt to connect to the OT-2 robot
- It will test basic OT-2 functionality (homing)

If all tests pass, you should see "All device tests PASSED" in the output.

## Experiment Control Tests

The `test_experiment_control.py` script tests the electrochemical experiment functionality.

### Running the Experiment Tests

1. Ensure both the Arduino and OT-2 are connected
2. Run the experiment test script:
   ```bash
   python test_experiment_control.py
   ```
3. Check the console output and the `experiment_test.log` file for results

### Expected Results

- The script will create test directories for experiment results
- It will simulate running Cyclic Voltammetry (CVA) and Open Circuit Voltage (OCV) experiments
- It will generate mock results files

If all tests pass, you should see "All experiment tests PASSED" in the output.

## Troubleshooting

### Arduino Connection Issues

- Check that the Arduino is properly connected via USB
- Verify the correct COM port in Device Manager (Windows) or using `ls /dev/tty*` (Linux/Mac)
- Ensure the Arduino has the correct firmware uploaded
- Try unplugging and reconnecting the Arduino

### OT-2 Connection Issues

- Verify the OT-2 is powered on
- Check network connectivity (try pinging the OT-2 IP address)
- Ensure the OT-2 IP address is correctly specified
- Check that no other applications are currently connected to the OT-2

### Experiment Execution Issues

- Check that all required Python modules are installed
- Verify that the experiment parameters are within valid ranges
- Ensure there is sufficient disk space for experiment results
- Check the log files for detailed error messages

## Running Real Experiments

After the basic tests pass, you can run actual experiments using the main experiment scripts:

- For electrodeposition experiments:
  ```bash
  python run_electrodeposition.py
  ```

- For automated corrosion experiments:
  ```bash
  python run_automatedCorrosion.py
  ```

- For cleaning platinum electrodes:
  ```bash
  python run_cleanPt.py
  ```

Each script will prompt for experiment parameters or read them from configuration files.

## Safety Precautions

- Always ensure proper ventilation when running experiments
- Wear appropriate personal protective equipment
- Follow all laboratory safety protocols
- Be prepared to manually stop experiments if necessary
- Keep emergency contact information readily available
