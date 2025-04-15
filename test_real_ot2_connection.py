#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Real OT-2 Connection

This script tests the connection to a real OT-2 robot using the opentronsHTTPAPI_clientBuilder.py file.
It performs basic operations to verify the connection is working properly.
"""

import sys
import logging
import argparse
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("real_ot2_connection_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger("RealOT2ConnectionTest")

def test_real_ot2_connection(robot_ip="100.67.89.154"):
    """Test connection to a real OT-2 robot."""
    try:
        # Try multiple approaches to import the opentronsClient class
        LOGGER.info("Trying multiple approaches to import opentronsClient class...")

        # Approach 1: Direct import
        try:
            LOGGER.info("Approach 1: Direct import...")
            from opentronsHTTPAPI_clientBuilder import opentronsClient
            LOGGER.info("Successfully imported opentronsClient using direct import")
        except ImportError as e:
            LOGGER.warning(f"Direct import failed: {str(e)}")

            # Approach 2: Using sys.path.append
            try:
                LOGGER.info("Approach 2: Using sys.path.append...")
                import sys
                import os
                current_dir = os.getcwd()
                LOGGER.info(f"Current directory: {current_dir}")
                if current_dir not in sys.path:
                    sys.path.append(current_dir)
                    LOGGER.info(f"Added {current_dir} to sys.path")
                from opentronsHTTPAPI_clientBuilder import opentronsClient
                LOGGER.info("Successfully imported opentronsClient using sys.path.append")
            except ImportError as e:
                LOGGER.warning(f"sys.path.append approach failed: {str(e)}")

                # Approach 3: Using importlib with exec
                try:
                    LOGGER.info("Approach 3: Using importlib with exec...")
                    import importlib.util
                    file_path = os.path.join(current_dir, "opentronsHTTPAPI_clientBuilder.py")
                    LOGGER.info(f"File path: {file_path}")

                    # Read the file content
                    with open(file_path, "r") as f:
                        file_content = f.read()

                    # Create a namespace
                    namespace = {}

                    # Execute the file content in the namespace
                    exec(file_content, namespace)

                    # Check if opentronsClient is in the namespace
                    if 'opentronsClient' in namespace:
                        opentronsClient = namespace['opentronsClient']
                        LOGGER.info("Successfully imported opentronsClient using exec")
                    else:
                        LOGGER.error("opentronsClient class not found in namespace after exec")
                        raise ImportError("opentronsClient class not found in namespace after exec")
                except Exception as e:
                    LOGGER.error(f"All import approaches failed: {str(e)}")
                    raise ImportError(f"Failed to import opentronsClient: {str(e)}")

        # Create a client instance
        LOGGER.info(f"Connecting to OT-2 at {robot_ip}...")
        ot2_client = opentronsClient(strRobotIP=robot_ip)
        LOGGER.info(f"Successfully connected to OT-2 with run ID: {ot2_client.runID}")

        # Get run info
        LOGGER.info("Getting run info...")
        run_info = ot2_client.getRunInfo()
        LOGGER.info(f"Run info retrieved successfully")

        # Turn on the lights
        LOGGER.info("Turning on the lights...")
        ot2_client.lights("true")
        LOGGER.info("Lights turned on")
        time.sleep(2)  # Wait for 2 seconds to see the lights

        # Home the robot
        LOGGER.info("Homing the robot...")
        ot2_client.homeRobot()
        LOGGER.info("Robot homed successfully")

        # Load a tip rack
        LOGGER.info("Loading tip rack...")
        tip_rack_id = ot2_client.loadLabware(
            intSlot=1,
            strLabwareName="opentrons_96_tiprack_1000ul"
        )
        LOGGER.info(f"Tip rack loaded with ID: {tip_rack_id}")

        # Load a pipette
        LOGGER.info("Loading pipette...")
        ot2_client.loadPipette(
            strPipetteName="p1000_single_gen2",
            strMount="right"
        )
        LOGGER.info("Pipette loaded successfully")

        # Move to a well
        LOGGER.info("Moving to well A1 of the tip rack...")
        ot2_client.moveToWell(
            strLabwareName=tip_rack_id,
            strWellName="A1",
            strPipetteName="p1000_single_gen2",
            strOffsetStart="top",
            intSpeed=100
        )
        LOGGER.info("Moved to well successfully")

        # Turn off the lights
        LOGGER.info("Turning off the lights...")
        ot2_client.lights("false")
        LOGGER.info("Lights turned off")

        LOGGER.info("OT-2 connection test completed successfully")
        return True
    except Exception as e:
        LOGGER.error(f"OT-2 connection test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test connection to a real OT-2 robot")
    parser.add_argument("--ip", type=str, default="100.67.89.154", help="IP address of the OT-2 robot")
    args = parser.parse_args()

    LOGGER.info(f"Starting OT-2 connection test with IP: {args.ip}")

    success = test_real_ot2_connection(args.ip)

    if success:
        print("\nOT-2 Connection Test: ✓")
        print("Connection to the real OT-2 robot was successful!")
    else:
        print("\nOT-2 Connection Test: ✗")
        print("Connection to the real OT-2 robot failed.")
        print("\nTroubleshooting Tips:")
        print("- Check if the OT-2 robot is powered on and connected to the network")
        print("- Verify the IP address is correct")
        print("- Make sure the robot is not currently running another protocol")
        print("- Check the log file for detailed error messages")

    return success

if __name__ == "__main__":
    main()
