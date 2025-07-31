"""
AASX ETL API: Thin FastAPI router using modular service architecture.
Enforces Use Case → Projects → Files hierarchy.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

# Import our service modules
from .use_cases import use_case_service
from .projects import project_service
from .files import file_service
from .processor import aasx_processor

router = APIRouter(tags=["aasx"])

# Template setup
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Models
class ETLConfigRequest(BaseModel):
    files: Optional[List[str]] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    output_dir: Optional[str] = None
    formats: Optional[List[str]] = ["json", "graph", "rdf", "yaml"]

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    use_case_id: str  # Required: Project must belong to a use case

class UseCaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None

# Dashboard
@router.get("/", response_class=HTMLResponse)
async def aasx_dashboard(request: Request):
    return templates.TemplateResponse(
        "aasx/index.html",
        {"request": request, "title": "AASX ETL Pipeline - AASX Digital Twin Analytics Framework"}
    )

# Use Case Endpoints
@router.get("/use-cases")
async def list_use_cases():
    """Get available use cases for AASX processing from database"""
    try:
        return use_case_service.list_use_cases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}")
async def get_use_case(use_case_id: str):
    """Get a specific use case"""
    try:
        use_case = use_case_service.get_use_case(use_case_id)
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        return use_case
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/use-cases")
async def create_use_case(use_case_data: UseCaseCreate):
    """Create a new use case"""
    try:
        use_case_id = use_case_service.create_use_case(use_case_data.dict())
        return {"use_case_id": use_case_id, "message": "Use case created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/use-cases/{use_case_id}")
async def update_use_case(use_case_id: str, updates: Dict[str, Any]):
    """Update a use case"""
    try:
        success = use_case_service.update_use_case(use_case_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Use case not found")
        return {"message": "Use case updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/use-cases/{use_case_id}")
async def delete_use_case(use_case_id: str):
    """Delete a use case and all its projects"""
    try:
        success = use_case_service.delete_use_case(use_case_id)
        if not success:
            raise HTTPException(status_code=404, detail="Use case not found")
        return {"message": "Use case deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}/projects")
async def get_use_case_projects(use_case_id: str):
    """Get all projects for a specific use case"""
    try:
        projects = project_service.list_projects(use_case_id)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Project Endpoints
@router.get("/projects")
async def list_projects(use_case_id: str = None):
    """Get all projects, optionally filtered by use case"""
    try:
        return project_service.list_projects(use_case_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project with its files and use case info"""
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects")
async def create_project(project_data: ProjectCreate):
    """Create a new project (must be linked to a use case)"""
    try:
        project_id = project_service.create_project(project_data.dict(), project_data.use_case_id)
        return {"project_id": project_id, "message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}")
async def update_project(project_id: str, updates: Dict[str, Any]):
    """Update a project"""
    try:
        success = project_service.update_project(project_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all its files"""
    try:
        success = project_service.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/validate-hierarchy")
async def validate_project_hierarchy(project_id: str):
    """Validate that a project is properly linked to a use case"""
    try:
        validation = project_service.validate_project_hierarchy(project_id)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Endpoints
@router.post("/projects/{project_id}/upload")
async def upload_file(project_id: str, file: UploadFile = File(...), description: str = Form(None)):
    """Upload a file to a project (project must be in valid hierarchy)"""
    try:
        file_info = file_service.upload_file(project_id, file, description)
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
async def list_project_files(project_id: str):
    """Get all files for a project (with hierarchy validation)"""
    try:
        return file_service.list_project_files(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files/{file_id}")
async def get_file(project_id: str, file_id: str):
    """Get a specific file (with hierarchy validation)"""
    try:
        file_info = file_service.get_file(project_id, file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}/files/{file_id}")
async def delete_file(project_id: str, file_id: str):
    """Delete a file from a project (with hierarchy validation)"""
    try:
        success = file_service.delete_file(project_id, file_id)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}/files/{file_id}")
async def update_file(project_id: str, file_id: str, updates: Dict[str, Any]):
    """Update file metadata (with hierarchy validation)"""
    try:
        success = file_service.update_file(project_id, file_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_all_files():
    """Get all files across all projects (with hierarchy information)"""
    try:
        return file_service.list_all_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ETL Processing Endpoints
@router.post("/etl/run")
async def run_etl_pipeline(config: ETLConfigRequest):
    """Run ETL pipeline for AASX files"""
    try:
        result = aasx_processor.run_etl_pipeline(config.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/progress")
async def get_etl_progress():
    """Get ETL processing progress"""
    try:
        return aasx_processor.get_etl_progress()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/status")
async def get_etl_status():
    """Get ETL processing status"""
    try:
        return aasx_processor.get_etl_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for frontend compatibility
@router.get("/files")
async def list_files_for_etl():
    """Get all files for ETL pipeline (alias for compatibility)"""
    try:
        return file_service.list_all_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/sync")
async def sync_projects():
    """Sync projects and refresh statuses"""
    try:
        return project_service.refresh_project_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics and Utility Endpoints
@router.get("/stats")
async def get_aasx_stats():
    """Get AASX processing statistics"""
    try:
        return aasx_processor.get_aasx_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_files_and_statuses(project_id: str = None):
    """Refresh file statuses and digital twin statuses"""
    try:
        return project_service.refresh_project_status(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/reset-statuses")
async def reset_file_statuses_endpoint():
    """Manually trigger file status reset when outputs are missing"""
    try:
        return file_service.reset_file_statuses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 