"""
Mock Opentrons module for testing purposes.
This module provides a simple mock implementation of the Opentrons API.
"""

import logging
import time
import random

logger = logging.getLogger(__name__)

class OT2Control:
    """Mock OT2 control class for testing."""
    
    def __init__(self, ip="100.67.89.154"):
        """Initialize the OT2 control."""
        self.ip = ip
        self.connected = False
        self.run_id = None
        self.pipettes = {
            "left": None,
            "right": {
                "model": "p1000_single_gen2",
                "name": "p1000_single",
                "id": "P1000S20220001"
            }
        }
        self.modules = []
        
    def connect(self):
        """Connect to the OT2 robot."""
        logger.info(f"Connecting to OT2 at {self.ip}...")
        time.sleep(1)  # Simulate connection delay
        self.connected = True
        self.run_id = f"test_run_{int(time.time())}"
        logger.info(f"Connected to OT2. Run ID: {self.run_id}")
        return True
        
    def disconnect(self):
        """Disconnect from the OT2 robot."""
        logger.info("Disconnecting from OT2...")
        time.sleep(0.5)  # Simulate disconnection delay
        self.connected = False
        logger.info("Disconnected from OT2")
        return True
        
    def home(self):
        """Home the OT2 robot."""
        if not self.connected:
            logger.error("Cannot home: Not connected to OT2")
            return False
        logger.info("Homing OT2 robot...")
        time.sleep(2)  # Simulate homing delay
        logger.info("OT2 robot homed")
        return True
        
    def get_pipettes(self):
        """Get the pipettes attached to the OT2 robot."""
        if not self.connected:
            logger.error("Cannot get pipettes: Not connected to OT2")
            return None
        return self.pipettes
        
    def get_modules(self):
        """Get the modules attached to the OT2 robot."""
        if not self.connected:
            logger.error("Cannot get modules: Not connected to OT2")
            return None
        return self.modules
        
    def run_protocol(self, protocol):
        """Run a protocol on the OT2 robot."""
        if not self.connected:
            logger.error("Cannot run protocol: Not connected to OT2")
            return False
        logger.info(f"Running protocol on OT2...")
        time.sleep(3)  # Simulate protocol execution
        logger.info("Protocol execution completed")
        return True

class ArduinoClient:
    """Mock Arduino client for testing."""
    
    def __init__(self, port="COM3"):
        """Initialize the Arduino client."""
        self.port = port
        self.connected = False
        self.temperature = 25.0
        self.led_state = False
        
    def connect(self):
        """Connect to the Arduino."""
        logger.info(f"Connecting to Arduino on {self.port}...")
        time.sleep(1)  # Simulate connection delay
        self.connected = True
        logger.info(f"Connected to Arduino on {self.port}")
        return True
        
    def close(self):
        """Close the connection to the Arduino."""
        logger.info("Closing Arduino connection...")
        time.sleep(0.5)  # Simulate disconnection delay
        self.connected = False
        logger.info("Arduino connection closed")
        return True
        
    def read_temperature(self):
        """Read the temperature from the Arduino."""
        if not self.connected:
            logger.error("Cannot read temperature: Not connected to Arduino")
            return None
        # Simulate temperature reading with small random fluctuations
        self.temperature += random.uniform(-0.2, 0.2)
        logger.info(f"Temperature reading: {self.temperature:.1f}°C")
        return self.temperature
        
    def set_led(self, state):
        """Set the LED state on the Arduino."""
        if not self.connected:
            logger.error("Cannot set LED: Not connected to Arduino")
            return False
        self.led_state = state
        logger.info(f"LED state set to: {'ON' if state else 'OFF'}")
        return True
        
    def set_pump(self, speed):
        """Set the pump speed on the Arduino."""
        if not self.connected:
            logger.error("Cannot set pump: Not connected to Arduino")
            return False
        logger.info(f"Pump speed set to: {speed}")
        return True
        
    def set_ultrasonic(self, state):
        """Set the ultrasonic state on the Arduino."""
        if not self.connected:
            logger.error("Cannot set ultrasonic: Not connected to Arduino")
            return False
        logger.info(f"Ultrasonic state set to: {'ON' if state else 'OFF'}")
        return True
