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

# Import AASX integration
from .aasx_integration import AASXIntegration
# Import real-time sync manager
from .realtime_sync import sync_manager, SyncStatus
# Import performance monitoring
from .performance_monitor import performance_monitor, MetricType
# Import enhanced twin management
from .twin_manager import twin_manager, TwinOperation, TwinStatus

# Create router
router = APIRouter(tags=["twin-registry"])

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize AASX integration
aasx_integration = AASXIntegration()

# Pydantic models
class TwinRegistration(BaseModel):
    twin_id: str
    twin_name: str
    twin_type: str
    aas_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    model_id: Optional[str] = None

class TwinUpdate(BaseModel):
    twin_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class TwinSyncRequest(BaseModel):
    twin_id: str
    sync_type: str
    force: bool = False

class AASXRegistrationRequest(BaseModel):
    aasx_filename: str
    project_id: str

# Mock twin data (will be replaced with real data from AASX integration)
TWINS_DB = [
    {
        "id": "dt-001",
        "twin_id": "dt-001",
        "twin_name": "Additive Manufacturing Facility",
        "twin_type": "additive_manufacturing",
        "aas_id": "aas-001",
        "description": "Digital twin for additive manufacturing facility with quality monitoring",
        "status": "active",
        "version": "1.0",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-07-08T15:30:00Z",
        "metadata": {
            "location": "Building A, Floor 2",
            "equipment_count": 15,
            "capacity": "1000 parts/day",
            "technology": "SLS, FDM, SLA"
        }
    },
    {
        "id": "dt-002",
        "twin_id": "dt-002",
        "twin_name": "Hydrogen Filling Station",
        "twin_type": "hydrogen_station",
        "aas_id": "aas-002",
        "description": "Digital twin for hydrogen filling station with safety monitoring",
        "status": "active",
        "version": "1.0",
        "created_at": "2024-02-20T14:00:00Z",
        "updated_at": "2024-07-08T16:45:00Z",
        "metadata": {
            "location": "Highway Exit 15",
            "storage_capacity": "5000 kg",
            "daily_capacity": "200 vehicles",
            "safety_level": "high"
        }
    },
    {
        "id": "dt-003",
        "twin_id": "dt-003",
        "twin_name": "Quality Control Lab",
        "twin_type": "quality_lab",
        "aas_id": "aas-003",
        "description": "Digital twin for quality control laboratory",
        "status": "active",
        "version": "1.0",
        "created_at": "2024-03-10T09:00:00Z",
        "updated_at": "2024-07-08T12:15:00Z",
        "metadata": {
            "location": "Building B, Floor 1",
            "equipment_count": 8,
            "certifications": ["ISO 17025", "ISO 9001"],
            "test_capacity": "500 samples/day"
        }
    }
]

@router.get("/", response_class=HTMLResponse)
async def twin_registry_dashboard(request: Request):
    """Twin registry dashboard"""
    print("🔍 Twin Registry dashboard route called")
    
    try:
        # Get real twins from AASX integration
        print("📊 Getting AASX twins...")
        aasx_twins = aasx_integration.get_all_twins_with_aasx()
        print(f"✅ Found {len(aasx_twins)} AASX twins")
    except Exception as e:
        print(f"⚠️ Warning: AASX integration error: {e}")
        aasx_twins = []
    
    # Combine mock data with real AASX twins
    all_twins = TWINS_DB + aasx_twins
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
):
    """Get twins with pagination and filtering"""
    print(f"🔍 /api/twins route called - page={page}, page_size={page_size}")
    
    try:
        # Get all twins from AASX integration
        aasx_twins = aasx_integration.get_all_twins_with_aasx()
        
        # Combine with mock data
        all_twins = TWINS_DB + aasx_twins
        
        # Apply filters
        filtered_twins = []
        for twin in all_twins:
            # Type filter
            if twin_type and twin.get("twin_type") != twin_type:
                continue
            
            # Status filter
            if status and twin.get("status") != status:
                continue
            
            # Owner filter
            if owner and twin.get("owner", "system") != owner:
                continue
            
            filtered_twins.append(twin)
        
        # Calculate pagination
        total_count = len(filtered_twins)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_twins = filtered_twins[start_index:end_index]
        
        # Calculate statistics
        active_count = len([t for t in filtered_twins if t.get("status") == "active"])
        total_data_points = sum([t.get("data_points", 0) for t in filtered_twins])
        active_alerts = len([t for t in filtered_twins if t.get("status") == "error"])
        
        print(f"✅ Returning {len(paginated_twins)} twins (page {page} of {total_count} total)")
        
        return {
            "twins": paginated_twins,
            "total_count": total_count,
            "active_count": active_count,
            "total_data_points": total_data_points,
            "active_alerts": active_alerts,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
        
    except Exception as e:
        print(f"❌ Error getting twins with pagination: {e}")
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
async def get_all_twins_summary():
    """Get summary of all twins with enhanced information"""
    print("🔍 /api/twins/summary route called")
    try:
        twins = await twin_manager.get_all_twins_summary()
        print(f"✅ Found {len(twins)} twins in summary")
        return {
            "success": True,
            "data": twins
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
        aasx_twins = aasx_integration.get_all_twins_with_aasx()
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
        # Find the twin
        twin = None
        for t in TWINS_DB:
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
        
        # Update twin status
        for i, t in enumerate(TWINS_DB):
            if t["twin_id"] == twin_id:
                t["status"] = "active"
                t["updated_at"] = datetime.now().isoformat()
                TWINS_DB[i] = t
                break
        
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
        # Calculate statistics
        total_twins = len(TWINS_DB)
        active_twins = len([twin for twin in TWINS_DB if twin["status"] == "active"])
        
        # Count by type
        type_counts = {}
        for twin in TWINS_DB:
            twin_type = twin["twin_type"]
            type_counts[twin_type] = type_counts.get(twin_type, 0) + 1
        
        # Recent activity
        recent_twins = [twin for twin in TWINS_DB if twin["created_at"] > "2024-06-01"]
        
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
        total_twins = len(TWINS_DB)
        active_twins = len([twin for twin in TWINS_DB if twin["status"] == "active"])
        
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

@router.post("/api/twins/register-from-aasx")
async def register_twin_from_aasx(request: AASXRegistrationRequest):
    """Register a new twin from processed AASX file"""
    try:
        result = aasx_integration.auto_register_twin_from_aasx(
            request.aasx_filename, 
            request.project_id
        )
        
        if result.get("success", False):
            return {
                "message": "Digital twin registered successfully from AASX",
                "twin_id": result["twin_id"],
                "twin_name": result["twin_name"],
                "aasx_filename": result["aasx_filename"],
                "status": result["status"]
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to register twin"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/{twin_id}/sync-status")
async def get_twin_sync_status(twin_id: str):
    """Get real-time sync status between twin and AASX data"""
    try:
        status = aasx_integration.get_sync_status(twin_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/aasx/discover")
async def discover_processed_aasx_files():
    """Discover AASX files that have been processed by the ETL pipeline"""
    try:
        files = aasx_integration.discover_processed_aasx_files()
        return {
            "files": files,
            "total_count": len(files),
            "discovered_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/aasx/auto-register-all")
async def auto_register_all_processed_aasx():
    """Automatically register twins for all processed AASX files"""
    try:
        files = aasx_integration.discover_processed_aasx_files()
        registered_twins = []
        errors = []
        
        for file_info in files:
            try:
                result = aasx_integration.auto_register_twin_from_aasx(
                    file_info["aasx_filename"],
                    file_info["project_id"]
                )
                
                if result.get("success", False):
                    registered_twins.append(result)
                else:
                    errors.append({
                        "file": file_info["aasx_filename"],
                        "error": result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                errors.append({
                    "file": file_info["aasx_filename"],
                    "error": str(e)
                })
        
        return {
            "message": f"Auto-registration completed. {len(registered_twins)} twins registered, {len(errors)} errors.",
            "registered_twins": registered_twins,
            "errors": errors,
            "total_processed": len(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/aasx/{aasx_filename}")
async def get_twin_by_aasx_filename(aasx_filename: str):
    """Get twin information by AASX filename"""
    try:
        twin = aasx_integration.get_twin_by_aasx(aasx_filename)
        
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
    """Get all available projects with AASX files"""
    try:
        projects = aasx_integration.get_all_projects()
        return {
            "success": True,
            "projects": projects,
            "total_count": len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/aasx/projects/{project_id}/files")
async def get_aasx_files_by_project(project_id: str):
    """Get all AASX files for a specific project"""
    try:
        # Get all processed files and filter by project
        all_files = aasx_integration.discover_processed_aasx_files()
        project_files = [file for file in all_files if file.get("project_id") == project_id]
        
        return {
            "success": True,
            "project_id": project_id,
            "files": project_files,
            "total_count": len(project_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/aasx/projects/{project_id}/auto-register")
async def auto_register_project_twins(project_id: str):
    """Auto-register all twins from a specific project"""
    try:
        result = aasx_integration.auto_register_project_twins(project_id)
        return result
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
    """Get comprehensive twin health data"""
    try:
        health = await twin_manager.get_twin_health(twin_id)
        if health:
            return {
                "success": True,
                "data": {
                    "twin_id": health.twin_id,
                    "overall_health": health.overall_health,
                    "performance_health": health.performance_health,
                    "connectivity_health": health.connectivity_health,
                    "data_health": health.data_health,
                    "operational_health": health.operational_health,
                    "last_check": health.last_check.isoformat(),
                    "issues": health.issues,
                    "recommendations": health.recommendations
                }
            }
        else:
            return {"success": False, "error": "Twin health data not found"}
    except Exception as e:
        print(f"Error getting twin health: {e}")
        return {"success": False, "error": str(e)} 