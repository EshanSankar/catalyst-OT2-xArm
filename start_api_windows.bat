@echo off
REM Windows batch script to start the Catalyst OT-2 Experiment API

echo Starting Catalyst OT-2 Experiment API...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to PATH
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/updating dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements-api.txt

REM Set environment variables for Windows
set API_HOST=127.0.0.1
set API_PORT=8000
set OT2_IP=100.67.89.154
set ARDUINO_PORT=COM3
set LOG_LEVEL=INFO
set MOCK_MODE=false

echo.
echo Configuration:
echo - Host: %API_HOST%
echo - Port: %API_PORT%
echo - OT-2 IP: %OT2_IP%
echo - Arduino Port: %ARDUINO_PORT%
echo - Mock Mode: %MOCK_MODE%
echo.

REM Start the API server
echo Starting API server...
python start_api_server.py --host %API_HOST% --port %API_PORT%

pause
