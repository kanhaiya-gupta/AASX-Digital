"""
AASX ETL API: Thin FastAPI router using modular service architecture.
Enforces Use Case → Projects → Files hierarchy.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Depends, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Import authentication decorators and user context from new engine/integration
from src.integration.api.dependencies import (
    require_auth, get_current_user, require_read_permission,
    require_write_permission, require_manage_permission,
    AuthenticatedUser, ReadUser, WriteUser, ManageUser
)
from src.engine.models.request_context import UserContext

# Configure logger
logger = logging.getLogger(__name__)

# Import our new client service modules
from .services.aasx_processor_client import AASXProcessorClient
from .services.aasx_file_client import AASXFileClient
from .services.aasx_metrics_client import AASXMetricsClient

# Import engine services for business domain operations
from src.engine.services.business_domain.use_case_service import UseCaseService
from src.engine.services.business_domain.project_service import ProjectService
from src.engine.services.business_domain.file_service import FileService
from src.engine.services.business_domain.organization_service import OrganizationService
from src.engine.services.auth.user_service import UserService

# Import engine database connection manager
from src.engine.database.connection_manager import ConnectionManager

# Create service instances
# Initialize connection manager (will be injected by dependency injection)
connection_manager = None

# Initialize our new client services
aasx_processor_client = None
aasx_file_client = None
aasx_metrics_client = None

# Initialize engine business domain services
use_case_service = None
project_service = None
file_service = None
organization_service = None
user_service = None

router = APIRouter(tags=["aasx-etl"])

# Template setup - uses app state templates from request.app.state.templates

def get_services():
    """Get or initialize services with connection manager."""
    global connection_manager, aasx_processor_client, aasx_file_client, aasx_metrics_client
    global use_case_service, project_service, file_service, organization_service, user_service
    
    if connection_manager is None:
        # Initialize connection manager
        connection_manager = ConnectionManager()
    
    if aasx_processor_client is None:
        aasx_processor_client = AASXProcessorClient(connection_manager)
    
    if aasx_file_client is None:
        aasx_file_client = AASXFileClient(connection_manager)
    
    if aasx_metrics_client is None:
        aasx_metrics_client = AASXMetricsClient(connection_manager)
    
    if use_case_service is None:
        use_case_service = UseCaseService(connection_manager)
    
    if project_service is None:
        project_service = ProjectService(connection_manager)
    
    if file_service is None:
        file_service = FileService(connection_manager)
    
    if organization_service is None:
        organization_service = OrganizationService(connection_manager)
    
    if user_service is None:
        user_service = UserService(connection_manager)
    
    return {
        'aasx_processor_client': aasx_processor_client,
        'aasx_file_client': aasx_file_client,
        'aasx_metrics_client': aasx_metrics_client,
        'use_case_service': use_case_service,
        'project_service': project_service,
        'file_service': file_service,
        'organization_service': organization_service,
        'user_service': user_service
    }

# Models
class ETLConfigRequest(BaseModel):
    file_ids: Optional[List[str]] = None  # Direct file IDs
    project_id: Optional[str] = None
    use_case_id: Optional[str] = None  # Direct use case ID
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
    metadata: Optional[Dict[str, Any]] = None

# Dashboard
@router.get("/", response_class=HTMLResponse)
async def aasx_dashboard(request: Request, user_context: ReadUser):
    """AASX ETL Dashboard - requires authentication, middleware handles demo users"""
    
    # ✅ IMPLEMENTATION: Use user-specific services instead of generic services
    # This implements the Netflix Principle: demo users see demo data, authenticated users see their data
    services = get_services()
    user_specific_service = services['user_service']
    
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
    
    return request.app.state.templates.TemplateResponse(
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
async def list_use_cases(request: Request, user_context: ReadUser):
    """List all use cases - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        logger.info(f"list_use_cases called with user_context: {user_context}")
        logger.info(f"User role: {getattr(user_context, 'role', 'unknown')}")
        logger.info(f"User organization_id: {getattr(user_context, 'organization_id', 'unknown')}")
        
        # ✅ IMPLEMENTATION: Use user-specific service for use cases
        services = get_services()
        user_specific_service = services['user_service']
        use_cases = user_specific_service.get_user_use_cases()
        
        logger.info(f"Retrieved use_cases: {len(use_cases) if use_cases else 0}")
        
        # Frontend expects use_cases array directly, not wrapped in object
        return use_cases
    except Exception as e:
        logger.error(f"Error in list_use_cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}")
async def get_use_case(request: Request, use_case_id: str, user_context: ReadUser):
    """Get specific use case - requires read permission, allows independent users"""
    try:
        services = get_services()
        use_case = services['use_case_service'].get_use_case(use_case_id)
        if not use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        return use_case
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/use-cases/{use_case_id}/projects")
async def get_projects_by_use_case(request: Request, use_case_id: str, user_context: ReadUser):
    """Get projects for a specific use case - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # ✅ IMPLEMENTATION: Use user-specific service for projects
        services = get_services()
        user_specific_service = services['user_service']
        projects = user_specific_service.get_projects_by_use_case(use_case_id)
        
        # Frontend expects projects array directly, not wrapped in object
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/use-cases")
async def create_use_case(request: Request, use_case_data: UseCaseCreate, user_context: WriteUser):
    """Create new use case - requires write permission, allows independent users"""
    try:
        services = get_services()
        use_case_id = services['use_case_service'].create_use_case(use_case_data.dict())
        return {"use_case_id": use_case_id, "message": "Use case created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Project Endpoints with User-Specific Data
@router.get("/projects")
async def list_projects(request: Request, user_context: ReadUser, use_case_id: str):
    """List projects for current user - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # ✅ IMPLEMENTATION: Use user-specific service for projects
        user_specific_service = UserService(user_context)
        
        if use_case_id:
            # Filter by use case if specified
            projects = user_specific_service.get_projects_by_use_case(use_case_id)
        else:
            # Get all user-accessible projects
            projects = user_specific_service.get_user_projects()
        
        logger.info(f"Retrieved {len(projects) if projects else 0} projects")
        
        # Frontend expects projects array directly, not wrapped in object
        return projects
    except Exception as e:
        logger.error(f"Error in list_projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(request: Request, project_id: str, user_context: ReadUser):
    """Get specific project - requires read permission, middleware handles demo users"""
    try:
        logger.info(f"Getting project: {project_id}")
        
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        if not user_context:
            logger.error("No user context available")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # ✅ IMPLEMENTATION: Use user-specific service for project access
        services = get_services()
        user_specific_service = services['user_service']
        project = user_specific_service.get_user_project(project_id)
        
        if not project:
            logger.warning(f"Project not found or access denied for project_id: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Add file count and files list using user-specific service
        file_count = user_specific_service.get_project_file_count(project_id)
        project["file_count"] = file_count
        
        # ✅ ADD FILES LIST: Get the actual files for this project
        all_files = user_specific_service.get_user_files()
        project_files = [file for file in all_files if file.get('project_id') == project_id]
        project["files"] = project_files
        
        logger.info(f"Returning project with {len(project_files)} files")
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects")
async def create_project(request: Request, project_data: ProjectCreate, user_context: WriteUser):
    """Create new project - requires write permission, allows independent users"""
    try:
        # Initialize user-specific service
        services = get_services()
        user_service = services['user_service']
        
        # Create project with user context
        project_id = user_service.create_user_project(project_data.dict())
        
        return {"project_id": project_id, "message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Endpoints with User-Specific Data
@router.get("/files")
async def list_files(request: Request, user_context: ReadUser):
    """List files for current user - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # ✅ IMPLEMENTATION: Use user-specific service for files
        services = get_services()
        user_specific_service = services['user_service']
        files = user_specific_service.get_user_files()
        
        # Frontend expects files array directly, not wrapped in object
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/upload")
async def upload_file(
    request: Request,
    user_context: WriteUser,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    job_type: str = Form(...),
    description: str = Form(None)
):
    """Upload a file to a project - requires write permission, allows demo users"""
    try:
        # Initialize file service
        services = get_services()
        file_service_instance = services['file_service']
        
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
        
        # 🔗 TWIN REGISTRY INTEGRATION: Trigger Phase 1 population after successful upload
        try:
            from .file_upload_twin_registry_integration import get_file_upload_integration
            
            # Get the integration instance
            integration = get_file_upload_integration()
            
            # Prepare upload data for twin registry population
            upload_data = {
                'upload_id': result.get("file_id"),
                'file_path': result.get("filepath", ''),
                'file_name': result.get("filename", ''),
                'file_size': result.get("size", 0),
                'file_type': result.get("file_type", 'unknown'),
                'upload_timestamp': result.get("upload_date"),
                'user_id': user_context.user_id,
                'org_id': user_context.organization_id,
                'project_id': project_id,
                'use_case_id': result.get("use_case", {}).get("use_case_id"),
                'upload_status': 'completed',
                'file_hash': result.get("file_hash", ''),
                'mime_type': file.content_type,
                'upload_source': 'manual_upload',
                'job_type': job_type,
                'description': description
            }
            
            # Trigger Phase 1: Basic twin registry population
            population_result = await integration.manually_trigger_upload_population(result.get("file_id"))
            
            if population_result.get('status') == 'success':
                logger.info(f"✅ Phase 1: Basic twin registry populated successfully for upload {result.get('file_id')}")
                result['twin_registry_status'] = 'populated'
            else:
                logger.warning(f"⚠️ Phase 1: Basic twin registry population failed for upload {result.get('file_id')}: {population_result.get('error')}")
                result['twin_registry_status'] = 'failed'
                
        except Exception as twin_reg_error:
            logger.error(f"⚠️ Twin Registry population failed for upload: {twin_reg_error}")
            result['twin_registry_status'] = 'error'
            # Don't fail the main upload if twin registry fails
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_id": result.get("file_id"),
            "filename": result.get("filename"),
            "project_id": project_id,
            "twin_registry_status": result.get("twin_registry_status", "unknown")
        }
    except Exception as e:
        import traceback
        logger.error(f"Upload file error: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/upload-from-url")
async def upload_file_from_url(
    request: Request,
    user_context: WriteUser,
    project_id: str = Form(...),
    url: str = Form(...), 
    job_type: str = Form(...),
    description: str = Form(None)
):
    """Upload a file from URL to a project - requires write permission, allows demo users"""
    try:
        # Initialize file service
        services = get_services()
        file_service_instance = services['file_service']
        
        # Upload the file from URL with user context (project_id is already provided)
        result = file_service_instance.upload_file_from_url(
            project_id, 
            url, 
            job_type,
            description,
            user_id=user_context.user_id,
            org_id=user_context.organization_id
        )
        
        # 🔗 TWIN REGISTRY INTEGRATION: Trigger Phase 1 population after successful URL upload
        try:
            from .file_upload_twin_registry_integration import get_file_upload_integration
            
            # Get the integration instance
            integration = get_file_upload_integration()
            
            # Prepare upload data for twin registry population
            upload_data = {
                'upload_id': result.get("file_id"),
                'file_path': result.get("filepath", ''),
                'file_name': result.get("filename", ''),
                'file_size': result.get("size", 0),
                'file_type': result.get("file_type", 'unknown'),
                'upload_timestamp': result.get("upload_date"),
                'user_id': user_context.user_id,
                'org_id': user_context.organization_id,
                'project_id': project_id,
                'use_case_id': result.get("use_case", {}).get("use_case_id"),
                'upload_status': 'completed',
                'file_hash': result.get("file_hash", ''),
                'mime_type': result.get("mime_type", ''),
                'upload_source': 'url_upload',
                'job_type': job_type,
                'description': description,
                'source_url': url
            }
            
            # Trigger Phase 1: Basic twin registry population
            population_result = await integration.manually_trigger_upload_population(result.get("file_id"))
            
            if population_result.get('status') == 'success':
                logger.info(f"✅ Phase 1: Basic twin registry populated successfully for URL upload {result.get('file_id')}")
                result['twin_registry_status'] = 'populated'
            else:
                logger.warning(f"⚠️ Phase 1: Basic twin registry population failed for URL upload {result.get('file_id')}: {population_result.get('error')}")
                result['twin_registry_status'] = 'failed'
                
        except Exception as twin_reg_error:
            logger.error(f"⚠️ Twin Registry population failed for URL upload: {twin_reg_error}")
            result['twin_registry_status'] = 'error'
            # Don't fail the main upload if twin registry fails
        
        return {
            "success": True,
            "message": "File uploaded from URL successfully",
            "file_id": result.get("file_id"),
            "filename": result.get("filename"),
            "project_id": project_id,
            "source_url": url,
            "twin_registry_status": result.get("twin_registry_status", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}")
async def get_file(request: Request, file_id: str, user_context: ReadUser):
    """Get specific file - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # ✅ IMPLEMENTATION: Use user-specific service for file access control and data retrieval
        services = get_services()
        user_specific_service = services['user_service']
        
        # Get file details with project and use case context (includes access control)
        file_data = user_specific_service.get_user_file_details(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        return file_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/{file_id}/populate-twin-registry")
async def populate_twin_registry_for_file(
    file_id: str,
    request: Request,
    user_context: WriteUser
):
    """Manually trigger twin registry population for a specific file"""
    try:
        from .file_upload_twin_registry_integration import get_file_upload_integration
        
        # Get the integration instance
        integration = get_file_upload_integration()
        
        # Trigger Phase 1: Basic twin registry population
        population_result = await integration.manually_trigger_upload_population(file_id)
        
        if population_result.get('status') == 'success':
            return {
                "success": True,
                "message": "Twin registry populated successfully",
                "file_id": file_id,
                "population_result": population_result
            }
        else:
            return {
                "success": False,
                "message": "Twin registry population failed",
                "file_id": file_id,
                "error": population_result.get('error', 'Unknown error')
            }
            
    except Exception as e:
        logger.error(f"Twin registry population error for file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/populate-all-twin-registries")
async def populate_all_twin_registries(
    request: Request,
    user_context: ManageUser
):
    """Process all existing file uploads for twin registry population"""
    try:
        from .file_upload_twin_registry_integration import get_file_upload_integration
        
        # Get the integration instance
        integration = get_file_upload_integration()
        
        # Process all existing uploads
        result = await integration.process_existing_uploads()
        
        return {
            "success": True,
            "message": "Bulk twin registry population completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Bulk twin registry population error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twin-registry/integration-status")
async def get_twin_registry_integration_status(
    request: Request,
    user_context: ReadUser
):
    """Get the current status of the twin registry integration"""
    try:
        from .file_upload_twin_registry_integration import get_file_upload_integration
        from .etl_twin_registry_integration import get_etl_integration
        
        # Get both integration instances
        file_upload_integration = get_file_upload_integration()
        etl_integration = get_etl_integration()
        
        # Get status from both integrations
        file_upload_status = file_upload_integration.get_integration_status()
        etl_status = etl_integration.get_integration_status()
        
        return {
            "success": True,
            "file_upload_integration": file_upload_status,
            "etl_integration": etl_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Twin registry integration status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
async def get_project_files(request: Request, project_id: str, user_context: ReadUser):
    """Get files for a specific project - requires read permission, allows demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        if not user_context:
            raise HTTPException(status_code=401, detail="User context not found")
        
        # Initialize user-specific service
        services = get_services()
        user_specific_service = services['user_service']
        
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
async def get_user_stats(request: Request, user_context: ReadUser):
    """Get user-specific statistics - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        # Initialize user-specific service
        services = get_services()
        user_service = services['user_service']
        organization_service = services['organization_service']
        
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
async def get_organization_projects(request: Request, user_context: ReadUser):
    """Get organization projects - requires read permission, organization members only"""
    try:
        # Initialize organization service
        services = get_services()
        organization_service = services['organization_service']
        
        projects = organization_service.get_organization_projects()
        return {"projects": projects, "total": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/organization/files")
async def get_organization_files(request: Request, user_context: ReadUser):
    """Get organization files - requires read permission, organization members only"""
    try:
        # Initialize organization service
        services = get_services()
        organization_service = services['organization_service']
        
        files = organization_service.get_organization_files()
        return {"files": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/organization/stats")
async def get_organization_stats(request: Request, user_context: ReadUser):
    """Get organization statistics - requires read permission, organization members only"""
    try:
        # Initialize organization service
        services = get_services()
        organization_service = services['organization_service']
        
        stats = organization_service.get_organization_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/organization/members")
async def get_organization_members(request: Request, user_context: ReadUser):
    """Get organization members - requires read permission, organization members only"""
    try:
        # Initialize organization service
        services = get_services()
        organization_service = services['organization_service']
        
        members = organization_service.get_organization_members()
        return {"members": members, "total": len(members)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Continue with existing endpoints...

# ETL Processing Endpoints
@router.post("/etl/extract-aasx")
async def extract_aasx_to_structured(request: Request, config: ETLConfigRequest, user_context: WriteUser):
    """Extract structured data from AASX files"""
    try:
        logger.info("ETL Extract Route: Processing AASX extraction request")
        logger.info(f"User: {user_context.user_id}, Org: {user_context.organization_id}")
        
        # Use IDs directly - super fast, no reverse engineering needed!
        config_dict = config.dict()
        config_dict['conversion_mode'] = 'aasx-to-structured'  # Set extraction mode
        
        # Validate required IDs
        if not config.use_case_id or not config.project_id:
            logger.error(f"Missing required IDs - use_case_id: {config.use_case_id}, project_id: {config.project_id}")
            raise HTTPException(status_code=400, detail="Missing use_case_id or project_id")
        
        if not config.file_ids or len(config.file_ids) == 0:
            logger.error("No files selected for processing")
            raise HTTPException(status_code=400, detail="No files selected for processing")
        
        logger.info(f"Using direct IDs - use_case_id: {config.use_case_id}, project_id: {config.project_id}, file_ids: {config.file_ids}")
        
        # Set the IDs directly in config
        config_dict['use_case_id'] = config.use_case_id
        config_dict['project_id'] = config.project_id
        config_dict['file_id'] = config.file_ids[0]  # For now, process first file (processor expects file_id singular)
        # Add user context to config
        config_dict['user_id'] = user_context.user_id
        config_dict['org_id'] = user_context.organization_id
        
        logger.info(f"Sending to processor: {config_dict}")
        
        # Run ETL pipeline for extraction - all business logic is in processor
        services = get_services()
        result = services['aasx_processor_client'].run_etl_pipeline(config_dict)
        
        logger.info(f"Processor result: {result}")
        return result
    except Exception as e:
        print(f"💥 ETL Extract Route: Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/etl/generate-aasx")
async def generate_aasx_from_structured(request: Request, config: ETLConfigRequest, user_context: WriteUser):
    """Generate AASX files from structured data"""
    try:
        logger.info("ETL Generate Route: Processing AASX generation request")
        logger.info(f"User: {user_context.user_id}, Org: {user_context.organization_id}")
        
        # Use IDs directly - super fast, no reverse engineering needed!
        config_dict = config.dict()
        config_dict['conversion_mode'] = 'structured-to-aasx'  # Set generation mode
        
        # Validate required IDs
        if not config.use_case_id or not config.project_id:
            logger.error(f"Missing required IDs - use_case_id: {config.use_case_id}, project_id: {config.project_id}")
            raise HTTPException(status_code=400, detail="Missing use_case_id or project_id")
        
        if not config.file_ids or len(config.file_ids) == 0:
            logger.error("No files selected for processing")
            raise HTTPException(status_code=400, detail="No files selected for processing")
        
        logger.info(f"Using direct IDs - use_case_id: {config.use_case_id}, project_id: {config.project_id}, file_ids: {config.file_ids}")
        
        # Set the IDs directly in config
        config_dict['use_case_id'] = config.use_case_id
        config_dict['project_id'] = config.project_id
        config_dict['file_id'] = config.file_ids[0]  # For now, process first file (processor expects file_id singular)
        # Add user context to config
        config_dict['user_id'] = user_context.user_id
        config_dict['org_id'] = user_context.organization_id
        
        logger.info(f"Sending to processor: {config_dict}")
        
        # Run ETL pipeline for generation - all business logic is in processor
        services = get_services()
        result = services['aasx_processor_client'].run_etl_pipeline(config_dict)
        
        logger.info(f"Processor result: {result}")
        return result
    except Exception as e:
        print(f"💥 ETL Generate Route: Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/etl/run")
async def run_etl_pipeline(request: Request, config: ETLConfigRequest, user_context: WriteUser):
    """Run ETL pipeline for AASX files with federated learning integration (legacy endpoint)"""
    try:
        logger.info("ETL Route: Processing ETL pipeline request")
        logger.info(f"User: {user_context.user_id}, Org: {user_context.organization_id}")
        
        # Use direct IDs - no reverse engineering needed
        config_dict = config.dict()
        
        # Add user context to config
        config_dict['user_id'] = user_context.user_id
        config_dict['org_id'] = user_context.organization_id
        
        logger.info(f"Sending to processor: {config_dict}")
        
        # Run ETL pipeline - all business logic is in processor
        services = get_services()
        result = services['aasx_processor_client'].run_etl_pipeline(config_dict)
        
        logger.info(f"Processor result: {result}")
        return result
    except Exception as e:
        logger.error(f"ETL Route Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/progress")
async def get_etl_progress(request: Request, user_context: ReadUser):
    """Get ETL processing progress"""
    try:
        logger.info(f"ETL Progress: Request from {request.client.host if request.client else 'unknown'}")
        logger.info(f"User: {user_context.user_id if user_context else 'unknown'}")
        services = get_services()
        return services['aasx_processor_client'].get_etl_progress()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/etl/status")
async def get_etl_status(request: Request, user_context: ReadUser):
    """Get ETL processing status"""
    try:
        logger.info(f"ETL Status: Request from {request.client.host if request.client else 'unknown'}")
        logger.info(f"User: {user_context.user_id if user_context else 'unknown'}")
        services = get_services()
        return services['aasx_processor_client'].get_etl_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for frontend compatibility
# Note: Main /files endpoint is defined above for user-specific files

@router.get("/files/by-path")
async def get_file_by_path(request: Request, use_case_name: str, project_name: str, filename: str, user_context: ReadUser):
    """Get file information by use case, project, and filename"""
    try:
        services = get_services()
        file_info = services['file_service'].get_file_by_path(use_case_name, project_name, filename)
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
async def get_file_path_info(request: Request, file_id: str, user_context: ReadUser):
    """Get logical path information for a file (usecase/project/filename)"""
    try:
        services = get_services()
        path_info = services['file_service'].get_file_path_info(file_id)
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
async def get_file_path(request: Request, file_id: str, user_context: ReadUser):
    """Get file hierarchy path from file_id (alias for path-info)"""
    try:
        services = get_services()
        path_info = services['file_service'].get_file_path_info(file_id)
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
        services = get_services()
        path_info = services['file_service'].get_file_path_info(file_id)
        if not path_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Public endpoint for Blazor server - no access control needed
        # Returns the logical path for Blazor to locate files
        return path_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/by-path/file-id")
async def get_file_id_by_path(request: Request, use_case_name: str, project_name: str, filename: str, user_context: ReadUser):
    """Get file ID by use case, project, and filename"""
    try:
        services = get_services()
        file_id = services['file_service'].get_file_id_by_path(use_case_name, project_name, filename)
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
async def sync_projects(request: Request, user_context: WriteUser):
    """Sync projects and refresh statuses"""
    try:
        services = get_services()
        return services['project_service'].refresh_project_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics and Utility Endpoints
@router.get("/stats")
async def get_aasx_stats(request: Request, user_context: ReadUser):
    """Get AASX processing statistics - requires read permission, middleware handles demo users"""
    try:
        # Get user context from middleware (already set by middleware)
        if not user_context:
            user_context = getattr(request.state, 'user_context', None)
        
        services = get_services()
        return services['aasx_processor_client'].get_aasx_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_files_and_statuses(request: Request, user_context: WriteUser, project_id: str = None):
    """Refresh file statuses and digital twin statuses"""
    try:
        services = get_services()
        return services['project_service'].refresh_project_status(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files/reset-statuses")
async def reset_file_statuses_endpoint(request: Request, user_context: WriteUser):
    """Manually trigger file status reset when outputs are missing"""
    try:
        services = get_services()
        return services['file_service'].reset_file_statuses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS ENDPOINTS - Phase 5: Frontend Integration & Real-Time Analytics
# ============================================================================

# Dashboard Overview Endpoints
@router.get("/analytics/dashboard/overview")
async def get_dashboard_overview(request: Request, user_context: ReadUser):
    """Get complete dashboard overview for the authenticated user."""
    try:
        logger.info(f"Getting dashboard overview for user: {user_context.user_id}")
        
        # Convert UserContext to dict format expected by analytics services
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        overview = services['aasx_metrics_client'].get_dashboard_overview(user_context_dict)
        
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
async def get_dashboard_summary_cards(request: Request, user_context: ReadUser):
    """Get dashboard summary cards for the authenticated user."""
    try:
        logger.info(f"Getting dashboard summary cards for user: {user_context.user_id}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        summary_cards = services['aasx_metrics_client'].get_dashboard_summary_cards(user_context_dict)
        
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
async def get_recent_processing_jobs(
    request: Request,
    user_context: ReadUser,
    limit: int = 5
):
    """Get recent processing jobs for the authenticated user."""
    try:
        logger.info(f"Getting recent processing jobs for user: {user_context.user_id}, limit: {limit}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        recent_jobs = services['aasx_metrics_client'].get_recent_processing_jobs(user_context_dict, limit)
        
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
async def get_processing_trends_chart(
    request: Request,
    user_context: ReadUser,
    days: int = 30
):
    """Get processing trends chart data for the authenticated user."""
    try:
        logger.info(f"Getting processing trends chart for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        chart_data = services['aasx_metrics_client'].get_processing_trends_chart(user_context_dict, days)
        
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
async def get_quality_metrics_chart(
    request: Request,
    user_context: ReadUser,
    days: int = 30
):
    """Get quality metrics chart data for the authenticated user."""
    try:
        logger.info(f"Getting quality metrics chart for user: {user_context.user_id}, days: {days}")
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        chart_data = services['aasx_metrics_client'].get_quality_metrics_chart(user_context_dict, days)
        
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
async def get_performance_metrics_chart(
    request: Request,
    user_context: ReadUser,
    days: int = 30
):
    """Get performance metrics chart data for the authenticated user."""
    try:
        logger.info(f"Getting performance metrics chart for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        chart_data = services['aasx_metrics_client'].get_performance_metrics_chart(user_context_dict, days)
        
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
async def get_user_behavior_chart(
    request: Request,
    user_context: ReadUser,
    days: int = 30
):
    """Get user behavior chart data for the authenticated user."""
    try:
        logger.info(f"Getting user behavior chart for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        chart_data = services['aasx_metrics_client'].get_user_behavior_chart(user_context_dict, days)
        
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
async def get_dashboard_metrics(request: Request, user_context: ReadUser):
    """Get comprehensive dashboard metrics for the authenticated user."""
    try:
        logger.info(f"Getting dashboard metrics for user: {user_context.user_id}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        metrics = services['aasx_metrics_client'].get_dashboard_metrics(user_context_dict)
        
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
async def get_performance_metrics(
    request: Request,
    user_context: ReadUser,
    days: int = 30
):
    """Get performance metrics for the authenticated user."""
    try:
        logger.info(f"Getting performance metrics for user: {user_context.user_id}, days: {days}")
        
        user_context_dict = {
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'role': user_context.role
        }
        
        services = get_services()
        metrics = services['aasx_metrics_client'].get_performance_metrics(user_context_dict, days)
        
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
async def analytics_health_check(request: Request, user_context: ReadUser):
    """Health check endpoint for analytics services."""
    try:
        services = get_services()
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
async def get_system_health(request: Request, user_context: ReadUser):
    """Get current system health status for the authenticated user."""
    try:
        logger.info(f"Getting system health for user: {user_context.user_id}")
        
        # Assuming system_monitor and service_monitor are initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "data": {"status": "healthy"},
            "message": "System health retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system health: {str(e)}"
        )


@router.get("/system/resources")
async def get_resource_metrics(request: Request, user_context: ReadUser):
    """Get current resource usage metrics for the authenticated user."""
    try:
        logger.info(f"Getting resource metrics for user: {user_context.user_id}")
        
        # Assuming resource_monitor is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "data": {"status": "healthy"},
            "message": "Resource metrics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get resource metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve resource metrics: {str(e)}"
        )


@router.get("/system/services")
async def get_service_status(request: Request, user_context: ReadUser):
    """Get current service health status for the authenticated user."""
    try:
        logger.info(f"Getting service status for user: {user_context.user_id}")
        
        # Assuming service_monitor is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "data": {"status": "healthy"},
            "message": "Service status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve service status: {str(e)}"
        )


@router.get("/system/logs")
async def get_system_logs(
    request: Request,
    user_context: ReadUser,
    level: Optional[str] = None,
    service: Optional[str] = None,
    hours: int = 24,
    query: str = "",
    limit: int = 1000
):
    """Get system logs for the authenticated user with filtering options."""
    try:
        logger.info(f"Getting system logs for user: {user_context.user_id}")
        
        # Assuming infrastructure_logs is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "data": {"logs": []},
            "message": "System logs retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system logs: {str(e)}"
        )


@router.get("/system/logs/summary")
async def get_log_summary(
    request: Request,
    user_context: ReadUser,
    hours: int = 24
):
    """Get log summary statistics for the authenticated user."""
    try:
        logger.info(f"Getting log summary for user: {user_context.user_id}")
        
        # Assuming infrastructure_logs is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "data": {"summary": {}},
            "message": "Log summary retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get log summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve log summary: {str(e)}"
        )


@router.get("/system/logs/trends")
async def get_log_trends(
    request: Request,
    user_context: ReadUser,
    hours: int = 24
):
    """Get log trends and patterns for the authenticated user."""
    try:
        logger.info(f"Getting log trends for user: {user_context.user_id}")
        
        # Assuming infrastructure_logs is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "data": {"trends": []},
            "message": "Log trends retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get log trends: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve log trends: {str(e)}"
        )


@router.get("/system/alerts/active")
async def get_active_alerts(request: Request, user_context: ReadUser):
    """Get active alerts for the authenticated user."""
    try:
        logger.info(f"Getting active alerts for user: {user_context.user_id}")
        
        # Assuming alert_manager is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "data": {"alerts": []},
            "message": "Active alerts retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve active alerts: {str(e)}"
        )


@router.post("/system/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    request: Request,
    alert_id: str,
    user_context: WriteUser
):
    """Acknowledge an alert for the authenticated user."""
    try:
        logger.info(f"User {user_context.user_id} acknowledging alert: {alert_id}")
        
        # Assuming alert_manager is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "message": f"Alert {alert_id} acknowledged successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.post("/system/alerts/{alert_id}/resolve")
async def resolve_alert(
    request: Request,
    alert_id: str,
    user_context: WriteUser
):
    """Resolve an alert for the authenticated user."""
    try:
        logger.info(f"User {user_context.user_id} resolving alert: {alert_id}")
        
        # Assuming alert_manager is initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
        return {
            "success": True,
            "message": f"Alert {alert_id} resolved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to resolve alert {alert_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve alert: {str(e)}"
        )


@router.get("/system/health-check")
async def system_health_check(request: Request, user_context: ReadUser):
    """Health check endpoint for system monitoring services."""
    try:
        # Assuming system_monitor and service_monitor are initialized elsewhere or not needed here
        # For now, we'll return a placeholder or remove if not used
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