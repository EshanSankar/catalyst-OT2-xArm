#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Installation script for API dependencies.

This script installs the required dependencies for the Catalyst OT-2 Experiment API.
"""

import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result."""
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"✓ {description} completed successfully")
        if result.stdout:
            logger.debug(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed")
        logger.error(f"Error: {e.stderr}")
        return False

def install_dependencies():
    """Install required dependencies."""
    logger.info("Installing Catalyst OT-2 Experiment API dependencies...")
    
    # Update pip first
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    ):
        logger.warning("Failed to upgrade pip, continuing anyway...")
    
    # Install requirements
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements from requirements.txt"
    ):
        logger.error("Failed to install requirements")
        return False
    
    # Verify critical imports
    critical_packages = [
        ("litestar", "Litestar web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("aiohttp", "HTTP client"),
    ]
    
    logger.info("Verifying critical package installations...")
    all_good = True
    
    for package, description in critical_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} ({description}) - OK")
        except ImportError:
            logger.error(f"✗ {package} ({description}) - FAILED")
            all_good = False
    
    return all_good

def main():
    """Main installation function."""
    logger.info("Starting Catalyst OT-2 Experiment API installation...")
    
    if install_dependencies():
        logger.info("🎉 Installation completed successfully!")
        logger.info("You can now start the API server with:")
        logger.info("  python start_api_server.py")
        logger.info("Or test the installation with:")
        logger.info("  python test_api.py --wait")
        return True
    else:
        logger.error("❌ Installation failed!")
        logger.error("Please check the error messages above and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
