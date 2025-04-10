# API Reference

## Backend Classes

### BaseBackend

Base class for all experiment backends.

```python
class BaseBackend:
    def __init__(self, config_path: Optional[str] = None)
    def connect_devices() -> None
    def disconnect_devices() -> None
    def execute_experiment(unit_operation: Dict[str, Any]) -> Dict[str, Any]
    def validate_parameters(parameters: Dict[str, Any]) -> None
```

### CVABackend

Cyclic Voltammetry Analysis backend.

```python
class CVABackend(BaseBackend):
    def execute_experiment(unit_operation: Dict[str, Any]) -> Dict[str, Any]
```

Parameters:
- start_voltage: float
- end_voltage: float
- scan_rate: float
- cycles: int
- arduino_control: Dict[str, Any]

### OCVBackend

Open Circuit Voltage backend.

```python
class OCVBackend(BaseBackend):
    def execute_experiment(unit_operation: Dict[str, Any]) -> Dict[str, Any]
```

Parameters:
- duration: float
- sample_interval: float
- arduino_control: Dict[str, Any]

### CPBackend

Chronopotentiometry backend.

```python
class CPBackend(BaseBackend):
    def execute_experiment(unit_operation: Dict[str, Any]) -> Dict[str, Any]
```

Parameters:
- current: float
- duration: float
- arduino_control: Dict[str, Any]

### LSVBackend

Linear Sweep Voltammetry backend.

```python
class LSVBackend(BaseBackend):
    def execute_experiment(unit_operation: Dict[str, Any]) -> Dict[str, Any]
```

Parameters:
- start_voltage: float
- end_voltage: float
- scan_rate: float
- arduino_control: Dict[str, Any]

### PEISBackend

Potentiostatic Electrochemical Impedance Spectroscopy backend.

```python
class PEISBackend(BaseBackend):
    def execute_experiment(unit_operation: Dict[str, Any]) -> Dict[str, Any]
```

Parameters:
- dc_voltage: float
- frequency_range: List[float]
- amplitude: float
- arduino_control: Dict[str, Any]

## Hardware Control

### Arduino Control

```python
class Arduino:
    def __init__(self, port: str = "/dev/ttyACM0")
    def set_temperature(temperature: float) -> None
    def read_temperature() -> float
    def pump_volume(volume: float) -> None
    def activate_ultrasonic(duration: int) -> None
    def close() -> None
```

### OT2 Control

```python
class OT2Control:
    def __init__(self, ip: str = "100.67.89.154")
    def connect() -> bool
    def disconnect() -> None
    def move_to_position(position: Dict[str, float]) -> None
    def home() -> None
```

## Data Processing

### Smoothing and Filtering

```python
def smooth_data(data: np.ndarray, window_size: int = 5) -> np.ndarray
def calculate_derivatives(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
```

### Peak Detection

```python
def find_peaks(data: np.ndarray, height: Optional[float] = None, 
               distance: Optional[int] = None) -> Dict[str, np.ndarray]
```

### Experiment-Specific Processing

```python
def process_cv_data(voltage: np.ndarray, current: np.ndarray, 
                   scan_rate: float) -> Dict[str, Any]
def process_eis_data(frequency: np.ndarray, z_real: np.ndarray, 
                    z_imag: np.ndarray) -> Dict[str, Any]
def analyze_lsv_data(voltage: np.ndarray, current: np.ndarray) -> Dict[str, Any]
```

## Parameter Validation

```python
def validate_voltage(voltage: float, limits: Optional[Dict[str, float]] = None) -> None
def validate_current(current: float, limits: Optional[Dict[str, float]] = None) -> None
def validate_temperature(temperature: float, limits: Optional[Dict[str, float]] = None) -> None
def validate_frequency(frequency: float, limits: Optional[Dict[str, float]] = None) -> None
```

## Configuration

### Default Configuration

```json
{
    "hardware": {
        "arduino": {
            "port": "/dev/ttyACM0",
            "baudrate": 9600
        },
        "ot2": {
            "ip": "100.67.89.154",
            "port": 31950
        }
    }
}
```

### Parameter Limits

```json
{
    "voltage": {
        "min": -10.0,
        "max": 10.0
    },
    "current": {
        "min": -2.0,
        "max": 2.0
    },
    "temperature": {
        "min": 10.0,
        "max": 80.0
    }
}
```

## Error Handling

### Custom Exceptions

```python
class ValidationError(Exception):
    pass

class HardwareError(Exception):
    pass

class ExperimentError(Exception):
    pass
```

### Error Logging

```python
logging.error(f"Hardware connection failed: {str(e)}")
logging.warning(f"Parameter {name} outside recommended range")
logging.info(f"Experiment {id} completed successfully")
``` 
