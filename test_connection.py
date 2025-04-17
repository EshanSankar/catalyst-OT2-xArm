# test_connections.py
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConnectionTest")

# Add parent directory to path if needed
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the necessary modules
try:
    # Import OT-2 control module
    from opentrons import opentronsClient
    logger.info("Successfully imported opentronsClient module")
except ImportError as e:
    logger.error(f"Failed to import opentronsClient module: {e}")

try:
    # Import Arduino control module (if applicable)
    from hardware.OT_Arduino_Client import Arduino
    logger.info("Successfully imported Arduino module")
except ImportError as e:
    logger.error(f"Failed to import Arduino module: {e}")

# Load configuration
def load_config():
    try:
        import json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'config', 'default_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {"hardware": {"ot2": {"ip": "100.67.89.154"}, "arduino": {"port": "COM3"}}}

# Test OT-2 connection
def test_ot2_connection(ip_address):
    logger.info(f"Testing OT-2 connection to {ip_address}...")
    try:
        ot2 = opentronsClient(strRobotIP=ip_address)
        logger.info("OT-2 Connected Successfully!")
        return True
    except Exception as e:
        logger.error(f"OT-2 Connection Failed: {e}")
        return False

# Test Arduino connection (if applicable)
def test_arduino_connection(port):
    logger.info(f"Testing Arduino connection on port {port}...")
    try:
        arduino = Arduino(port=port)
        logger.info("Arduino Connected Successfully!")
        arduino.close()
        return True
    except Exception as e:
        logger.error(f"Arduino Connection Failed: {e}")
        return False

def main():
    # Load configuration
    config = load_config()
    
    # Get OT-2 IP address and Arduino port from config
    ot2_ip = config.get("hardware", {}).get("ot2", {}).get("ip", "100.67.89.154")
    arduino_port = config.get("hardware", {}).get("arduino", {}).get("port", "COM3")
    
    # Test OT-2 connection
    ot2_success = test_ot2_connection(ot2_ip)
    
    # Test Arduino connection (if applicable)
    arduino_success = test_arduino_connection(arduino_port)
    
    # Print summary
    print("\nConnection Test Summary:")
    print("------------------------")
    print(f"OT-2 Connection: {'✓' if ot2_success else '✗'}")
    print(f"Arduino Connection: {'✓' if arduino_success else '✗'}")
    
    if not (ot2_success and arduino_success):
        print("\nTroubleshooting Tips:")
        if not ot2_success:
            print("- Check if OT-2 is powered on and connected to the network")
            print(f"- Verify OT-2 IP address ({ot2_ip}) is correct")
            print("- Try pinging the OT-2 IP address")
        if not arduino_success:
            print("- Check if Arduino is properly connected via USB")
            print(f"- Verify Arduino port ({arduino_port}) is correct")
            print("- Check if you have necessary permissions to access the port")
        return False
    
    print("\nAll connections successful!")
    return True

if __name__ == "__main__":
    main()