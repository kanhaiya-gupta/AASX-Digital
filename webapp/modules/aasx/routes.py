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

# Import existing services from src/shared
from src.shared.services.digital_twin_service import DigitalTwinService
from src.federated_learning.core.federated_learning_service import FederatedLearningService
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository

router = APIRouter(tags=["aasx-etl"])

# Template setup
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Initialize shared services
data_dir = Path("data")
db_path = data_dir / "aasx_database.db"
connection_manager = DatabaseConnectionManager(db_path)
db_manager = BaseDatabaseManager(connection_manager)

# Create service instances
file_repo = FileRepository(db_manager)
project_repo = ProjectRepository(db_manager)
digital_twin_service = DigitalTwinService(db_manager, file_repo, project_repo)
federated_learning_service = FederatedLearningService(digital_twin_service)

# Models
class ETLConfigRequest(BaseModel):
    files: Optional[List[Any]] = None  # Can be List[str] (filenames) or List[dict] (file objects with hierarchy)
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    use_case_name: Optional[str] = None  # For hierarchy-based file lookup
    output_dir: Optional[str] = None
    formats: Optional[List[str]] = ["json", "graph", "rdf", "yaml"]
    federated_learning: Optional[str] = "not_allowed"  # "allowed", "not_allowed", "conditional"
    user_consent: Optional[bool] = False  # User must explicitly consent to federated learning
    user_id: Optional[str] = None  # User ID for tracking consent
    consent_timestamp: Optional[str] = None  # When consent was given
    data_privacy_level: Optional[str] = "private"  # "private", "restricted", "shared"
    consent_terms: Optional[str] = None  # Specific terms user agreed to

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    use_case_id: str  # Required: Project must belong to a use case

class UseCaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

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
        # Validate project_id format
        if not project_id or not isinstance(project_id, str):
            raise HTTPException(status_code=400, detail="Invalid project ID format")
        
        # Validate file object
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided or invalid file object")
        
        # Validate file size (max 100MB)
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Validate file extension
        if not file.filename.lower().endswith('.aasx'):
            raise HTTPException(status_code=400, detail="Only AASX files are allowed")
        
        # Validate filename (prevent path traversal)
        import re
        if re.search(r'[<>:"/\\|?*]', file.filename):
            raise HTTPException(status_code=400, detail="Invalid filename. Contains forbidden characters")
        
        # Upload file with enhanced error handling
        file_info = file_service.upload_file(project_id, file, description)
        return file_info
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except FileNotFoundError as e:
        # Handle file system errors
        raise HTTPException(status_code=404, detail=f"File system error: {str(e)}")
    except PermissionError as e:
        # Handle permission errors
        raise HTTPException(status_code=403, detail=f"Permission denied: {str(e)}")
    except OSError as e:
        # Handle other OS errors
        raise HTTPException(status_code=500, detail=f"File system error: {str(e)}")
    except Exception as e:
        # Handle all other errors
        import logging
        logging.error(f"File upload failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

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
    """Run ETL pipeline for AASX files with federated learning integration"""
    try:
        print("🔍 ETL Route: Received request")
        print(f"📋 ETL Route: Config data: {config.dict()}")
        
        # Validate federated learning setting
        if config.federated_learning not in ['allowed', 'not_allowed', 'conditional']:
            raise HTTPException(status_code=400, detail="Invalid federated_learning value. Must be 'allowed', 'not_allowed', or 'conditional'")
        
        # Handle file selection - do reverse engineering to find file_id and project_id
        config_dict = config.dict()
        if config.files and len(config.files) > 0:
            print(f"🔄 ETL Route: Processing file selection: {config.files}")
            
            # Check if we have file objects with hierarchy info
            if isinstance(config.files[0], dict) and 'use_case_name' in config.files[0]:
                # We have hierarchy info - do reverse engineering
                file_obj = config.files[0]  # Process first file for now
                filename = file_obj['filename']
                use_case_name = file_obj['use_case_name']
                project_name = file_obj['project_name']
                
                print(f"🔍 ETL Route: Reverse engineering file_id for: {use_case_name}/{project_name}/{filename}")
                
                # Get use_case_id from use case name
                use_case_id = use_case_service.get_use_case_id_by_name(use_case_name)
                if use_case_id:
                    print(f"✅ ETL Route: Found use_case_id: {use_case_id}")
                                
                    # Use project service to find project_id first
                    project_id = project_service.get_project_id_by_path(use_case_name, project_name)
                    if project_id:
                        print(f"✅ ETL Route: Found project_id: {project_id}")
                                
                        # Get file_id from filename
                        file_id = file_service.get_file_id_by_path(use_case_name, project_name, filename)
                        if file_id:
                            config_dict['file_id'] = file_id
                            config_dict['project_id'] = project_id
                            config_dict['use_case_id'] = use_case_id
                            config_dict['use_case_name'] = use_case_name
                            config_dict['project_name'] = project_name
                            print(f"✅ ETL Route: Found file_id: {file_id}, project_id: {project_id}, use_case_id: {use_case_id}")
                        else:
                            print(f"❌ ETL Route: Could not find file_id for {use_case_name}/{project_name}/{filename}")
                            raise HTTPException(status_code=404, detail=f"File {filename} not found in {use_case_name}/{project_name}")
                else:
                    print(f"❌ ETL Route: Could not find project_id for {use_case_name}/{project_name}")
                    raise HTTPException(status_code=404, detail=f"Project {project_name} not found in use case {use_case_name}")
            else:
                # Invalid file format - should be dict with hierarchy info
                print(f"❌ ETL Route: Invalid file format. Expected dict with hierarchy info, got: {type(config.files[0])}")
                raise HTTPException(status_code=400, detail="Invalid file format. Expected hierarchy information (use_case_name, project_name, filename)")
        
        print(f"📤 ETL Route: Sending to processor: {config_dict}")
        
        # Run ETL pipeline - all business logic is in processor
        result = aasx_processor.run_etl_pipeline(config_dict)
        
        print(f"📥 ETL Route: Processor result: {result}")
        return result
    except Exception as e:
        print(f"💥 ETL Route: Exception: {str(e)}")
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

@router.get("/files/by-path")
async def get_file_by_path(use_case_name: str, project_name: str, filename: str):
    """Get file information by use case, project, and filename"""
    try:
        file_info = file_service.get_file_by_path(use_case_name, project_name, filename)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/path-info")
async def get_file_path_info(file_id: str):
    """Get logical path information for a file (usecase/project/filename)"""
    try:
        path_info = file_service.get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/path")
async def get_file_path(file_id: str):
    """Get file hierarchy path from file_id (alias for path-info)"""
    try:
        path_info = file_service.get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/by-path/file-id")
async def get_file_id_by_path(use_case_name: str, project_name: str, filename: str):
    """Get file ID by use case, project, and filename"""
    try:
        file_id = file_service.get_file_id_by_path(use_case_name, project_name, filename)
        if not file_id:
            raise HTTPException(status_code=404, detail="File not found")
        return {"file_id": file_id, "logical_path": f"{use_case_name}/{project_name}/{filename}"}
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

# Digital Twin Federated Learning Endpoints
@router.get("/digital-twins/federated-learning/stats")
async def get_digital_twin_federated_stats():
    """Get federated learning statistics for digital twins"""
    try:
        stats = digital_twin_service.get_repository().get_federated_learning_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-consent/federated-learning")
async def record_user_consent_for_federated_learning(
    user_id: str,
    consent_given: bool,
    data_privacy_level: str = "private",
    consent_terms: str = None,
    project_id: str = None,
    file_id: str = None
):
    """Record user consent for federated learning participation"""
    try:
        # For now, return a simple response
        # In the future, this would integrate with a proper consent management system
        return {
            "success": True,
            "message": f"User consent {'recorded' if consent_given else 'declined'}",
            "user_id": user_id,
            "consent_given": consent_given,
            "data_privacy_level": data_privacy_level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-consent/{user_id}/federated-learning")
async def get_user_consent_status(user_id: str):
    """Get user's federated learning consent status"""
    try:
        # For now, return a placeholder
        # In the future, this would query the consent database
        return {
            "success": True,
            "user_id": user_id,
            "has_consent": False,  # Default to no consent
            "consent_timestamp": None,
            "data_privacy_level": "private"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/federated-learning/consent-terms")
async def get_federated_learning_consent_terms():
    """Get the current federated learning consent terms"""
    try:
        terms = {
            "version": "1.0",
            "title": "Federated Learning Participation Consent",
            "terms": [
                "I understand that my data may be used in federated learning processes",
                "I consent to the sharing of anonymized data for collaborative model training",
                "I understand that my data will be processed securely with privacy-preserving techniques",
                "I can withdraw my consent at any time",
                "I understand that participation is voluntary and I can opt out"
            ],
            "data_usage": [
                "Anonymized data sharing for model training",
                "Secure aggregation of model updates",
                "Privacy-preserving computation",
                "No direct access to raw data by other participants"
            ],
            "privacy_levels": {
                "private": "No data sharing, local processing only",
                "restricted": "Limited data sharing with strict controls",
                "shared": "Full participation in federated learning"
            }
        }
        return {"success": True, "terms": terms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital-twins/federated-learning/{participation_status}")
async def get_digital_twins_by_federated_status(participation_status: str):
    """Get digital twins by federated participation status"""
    try:
        twins = digital_twin_service.get_repository().get_federated_twins(participation_status)
        twin_data = [twin.to_dict() for twin in twins]
        return {"success": True, "data": twin_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/digital-twins/{twin_id}/federated-learning")
async def update_digital_twin_federated_learning(twin_id: str, federated_data: Dict[str, Any]):
    """Update federated learning settings for a digital twin"""
    try:
        success = digital_twin_service.get_repository().update_federated_metadata(twin_id, federated_data)
        if success:
            return {"success": True, "message": "Digital twin federated learning settings updated"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update federated learning settings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 