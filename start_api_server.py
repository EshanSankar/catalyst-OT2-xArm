#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Startup script for the Catalyst OT-2 Experiment API server.

This script starts the Litestar-based API server that can receive and process
real-time experiment configurations from remote sources.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("api_server.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Start the Catalyst OT-2 Experiment API server"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1,
        help="Number of worker processes (default: 1)"
    )
    return parser.parse_args()

def main():
    """Main function to start the API server."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Catalyst OT-2 Experiment API server...")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Log level: {args.log_level}")
    logger.info(f"Workers: {args.workers}")
    
    try:
        import uvicorn

        # Start the server
        uvicorn.run(
            "api.litestar_app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower(),
            workers=args.workers if not args.reload else 1,  # Reload mode requires single worker
            access_log=True
        )

    except ImportError:
        logger.error("uvicorn is not installed. Please install it with: pip install uvicorn")
        logger.info("Trying alternative method...")
        try:
            import subprocess
            cmd = [
                sys.executable, "-m", "uvicorn",
                "api.litestar_app:app",
                "--host", args.host,
                "--port", str(args.port),
                "--log-level", args.log_level.lower()
            ]
            if args.reload:
                cmd.append("--reload")

            subprocess.run(cmd, check=True)
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
