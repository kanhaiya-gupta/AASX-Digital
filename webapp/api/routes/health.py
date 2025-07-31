"""
Health check routes for AASX Digital Twin Analytics Framework
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import psutil
import os
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AASX Digital Twin Analytics Framework"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system information"""
    try:
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process information
        process = psutil.Process(os.getpid())
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "AASX Digital Twin Analytics Framework",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total
            },
            "process": {
                "pid": process.pid,
                "memory_info": process.memory_info()._asdict(),
                "cpu_percent": process.cpu_percent(),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes/container orchestration"""
    # Add any readiness checks here (database connections, external services, etc.)
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration"""
    # Add any liveness checks here
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    } 