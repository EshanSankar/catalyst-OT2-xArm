# Installation Guide

## Prerequisites

- Python 3.8 or higher
- OT-2 robot with API access
- Arduino board (compatible with provided firmware)
- USB connection to Arduino
- Network connection to OT-2

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/sissifeng/catalyst-OT2-arduino.git
cd catalyst-OT2-arduino
```

2. Run the installation script:
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

This script will:
- Create a virtual environment
- Install all required dependencies
- Set up configuration files
- Configure Arduino permissions (Linux only)

3. Configure your setup:
- Edit `config/default_config.json` with your OT-2 IP address
- Verify Arduino port settings
- Adjust parameter limits in `config/parameter_limits.json` if needed

4. Test the installation:
```bash
python scripts/test_connection.py
```

## Manual Installation

If you prefer to install manually:

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install package in development mode:
```bash
pip install -e .
```

4. Create necessary directories:
```bash
mkdir -p logs results config
```

5. Copy configuration files:
```bash
cp config.default/* config/
```

## Arduino Setup

1. Upload the provided firmware to your Arduino board
2. Connect Arduino via USB
3. Note the port name:
   - Linux: Usually `/dev/ttyACM0` or `/dev/ttyUSB0`
   - Windows: `COM3` or similar
   - Mac: `/dev/tty.usbmodem*`

4. Update the port in `config/default_config.json`

## OT-2 Setup

1. Ensure your OT-2 is on the same network
2. Find your OT-2's IP address
3. Update the IP in `config/default_config.json`
4. Test connection using the test script

## Troubleshooting

### Common Issues

1. Arduino Permission Denied:
```bash
sudo usermod -a -G dialout $USER  # Linux
# Log out and back in for changes to take effect
```

2. OT-2 Connection Failed:
- Verify IP address
- Check network connectivity
- Ensure OT-2 is powered on
- Try pinging the OT-2

3. Python Package Issues:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Getting Help

- Check the [GitHub Issues](https://github.com/sissifeng/catalyst-OT2-arduino/issues)
- Submit a new issue with:
  - Error messages
  - System information
  - Steps to reproduce
  - Configuration details 
