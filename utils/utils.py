import logging
from typing import Dict, Any

LOGGER = logging.getLogger(__name__)

def execute_arduino_actions(control_dict: Dict[str, Any], arduino) -> None:
    """
    Execute Arduino control actions based on the provided control dictionary.
    
    This function parses the control dictionary and calls the appropriate Arduino methods.
    The control dictionary should have keys in the format:
    - base{number}_temp: Set temperature for base {number}
    - pump{number}_ml: Dispense {volume} ml from pump {number}
    - ultrasonic{number}_ms: Turn on ultrasonic for {time} ms on base {number}
    
    Args:
        control_dict (Dict[str, Any]): Dictionary containing Arduino control parameters
        arduino: Arduino client instance
    
    Examples:
        control_dict = {
            "base0_temp": 60,
            "pump0_ml": 2.5,
            "ultrasonic0_ms": 3000
        }
        execute_arduino_actions(control_dict, arduino)
    """
    if not control_dict:
        LOGGER.warning("Empty Arduino control dictionary provided")
        return
    
    LOGGER.info(f"Executing Arduino actions: {control_dict}")
    
    for key, value in control_dict.items():
        try:
            # Handle temperature control
            if key.startswith("base") and key.endswith("_temp"):
                base_number = int(key.split("base")[1].split("_")[0])
                arduino.setTemp(base_number, float(value))
                LOGGER.info(f"Set base {base_number} temperature to {value}°C")
            
            # Handle pump control
            elif key.startswith("pump") and key.endswith("_ml"):
                pump_number = int(key.split("pump")[1].split("_")[0])
                arduino.dispense_ml(pump_number, float(value))
                LOGGER.info(f"Dispensed {value} ml from pump {pump_number}")
            
            # Handle ultrasonic control
            elif key.startswith("ultrasonic") and key.endswith("_ms"):
                base_number = int(key.split("ultrasonic")[1].split("_")[0])
                arduino.setUltrasonicOnTimer(base_number, int(value))
                LOGGER.info(f"Set ultrasonic on base {base_number} for {value} ms")
            
            else:
                LOGGER.warning(f"Unknown Arduino control parameter: {key}")
        
        except Exception as e:
            LOGGER.error(f"Error executing Arduino action {key}={value}: {str(e)}")
            # Continue with other actions even if one fails
            continue
    
    LOGGER.info("Completed Arduino actions") 
