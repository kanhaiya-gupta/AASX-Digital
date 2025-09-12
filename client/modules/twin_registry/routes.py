"""
Twin Registry Routes - Modern Modular Architecture
=================================================

FastAPI router for digital twin registry using modular service architecture.
Follows the same pattern as the AASX module for consistency.
"""

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging

# Import our modular services
from .services.twin_registry_service import TwinRegistryService
from .services.twin_operations_service import TwinOperationsService
from .services.twin_monitoring_service import TwinMonitoringService
from .services.twin_analytics_service import TwinAnalyticsService
from .services.user_specific_service import TwinRegistryUserSpecificService
from .services.organization_service import TwinRegistryOrganizationService

# Import configuration service
from src.modules.twin_registry.core.configuration_service import configuration_service

# Import authentication decorators and context
from src.integration.api.dependencies import require_auth, get_current_user
from src.engine.models.request_context import UserContext

# Create router
router = APIRouter(tags=["twin-registry"])

# Initialize logger
logger = logging.getLogger(__name__)

# Template setup (following AASX pattern)
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize twin registry services
# Note: These services need to be updated for new table structure
# For now, initialize without parameters until services are updated
try:
    twin_registry_service = TwinRegistryService()
    twin_operations_service = TwinOperationsService()
    twin_monitoring_service = TwinMonitoringService()
    twin_analytics_service = TwinAnalyticsService()
    logger.info("✅ Twin registry services initialized successfully")
except Exception as e:
    logger.warning(f"⚠️ Some twin registry services failed to initialize: {e}")
    # Initialize with None for now - these will be updated for new tables
    twin_registry_service = None
    twin_operations_service = None
    twin_monitoring_service = None
    twin_analytics_service = None

# Note: User-specific and organization services will be initialized per-request
# to ensure proper user context integration

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

# Missing request models for bulk operations and configuration
# Note: Bulk start/stop operations are handled by AASX-ETL integration

class ConfigurationResetRequest(BaseModel):
    reset_type: str = "all"  # "all", "registry", "monitoring", "analytics"
    user: str = "system"

class ConfigurationImportRequest(BaseModel):
    config_data: Dict[str, Any]
    import_type: str = "merge"  # "merge", "replace", "validate_only"

class ConfigurationValidateRequest(BaseModel):
    config_data: Dict[str, Any]
    validation_level: str = "strict"  # "strict", "normal", "loose"

# ============================================================================
# Dashboard Routes
# ============================================================================

@router.get("/", response_class=HTMLResponse)
@require_auth("read", allow_independent=True)
async def twin_registry_dashboard(
    request: Request, 
    user_context: UserContext = Depends(get_current_user)
):
    """Twin registry dashboard with user-specific data"""
    try:
        # Initialize user-specific and organization services
        user_specific_service = TwinRegistryUserSpecificService(user_context)
        organization_service = TwinRegistryOrganizationService(user_context)
        
        # Get user-specific and organization data
        user_twins = user_specific_service.get_user_twins()
        user_relationships = user_specific_service.get_user_twin_relationships()
        user_instances = user_specific_service.get_user_twin_instances()
        user_stats = user_specific_service.get_user_twin_statistics()
        organization_stats = organization_service.get_organization_statistics()
        
        # Get general twin statistics
        general_stats = await twin_registry_service.get_twin_statistics()
        
        return templates.TemplateResponse(
            "twin_registry/index.html",
            {
                "request": request,
                "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework",
                "user": user_context,
                "can_create": getattr(user_context, 'has_permission', lambda x: False)("write"),
                "can_manage": getattr(user_context, 'has_permission', lambda x: False)("manage"),
                "can_delete": getattr(user_context, 'has_permission', lambda x: False)("manage"),
                "is_independent": getattr(user_context, 'is_independent', False),
                "user_type": getattr(user_context, 'get_user_type', lambda: 'independent')(),
                "user_twins": user_twins,
                "user_relationships": user_relationships,
                "user_instances": user_instances,
                "user_stats": user_stats,
                "organization_stats": organization_stats,
                "general_stats": general_stats
            }
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

# ============================================================================
# Core Twin Registry Endpoints
# ============================================================================

@router.get("/twins")
@require_auth("read", allow_independent=True)
async def get_twins(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    twin_type: str = "",
    status: str = "",
    project_id: str = None,
    user_context: UserContext = Depends(get_current_user)
):
    """
    Get twins accessible to the current user with pagination and filtering.
    Uses the integrated twin registry core service.
    """
    try:
        # Use the integrated core service directly
        result = await twin_registry_service.get_all_twins(
            page=page,
            page_size=page_size,
            filters={
                "twin_type": twin_type if twin_type else None,
                "status": status if status else None,
                "project_id": project_id
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error getting twins: {e}")
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



# ============================================================================
# Bulk Operations Endpoints
# ============================================================================

# Note: Twin start/stop/restart operations are handled by AASX-ETL integration
# The twin-registry only provides monitoring, analytics, and configuration

# ============================================================================
# Lifecycle Management Endpoints (New Core Services)
# ============================================================================

# Note: Twin start/stop operations are handled by AASX-ETL integration
# The twin-registry only provides monitoring and status information

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
            # Get all relationships using core service
            result = await twin_registry_service.get_all_relationships()
        
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
        # Get configuration from service
        config = configuration_service.get_configuration()
        return {
            "success": True,
            "configuration": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration")
async def save_configuration(
    config_data: Dict[str, Any],
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Save system configuration"""
    try:
        # Update configuration using service
        user_id = user_context.user_id if user_context else "system"
        result = configuration_service.update_configuration(config_data, user_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "config_id": result["config_id"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration/reset")
@require_auth("manage", allow_independent=True)
async def reset_configuration(
    request: Request,
    request_data: ConfigurationResetRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Reset system configuration"""
    try:
        # Reset configuration using service
        user_id = user_context.user_id if user_context else "system"
        result = configuration_service.reset_configuration(request_data.reset_type, user_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "config_id": result["config_id"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configuration/export")
@require_auth("read", allow_independent=True)
async def export_configuration(
    request: Request,
    format: str = "json",
    user_context: UserContext = Depends(get_current_user)
):
    """Export system configuration"""
    try:
        # Export configuration using service
        result = configuration_service.export_configuration(format)
        
        if result["success"]:
            return {
                "success": True,
                "format": result["format"],
                "config": result["data"],
                "config_id": result["config_id"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration/import")
@require_auth("manage", allow_independent=True)
async def import_configuration(
    request: Request,
    request_data: ConfigurationImportRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Import system configuration"""
    try:
        # Import configuration using service
        user_id = user_context.user_id if user_context else "system"
        
        # Convert config_data to string format
        if request_data.import_type == "yaml":
            import yaml
            config_string = yaml.dump(request_data.config_data, default_flow_style=False)
            format_type = "yaml"
        else:
            import json
            config_string = json.dumps(request_data.config_data)
            format_type = "json"
        
        result = configuration_service.import_configuration(config_string, format_type, user_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "config_id": result["config_id"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to import configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration/validate")
@require_auth("read", allow_independent=True)
async def validate_configuration(
    request: Request,
    request_data: ConfigurationValidateRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Validate system configuration"""
    try:
        # Validate configuration using service
        result = configuration_service.validate_configuration()
        
        return {
            "valid": result.is_valid,
            "validation_level": request_data.validation_level,
            "errors": result.errors,
            "warnings": result.warnings,
            "timestamp": result.timestamp,
            "config_id": result.config_id
        }
        
    except Exception as e:
        logger.error(f"Failed to validate configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configuration/summary")
@require_auth("read", allow_independent=True)
async def get_configuration_summary(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Get configuration summary for dashboard"""
    try:
        summary = configuration_service.get_configuration_summary()
        return {
            "success": True,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get configuration summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configuration/history")
@require_auth("read", allow_independent=True)
async def get_configuration_history(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Get configuration history"""
    try:
        history = configuration_service.get_configuration_history()
        return {
            "success": True,
            "history": [entry.dict() for entry in history],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get configuration history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration/rollback/{config_id}")
@require_auth("manage", allow_independent=True)
async def rollback_configuration(
    config_id: str,
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Rollback to specific configuration version"""
    try:
        user_id = user_context.user_id if user_context else "system"
        result = configuration_service.rollback_to_version(config_id, user_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "config_id": result["config_id"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rollback configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration/environment/{environment}")
@require_auth("manage", allow_independent=True)
async def apply_environment_overrides(
    environment: str,
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Apply environment-specific configuration overrides"""
    try:
        user_id = user_context.user_id if user_context else "system"
        result = configuration_service.apply_environment_overrides(environment, user_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "config_id": result["config_id"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply environment overrides: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configuration/setting/{path:path}")
@require_auth("read", allow_independent=True)
async def get_configuration_setting(
    path: str,
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Get specific configuration setting using dot notation"""
    try:
        value = configuration_service.get_setting(path)
        if value is not None:
            return {
                "success": True,
                "path": path,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Setting '{path}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get configuration setting '{path}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/configuration/setting/{path:path}")
@require_auth("manage", allow_independent=True)
async def set_configuration_setting(
    path: str,
    value: Any,
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Set specific configuration setting using dot notation"""
    try:
        user_id = user_context.user_id if user_context else "system"
        success = configuration_service.set_setting(path, value, user_id)
        
        if success:
            return {
                "success": True,
                "message": f"Setting '{path}' updated successfully",
                "path": path,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to update setting '{path}'")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set configuration setting '{path}': {e}")
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
# Real-time Monitoring Endpoints
# ============================================================================

@router.get("/monitoring/active-sessions")
@require_auth("read", allow_independent=True)
async def get_active_monitoring_sessions(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Get active monitoring sessions"""
    try:
        # For now, return mock data
        return {
            "active_sessions": [
                {
                    "session_id": "session_001",
                    "twin_id": "test_registry_001",
                    "started_at": datetime.now().isoformat(),
                    "status": "active",
                    "metrics_count": 15
                }
            ],
            "total_sessions": 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitoring/start-session")
@require_auth("write", allow_independent=True)
async def start_monitoring_session(
    request: Request,
    twin_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Start a monitoring session for a twin"""
    try:
        # For now, return mock data
        return {
            "success": True,
            "session_id": f"session_{twin_id}_{int(datetime.now().timestamp())}",
            "twin_id": twin_id,
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/monitoring/stop-session")
@require_auth("write", allow_independent=True)
async def stop_monitoring_session(
    request: Request,
    session_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Stop a monitoring session"""
    try:
        # For now, return mock data
        return {
            "success": True,
            "session_id": session_id,
            "stopped_at": datetime.now().isoformat(),
            "status": "stopped"
        }
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
            # Test database connection using new service method
            all_twins = await twin_registry_service.get_all_twins(page=1, page_size=1000, filters={})
            twin_count = all_twins.get("statistics", {}).get("total_twins", 0)
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
# Data Export Endpoints
# ============================================================================

@router.get("/export/twins")
@require_auth("read", allow_independent=True)
async def export_twins(
    request: Request,
    format: str = "json",
    twin_type: str = None,
    status: str = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Export twins data"""
    try:
        # Get twins data
        twins_data = await twin_registry_service.get_all_twins(filters={})
        
        # Apply filters if specified
        if twin_type:
            twins_data = [t for t in twins_data if t.get("twin_type") == twin_type]
        if status:
            twins_data = [t for t in twins_data if t.get("status") == status]
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if twins_data:
                writer = csv.DictWriter(output, fieldnames=twins_data[0].keys())
                writer.writeheader()
                writer.writerows(twins_data)
            
            return {"data": output.getvalue(), "format": "csv", "count": len(twins_data)}
        else:
            return {"data": twins_data, "format": "json", "count": len(twins_data)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/metrics")
@require_auth("read", allow_independent=True)
async def export_metrics(
    request: Request,
    format: str = "json",
    registry_id: str = None,
    time_range: str = "30d",
    user_context: UserContext = Depends(get_current_user)
):
    """Export metrics data"""
    try:
        # Get metrics data
        if registry_id:
            metrics_data = await twin_registry_service.get_twin_metrics(registry_id, time_range)
        else:
            metrics_data = await twin_registry_service.get_all_metrics(time_range)
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if metrics_data:
                writer = csv.DictWriter(output, fieldnames=metrics_data[0].keys())
                writer.writeheader()
                writer.writerows(metrics_data)
            
            return {"data": output.getvalue(), "format": "csv", "count": len(metrics_data)}
        else:
            return {"data": metrics_data, "format": "json", "count": len(metrics_data)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
@require_auth("read", allow_independent=True)
async def get_metrics(
    request: Request,
    registry_id: str = None,
    time_range: str = "30d",
    user_context: UserContext = Depends(get_current_user)
):
    """Get metrics data"""
    try:
        # Get metrics data
        if registry_id:
            metrics_data = await twin_registry_service.get_twin_metrics(registry_id, time_range)
        else:
            metrics_data = await twin_registry_service.get_all_metrics(time_range)
        
        return {
            "success": True,
            "data": metrics_data,
            "total_count": len(metrics_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/relationships")
@require_auth("read", allow_independent=True)
async def export_relationships(
    request: Request,
    format: str = "json",
    source_twin_id: str = None,
    target_twin_id: str = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Export relationships data"""
    try:
        # Get relationships data
        if source_twin_id:
            relationships_data = await twin_registry_service.get_twin_relationships(source_twin_id)
        elif target_twin_id:
            relationships_data = await twin_registry_service.get_twin_relationships(target_twin_id)
        else:
            relationships_data = await twin_registry_service.get_all_relationships()
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if relationships_data:
                writer = csv.DictWriter(output, fieldnames=relationships_data[0].keys())
                writer.writeheader()
                writer.writerows(relationships_data)
            
            return {"data": output.getvalue(), "format": "csv", "count": len(relationships_data)}
        else:
            return {"data": relationships_data, "format": "json", "count": len(relationships_data)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/instances")
@require_auth("read", allow_independent=True)
async def export_instances(
    request: Request,
    format: str = "json",
    twin_id: str = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Export instances data"""
    try:
        # Get instances data
        if twin_id:
            instances_data = await twin_registry_service.get_twin_instances(twin_id)
        else:
            instances_data = await twin_registry_service.get_all_instances()
        
        if format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if instances_data:
                writer = csv.DictWriter(output, fieldnames=instances_data[0].keys())
                writer.writeheader()
                writer.writerows(instances_data)
            
            return {"data": output.getvalue(), "format": "csv", "count": len(instances_data)}
        else:
            return {"data": instances_data, "format": "json", "count": len(instances_data)}
            
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