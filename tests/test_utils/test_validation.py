import pytest
from utils.validation import validate_voltage, ValidationError

def test_voltage_validation():
    """Test that voltage validation catches out-of-range values."""
    with pytest.raises(ValidationError):
        validate_voltage(100.0)  # 超出范围的电压值

def test_valid_voltage():
    """Test that voltage validation accepts valid values."""
    try:
        validate_voltage(1.0)  # 有效的电压值
    except ValidationError:
        pytest.fail("Unexpected ValidationError") 
