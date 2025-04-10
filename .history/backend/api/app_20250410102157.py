from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, Any
import os
import sys

# Add the parent directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dispatch import ExperimentDispatcher
from utils import setup_logging

app = FastAPI(title="Automated Experiment API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create dispatcher instance
dispatcher = ExperimentDispatcher()

@app.post("/run_experiment")
async def run_experiment(request: Request) -> Dict[str, Any]:
    """
    Execute an experiment based on the provided unit operation (UO)
    
    Args:
        request: FastAPI request object containing the UO JSON
        
    Returns:
        Dict containing experiment results and status
    """
    try:
        uo = await request.json()
        logger.info(f"Received experiment request: {uo}")
        
        # Execute experiment
        result = dispatcher.execute_experiment(uo)
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error executing experiment: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Automated Experiment API",
        "version": "1.0.0",
        "description": "API for controlling automated experiments with OT-2 and Arduino"
    } 
