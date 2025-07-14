"""
Digital Twin Registry and Management System
This system manages digital twin registration, synchronization, and lifecycle management.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime, timedelta
import os
import uuid

# Database imports
import asyncpg
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Digital Twin Registry",
    description="Registry and management system for digital twins",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aasx_user:aasx_password@localhost:5432/aasx_data")
AAS_ENDPOINT = os.getenv("AAS_ENDPOINT", "http://localhost:1111")
TWIN_STORAGE_PATH = os.getenv("TWIN_STORAGE_PATH", "/app/digital-twins")

# Pydantic models
class TwinRegistration(BaseModel):
    twin_id: str = Field(..., description="Unique identifier for the digital twin")
    twin_name: str = Field(..., description="Human-readable name for the twin")
    twin_type: str = Field(..., description="Type of digital twin (additive_manufacturing, hydrogen_station, etc.)")
    aas_id: Optional[str] = Field(None, description="Associated AAS ID")
    description: Optional[str] = Field(None, description="Description of the digital twin")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    model_id: Optional[str] = Field(None, description="Reference to twin model")

class TwinUpdate(BaseModel):
    twin_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class TwinSyncRequest(BaseModel):
    twin_id: str
    sync_type: str = Field(..., description="Type of sync: full, incremental, metadata")
    force: bool = False

class TwinRelationship(BaseModel):
    source_twin_id: str
    target_twin_id: str
    relationship_type: str = Field(..., description="Type of relationship: contains, depends_on, communicates_with")
    relationship_data: Optional[Dict[str, Any]] = None

# Database connection pool
async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@app.on_event("startup")
async def startup_event():
    """Initialize the twin registry on startup"""
    try:
        # Ensure twin storage directory exists
        os.makedirs(TWIN_STORAGE_PATH, exist_ok=True)
        logger.info("Digital Twin Registry initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing twin registry: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if we can connect to external services
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "database": "unknown",
                "aas_endpoint": "unknown"
            }
        }
        
        # Try database connection
        try:
            pool = await get_db_pool()
            await pool.close()
            health_status["services"]["database"] = "connected"
        except Exception as e:
            health_status["services"]["database"] = "disconnected"
            logger.warning(f"Database connection failed: {e}")
        
        # Try AAS endpoint connection
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{AAS_ENDPOINT}/health", timeout=5)
                if response.status_code == 200:
                    health_status["services"]["aas_endpoint"] = "connected"
                else:
                    health_status["services"]["aas_endpoint"] = "unavailable"
        except Exception as e:
            health_status["services"]["aas_endpoint"] = "disconnected"
            logger.warning(f"AAS endpoint connection failed: {e}")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow()}

@app.post("/register")
async def register_twin(
    twin: TwinRegistration,
    background_tasks: BackgroundTasks,
    db_pool=Depends(get_db_pool)
):
    """Register a new digital twin"""
    try:
        # Check if twin already exists
        async with db_pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT twin_id FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin.twin_id
            )
            
            if existing:
                raise HTTPException(status_code=400, detail="Digital twin already exists")
            
            # Insert new twin
            await conn.execute(
                """
                INSERT INTO digital_twins.twin_registry 
                (twin_id, twin_name, twin_type, aas_id, description, metadata, version, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                twin.twin_id,
                twin.twin_name,
                twin.twin_type,
                twin.aas_id,
                twin.description,
                json.dumps(twin.metadata) if twin.metadata else None,
                "1.0",
                "system"
            )
        
        # Schedule initial sync
        background_tasks.add_task(sync_twin_with_aas, twin.twin_id, "full", db_pool)
        
        return {
            "message": "Digital twin registered successfully",
            "twin_id": twin.twin_id,
            "status": "pending_sync"
        }
        
    except Exception as e:
        logger.error(f"Error registering twin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/twins")
async def list_twins(
    twin_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db_pool=Depends(get_db_pool)
):
    """List digital twins with optional filtering"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM digital_twins.twin_registry WHERE 1=1"
            params = []
            param_count = 0
            
            if twin_type:
                param_count += 1
                query += f" AND twin_type = ${param_count}"
                params.append(twin_type)
            
            if status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(status)
            
            query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([limit, offset])
            
            twins = await conn.fetch(query, *params)
            
            return [dict(twin) for twin in twins]
            
    except Exception as e:
        logger.error(f"Error listing twins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/twins/{twin_id}")
async def get_twin(twin_id: str, db_pool=Depends(get_db_pool)):
    """Get specific digital twin details"""
    try:
        async with db_pool.acquire() as conn:
            twin = await conn.fetchrow(
                "SELECT * FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not twin:
                raise HTTPException(status_code=404, detail="Digital twin not found")
            
            # Get twin instances
            instances = await conn.fetch(
                "SELECT * FROM digital_twins.twin_instances WHERE twin_id = $1 ORDER BY created_at DESC",
                twin['id']
            )
            
            # Get relationships
            relationships = await conn.fetch(
                """
                SELECT tr.*, rt.twin_name as target_name 
                FROM digital_twins.twin_relationships tr
                JOIN digital_twins.twin_registry rt ON tr.target_twin_id = rt.id
                WHERE tr.source_twin_id = $1
                """,
                twin['id']
            )
            
            return {
                "twin": dict(twin),
                "instances": [dict(instance) for instance in instances],
                "relationships": [dict(rel) for rel in relationships]
            }
            
    except Exception as e:
        logger.error(f"Error getting twin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/twins/{twin_id}")
async def update_twin(
    twin_id: str,
    update: TwinUpdate,
    db_pool=Depends(get_db_pool)
):
    """Update digital twin information"""
    try:
        async with db_pool.acquire() as conn:
            # Check if twin exists
            existing = await conn.fetchrow(
                "SELECT id FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not existing:
                raise HTTPException(status_code=404, detail="Digital twin not found")
            
            # Build update query
            update_fields = []
            params = []
            param_count = 0
            
            if update.twin_name is not None:
                param_count += 1
                update_fields.append(f"twin_name = ${param_count}")
                params.append(update.twin_name)
            
            if update.description is not None:
                param_count += 1
                update_fields.append(f"description = ${param_count}")
                params.append(update.description)
            
            if update.metadata is not None:
                param_count += 1
                update_fields.append(f"metadata = ${param_count}")
                params.append(json.dumps(update.metadata))
            
            if update.status is not None:
                param_count += 1
                update_fields.append(f"status = ${param_count}")
                params.append(update.status)
            
            if update_fields:
                param_count += 1
                update_fields.append(f"updated_at = ${param_count}")
                params.append(datetime.utcnow())
                
                param_count += 1
                params.append(twin_id)
                
                query = f"UPDATE digital_twins.twin_registry SET {', '.join(update_fields)} WHERE twin_id = ${param_count}"
                await conn.execute(query, *params)
            
            return {"message": "Digital twin updated successfully"}
            
    except Exception as e:
        logger.error(f"Error updating twin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/twins/{twin_id}")
async def delete_twin(twin_id: str, db_pool=Depends(get_db_pool)):
    """Delete a digital twin"""
    try:
        async with db_pool.acquire() as conn:
            # Check if twin exists
            existing = await conn.fetchrow(
                "SELECT id FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not existing:
                raise HTTPException(status_code=404, detail="Digital twin not found")
            
            # Delete twin (cascade will handle related data)
            await conn.execute(
                "DELETE FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            return {"message": "Digital twin deleted successfully"}
            
    except Exception as e:
        logger.error(f"Error deleting twin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/twins/{twin_id}/sync")
async def sync_twin(
    twin_id: str,
    sync_request: TwinSyncRequest,
    background_tasks: BackgroundTasks,
    db_pool=Depends(get_db_pool)
):
    """Synchronize digital twin with AAS"""
    try:
        async with db_pool.acquire() as conn:
            # Check if twin exists
            twin = await conn.fetchrow(
                "SELECT * FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not twin:
                raise HTTPException(status_code=404, detail="Digital twin not found")
            
            # Update sync status
            await conn.execute(
                """
                UPDATE digital_twins.twin_registry 
                SET sync_status = 'syncing', last_sync_at = $1 
                WHERE twin_id = $2
                """,
                datetime.utcnow(),
                twin_id
            )
        
        # Start sync in background
        background_tasks.add_task(sync_twin_with_aas, twin_id, sync_request.sync_type, db_pool)
        
        return {
            "message": "Synchronization started",
            "twin_id": twin_id,
            "sync_type": sync_request.sync_type
        }
        
    except Exception as e:
        logger.error(f"Error starting sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/relationships")
async def create_relationship(
    relationship: TwinRelationship,
    db_pool=Depends(get_db_pool)
):
    """Create a relationship between digital twins"""
    try:
        async with db_pool.acquire() as conn:
            # Get twin IDs
            source_twin = await conn.fetchrow(
                "SELECT id FROM digital_twins.twin_registry WHERE twin_id = $1",
                relationship.source_twin_id
            )
            
            target_twin = await conn.fetchrow(
                "SELECT id FROM digital_twins.twin_registry WHERE twin_id = $1",
                relationship.target_twin_id
            )
            
            if not source_twin or not target_twin:
                raise HTTPException(status_code=404, detail="One or both twins not found")
            
            # Check if relationship already exists
            existing = await conn.fetchrow(
                """
                SELECT id FROM digital_twins.twin_relationships 
                WHERE source_twin_id = $1 AND target_twin_id = $2 AND relationship_type = $3
                """,
                source_twin['id'],
                target_twin['id'],
                relationship.relationship_type
            )
            
            if existing:
                raise HTTPException(status_code=400, detail="Relationship already exists")
            
            # Create relationship
            await conn.execute(
                """
                INSERT INTO digital_twins.twin_relationships 
                (source_twin_id, target_twin_id, relationship_type, relationship_data)
                VALUES ($1, $2, $3, $4)
                """,
                source_twin['id'],
                target_twin['id'],
                relationship.relationship_type,
                json.dumps(relationship.relationship_data) if relationship.relationship_data else None
            )
            
            return {"message": "Relationship created successfully"}
            
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/relationships/{twin_id}")
async def get_relationships(twin_id: str, db_pool=Depends(get_db_pool)):
    """Get relationships for a digital twin"""
    try:
        async with db_pool.acquire() as conn:
            # Get twin ID
            twin = await conn.fetchrow(
                "SELECT id FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not twin:
                raise HTTPException(status_code=404, detail="Digital twin not found")
            
            # Get outgoing relationships
            outgoing = await conn.fetch(
                """
                SELECT tr.*, rt.twin_name as target_name, rt.twin_id as target_twin_id
                FROM digital_twins.twin_relationships tr
                JOIN digital_twins.twin_registry rt ON tr.target_twin_id = rt.id
                WHERE tr.source_twin_id = $1
                """,
                twin['id']
            )
            
            # Get incoming relationships
            incoming = await conn.fetch(
                """
                SELECT tr.*, rt.twin_name as source_name, rt.twin_id as source_twin_id
                FROM digital_twins.twin_relationships tr
                JOIN digital_twins.twin_registry rt ON tr.source_twin_id = rt.id
                WHERE tr.target_twin_id = $1
                """,
                twin['id']
            )
            
            return {
                "outgoing": [dict(rel) for rel in outgoing],
                "incoming": [dict(rel) for rel in incoming]
            }
            
    except Exception as e:
        logger.error(f"Error getting relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/instances")
async def create_instance(
    twin_id: str,
    instance_data: Dict[str, Any],
    db_pool=Depends(get_db_pool)
):
    """Create a new instance for a digital twin"""
    try:
        async with db_pool.acquire() as conn:
            # Get twin ID
            twin = await conn.fetchrow(
                "SELECT id FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not twin:
                raise HTTPException(status_code=404, detail="Digital twin not found")
            
            # Create instance
            await conn.execute(
                """
                INSERT INTO digital_twins.twin_instances 
                (twin_id, instance_data, status)
                VALUES ($1, $2, 'active')
                """,
                twin['id'],
                json.dumps(instance_data)
            )
            
            return {"message": "Instance created successfully"}
            
    except Exception as e:
        logger.error(f"Error creating instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/instances/{twin_id}")
async def get_instances(twin_id: str, limit: int = 50, db_pool=Depends(get_db_pool)):
    """Get instances for a digital twin"""
    try:
        async with db_pool.acquire() as conn:
            # Get twin ID
            twin = await conn.fetchrow(
                "SELECT id FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not twin:
                raise HTTPException(status_code=404, detail="Digital twin not found")
            
            # Get instances
            instances = await conn.fetch(
                """
                SELECT * FROM digital_twins.twin_instances 
                WHERE twin_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                twin['id'],
                limit
            )
            
            return [dict(instance) for instance in instances]
            
    except Exception as e:
        logger.error(f"Error getting instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def sync_twin_with_aas(twin_id: str, sync_type: str, db_pool):
    """Synchronize digital twin with AAS system"""
    try:
        async with db_pool.acquire() as conn:
            # Get twin information
            twin = await conn.fetchrow(
                "SELECT * FROM digital_twins.twin_registry WHERE twin_id = $1",
                twin_id
            )
            
            if not twin:
                logger.error(f"Twin not found for sync: {twin_id}")
                return
            
            # Update sync status
            await conn.execute(
                """
                UPDATE digital_twins.twin_registry 
                SET sync_status = 'syncing', last_sync_at = $1 
                WHERE twin_id = $2
                """,
                datetime.utcnow(),
                twin_id
            )
        
        # Perform sync based on type
        if sync_type == "full":
            await perform_full_sync(twin, db_pool)
        elif sync_type == "incremental":
            await perform_incremental_sync(twin, db_pool)
        elif sync_type == "metadata":
            await perform_metadata_sync(twin, db_pool)
        
        # Update sync status to completed
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE digital_twins.twin_registry 
                SET sync_status = 'completed', last_sync_at = $1 
                WHERE twin_id = $2
                """,
                datetime.utcnow(),
                twin_id
            )
        
        logger.info(f"Sync completed for twin: {twin_id}")
        
    except Exception as e:
        logger.error(f"Error during sync for twin {twin_id}: {e}")
        
        # Update sync status to failed
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE digital_twins.twin_registry 
                SET sync_status = 'failed', last_sync_at = $1 
                WHERE twin_id = $2
                """,
                datetime.utcnow(),
                twin_id
            )

async def perform_full_sync(twin, db_pool):
    """Perform full synchronization with AAS"""
    try:
        # Fetch AAS data
        async with httpx.AsyncClient() as client:
            if twin['aas_id']:
                response = await client.get(f"{AAS_ENDPOINT}/api/aas/{twin['aas_id']}")
                if response.status_code == 200:
                    aas_data = response.json()
                    
                    # Update twin with AAS data
                    async with db_pool.acquire() as conn:
                        await conn.execute(
                            """
                            UPDATE digital_twins.twin_registry 
                            SET metadata = $1, updated_at = $2 
                            WHERE id = $3
                            """,
                            json.dumps(aas_data),
                            datetime.utcnow(),
                            twin['id']
                        )
        
        # Create sync instance
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO digital_twins.twin_instances 
                (twin_id, instance_data, status)
                VALUES ($1, $2, 'active')
                """,
                twin['id'],
                json.dumps({"sync_type": "full", "timestamp": datetime.utcnow().isoformat()})
            )
        
    except Exception as e:
        logger.error(f"Error in full sync: {e}")
        raise

async def perform_incremental_sync(twin, db_pool):
    """Perform incremental synchronization with AAS"""
    try:
        # Get last sync timestamp
        async with db_pool.acquire() as conn:
            last_sync = await conn.fetchrow(
                """
                SELECT last_sync_at FROM digital_twins.twin_registry 
                WHERE id = $1
                """,
                twin['id']
            )
        
        # Fetch incremental AAS data
        if last_sync and last_sync['last_sync_at']:
            async with httpx.AsyncClient() as client:
                if twin['aas_id']:
                    response = await client.get(
                        f"{AAS_ENDPOINT}/api/aas/{twin['aas_id']}/changes",
                        params={"since": last_sync['last_sync_at'].isoformat()}
                    )
                    if response.status_code == 200:
                        changes = response.json()
                        
                        # Apply changes
                        async with db_pool.acquire() as conn:
                            await conn.execute(
                                """
                                UPDATE digital_twins.twin_registry 
                                SET metadata = metadata || $1, updated_at = $2 
                                WHERE id = $3
                                """,
                                json.dumps(changes),
                                datetime.utcnow(),
                                twin['id']
                            )
        
        # Create sync instance
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO digital_twins.twin_instances 
                (twin_id, instance_data, status)
                VALUES ($1, $2, 'active')
                """,
                twin['id'],
                json.dumps({"sync_type": "incremental", "timestamp": datetime.utcnow().isoformat()})
            )
        
    except Exception as e:
        logger.error(f"Error in incremental sync: {e}")
        raise

async def perform_metadata_sync(twin, db_pool):
    """Perform metadata-only synchronization with AAS"""
    try:
        # Fetch only metadata from AAS
        async with httpx.AsyncClient() as client:
            if twin['aas_id']:
                response = await client.get(f"{AAS_ENDPOINT}/api/aas/{twin['aas_id']}/metadata")
                if response.status_code == 200:
                    metadata = response.json()
                    
                    # Update twin metadata
                    async with db_pool.acquire() as conn:
                        await conn.execute(
                            """
                            UPDATE digital_twins.twin_registry 
                            SET metadata = metadata || $1, updated_at = $2 
                            WHERE id = $3
                            """,
                            json.dumps(metadata),
                            datetime.utcnow(),
                            twin['id']
                        )
        
        # Create sync instance
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO digital_twins.twin_instances 
                (twin_id, instance_data, status)
                VALUES ($1, $2, 'active')
                """,
                twin['id'],
                json.dumps({"sync_type": "metadata", "timestamp": datetime.utcnow().isoformat()})
            )
        
    except Exception as e:
        logger.error(f"Error in metadata sync: {e}")
        raise

# Statistics and monitoring endpoints
@app.get("/statistics")
async def get_statistics(db_pool=Depends(get_db_pool)):
    """Get registry statistics"""
    try:
        async with db_pool.acquire() as conn:
            # Get twin counts by type
            type_counts = await conn.fetch(
                """
                SELECT twin_type, COUNT(*) as count 
                FROM digital_twins.twin_registry 
                GROUP BY twin_type
                """
            )
            
            # Get status counts
            status_counts = await conn.fetch(
                """
                SELECT status, COUNT(*) as count 
                FROM digital_twins.twin_registry 
                GROUP BY status
                """
            )
            
            # Get sync status counts
            sync_counts = await conn.fetch(
                """
                SELECT sync_status, COUNT(*) as count 
                FROM digital_twins.twin_registry 
                GROUP BY sync_status
                """
            )
            
            # Get total counts
            total_twins = await conn.fetchval("SELECT COUNT(*) FROM digital_twins.twin_registry")
            total_instances = await conn.fetchval("SELECT COUNT(*) FROM digital_twins.twin_instances")
            total_relationships = await conn.fetchval("SELECT COUNT(*) FROM digital_twins.twin_relationships")
            
            return {
                "total_twins": total_twins,
                "total_instances": total_instances,
                "total_relationships": total_relationships,
                "by_type": [dict(count) for count in type_counts],
                "by_status": [dict(count) for count in status_counts],
                "by_sync_status": [dict(count) for count in sync_counts]
            }
            
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 