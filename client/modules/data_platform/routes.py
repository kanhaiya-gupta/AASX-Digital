"""
Data Platform Routes - Central Business Operations API
=====================================================

API routes for all business operations including file management, project management,
use case management, and organization management. This module provides the central
API endpoints that all other modules can consume.

Architecture: Clean routes that delegate business logic to integration services
Pattern: Async route handlers with proper error handling and logging
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Import our integration services
from .services import (
    FileManagementService,
    ProjectManagementService,
    UseCaseManagementService,
    OrganizationManagementService,
    UserManagementService
)

logger = logging.getLogger(__name__)

# Create single router for all data platform routes
router = APIRouter(tags=["Data Platform"])

# Initialize templates
templates = Jinja2Templates(directory="client/templates")

# Initialize services
file_service = FileManagementService()
project_service = ProjectManagementService()
use_case_service = UseCaseManagementService()
organization_service = OrganizationManagementService()
user_service = UserManagementService()

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@router.get("/")
async def get_data_platform_root():
    """Get data platform root information"""
    return {
        "success": True,
        "message": "Data Platform API - Central Business Services Hub",
        "version": "1.0.0",
        "services": {
            "file_management": "/files",
            "project_management": "/projects", 
            "use_case_management": "/use-cases",
            "organization_management": "/organizations",
            "user_management": "/users",
            "search": "/search",
            "analytics": "/analytics",
            "notifications": "/notifications"
        },
        "status": "active"
    }

@router.get("/dashboard", response_class=HTMLResponse)
async def get_data_platform_dashboard(request: Request):
    """Get data platform dashboard page"""
    try:
        return templates.TemplateResponse("data_platform/index.html", {
            "request": request,
            "title": "Data Platform Dashboard",
            "module_name": "Data Platform",
            "page_title": "Central Business Services Hub"
        })
    except Exception as e:
        logger.error(f"Error rendering data platform dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render dashboard: {str(e)}"
        )

# ============================================================================
# FILE MANAGEMENT ROUTES
# ============================================================================

@router.post("/files/upload")
async def upload_file(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Upload a file to a specific project"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Prepare file data
        file_data = {
            "original_filename": file.filename,
            "description": description,
            "tags": tags.split(",") if tags else [],
            "mime_type": file.content_type,
            "size_bytes": len(file_content)
        }
        
        # Upload file using service with user and organization context
        result = await file_service.upload_file(file_data, project_id, file_content, user_id, organization_id)
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_id": result.get("file_id"),
            "filename": result.get("filename")
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """Get file information with trace data"""
    try:
        file_info = await file_service.get_file_with_trace(file_id)
        
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return {
            "success": True,
            "data": file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}"
        )

@router.get("/files/{file_id}/hierarchy")
async def get_file_hierarchy_info(file_id: str):
    """Get complete hierarchy information for a file (use case, project, file details)"""
    try:
        hierarchy_info = await file_service.get_file_hierarchy_info(file_id)
        
        if not hierarchy_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return {
            "success": True,
            "data": hierarchy_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file hierarchy info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file hierarchy info: {str(e)}"
        )

@router.get("/files/use-case/{use_case_id}")
async def get_files_by_use_case(
    use_case_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Get all files in a specific use case"""
    try:
        files = await file_service.get_files_by_use_case(use_case_id, user_id, organization_id)
        
        return {
            "success": True,
            "data": files,
            "count": len(files)
        }
        
    except Exception as e:
        logger.error(f"Error getting files by use case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files by use case: {str(e)}"
        )

@router.get("/files/statistics/{project_id}")
async def get_file_statistics(
    project_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Get file statistics for a project"""
    try:
        stats = await file_service.get_file_statistics(project_id, user_id, organization_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting file statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file statistics: {str(e)}"
        )

@router.get("/files/project/{project_id}")
async def get_project_files(
    project_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Get all files for a specific project"""
    try:
        files = await file_service.get_files_by_project(project_id, user_id, organization_id)
        
        return {
            "success": True,
            "data": files,
            "count": len(files)
        }
        
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project files: {str(e)}"
        )

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Delete a file with cascading operations"""
    try:
        success = await file_service.delete_file(file_id, user_id, organization_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file"
            )
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

# ============================================================================
# PROJECT MANAGEMENT ROUTES
# ============================================================================

@router.post("/projects")
async def create_project(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    use_case_id: Optional[str] = Form(None),
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Create a new project"""
    try:
        project_data = {
            "name": name,
            "description": description,
            "use_case_id": use_case_id
        }
        
        result = await project_service.create_project(project_data, user_id, organization_id)
        
        return {
            "success": True,
            "message": "Project created successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Get project information"""
    try:
        project = await project_service.get_project(project_id, user_id, organization_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return {
            "success": True,
            "data": project
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )

@router.get("/projects/organization/{organization_id}")
async def get_organization_projects(
    organization_id: str,
    user_id: str = Form(...)
):
    """Get all projects in an organization"""
    try:
        projects = await project_service.get_projects_by_organization(organization_id, user_id)
        
        return {
            "success": True,
            "data": projects,
            "count": len(projects)
        }
        
    except Exception as e:
        logger.error(f"Error getting organization projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get organization projects: {str(e)}"
        )

@router.put("/projects/{project_id}")
async def update_project(
    project_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Update project information"""
    try:
        project_data = {}
        if name is not None:
            project_data["name"] = name
        if description is not None:
            project_data["description"] = description
        
        updated_project = await project_service.update_project(project_id, project_data, user_id, organization_id)
        
        return {
            "success": True,
            "message": "Project updated successfully",
            "data": updated_project
        }
        
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Delete a project"""
    try:
        success = await project_service.delete_project(project_id, user_id, organization_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )
        
        return {
            "success": True,
            "message": "Project deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

# ============================================================================
# USE CASE MANAGEMENT ROUTES
# ============================================================================

@router.post("/use-cases")
async def create_use_case(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Create a new use case"""
    try:
        use_case_data = {
            "name": name,
            "description": description,
            "category": category
        }
        
        result = await use_case_service.create_use_case(use_case_data, user_id, organization_id)
        
        return {
            "success": True,
            "message": "Use case created successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error creating use case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create use case: {str(e)}"
        )

@router.get("/use-cases/{use_case_id}")
async def get_use_case(
    use_case_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Get use case information"""
    try:
        use_case = await use_case_service.get_use_case(use_case_id, user_id, organization_id)
        
        if not use_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Use case not found"
            )
        
        return {
            "success": True,
            "data": use_case
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting use case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get use case: {str(e)}"
        )

@router.get("/use-cases/organization/{organization_id}")
async def get_organization_use_cases(
    organization_id: str,
    user_id: str = Form(...)
):
    """Get all use cases in an organization"""
    try:
        use_cases = await use_case_service.get_use_cases_by_organization(organization_id, user_id)
        
        return {
            "success": True,
            "data": use_cases,
            "count": len(use_cases)
        }
        
    except Exception as e:
        logger.error(f"Error getting organization use cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get organization use cases: {str(e)}"
        )

@router.get("/use-cases/{use_case_id}/with-projects")
async def get_use_case_with_projects(
    use_case_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Get use case with all its projects"""
    try:
        use_case = await use_case_service.get_use_case_with_projects(use_case_id, user_id, organization_id)
        
        if not use_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Use case not found"
            )
        
        return {
            "success": True,
            "data": use_case
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting use case with projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get use case with projects: {str(e)}"
        )

@router.put("/use-cases/{use_case_id}")
async def update_use_case(
    use_case_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Update use case information"""
    try:
        use_case_data = {}
        if name is not None:
            use_case_data["name"] = name
        if description is not None:
            use_case_data["description"] = description
        if category is not None:
            use_case_data["category"] = category
        
        updated_use_case = await use_case_service.update_use_case(use_case_id, use_case_data, user_id, organization_id)
        
        return {
            "success": True,
            "message": "Use case updated successfully",
            "data": updated_use_case
        }
        
    except Exception as e:
        logger.error(f"Error updating use case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update use case: {str(e)}"
        )

@router.delete("/use-cases/{use_case_id}")
async def delete_use_case(
    use_case_id: str,
    user_id: str = Form(...),
    organization_id: str = Form(...)
):
    """Delete a use case"""
    try:
        success = await use_case_service.delete_use_case(use_case_id, user_id, organization_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete use case"
            )
        
        return {
            "success": True,
            "message": "Use case deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting use case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete use case: {str(e)}"
        )

# ============================================================================
# USER MANAGEMENT ROUTES
# ============================================================================

@router.post("/users")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    organization_id: str = Form(...),
    role: str = Form("user"),
    department: Optional[str] = Form(None),
    job_title: Optional[str] = Form(None),
    admin_user_id: str = Form(...)
):
    """Create a new user"""
    try:
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password,
            "organization_id": organization_id,
            "role": role,
            "department": department,
            "job_title": job_title
        }
        
        result = await user_service.create_user(user_data, admin_user_id)
        
        return {
            "success": True,
            "message": "User created successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    requesting_user_id: str = Form(...)
):
    """Get user information"""
    try:
        user = await user_service.get_user(user_id, requesting_user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "data": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.get("/users/{user_id}/organization-info")
async def get_user_organization_info(user_id: str):
    """Get user's organization and department information"""
    try:
        org_info = await user_service.get_user_organization_info(user_id)
        
        if not org_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "data": org_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user organization info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user organization info: {str(e)}"
        )

@router.get("/users/organization/{organization_id}")
async def get_organization_users(
    organization_id: str,
    requesting_user_id: str = Form(...)
):
    """Get all users in an organization"""
    try:
        users = await user_service.get_users_by_organization(organization_id, requesting_user_id)
        
        return {
            "success": True,
            "data": users,
            "count": len(users)
        }
        
    except Exception as e:
        logger.error(f"Error getting organization users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get organization users: {str(e)}"
        )

@router.get("/users/department/{organization_id}/{department}")
async def get_users_by_department(
    organization_id: str,
    department: str,
    requesting_user_id: str = Form(...)
):
    """Get all users in a specific department"""
    try:
        users = await user_service.get_users_by_department(organization_id, department, requesting_user_id)
        
        return {
            "success": True,
            "data": users,
            "count": len(users)
        }
        
    except Exception as e:
        logger.error(f"Error getting users by department: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users by department: {str(e)}"
        )

@router.post("/users/authenticate")
async def authenticate_user(
    username: str = Form(...),
    password: str = Form(...)
):
    """Authenticate user with username and password"""
    try:
        auth_result = await user_service.authenticate_user(username, password)
        
        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return {
            "success": True,
            "message": "Authentication successful",
            "data": auth_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate user: {str(e)}"
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    full_name: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    job_title: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    requesting_user_id: str = Form(...)
):
    """Update user information"""
    try:
        user_data = {}
        if username is not None:
            user_data["username"] = username
        if email is not None:
            user_data["email"] = email
        if full_name is not None:
            user_data["full_name"] = full_name
        if department is not None:
            user_data["department"] = department
        if job_title is not None:
            user_data["job_title"] = job_title
        if role is not None:
            user_data["role"] = role
        
        updated_user = await user_service.update_user(user_id, user_data, requesting_user_id)
        
        return {
            "success": True,
            "message": "User updated successfully",
            "data": updated_user
        }
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    requesting_user_id: str = Form(...)
):
    """Delete a user"""
    try:
        success = await user_service.delete_user(user_id, requesting_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

# ============================================================================
# ORGANIZATION MANAGEMENT ROUTES
# ============================================================================

@router.post("/organizations")
async def create_organization(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    admin_user_id: str = Form(...)
):
    """Create a new organization"""
    try:
        organization_data = {
            "name": name,
            "description": description
        }
        
        result = await organization_service.create_organization(organization_data, admin_user_id)
        
        return {
            "success": True,
            "message": "Organization created successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )

@router.get("/organizations/{organization_id}")
async def get_organization(
    organization_id: str,
    user_id: str = Form(...)
):
    """Get organization information"""
    try:
        organization = await organization_service.get_organization(organization_id, user_id)
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return {
            "success": True,
            "data": organization
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get organization: {str(e)}"
        )

@router.get("/organizations/{organization_id}/with-stats")
async def get_organization_with_stats(
    organization_id: str,
    user_id: str = Form(...)
):
    """Get organization with statistics"""
    try:
        organization = await organization_service.get_organization_with_stats(organization_id, user_id)
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return {
            "success": True,
            "data": organization
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization with stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get organization with stats: {str(e)}"
        )

@router.put("/organizations/{organization_id}")
async def update_organization(
    organization_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_id: str = Form(...)
):
    """Update organization information"""
    try:
        organization_data = {}
        if name is not None:
            organization_data["name"] = name
        if description is not None:
            organization_data["description"] = description
        
        updated_organization = await organization_service.update_organization(organization_id, organization_data, user_id)
        
        return {
            "success": True,
            "message": "Organization updated successfully",
            "data": updated_organization
        }
        
    except Exception as e:
        logger.error(f"Error updating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )

@router.delete("/organizations/{organization_id}")
async def delete_organization(
    organization_id: str,
    user_id: str = Form(...)
):
    """Delete an organization"""
    try:
        success = await organization_service.delete_organization(organization_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete organization"
            )
        
        return {
            "success": True,
            "message": "Organization deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete organization: {str(e)}"
        )

@router.post("/organizations/{organization_id}/users")
async def add_user_to_organization(
    organization_id: str,
    user_id: str = Form(...),
    admin_user_id: str = Form(...),
    role: str = Form("user")
):
    """Add user to organization"""
    try:
        success = await organization_service.add_user_to_organization(organization_id, user_id, admin_user_id, role)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add user to organization"
            )
        
        return {
            "success": True,
            "message": "User added to organization successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding user to organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add user to organization: {str(e)}"
        )

@router.delete("/organizations/{organization_id}/users/{user_id}")
async def remove_user_from_organization(
    organization_id: str,
    user_id: str,
    admin_user_id: str = Form(...)
):
    """Remove user from organization"""
    try:
        success = await organization_service.remove_user_from_organization(organization_id, user_id, admin_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove user from organization"
            )
        
        return {
            "success": True,
            "message": "User removed from organization successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing user from organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove user from organization: {str(e)}"
        )

# ============================================================================
# HEALTH CHECK ROUTES
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for data platform services"""
    try:
        # Basic health check - services will be initialized on first use
        return {
            "success": True,
            "status": "healthy",
            "message": "Data Platform services are ready",
            "services": {
                "file_management": "ready",
                "project_management": "ready",
                "use_case_management": "ready",
                "organization_management": "ready"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}"
        }
