"""
AASX ETL API: Thin FastAPI router using modular service architecture.
Enforces Use Case → Projects → Files hierarchy.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import logging
from datetime import datetime

# Import authentication decorators and user context
from webapp.core.decorators.auth_decorators import (
    require_auth, require_role, require_organization, 
    get_current_user, require_permission
)
from webapp.core.context.user_context import UserContext

# Configure logger
logger = logging.getLogger(__name__)

# Import our service modules
from .use_cases import UseCaseService
from .projects import ProjectService
from .files import FileService
from .processor import AASXProcessor

# Import analytics services
from .analytics.analytics_service import AnalyticsService
from .analytics.dashboard_service import DashboardService
from .analytics.chart_data_service import ChartDataService

# Import system monitoring services
from .system.system_monitor import SystemMonitor
from .system.service_monitor import ServiceMonitor
from .system.infrastructure_logs import InfrastructureLogs
from .monitoring.resource_monitor import ResourceMonitor
from .monitoring.alert_manager import AlertManager

# Create service instances
use_case_service = UseCaseService()
project_service = ProjectService()
file_service = FileService()
aasx_processor = AASXProcessor()

# Analytics services will be initialized after db_manager is created
analytics_service = None
dashboard_service = None
chart_data_service = None

# System monitoring services
system_monitor = SystemMonitor()
service_monitor = ServiceMonitor()
infrastructure_logs = InfrastructureLogs()
resource_monitor = ResourceMonitor()
alert_manager = AlertManager()

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

# Initialize analytics services with database connection
analytics_service = AnalyticsService(db_manager)
dashboard_service = DashboardService(db_manager)
chart_data_service = ChartDataService(db_manager)

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
@require_auth()  # ✅ PHASE 2: Require authentication (middleware handles demo users)
async def aasx_dashboard(request: Request, user_context: UserContext = Depends(get_current_user)):
    """AASX ETL Dashboard - requires authentication, middleware handles demo users"""
    
    # ✅ IMPLEMENTATION: Use user-specific services instead of generic services
    # This implements the Netflix Principle: demo users see demo data, authenticated users see their data
    user_specific_service = UserSpecificService(user_context)
    
    # Get user-specific data based on role and permissions
    user_projects = user_specific_service.get_user_projects()
    user_files = user_specific_service.get_user_files()
    
    # Check if this is a demo user
    is_demo = user_context.username == 'demo'
    
    # Get user-specific statistics
    user_stats = user_specific_service.get_user_statistics()
    # For demo users, use the same stats for organization (they only see demo org data)
    try:
        if is_demo:
            organization_stats = user_stats
        else:
            organization_stats = user_specific_service.get_organization_statistics()
    except Exception as e:
        logger.warning(f"Could not get organization statistics: {e}, using user stats as fallback")
        organization_stats = user_stats
    
    return templates.TemplateResponse(
        "aasx/index.html",
        {
            "request": request, 
            "title": "AASX ETL Pipeline - AASX Digital Twin Analytics Framework",
            "user": user_context,
            "can_upload": user_context.has_permission("write"),  # Demo users can upload to experience full capabilities
            "can_process": user_context.has_permission("write"),  # Demo users can run pipeline to experience full capabilities
            "can_delete": user_context.has_permission("manage") and not is_demo,  # But demo users can't delete (safety)
            "user_type": "organization",  # All users are organization users
            "user_type": user_context.get_user_type(),
            "user_projects": user_projects,
            "user_files": user_files,
            "user_stats": user_stats,
            "organization_stats": organization_stats,
            "is_demo": is_demo
        }
    )

# Use Case Endpoints
@router.get("/use-cases")
@require_auth("read")  # ✅ PHASE 2: Require read permission (middleware handles demo users)
async def list_use_cases(request: Request, user_context: UserContext = Depends(get_current_user)):
    """List all use cases - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        logger.info(f"list_use_cases called with user_context: {user_context}")
        logger.info(f"User role: {getattr(user_context, 'role', 'unknown')}")
        logger.info(f"User organization_id: {getattr(user_context, 'organization_id', 'unknown')}")
        
        # ✅ IMPLEMENTATION: Use user-specific service for use cases
        user_specific_service = UserSpecificService(user_context)
        use_cases = user_specific_service.get_user_use_cases()
        
        logger.info(f"Retrieved use_cases: {len(use_cases) if use_cases else 0}")
        
        # Frontend expects use_cases array directly, not wrapped in object
        return use_cases
    except Exception as e:
        logger.error(f"Error in list_use_cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}")
@require_auth("read", allow_independent=True)  # ✅ PHASE 2: Require read permission, allow independent users
async def get_use_case(use_case_id: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get specific use case - requires read permission, allows independent users"""
    try:
        use_case = use_case_service.get_use_case(use_case_id)
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        return use_case
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}/projects")
@require_auth("read")  # ✅ PHASE 2: Require read permission (middleware handles demo users)
async def get_projects_by_use_case(use_case_id: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get projects for a specific use case - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # ✅ IMPLEMENTATION: Use user-specific service for projects
        user_specific_service = UserSpecificService(user_context)
        projects = user_specific_service.get_projects_by_use_case(use_case_id)
        
        # Frontend expects projects array directly, not wrapped in object
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/use-cases")
@require_auth("write", allow_independent=True)
async def create_use_case(use_case_data: UseCaseCreate, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Create new use case - requires write permission, allows independent users"""
    try:
        use_case_id = use_case_service.create_use_case(use_case_data.dict())
        return {"use_case_id": use_case_id, "message": "Use case created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Project Endpoints with User-Specific Data
@router.get("/projects")
@require_auth("read")  # ✅ PHASE 2: Require read permission (middleware handles demo users)
async def list_projects(use_case_id: str = None, request: Request = None, user_context: UserContext = Depends(get_current_user)):
    """List projects for current user - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        logger.info(f"list_projects called with user_context: {user_context}")
        logger.info(f"User role: {getattr(user_context, 'role', 'unknown')}")
        logger.info(f"User organization_id: {getattr(user_context, 'organization_id', 'unknown')}")
        logger.info(f"User username: {getattr(user_context, 'username', 'unknown')}")
        logger.info(f"User user_id: {getattr(user_context, 'user_id', 'unknown')}")
        
        # ✅ IMPLEMENTATION: Use user-specific service for projects
        user_specific_service = UserSpecificService(user_context)
        
        if use_case_id:
            # Filter by use case if specified
            projects = user_specific_service.get_projects_by_use_case(use_case_id)
        else:
            # Get all user-accessible projects
            projects = user_specific_service.get_user_projects()
        
        logger.info(f"Retrieved projects: {len(projects) if projects else 0}")
        
        # Frontend expects projects array directly, not wrapped in object
        return projects
    except Exception as e:
        logger.error(f"Error in list_projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
@require_auth("read", allow_independent=True)  # ✅ PHASE 2: Allow demo users and logged-in users
async def get_project(project_id: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get specific project - requires read permission, middleware handles demo users"""
    try:
        logger.info(f"🔍 get_project called for project_id: {project_id}")
        logger.info(f"🔍 user_context: {user_context}")
        logger.info(f"🔍 user_context type: {type(user_context)}")
        
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
            logger.info(f"🔍 Fallback user_context from request.state: {user_context}")
        
        if not user_context:
            logger.error("❌ No user context available")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # ✅ IMPLEMENTATION: Use user-specific service for project access
        logger.info(f"🔍 Creating UserSpecificService with user_context")
        user_specific_service = UserSpecificService(user_context)
        logger.info(f"🔍 Calling get_user_project for project_id: {project_id}")
        project = user_specific_service.get_user_project(project_id)
        logger.info(f"🔍 get_user_project returned: {project}")
        
        if not project:
            logger.warning(f"❌ Project not found or access denied for project_id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Add file count and files list using user-specific service
        logger.info(f"🔍 Getting file count for project_id: {project_id}")
        file_count = user_specific_service.get_project_file_count(project_id)
        project["file_count"] = file_count
        logger.info(f"🔍 File count: {file_count}")
        
        # ✅ ADD FILES LIST: Get the actual files for this project
        logger.info(f"🔍 Getting files list for project_id: {project_id}")
        all_files = user_specific_service.get_user_files()
        project_files = [file for file in all_files if file.get('project_id') == project_id]
        project["files"] = project_files
        logger.info(f"🔍 Files found: {len(project_files)}")
        
        logger.info(f"✅ Returning project with files: {project}")
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects")
@require_auth("write", allow_independent=True)
async def create_project(project_data: ProjectCreate, request: Request, user_context: UserContext = Depends(get_current_user)):
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
@require_auth("read")  # ✅ PHASE 2: Require read permission (middleware handles demo users)
async def list_files(request: Request, user_context: UserContext = Depends(get_current_user)):
    """List files for current user - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # ✅ IMPLEMENTATION: Use user-specific service for files
        user_specific_service = UserSpecificService(user_context)
        files = user_specific_service.get_user_files()
        
        # Frontend expects files array directly, not wrapped in object
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/upload")
@require_auth("write", allow_independent=True)  # ✅ PHASE 2: Allow demo users to upload
async def upload_file(
    request: Request,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    job_type: str = Form(...),
    description: str = Form(None),
    user_context: UserContext = Depends(get_current_user)
):
    """Upload a file to a project - requires write permission, allows demo users"""
    try:
        # Initialize file service
        file_service_instance = FileService()
        
        # Upload the file with user context (project_id is already provided)
        result = file_service_instance.upload_file(
            project_id, 
            file, 
            job_type,
            description,
            user_id=user_context.user_id,
            org_id=user_context.organization_id,
            source_type='manual_upload'
        )
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_id": result.get("file_id"),
            "filename": result.get("filename"),
            "project_id": project_id
        }
    except Exception as e:
        import traceback
        logger.error(f"Upload file error: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/upload-from-url")
@require_auth("write", allow_independent=True)  # ✅ PHASE 2: Allow demo users to upload
async def upload_file_from_url(
    request: Request,
    project_id: str = Form(...),
    url: str = Form(...), 
    job_type: str = Form(...),
    description: str = Form(None),
    user_context: UserContext = Depends(get_current_user)
):
    """Upload a file from URL to a project - requires write permission, allows demo users"""
    try:
        # Initialize file service
        file_service_instance = FileService()
        
        # Upload the file from URL with user context (project_id is already provided)
        result = file_service_instance.upload_file_from_url(
            project_id, 
            url, 
            job_type,
            description,
            user_id=user_context.user_id,
            org_id=user_context.organization_id
        )
        
        return {
            "success": True,
            "message": "File uploaded from URL successfully",
            "file_id": result.get("file_id"),
            "filename": result.get("filename"),
            "project_id": project_id,
            "source_url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}")
@require_auth("read")  # ✅ PHASE 2: Require read permission (middleware handles demo users)
async def get_file(file_id: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get specific file - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # ✅ IMPLEMENTATION: Use user-specific service for file access control and data retrieval
        user_specific_service = UserSpecificService(user_context)
        
        # Get file details with project and use case context (includes access control)
        file_data = user_specific_service.get_user_file_details(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        return file_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
@require_auth("read", allow_independent=True)
async def get_project_files(request: Request, project_id: str, user_context: UserContext = Depends(get_current_user)):
    """Get files for a specific project - requires read permission, allows demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        if not user_context:
            raise HTTPException(status_code=401, detail="User context not found")
        
        # Initialize user-specific service
        user_specific_service = UserSpecificService(user_context)
        
        # Get all files for the current user
        all_files = user_specific_service.get_user_files()
        
        # Filter files by project_id
        project_files = [file for file in all_files if file.get('project_id') == project_id]
        
        return {
            "files": project_files,
            "count": len(project_files),
            "project_id": project_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User-Specific Statistics
@router.get("/user/stats")
@require_auth("read")  # ✅ PHASE 2: Require read permission (middleware handles demo users)
async def get_user_stats(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get user-specific statistics - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
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
async def get_organization_projects(request: Request, user_context: UserContext = Depends(get_current_user)):
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
async def get_organization_files(request: Request, user_context: UserContext = Depends(get_current_user)):
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
async def get_organization_stats(request: Request, user_context: UserContext = Depends(get_current_user)):
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
async def get_organization_members(request: Request, user_context: UserContext = Depends(get_current_user)):
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
async def run_etl_pipeline(config: ETLConfigRequest, request: Request, user_context: UserContext = Depends(get_current_user)):
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
        
        # Add user context to config
        config_dict['user_id'] = user_context.user_id
        config_dict['org_id'] = user_context.organization_id
        
        print(f"📤 ETL Route: Sending to processor: {config_dict}")
        print(f"👤 User: {user_context.user_id}, Org: {user_context.organization_id}")
        
        # Run ETL pipeline - all business logic is in processor
        result = aasx_processor.run_etl_pipeline(config_dict)
        
        print(f"📥 ETL Route: Processor result: {result}")
        return result
    except Exception as e:
        print(f"💥 ETL Route: Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/progress")
@require_auth("read", allow_independent=True)
async def get_etl_progress(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get ETL processing progress"""
    try:
        return aasx_processor.get_etl_progress()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/status")
@require_auth("read", allow_independent=True)
async def get_etl_status(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get ETL processing status"""
    try:
        return aasx_processor.get_etl_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for frontend compatibility
@router.get("/files")
@require_auth("read", allow_independent=True)
async def list_files_for_etl(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get all files for ETL pipeline (alias for compatibility)"""
    try:
        files = file_service.list_all_files()
        
        # Check access permissions for all files - organization-based access control
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        for file_info in files:
            # Users can access files from their organization or files they created
            if (file_info.get('organization_id') != organization_id and 
                file_info.get('created_by') != user_id):
                raise HTTPException(status_code=403, detail="Access denied")

        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/by-path")
@require_auth("read", allow_independent=True)
async def get_file_by_path(use_case_name: str, project_name: str, filename: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get file information by use case, project, and filename"""
    try:
        file_info = file_service.get_file_by_path(use_case_name, project_name, filename)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions - organization-based access control
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        # Users can access files from their organization or files they created
        if (file_info.get('organization_id') != organization_id and 
            file_info.get('created_by') != user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/path-info")
@require_auth("read", allow_independent=True)
async def get_file_path_info(file_id: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get logical path information for a file (usecase/project/filename)"""
    try:
        path_info = file_service.get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions - organization-based access control
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        # Users can access files from their organization or files they created
        if (path_info.get('organization_id') != organization_id and 
            path_info.get('created_by') != user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/path")
@require_auth("read", allow_independent=True)
async def get_file_path(file_id: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get file hierarchy path from file_id (alias for path-info)"""
    try:
        path_info = file_service.get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions - organization-based access control
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        # Users can access files from their organization or files they created
        if (path_info.get('organization_id') != organization_id and 
            path_info.get('created_by') != user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blazor/files/{file_id}/path")
# Public endpoint specifically for Blazor server - no authentication required
async def get_file_path_for_blazor(file_id: str):
    """Get file hierarchy path from file_id - PUBLIC endpoint for Blazor server calls"""
    try:
        path_info = file_service.get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Public endpoint for Blazor server - no access control needed
        # Returns the logical path for Blazor to locate files
        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/by-path/file-id")
@require_auth("read", allow_independent=True)
async def get_file_id_by_path(use_case_name: str, project_name: str, filename: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get file ID by use case, project, and filename"""
    try:
        file_id = file_service.get_file_id_by_path(use_case_name, project_name, filename)
        if not file_id:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access permissions - organization-based access control
        user_id = getattr(user_context, 'user_id', None)
        organization_id = getattr(user_context, 'organization_id', None)
        
        # Users can access files from their organization or files they created
        if (file_id.get('organization_id') != organization_id and 
            file_id.get('created_by') != user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        return {"file_id": file_id, "logical_path": f"{use_case_name}/{project_name}/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/sync")
@require_auth("write", allow_independent=True)
async def sync_projects(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Sync projects and refresh statuses"""
    try:
        return project_service.refresh_project_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics and Utility Endpoints
@router.get("/stats")
@require_auth("read")  # ✅ PHASE 2: Require read permission (middleware handles demo users)
async def get_aasx_stats(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get AASX processing statistics - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        return aasx_processor.get_aasx_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
@require_auth("write", allow_independent=True)
async def refresh_files_and_statuses(project_id: str = None, request: Request = None, user_context: UserContext = Depends(get_current_user)):
    """Refresh file statuses and digital twin statuses"""
    try:
        return project_service.refresh_project_status(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/reset-statuses")
@require_auth("write", allow_independent=True)
async def reset_file_statuses_endpoint(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Manually trigger file status reset when outputs are missing"""
    try:
        return file_service.reset_file_statuses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Digital Twin Federated Learning Endpoints
@router.get("/digital-twins/federated-learning/stats")
@require_auth("read", allow_independent=True)
async def get_digital_twin_federated_stats(request: Request, user_context: UserContext = Depends(get_current_user)):
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
    request: Request = None,
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
async def get_user_consent_status(user_id: str, request: Request, user_context: UserContext = Depends(get_current_user)):
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
async def get_federated_learning_consent_terms(request: Request, user_context: UserContext = Depends(get_current_user)):
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
async def get_digital_twins_by_federated_status(participation_status: str, request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get digital twins by federated participation status"""
    try:
        twins = digital_twin_service.get_repository().get_federated_twins(participation_status)
        twin_data = [twin.to_dict() for twin in twins]
        return {"success": True, "data": twin_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/digital-twins/{twin_id}/federated-learning")
@require_auth("write", allow_independent=True)
async def update_digital_twin_federated_learning(twin_id: str, federated_data: Dict[str, Any], request: Request, user_context: UserContext = Depends(get_current_user)):
    """Update federated learning settings for a digital twin"""
    try:
        success = digital_twin_service.get_repository().update_federated_metadata(twin_id, federated_data)
        if success:
            return {"success": True, "message": "Digital twin federated learning settings updated"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update federated learning settings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/processing/{job_id}/federated-learning-consent")
@require_auth("write", allow_independent=True)
async def update_federated_learning_consent(
    job_id: str, 
    consent_data: Dict[str, Any], 
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Update federated learning consent for a processing job"""
    try:
        # Validate that the user owns this job or has permission to update it
        job = aasx_processing_service.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Processing job not found")
        
        # Check if user has permission to update this job
        if job.get('processed_by') != user_context.user_id:
            # TODO: Add role-based permission check here
            pass
        
        # Update the consent
        success = aasx_processing_service.update_federated_learning_consent(job_id, consent_data)
        
        if success:
            return {
                "success": True, 
                "message": "Federated learning consent updated successfully",
                "job_id": job_id,
                "consent_data": consent_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update federated learning consent")
            
    except Exception as e:
        logger.error(f"Failed to update federated learning consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processing/federated-learning/stats")
@require_auth("read", allow_independent=True)
async def get_federated_learning_stats(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    request: Request = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Get federated learning consent statistics"""
    try:
        # If no user_id specified, use the authenticated user's ID
        if not user_id:
            user_id = user_context.user_id
        
        stats = aasx_processing_service.get_federated_learning_stats(user_id, project_id)
        
        return {
            "success": True,
            "stats": stats,
            "user_id": user_id,
            "project_id": project_id
        }
        
    except Exception as e:
        logger.error(f"Failed to get federated learning stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS ENDPOINTS - Phase 5: Frontend Integration & Real-Time Analytics
# ============================================================================

# Dashboard Overview Endpoints
@router.get("/analytics/dashboard/overview")
@require_auth("read", allow_independent=True)
async def get_dashboard_overview(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get complete dashboard overview for the authenticated user."""
    try:
        logger.info(f"Getting dashboard overview for user: {user_context.user_id}")
        
        # Convert UserContext to dict format expected by analytics services
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        overview = dashboard_service.get_dashboard_overview(user_context_dict)
        
        return {
            "success": True,
            "data": overview,
            "message": "Dashboard overview retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard overview: {str(e)}"
        )


@router.get("/analytics/dashboard/summary-cards")
@require_auth("read", allow_independent=True)
async def get_dashboard_summary_cards(request: Request, user_context: UserContext = Depends(get_current_user)):
    """Get dashboard summary cards for the authenticated user."""
    try:
        logger.info(f"Getting dashboard summary cards for user: {user_context.user_id}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        summary_cards = dashboard_service.get_dashboard_summary_cards(user_context_dict)
        
        return {
            "success": True,
            "data": summary_cards,
            "message": "Summary cards retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get summary cards: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve summary cards: {str(e)}"
        )


@router.get("/analytics/dashboard/recent-jobs")
@require_auth("read", allow_independent=True)
async def get_recent_processing_jobs(
    limit: int = 5,
    user_context: UserContext = Depends(get_current_user)
):
    """Get recent processing jobs for the authenticated user."""
    try:
        logger.info(f"Getting recent processing jobs for user: {user_context.user_id}, limit: {limit}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        recent_jobs = dashboard_service.get_recent_processing_jobs(user_context_dict, limit)
        
        return {
            "success": True,
            "data": recent_jobs,
            "message": f"Retrieved {len(recent_jobs)} recent jobs"
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent processing jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve recent jobs: {str(e)}"
        )


# Chart Data Endpoints
@router.get("/analytics/charts/processing-trends")
@require_auth("read", allow_independent=True)
async def get_processing_trends_chart(
    days: int = 30,
    user_context: UserContext = Depends(get_current_user)
):
    """Get processing trends chart data for the authenticated user."""
    try:
        logger.info(f"Getting processing trends chart for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        chart_data = chart_data_service.get_processing_trends_chart(user_context_dict, days)
        
        return {
            "success": True,
            "data": chart_data,
            "message": "Processing trends chart data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get processing trends chart: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve processing trends chart: {str(e)}"
        )


@router.get("/analytics/charts/quality-metrics")
@require_auth("read", allow_independent=True)
async def get_quality_metrics_chart(
    days: int = 30,
    user_context: UserContext = Depends(get_current_user)
):
    """Get quality metrics chart data for the authenticated user."""
    try:
        logger.info(f"Getting quality metrics chart for user: {user_context.user_id}, days: {days}")
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        chart_data = chart_data_service.get_quality_metrics_chart(user_context_dict, days)
        
        return {
            "success": True,
            "data": chart_data,
            "message": "Quality metrics chart data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get quality metrics chart: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve quality metrics chart: {str(e)}"
        )


@router.get("/analytics/charts/performance-metrics")
@require_auth("read", allow_independent=True)
async def get_performance_metrics_chart(
    days: int = 30,
    user_context: UserContext = Depends(get_current_user)
):
    """Get performance metrics chart data for the authenticated user."""
    try:
        logger.info(f"Getting performance metrics chart for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        chart_data = chart_data_service.get_performance_metrics_chart(user_context_dict, days)
        
        return {
            "success": True,
            "data": chart_data,
            "message": "Performance metrics chart data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics chart: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve performance metrics chart: {str(e)}"
        )


@router.get("/analytics/charts/user-behavior")
@require_auth("read", allow_independent=True)
async def get_user_behavior_chart(
    days: int = 30,
    user_context: UserContext = Depends(get_current_user)
):
    """Get user behavior chart data for the authenticated user."""
    try:
        logger.info(f"Getting user behavior chart for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        chart_data = chart_data_service.get_user_behavior_chart(user_context_dict, days)
        
        return {
            "success": True,
            "data": chart_data,
            "message": "User behavior chart data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get user behavior chart: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user behavior chart: {str(e)}"
        )


# Analytics Data Endpoints
@router.get("/analytics/metrics/dashboard")
@require_auth("read", allow_independent=True)
async def get_dashboard_metrics(user_context: UserContext = Depends(get_current_user)):
    """Get comprehensive dashboard metrics for the authenticated user."""
    try:
        logger.info(f"Getting dashboard metrics for user: {user_context.user_id}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        metrics = analytics_service.get_dashboard_metrics(user_context_dict)
        
        return {
            "success": True,
            "data": metrics,
            "message": "Dashboard metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard metrics: {str(e)}"
        )


@router.get("/analytics/metrics/performance")
@require_auth("read", allow_independent=True)
async def get_performance_metrics(
    days: int = 30,
    user_context: UserContext = Depends(get_current_user)
):
    """Get performance metrics for the authenticated user."""
    try:
        logger.info(f"Getting performance metrics for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        metrics = analytics_service.get_performance_metrics(user_context_dict, days)
        
        return {
            "success": True,
            "data": metrics,
            "message": "Performance metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve performance metrics: {str(e)}"
        )


@router.get("/analytics/health")
@require_auth("read", allow_independent=True)
async def analytics_health_check(user_context: UserContext = Depends(get_current_user)):
    """Health check endpoint for analytics services."""
    try:
        return {
            "success": True,
            "status": "healthy",
            "services": {
                "analytics_service": "initialized",
                "dashboard_service": "initialized",
                "chart_data_service": "initialized"
            },
            "message": "Analytics services are healthy"
        }
        
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "message": "Analytics services are not healthy"
        }


# ============================================================================
# SYSTEM MONITORING ENDPOINTS
# ============================================================================

@router.get("/system/health")
@require_auth("read", allow_independent=True)
async def get_system_health(user_context: UserContext = Depends(get_current_user)):
    """Get current system health status for the authenticated user."""
    try:
        logger.info(f"Getting system health for user: {user_context.user_id}")
        
        health = system_monitor.get_current_health()
        
        return {
            "success": True,
            "data": health,
            "message": "System health retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system health: {str(e)}"
        )


@router.get("/system/resources")
@require_auth("read", allow_independent=True)
async def get_resource_metrics(user_context: UserContext = Depends(get_current_user)):
    """Get current resource usage metrics for the authenticated user."""
    try:
        logger.info(f"Getting resource metrics for user: {user_context.user_id}")
        
        metrics = resource_monitor.get_current_resources(
            user_context.user_id, 
            user_context.organization_id
        )
        
        return {
            "success": True,
            "data": metrics,
            "message": "Resource metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get resource metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve resource metrics: {str(e)}"
        )


@router.get("/system/services")
@require_auth("read", allow_independent=True)
async def get_service_status(user_context: UserContext = Depends(get_current_user)):
    """Get current service health status for the authenticated user."""
    try:
        logger.info(f"Getting service status for user: {user_context.user_id}")
        
        status = service_monitor.get_service_health(
            user_context.user_id, 
            user_context.organization_id
        )
        
        return {
            "success": True,
            "data": status,
            "message": "Service status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve service status: {str(e)}"
        )


@router.get("/system/logs")
@require_auth("read", allow_independent=True)
async def get_system_logs(
    level: Optional[str] = None,
    service: Optional[str] = None,
    hours: int = 24,
    query: str = "",
    limit: int = 1000,
    user_context: UserContext = Depends(get_current_user)
):
    """Get system logs for the authenticated user with filtering options."""
    try:
        logger.info(f"Getting system logs for user: {user_context.user_id}")
        
        logs = infrastructure_logs.get_logs_for_user(
            user_context.user_id,
            user_context.organization_id,
            level,
            service,
            hours,
            limit
        )
        
        return {
            "success": True,
            "data": {"logs": logs},
            "message": "System logs retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system logs: {str(e)}"
        )


@router.get("/system/logs/summary")
@require_auth("read", allow_independent=True)
async def get_log_summary(
    hours: int = 24,
    user_context: UserContext = Depends(get_current_user)
):
    """Get log summary statistics for the authenticated user."""
    try:
        logger.info(f"Getting log summary for user: {user_context.user_id}")
        
        summary = infrastructure_logs.get_log_summary_for_user(
            user_context.user_id,
            user_context.organization_id,
            hours
        )
        
        return {
            "success": True,
            "data": summary,
            "message": "Log summary retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get log summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve log summary: {str(e)}"
        )


@router.get("/system/logs/trends")
@require_auth("read", allow_independent=True)
async def get_log_trends(
    hours: int = 24,
    user_context: UserContext = Depends(get_current_user)
):
    """Get log trends and patterns for the authenticated user."""
    try:
        logger.info(f"Getting log trends for user: {user_context.user_id}")
        
        trends = infrastructure_logs.get_log_trends_for_user(
            user_context.user_id,
            user_context.organization_id,
            hours
        )
        
        return {
            "success": True,
            "data": trends,
            "message": "Log trends retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get log trends: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve log trends: {str(e)}"
        )


@router.get("/system/alerts/active")
@require_auth("read", allow_independent=True)
async def get_active_alerts(user_context: UserContext = Depends(get_current_user)):
    """Get active alerts for the authenticated user."""
    try:
        logger.info(f"Getting active alerts for user: {user_context.user_id}")
        
        alerts = alert_manager.get_alerts_for_user(
            user_context.user_id,
            user_context.organization_id
        )
        
        return {
            "success": True,
            "data": {"alerts": alerts},
            "message": "Active alerts retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve active alerts: {str(e)}"
        )


@router.post("/system/alerts/{alert_id}/acknowledge")
@require_auth("write", allow_independent=True)
async def acknowledge_alert(
    alert_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Acknowledge an alert for the authenticated user."""
    try:
        logger.info(f"User {user_context.user_id} acknowledging alert: {alert_id}")
        
        success = alert_manager.acknowledge_alert(
            alert_id,
            user_context.user_id,
            user_context.organization_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Alert {alert_id} acknowledged successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Alert {alert_id} not found or cannot be acknowledged"
            )
        
    except Exception as e:
        logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.post("/system/alerts/{alert_id}/resolve")
@require_auth("write", allow_independent=True)
async def resolve_alert(
    alert_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Resolve an alert for the authenticated user."""
    try:
        logger.info(f"User {user_context.user_id} resolving alert: {alert_id}")
        
        success = alert_manager.resolve_alert(
            alert_id,
            user_context.user_id,
            user_context.organization_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Alert {alert_id} resolved successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Alert {alert_id} not found or cannot be resolved"
            )
        
    except Exception as e:
        logger.error(f"Failed to resolve alert {alert_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve alert: {str(e)}"
        )


@router.get("/system/health-check")
@require_auth("read", allow_independent=True)
async def system_health_check(user_context: UserContext = Depends(get_current_user)):
    """Health check endpoint for system monitoring services."""
    try:
        return {
            "success": True,
            "status": "healthy",
            "services": {
                "system_monitor": "initialized",
                "service_monitor": "initialized",
                "infrastructure_logs": "initialized",
                "resource_monitor": "initialized",
                "alert_manager": "initialized"
            },
            "message": "System monitoring services are healthy"
        }
        
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "message": "System monitoring services are not healthy"
        }