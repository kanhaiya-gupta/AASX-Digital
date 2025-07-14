"""
Neo4j Management Hub API Routes
Provides REST API endpoints for Neo4j management and Docker operations
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import json
import subprocess
import time
from pathlib import Path
import logging
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI Router
router = APIRouter(tags=["Neo4j Management"])

# Pydantic models for request/response
class DockerResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None

class StatusResponse(BaseModel):
    success: bool
    docker_running: bool
    browser_accessible: bool
    active_connections: int
    docker_status: str
    last_checked: str
    error: Optional[str] = None

# ============================================================================
# ROUTE DEFINITIONS
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Neo4j Management Hub main page"""
    templates = Jinja2Templates(directory="webapp/templates")
    return templates.TemplateResponse("kg_neo4j/index.html", {"request": request})

@router.get("/visualize", response_class=HTMLResponse)
async def visualize(request: Request):
    """Neo4j Graph Visualization page"""
    templates = Jinja2Templates(directory="webapp/templates")
    return templates.TemplateResponse("kg_neo4j/visualize.html", {"request": request})

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get Neo4j connection and system status"""
    try:
        # Check if Neo4j is running via Docker
        docker_status = check_docker_status()
        
        # Check if Neo4j Browser is accessible
        browser_accessible = check_browser_accessibility()
        
        # Check active connections (simplified)
        active_connections = get_active_connections()
        
        status_data = StatusResponse(
            success=docker_status.get('running', False),
            docker_running=docker_status.get('running', False),
            browser_accessible=browser_accessible,
            active_connections=active_connections,
            docker_status=docker_status.get('status', 'Unknown'),
            last_checked=time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/docker-status")
async def get_docker_status():
    """Get detailed Docker container status"""
    try:
        status = check_docker_status()
        return {
            'success': True,
            'status': status.get('status', 'Unknown'),
            'running': status.get('running', False),
            'container_id': status.get('container_id', ''),
            'details': status
        }
    except Exception as e:
        logger.error(f"Error getting Docker status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/docker/start", response_model=DockerResponse)
async def start_docker():
    """Start Neo4j Docker container"""
    try:
        result = start_neo4j_docker()
        return DockerResponse(
            success=result.get('success', False),
            message=result.get('message', ''),
            error=result.get('error', '')
        )
    except Exception as e:
        logger.error(f"Error starting Docker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/docker/stop", response_model=DockerResponse)
async def stop_docker():
    """Stop Neo4j Docker container"""
    try:
        result = stop_neo4j_docker()
        return DockerResponse(
            success=result.get('success', False),
            message=result.get('message', ''),
            error=result.get('error', '')
        )
    except Exception as e:
        logger.error(f"Error stopping Docker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LOCAL NEO4J DESKTOP ENDPOINTS
# ============================================================================

@router.get("/api/local/status")
async def get_local_neo4j_status():
    """Get local Neo4j Desktop status"""
    try:
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        return neo4j_manager.get_local_neo4j_info()
    except Exception as e:
        logger.error(f"Error checking local Neo4j status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/local/desktop-status")
async def get_local_desktop_status():
    """Get local Neo4j Desktop application status"""
    try:
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        return neo4j_manager.check_local_neo4j_desktop()
    except Exception as e:
        logger.error(f"Error checking local desktop status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/local/connection-status")
async def get_local_connection_status():
    """Get local Neo4j connection status"""
    try:
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        return neo4j_manager.check_local_neo4j_connection()
    except Exception as e:
        logger.error(f"Error checking local connection status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/local/launch")
async def launch_local_neo4j_desktop():
    """Launch local Neo4j Desktop application"""
    try:
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        return neo4j_manager.launch_local_neo4j_desktop()
    except Exception as e:
        logger.error(f"Error launching local Neo4j Desktop: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/local/info")
async def get_local_neo4j_info():
    """Get comprehensive local Neo4j Desktop information"""
    try:
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        return neo4j_manager.get_local_neo4j_info()
    except Exception as e:
        logger.error(f"Error getting local Neo4j info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/query")
async def execute_cypher_query(request: Request):
    """Execute Cypher query and return results for visualization"""
    try:
        body = await request.json()
        query = body.get('query', '')
        
        if not query:
            return {
                'success': False,
                'error': 'No query provided'
            }
        
        # Try to connect to Neo4j and execute query
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        
        # Try Docker first, then local
        results = None
        statistics = {
            'total_nodes': 0,
            'total_relationships': 0,
            'asset_nodes': 0,
            'submodel_nodes': 0,
            'property_nodes': 0
        }
        
        try:
            # Try Docker connection
            results = neo4j_manager.execute_query_docker(query)
            if results:
                statistics = calculate_statistics(results)
        except Exception as docker_error:
            logger.warning(f"Docker query failed: {docker_error}")
            
            try:
                # Try local connection
                results = neo4j_manager.execute_query_local(query)
                if results:
                    statistics = calculate_statistics(results)
            except Exception as local_error:
                logger.error(f"Local query failed: {local_error}")
                raise Exception(f"Both Docker and Local connections failed: {docker_error}, {local_error}")
        
        if results is None:
            return {
                'success': False,
                'error': 'No Neo4j connection available'
            }
        
        return {
            'success': True,
            'results': results,
            'statistics': statistics
        }
        
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get("/api/projects")
async def get_projects():
    """Get list of projects from output directory structure"""
    try:
        import os
        import json
        from pathlib import Path
        
        projects = []
        
        # First try to read from output directory structure
        output_dir = Path("output/projects")
        if output_dir.exists():
            for project_dir in output_dir.iterdir():
                if project_dir.is_dir():
                    # Try to find project info in the directory
                    project_info_file = project_dir / "project_info.json"
                    if project_info_file.exists():
                        try:
                            with open(project_info_file, 'r') as f:
                                project_info = json.load(f)
                                projects.append(project_info)
                        except:
                            # If project_info.json doesn't exist or is invalid, create basic info
                            projects.append({
                                "id": project_dir.name,
                                "name": f"Project {project_dir.name[:8]}...",
                                "description": f"Project from directory {project_dir.name}",
                                "created_at": "Unknown",
                                "updated_at": "Unknown",
                                "file_count": 0,
                                "total_size": 0
                            })
        
        # If no projects found in output directory, try to import from AASX routes
        if not projects:
            try:
                from webapp.aasx.routes import PROJECTS_DB
                projects = list(PROJECTS_DB.values())
            except ImportError:
                # If import fails, try to read from projects database file
                projects_db_file = Path("output/projects_database.json")
                if projects_db_file.exists():
                    try:
                        with open(projects_db_file, 'r') as f:
                            db_data = json.load(f)
                            projects = list(db_data.get('projects', {}).values())
                    except:
                        pass
        
        return {
            'success': True,
            'projects': projects
        }
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get("/api/projects/{project_id}/files")
async def get_project_files(project_id: str):
    """Get files for a specific project with graph existence information"""
    try:
        import os
        import json
        from pathlib import Path
        
        project_files = []
        
        # First try to import from AASX routes
        try:
            from webapp.aasx.routes import FILES_DB
            project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        except ImportError:
            # If import fails, try to read from project directory structure
            project_dir = Path(f"output/projects/{project_id}")
            if project_dir.exists():
                for file_dir in project_dir.iterdir():
                    if file_dir.is_dir():
                        # Try to find file info
                        file_info_file = file_dir / "file_info.json"
                        if file_info_file.exists():
                            try:
                                with open(file_info_file, 'r') as f:
                                    file_info = json.load(f)
                                    project_files.append(file_info)
                            except:
                                # Create basic file info from directory name
                                project_files.append({
                                    "id": file_dir.name,
                                    "filename": file_dir.name,
                                    "original_filename": file_dir.name,
                                    "project_id": project_id,
                                    "filepath": str(file_dir),
                                    "size": 0,
                                    "upload_date": "Unknown",
                                    "description": f"File from directory {file_dir.name}",
                                    "status": "completed",
                                    "processing_result": {}
                                })
        
        # Add graph existence information for each file
        for file_info in project_files:
            # Check if graph data file exists
            file_output_dir = Path(file_info.get('filepath', ''))
            if not file_output_dir.exists():
                filename = file_info.get('original_filename', file_info.get('filename', file_info['id']))
                file_output_dir = Path(f"output/projects/{project_id}/{filename}")
            
            graph_data_file = file_output_dir / "aasx_data_graph.json"
            file_info['graph_exists'] = graph_data_file.exists()
            
            if file_info['graph_exists']:
                try:
                    with open(graph_data_file, 'r') as f:
                        graph_data = json.load(f)
                    file_info['node_count'] = len(graph_data.get('nodes', []))
                except:
                    file_info['node_count'] = 0
            else:
                file_info['node_count'] = 0
        
        return {
            'success': True,
            'files': project_files
        }
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get("/api/projects/{project_id}/graph")
async def get_project_graph(project_id: str):
    """Get graph data for a specific project"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to get project info from AASX routes first
        project = None
        project_files = []
        
        try:
            from webapp.aasx.routes import PROJECTS_DB, FILES_DB
            
            if project_id in PROJECTS_DB:
                project = PROJECTS_DB[project_id]
                project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        except ImportError:
            # If import fails, try to get project info from directory structure
            project_dir = Path(f"output/projects/{project_id}")
            if project_dir.exists():
                project_info_file = project_dir / "project_info.json"
                if project_info_file.exists():
                    try:
                        with open(project_info_file, 'r') as f:
                            project = json.load(f)
                    except:
                        pass
                
                # Get files from directory structure
                for file_dir in project_dir.iterdir():
                    if file_dir.is_dir():
                        file_info_file = file_dir / "file_info.json"
                        if file_info_file.exists():
                            try:
                                with open(file_info_file, 'r') as f:
                                    file_info = json.load(f)
                                    project_files.append(file_info)
                            except:
                                project_files.append({
                                    "id": file_dir.name,
                                    "filename": file_dir.name,
                                    "original_filename": file_dir.name,
                                    "project_id": project_id,
                                    "filepath": str(file_dir),
                                    "size": 0,
                                    "upload_date": "Unknown",
                                    "description": f"File from directory {file_dir.name}",
                                    "status": "completed",
                                    "processing_result": {}
                                })
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found'
            }
        
        # Build query for project data
        project_name = project.get('name', project_id)
        query = f"""
        MATCH (n) 
        WHERE n.source_file STARTS WITH '{project_name}' 
        RETURN n 
        LIMIT 50
        """
        
        # Execute query
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        
        results = None
        try:
            results = neo4j_manager.execute_query_docker(query)
        except:
            try:
                results = neo4j_manager.execute_query_local(query)
            except Exception as e:
                logger.error(f"Failed to execute project query: {e}")
                return {
                    'success': False,
                    'error': f'Failed to query Neo4j: {str(e)}'
                }
        
        if results is None:
            return {
                'success': False,
                'error': 'No Neo4j connection available'
            }
        
        statistics = calculate_statistics(results)
        
        return {
            'success': True,
            'project': project,
            'files': project_files,
            'results': results,
            'statistics': statistics
        }
        
    except Exception as e:
        logger.error(f"Error getting project graph: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get("/api/files/{file_id}/graph")
async def get_file_graph(file_id: str):
    """Get graph data for a specific file"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to get file info from AASX routes first
        file_info = None
        
        try:
            from webapp.aasx.routes import FILES_DB
            
            if file_id in FILES_DB:
                file_info = FILES_DB[file_id]
        except ImportError:
            # If import fails, try to find file in project directories
            output_dir = Path("output/projects")
            if output_dir.exists():
                for project_dir in output_dir.iterdir():
                    if project_dir.is_dir():
                        file_dir = project_dir / file_id
                        if file_dir.exists() and file_dir.is_dir():
                            file_info_file = file_dir / "file_info.json"
                            if file_info_file.exists():
                                try:
                                    with open(file_info_file, 'r') as f:
                                        file_info = json.load(f)
                                        break
                                except:
                                    pass
                            else:
                                # Create basic file info
                                file_info = {
                                    "id": file_id,
                                    "filename": file_id,
                                    "original_filename": file_id,
                                    "project_id": project_dir.name,
                                    "filepath": str(file_dir),
                                    "size": 0,
                                    "upload_date": "Unknown",
                                    "description": f"File from directory {file_id}",
                                    "status": "completed",
                                    "processing_result": {}
                                }
                                break
        
        if not file_info:
            return {
                'success': False,
                'error': 'File not found'
            }
        
        # Build query for file data
        filename = file_info.get('original_filename', file_id)
        query = f"""
        MATCH (n) 
        WHERE n.source_file = '{filename}' 
        RETURN n 
        LIMIT 50
        """
        
        # Execute query
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        
        results = None
        try:
            results = neo4j_manager.execute_query_docker(query)
        except:
            try:
                results = neo4j_manager.execute_query_local(query)
            except Exception as e:
                logger.error(f"Failed to execute file query: {e}")
                return {
                    'success': False,
                    'error': f'Failed to query Neo4j: {str(e)}'
                }
        
        if results is None:
            return {
                'success': False,
                'error': 'No Neo4j connection available'
            }
        
        statistics = calculate_statistics(results)
        
        return {
            'success': True,
            'file': file_info,
            'results': results,
            'statistics': statistics
        }
        
    except Exception as e:
        logger.error(f"Error getting file graph: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get("/api/files/{file_id}/graph-exists")
async def check_file_graph_exists(file_id: str):
    """Check if graph data exists for a specific file"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to get file info from AASX routes first
        file_info = None
        
        try:
            from webapp.aasx.routes import FILES_DB
            
            if file_id in FILES_DB:
                file_info = FILES_DB[file_id]
        except ImportError:
            # If import fails, try to find file in project directories
            output_dir = Path("output/projects")
            if output_dir.exists():
                for project_dir in output_dir.iterdir():
                    if project_dir.is_dir():
                        file_dir = project_dir / file_id
                        if file_dir.exists() and file_dir.is_dir():
                            file_info_file = file_dir / "file_info.json"
                            if file_info_file.exists():
                                try:
                                    with open(file_info_file, 'r') as f:
                                        file_info = json.load(f)
                                        break
                                except:
                                    pass
                            else:
                                # Create basic file info
                                file_info = {
                                    "id": file_id,
                                    "filename": file_id,
                                    "original_filename": file_id,
                                    "project_id": project_dir.name,
                                    "filepath": str(file_dir),
                                    "size": 0,
                                    "upload_date": "Unknown",
                                    "description": f"File from directory {file_id}",
                                    "status": "completed",
                                    "processing_result": {}
                                }
                                break
        
        if not file_info:
            return {
                'success': False,
                'error': 'File not found',
                'graph_exists': False
            }
        
        # Check if graph data exists by querying Neo4j
        filename = file_info.get('original_filename', file_id)
        query = f"""
        MATCH (n) 
        WHERE n.source_file = '{filename}' 
        RETURN count(n) as node_count
        """
        
        # Execute query
        from src.kg_neo4j.neo4j_manager import neo4j_manager
        
        results = None
        try:
            results = neo4j_manager.execute_query_docker(query)
        except:
            try:
                results = neo4j_manager.execute_query_local(query)
            except Exception as e:
                logger.error(f"Failed to check graph existence: {e}")
                return {
                    'success': False,
                    'error': f'Failed to query Neo4j: {str(e)}',
                    'graph_exists': False
                }
        
        if results is None:
            return {
                'success': False,
                'error': 'No Neo4j connection available',
                'graph_exists': False
            }
        
        # Check if any nodes exist for this file
        node_count = 0
        if results and len(results) > 0:
            node_count = results[0].get('node_count', 0)
        
        graph_exists = node_count > 0
        
        return {
            'success': True,
            'file': file_info,
            'graph_exists': graph_exists,
            'node_count': node_count
        }
        
    except Exception as e:
        logger.error(f"Error checking file graph existence: {e}")
        return {
            'success': False,
            'error': str(e),
            'graph_exists': False
        }

@router.get("/api/files/{file_id}/graph-data")
async def get_file_graph_data(file_id: str):
    """Get graph data directly from JSON files without Neo4j"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to get file info from AASX routes first
        file_info = None
        
        try:
            from webapp.aasx.routes import FILES_DB
            
            if file_id in FILES_DB:
                file_info = FILES_DB[file_id]
        except ImportError:
            pass
        
        # Search for graph data file directly
        output_dir = Path("output/projects")
        graph_data_file = None
        found_project_id = None
        found_file_dir = None
        
        logger.info(f"Searching for file {file_id} in output directory: {output_dir}")
        if file_info:
            logger.info(f"File info: project_id={file_info.get('project_id')}, filename={file_info.get('original_filename')}")
            logger.info(f"Base filename: {os.path.splitext(file_info.get('original_filename', ''))[0]}")
        
        if output_dir.exists():
            logger.info(f"Found output directory, scanning projects...")
            for project_dir in output_dir.iterdir():
                if project_dir.is_dir():
                    logger.info(f"Checking project directory: {project_dir.name}")
                    for file_dir in project_dir.iterdir():
                        if file_dir.is_dir():
                            potential_graph_file = file_dir / "aasx_data_graph.json"
                            logger.info(f"Checking file directory: {file_dir.name}, graph file exists: {potential_graph_file.exists()}")
                            if potential_graph_file.exists():
                                # If we have file info, check if this matches
                                if file_info:
                                    # Compare with base filename (without extension)
                                    file_base_name = os.path.splitext(file_info.get('original_filename', ''))[0]
                                    if (file_info.get('project_id') == project_dir.name and 
                                        file_base_name == file_dir.name):
                                        graph_data_file = potential_graph_file
                                        found_project_id = project_dir.name
                                        found_file_dir = file_dir.name
                                        break
                                else:
                                    # If no file info, use the first one we find
                                    graph_data_file = potential_graph_file
                                    found_project_id = project_dir.name
                                    found_file_dir = file_dir.name
                                    break
                    if graph_data_file:
                        break
        
        if not graph_data_file:
            return {
                'success': False,
                'error': 'Graph data file not found',
                'graph_data': None
            }
        
        # Create file info if not available
        if not file_info:
            file_info = {
                "id": file_id,
                "filename": found_file_dir,
                "original_filename": found_file_dir,
                "project_id": found_project_id,
                "filepath": str(graph_data_file.parent),
                "size": 0,
                "upload_date": "Unknown",
                "description": f"File from directory {found_file_dir}",
                "status": "completed",
                "processing_result": {}
            }
        
        # Read and parse the graph data
        try:
            with open(graph_data_file, 'r') as f:
                graph_data = json.load(f)
            
            # Convert to D3.js compatible format
            nodes = []
            links = []
            
            # Process nodes
            for node in graph_data.get('nodes', []):
                nodes.append({
                    'id': node['id'],
                    'label': node.get('description', node['id']),
                    'type': node['type'],
                    'properties': {k: v for k, v in node.items() if k not in ['id', 'type']}
                })
            
            # Process edges
            for edge in graph_data.get('edges', []):
                links.append({
                    'source': edge['source_id'],
                    'target': edge['target_id'],
                    'type': edge['type'],
                    'properties': edge.get('properties', {})
                })
            
            # Calculate statistics
            statistics = {
                'total_nodes': len(nodes),
                'total_relationships': len(links),
                'asset_nodes': len([n for n in nodes if n['type'] == 'asset']),
                'submodel_nodes': len([n for n in nodes if n['type'] == 'submodel']),
                'property_nodes': len([n for n in nodes if n['type'] == 'property']),
                'document_nodes': len([n for n in nodes if n['type'] == 'document'])
            }
            
            return {
                'success': True,
                'file': file_info,
                'graph_data': {
                    'nodes': nodes,
                    'links': links
                },
                'statistics': statistics,
                'metadata': graph_data.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error reading graph data file: {e}")
            return {
                'success': False,
                'error': f'Error reading graph data: {str(e)}',
                'graph_data': None
            }
        
    except Exception as e:
        logger.error(f"Error getting file graph data: {e}")
        return {
            'success': False,
            'error': str(e),
            'graph_data': None
        }

@router.get("/api/projects/{project_id}/graph-data")
async def get_project_graph_data(project_id: str):
    """Get graph data for all files in a project directly from JSON files"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to get project info from AASX routes first
        project = None
        project_files = []
        
        try:
            from webapp.aasx.routes import PROJECTS_DB, FILES_DB
            
            if project_id in PROJECTS_DB:
                project = PROJECTS_DB[project_id]
                project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
        except ImportError:
            # If import fails, try to get project info from directory structure
            project_dir = Path(f"output/projects/{project_id}")
            if project_dir.exists():
                project_info_file = project_dir / "project_info.json"
                if project_info_file.exists():
                    try:
                        with open(project_info_file, 'r') as f:
                            project = json.load(f)
                    except:
                        pass
                
                # Get files from directory structure
                for file_dir in project_dir.iterdir():
                    if file_dir.is_dir():
                        file_info_file = file_dir / "file_info.json"
                        if file_info_file.exists():
                            try:
                                with open(file_info_file, 'r') as f:
                                    file_info = json.load(f)
                                    project_files.append(file_info)
                            except:
                                project_files.append({
                                    "id": file_dir.name,
                                    "filename": file_dir.name,
                                    "original_filename": file_dir.name,
                                    "project_id": project_id,
                                    "filepath": str(file_dir),
                                    "size": 0,
                                    "upload_date": "Unknown",
                                    "description": f"File from directory {file_dir.name}",
                                    "status": "completed",
                                    "processing_result": {}
                                })
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'graph_data': None
            }
        
        # Collect graph data from all files in the project
        all_nodes = []
        all_links = []
        node_id_map = {}  # To handle duplicate nodes across files
        
        for file_info in project_files:
            # Look for graph data file
            filename = file_info.get('original_filename', file_info['id'])
            base_filename = os.path.splitext(filename)[0]
            file_output_dir = Path(f"output/projects/{project_id}/{base_filename}")
            
            graph_data_file = file_output_dir / "aasx_data_graph.json"
            
            if graph_data_file.exists():
                try:
                    with open(graph_data_file, 'r') as f:
                        graph_data = json.load(f)
                    
                    # Process nodes
                    for node in graph_data.get('nodes', []):
                        node_id = node['id']
                        if node_id not in node_id_map:
                            node_id_map[node_id] = len(all_nodes)
                            all_nodes.append({
                                'id': node_id,
                                'label': node.get('description', node_id),
                                'type': node['type'],
                                'properties': {k: v for k, v in node.items() if k not in ['id', 'type']},
                                'source_file': file_info.get('original_filename', file_info['id'])
                            })
                    
                    # Process edges
                    for edge in graph_data.get('edges', []):
                        source_id = edge['source_id']
                        target_id = edge['target_id']
                        
                        # Only add edge if both nodes exist
                        if source_id in node_id_map and target_id in node_id_map:
                            all_links.append({
                                'source': source_id,
                                'target': target_id,
                                'type': edge['type'],
                                'properties': edge.get('properties', {}),
                                'source_file': file_info.get('original_filename', file_info['id'])
                            })
                
                except Exception as e:
                    logger.error(f"Error reading graph data for file {file_info.get('original_filename', file_info['id'])}: {e}")
                    continue
        
        # Calculate statistics
        statistics = {
            'total_nodes': len(all_nodes),
            'total_relationships': len(all_links),
            'asset_nodes': len([n for n in all_nodes if n['type'] == 'asset']),
            'submodel_nodes': len([n for n in all_nodes if n['type'] == 'submodel']),
            'property_nodes': len([n for n in all_nodes if n['type'] == 'property']),
            'document_nodes': len([n for n in all_nodes if n['type'] == 'document'])
        }
        
        return {
            'success': True,
            'project': project,
            'files': project_files,
            'graph_data': {
                'nodes': all_nodes,
                'links': all_links
            },
            'statistics': statistics,
            'metadata': {
                'total_files_processed': len([f for f in project_files if Path(f.get('filepath', '')).exists()]),
                'total_files': len(project_files)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting project graph data: {e}")
        return {
            'success': False,
            'error': str(e),
            'graph_data': None
        }

@router.get("/api/debug/file-path/{file_id}")
async def debug_file_path(file_id: str):
    """Debug endpoint to test file path construction"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to get file info from AASX routes first
        file_info = None
        
        try:
            from webapp.aasx.routes import FILES_DB
            
            if file_id in FILES_DB:
                file_info = FILES_DB[file_id]
                logger.info(f"Found file in FILES_DB: {file_info}")
            else:
                logger.info(f"File {file_id} not found in FILES_DB")
        except ImportError as e:
            logger.info(f"Import error: {e}")
        
        # Also try to find file in project directories
        output_dir = Path("output/projects")
        found_dirs = []
        
        if output_dir.exists():
            for project_dir in output_dir.iterdir():
                if project_dir.is_dir():
                    for file_dir in project_dir.iterdir():
                        if file_dir.is_dir():
                            graph_file = file_dir / "aasx_data_graph.json"
                            if graph_file.exists():
                                found_dirs.append({
                                    'project_id': project_dir.name,
                                    'file_dir': file_dir.name,
                                    'graph_file': str(graph_file),
                                    'file_id_match': file_dir.name == file_id
                                })
        
        return {
            'success': True,
            'file_id': file_id,
            'file_info_from_db': file_info,
            'found_directories': found_dirs,
            'all_files_in_db': list(FILES_DB.keys()) if 'FILES_DB' in locals() else []
        }
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get("/api/debug/graph-data/{project_id}")
async def debug_graph_data(project_id: str):
    """Debug endpoint to test graph data loading"""
    try:
        import os
        import json
        from pathlib import Path
        
        # Try to get project info from AASX routes first
        project = None
        project_files = []
        
        try:
            from webapp.aasx.routes import PROJECTS_DB, FILES_DB
            
            if project_id in PROJECTS_DB:
                project = PROJECTS_DB[project_id]
                project_files = [f for f in FILES_DB.values() if f["project_id"] == project_id]
                logger.info(f"Found project in DB: {project}")
                logger.info(f"Project files: {len(project_files)}")
        except ImportError as e:
            logger.info(f"Import error: {e}")
        
        # Collect graph data from all files in the project
        all_nodes = []
        all_links = []
        node_id_map = {}  # To handle duplicate nodes across files
        debug_info = []
        
        for file_info in project_files:
            # Look for graph data file
            filename = file_info.get('original_filename', file_info['id'])
            base_filename = os.path.splitext(filename)[0]
            file_output_dir = Path(f"output/projects/{project_id}/{base_filename}")
            
            graph_data_file = file_output_dir / "aasx_data_graph.json"
            debug_info.append({
                'file_info': file_info,
                'file_output_dir': str(file_output_dir),
                'graph_data_file': str(graph_data_file),
                'exists': graph_data_file.exists()
            })
            
            if graph_data_file.exists():
                try:
                    with open(graph_data_file, 'r') as f:
                        graph_data = json.load(f)
                    
                    debug_info[-1]['graph_data_keys'] = list(graph_data.keys())
                    debug_info[-1]['nodes_count'] = len(graph_data.get('nodes', []))
                    debug_info[-1]['edges_count'] = len(graph_data.get('edges', []))
                    
                    # Process nodes
                    for node in graph_data.get('nodes', []):
                        node_id = node['id']
                        if node_id not in node_id_map:
                            node_id_map[node_id] = len(all_nodes)
                            all_nodes.append({
                                'id': node_id,
                                'label': node.get('description', node_id),
                                'type': node['type'],
                                'properties': {k: v for k, v in node.items() if k not in ['id', 'type']},
                                'source_file': file_info.get('original_filename', file_info['id'])
                            })
                    
                    # Process edges
                    for edge in graph_data.get('edges', []):
                        source_id = edge['source_id']
                        target_id = edge['target_id']
                        
                        # Only add edge if both nodes exist
                        if source_id in node_id_map and target_id in node_id_map:
                            all_links.append({
                                'source': source_id,
                                'target': target_id,
                                'type': edge['type'],
                                'properties': edge.get('properties', {}),
                                'source_file': file_info.get('original_filename', file_info['id'])
                            })
                
                except Exception as e:
                    logger.error(f"Error reading graph data for file {file_info.get('original_filename', file_info['id'])}: {e}")
                    debug_info[-1]['error'] = str(e)
                    continue
        
        return {
            'success': True,
            'project': project,
            'project_files_count': len(project_files),
            'debug_info': debug_info,
            'processed_nodes': len(all_nodes),
            'processed_links': len(all_links),
            'node_id_map_size': len(node_id_map),
            'sample_nodes': all_nodes[:3] if all_nodes else [],
            'sample_links': all_links[:3] if all_links else []
        }
        
    except Exception as e:
        logger.error(f"Error in debug graph data endpoint: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_docker_status():
    """Check if Neo4j Docker container is running"""
    try:
        # Check if Docker is available
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return {
                'running': False,
                'status': 'Docker not available',
                'error': 'Docker command not found'
            }
        
        # Check for Neo4j container
        result = subprocess.run([
            'docker', 'ps', '--filter', 'name=neo4j', 
            '--format', '{{.Names}}\t{{.Status}}\t{{.ID}}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'neo4j' in line.lower():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        return {
                            'running': True,
                            'status': parts[1],
                            'container_id': parts[2],
                            'container_name': parts[0]
                        }
        
        # Check if container exists but is stopped
        result = subprocess.run([
            'docker', 'ps', '-a', '--filter', 'name=neo4j',
            '--format', '{{.Names}}\t{{.Status}}\t{{.ID}}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'neo4j' in line.lower():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        return {
                            'running': False,
                            'status': parts[1],
                            'container_id': parts[2],
                            'container_name': parts[0]
                        }
        
        return {
            'running': False,
            'status': 'Container not found',
            'error': 'Neo4j container not found'
        }
        
    except subprocess.TimeoutExpired:
        return {
            'running': False,
            'status': 'Timeout',
            'error': 'Docker command timed out'
        }
    except Exception as e:
        return {
            'running': False,
            'status': 'Error',
            'error': str(e)
        }

def check_browser_accessibility():
    """Check if Neo4j Browser is accessible"""
    try:
        import requests
        # Try port 7475 first (your container's port), then fallback to 7474
        try:
            response = requests.get('http://localhost:7475', timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        # Fallback to standard port 7474
        response = requests.get('http://localhost:7474', timeout=5)
        return response.status_code == 200
    except:
        return False

def get_active_connections():
    """Get number of active connections (simplified)"""
    try:
        # This would require Neo4j connection to get actual count
        # For now, return a placeholder
        return 0
    except:
        return 0

def start_neo4j_docker():
    """Start Neo4j Docker container"""
    try:
        # Check if container already exists
        status = check_docker_status()
        
        if status.get('running', False):
            return {
                'success': True,
                'message': 'Neo4j container is already running'
            }
        
        # Start the container
        if status.get('container_id'):
            # Container exists but stopped, start it
            result = subprocess.run([
                'docker', 'start', status['container_id']
            ], capture_output=True, text=True, timeout=30)
        else:
            # Create and start new container
            result = subprocess.run([
                'docker', 'run', '-d',
                '--name', 'neo4j',
                '-p', '7474:7474',
                '-p', '7687:7687',
                '-e', 'NEO4J_AUTH=neo4j/password',
                '-e', 'NEO4J_PLUGINS=["apoc"]',
                'neo4j:latest'
            ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': 'Neo4j container started successfully'
            }
        else:
            return {
                'success': False,
                'error': f'Failed to start container: {result.stderr}'
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Docker command timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def stop_neo4j_docker():
    """Stop Neo4j Docker container"""
    try:
        status = check_docker_status()
        
        if not status.get('running', False):
            return {
                'success': True,
                'message': 'Neo4j container is not running'
            }
        
        if status.get('container_id'):
            result = subprocess.run([
                'docker', 'stop', status['container_id']
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Neo4j container stopped successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to stop container: {result.stderr}'
                }
        else:
            return {
                'success': False,
                'error': 'No container ID found'
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Docker command timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def calculate_statistics(results):
    """Calculate statistics from query results"""
    try:
        stats = {
            'total_nodes': 0,
            'total_relationships': 0,
            'asset_nodes': 0,
            'submodel_nodes': 0,
            'property_nodes': 0
        }
        
        node_ids = set()
        relationship_ids = set()
        
        for record in results:
            # Count nodes
            if hasattr(record, 'n') and record.n:
                node_id = getattr(record.n, 'identity', getattr(record.n, 'id', None))
                if node_id and node_id not in node_ids:
                    node_ids.add(node_id)
                    stats['total_nodes'] += 1
                    
                    # Count by type
                    labels = getattr(record.n, 'labels', [])
                    if labels:
                        label = labels[0].lower()
                        if 'asset' in label:
                            stats['asset_nodes'] += 1
                        elif 'submodel' in label:
                            stats['submodel_nodes'] += 1
                        elif 'property' in label:
                            stats['property_nodes'] += 1
            
            # Count relationships
            if hasattr(record, 'r') and record.r:
                rel_id = getattr(record.r, 'identity', getattr(record.r, 'id', None))
                if rel_id and rel_id not in relationship_ids:
                    relationship_ids.add(rel_id)
                    stats['total_relationships'] += 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return {
            'total_nodes': 0,
            'total_relationships': 0,
            'asset_nodes': 0,
            'submodel_nodes': 0,
            'property_nodes': 0
        }