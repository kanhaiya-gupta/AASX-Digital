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