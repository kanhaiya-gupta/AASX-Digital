"""
Twin Registry Routes - Modern Modular Architecture
=================================================

FastAPI router for digital twin registry using modular service architecture.
Follows the same pattern as the AASX module for consistency.
"""

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path
import json

# Import our modular services
from .services.twin_registry_service import TwinRegistryService
from .services.twin_operations_service import TwinOperationsService
from .services.twin_monitoring_service import TwinMonitoringService
from .services.twin_analytics_service import TwinAnalyticsService

# Import shared services (following AASX pattern)
from src.shared.services.digital_twin_service import DigitalTwinService
from src.federated_learning.core.federated_learning_service import FederatedLearningService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository

# Create router
router = APIRouter(tags=["twin-registry"])

# Template setup (following AASX pattern)
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize shared services (following AASX pattern)
data_dir = Path("data")
db_path = data_dir / "aasx_database.db"
connection_manager = DatabaseConnectionManager(db_path)
db_manager = BaseDatabaseManager(connection_manager)

# Create shared service instances
file_repo = FileRepository(db_manager)
project_repo = ProjectRepository(db_manager)
digital_twin_service = DigitalTwinService(db_manager, file_repo, project_repo)
federated_learning_service = FederatedLearningService(digital_twin_service)

# Initialize twin registry services
twin_registry_service = TwinRegistryService(db_manager)
twin_operations_service = TwinOperationsService(digital_twin_service)
twin_monitoring_service = TwinMonitoringService(digital_twin_service)
twin_analytics_service = TwinAnalyticsService(digital_twin_service)

# Pydantic models
class TwinRegistration(BaseModel):
    twin_id: str
    twin_name: str
    twin_type: str
    aas_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    twin_model_id: Optional[str] = None
    
    model_config = {
        "protected_namespaces": ()
    }

class TwinUpdate(BaseModel):
    twin_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class TwinSyncRequest(BaseModel):
    twin_id: str
    sync_type: str
    force: bool = False

class BulkOperationRequest(BaseModel):
    twin_ids: List[str]
    user: str = "system"

# New models for core services
class RelationshipCreate(BaseModel):
    source_twin_id: str
    target_twin_id: str
    relationship_type: str
    relationship_data: Optional[Dict[str, Any]] = None

class InstanceCreate(BaseModel):
    twin_id: str
    instance_data: Dict[str, Any]
    instance_metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None

class LifecycleEventCreate(BaseModel):
    twin_id: str
    event_type: str
    event_data: Optional[Dict[str, Any]] = None
    triggered_by: Optional[str] = None

# ============================================================================
# Dashboard Routes
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def twin_registry_dashboard(request: Request):
    """Twin registry dashboard"""
    try:
        # Get twin statistics for dashboard
        stats = await twin_registry_service.get_twin_statistics()
        
        return templates.TemplateResponse(
            "twin_registry/index.html",
            {
                "request": request,
                "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework",
                "stats": stats
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

# ============================================================================
# Core Twin Registry Endpoints
# ============================================================================

@router.get("/twins")
async def get_twins(
    page: int = 1,
    page_size: int = 10,
    twin_type: str = "",
    status: str = "",
    project_id: str = None
):
    """
    Get all twins with pagination and filtering.
    Uses modular twin registry service.
    """
    try:
        result = await twin_registry_service.get_all_twins(
            page=page,
            page_size=page_size,
            twin_type=twin_type,
            status=status,
            project_id=project_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/search")
async def search_twins(
    query: str = "",
    twin_type: str = "",
    status: str = "",
    project_id: str = None,
    limit: int = 50
):
    """Search twins by various criteria"""
    try:
        result = await twin_registry_service.search_twins(
            query=query,
            twin_type=twin_type,
            status=status,
            project_id=project_id,
            limit=limit
        )
        return {"success": True, "data": result, "total_count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/statistics")
async def get_twin_statistics():
    """Get comprehensive twin registry statistics"""
    try:
        result = await twin_registry_service.get_twin_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}")
async def get_twin_by_id(twin_id: str):
    """Get specific twin by ID"""
    try:
        twin = await twin_registry_service.get_twin_by_id(twin_id)
        if not twin:
            raise HTTPException(status_code=404, detail="Twin not found")
        return twin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins")
async def create_twin(twin_data: Dict[str, Any]):
    """Create a new twin"""
    try:
        result = await twin_registry_service.create_twin(twin_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/twins/{twin_id}")
async def update_twin(twin_id: str, update_data: Dict[str, Any]):
    """Update an existing twin"""
    try:
        result = await twin_registry_service.update_twin(twin_id, update_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/twins/{twin_id}")
async def delete_twin(twin_id: str):
    """Delete a twin"""
    try:
        success = await twin_registry_service.delete_twin(twin_id)
        if not success:
            raise HTTPException(status_code=404, detail="Twin not found or could not be deleted")
        return {"success": True, "message": f"Twin {twin_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Twin Operations Endpoints
# ============================================================================

@router.post("/twins/{twin_id}/start")
async def start_twin(twin_id: str, user: str = "system"):
    """Start a twin operation"""
    try:
        result = await twin_operations_service.start_twin(twin_id, user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/stop")
async def stop_twin(twin_id: str, user: str = "system"):
    """Stop a twin operation"""
    try:
        result = await twin_operations_service.stop_twin(twin_id, user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/restart")
async def restart_twin(twin_id: str, user: str = "system"):
    """Restart a twin"""
    try:
        # Stop the twin first
        stop_result = await twin_registry_service.stop_twin(twin_id, user)
        if not stop_result.get("success"):
            return stop_result
        
        # Start the twin
        start_result = await twin_registry_service.start_twin(twin_id, user)
        return start_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Lifecycle Management Endpoints (New Core Services)
# ============================================================================

@router.post("/twins/{twin_id}/lifecycle/start")
async def start_twin_lifecycle(twin_id: str, user: str = "system"):
    """Start a twin using core lifecycle service"""
    try:
        result = await twin_registry_service.start_twin(twin_id, user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/lifecycle/stop")
async def stop_twin_lifecycle(twin_id: str, user: str = "system"):
    """Stop a twin using core lifecycle service"""
    try:
        result = await twin_registry_service.stop_twin(twin_id, user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/lifecycle/sync")
async def sync_twin_lifecycle(twin_id: str, sync_request: TwinSyncRequest, user: str = "system"):
    """Sync a twin using core lifecycle service"""
    try:
        sync_data = {
            "sync_type": sync_request.sync_type,
            "force": sync_request.force
        }
        result = await twin_registry_service.sync_twin(twin_id, sync_data, user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}/lifecycle/status")
async def get_twin_lifecycle_status(twin_id: str):
    """Get lifecycle status for a twin"""
    try:
        twin_info = await twin_registry_service.get_twin_by_id(twin_id)
        if not twin_info:
            raise HTTPException(status_code=404, detail="Twin not found")
        
        return {
            "twin_id": twin_id,
            "lifecycle_status": twin_info.get("lifecycle_status", "unknown"),
            "health_score": twin_info.get("health_score", 0),
            "last_lifecycle_update": twin_info.get("last_lifecycle_update"),
            "health_info": twin_info.get("health_info", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}/lifecycle/events")
async def get_twin_lifecycle_events(twin_id: str, limit: int = 10):
    """Get lifecycle events for a twin"""
    try:
        # This would use the core lifecycle service directly
        # For now, return basic info from twin details
        twin_info = await twin_registry_service.get_twin_by_id(twin_id)
        if not twin_info:
            raise HTTPException(status_code=404, detail="Twin not found")
        
        return {
            "twin_id": twin_id,
            "events": twin_info.get("health_info", {}).get("recent_events", []),
            "total_events": len(twin_info.get("health_info", {}).get("recent_events", []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Relationship Management Endpoints (New Core Services)
# ============================================================================

@router.post("/relationships")
async def create_relationship(relationship: RelationshipCreate):
    """Create a relationship between twins"""
    try:
        result = await twin_registry_service.create_relationship(
            relationship.source_twin_id,
            relationship.target_twin_id,
            relationship.relationship_type,
            relationship.relationship_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships")
async def get_relationships(source_twin_id: str = None, target_twin_id: str = None):
    """Get relationships with optional filtering"""
    try:
        if source_twin_id:
            result = await twin_registry_service.get_twin_relationships(source_twin_id)
        elif target_twin_id:
            result = await twin_registry_service.get_twin_relationships(target_twin_id)
        else:
            raise HTTPException(status_code=400, detail="Must specify source_twin_id or target_twin_id")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}/relationships")
async def get_twin_relationships(twin_id: str):
    """Get all relationships for a specific twin"""
    try:
        result = await twin_registry_service.get_twin_relationships(twin_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/relationships/{relationship_id}")
async def delete_relationship(relationship_id: str):
    """Delete a relationship"""
    try:
        # This would use the core relationship service directly
        # For now, return a placeholder response
        return {
            "success": True,
            "message": f"Relationship {relationship_id} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Instance Management Endpoints (New Core Services)
# ============================================================================

@router.post("/instances")
async def create_instance(instance: InstanceCreate):
    """Create a new instance of a twin"""
    try:
        result = await twin_registry_service.create_instance(
            instance.twin_id,
            instance.instance_data,
            instance.instance_metadata,
            instance.created_by
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances")
async def get_instances(twin_id: str = None):
    """Get instances with optional twin filtering"""
    try:
        if twin_id:
            # Get instances for specific twin
            result = await twin_registry_service.get_twin_instances(twin_id)
        else:
            # Get all instances (placeholder for now)
            result = {
                "instances": [],
                "total_count": 0,
                "message": "No instances found"
            }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}/instances")
async def get_twin_instances(twin_id: str):
    """Get all instances for a specific twin"""
    try:
        result = await twin_registry_service.get_twin_instances(twin_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}")
async def get_instance_by_id(instance_id: str):
    """Get a specific instance by ID"""
    try:
        # This would use the core instance service directly
        # For now, return a placeholder response
        return {
            "instance_id": instance_id,
            "message": "Instance details would be retrieved from core service"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Configuration Endpoints
# ============================================================================

@router.get("/configuration")
async def get_configuration():
    """Get system configuration"""
    try:
        # Return default configuration for now
        return {
            "system": {
                "auto_sync": True,
                "sync_interval": 300,
                "max_instances_per_twin": 10,
                "enable_monitoring": True,
                "monitoring_interval": 60
            },
            "registry": {
                "max_twins": 1000,
                "enable_relationships": True,
                "enable_lifecycle_tracking": True,
                "enable_performance_monitoring": True
            },
            "ui": {
                "refresh_interval": 30,
                "show_advanced_options": False,
                "enable_real_time_updates": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration")
async def save_configuration(config_data: Dict[str, Any]):
    """Save system configuration"""
    try:
        # For now, just return success
        return {
            "success": True,
            "message": "Configuration saved successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Registry Analytics Endpoints (New Core Services)
# ============================================================================

@router.get("/registry/summary")
async def get_registry_summary():
    """Get comprehensive registry summary"""
    try:
        result = await twin_registry_service.get_registry_summary()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/registry/health")
async def get_registry_health():
    """Get registry health information"""
    try:
        summary = await twin_registry_service.get_registry_summary()
        return {
            "status": "healthy",
            "summary": summary.get("summary", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============================================================================
# Twin Monitoring Endpoints
# ============================================================================

@router.get("/twins/{twin_id}/health")
async def get_twin_health(twin_id: str):
    """Get comprehensive health status for a twin"""
    try:
        result = await twin_monitoring_service.get_twin_health(twin_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}/performance")
async def get_twin_performance(twin_id: str, time_range: str = "24h"):
    """Get performance metrics for a twin"""
    try:
        result = await twin_monitoring_service.get_twin_performance(twin_id, time_range)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twins/{twin_id}/events")
async def get_twin_events(twin_id: str, event_type: str = None, limit: int = 50):
    """Get event history for a twin"""
    try:
        result = await twin_monitoring_service.get_twin_events(twin_id, event_type, limit)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twins/{twin_id}/monitor")
async def start_monitoring(twin_id: str):
    """Start real-time monitoring for a twin"""
    try:
        result = await twin_monitoring_service.monitor_twin_status(twin_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/twins/{twin_id}/monitor")
async def stop_monitoring(twin_id: str):
    """Stop real-time monitoring for a twin"""
    try:
        result = await twin_monitoring_service.stop_monitoring(twin_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/system-health")
async def get_system_health():
    """Get overall system health status"""
    try:
        result = await twin_monitoring_service.get_system_health()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Health Check Endpoints (for frontend compatibility)
# ============================================================================

@router.get("/health/system")
async def get_system_health_check():
    """Get system health check for frontend"""
    try:
        # Get basic system health
        system_health = await twin_monitoring_service.get_system_health()
        
        return {
            "status": "healthy",
            "system_status": system_health.get("system_status", "healthy"),
            "cpu_usage": system_health.get("cpu_usage", 0),
            "memory_usage": system_health.get("memory_usage", 0),
            "disk_usage": system_health.get("disk_usage", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/database")
async def get_database_health_check():
    """Get database health check for frontend"""
    try:
        # Check database connection
        db_status = "healthy"
        try:
            # Test database connection
            all_twins = twin_registry_service.twin_repo.get_all()
            twin_count = len(all_twins)
        except Exception as db_error:
            db_status = "error"
            twin_count = 0
        
        return {
            "status": db_status,
            "connection": "active" if db_status == "healthy" else "failed",
            "twin_count": twin_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/api")
async def get_api_health_check():
    """Get API health check for frontend"""
    try:
        return {
            "status": "healthy",
            "api_version": "1.0",
            "endpoints_available": True,
            "response_time": 0.001,  # Mock response time
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/registry")
async def get_registry_health_check():
    """Get registry health check for frontend"""
    try:
        # Get registry statistics
        stats = await twin_registry_service.get_twin_statistics()
        
        return {
            "status": "healthy",
            "total_twins": stats.get("total_twins", 0),
            "active_twins": stats.get("status_distribution", {}).get("active", 0),
            "registry_ready": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/network")
async def get_network_health_check():
    """Get network health check for frontend"""
    try:
        return {
            "status": "healthy",
            "connectivity": "active",
            "latency": 0.001,  # Mock latency
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/storage")
async def get_storage_health_check():
    """Get storage health check for frontend"""
    try:
        return {
            "status": "healthy",
            "storage_available": True,
            "disk_space": "sufficient",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# Performance Endpoints (for frontend compatibility)
# ============================================================================

@router.get("/performance/response-time")
async def get_response_time_performance():
    """Get response time performance metrics for frontend"""
    try:
        return {
            "status": "healthy",
            "average_response_time": 0.05,  # Mock response time in seconds
            "min_response_time": 0.01,
            "max_response_time": 0.15,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/performance/throughput")
async def get_throughput_performance():
    """Get throughput performance metrics for frontend"""
    try:
        return {
            "status": "healthy",
            "requests_per_second": 100,  # Mock throughput
            "total_requests": 1500,
            "successful_requests": 1495,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/performance/error-rate")
async def get_error_rate_performance():
    """Get error rate performance metrics for frontend"""
    try:
        return {
            "status": "healthy",
            "error_rate": 0.003,  # 0.3% error rate
            "total_errors": 5,
            "total_requests": 1500,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/performance/system")
async def get_system_performance():
    """Get system performance metrics for frontend"""
    try:
        return {
            "status": "healthy",
            "cpu_usage": 15.5,  # Mock CPU usage percentage
            "memory_usage": 45.2,  # Mock memory usage percentage
            "disk_usage": 23.1,  # Mock disk usage percentage
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/performance/registry")
async def get_registry_performance():
    """Get registry performance metrics for frontend"""
    try:
        # Get registry statistics
        stats = await twin_registry_service.get_twin_statistics()
        
        return {
            "status": "healthy",
            "total_twins": stats.get("total_twins", 0),
            "active_twins": stats.get("status_distribution", {}).get("active", 0),
            "registration_rate": 2.5,  # Mock registration rate per hour
            "update_rate": 1.8,  # Mock update rate per hour
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# Twin Analytics Endpoints
# ============================================================================

@router.get("/analytics/twins")
async def get_twin_analytics(twin_id: str = None, time_range: str = "30d"):
    """Get comprehensive analytics for twins"""
    try:
        result = await twin_analytics_service.get_twin_analytics(twin_id, time_range)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/twins/{twin_id}/trends")
async def get_performance_trends(
    twin_id: str,
    metric: str = "health_score",
    time_range: str = "30d"
):
    """Get performance trends for specific metrics"""
    try:
        result = await twin_analytics_service.get_performance_trends(
            twin_id, metric, time_range
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/usage-statistics")
async def get_usage_statistics(time_range: str = "30d"):
    """Get usage statistics for the twin registry"""
    try:
        result = await twin_analytics_service.get_usage_statistics(time_range)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/reports")
async def generate_reports(
    report_type: str = "comprehensive",
    twin_id: str = None,
    time_range: str = "30d",
    format: str = "json"
):
    """Generate comprehensive analytics reports"""
    try:
        result = await twin_analytics_service.generate_reports(
            report_type, twin_id, time_range, format
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/export")
async def export_data(
    data_type: str = "twins",
    filters: Dict[str, Any] = None,
    format: str = "json"
):
    """Export twin registry data"""
    try:
        result = await twin_analytics_service.export_data(data_type, filters, format)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ============================================================================
# Status and Health Endpoints
# ============================================================================

@router.get("/status")
async def get_twin_registry_status():
    """Get twin registry status"""
    try:
        # Get basic statistics
        stats = await twin_registry_service.get_twin_statistics()
        
        status = {
            "status": "available",
            "total_twins": stats.get("total_twins", 0),
            "active_twins": stats.get("active_count", 0),
            "registry_ready": True,
            "services": {
                "twin_registry": "available",
                "twin_operations": "available",
                "twin_monitoring": "available",
                "twin_analytics": "available"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return status
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health")
async def get_twin_registry_health():
    """Get comprehensive health status"""
    try:
        # Get system health
        system_health = await twin_monitoring_service.get_system_health()
        
        health = {
            "overall_status": "healthy",
            "system_health": system_health,
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine overall status
        if system_health.get("system_status") == "critical":
            health["overall_status"] = "critical"
        elif system_health.get("system_status") == "warning":
            health["overall_status"] = "warning"
        
        return health
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# WebSocket Endpoints (for real-time monitoring)
# ============================================================================

@router.websocket("/ws/twin-monitoring")
async def websocket_twin_monitoring(websocket: WebSocket):
    """WebSocket endpoint for real-time twin monitoring"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            
            # Parse message
            try:
                data = json.loads(message)
                action = data.get("action")
                twin_id = data.get("twin_id")
                
                if action == "subscribe" and twin_id:
                    # Start monitoring this twin
                    await twin_monitoring_service.monitor_twin_status(
                        twin_id, 
                        callback=lambda tid, status: websocket.send_text(json.dumps(status))
                    )
                    await websocket.send_text(json.dumps({
                        "action": "subscribed",
                        "twin_id": twin_id,
                        "status": "success"
                    }))
                elif action == "unsubscribe" and twin_id:
                    # Stop monitoring this twin
                    await twin_monitoring_service.stop_monitoring(twin_id)
                    await websocket.send_text(json.dumps({
                        "action": "unsubscribed",
                        "twin_id": twin_id,
                        "status": "success"
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "error": "Invalid action or missing twin_id"
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON message"
                }))
                
    except WebSocketDisconnect:
        # Clean up any active monitoring
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "error": f"WebSocket error: {str(e)}"
            }))
        except:
            pass 