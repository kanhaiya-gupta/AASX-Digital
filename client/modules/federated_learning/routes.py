"""
Federated Learning Routes - Modern Modular Architecture
======================================================

FastAPI router for federated learning using modular service architecture.
Follows the same pattern as other modules for consistency.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import os
from pathlib import Path

# Import authentication dependencies
from webapp.core.decorators.auth_decorators import require_auth, get_current_user
from webapp.core.context.user_context import UserContext

# Import our modular services
from .federation_service import FederationService
from .twin_performance_service import TwinPerformanceService
from .insights_service import InsightsService
from .monitoring_service import MonitoringService

# Import authentication services
from .services.user_specific_service import FederatedLearningUserSpecificService
from .services.organization_service import FederatedLearningOrganizationService

# Import shared services and database managers (following twin_registry pattern)
from src.federated_learning.core.federated_learning_service import FederatedLearningService
# Migrated to new twin registry system
from src.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
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
# Migrated to new twin registry system
twin_registry_service = CoreTwinRegistryService()
federated_learning_service = FederatedLearningService(twin_registry_service)

# Initialize federated learning services
federation_service = FederationService(db_manager, digital_twin_service, federated_learning_service)
twin_performance_service = TwinPerformanceService(db_manager, twin_registry_service, federated_learning_service)
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
@require_auth("read", allow_independent=True)
async def federated_learning_dashboard(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Federated learning dashboard"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Get user-specific data
        user_federations = user_specific_service.get_user_federations()
        user_limits = user_specific_service.get_user_federation_limits()
        
        return templates.TemplateResponse(
            "federated_learning/index.html",
            {
                "request": request,
                "title": "Federated Learning - AASX Digital Twin Analytics Framework",
                "active_page": "federated-learning",
                "user_context": user_context,
                "user_federations": user_federations,
                "user_limits": user_limits
            }
        )
    except Exception as e:
        logger.error(f"Error rendering federated learning dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to render dashboard")

# ============================================================================
# API Routes
# ============================================================================

@router.post("/federation/start")
@require_auth("create", allow_independent=True)
async def start_federation(
    request: FederationStartRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Start federated learning process"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Check if user can start federations
        if not user_specific_service.can_start_federation():
            raise HTTPException(status_code=403, detail="Insufficient permissions to start federated learning")
        
        # Get user limits
        user_limits = user_specific_service.get_user_federation_limits()
        
        # Check if user has reached federation limit
        current_federations = len(user_specific_service.get_user_federations())
        if current_federations >= user_limits['max_federations']:
            raise HTTPException(
                status_code=400, 
                detail=f"Federation limit reached. Maximum allowed: {user_limits['max_federations']}"
            )
        
        # Check privacy level restrictions
        if request.privacy_level not in user_limits['privacy_levels']:
            raise HTTPException(
                status_code=400,
                detail=f"Privacy level '{request.privacy_level}' not allowed. Allowed levels: {user_limits['privacy_levels']}"
            )
        
        federation_service, _, _, _ = get_services()
        
        # Add user context to request
        federation_data = request.dict()
        federation_data['created_by'] = user_context.user_id
        federation_data['organization_id'] = getattr(user_context, 'organization_id', None)
        
        result = federation_service.start_federation(
            twin_ids=federation_data['twin_ids'],
            model_type=federation_data['model_type'],
            rounds=federation_data['rounds'],
            privacy_level=federation_data['privacy_level'],
            created_by=federation_data['created_by'],
            organization_id=federation_data['organization_id']
        )
        
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting federation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/federation/status")
@require_auth("read", allow_independent=True)
async def get_federation_status(
    user_context: UserContext = Depends(get_current_user)
):
    """Get federation status"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Get user-specific federations
        user_federations = user_specific_service.get_user_federations()
        
        federation_service, _, _, _ = get_services()
        
        # Get status for user's federations
        if user_federations:
            status = federation_service.get_federation_status()
            # Filter to only show user's federations
            filtered_status = {
                'federations': [f for f in status.get('federations', []) 
                               if f.get('id') in [uf.get('id') for uf in user_federations]],
                'total_count': len(user_federations),
                'active_count': len([f for f in user_federations if f.get('status') == 'active'])
            }
        else:
            filtered_status = {
                'federations': [],
                'total_count': 0,
                'active_count': 0
            }
        
        return {
            "status": "success",
            "data": filtered_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting federation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/federation/stop")
@require_auth("update", allow_independent=True)
async def stop_federation(
    user_context: UserContext = Depends(get_current_user)
):
    """Stop federated learning process"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Check if user can stop federations
        if not user_specific_service.can_stop_federation():
            raise HTTPException(status_code=403, detail="Insufficient permissions to stop federated learning")
        
        federation_service, _, _, _ = get_services()
        result = federation_service.stop_federation()
        
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping federation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twin/performance")
@require_auth("read", allow_independent=True)
async def get_twin_performance(
    user_context: UserContext = Depends(get_current_user)
):
    """Get twin performance metrics"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Get user-specific twin performance data
        user_twin_performance = user_specific_service.get_user_twin_performance()
        
        _, twin_performance_service, _, _ = get_services()
        
        # Get performance data and filter for user's twins
        if user_twin_performance:
            performance = twin_performance_service.get_twin_performance()
            # Filter to only show user's twins
            filtered_performance = [p for p in performance if p.get('twin_id') in 
                                  [utp.get('twin_id') for utp in user_twin_performance]]
        else:
            filtered_performance = []
        
        return {
            "status": "success",
            "data": filtered_performance
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting twin performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/performance")
@require_auth("read", allow_independent=True)
async def get_twins_performance(
    user_context: UserContext = Depends(get_current_user)
):
    """Get twins performance metrics (alias for twin/performance)"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Get user-specific twin performance data
        user_twin_performance = user_specific_service.get_user_twin_performance()
        
        _, twin_performance_service, _, _ = get_services()
        
        # Get performance data and filter for user's twins
        if user_twin_performance:
            performance = twin_performance_service.get_twin_performance()
            # Filter to only show user's twins
            filtered_performance = [p for p in performance if p.get('twin_id') in 
                                  [utp.get('twin_id') for utp in user_twin_performance]]
        else:
            filtered_performance = []
        
        return {
            "status": "success",
            "data": filtered_performance
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting twins performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
@require_auth("read", allow_independent=True)
async def get_insights(
    user_context: UserContext = Depends(get_current_user)
):
    """Get cross-twin insights"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Check if user can access insights
        if not user_specific_service.can_access_insights():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access insights")
        
        # Get user-specific insights data
        user_insights = user_specific_service.get_user_insights()
        
        _, _, insights_service, _ = get_services()
        
        # Get insights and filter for user's data
        if user_insights:
            insights = insights_service.get_insights()
            # Filter to only show insights relevant to user's twins
            filtered_insights = [i for i in insights if i.get('twin_id') in 
                               [ui.get('twin_id') for ui in user_insights]]
        else:
            filtered_insights = []
        
        return {
            "status": "success",
            "data": filtered_insights
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/federation")
@require_auth("read", allow_independent=True)
async def get_federation_metrics(
    user_context: UserContext = Depends(get_current_user)
):
    """Get federation metrics"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Get user-specific federations
        user_federations = user_specific_service.get_user_federations()
        
        _, _, _, monitoring_service = get_services()
        
        # Get metrics and filter for user's federations
        if user_federations:
            metrics = monitoring_service.get_federation_metrics()
            # Filter to only show metrics relevant to user's federations
            filtered_metrics = {k: v for k, v in metrics.items() 
                              if k in ['system_overview', 'general_stats'] or 
                              any(fed_id in str(v) for fed_id in [uf.get('id') for uf in user_federations])}
        else:
            # If no user-specific data, show basic system metrics
            metrics = monitoring_service.get_federation_metrics()
            filtered_metrics = {k: v for k, v in metrics.items() 
                              if k in ['system_overview', 'general_stats']}
        
        return {
            "status": "success",
            "data": filtered_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting federation metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring")
@require_auth("read", allow_independent=True)
async def get_monitoring(
    user_context: UserContext = Depends(get_current_user)
):
    """Get monitoring metrics"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Check if user can access monitoring
        if not user_specific_service.can_access_monitoring():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access monitoring")
        
        # Get user-specific monitoring data
        user_monitoring = user_specific_service.get_user_monitoring_metrics()
        
        _, _, _, monitoring_service = get_services()
        
        # Get monitoring data and filter for user's data
        if user_monitoring:
            monitoring = monitoring_service.get_monitoring_metrics()
            # Filter to only show monitoring relevant to user's federations
            filtered_monitoring = {k: v for k, v in monitoring.items() 
                                 if k in user_monitoring or k in ['system_status', 'overall_health']}
        else:
            # If no user-specific data, show basic system monitoring
            monitoring = monitoring_service.get_monitoring_metrics()
            filtered_monitoring = {k: v for k, v in monitoring.items() 
                                 if k in ['system_status', 'overall_health']}
        
        return {
            "status": "success",
            "data": filtered_monitoring
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/metrics")
@require_auth("read", allow_independent=True)
async def get_monitoring_metrics(
    user_context: UserContext = Depends(get_current_user)
):
    """Get monitoring metrics (alias for federation metrics)"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Get user-specific monitoring data
        user_monitoring = user_specific_service.get_user_monitoring_metrics()
        
        _, _, _, monitoring_service = get_services()
        
        # Get metrics and filter for user's data
        if user_monitoring:
            metrics = monitoring_service.get_federation_metrics()
            # Filter to only show metrics relevant to user's federations
            filtered_metrics = {k: v for k, v in metrics.items() 
                              if k in ['system_overview', 'general_stats'] or 
                              any(fed_id in str(v) for fed_id in user_monitoring.get('federation_ids', []))}
        else:
            # If no user-specific data, show basic system metrics
            metrics = monitoring_service.get_federation_metrics()
            filtered_metrics = {k: v for k, v in metrics.items() 
                              if k in ['system_overview', 'general_stats']}
        
        return {
            "status": "success",
            "data": filtered_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/privacy/status")
@require_auth("read", allow_independent=True)
async def get_privacy_status(
    user_context: UserContext = Depends(get_current_user)
):
    """Get privacy and security status"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Check if user can access privacy status
        if not user_specific_service.can_access_privacy_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access privacy status")
        
        # Get user-specific privacy data
        user_privacy = user_specific_service.get_user_privacy_status()
        
        # Get organization privacy settings if applicable
        if not user_specific_service.is_independent:
            org_service = FederatedLearningOrganizationService(user_context)
            org_collaboration = org_service.get_organization_collaboration_settings()
            user_privacy.update(org_collaboration)
        
        return {
            "status": "success",
            "data": user_privacy
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting privacy status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/real-time")
@require_auth("read", allow_independent=True)
async def get_real_time_metrics(
    user_context: UserContext = Depends(get_current_user)
):
    """Get real-time monitoring metrics"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = FederatedLearningUserSpecificService(user_context)
        
        # Check if user can access monitoring
        if not user_specific_service.can_access_monitoring():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access real-time monitoring")
        
        # Get user-specific monitoring data
        user_monitoring = user_specific_service.get_user_monitoring_metrics()
        
        _, _, _, monitoring_service = get_services()
        
        # Get real-time metrics and filter for user's data
        if user_monitoring:
            real_time_metrics = monitoring_service.get_real_time_metrics()
            # Filter to only show metrics relevant to user's federations
            filtered_metrics = {k: v for k, v in real_time_metrics.items() 
                              if k in ['system_status', 'overall_health'] or 
                              any(fed_id in str(v) for fed_id in user_monitoring.get('federation_ids', []))}
        else:
            # If no user-specific data, show basic system metrics
            real_time_metrics = monitoring_service.get_real_time_metrics()
            filtered_metrics = {k: v for k, v in real_time_metrics.items() 
                              if k in ['system_status', 'overall_health']}
        
        return {
            "status": "success",
            "data": filtered_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 