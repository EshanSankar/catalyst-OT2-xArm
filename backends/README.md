# Backends Package

This package contains the backend implementations for various electrochemical experiments.

## Structure

- `base.py`: Contains the `BaseBackend` class that all experiment backends inherit from
- `cva_backend.py`: Cyclic Voltammetry Analysis backend
- `peis_backend.py`: Potentiostatic Electrochemical Impedance Spectroscopy backend
- `ocv_backend.py`: Open Circuit Voltage backend
- `cp_backend.py`: Chronopotentiometry backend
- `lsv_backend.py`: Linear Sweep Voltammetry backend

## Usage

```python
from backends import CVABackend

# Create backend instance
backend = CVABackend()

# Execute experiment
result = backend.execute_experiment({
    "uo_type": "CVA",
    "parameters": {
        "start_voltage": 0.0,
        "end_voltage": 1.0,
        "scan_rate": 0.05,
        "cycles": 3,
        "arduino_control": {
            "base0_temp": 25.0,
            "pump0_ml": 2.5,
            "ultrasonic0_ms": 3000
        }
    }
})
```

## Extending

To add a new experiment type:

1. Create a new backend class that inherits from `BaseBackend`
2. Implement the `_execute_measurement` method
3. Implement the `validate_parameters` method
4. Add the new backend class to `__init__.py`
5. Update the `_get_backend_instance` method in `dispatch.py`

Example:

```python
from backends.base import BaseBackend

class NewExperimentBackend(BaseBackend):
    def __init__(self, config_path=None, result_uploader=None):
        super().__init__(config_path, result_uploader, experiment_type="NEW_EXPERIMENT")
    
    def _execute_measurement(self, params):
        # Implement measurement logic
        pass
    
    def validate_parameters(self, params):
        errors = super().validate_parameters(params)
        # Add experiment-specific validation
        return errors
```
