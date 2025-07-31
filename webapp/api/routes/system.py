"""
System routes for AASX Digital Twin Analytics Framework
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import sys
import platform
import psutil
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


@router.get("/status")
async def system_status():
    """Get system status information"""
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AASX Digital Twin Analytics Framework",
        "version": "1.0.0"
    }


@router.get("/debug")
async def debug_info():
    """Get debug information"""
    try:
        # System information
        system_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "hostname": platform.node()
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        }
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
        
        # Process information
        process = psutil.Process(os.getpid())
        process_info = {
            "pid": process.pid,
            "name": process.name(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
            "num_threads": process.num_threads(),
            "num_fds": process.num_fds() if hasattr(process, 'num_fds') else None
        }
        
        # Environment information
        env_info = {
            "working_directory": os.getcwd(),
            "environment_variables": dict(os.environ),
            "python_path": sys.path
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_info,
            "memory": memory_info,
            "disk": disk_info,
            "process": process_info,
            "environment": env_info
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/info")
async def system_info():
    """Get basic system information"""
    return {
        "name": "AASX Digital Twin Analytics Framework",
        "version": "1.0.0",
        "description": "A comprehensive framework for processing AASX files and building digital twin analytics",
        "python_version": sys.version,
        "platform": platform.platform(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/modules")
async def list_modules():
    """List available modules and their status"""
    modules = {
        "aasx": {"enabled": True, "status": "active"},
        "ai_rag": {"enabled": True, "status": "active"},
        "twin_registry": {"enabled": True, "status": "active"},
        "certificate_manager": {"enabled": True, "status": "active"},
        "qi_analytics": {"enabled": True, "status": "active"},
        "kg_neo4j": {"enabled": True, "status": "active"},
        "federated_learning": {"enabled": True, "status": "active"},
        "physics_modeling": {"enabled": True, "status": "active"}
    }
    
    return {
        "modules": modules,
        "total_modules": len(modules),
        "active_modules": len([m for m in modules.values() if m["enabled"]]),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/config")
async def get_config():
    """Get current configuration (non-sensitive)"""
    from config.settings import settings
    
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "host": settings.host,
        "port": settings.port,
        "allowed_origins": settings.allowed_origins,
        "max_file_size": settings.max_file_size,
        "upload_dir": settings.upload_dir,
        "log_level": settings.log_level,
        "websocket_ping_interval": settings.websocket_ping_interval,
        "websocket_ping_timeout": settings.websocket_ping_timeout,
        "timestamp": datetime.utcnow().isoformat()
    } 