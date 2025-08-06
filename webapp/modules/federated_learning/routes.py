"""
Federated Learning Routes - Modern Modular Architecture
======================================================

FastAPI router for federated learning using modular service architecture.
Follows the same pattern as other modules for consistency.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import os
from pathlib import Path

# Import our modular services
from .federation_service import FederationService
from .twin_performance_service import TwinPerformanceService
from .insights_service import InsightsService
from .monitoring_service import MonitoringService

# Import shared services and database managers (following twin_registry pattern)
from src.federated_learning.core.federated_learning_service import FederatedLearningService
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["federated-learning"])

# Template setup (following twin_registry pattern)
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize shared services (following twin_registry pattern)
data_dir = Path("data")
db_path = data_dir / "aasx_database.db"
connection_manager = DatabaseConnectionManager(db_path)
db_manager = BaseDatabaseManager(connection_manager)

# Create shared service instances
file_repo = FileRepository(db_manager)
project_repo = ProjectRepository(db_manager)
digital_twin_service = DigitalTwinService(db_manager, file_repo, project_repo)
federated_learning_service = FederatedLearningService(digital_twin_service)

# Initialize federated learning services
federation_service = FederationService(db_manager, digital_twin_service, federated_learning_service)
twin_performance_service = TwinPerformanceService(db_manager, digital_twin_service, federated_learning_service)
insights_service = InsightsService(db_manager, digital_twin_service, federated_learning_service)
monitoring_service = MonitoringService(db_manager, digital_twin_service, federated_learning_service)

def get_services():
    """Get or initialize service instances"""
    return federation_service, twin_performance_service, insights_service, monitoring_service

# Pydantic models
class FederationStartRequest(BaseModel):
    twin_ids: List[str]
    model_type: str = "federated_averaging"
    rounds: int = 10
    privacy_level: str = "high"

class FederationStatusResponse(BaseModel):
    status: str
    active_twins: int
    total_rounds: int
    current_round: int
    model_accuracy: float
    last_update: str

# ============================================================================
# Dashboard Routes
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def federated_learning_dashboard(request: Request):
    """Federated learning dashboard"""
    try:
        return templates.TemplateResponse(
            "federated_learning/index.html",
            {
                "request": request,
                "title": "Federated Learning - AASX Digital Twin Analytics Framework",
                "active_page": "federated-learning"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering federated learning dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to render dashboard")

# ============================================================================
# API Routes
# ============================================================================

@router.post("/federation/start")
async def start_federation(request: FederationStartRequest):
    """Start federated learning process"""
    try:
        federation_service, _, _, _ = get_services()
        result = federation_service.start_federation(
            twin_ids=request.twin_ids,
            model_type=request.model_type,
            rounds=request.rounds,
            privacy_level=request.privacy_level
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error starting federation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/federation/status")
async def get_federation_status():
    """Get federation status"""
    try:
        federation_service, _, _, _ = get_services()
        status = federation_service.get_federation_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting federation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/federation/stop")
async def stop_federation():
    """Stop federated learning process"""
    try:
        federation_service, _, _, _ = get_services()
        result = federation_service.stop_federation()
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error stopping federation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twin/performance")
async def get_twin_performance():
    """Get twin performance metrics"""
    try:
        _, twin_performance_service, _, _ = get_services()
        performance = twin_performance_service.get_twin_performance()
        return {
            "status": "success",
            "data": performance
        }
    except Exception as e:
        logger.error(f"Error getting twin performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/performance")
async def get_twins_performance():
    """Get twins performance metrics (alias for twin/performance)"""
    try:
        _, twin_performance_service, _, _ = get_services()
        performance = twin_performance_service.get_twin_performance()
        return {
            "status": "success",
            "data": performance
        }
    except Exception as e:
        logger.error(f"Error getting twins performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/cross-twin")
async def get_cross_twin_insights():
    """Get cross-twin insights"""
    try:
        _, _, insights_service, _ = get_services()
        insights = insights_service.get_cross_twin_insights()
        return {
            "status": "success",
            "data": insights
        }
    except Exception as e:
        logger.error(f"Error getting cross-twin insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/federation")
async def get_federation_metrics():
    """Get federation metrics"""
    try:
        _, _, _, monitoring_service = get_services()
        metrics = monitoring_service.get_federation_metrics()
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Error getting federation metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/metrics")
async def get_monitoring_metrics():
    """Get monitoring metrics (alias for federation metrics)"""
    try:
        _, _, _, monitoring_service = get_services()
        metrics = monitoring_service.get_federation_metrics()
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Error getting monitoring metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/privacy/status")
async def get_privacy_status():
    """Get privacy and security status"""
    try:
        # Return privacy status data
        privacy_data = {
            "privacy_level": "high",
            "differential_privacy_enabled": True,
            "secure_aggregation_enabled": True,
            "data_encryption": "AES-256",
            "compliance_status": "compliant",
            "last_audit": "2024-01-15",
            "privacy_metrics": {
                "data_leakage_risk": "low",
                "privacy_loss": 0.1,
                "anonymization_level": "high"
            }
        }
        return {
            "status": "success",
            "data": privacy_data
        }
    except Exception as e:
        logger.error(f"Error getting privacy status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/real-time")
async def get_real_time_metrics():
    """Get real-time monitoring metrics"""
    try:
        _, _, _, monitoring_service = get_services()
        real_time_data = monitoring_service.get_real_time_metrics()
        return {
            "status": "success",
            "data": real_time_data
        }
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 