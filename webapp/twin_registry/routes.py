"""
Twin Registry Routes
FastAPI router for digital twin registry and management functionality.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import random
import os

# Create router
router = APIRouter(tags=["twin-registry"])

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

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

# Mock twin data
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
    return templates.TemplateResponse(
        "twin_registry/index.html",
        {
            "request": request,
            "title": "Digital Twin Registry - QI Digital Platform",
            "twins": TWINS_DB,
            "twin_types": [
                {"id": "additive_manufacturing", "name": "Additive Manufacturing", "count": 1},
                {"id": "hydrogen_station", "name": "Hydrogen Station", "count": 1},
                {"id": "quality_lab", "name": "Quality Lab", "count": 1}
            ]
        }
    )

@router.get("/api/twins")
async def list_twins(twin_type: Optional[str] = None, status: Optional[str] = None, limit: int = 100, offset: int = 0):
    """List digital twins with optional filtering"""
    try:
        filtered_twins = TWINS_DB.copy()
        
        if twin_type:
            filtered_twins = [twin for twin in filtered_twins if twin["twin_type"] == twin_type]
        
        if status:
            filtered_twins = [twin for twin in filtered_twins if twin["status"] == status]
        
        # Apply pagination
        paginated_twins = filtered_twins[offset:offset + limit]
        
        return {
            "twins": paginated_twins,
            "total_count": len(filtered_twins),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/twins", response_model=Dict[str, Any])
async def register_twin(twin: TwinRegistration):
    """Register a new digital twin"""
    try:
        # Check if twin already exists
        for existing_twin in TWINS_DB:
            if existing_twin["twin_id"] == twin.twin_id:
                raise HTTPException(status_code=400, detail="Digital twin already exists")
        
        # Create new twin
        new_twin = {
            "id": twin.twin_id,
            "twin_id": twin.twin_id,
            "twin_name": twin.twin_name,
            "twin_type": twin.twin_type,
            "aas_id": twin.aas_id,
            "description": twin.description,
            "status": "pending_sync",
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": twin.metadata or {}
        }
        
        TWINS_DB.append(new_twin)
        
        return {
            "message": "Digital twin registered successfully",
            "twin_id": twin.twin_id,
            "status": "pending_sync"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/twins/{twin_id}")
async def get_twin(twin_id: str):
    """Get specific digital twin details"""
    try:
        for twin in TWINS_DB:
            if twin["twin_id"] == twin_id:
                return twin
        
        raise HTTPException(status_code=404, detail="Digital twin not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/twins/{twin_id}")
async def update_twin(twin_id: str, update: TwinUpdate):
    """Update digital twin"""
    try:
        for i, twin in enumerate(TWINS_DB):
            if twin["twin_id"] == twin_id:
                # Update fields
                if update.twin_name is not None:
                    twin["twin_name"] = update.twin_name
                if update.description is not None:
                    twin["description"] = update.description
                if update.metadata is not None:
                    twin["metadata"] = update.metadata
                if update.status is not None:
                    twin["status"] = update.status
                
                twin["updated_at"] = datetime.now().isoformat()
                TWINS_DB[i] = twin
                
                return twin
        
        raise HTTPException(status_code=404, detail="Digital twin not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/twins/{twin_id}")
async def delete_twin(twin_id: str):
    """Delete digital twin"""
    try:
        for i, twin in enumerate(TWINS_DB):
            if twin["twin_id"] == twin_id:
                del TWINS_DB[i]
                return {"message": "Digital twin deleted successfully"}
        
        raise HTTPException(status_code=404, detail="Digital twin not found")
        
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