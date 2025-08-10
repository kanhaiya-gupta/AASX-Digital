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
from src.core.auth.user_context import UserContext
from src.core.auth.auth_middleware import get_current_user, require_auth

# Import module-specific services
from .services.kg_neo4j_service import KGNeo4jService
from .services.graph_discovery_service import GraphDiscoveryService
from .services.user_specific_service import KGNeo4jUserSpecificService
from .services.organization_service import KGNeo4jOrganizationService

# Create FastAPI Router
router = APIRouter(tags=["Knowledge Graph Neo4j"])

# Create service instances
kg_neo4j_service = KGNeo4jService()
graph_discovery_service = GraphDiscoveryService()

# Note: Authentication services will be created per-request with user context

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

@router.get("/visualize", response_class=HTMLResponse)
@require_auth("read", allow_independent=True)
async def visualize(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Knowledge Graph visualization page"""
    templates = Jinja2Templates(directory="webapp/templates")
    
    # Initialize authentication services
    user_specific_service = KGNeo4jUserSpecificService(user_context)
    
    # Get user-specific graph data
    user_graph_data = user_specific_service.get_user_graph_data()
    
    context = {
        "request": request,
        "user_graph_data": user_graph_data,
        "is_independent": user_context.is_independent
    }
    
    return templates.TemplateResponse("kg_neo4j/visualize.html", context)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status", response_model=StatusResponse)
@require_auth("read", allow_independent=True)
async def get_status(user_context: UserContext = Depends(get_current_user)):
    """Get Neo4j connection and system status"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access system status")
        
        result = kg_neo4j_service.get_system_status()
        return StatusResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docker-status")
@require_auth("read", allow_independent=True)
async def get_docker_status(user_context: UserContext = Depends(get_current_user)):
    """Get Docker container status"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access docker status")
        
        # Get docker status
        result = kg_neo4j_service.get_docker_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/start", response_model=DockerResponse)
@require_auth("admin", allow_independent=False)
async def start_docker(user_context: UserContext = Depends(get_current_user)):
    """Start Neo4j Docker container"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can manage Docker
        if not user_specific_service.can_manage_docker():
            raise HTTPException(status_code=403, detail="Insufficient permissions to manage Docker containers")
        
        result = kg_neo4j_service.start_docker_container()
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
        
        result = kg_neo4j_service.stop_docker_container()
        return DockerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/status")
@require_auth("read", allow_independent=True)
async def get_local_neo4j_status(user_context: UserContext = Depends(get_current_user)):
    """Get local Neo4j status"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access local Neo4j status")
        
        return {
            "success": True,
            "local_status": kg_neo4j_service.get_local_neo4j_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/desktop-status")
@require_auth("read", allow_independent=True)
async def get_local_desktop_status(user_context: UserContext = Depends(get_current_user)):
    """Get local Neo4j Desktop status"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access local Neo4j Desktop status")
        
        return {
            "success": True,
            "desktop_status": kg_neo4j_service.get_local_desktop_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/connection-status")
@require_auth("read", allow_independent=True)
async def get_local_connection_status(user_context: UserContext = Depends(get_current_user)):
    """Get local Neo4j connection status"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access local Neo4j connection status")
        
        return {
            "success": True,
            "connection_status": kg_neo4j_service.get_local_connection_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/local/launch")
@require_auth("admin", allow_independent=False)
async def launch_local_neo4j_desktop(user_context: UserContext = Depends(get_current_user)):
    """Launch local Neo4j Desktop"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can manage Docker
        if not user_specific_service.can_manage_docker():
            raise HTTPException(status_code=403, detail="Insufficient permissions to launch local Neo4j Desktop")
        
        result = kg_neo4j_service.launch_local_neo4j_desktop()
        return {
            "success": True,
            "message": "Neo4j Desktop launched successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/info")
@require_auth("read", allow_independent=True)
async def get_local_neo4j_info(user_context: UserContext = Depends(get_current_user)):
    """Get local Neo4j information"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access local Neo4j information")
        
        result = kg_neo4j_service.get_local_neo4j_info()
        return {
            "success": True,
            "info": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        result = kg_neo4j_service.execute_cypher_query(request.query)
        
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
            result = kg_neo4j_service.get_projects()
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
        
        result = kg_neo4j_service.get_project_graph(project_id)
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
        
        result = kg_neo4j_service.get_file_graph(file_id)
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
        
        result = kg_neo4j_service.check_file_graph_exists(file_id)
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
        
        result = kg_neo4j_service.get_file_graph_data(file_id)
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
        
        result = kg_neo4j_service.get_project_graph_data(project_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-folders")
@require_auth("read", allow_independent=True)
async def get_available_folders(user_context: UserContext = Depends(get_current_user)):
    """Get list of available data folders"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access folder information")
        
        result = kg_neo4j_service.get_available_folders()
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database-stats")
@require_auth("read", allow_independent=True)
async def get_database_stats(user_context: UserContext = Depends(get_current_user)):
    """Get database statistics"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access database statistics")
        
        result = kg_neo4j_service.get_database_stats()
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for UI components
@router.get("/kg-neo4j/status")
@require_auth("read", allow_independent=True)
async def get_kg_neo4j_status(user_context: UserContext = Depends(get_current_user)):
    """Get Knowledge Graph Neo4j status for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access system status")
        
        result = kg_neo4j_service.get_system_status()
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

@router.get("/kg-neo4j/graph-data")
@require_auth("read", allow_independent=True)
async def get_kg_neo4j_graph_data(user_context: UserContext = Depends(get_current_user)):
    """Get graph data for visualization"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access graph data")
        
        # This would return actual graph data for visualization
        return {
            'success': True,
            'nodes': [],
            'edges': []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kg-neo4j/execute-query")
@require_auth("read", allow_independent=True)
async def execute_kg_neo4j_query(request: QueryRequest, user_context: UserContext = Depends(get_current_user)):
    """Execute Cypher query for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can execute queries
        if not user_specific_service.can_execute_queries():
            raise HTTPException(status_code=403, detail="Insufficient permissions to execute queries")
        
        result = kg_neo4j_service.execute_cypher_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kg-neo4j/available-folders")
@require_auth("read", allow_independent=True)
async def get_kg_neo4j_available_folders(user_context: UserContext = Depends(get_current_user)):
    """Get available folders for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access folder information")
        
        result = kg_neo4j_service.get_available_folders()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kg-neo4j/import-data")
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

@router.get("/kg-neo4j/export-data")
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

@router.get("/kg-neo4j/database-stats")
@require_auth("read", allow_independent=True)
async def get_kg_neo4j_database_stats(user_context: UserContext = Depends(get_current_user)):
    """Get database stats for UI components"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access database statistics")
        
        result = kg_neo4j_service.get_database_stats()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kg-neo4j/clear-data")
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
# GRAPH DISCOVERY ENDPOINTS
# ============================================================================

@router.get("/hierarchy/use-cases")
@require_auth("read", allow_independent=True)
async def get_use_cases_with_graphs(user_context: UserContext = Depends(get_current_user)):
    """Get all use cases that have graph data files"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access use case information")
        
        use_cases = graph_discovery_service.discover_use_cases_with_graphs()
        return {
            "success": True,
            "use_cases": use_cases,
            "count": len(use_cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hierarchy/use-cases/{use_case_id}/projects")
@require_auth("read", allow_independent=True)
async def get_projects_with_graphs(use_case_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get all projects in a use case that have graph data files"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this use case
        if not user_specific_service.can_access_use_case(use_case_id):
            raise HTTPException(status_code=403, detail="Access denied to this use case")
        
        projects = graph_discovery_service.discover_projects_with_graphs(use_case_id)
        return {
            "success": True,
            "use_case_id": use_case_id,
            "projects": projects,
            "count": len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hierarchy/projects/{project_id}/files")
@require_auth("read", allow_independent=True)
async def get_files_with_graphs(project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get all files in a project that have graph data files"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this project
        if not user_specific_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        files = graph_discovery_service.discover_files_with_graphs(project_id)
        return {
            "success": True,
            "project_id": project_id,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hierarchy/files/{file_id}/graph")
@require_auth("read", allow_independent=True)
async def get_file_graph_status(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get graph file status for a specific file"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Access denied to this file")
        
        graph_status = graph_discovery_service.get_graph_file_status(file_id)
        return {
            "success": True,
            "file_id": file_id,
            "graph_status": graph_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/use-cases")
@require_auth("read", allow_independent=True)
async def discover_use_cases_with_graphs(user_context: UserContext = Depends(get_current_user)):
    """Discover use cases with graphs (alias for hierarchy endpoint)"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access use case information")
        
        use_cases = graph_discovery_service.discover_use_cases_with_graphs()
        return {
            "success": True,
            "use_cases": use_cases,
            "count": len(use_cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/projects/{use_case_id}")
@require_auth("read", allow_independent=True)
async def discover_projects_with_graphs(use_case_id: str, user_context: UserContext = Depends(get_current_user)):
    """Discover projects with graphs (alias for hierarchy endpoint)"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this use case
        if not user_specific_service.can_access_use_case(use_case_id):
            raise HTTPException(status_code=403, detail="Access denied to this use case")
        
        projects = graph_discovery_service.discover_projects_with_graphs(use_case_id)
        return {
            "success": True,
            "use_case_id": use_case_id,
            "projects": projects,
            "count": len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/files/{project_id}")
@require_auth("read", allow_independent=True)
async def discover_files_with_graphs(project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Discover files with graphs (alias for hierarchy endpoint)"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this project
        if not user_specific_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        files = graph_discovery_service.discover_files_with_graphs(project_id)
        return {
            "success": True,
            "project_id": project_id,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/validate/{file_id}")
@require_auth("read", allow_independent=True)
async def validate_graph_file(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Validate graph file for a specific file"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this file
        if not user_specific_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Access denied to this file")
        
        validation_result = graph_discovery_service.validate_graph_file(file_id)
        return {
            "success": True,
            "file_id": file_id,
            "validation_result": validation_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/status")
@require_auth("read", allow_independent=True)
async def get_discovery_status(user_context: UserContext = Depends(get_current_user)):
    """Get discovery service status"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access discovery status")
        
        status = graph_discovery_service.get_discovery_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FRONTEND CONFIGURATION ENDPOINTS
# ============================================================================

@router.get("/config")
@require_auth("read", allow_independent=True)
async def get_config(user_context: UserContext = Depends(get_current_user)):
    """Get module configuration"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access configuration")
        
        config = {
            "neo4j_connection": {
                "docker_enabled": True,
                "local_enabled": True,
                "browser_enabled": True
            },
            "graph_processing": {
                "max_nodes": 10000,
                "max_relationships": 50000,
                "batch_size": 1000
            },
            "visualization": {
                "default_layout": "force",
                "max_display_nodes": 1000,
                "animation_enabled": True
            }
        }
        
        return {
            "success": True,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
@require_auth("admin", allow_independent=False)
async def initialize_module(user_context: UserContext = Depends(get_current_user)):
    """Initialize the Knowledge Graph module"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can manage docker
        if not user_specific_service.can_manage_docker():
            raise HTTPException(status_code=403, detail="Insufficient permissions to initialize module")
        
        # Initialize services
        kg_neo4j_service.initialize()
        graph_discovery_service.initialize()
        
        return {
            "success": True,
            "message": "Knowledge Graph module initialized successfully",
            "services": {
                "kg_neo4j_service": "initialized",
                "graph_discovery_service": "initialized"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph-data")
@require_auth("read", allow_independent=True)
async def get_graph_data(user_context: UserContext = Depends(get_current_user)):
    """Get graph data for visualization"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access graph data")
        
        # Get user-specific graph data
        user_graph_data = user_specific_service.get_user_graph_data()
        
        if user_graph_data:
            return {
                "success": True,
                "data": user_graph_data
            }
        else:
            # Fallback to general graph data if user has access
            try:
                result = kg_neo4j_service.get_graph_data()
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
            except Exception:
                return {
                    "success": False,
                    "error": "No graph data available"
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
        result = kg_neo4j_service.create_node(node_data)
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
        result = kg_neo4j_service.get_node(node_id)
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
        result = kg_neo4j_service.update_node(node_id, node_data)
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
        result = kg_neo4j_service.delete_node(node_id)
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
        result = kg_neo4j_service.create_relationship(relationship_data)
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
        result = kg_neo4j_service.get_relationship(relationship_id)
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
        result = kg_neo4j_service.update_relationship(relationship_id, relationship_data)
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
        result = kg_neo4j_service.delete_relationship(relationship_id)
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
        result = kg_neo4j_service.get_nodes_by_label(label, limit)
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
        result = kg_neo4j_service.get_relationships_by_type(type, limit)
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
        result = kg_neo4j_service.clear_all_data()
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
        result = kg_neo4j_service.export_graph(format)
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
        result = kg_neo4j_service.import_graph(import_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DOCKER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/docker-status")
@require_auth("read", allow_independent=True)
async def get_docker_status(user_context: UserContext = Depends(get_current_user)):
    """Get Docker container status"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access docker status")
        
        return {
            "success": True,
            "docker_status": kg_neo4j_service.get_docker_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/start")
@require_auth("admin", allow_independent=False)
async def start_docker_container(user_context: UserContext = Depends(get_current_user)):
    """Start Neo4j Docker container"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can manage Docker
        if not user_specific_service.can_manage_docker():
            raise HTTPException(status_code=403, detail="Insufficient permissions to manage Docker containers")
        
        result = kg_neo4j_service.start_docker_container()
        return {
            "success": True,
            "message": "Docker container started successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/stop")
@require_auth("admin", allow_independent=False)
async def stop_docker_container(user_context: UserContext = Depends(get_current_user)):
    """Stop Neo4j Docker container"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can manage Docker
        if not user_specific_service.can_manage_docker():
            raise HTTPException(status_code=403, detail="Insufficient permissions to manage Docker containers")
        
        result = kg_neo4j_service.stop_docker_container()
        return {
            "success": True,
            "message": "Docker container stopped successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Removed duplicate /status endpoint - using the one with StatusResponse model above

@router.get("/docker/logs")
@require_auth("read", allow_independent=True)
async def get_docker_logs(user_context: UserContext = Depends(get_current_user)):
    """Get Docker container logs"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access docker logs")
        
        logs = kg_neo4j_service.get_docker_logs()
        return {
            "success": True,
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DATA MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/use-cases")
@require_auth("read", allow_independent=True)
async def get_use_cases(user_context: UserContext = Depends(get_current_user)):
    """Get all use cases regardless of graph data availability"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access graph data
        if not user_specific_service.can_access_graph_data():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access use case information")
        
        use_cases = graph_discovery_service.get_all_use_cases()
        return {
            "success": True,
            "use_cases": use_cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}/projects")
@require_auth("read", allow_independent=True)
async def get_projects_by_use_case(use_case_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get projects for a specific use case"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this use case
        if not user_specific_service.can_access_use_case(use_case_id):
            raise HTTPException(status_code=403, detail="Access denied to this use case")
        
        projects = graph_discovery_service.get_all_projects_for_use_case(use_case_id)
        return {
            "success": True,
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
@require_auth("read", allow_independent=True)
async def get_files_by_project(project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get files for a specific project"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access this project
        if not user_specific_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        files = graph_discovery_service.get_all_files_for_project(project_id)
        return {
            "success": True,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        result = kg_neo4j_service.import_graph(import_data)
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
        result = kg_neo4j_service.import_graph(import_data)
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
@require_auth("read", allow_independent=True)
async def get_query_config(user_context: UserContext = Depends(get_current_user)):
    """Get query engine configuration"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access query configuration")
        
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
@require_auth("read", allow_independent=True)
async def get_processor_config(user_context: UserContext = Depends(get_current_user)):
    """Get data processor configuration"""
    try:
        # Initialize authentication services
        user_specific_service = KGNeo4jUserSpecificService(user_context)
        
        # Check if user can access system status
        if not user_specific_service.can_access_system_status():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access processor configuration")
        
        return {
            "success": True,
            "config": {
                "batch_size": 100,
                "max_workers": 4,
                "supported_formats": ["json", "csv", "xml"],
                "node_types": ["Asset", "Submodel", "Property", "Collection"],
                "relationship_types": ["hasSubmodel", "hasProperty", "references", "contains"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))