"""
Backend Knowledge Graph Neo4j Package
Provides Neo4j integration for the AASX Knowledge Graph system
"""

from fastapi import APIRouter, HTTPException
from .neo4j_manager import neo4j_manager
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/status")
async def get_neo4j_status() -> Dict[str, Any]:
    """Get Docker Neo4j connection status"""
    try:
        return neo4j_manager.check_docker_connection()
    except Exception as e:
        logger.error(f"Error checking Neo4j status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/docker-status")
async def get_docker_status() -> Dict[str, Any]:
    """Get Docker container status"""
    try:
        return neo4j_manager.check_docker_status()
    except Exception as e:
        logger.error(f"Error checking Docker status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/docker/start")
async def start_docker_neo4j() -> Dict[str, Any]:
    """Start Docker Neo4j container"""
    try:
        return neo4j_manager.start_docker_neo4j()
    except Exception as e:
        logger.error(f"Error starting Docker Neo4j: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/docker/stop")
async def stop_docker_neo4j() -> Dict[str, Any]:
    """Stop Docker Neo4j container"""
    try:
        return neo4j_manager.stop_docker_neo4j()
    except Exception as e:
        logger.error(f"Error stopping Docker Neo4j: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Local Neo4j Desktop routes
@router.get("/api/local/status")
async def get_local_neo4j_status() -> Dict[str, Any]:
    """Get local Neo4j Desktop status"""
    try:
        return neo4j_manager.get_local_neo4j_info()
    except Exception as e:
        logger.error(f"Error checking local Neo4j status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/local/desktop-status")
async def get_local_desktop_status() -> Dict[str, Any]:
    """Get local Neo4j Desktop application status"""
    try:
        return neo4j_manager.check_local_neo4j_desktop()
    except Exception as e:
        logger.error(f"Error checking local desktop status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/local/connection-status")
async def get_local_connection_status() -> Dict[str, Any]:
    """Get local Neo4j connection status"""
    try:
        return neo4j_manager.check_local_neo4j_connection()
    except Exception as e:
        logger.error(f"Error checking local connection status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/local/launch")
async def launch_local_neo4j_desktop() -> Dict[str, Any]:
    """Launch local Neo4j Desktop application"""
    try:
        return neo4j_manager.launch_local_neo4j_desktop()
    except Exception as e:
        logger.error(f"Error launching local Neo4j Desktop: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/local/info")
async def get_local_neo4j_info() -> Dict[str, Any]:
    """Get comprehensive local Neo4j Desktop information"""
    try:
        return neo4j_manager.get_local_neo4j_info()
    except Exception as e:
        logger.error(f"Error getting local Neo4j info: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 