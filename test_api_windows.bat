@echo off
REM Windows batch script to test the Catalyst OT-2 Experiment API

echo Testing Catalyst OT-2 Experiment API...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install test dependencies
echo Installing test dependencies...
python -m pip install requests

REM Run the API test
echo.
echo Running API tests...
python test_api.py --url http://127.0.0.1:8000 --wait

echo.
echo Test completed. Check the output above for results.
pause
