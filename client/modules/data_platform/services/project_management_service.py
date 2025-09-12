"""
Project Management Service - Data Platform Integration Service
============================================================

Integration service for project management operations that delegates to backend
engine services while handling frontend-specific logic and maintaining clean
architecture.

Pattern: Lazy initialization with async services for world-class standards
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Import from backend engine
from src.engine.services.business_domain.project_service import ProjectService
from src.engine.repositories.business_domain_repository import BusinessDomainRepository

# Import user and organization services
from src.engine.services.auth.user_service import UserService
from src.engine.services.business_domain.organization_service import OrganizationService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class ProjectManagementService:
    """Integration service for project management operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._project_service = None
        self._business_domain_repo = None
        self._user_service = None
        self._organization_service = None
        self._auth_repo = None
        
        logger.info("✅ Project management service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            self._organization_service = OrganizationService()
            self._business_domain_repo = BusinessDomainRepository()
            self._project_service = ProjectService()
            
            self._initialized = True
            logger.info("✅ Project management service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize project management service: {e}")
            raise
    
    @property
    def project_service(self):
        """Get project service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._project_service
    
    @property
    def business_domain_repo(self):
        """Get business domain repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._business_domain_repo
    
    @property
    def user_service(self):
        """Get user service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._user_service
    
    @property
    def organization_service(self):
        """Get organization service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._organization_service
    
    async def create_project(self, project_data: Dict[str, Any], user_id: str, 
                           organization_id: str) -> Dict[str, Any]:
        """Create a new project with user and organization context"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Generate unique project ID
            project_id = str(uuid.uuid4())
            project_data["project_id"] = project_id
            project_data["user_id"] = user_id
            project_data["organization_id"] = organization_id
            project_data["created_by"] = user_id
            project_data["created_at"] = datetime.utcnow().isoformat()
            
            # Create project using backend service
            project_info = await self.project_service.create_project(project_data)
            
            logger.info(f"Created project: {project_data.get('name', 'Unknown')} by user: {user_id}")
            return project_info
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    async def get_project(self, project_id: str, user_id: str, 
                         organization_id: str) -> Optional[Dict[str, Any]]:
        """Get project with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Get project information
            project = await self.project_service.get_project_by_id(project_id)
            if not project:
                return None
            
            # Validate project belongs to organization
            if project.get("organization_id") != organization_id:
                raise ValueError(f"Project {project_id} not found in organization {organization_id}")
            
            return project
            
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            raise
    
    async def get_projects_by_organization(self, organization_id: str, 
                                         user_id: str) -> List[Dict[str, Any]]:
        """Get all projects in an organization with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Get projects by organization
            projects = await self.project_repo.get_projects_by_organization_id(organization_id)
            return projects
            
        except Exception as e:
            logger.error(f"Error getting projects by organization: {e}")
            raise
    
    async def update_project(self, project_id: str, project_data: Dict[str, Any], 
                           user_id: str, organization_id: str) -> Dict[str, Any]:
        """Update project with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Validate project exists and belongs to organization
            project = await self.get_project(project_id, user_id, organization_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Update project
            updated_project = await self.project_service.update_project(project_id, project_data)
            
            logger.info(f"Updated project: {project_id} by user: {user_id}")
            return updated_project
            
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            raise
    
    async def delete_project(self, project_id: str, user_id: str, 
                           organization_id: str) -> bool:
        """Delete project with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Validate project exists and belongs to organization
            project = await self.get_project(project_id, user_id, organization_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Delete project
            success = await self.project_service.delete_project(project_id)
            
            if success:
                logger.info(f"Successfully deleted project: {project_id} by user: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            raise
    
    async def _validate_user_access(self, user_id: str, organization_id: str):
        """Validate user has access to the organization"""
        try:
            # Get user information
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Validate user belongs to organization
            if user.get("organization_id") != organization_id:
                raise ValueError(f"User {user_id} does not belong to organization {organization_id}")
            
            logger.debug(f"User access validated: {user_id} -> {organization_id}")
            
        except Exception as e:
            logger.error(f"User access validation failed: {e}")
            raise
