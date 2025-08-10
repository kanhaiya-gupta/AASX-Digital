"""
AASX ETL API: Thin FastAPI router using modular service architecture.
Enforces Use Case → Projects → Files hierarchy.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

# Import authentication decorators and user context
from webapp.core.decorators.auth_decorators import (
    require_auth, require_role, require_organization, 
    get_current_user, require_permission
)
from webapp.core.context.user_context import UserContext

# Import our service modules
from .use_cases import use_case_service
from .projects import project_service
from .files import file_service
from .processor import aasx_processor

# Import new user-specific and organization services
from .services.user_specific_service import UserSpecificService
from .services.organization_service import OrganizationService

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
@require_auth("read", allow_independent=True)
async def aasx_dashboard(request: Request, user_context: UserContext = Depends(get_current_user)):
    """AASX ETL Dashboard - requires read permission, allows independent users"""
    # Initialize user-specific service
    user_service = UserSpecificService(user_context)
    organization_service = OrganizationService(user_context)
    
    # Get user-specific data
    user_projects = user_service.get_user_projects()
    user_files = user_service.get_user_files()
    user_stats = user_service.get_user_statistics()
    organization_stats = organization_service.get_organization_statistics()
    
    return templates.TemplateResponse(
        "aasx/index.html",
        {
            "request": request, 
            "title": "AASX ETL Pipeline - AASX Digital Twin Analytics Framework",
            "user": user_context,
            "can_upload": getattr(user_context, 'has_permission', lambda x: False)("write"),
            "can_process": getattr(user_context, 'has_permission', lambda x: False)("write"),
            "can_delete": getattr(user_context, 'has_permission', lambda x: False)("manage"),
            "is_independent": getattr(user_context, 'is_independent', False),
            "user_type": getattr(user_context, 'get_user_type', lambda: 'independent')(),
            "user_projects": user_projects,
            "user_files": user_files,
            "user_stats": user_stats,
            "organization_stats": organization_stats
        }
    )

# Use Case Endpoints
@router.get("/use-cases")
@require_auth("read", allow_independent=True)
async def list_use_cases(user_context: UserContext = Depends(get_current_user)):
    """List all use cases - requires read permission, allows independent users"""
    try:
        use_cases = use_case_service.list_use_cases()
        return {"use_cases": use_cases, "total": len(use_cases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}")
@require_auth("read", allow_independent=True)
async def get_use_case(use_case_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get specific use case - requires read permission, allows independent users"""
    try:
        use_case = use_case_service.get_use_case(use_case_id)
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        return use_case
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/use-cases")
@require_auth("write", allow_independent=True)
async def create_use_case(use_case_data: UseCaseCreate, user_context: UserContext = Depends(get_current_user)):
    """Create new use case - requires write permission, allows independent users"""
    try:
        use_case_id = use_case_service.create_use_case(use_case_data.dict())
        return {"use_case_id": use_case_id, "message": "Use case created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Project Endpoints with User-Specific Data
@router.get("/projects")
@require_auth("read", allow_independent=True)
async def list_projects(use_case_id: str = None, user_context: UserContext = Depends(get_current_user)):
    """List projects for current user - requires read permission, allows independent users"""
    try:
        # Initialize user-specific service
        user_service = UserSpecificService(user_context)
        
        if use_case_id:
            # Filter by use case if specified
            all_projects = user_service.get_user_projects()
            projects = [p for p in all_projects if p.get("use_case_id") == use_case_id]
        else:
            # Get all user projects
            projects = user_service.get_user_projects()
        
        return {"projects": projects, "total": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
@require_auth("read", allow_independent=True)
async def get_project(project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get specific project - requires read permission, allows independent users"""
    try:
        # Initialize user-specific service
        user_service = UserSpecificService(user_context)
        
        # Check if user can access this project
        if not user_service.can_access_project(project_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Add file count
        project["file_count"] = user_service.get_project_file_count(project_id)
        
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects")
@require_auth("write", allow_independent=True)
async def create_project(project_data: ProjectCreate, user_context: UserContext = Depends(get_current_user)):
    """Create new project - requires write permission, allows independent users"""
    try:
        # Initialize user-specific service
        user_service = UserSpecificService(user_context)
        
        # Create project with user context
        project_id = user_service.create_user_project(project_data.dict())
        
        return {"project_id": project_id, "message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Endpoints with User-Specific Data
@router.get("/files")
@require_auth("read", allow_independent=True)
async def list_all_files(user_context: UserContext = Depends(get_current_user)):
    """List all files for current user - requires read permission, allows independent users"""
    try:
        # Initialize user-specific service
        user_service = UserSpecificService(user_context)
        
        files = user_service.get_user_files()
        return {"files": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}")
@require_auth("read", allow_independent=True)
async def get_file(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get specific file - requires read permission, allows independent users"""
    try:
        # Initialize user-specific service
        user_service = UserSpecificService(user_context)
        
        # Check if user can access this file
        if not user_service.can_access_file(file_id):
            raise HTTPException(status_code=403, detail="Access denied to this file")
        
        file_data = file_service.get_file_by_id(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        return file_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User-Specific Statistics
@router.get("/user/stats")
@require_auth("read", allow_independent=True)
async def get_user_stats(user_context: UserContext = Depends(get_current_user)):
    """Get user-specific statistics - requires read permission, allows independent users"""
    try:
        # Initialize user-specific service
        user_service = UserSpecificService(user_context)
        organization_service = OrganizationService(user_context)
        
        user_stats = user_service.get_user_statistics()
        organization_stats = organization_service.get_organization_statistics()
        
        return {
            "user_stats": user_stats,
            "organization_stats": organization_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Organization-Specific Endpoints
@router.get("/organization/projects")
@require_auth("read", allow_independent=False)
async def get_organization_projects(user_context: UserContext = Depends(get_current_user)):
    """Get organization projects - requires read permission, organization members only"""
    try:
        # Initialize organization service
        organization_service = OrganizationService(user_context)
        
        projects = organization_service.get_organization_projects()
        return {"projects": projects, "total": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/organization/files")
@require_auth("read", allow_independent=False)
async def get_organization_files(user_context: UserContext = Depends(get_current_user)):
    """Get organization files - requires read permission, organization members only"""
    try:
        # Initialize organization service
        organization_service = OrganizationService(user_context)
        
        files = organization_service.get_organization_files()
        return {"files": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/organization/stats")
@require_auth("read", allow_independent=False)
async def get_organization_stats(user_context: UserContext = Depends(get_current_user)):
    """Get organization statistics - requires read permission, organization members only"""
    try:
        # Initialize organization service
        organization_service = OrganizationService(user_context)
        
        stats = organization_service.get_organization_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/organization/members")
@require_auth("read", allow_independent=False)
async def get_organization_members(user_context: UserContext = Depends(get_current_user)):
    """Get organization members - requires read permission, organization members only"""
    try:
        # Initialize organization service
        organization_service = OrganizationService(user_context)
        
        members = organization_service.get_organization_members()
        return {"members": members, "total": len(members)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Continue with existing endpoints...

# ETL Processing Endpoints
@router.post("/etl/run")
@require_auth("write", allow_independent=True)
async def run_etl_pipeline(config: ETLConfigRequest, user_context: UserContext = Depends(get_current_user)):
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
@require_auth("read", allow_independent=True)
async def get_etl_progress(user_context: UserContext = Depends(get_current_user)):
    """Get ETL processing progress"""
    try:
        return aasx_processor.get_etl_progress()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/status")
@require_auth("read", allow_independent=True)
async def get_etl_status(user_context: UserContext = Depends(get_current_user)):
    """Get ETL processing status"""
    try:
        return aasx_processor.get_etl_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for frontend compatibility
@router.get("/files")
@require_auth("read", allow_independent=True)
async def list_files_for_etl(user_context: UserContext = Depends(get_current_user)):
    """Get all files for ETL pipeline (alias for compatibility)"""
    try:
        files = file_service.list_all_files()
        
        # Check access permissions for all files
        is_independent = getattr(user_context, 'is_independent', False)
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        for file_info in files:
            if is_independent:
                if file_info.get('created_by') != user_id:
                    raise HTTPException(status_code=403, detail="Access denied")
            else:
                if (file_info.get('organization_id') != organization_id and 
                    file_info.get('created_by') != user_id):
                    raise HTTPException(status_code=403, detail="Access denied")

        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/by-path")
@require_auth("read", allow_independent=True)
async def get_file_by_path(use_case_name: str, project_name: str, filename: str, user_context: UserContext = Depends(get_current_user)):
    """Get file information by use case, project, and filename"""
    try:
        file_info = file_service.get_file_by_path(use_case_name, project_name, filename)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        is_independent = getattr(user_context, 'is_independent', False)
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        if is_independent:
            if file_info.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            if (file_info.get('organization_id') != organization_id and 
                file_info.get('created_by') != user_id):
                raise HTTPException(status_code=403, detail="Access denied")

        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/path-info")
@require_auth("read", allow_independent=True)
async def get_file_path_info(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get logical path information for a file (usecase/project/filename)"""
    try:
        path_info = file_service.get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        is_independent = getattr(user_context, 'is_independent', False)
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        if is_independent:
            if path_info.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            if (path_info.get('organization_id') != organization_id and 
                path_info.get('created_by') != user_id):
                raise HTTPException(status_code=403, detail="Access denied")

        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/path")
@require_auth("read", allow_independent=True)
async def get_file_path(file_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get file hierarchy path from file_id (alias for path-info)"""
    try:
        path_info = file_service.get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        is_independent = getattr(user_context, 'is_independent', False)
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        if is_independent:
            if path_info.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            if (path_info.get('organization_id') != organization_id and 
                path_info.get('created_by') != user_id):
                raise HTTPException(status_code=403, detail="Access denied")

        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/by-path/file-id")
@require_auth("read", allow_independent=True)
async def get_file_id_by_path(use_case_name: str, project_name: str, filename: str, user_context: UserContext = Depends(get_current_user)):
    """Get file ID by use case, project, and filename"""
    try:
        file_id = file_service.get_file_id_by_path(use_case_name, project_name, filename)
        if not file_id:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions
        is_independent = getattr(user_context, 'is_independent', False)
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        if is_independent:
            if file_id.get('created_by') != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            if (file_id.get('organization_id') != organization_id and 
                file_id.get('created_by') != user_id):
                raise HTTPException(status_code=403, detail="Access denied")

        return {"file_id": file_id, "logical_path": f"{use_case_name}/{project_name}/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/sync")
@require_auth("write", allow_independent=True)
async def sync_projects(user_context: UserContext = Depends(get_current_user)):
    """Sync projects and refresh statuses"""
    try:
        return project_service.refresh_project_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics and Utility Endpoints
@router.get("/stats")
@require_auth("read", allow_independent=True)
async def get_aasx_stats(user_context: UserContext = Depends(get_current_user)):
    """Get AASX processing statistics"""
    try:
        return aasx_processor.get_aasx_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
@require_auth("write", allow_independent=True)
async def refresh_files_and_statuses(project_id: str = None, user_context: UserContext = Depends(get_current_user)):
    """Refresh file statuses and digital twin statuses"""
    try:
        return project_service.refresh_project_status(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/reset-statuses")
@require_auth("write", allow_independent=True)
async def reset_file_statuses_endpoint(user_context: UserContext = Depends(get_current_user)):
    """Manually trigger file status reset when outputs are missing"""
    try:
        return file_service.reset_file_statuses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Digital Twin Federated Learning Endpoints
@router.get("/digital-twins/federated-learning/stats")
@require_auth("read", allow_independent=True)
async def get_digital_twin_federated_stats(user_context: UserContext = Depends(get_current_user)):
    """Get federated learning statistics for digital twins"""
    try:
        stats = digital_twin_service.get_repository().get_federated_learning_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-consent/federated-learning")
@require_auth("write", allow_independent=True)
async def record_user_consent_for_federated_learning(
    user_id: str,
    consent_given: bool,
    data_privacy_level: str = "private",
    consent_terms: str = None,
    project_id: str = None,
    file_id: str = None,
    user_context: UserContext = Depends(get_current_user)
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
@require_auth("read", allow_independent=True)
async def get_user_consent_status(user_id: str, user_context: UserContext = Depends(get_current_user)):
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
@require_auth("read", allow_independent=True)
async def get_federated_learning_consent_terms(user_context: UserContext = Depends(get_current_user)):
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
@require_auth("read", allow_independent=True)
async def get_digital_twins_by_federated_status(participation_status: str, user_context: UserContext = Depends(get_current_user)):
    """Get digital twins by federated participation status"""
    try:
        twins = digital_twin_service.get_repository().get_federated_twins(participation_status)
        twin_data = [twin.to_dict() for twin in twins]
        return {"success": True, "data": twin_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/digital-twins/{twin_id}/federated-learning")
@require_auth("write", allow_independent=True)
async def update_digital_twin_federated_learning(twin_id: str, federated_data: Dict[str, Any], user_context: UserContext = Depends(get_current_user)):
    """Update federated learning settings for a digital twin"""
    try:
        success = digital_twin_service.get_repository().update_federated_metadata(twin_id, federated_data)
        if success:
            return {"success": True, "message": "Digital twin federated learning settings updated"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update federated learning settings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 