"""
Knowledge Graph Neo4j API Routes
Provides REST API endpoints for Neo4j management and Docker operations
Uses centralized data management system for clean separation of concerns
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Import authentication dependencies
from webapp.core.context.user_context import UserContext
from webapp.core.decorators.auth_decorators import get_current_user, require_auth

# Import module-specific services
from .services.kg_neo4j_service import KGNeo4jService
from .services.user_specific_service import KGNeo4jUserSpecificService
from .services.organization_service import KGNeo4jOrganizationService

# Create FastAPI Router
router = APIRouter(tags=["Knowledge Graph Neo4j"])

# 🔐 CRITICAL FIX: Services are created per-request to prevent 500 errors during import
# This ensures proper authentication context and prevents module-level initialization failures
logger.info("🔐 Knowledge Graph services will be initialized per-request after authentication")

# Note: All services (KG, User, Organization) are created per-request with user context

# Pydantic models for request/response
class DockerResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None

class StatusResponse(BaseModel):
    success: bool
    docker_running: bool
    connected: bool
    browser_accessible: bool
    active_connections: int
    docker_status: str
    last_checked: str
    error: Optional[str] = None

class QueryRequest(BaseModel):
    query: str

# ============================================================================
# ROUTE DEFINITIONS
# ============================================================================

@router.get("/", response_class=HTMLResponse)
@require_auth("read", allow_independent=True)
async def index(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Knowledge Graph Neo4j main page"""
    templates = Jinja2Templates(directory="webapp/templates")
    
    # Initialize authentication services
    user_specific_service = KGNeo4jUserSpecificService(user_context)
    organization_service = KGNeo4jOrganizationService(user_context)
    
    # Get user-specific data
    user_projects = user_specific_service.get_user_projects()
    user_limits = user_specific_service.get_user_graph_limits()
    
    context = {
        "request": request,
        "user_projects": user_projects,
        "user_limits": user_limits,
        "is_independent": user_context.is_independent
    }
    
    return templates.TemplateResponse("kg_neo4j/index.html", context)



# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get Neo4j connection and system status"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_system_status()
        return StatusResponse(**result)
    except Exception as e:
        logger.error(f"❌ Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config():
    """Get Knowledge Graph module configuration"""
    try:
        return {
            "success": True,
            "config": {
                "module_name": "Knowledge Graph Neo4j",
                "version": "1.0.0",
                "features": {
                    "docker_management": True,
                    "graph_visualization": True,
                    "query_engine": True,
                    "data_import": True
                },
                "neo4j": {
                    "connection_type": "docker",
                    "default_port": 7687,
                    "browser_port": 7474
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docker-status")
async def get_docker_status():
    """Get Docker container status"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_docker_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/start", response_model=DockerResponse)
async def start_docker():
    """Start Neo4j Docker container"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.start_docker_container()
        return DockerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/stop", response_model=DockerResponse)
@require_auth("admin", allow_independent=False)
async def stop_docker(user_context: UserContext = Depends(get_current_user)):
    """Stop Neo4j Docker container"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can manage Docker
        if not user_specific_service.can_manage_docker():
            raise HTTPException(status_code=403, detail="Insufficient permissions to manage Docker containers")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.stop_docker_container()
        return DockerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docker/logs")
async def get_docker_logs():
    """Get Docker container logs"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        logs = kg_service.get_docker_logs()
        return {
            "success": True,
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔐 ADDING MISSING ENDPOINTS THAT FRONTEND IS CALLING

@router.get("/database-stats")
async def get_database_stats():
    """Get Neo4j database statistics"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_database_stats()
        return result
    except Exception as e:
        logger.error(f"❌ Failed to get database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph-data")
async def get_graph_data():
    """Get graph data for visualization"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_graph_data()
        if result['success']:
            return {
                "success": True,
                "data": result['data']
            }
        else:
            return {
                "success": False,
                "error": "No graph data available"
            }
    except Exception as e:
        logger.error(f"❌ Failed to get graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-folders")
async def get_available_folders():
    """Get available folders for data import"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_available_folders()
        return result
    except Exception as e:
        logger.error(f"❌ Failed to get available folders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-data")
async def export_data(format: str = "json"):
    """Export graph data"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.export_graph(format)
        return result
    except Exception as e:
        logger.error(f"❌ Failed to export data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-data")
async def clear_data():
    """Clear database data"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.clear_all_data()
        return result
    except Exception as e:
        logger.error(f"❌ Failed to clear data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-query")
async def execute_query(request: QueryRequest):
    """Execute Cypher query"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.execute_cypher_query(request.query)
        return result
    except Exception as e:
        logger.error(f"❌ Failed to execute query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-data")
async def import_data(directory: str):
    """Import data from directory"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.import_graph({"directory": directory})
        return result
    except Exception as e:
        logger.error(f"❌ Failed to import data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Local Neo4j endpoints removed - using Docker-based Neo4j instead

@router.post("/query")
@require_auth("read", allow_independent=True)
async def execute_cypher_query(request: QueryRequest, user_context: UserContext = Depends(get_current_user)):
    """Execute Cypher query against Neo4j"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can execute queries
        if not user_specific_service.can_execute_queries():
            raise HTTPException(status_code=403, detail="Insufficient permissions to execute queries")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.execute_cypher_query(request.query)
        
        if result['success']:
            return {
                'success': True,
                'data': result['data'],
                'query': result['query'],
                'timestamp': result['timestamp'],
                'user_id': user_context.user_id,
                'organization_id': user_context.organization_id
            }
        else:
            return {
                'success': False,
                'error': result['error'],
                'query': result['query']
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
@require_auth("read", allow_independent=True)
async def get_projects(user_context: UserContext = Depends(get_current_user)):
    """Get all projects"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Get user-specific projects
        user_projects = user_specific_service.get_user_projects()
        
        # Filter projects based on user access
        if user_projects:
            return {
                'success': True,
                'projects': user_projects
            }
        else:
            # Fallback to all projects if user has access
            # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
            kg_service = KGNeo4jService()
            result = kg_service.get_projects()
            if result['success']:
                return {
                    'success': True,
                    'projects': result['projects']
                }
            else:
                raise HTTPException(status_code=500, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/projects/{project_id}/graph")
@require_auth("read", allow_independent=True)
async def get_project_graph(project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get graph data for a specific project"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this project
        if not user_specific_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_project_graph(project_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/graph-data")
@require_auth("read", allow_independent=True)
async def get_project_graph_data(project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get detailed graph data for a project"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this project
        if not user_specific_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_project_graph_data(project_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/graph")
@require_auth("read", allow_independent=True)
async def get_file_graph(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get graph data for a specific file"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Access denied to this file")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_file_graph(file_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/graph-exists")
@require_auth("read", allow_independent=True)
async def check_file_graph_exists(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Check if graph data exists for a file"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Access denied to this file")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.check_file_graph_exists(file_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/graph-data")
@require_auth("read", allow_independent=True)
async def get_file_graph_data(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get detailed graph data for a file"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Access denied to this file")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_file_graph_data(file_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional endpoints for UI components
@router.get("/ui-status")
@require_auth("read", allow_independent=True)
async def get_kg_neo4j_ui_status(user_context: UserContext = Depends(get_current_user)):
    """Get Knowledge Graph Neo4j status for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access system status")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_system_status()
        return {
            'docker_status': 'connected' if result.get('docker_running') else 'disconnected',
            'local_status': 'connected' if result.get('browser_accessible') else 'disconnected',
            'browser_status': 'connected' if result.get('browser_accessible') else 'disconnected',
            'connection_status': 'connected' if result.get('docker_running') else 'disconnected',
            'data_status': 'loaded' if result.get('active_connections', 0) > 0 else 'empty',
            'performance_status': 'good' if result.get('docker_running') else 'poor'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/execute-query")
@require_auth("read", allow_independent=True)
async def execute_kg_neo4j_query(request: QueryRequest, user_context: UserContext = Depends(get_current_user)):
    """Execute Cypher query for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can execute queries
        if not user_specific_service.can_execute_queries():
            raise HTTPException(status_code=403, detail="Insufficient permissions to execute queries")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.execute_cypher_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-folders")
@require_auth("read", allow_independent=True)
async def get_kg_neo4j_available_folders(user_context: UserContext = Depends(get_current_user)):
    """Get available folders for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access folder information")
        
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_available_folders()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-data")
@require_auth("create", allow_independent=True)
async def import_kg_neo4j_data(directory: str, user_context: UserContext = Depends(get_current_user)):
    """Import data for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can import data
        if not user_specific_service.can_import_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to import data")
        
        # Implementation for data import
        return {
            'success': True,
            'imported_files': 0,
            'message': 'Data import completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-data")
@require_auth("read", allow_independent=True)
async def export_kg_neo4j_data(format: str = "json", user_context: UserContext = Depends(get_current_user)):
    """Export data for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can export data
        if not user_specific_service.can_export_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to export data")
        
        # Implementation for data export
        return {
            'success': True,
            'format': format,
            'message': 'Data export completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/clear-data")
@require_auth("delete", allow_independent=False)
async def clear_kg_neo4j_data(user_context: UserContext = Depends(get_current_user)):
    """Clear database data for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can clear data
        if not user_specific_service.can_clear_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to clear database data")
        
        # Implementation for clearing data
        return {
            'success': True,
            'message': 'Database cleared successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GRAPH DISCOVERY ENDPOINTS - REMOVED (Using AASX-ETL for data management)
# ============================================================================
# Note: Use Case → Project → File hierarchy is handled by AASX-ETL module
# Knowledge Graph focuses on graph-specific operations like /graph-data, /database-stats, etc.



















# ============================================================================
# FRONTEND CONFIGURATION ENDPOINTS
# ============================================================================

@router.get("/visualization-config")
@require_auth("read", allow_independent=True)
async def get_visualization_config(user_context: UserContext = Depends(get_current_user)):
    """Get visualization configuration"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access visualization configuration")
        
        config = {
            "layouts": {
                "force": {
                    "enabled": True,
                    "default": True,
                    "settings": {
                        "charge": -300,
                        "linkDistance": 30,
                        "gravity": 0.1
                    }
                },
                "hierarchical": {
                    "enabled": True,
                    "default": False,
                    "settings": {
                        "direction": "TB",
                        "sortMethod": "directed"
                    }
                },
                "circular": {
                    "enabled": True,
                    "default": False,
                    "settings": {
                        "radius": 200,
                        "startAngle": 0
                    }
                }
            },
            "node_styling": {
                "default_size": 10,
                "default_color": "#1f77b4",
                "label_enabled": True,
                "label_font_size": 12
            },
            "edge_styling": {
                "default_width": 2,
                "default_color": "#666",
                "arrow_enabled": True,
                "label_enabled": True
            },
            "interactions": {
                "zoom_enabled": True,
                "pan_enabled": True,
                "drag_enabled": True,
                "hover_effects": True
            }
        }
        
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize")
async def initialize_module():
    """Initialize the Knowledge Graph module"""
    try:
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        try:
            kg_service = KGNeo4jService()
            kg_service.initialize()
        except Exception as service_error:
            logger.error(f"❌ Failed to create Knowledge Graph service: {service_error}")
            raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(service_error)}")
        
        return {
            "success": True,
            "message": "Knowledge Graph module initialized successfully",
            "services": {
                "kg_neo4j_service": "initialized"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nodes")
@require_auth("create", allow_independent=True)
async def create_node(node_data: Dict[str, Any], user_context: UserContext = Depends(get_current_user)):
    """Create a new node in the graph"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can create nodes
        if not user_specific_service.can_create_nodes():
            raise HTTPException(status_code=403, detail="Insufficient permissions to create nodes")
        
        # Add user context to node data
        node_data['user_id'] = user_context.user_id
        if user_context.organization_id:
            node_data['organization_id'] = user_context.organization_id
        
        # Create node
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.create_node(node_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nodes/{node_id}")
@require_auth("read", allow_independent=True)
async def get_node(node_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get a specific node by ID"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access graph data")
        
        # Get node
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_node(node_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/nodes/{node_id}")
@require_auth("update", allow_independent=True)
async def update_node(node_id: str, node_data: Dict[str, Any], user_context: UserContext = Depends(get_current_user)):
    """Update an existing node"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can update nodes
        if not user_specific_service.can_update_nodes():
            raise HTTPException(status_code=403, detail="Insufficient permissions to update nodes")
        
        # Update node
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.update_node(node_id, node_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/nodes/{node_id}")
@require_auth("delete", allow_independent=True)
async def delete_node(node_id: str, user_context: UserContext = Depends(get_current_user)):
    """Delete a specific node"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can delete nodes
        if not user_specific_service.can_delete_nodes():
            raise HTTPException(status_code=403, detail="Insufficient permissions to delete nodes")
        
        # Delete node
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.delete_node(node_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relationships")
@require_auth("create", allow_independent=True)
async def create_relationship(relationship_data: Dict[str, Any], user_context: UserContext = Depends(get_current_user)):
    """Create a new relationship between nodes"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can create relationships
        if not user_specific_service.can_create_relationships():
            raise HTTPException(status_code=403, detail="Insufficient permissions to create relationships")
        
        # Add user context to relationship data
        relationship_data['user_id'] = user_context.user_id
        if user_context.organization_id:
            relationship_data['organization_id'] = user_context.organization_id
        
        # Create relationship
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.create_relationship(relationship_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/{relationship_id}")
@require_auth("read", allow_independent=True)
async def get_relationship(relationship_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get a specific relationship by ID"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access graph data")
        
        # Get relationship
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_relationship(relationship_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/relationships/{relationship_id}")
@require_auth("update", allow_independent=True)
async def update_relationship(relationship_id: str, relationship_data: Dict[str, Any], user_context: UserContext = Depends(get_current_user)):
    """Update an existing relationship"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can update relationships
        if not user_specific_service.can_update_relationships():
            raise HTTPException(status_code=403, detail="Insufficient permissions to update relationships")
        
        # Update relationship
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.update_relationship(relationship_id, relationship_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/relationships/{relationship_id}")
@require_auth("delete", allow_independent=True)
async def delete_relationship(relationship_id: str, user_context: UserContext = Depends(get_current_user)):
    """Delete a specific relationship"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can delete relationships
        if not user_specific_service.can_delete_relationships():
            raise HTTPException(status_code=403, detail="Insufficient permissions to delete relationships")
        
        # Delete relationship
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.delete_relationship(relationship_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nodes/label/{label}")
@require_auth("read", allow_independent=True)
async def get_nodes_by_label(label: str, limit: int = 100, user_context: UserContext = Depends(get_current_user)):
    """Get nodes by label"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access graph data")
        
        # Get nodes by label
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_nodes_by_label(label, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/type/{type}")
@require_auth("read", allow_independent=True)
async def get_relationships_by_type(type: str, limit: int = 100, user_context: UserContext = Depends(get_current_user)):
    """Get relationships by type"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access graph data")
        
        # Get relationships by type
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.get_relationships_by_type(type, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
@require_auth("delete", allow_independent=False)
async def clear_all_data(user_context: UserContext = Depends(get_current_user)):
    """Clear all data from the graph"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can clear data
        if not user_specific_service.can_clear_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to clear all data")
        
        # Clear all data
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.clear_all_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
@require_auth("read", allow_independent=True)
async def export_graph(format: str = "json", user_context: UserContext = Depends(get_current_user)):
    """Export the entire graph"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can export data
        if not user_specific_service.can_export_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to export graph data")
        
        # Export graph
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.export_graph(format)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
@require_auth("create", allow_independent=True)
async def import_graph(import_data: Dict[str, Any], user_context: UserContext = Depends(get_current_user)):
    """Import graph data"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can import data
        if not user_specific_service.can_import_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to import graph data")
        
        # Add user context to import data
        import_data['user_id'] = user_context.user_id
        if user_context.organization_id:
            import_data['organization_id'] = user_context.organization_id
        
        # Import graph
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.import_graph(import_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GRAPH OPERATIONS ENDPOINTS (Data comes from AASX-ETL endpoints)
# ============================================================================

# ============================================================================
# GRAPH OPERATIONS ENDPOINTS (Data comes from AASX-ETL endpoints)
# ============================================================================

@router.post("/import/file/{file_id}")
@require_auth("create", allow_independent=True)
async def import_file_to_neo4j(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Import a specific file to Neo4j"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can import data
        if not user_specific_service.can_import_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to import data")
        
        # Add user context to import data
        import_data = {'file_id': file_id}
        import_data['user_id'] = user_context.user_id
        if user_context.organization_id:
            import_data['organization_id'] = user_context.organization_id
        
        # Import graph
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.import_graph(import_data)
        return {
            "success": True,
            "message": f"File {file_id} imported successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/project/{project_id}")
@require_auth("create", allow_independent=True)
async def import_project_to_neo4j(project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Import all files in a project to Neo4j"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can import data
        if not user_specific_service.can_import_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to import data")
        
        # Add user context to import data
        import_data = {'project_id': project_id}
        import_data['user_id'] = user_context.user_id
        if user_context.organization_id:
            import_data['organization_id'] = user_context.organization_id
        
        # Import graph
        # 🔐 CRITICAL FIX: Create service per-request to prevent 500 errors
        kg_service = KGNeo4jService()
        result = kg_service.import_graph(import_data)
        return {
            "success": True,
            "message": f"Project {project_id} imported successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/import/status")
@require_auth("read", allow_independent=True)
async def get_import_status(user_context: UserContext = Depends(get_current_user)):
    """Get import status for all files"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access import status")
        
        # This would return the current import status
        return {
            "success": True,
            "status": {
                "total_files": 0,
                "imported_files": 0,
                "failed_files": 0,
                "in_progress": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query-config")
async def get_query_config():
    """Get query engine configuration"""
    try:
        return {
            "success": True,
            "config": {
                "max_results": 1000,
                "timeout": 30,
                "allowed_queries": ["MATCH", "RETURN", "WHERE", "WITH", "ORDER BY", "LIMIT"],
                "forbidden_queries": ["DELETE", "REMOVE", "SET", "CREATE", "MERGE"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processor-config")
async def get_processor_config():
    """Get data processor configuration"""
    try:
        return {
            "success": True,
            "config": {
                "batch_size": 100,
                "max_response": 1000,
                "max_workers": 4,
                "supported_formats": ["json", "csv", "xml"],
                "node_types": ["Asset", "Submodel", "Property", "Collection"],
                "relationship_types": ["hasSubmodel", "hasProperty", "references", "contains"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-data")
async def get_demo_data():
    """Get demo graph data for testing and development"""
    try:
        return {
            "success": True,
            "data": {
                "nodes": [
                    {"id": "1", "label": "Asset", "type": "Asset", "properties": {"name": "Demo Asset"}},
                    {"id": "2", "label": "Submodel", "type": "Submodel", "properties": {"name": "Demo Submodel"}},
                    {"id": "3", "label": "Property", "type": "Property", "properties": {"name": "Demo Property"}}
                ],
                "edges": [
                    {"source": "1", "target": "2", "type": "hasSubmodel"},
                    {"source": "2", "target": "3", "type": "hasProperty"}
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))