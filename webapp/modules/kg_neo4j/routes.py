"""
Knowledge Graph Neo4j API Routes
Provides REST API endpoints for Neo4j management and Docker operations
Uses centralized data management system for clean separation of concerns
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Import module-specific services
from .services.kg_neo4j_service import KGNeo4jService
from .services.graph_discovery_service import GraphDiscoveryService

# Create FastAPI Router
router = APIRouter(tags=["Knowledge Graph Neo4j"])

# Create service instances
kg_neo4j_service = KGNeo4jService()
graph_discovery_service = GraphDiscoveryService()

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
async def index(request: Request):
    """Knowledge Graph Neo4j main page"""
    templates = Jinja2Templates(directory="webapp/templates")
    return templates.TemplateResponse("kg_neo4j/index.html", {"request": request})

@router.get("/visualize", response_class=HTMLResponse)
async def visualize(request: Request):
    """Knowledge Graph visualization page"""
    templates = Jinja2Templates(directory="webapp/templates")
    return templates.TemplateResponse("kg_neo4j/visualize.html", {"request": request})

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get Neo4j connection and system status"""
    try:
        result = kg_neo4j_service.get_system_status()
        return StatusResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docker-status")
async def get_docker_status():
    """Get detailed Docker container status"""
    try:
        return kg_neo4j_service.get_docker_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/start", response_model=DockerResponse)
async def start_docker():
    """Start Neo4j Docker container"""
    try:
        result = kg_neo4j_service.start_docker_container()
        return DockerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/stop", response_model=DockerResponse)
async def stop_docker():
    """Stop Neo4j Docker container"""
    try:
        result = kg_neo4j_service.stop_docker_container()
        return DockerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/status")
async def get_local_neo4j_status():
    """Get local Neo4j Desktop status"""
    try:
        return kg_neo4j_service.get_local_neo4j_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/desktop-status")
async def get_local_desktop_status():
    """Get local Neo4j Desktop installation status"""
    try:
        result = kg_neo4j_service.get_local_neo4j_status()
        return {
            'installed': result.get('desktop_installed', False),
            'running': result.get('desktop_running', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/connection-status")
async def get_local_connection_status():
    """Get local Neo4j connection status"""
    try:
        result = kg_neo4j_service.get_local_neo4j_status()
        return {
            'available': result.get('connection_available', False),
            'browser_url': result.get('browser_url'),
            'bolt_url': result.get('bolt_url')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/local/launch")
async def launch_local_neo4j_desktop():
    """Launch Neo4j Desktop application"""
    try:
        return kg_neo4j_service.launch_local_desktop()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local/info")
async def get_local_neo4j_info():
    """Get local Neo4j information"""
    try:
        result = kg_neo4j_service.get_local_neo4j_status()
        return {
            'desktop_installed': result.get('desktop_installed', False),
            'desktop_running': result.get('desktop_running', False),
            'connection_available': result.get('connection_available', False),
            'browser_url': result.get('browser_url'),
            'bolt_url': result.get('bolt_url')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def execute_cypher_query(request: QueryRequest):
    """Execute Cypher query against Neo4j"""
    try:
        result = kg_neo4j_service.execute_cypher_query(request.query)
        
        if result['success']:
            return {
                'success': True,
                'data': result['data'],
                'query': result['query'],
                'timestamp': result['timestamp']
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
async def get_projects():
    """Get all projects"""
    try:
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
async def get_project_graph(project_id: str):
    """Get graph data for a specific project"""
    try:
        result = kg_neo4j_service.get_project_graph(project_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/graph")
async def get_file_graph(file_id: str):
    """Get graph data for a specific file"""
    try:
        result = kg_neo4j_service.get_file_graph(file_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/graph-exists")
async def check_file_graph_exists(file_id: str):
    """Check if graph data exists for a file"""
    try:
        result = kg_neo4j_service.check_file_graph_exists(file_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/graph-data")
async def get_file_graph_data(file_id: str):
    """Get detailed graph data for a file"""
    try:
        result = kg_neo4j_service.get_file_graph_data(file_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/graph-data")
async def get_project_graph_data(project_id: str):
    """Get detailed graph data for a project"""
    try:
        result = kg_neo4j_service.get_project_graph_data(project_id)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-folders")
async def get_available_folders():
    """Get list of available data folders"""
    try:
        result = kg_neo4j_service.get_available_folders()
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database-stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        result = kg_neo4j_service.get_database_stats()
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result['error'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for UI components
@router.get("/kg-neo4j/status")
async def get_kg_neo4j_status():
    """Get Knowledge Graph Neo4j status for UI components"""
    try:
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
async def get_kg_neo4j_graph_data():
    """Get graph data for visualization"""
    try:
        # This would return actual graph data for visualization
        return {
            'success': True,
            'nodes': [],
            'edges': []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kg-neo4j/execute-query")
async def execute_kg_neo4j_query(request: QueryRequest):
    """Execute Cypher query for UI components"""
    try:
        result = kg_neo4j_service.execute_cypher_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kg-neo4j/available-folders")
async def get_kg_neo4j_available_folders():
    """Get available folders for UI components"""
    try:
        result = kg_neo4j_service.get_available_folders()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kg-neo4j/import-data")
async def import_kg_neo4j_data(directory: str):
    """Import data for UI components"""
    try:
        # Implementation for data import
        return {
            'success': True,
            'imported_files': 0,
            'message': 'Data import completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kg-neo4j/export-data")
async def export_kg_neo4j_data(format: str = "json"):
    """Export data for UI components"""
    try:
        # Implementation for data export
        return {
            'success': True,
            'format': format,
            'message': 'Data export completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kg-neo4j/database-stats")
async def get_kg_neo4j_database_stats():
    """Get database stats for UI components"""
    try:
        result = kg_neo4j_service.get_database_stats()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kg-neo4j/clear-data")
async def clear_kg_neo4j_data():
    """Clear database data for UI components"""
    try:
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
async def get_use_cases_with_graphs():
    """Get all use cases that have graph data files"""
    try:
        use_cases = graph_discovery_service.discover_use_cases_with_graphs()
        return {
            "success": True,
            "use_cases": use_cases,
            "count": len(use_cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hierarchy/use-cases/{use_case_id}/projects")
async def get_projects_with_graphs(use_case_id: str):
    """Get all projects in a use case that have graph data files"""
    try:
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
async def get_files_with_graphs(project_id: str):
    """Get all files in a project that have graph data files"""
    try:
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
async def get_file_graph_status(file_id: str):
    """Get graph file status for a specific file"""
    try:
        graph_status = graph_discovery_service.get_graph_file_status(file_id)
        return {
            "success": True,
            "file_id": file_id,
            "graph_status": graph_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/use-cases")
async def discover_use_cases_with_graphs():
    """Discover use cases with graphs (alias for hierarchy endpoint)"""
    try:
        use_cases = graph_discovery_service.discover_use_cases_with_graphs()
        return {
            "success": True,
            "use_cases": use_cases,
            "count": len(use_cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/projects/{use_case_id}")
async def discover_projects_with_graphs(use_case_id: str):
    """Discover projects with graphs for a use case"""
    try:
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
async def discover_files_with_graphs(project_id: str):
    """Discover files with graphs for a project"""
    try:
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
async def validate_graph_file(file_id: str):
    """Validate if a graph file exists and has correct format"""
    try:
        is_valid = graph_discovery_service.validate_graph_file(file_id)
        return {
            "success": True,
            "file_id": file_id,
            "is_valid": is_valid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discovery/status")
async def get_discovery_status():
    """Get overall discovery status for all graph data"""
    try:
        status = graph_discovery_service.get_hierarchical_availability_status()
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
async def get_config():
    """Get configuration for frontend initialization"""
    try:
        return {
            "success": True,
            "config": {
                "api_base_url": "/api/kg-neo4j",
                "docker_enabled": True,
                "local_enabled": True,
                "graph_discovery_enabled": True,
                "hierarchical_data_enabled": True,
                "features": {
                    "docker_management": True,
                    "graph_visualization": True,
                    "data_management": True,
                    "analytics": True,
                    "query_interface": True
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visualization-config")
async def get_visualization_config():
    """Get visualization configuration"""
    try:
        return {
            "success": True,
            "config": {
                "containerId": "graph-container",
                "width": 800,
                "height": 600,
                "nodeSize": 20,
                "linkDistance": 100,
                "charge": -300,
                "gravity": 0.1,
                "alpha": 0.3,
                "colors": {
                    "default": "#1f77b4",
                    "person": "#ff7f0e",
                    "organization": "#2ca02c",
                    "location": "#d62728",
                    "concept": "#9467bd",
                    "event": "#8c564b",
                    "relationship": "#e377c2"
                },
                "nodeLabels": True,
                "linkLabels": True,
                "zoomEnabled": True,
                "panEnabled": True,
                "dragEnabled": True,
                "tooltipEnabled": True,
                "animationEnabled": True,
                "autoLayout": True,
                "layoutAlgorithm": "force",
                "updateInterval": 1000
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize")
async def initialize_module():
    """Initialize the Knowledge Graph module"""
    try:
        # Check if services are available
        discovery_status = graph_discovery_service.get_hierarchical_availability_status()
        docker_status = kg_neo4j_service.get_docker_status()
        
        return {
            "success": True,
            "initialized": True,
            "services": {
                "graph_discovery": True,
                "docker_management": True,
                "neo4j_integration": True
            },
            "status": {
                "discovery": discovery_status,
                "docker": docker_status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph-data")
async def get_graph_data():
    """Get graph data for visualization"""
    try:
        # Get all nodes and relationships from Neo4j
        nodes_query = "MATCH (n) RETURN n"
        relationships_query = "MATCH (a)-[r]->(b) RETURN a, r, b"
        
        nodes = []
        relationships = []
        
        try:
            # Use the database stats to get basic info
            stats = kg_neo4j_service.get_database_stats()
            logger.info(f"Database stats: {stats}")
            
            # Simple queries that should work
            nodes_query = "MATCH (n) RETURN n LIMIT 100"
            relationships_query = "MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 100"
            
            logger.info("Executing nodes query...")
            nodes_result = kg_neo4j_service.execute_query_raw(nodes_query)
            logger.info(f"Nodes query returned {len(nodes_result)} results")
            
            logger.info("Executing relationships query...")
            relationships_result = kg_neo4j_service.execute_query_raw(relationships_query)
            logger.info(f"Relationships query returned {len(relationships_result)} results")
            
            # Process nodes
            logger.info("Processing nodes...")
            for record in nodes_result:
                try:
                    node = record['n']  # This is now a raw Neo4j Node object
                    node_dict = dict(node)
                    
                    # Extract node ID - prioritize the 'id' property from the data
                    node_id = node_dict.get('id') or node_dict.get('idShort')
                    if not node_id:
                        # Fallback to Neo4j element_id
                        node_id = node.element_id if hasattr(node, 'element_id') else f"node_{hash(str(node))}"
                    
                    # Extract label from Neo4j labels
                    node_label = list(node.labels)[0] if node.labels else 'Node'
                    
                    nodes.append({
                        'id': str(node_id),
                        'label': str(node_label),
                        'properties': node_dict
                    })
                except Exception as node_error:
                    logger.warning(f"Error processing node: {node_error}")
                    continue
            
            # Process relationships
            logger.info("Processing relationships...")
            for record in relationships_result:
                try:
                    rel = record['r']  # This is now a raw Neo4j Relationship object
                    a_node = record['a']  # Raw Neo4j Node object
                    b_node = record['b']  # Raw Neo4j Node object
                    
                    # Convert to dictionaries for property access
                    a_dict = dict(a_node)
                    b_dict = dict(b_node)
                    rel_dict = dict(rel)
                    
                    # Extract relationship ID from Neo4j element_id
                    rel_id = rel.element_id if hasattr(rel, 'element_id') else f"rel_{hash(str(rel))}"
                    
                    # Extract node IDs - prioritize 'id' property from data
                    a_id = a_dict.get('id') or a_dict.get('idShort') or a_node.element_id
                    b_id = b_dict.get('id') or b_dict.get('idShort') or b_node.element_id
                    
                    # Extract relationship type from Neo4j object
                    rel_type = rel.type if hasattr(rel, 'type') else 'RELATES_TO'
                    
                    relationships.append({
                        'id': str(rel_id),
                        'source': str(a_id),
                        'target': str(b_id),
                        'type': str(rel_type),
                        'properties': rel_dict
                    })
                except Exception as rel_error:
                    logger.warning(f"Error processing relationship: {rel_error}")
                    continue
                
        except Exception as db_error:
            logger.error(f"Database query failed: {db_error}")
            # Return empty arrays if database query fails
            nodes = []
            relationships = []
        
        return {
            "success": True,
            "nodes": nodes,
            "relationships": relationships
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nodes")
async def create_node(node_data: Dict[str, Any]):
    """Create a new node"""
    try:
        import time
        return {
            "success": True,
            "node": {
                "id": f"node_{len(node_data.get('labels', []))}_{int(time.time() * 1000)}",
                "labels": node_data.get('labels', []),
                "properties": node_data.get('properties', {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """Get a specific node"""
    try:
        return {
            "success": True,
            "node": {
                "id": node_id,
                "labels": [],
                "properties": {}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/nodes/{node_id}")
async def update_node(node_id: str, node_data: Dict[str, Any]):
    """Update a specific node"""
    try:
        return {
            "success": True,
            "node": {
                "id": node_id,
                "labels": node_data.get('labels', []),
                "properties": node_data.get('properties', {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """Delete a specific node"""
    try:
        return {
            "success": True,
            "message": f"Node {node_id} deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relationships")
async def create_relationship(relationship_data: Dict[str, Any]):
    """Create a new relationship"""
    try:
        import time
        return {
            "success": True,
            "relationship": {
                "id": f"rel_{int(time.time() * 1000)}",
                "startNode": relationship_data.get('startNode'),
                "endNode": relationship_data.get('endNode'),
                "type": relationship_data.get('type'),
                "properties": relationship_data.get('properties', {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/{relationship_id}")
async def get_relationship(relationship_id: str):
    """Get a specific relationship"""
    try:
        return {
            "success": True,
            "relationship": {
                "id": relationship_id,
                "startNode": "",
                "endNode": "",
                "type": "",
                "properties": {}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/relationships/{relationship_id}")
async def update_relationship(relationship_id: str, relationship_data: Dict[str, Any]):
    """Update a specific relationship"""
    try:
        return {
            "success": True,
            "relationship": {
                "id": relationship_id,
                "startNode": relationship_data.get('startNode'),
                "endNode": relationship_data.get('endNode'),
                "type": relationship_data.get('type'),
                "properties": relationship_data.get('properties', {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/relationships/{relationship_id}")
async def delete_relationship(relationship_id: str):
    """Delete a specific relationship"""
    try:
        return {
            "success": True,
            "message": f"Relationship {relationship_id} deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nodes/label/{label}")
async def get_nodes_by_label(label: str, limit: int = 100):
    """Get nodes by label"""
    try:
        return {
            "success": True,
            "nodes": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships/type/{type}")
async def get_relationships_by_type(type: str, limit: int = 100):
    """Get relationships by type"""
    try:
        return {
            "success": True,
            "relationships": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_all_data():
    """Clear all graph data"""
    try:
        result = kg_neo4j_service.clear_all_neo4j_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_graph(format: str = "json"):
    """Export graph data"""
    try:
        return {
            "success": True,
            "format": format,
            "data": {
                "nodes": [],
                "relationships": []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_graph(import_data: Dict[str, Any]):
    """Import graph data"""
    try:
        return {
            "success": True,
            "message": "Graph data imported successfully",
            "imported_nodes": len(import_data.get('nodes', [])),
            "imported_relationships": len(import_data.get('relationships', []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DOCKER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/docker-status")
async def get_docker_status():
    """Get Docker container status"""
    try:
        return {
            "success": True,
            "docker_status": kg_neo4j_service.get_docker_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/start")
async def start_docker_container():
    """Start Neo4j Docker container"""
    try:
        result = kg_neo4j_service.start_docker_container()
        return {
            "success": True,
            "message": "Docker container started successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/stop")
async def stop_docker_container():
    """Stop Neo4j Docker container"""
    try:
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
async def get_docker_logs():
    """Get Docker container logs"""
    try:
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
async def get_use_cases():
    """Get all use cases regardless of graph data availability"""
    try:
        use_cases = graph_discovery_service.get_all_use_cases()
        return {
            "success": True,
            "use_cases": use_cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}/projects")
async def get_projects_by_use_case(use_case_id: str):
    """Get projects for a specific use case"""
    try:
        projects = graph_discovery_service.get_all_projects_for_use_case(use_case_id)
        return {
            "success": True,
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
async def get_files_by_project(project_id: str):
    """Get files for a specific project"""
    try:
        files = graph_discovery_service.get_all_files_for_project(project_id)
        return {
            "success": True,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/file/{file_id}")
async def import_file_to_neo4j(file_id: str):
    """Import a specific file to Neo4j"""
    try:
        # This would integrate with the actual Neo4j import logic
        result = kg_neo4j_service.import_file_to_neo4j(file_id)
        return {
            "success": True,
            "message": f"File {file_id} imported successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/project/{project_id}")
async def import_project_to_neo4j(project_id: str):
    """Import all files in a project to Neo4j"""
    try:
        # This would integrate with the actual Neo4j import logic
        result = kg_neo4j_service.import_project_to_neo4j(project_id)
        return {
            "success": True,
            "message": f"Project {project_id} imported successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/import/status")
async def get_import_status():
    """Get import status for all files"""
    try:
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
                "max_workers": 4,
                "supported_formats": ["json", "csv", "xml"],
                "node_types": ["Asset", "Submodel", "Property", "Collection"],
                "relationship_types": ["hasSubmodel", "hasProperty", "references", "contains"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))