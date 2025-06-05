#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test version of the Litestar API for testing basic functionality.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from litestar import Litestar, get, post
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models
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

# Simple in-memory storage for testing
experiments_db = {}

@post("/experiments")
async def submit_experiment(data: ExperimentRequest) -> ExperimentResponse:
    """Submit a new experiment for execution."""
    try:
        logger.info(f"Received experiment request: {data.uo_type}")
        
        # Generate experiment ID
        experiment_id = str(uuid.uuid4())
        
        # Store experiment (mock execution)
        experiments_db[experiment_id] = {
            "id": experiment_id,
            "uo_type": data.uo_type,
            "parameters": data.parameters,
            "metadata": data.metadata,
            "status": "completed",  # Mock as completed for testing
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "result": {
                "mock_result": True,
                "message": f"Mock execution of {data.uo_type} experiment",
                "data": {"voltage": [0.1, 0.2, 0.3], "current": [0.01, 0.02, 0.03]}
            }
        }
        
        return ExperimentResponse(
            status="success",
            experiment_id=experiment_id,
            message="Experiment submitted and completed successfully (mock mode)"
        )
        
    except Exception as e:
        logger.error(f"Error submitting experiment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@get("/experiments/{experiment_id:str}")
async def get_experiment_status(experiment_id: str) -> ExperimentResponse:
    """Get the status of a specific experiment."""
    try:
        if experiment_id not in experiments_db:
            raise HTTPException(
                status_code=404,
                detail=f"Experiment {experiment_id} not found"
            )
        
        experiment = experiments_db[experiment_id]
        
        return ExperimentResponse(
            status="success",
            experiment_id=experiment_id,
            message=f"Experiment status: {experiment['status']}",
            data=experiment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting experiment status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@get("/experiments")
async def list_experiments() -> ExperimentResponse:
    """List all experiments."""
    try:
        experiments_list = list(experiments_db.values())
        
        return ExperimentResponse(
            status="success",
            message=f"Found {len(experiments_list)} experiments",
            data={"experiments": experiments_list}
        )
        
    except Exception as e:
        logger.error(f"Error listing experiments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@post("/experiments/batch")
async def submit_batch_experiments(experiments: List[ExperimentRequest]) -> ExperimentResponse:
    """Submit multiple experiments for batch execution."""
    try:
        experiment_ids = []
        
        for exp_data in experiments:
            experiment_id = str(uuid.uuid4())
            
            # Store experiment (mock execution)
            experiments_db[experiment_id] = {
                "id": experiment_id,
                "uo_type": exp_data.uo_type,
                "parameters": exp_data.parameters,
                "metadata": exp_data.metadata,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "result": {
                    "mock_result": True,
                    "message": f"Mock batch execution of {exp_data.uo_type} experiment"
                }
            }
            
            experiment_ids.append(experiment_id)
        
        return ExperimentResponse(
            status="success",
            message=f"Submitted {len(experiment_ids)} experiments",
            data={"experiment_ids": experiment_ids}
        )
        
    except Exception as e:
        logger.error(f"Error submitting batch experiments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-test"
    }

@get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "Catalyst OT-2 Experiment API (Test Mode)",
        "version": "1.0.0-test",
        "description": "Test version of the real-time API for controlling automated electrochemical experiments",
        "mode": "mock",
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
    allow_origins=["*"],
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

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Catalyst OT-2 Experiment API (Test Mode)...")
    uvicorn.run(
        "simple_test_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
