#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration module for the Catalyst OT-2 Experiment API.

This module provides configuration management for the API server,
including environment-specific settings and validation.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    type: str = Field(default="local", description="Database type (local, postgresql, sqlite)")
    url: Optional[str] = Field(default=None, description="Database connection URL")
    max_connections: int = Field(default=10, description="Maximum database connections")

class HardwareConfig(BaseModel):
    """Hardware configuration settings."""
    ot2_ip: str = Field(default="100.67.89.154", description="OT-2 robot IP address")
    ot2_port: int = Field(default=31950, description="OT-2 robot port")
    arduino_port: str = Field(default="COM3", description="Arduino serial port")
    arduino_baudrate: int = Field(default=9600, description="Arduino baud rate")
    connection_timeout: float = Field(default=10.0, description="Connection timeout in seconds")
    mock_mode: bool = Field(default=False, description="Use mock devices for testing")

class APIConfig(BaseModel):
    """API server configuration settings."""
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    reload: bool = Field(default=False, description="Enable auto-reload")
    workers: int = Field(default=1, description="Number of worker processes")
    max_request_size: int = Field(default=10 * 1024 * 1024, description="Max request size in bytes")
    request_timeout: float = Field(default=300.0, description="Request timeout in seconds")

class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    file_path: str = Field(default="api_server.log", description="Log file path")
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max log file size in bytes")
    backup_count: int = Field(default=5, description="Number of backup log files")

class SecurityConfig(BaseModel):
    """Security configuration settings."""
    cors_origins: list = Field(default=["*"], description="CORS allowed origins")
    cors_methods: list = Field(default=["GET", "POST", "PUT", "DELETE"], description="CORS allowed methods")
    cors_headers: list = Field(default=["*"], description="CORS allowed headers")
    api_key_required: bool = Field(default=False, description="Require API key authentication")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")

class ExperimentConfig(BaseModel):
    """Experiment execution configuration."""
    max_concurrent_experiments: int = Field(default=5, description="Maximum concurrent experiments")
    experiment_timeout: float = Field(default=3600.0, description="Experiment timeout in seconds")
    results_directory: str = Field(default="results", description="Results storage directory")
    cleanup_interval: int = Field(default=3600, description="Cleanup interval in seconds")
    max_experiment_history: int = Field(default=1000, description="Maximum experiments to keep in history")

class AppConfig(BaseModel):
    """Main application configuration."""
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    experiments: ExperimentConfig = Field(default_factory=ExperimentConfig)
    
    @validator('api')
    def validate_api_config(cls, v):
        """Validate API configuration."""
        if v.port < 1 or v.port > 65535:
            raise ValueError("API port must be between 1 and 65535")
        return v
    
    @validator('hardware')
    def validate_hardware_config(cls, v):
        """Validate hardware configuration."""
        if v.ot2_port < 1 or v.ot2_port > 65535:
            raise ValueError("OT-2 port must be between 1 and 65535")
        if v.arduino_baudrate <= 0:
            raise ValueError("Arduino baud rate must be positive")
        return v

def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config file {config_path}: {e}")
        return {}

def load_config_from_env() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {}
    
    # API configuration
    if os.getenv("API_HOST"):
        config.setdefault("api", {})["host"] = os.getenv("API_HOST")
    if os.getenv("API_PORT"):
        config.setdefault("api", {})["port"] = int(os.getenv("API_PORT"))
    if os.getenv("API_DEBUG"):
        config.setdefault("api", {})["debug"] = os.getenv("API_DEBUG").lower() == "true"
    
    # Hardware configuration
    if os.getenv("OT2_IP"):
        config.setdefault("hardware", {})["ot2_ip"] = os.getenv("OT2_IP")
    if os.getenv("OT2_PORT"):
        config.setdefault("hardware", {})["ot2_port"] = int(os.getenv("OT2_PORT"))
    if os.getenv("ARDUINO_PORT"):
        config.setdefault("hardware", {})["arduino_port"] = os.getenv("ARDUINO_PORT")
    if os.getenv("MOCK_MODE"):
        config.setdefault("hardware", {})["mock_mode"] = os.getenv("MOCK_MODE").lower() == "true"
    
    # Logging configuration
    if os.getenv("LOG_LEVEL"):
        config.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")
    if os.getenv("LOG_FILE"):
        config.setdefault("logging", {})["file_path"] = os.getenv("LOG_FILE")
    
    # Security configuration
    if os.getenv("API_KEY"):
        config.setdefault("security", {})["api_key"] = os.getenv("API_KEY")
        config.setdefault("security", {})["api_key_required"] = True
    
    return config

def create_config(config_path: Optional[str] = None) -> AppConfig:
    """Create application configuration from file and environment."""
    # Start with default configuration
    config_dict = {}
    
    # Load from file if provided
    if config_path and os.path.exists(config_path):
        file_config = load_config_from_file(config_path)
        config_dict.update(file_config)
    
    # Override with environment variables
    env_config = load_config_from_env()
    for section, values in env_config.items():
        if section in config_dict:
            config_dict[section].update(values)
        else:
            config_dict[section] = values
    
    # Create and validate configuration
    try:
        return AppConfig(**config_dict)
    except Exception as e:
        logger.error(f"Error creating configuration: {e}")
        logger.info("Using default configuration")
        return AppConfig()

def save_config_template(output_path: str):
    """Save a configuration template file."""
    template_config = AppConfig()
    
    config_dict = template_config.dict()
    
    with open(output_path, 'w') as f:
        json.dump(config_dict, f, indent=2)
    
    logger.info(f"Configuration template saved to {output_path}")

# Global configuration instance
_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = create_config()
    return _config

def set_config(config: AppConfig):
    """Set the global configuration instance."""
    global _config
    _config = config

# Example usage and CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuration management")
    parser.add_argument("--create-template", type=str, help="Create configuration template file")
    parser.add_argument("--validate", type=str, help="Validate configuration file")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    
    args = parser.parse_args()
    
    if args.create_template:
        save_config_template(args.create_template)
    elif args.validate:
        try:
            config = create_config(args.validate)
            print(f"Configuration file {args.validate} is valid!")
            print(json.dumps(config.dict(), indent=2))
        except Exception as e:
            print(f"Configuration validation failed: {e}")
    elif args.show:
        config = get_config()
        print(json.dumps(config.dict(), indent=2))
    else:
        parser.print_help()
