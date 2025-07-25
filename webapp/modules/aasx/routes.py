"""
AASX ETL API: Minimal, modern FastAPI router for project/file management and ETL pipeline.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uuid
from pathlib import Path
from src.aasx.aasx_extraction import extract_aasx, batch_extract
from src.shared.management import ProjectManager, FileManagementError

router = APIRouter(tags=["aasx"])

# Template setup
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))
AASX_CONTENT_PATH = os.path.join(current_dir, "data", "aasx-examples")
project_manager = ProjectManager()

# Models
class ETLConfigRequest(BaseModel):
    files: Optional[List[str]] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None  # Allow user to specify project by name
    output_dir: Optional[str] = None
    formats: Optional[List[str]] = ["json", "graph", "rdf", "yaml"]

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

# Dashboard
@router.get("/", response_class=HTMLResponse)
async def aasx_dashboard(request: Request):
    return templates.TemplateResponse(
        "aasx/index.html",
        {"request": request, "title": "AASX ETL Pipeline - AASX Digital Twin Analytics Framework"}
    )

# ETL Endpoints
@router.post("/api/etl/run")
async def run_etl_pipeline(config: ETLConfigRequest):
    # Accept project_id or project_name
    project_id = config.project_id
    if not project_id:
        # Try to resolve project_id from project_name
        if config.project_name:
            projects = project_manager.list_projects()
            match = next((p for p in projects if p["name"] == config.project_name), None)
            if not match:
                raise HTTPException(status_code=404, detail=f"Project with name '{config.project_name}' not found.")
            project_id = match["id"]
        else:
            raise HTTPException(status_code=400, detail="project_id or project_name is required.")
    # Fallback: select all files if none specified
    files = config.files
    if not files or len(files) == 0:
        project_files = project_manager.list_project_files(project_id)
        if not project_files:
            raise HTTPException(status_code=400, detail="No files found in the selected project.")
        files = [f["filename"] for f in project_files]
    # Find file paths
    file_infos = []
    print(f"🔍 Debug config: {config}")
    for fname in files:
        file_info = project_manager.find_file_by_name(project_id, fname)
        if not file_info:
            raise HTTPException(status_code=404, detail=f"File {fname} not found in project {project_id}")
        file_infos.append(file_info)
    # Output dir
    output_dir = Path(config.output_dir) if config.output_dir else Path("output") / "projects" / project_id
    output_dir.mkdir(parents=True, exist_ok=True)
    # Run extraction for each file
    results = {}
    print(f"🔍 Debug file_infos: {file_infos}")
    for file_info in file_infos:
        file_path = Path(file_info["filepath"])
        # Use a simpler output directory structure without {filename} placeholder
        file_output_dir = output_dir / Path(file_info["filename"]).stem
        file_output_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = extract_aasx(file_path, file_output_dir, formats=config.formats)
            # Update file status to completed REGARDLESS of previous status
            file_id = file_info.get('file_id')
            if file_id:
                # Always overwrite status to completed on successful ETL
                project_manager.update_file_status(project_id, file_id, "completed", result)
                
                # Always register digital twin after successful ETL (regardless of previous status)
                twin_result = project_manager.register_digital_twin(project_id, file_id)
                
                # Use file_id as key for consistency
                results[file_id] = result
                results[file_id]["twin_registration"] = twin_result
                
                print(f"✅ Successfully processed {file_info['filename']} and registered twin")
            else:
                print(f"⚠️ Could not update file status: no file_id found for {file_info['filename']}")
                results[file_info["filename"]] = result
        except Exception as e:
            # Update file status to error
            file_id = file_info.get('file_id')
            if file_id:
                project_manager.update_file_status(project_id, file_id, "error", {"error": str(e)})
                results[file_id] = {"status": "error", "error": str(e)}
            else:
                print(f"⚠️ Could not update file status: no file_id found for {file_info['filename']}")
                results[file_info["filename"]] = {"status": "error", "error": str(e)}
    return {"success": True, "results": results}

@router.get("/api/etl/progress")
async def get_etl_progress():
    """Get current ETL pipeline progress"""
    # For now, return a simple progress response since we don't have real-time progress tracking
    # This can be enhanced later with actual progress tracking
    return {
        "is_running": False,
        "current_file": None,
        "files_completed": 0,
        "total_files": 0,
        "progress": 0,
        "status_message": "ETL pipeline not running",
        "timestamp": datetime.now().isoformat()
    }

# Project Endpoints - Less specific routes after
@router.get("/api/projects")
async def list_projects():
    return project_manager.list_projects()

# File Endpoints - More specific routes first
from fastapi import UploadFile, File, Form

@router.post("/api/projects/{project_id}/upload")
async def upload_file(project_id: str, file: UploadFile = File(...), description: str = Form(None)):
    if not project_manager.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not file.filename.lower().endswith('.aasx'):
        raise HTTPException(status_code=400, detail="Only AASX files are allowed")
    if project_manager.check_duplicate_file(project_id, file.filename):
        raise HTTPException(status_code=409, detail=f"File '{file.filename}' already exists in this project.")
    temp_file_path = Path(f"/tmp/{file.filename}")
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    try:
        file_info = project_manager.upload_file(
            project_id=project_id,
            file_path=temp_file_path,
            original_filename=file.filename,
            description=description
        )
        return file_info
    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()

@router.get("/api/projects/{project_id}/files")
async def list_project_files(project_id: str):
    print(f"DEBUG: Called list_project_files for {project_id}")
    if not project_manager.project_exists(project_id):
        print(f"DEBUG: Project {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    files = project_manager.list_project_files(project_id)
    print(f"DEBUG: Returning {len(files)} files for {project_id}")
    return files

@router.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    if not project_manager.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    project = project_manager.get_project_metadata(project_id)
    project["id"] = project_id
    project["files"] = project_manager.list_project_files(project_id)
    return project

@router.delete("/api/projects/{project_id}/files/{file_id}")
async def delete_project_file(project_id: str, file_id: str):
    if not project_manager.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    file_info = project_manager.get_file_info(project_id, file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    success = project_manager.delete_file(project_id, file_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete file")
    return {"message": "File deleted successfully"}

@router.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    if not project_manager.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    success = project_manager.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete project")
    return {"message": "Project deleted successfully"}

@router.post("/api/refresh")
async def refresh_files_and_statuses(project_id: str = None):
    """
    Refresh file statuses and digital twin statuses for all projects or a specific project.
    This should be called on page load or when the user clicks a refresh button.
    """
    result = project_manager.refresh_files_and_reset_statuses(project_id)
    return result

@router.post("/api/files/reset-statuses")
async def reset_file_statuses_endpoint():
    """Manually trigger file status reset when outputs are missing"""
    try:
        print("🔄 Reset file statuses endpoint called")
        result = project_manager.reset_file_statuses_if_output_missing()
        print(f"✅ Reset result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error in reset endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset file statuses: {str(e)}")

# Helper: Find AASX file in content dir

def find_aasx_file(filename: str) -> Optional[str]:
    for root, dirs, files in os.walk(AASX_CONTENT_PATH):
        if filename in files:
            return os.path.join(root, filename)
    return None 