#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Litestar API Application for Real-time Experiment Control

This module provides a Litestar-based API server that can receive JSON experiment
configurations from remote sources and execute them in real-time.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from litestar import Litestar, Request, Response, get, post
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from pydantic import BaseModel, Field, ValidationError

# Add the parent directory to sys.path to import local modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from dispatch import ExperimentDispatcher, LocalResultUploader
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from dispatch import ExperimentDispatcher, LocalResultUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models for request/response validation
class ExperimentRequest(BaseModel):
    """Model for experiment request validation."""
    uo_type: str = Field(..., description="Type of experiment (CVA, PEIS, OCV, CP, LSV)")
    parameters: Dict[str, Any] = Field(..., description="Experiment parameters")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")

class ExperimentResponse(BaseModel):
    """Model for experiment response."""
    status: str = Field(..., description="Status of the request (success, error, pending)")
    experiment_id: Optional[str] = Field(default=None, description="Unique experiment identifier")
    message: Optional[str] = Field(default=None, description="Status message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Experiment results or data")

class ExperimentStatus(BaseModel):
    """Model for experiment status."""
    experiment_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

# Global state management
class ExperimentManager:
    """Manages experiment execution and status tracking."""
    
    def __init__(self):
        self.dispatcher = ExperimentDispatcher()
        self.experiments: Dict[str, ExperimentStatus] = {}
        self.running_experiments: Dict[str, asyncio.Task] = {}
    
    async def submit_experiment(self, experiment_data: Dict[str, Any]) -> str:
        """Submit an experiment for execution."""
        experiment_id = str(uuid.uuid4())
        
        # Create experiment status
        status = ExperimentStatus(
            experiment_id=experiment_id,
            status="pending",
            created_at=datetime.now()
        )
        self.experiments[experiment_id] = status
        
        # Start experiment execution in background
        task = asyncio.create_task(self._execute_experiment(experiment_id, experiment_data))
        self.running_experiments[experiment_id] = task
        
        return experiment_id
    
    async def _execute_experiment(self, experiment_id: str, experiment_data: Dict[str, Any]):
        """Execute experiment in background."""
        try:
            logger.info(f"Starting experiment execution: {experiment_id}")
            self.experiments[experiment_id].status = "running"
            
            # Execute experiment using dispatcher
            result = self.dispatcher.execute_experiment(experiment_data)
            
            # Update status
            self.experiments[experiment_id].status = "completed"
            self.experiments[experiment_id].completed_at = datetime.now()
            self.experiments[experiment_id].result = result
            
            logger.info(f"Experiment completed successfully: {experiment_id}")
            
        except Exception as e:
            logger.error(f"Experiment failed: {experiment_id}, Error: {str(e)}")
            self.experiments[experiment_id].status = "failed"
            self.experiments[experiment_id].completed_at = datetime.now()
            self.experiments[experiment_id].result = {"error": str(e)}
        
        finally:
            # Clean up running task
            if experiment_id in self.running_experiments:
                del self.running_experiments[experiment_id]
    
    def get_experiment_status(self, experiment_id: str) -> Optional[ExperimentStatus]:
        """Get experiment status by ID."""
        return self.experiments.get(experiment_id)
    
    def list_experiments(self) -> List[ExperimentStatus]:
        """List all experiments."""
        return list(self.experiments.values())
    
    def cleanup(self):
        """Clean up resources."""
        # Cancel running tasks
        for task in self.running_experiments.values():
            if not task.done():
                task.cancel()
        
        # Clean up dispatcher
        self.dispatcher.cleanup()

# Create global experiment manager
experiment_manager = ExperimentManager()

# API Endpoints
@post("/experiments")
async def submit_experiment(data: ExperimentRequest) -> ExperimentResponse:
    """
    Submit a new experiment for execution.
    
    This endpoint receives JSON experiment configurations and queues them for execution.
    """
    try:
        logger.info(f"Received experiment request: {data.uo_type}")
        
        # Convert to dict for dispatcher
        experiment_data = {
            "uo_type": data.uo_type,
            "parameters": data.parameters
        }
        
        if data.metadata:
            experiment_data["metadata"] = data.metadata
        
        # Submit experiment
        experiment_id = await experiment_manager.submit_experiment(experiment_data)
        
        return ExperimentResponse(
            status="success",
            experiment_id=experiment_id,
            message="Experiment submitted successfully"
        )
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Invalid experiment data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error submitting experiment: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@get("/experiments/{experiment_id:str}")
async def get_experiment_status(experiment_id: str) -> ExperimentResponse:
    """Get the status of a specific experiment."""
    try:
        status = experiment_manager.get_experiment_status(experiment_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Experiment {experiment_id} not found"
            )
        
        return ExperimentResponse(
            status="success",
            experiment_id=experiment_id,
            message=f"Experiment status: {status.status}",
            data={
                "status": status.status,
                "created_at": status.created_at.isoformat(),
                "completed_at": status.completed_at.isoformat() if status.completed_at else None,
                "result": status.result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting experiment status: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@get("/experiments")
async def list_experiments() -> ExperimentResponse:
    """List all experiments."""
    try:
        experiments = experiment_manager.list_experiments()
        
        experiments_data = []
        for exp in experiments:
            experiments_data.append({
                "experiment_id": exp.experiment_id,
                "status": exp.status,
                "created_at": exp.created_at.isoformat(),
                "completed_at": exp.completed_at.isoformat() if exp.completed_at else None
            })
        
        return ExperimentResponse(
            status="success",
            message=f"Found {len(experiments)} experiments",
            data={"experiments": experiments_data}
        )
        
    except Exception as e:
        logger.error(f"Error listing experiments: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@post("/experiments/batch")
async def submit_batch_experiments(experiments: List[ExperimentRequest]) -> ExperimentResponse:
    """Submit multiple experiments for batch execution."""
    try:
        experiment_ids = []
        
        for exp_data in experiments:
            experiment_data = {
                "uo_type": exp_data.uo_type,
                "parameters": exp_data.parameters
            }
            
            if exp_data.metadata:
                experiment_data["metadata"] = exp_data.metadata
            
            experiment_id = await experiment_manager.submit_experiment(experiment_data)
            experiment_ids.append(experiment_id)
        
        return ExperimentResponse(
            status="success",
            message=f"Submitted {len(experiment_ids)} experiments",
            data={"experiment_ids": experiment_ids}
        )
        
    except Exception as e:
        logger.error(f"Error submitting batch experiments: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "Catalyst OT-2 Experiment API",
        "version": "1.0.0",
        "description": "Real-time API for controlling automated electrochemical experiments",
        "endpoints": {
            "submit_experiment": "POST /experiments",
            "get_experiment_status": "GET /experiments/{experiment_id}",
            "list_experiments": "GET /experiments",
            "batch_experiments": "POST /experiments/batch",
            "health_check": "GET /health"
        }
    }

# CORS configuration
cors_config = CORSConfig(
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Create Litestar application
app = Litestar(
    route_handlers=[
        submit_experiment,
        get_experiment_status,
        list_experiments,
        submit_batch_experiments,
        health_check,
        root
    ],
    cors_config=cors_config,
    debug=True,
)

# Cleanup on shutdown
@app.on_shutdown
async def cleanup_on_shutdown():
    """Clean up resources on application shutdown."""
    logger.info("Shutting down API server...")
    experiment_manager.cleanup()
    logger.info("API server shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Catalyst OT-2 Experiment API server...")
    uvicorn.run(
        "litestar_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
