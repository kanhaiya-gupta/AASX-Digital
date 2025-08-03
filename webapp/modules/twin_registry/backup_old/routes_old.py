"""
Twin Registry Routes
FastAPI router for digital twin registry and management functionality.
"""

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import random
import os

# Import real-time sync manager
from .realtime_sync import sync_manager, SyncStatus
# Import performance monitoring
from .performance_monitor import performance_monitor, MetricType
# Import enhanced twin management
from .twin_manager import twin_manager, TwinOperation, TwinStatus

# Import centralized file management system
from src.shared.management import ProjectManager, FileManagementError

# Create router
router = APIRouter(tags=["twin-registry"])

# Initialize centralized project manager
project_manager = ProjectManager()

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# AASX integration is now handled by TwinManager

# Pydantic models
class TwinRegistration(BaseModel):
    twin_id: str
    twin_name: str
    twin_type: str
    aas_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    model_id: Optional[str] = None
    
    class Config:
        protected_namespaces = ()

class TwinUpdate(BaseModel):
    twin_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class TwinSyncRequest(BaseModel):
    twin_id: str
    sync_type: str
    force: bool = False


@router.get("/", response_class=HTMLResponse)
async def twin_registry_dashboard(request: Request):
    """Twin registry dashboard"""
    print("🔍 Twin Registry dashboard route called")
    
    try:
        # Get real twins from TwinManager
        print("📊 Getting AASX twins...")
        aasx_twins = twin_manager.get_all_registered_twins()
        print(f"✅ Found {len(aasx_twins)} AASX twins")
    except Exception as e:
        print(f"⚠️ Warning: AASX integration error: {e}")
        aasx_twins = []
    
    # Combine mock data with real AASX twins
    all_twins = aasx_twins
    print(f"📋 Total twins: {len(all_twins)}")
    
    print("🎨 Rendering twin registry template...")
    return templates.TemplateResponse(
        "twin_registry/index.html",
        {
            "request": request,
            "title": "Digital Twin Registry - QI Digital Platform",
            "twins": all_twins,
            "twin_types": [
                {"id": "additive_manufacturing", "name": "Additive Manufacturing", "count": 1},
                {"id": "hydrogen_station", "name": "Hydrogen Station", "count": 1},
                {"id": "quality_lab", "name": "Quality Lab", "count": 1}
            ]
        }
    )

# Enhanced Twin Management Endpoints (Moved to top to avoid route conflicts)
@router.get("/api/twins")
async def get_twins_with_pagination(
    page: int = 1,
    page_size: int = 5,
    twin_type: str = "",
    status: str = "",
    owner: str = ""
) -> dict:
    """
    Get all registered twins for completed files, paginated and filtered.
    Args:
        page (int): Page number for pagination.
        page_size (int): Number of twins per page.
        twin_type (str): Optional filter for twin type.
        status (str): Optional filter for twin status.
        owner (str): Optional filter for twin owner.
    Returns:
        dict: Paginated list of twins and summary statistics.
    """
    print(f"🔍 /api/twins route called - page={page}, page_size={page_size}")
    try:
        all_twins = twin_manager.get_all_registered_twins()
        filtered_twins = []
        for twin in all_twins:
            if twin_type and twin.get("twin_type") != twin_type:
                continue
            if status and twin.get("status") != status:
                continue
            if owner and twin.get("owner", "system") != owner:
                continue
            filtered_twins.append(twin)
        total_count = len(filtered_twins)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_twins = filtered_twins[start_index:end_index]
        print(f"✅ Returning {len(paginated_twins)} twins (page {page} of {total_count} total)")
        return {
            "twins": paginated_twins,
            "total_count": total_count,
            "active_count": len([t for t in filtered_twins if t.get("status") == "active"]),
            "total_data_points": sum([t.get("data_points") or 0 for t in filtered_twins]),
            "active_alerts": len([t for t in filtered_twins if t.get("status") == "error"]),
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    except Exception as e:
        print(f"❌ Error getting twins: {e}")
        return {
            "twins": [],
            "total_count": 0,
            "active_count": 0,
            "total_data_points": 0,
            "active_alerts": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "error": str(e)
        }

@router.get("/api/twins/summary")
async def get_all_twins_summary() -> dict:
    """
    Get summary of all registered twins for completed files (for analytics, dashboards, etc.).
    Returns:
        dict: List of twins and summary information.
    """
    print("�� /api/twins/summary route called")
    try:
        all_twins = twin_manager.get_all_registered_twins()
        # Add summary fields if needed (or just return all_twins)
        print(f"✅ Found {len(all_twins)} twins in summary")
        return {
            "success": True,
            "data": all_twins
        }
    except Exception as e:
        print(f"❌ Error getting twins summary: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/twins/search")
async def search_twins(
    query: str = "",
    twin_type: str = "",
    owner: str = "",
    status: str = "",
    limit: int = 50
):
    """Search twins by various criteria"""
    try:
        twins = await twin_manager.get_all_twins_summary()
        
        # Apply filters
        filtered_twins = []
        for twin in twins:
            # Text search
            if query and query.lower() not in twin["twin_name"].lower():
                continue
            
            # Type filter
            if twin_type and twin["twin_type"] != twin_type:
                continue
            
            # Owner filter
            if owner and twin["owner"] != owner:
                continue
            
            # Status filter
            if status and twin["status"] != status:
                continue
            
            filtered_twins.append(twin)
        
        # Apply limit
        filtered_twins = filtered_twins[:limit]
        
        return {
            "success": True,
            "data": filtered_twins,
            "total_count": len(filtered_twins)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/api/twins/bulk/start")
async def bulk_start_twins(request: Dict[str, Any]):
    """Start multiple twins in bulk"""
    try:
        twin_ids = request.get("twin_ids", [])
        user = request.get("user", "system")
        
        results = []
        for twin_id in twin_ids:
            result = await twin_manager.start_twin(twin_id, user)
            results.append({
                "twin_id": twin_id,
                "success": result.get("success", False),
                "message": result.get("message", "Unknown error")
            })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "message": f"Started {success_count} of {len(twin_ids)} twins",
            "results": results
        }
    except Exception as e:
        print(f"Error bulk starting twins: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/twins/bulk/stop")
async def bulk_stop_twins(request: Dict[str, Any]):
    """Stop multiple twins in bulk"""
    try:
        twin_ids = request.get("twin_ids", [])
        user = request.get("user", "system")
        
        results = []
        for twin_id in twin_ids:
            result = await twin_manager.stop_twin(twin_id, user)
            results.append({
                "twin_id": twin_id,
                "success": result.get("success", False),
                "message": result.get("message", "Unknown error")
            })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "message": f"Stopped {success_count} of {len(twin_ids)} twins",
            "results": results
        }
    except Exception as e:
        print(f"Error bulk stopping twins: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/twins/{twin_id}")
async def get_twin_details(twin_id: str):
    """Get detailed twin information"""
    try:
        # First check if it's a registered twin
        twin = await twin_manager.get_twin_configuration(twin_id)
        if twin:
            return {
                "twin_id": twin.twin_id,
                "twin_name": twin.twin_name,
                "description": twin.description,
                "twin_type": twin.twin_type,
                "version": twin.version,
                "owner": twin.owner,
                "tags": twin.tags,
                "settings": twin.settings,
                "created_at": twin.created_at.isoformat() if twin.created_at else None,
                "updated_at": twin.updated_at.isoformat() if twin.updated_at else None
            }
        
        # Check if it's an AASX twin
        aasx_twins = twin_manager.get_all_registered_twins()
        for aasx_twin in aasx_twins:
            if aasx_twin["twin_id"] == twin_id:
                return aasx_twin
        
        raise HTTPException(status_code=404, detail="Digital twin not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/twins/{twin_id}")
async def update_twin_enhanced(twin_id: str, update_data: Dict[str, Any]):
    """Update twin with enhanced management"""
    try:
        result = await twin_manager.update_twin(twin_id, update_data)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Twin updated successfully",
                "twin_id": twin_id
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update twin"))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/twins/{twin_id}")
async def delete_twin_enhanced(twin_id: str):
    """Delete twin with enhanced management"""
    try:
        result = await twin_manager.delete_twin(twin_id, "system")
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Twin deleted successfully",
                "twin_id": twin_id
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete twin"))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/twins", response_model=Dict[str, Any])
async def create_twin_enhanced(twin_data: Dict[str, Any]):
    """Create a new digital twin with enhanced management"""
    try:
        # Validate required fields
        required_fields = ["twin_id", "twin_name", "twin_type"]
        for field in required_fields:
            if not twin_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Use enhanced twin manager
        result = await twin_manager.create_twin(twin_data)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Digital twin created successfully",
                "twin_id": twin_data["twin_id"],
                "status": "active"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create twin"))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/twins/{twin_id}/sync")
async def sync_twin(twin_id: str, sync_request: TwinSyncRequest):
    """Sync digital twin with AAS"""
    try:
        # Find the twin from TwinManager
        aasx_twins = twin_manager.get_all_registered_twins()
        twin = None
        for t in aasx_twins:
            if t["twin_id"] == twin_id:
                twin = t
                break
        
        if not twin:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        
        # Mock sync process
        sync_result = {
            "twin_id": twin_id,
            "sync_type": sync_request.sync_type,
            "status": "completed",
            "sync_timestamp": datetime.now().isoformat(),
            "details": {
                "aas_connection": "successful",
                "data_synced": random.randint(100, 1000),
                "errors": 0,
                "warnings": random.randint(0, 3)
            }
        }
        
        # Note: Twin status is managed by AASX integration database
        # No need to update here as it's handled by the integration system
        
        return sync_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/{twin_id}/instances")
async def get_twin_instances(twin_id: str, limit: int = 50):
    """Get twin instances"""
    try:
        # Mock instances
        instances = []
        for i in range(min(limit, 10)):
            instances.append({
                "id": f"instance-{twin_id}-{i+1}",
                "twin_id": twin_id,
                "instance_name": f"Instance {i+1}",
                "created_at": datetime.now().isoformat(),
                "status": random.choice(["running", "stopped", "error"]),
                "data_points": random.randint(100, 1000)
            })
        
        return {
            "twin_id": twin_id,
            "instances": instances,
            "total_count": len(instances)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/{twin_id}/relationships")
async def get_twin_relationships(twin_id: str):
    """Get twin relationships"""
    try:
        # Mock relationships
        relationships = [
            {
                "id": "rel-001",
                "source_twin_id": twin_id,
                "target_twin_id": "dt-002",
                "relationship_type": "communicates_with",
                "relationship_data": {
                    "protocol": "OPC UA",
                    "frequency": "real-time"
                }
            },
            {
                "id": "rel-002",
                "source_twin_id": twin_id,
                "target_twin_id": "dt-003",
                "relationship_type": "depends_on",
                "relationship_data": {
                    "dependency_type": "quality_assurance",
                    "criticality": "high"
                }
            }
        ]
        
        return {
            "twin_id": twin_id,
            "relationships": relationships,
            "total_count": len(relationships)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/statistics")
async def get_twin_statistics():
    """Get twin registry statistics"""
    try:
        # Get real twins from TwinManager
        aasx_twins = twin_manager.get_all_registered_twins()
        
        # Calculate statistics
        total_twins = len(aasx_twins)
        active_twins = len([twin for twin in aasx_twins if twin.get("status") == "active"])
        
        # Count by type
        type_counts = {}
        for twin in aasx_twins:
            twin_type = twin.get("twin_type", "unknown")
            type_counts[twin_type] = type_counts.get(twin_type, 0) + 1
        
        # Recent activity (using current timestamp for all twins since they're recent)
        recent_twins = aasx_twins  # All AASX twins are considered recent
        
        return {
            "total_twins": total_twins,
            "active_twins": active_twins,
            "inactive_twins": total_twins - active_twins,
            "type_distribution": type_counts,
            "recent_registrations": len(recent_twins),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_twin_registry_status():
    """Get twin registry status"""
    try:
        # Get real twins from TwinManager
        aasx_twins = twin_manager.get_all_registered_twins()
        
        total_twins = len(aasx_twins)
        active_twins = len([twin for twin in aasx_twins if twin.get("status") == "active"])
        
        status = {
            "status": "available",
            "total_twins": total_twins,
            "active_twins": active_twins,
            "registry_ready": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return status
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 

# AASX Integration Endpoints



@router.get("/api/twins/{twin_id}/sync-status")
async def get_twin_sync_status(twin_id: str):
    """Get real-time sync status between twin and AASX data"""
    try:
        status = twin_manager.get_sync_status(twin_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/aasx/discover")
async def discover_processed_aasx_files():
    """Discover AASX files that have been processed by checking FILES_DB status"""
    try:
        files = twin_manager.discover_processed_aasx_files()
        return {
            "files": files,
            "total_count": len(files),
            "method": "status_based",
            "discovered_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/twins/aasx/{aasx_filename}")
async def get_twin_by_aasx_filename(aasx_filename: str):
    """Get twin information by AASX filename"""
    try:
        twin = twin_manager.get_twin_by_aasx(aasx_filename)
        
        if twin:
            return twin
        else:
            raise HTTPException(status_code=404, detail="Twin not found for this AASX file")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/api/aasx/projects")
async def get_aasx_projects():
    """Get all available projects with AASX files using centralized project manager"""
    try:
        # Get projects from centralized manager
        projects = project_manager.list_projects()
        
        # Also get projects from AASX integration for backward compatibility
        try:
            aasx_projects = twin_manager.get_all_projects()
            
            # Merge projects, giving priority to centralized projects
            centralized_project_ids = {p.get('id') for p in projects}
            
            for project in aasx_projects:
                if project.get('project_id') not in centralized_project_ids:
                    # Convert AASX project format to centralized format
                    centralized_project = {
                        'id': project.get('project_id'),
                        'name': project.get('name', f"Project {project.get('project_id', 'Unknown')}"),
                        'description': f"AASX project: {project.get('name', 'Unknown')}",
                        'file_count': project.get('file_count', 0),
                        'created_at': project.get('created_at', 'Unknown'),
                        'updated_at': project.get('created_at', 'Unknown'),
                        'total_size': 0
                    }
                    projects.append(centralized_project)
        except Exception as e:
            # If AASX integration fails, continue with centralized projects only
            pass
        
        return {
            "success": True,
            "projects": projects,
            "total_count": len(projects)
        }
    except FileManagementError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/aasx/projects/{project_id}/files")
async def get_aasx_files_by_project(project_id: str):
    """Get all AASX files for a specific project using centralized project manager"""
    try:
        # Check if project exists in centralized system
        if not project_manager.project_exists(project_id):
            return {
                "success": False,
                "error": "Project not found"
            }
        
        # Get files from centralized manager
        project_files = project_manager.list_project_files(project_id)
        
        # Also get files from AASX integration for backward compatibility
        try:
            all_files = twin_manager.discover_processed_aasx_files()
            aasx_project_files = [file for file in all_files if file.get("project_id") == project_id]
            
            # Merge files, giving priority to centralized files
            centralized_file_ids = {f.get('id') for f in project_files}
            
            for file_info in aasx_project_files:
                if file_info.get('id') not in centralized_file_ids:
                    project_files.append(file_info)
        except Exception as e:
            # If AASX integration fails, continue with centralized files only
            pass
        
        return {
            "success": True,
            "project_id": project_id,
            "files": project_files,
            "total_count": len(project_files)
        }
    except FileManagementError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# Phase 2.1: Real-Time Sync Endpoints
# ============================================================================

@router.websocket("/ws/twin-sync")
async def websocket_twin_sync(websocket: WebSocket):
    """WebSocket endpoint for real-time twin synchronization"""
    await sync_manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            await sync_manager.handle_websocket_message(websocket, message)
            
    except WebSocketDisconnect:
        sync_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        sync_manager.disconnect(websocket)

@router.post("/api/twins/{twin_id}/realtime-sync")
async def start_realtime_sync(twin_id: str):
    """Start real-time synchronization for a specific twin"""
    try:
        # Start sync in background
        import asyncio
        asyncio.create_task(sync_manager.start_twin_sync(twin_id, "manual"))
        
        return {
            "message": f"Real-time sync started for twin {twin_id}",
            "twin_id": twin_id,
            "status": "syncing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/realtime/status")
async def get_realtime_sync_status():
    """Get real-time sync status for all twins"""
    try:
        statuses = await sync_manager.get_all_twin_sync_status()
        return {
            "twins": statuses,
            "total_connections": len(sync_manager.active_connections),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/twins/{twin_id}/subscribe")
async def subscribe_to_twin_updates(twin_id: str):
    """Subscribe to real-time updates for a specific twin (for non-WebSocket clients)"""
    try:
        # This endpoint is for clients that can't use WebSockets
        # They can poll this endpoint to get updates
        return {
            "message": f"Subscription request received for twin {twin_id}",
            "twin_id": twin_id,
            "polling_url": f"/api/twins/{twin_id}/sync-status"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/realtime/health")
async def get_realtime_health():
    """Get real-time system health metrics"""
    try:
        return {
            "active_connections": len(sync_manager.active_connections),
            "twin_subscriptions": len(sync_manager.twin_subscriptions),
            "total_twins_tracked": len(sync_manager.twin_sync_status),
            "system_status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

# Performance Monitoring Endpoints
@router.get("/api/performance/twins")
async def get_all_twin_performance():
    """Get performance data for all twins"""
    try:
        performance_data = await performance_monitor.get_all_twin_performance()
        return {
            "success": True,
            "data": [
                {
                    "twin_id": p.twin_id,
                    "twin_name": p.twin_name,
                    "cpu_usage": round(p.cpu_usage, 1),
                    "memory_usage": round(p.memory_usage, 1),
                    "response_time": round(p.response_time, 2),
                    "throughput": round(p.throughput, 1),
                    "error_rate": round(p.error_rate, 1),
                    "uptime_seconds": p.uptime_seconds,
                    "data_points_processed": p.data_points_processed,
                    "health_score": p.health_score,
                    "status": p.status,
                    "last_update": p.last_update.isoformat()
                }
                for p in performance_data
            ]
        }
    except Exception as e:
        # Assuming 'logger' is defined elsewhere or needs to be imported
        # For now, using print as a placeholder
        print(f"Error getting twin performance: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/performance/twins/{twin_id}")
async def get_twin_performance(twin_id: str):
    """Get performance data for a specific twin"""
    try:
        performance = await performance_monitor.get_twin_performance(twin_id)
        if not performance:
            return {"success": False, "error": "Twin not found"}
        
        return {
            "success": True,
            "data": {
                "twin_id": performance.twin_id,
                "twin_name": performance.twin_name,
                "cpu_usage": round(performance.cpu_usage, 1),
                "memory_usage": round(performance.memory_usage, 1),
                "response_time": round(performance.response_time, 2),
                "throughput": round(performance.throughput, 1),
                "error_rate": round(performance.error_rate, 1),
                "uptime_seconds": performance.uptime_seconds,
                "data_points_processed": performance.data_points_processed,
                "health_score": performance.health_score,
                "status": performance.status,
                "last_update": performance.last_update.isoformat()
            }
        }
    except Exception as e:
        # Assuming 'logger' is defined elsewhere or needs to be imported
        # For now, using print as a placeholder
        print(f"Error getting twin performance: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/performance/twins/{twin_id}/history")
async def get_twin_performance_history(
    twin_id: str, 
    metric_type: str = "cpu_usage",
    hours: int = 24
):
    """Get performance history for a specific twin and metric"""
    try:
        # Convert string to MetricType enum
        try:
            metric_enum = MetricType(metric_type)
        except ValueError:
            return {"success": False, "error": f"Invalid metric type: {metric_type}"}
        
        history = await performance_monitor.get_performance_history(twin_id, metric_enum, hours)
        
        return {
            "success": True,
            "data": {
                "twin_id": twin_id,
                "metric_type": metric_type,
                "hours": hours,
                "history": history
            }
        }
    except Exception as e:
        # Assuming 'logger' is defined elsewhere or needs to be imported
        # For now, using print as a placeholder
        print(f"Error getting performance history: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/performance/alerts")
async def get_performance_alerts():
    """Get all active performance alerts"""
    try:
        alerts = await performance_monitor.get_active_alerts()
        
        return {
            "success": True,
            "data": alerts
        }
    except Exception as e:
        # Assuming 'logger' is defined elsewhere or needs to be imported
        # For now, using print as a placeholder
        print(f"Error getting alerts: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/performance/alerts/{alert_id}/resolve")
async def resolve_performance_alert(alert_id: int):
    """Mark a performance alert as resolved"""
    try:
        await performance_monitor.resolve_alert(alert_id)
        
        return {
            "success": True,
            "message": f"Alert {alert_id} resolved successfully"
        }
    except Exception as e:
        # Assuming 'logger' is defined elsewhere or needs to be imported
        # For now, using print as a placeholder
        print(f"Error resolving alert: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/performance/dashboard")
async def get_performance_dashboard():
    """Get comprehensive performance dashboard data"""
    try:
        # Get all twin performance
        performance_data = await performance_monitor.get_all_twin_performance()
        
        # Get active alerts
        alerts = await performance_monitor.get_active_alerts()
        
        # Calculate summary statistics
        total_twins = len(performance_data)
        healthy_twins = len([p for p in performance_data if p.health_score >= 75])
        warning_twins = len([p for p in performance_data if 60 <= p.health_score < 75])
        critical_twins = len([p for p in performance_data if p.health_score < 60])
        
        avg_health_score = sum(p.health_score for p in performance_data) / total_twins if total_twins > 0 else 0
        avg_cpu_usage = sum(p.cpu_usage for p in performance_data) / total_twins if total_twins > 0 else 0
        avg_memory_usage = sum(p.memory_usage for p in performance_data) / total_twins if total_twins > 0 else 0
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_twins": total_twins,
                    "healthy_twins": healthy_twins,
                    "warning_twins": warning_twins,
                    "critical_twins": critical_twins,
                    "avg_health_score": round(avg_health_score, 1),
                    "avg_cpu_usage": round(avg_cpu_usage, 1),
                    "avg_memory_usage": round(avg_memory_usage, 1)
                },
                "twins": [
                    {
                        "twin_id": p.twin_id,
                        "twin_name": p.twin_name,
                        "health_score": p.health_score,
                        "status": p.status,
                        "cpu_usage": round(p.cpu_usage, 1),
                        "memory_usage": round(p.memory_usage, 1),
                        "response_time": round(p.response_time, 2),
                        "error_rate": round(p.error_rate, 1)
                    }
                    for p in performance_data
                ],
                "alerts": alerts
            }
        }
    except Exception as e:
        # Assuming 'logger' is defined elsewhere or needs to be imported
        # For now, using print as a placeholder
        print(f"Error getting performance dashboard: {e}")
        return {"success": False, "error": str(e)} 

# Enhanced Twin Management Endpoints (Additional routes - no conflicts)
@router.post("/api/twins/{twin_id}/start")
async def start_twin_operation(twin_id: str, user: str = "system"):
    """Start a twin operation"""
    try:
        result = await twin_manager.start_twin(twin_id, user)
        return result
    except Exception as e:
        print(f"Error starting twin: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/twins/{twin_id}/stop")
async def stop_twin_operation(twin_id: str, user: str = "system"):
    """Stop a twin operation"""
    try:
        result = await twin_manager.stop_twin(twin_id, user)
        return result
    except Exception as e:
        print(f"Error stopping twin: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/twins/{twin_id}/restart")
async def restart_twin_operation(twin_id: str, user: str = "system"):
    """Restart a twin operation"""
    try:
        result = await twin_manager.restart_twin(twin_id, user)
        return result
    except Exception as e:
        print(f"Error restarting twin: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/twins/{twin_id}/configuration")
async def get_twin_configuration(twin_id: str):
    """Get twin configuration"""
    try:
        config = await twin_manager.get_twin_configuration(twin_id)
        if config:
            return {
                "success": True,
                "data": {
                    "twin_id": config.twin_id,
                    "twin_name": config.twin_name,
                    "description": config.description,
                    "twin_type": config.twin_type,
                    "version": config.version,
                    "owner": config.owner,
                    "tags": config.tags,
                    "settings": config.settings,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat()
                }
            }
        else:
            return {"success": False, "error": "Twin configuration not found"}
    except Exception as e:
        print(f"Error getting twin configuration: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/twins/{twin_id}/events")
async def get_twin_events(twin_id: str, limit: int = 50):
    """Get twin event history"""
    try:
        events = await twin_manager.get_twin_events(twin_id, limit)
        return {
            "success": True,
            "data": [
                {
                    "twin_id": event.twin_id,
                    "event_type": event.event_type,
                    "event_message": event.event_message,
                    "severity": event.severity,
                    "timestamp": event.timestamp.isoformat(),
                    "user": event.user,
                    "metadata": event.metadata
                }
                for event in events
            ]
        }
    except Exception as e:
        print(f"Error getting twin events: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/twins/{twin_id}/health")
async def get_twin_health(twin_id: str):
    """Get twin health status"""
    try:
        # Get twin details
        twin = twin_manager.get_twin(twin_id)
        if not twin:
            raise HTTPException(status_code=404, detail="Twin not found")
        
        # Get performance metrics
        performance = performance_monitor.get_twin_performance(twin_id)
        
        # Get sync status
        sync_status = twin_manager.get_sync_status(twin_id)
        
        # Determine overall health
        health_status = "healthy"
        issues = []
        
        if performance.get('cpu_usage', 0) > 80:
            health_status = "warning"
            issues.append("High CPU usage")
        
        if performance.get('memory_usage', 0) > 85:
            health_status = "warning"
            issues.append("High memory usage")
        
        if sync_status.get('status') == 'out_of_sync':
            health_status = "warning"
            issues.append("Data out of sync")
        
        if twin.get('status') == 'orphaned':
            health_status = "orphaned"
            issues.append("No output data available")
        
        return {
            "twin_id": twin_id,
            "health_status": health_status,
            "issues": issues,
            "performance": performance,
            "sync_status": sync_status,
            "last_check": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ORPHANED TWIN MANAGEMENT ====================

@router.get("/api/twins/orphaned")
async def get_orphaned_twins():
    """Get all orphaned twins"""
    try:
        orphaned_twins = twin_manager.get_orphaned_twins()
        return {
            "orphaned_twins": orphaned_twins,
            "count": len(orphaned_twins),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/twins/{twin_id}/restore")
async def restore_orphaned_twin(twin_id: str):
    """Restore orphaned twin when output data is available"""
    try:
        # Get twin information
        twin = twin_manager.get_twin_by_aasx(twin_id)
        if not twin:
            raise HTTPException(status_code=404, detail="Twin not found")
        
        if twin.get('status') != 'orphaned':
            raise HTTPException(status_code=400, detail="Twin is not orphaned")
        
        # Check if output data is available
        aasx_filename = twin.get('aasx_filename')
        project_id = twin.get('project_id')
        
        if not aasx_filename or not project_id:
            raise HTTPException(status_code=400, detail="Missing AASX filename or project ID")
        
        # Try to restore twin status
        result = twin_manager.db_manager.update_twin_status_to_active(aasx_filename, project_id)
        
        if result.get('success', False):
            return {
                "success": True,
                "message": f"Twin {twin_id} restored to active status",
                "twin_id": twin_id,
                "previous_status": "orphaned",
                "new_status": "active"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to restore twin'))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/twins/orphaned/restore-all")
async def restore_all_orphaned_twins():
    """Restore all orphaned twins that have output data available"""
    try:
        orphaned_twins = twin_manager.get_orphaned_twins()
        restored_count = 0
        failed_count = 0
        results = []
        
        for twin in orphaned_twins:
            try:
                result = twin_manager.db_manager.update_twin_status_to_active(
                    twin['aasx_filename'], 
                    twin['project_id']
                )
                
                if result.get('success', False):
                    restored_count += 1
                    results.append({
                        "twin_id": twin['twin_id'],
                        "status": "restored",
                        "message": "Successfully restored"
                    })
                else:
                    failed_count += 1
                    results.append({
                        "twin_id": twin['twin_id'],
                        "status": "failed",
                        "error": result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                failed_count += 1
                results.append({
                    "twin_id": twin['twin_id'],
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Restored {restored_count} twins, {failed_count} failed",
            "restored_count": restored_count,
            "failed_count": failed_count,
            "total_orphaned": len(orphaned_twins),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Removed redundant status-based endpoints - now using status-based discovery as primary method 