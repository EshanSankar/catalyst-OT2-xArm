import pytest
from backends.base import BaseBackend

def test_base_backend_initialization():
    backend = BaseBackend()
    assert backend is not None

# tests/test_hardware/test_arduino.py
import pytest
from hardware.OT_Arduino_Client import Arduino

def test_arduino_connection():
    with pytest.raises(Exception):
        arduino = Arduino(port="NONEXISTENT")

# tests/test_utils/test_validation.py
import pytest
from utils.validation import validate_voltage

def test_voltage_validation():
    with pytest.raises(ValidationError):
        validate_voltage(100.0)  # Should be out of range
