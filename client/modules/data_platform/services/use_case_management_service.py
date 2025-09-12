"""
Use Case Management Service - Data Platform Integration Service
==============================================================

Integration service for use case management operations that delegates to backend
engine services while handling frontend-specific logic and maintaining clean
architecture.

Pattern: Lazy initialization with async services for world-class standards
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Import from backend engine
from src.engine.services.business_domain.use_case_service import UseCaseService
from src.engine.repositories.business_domain_repository import BusinessDomainRepository

# Import user and organization services
from src.engine.services.auth.user_service import UserService
from src.engine.services.business_domain.organization_service import OrganizationService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class UseCaseManagementService:
    """Integration service for use case management operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._use_case_service = None
        self._business_domain_repo = None
        self._user_service = None
        self._organization_service = None
        self._auth_repo = None
        
        logger.info("✅ Use case management service created (lazy initialization)")
    
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
            self._use_case_service = UseCaseService()
            
            self._initialized = True
            logger.info("✅ Use case management service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize use case management service: {e}")
            raise
    
    @property
    def use_case_service(self):
        """Get use case service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._use_case_service
    
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
    
    async def create_use_case(self, use_case_data: Dict[str, Any], user_id: str, 
                             organization_id: str) -> Dict[str, Any]:
        """Create a new use case with user and organization context"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Generate unique use case ID
            use_case_id = str(uuid.uuid4())
            use_case_data["use_case_id"] = use_case_id
            use_case_data["user_id"] = user_id
            use_case_data["organization_id"] = organization_id
            use_case_data["created_by"] = user_id
            use_case_data["created_at"] = datetime.utcnow().isoformat()
            
            # Create use case using backend service
            use_case_info = await self.use_case_service.create_use_case(use_case_data)
            
            logger.info(f"Created use case: {use_case_data.get('name', 'Unknown')} by user: {user_id}")
            return use_case_info
            
        except Exception as e:
            logger.error(f"Error creating use case: {e}")
            raise
    
    async def get_use_case(self, use_case_id: str, user_id: str, 
                          organization_id: str) -> Optional[Dict[str, Any]]:
        """Get use case with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Get use case information
            use_case = await self.use_case_service.get_use_case_by_id(use_case_id)
            if not use_case:
                return None
            
            # Validate use case belongs to organization
            if use_case.get("organization_id") != organization_id:
                raise ValueError(f"Use case {use_case_id} not found in organization {organization_id}")
            
            return use_case
            
        except Exception as e:
            logger.error(f"Error getting use case: {e}")
            raise
    
    async def get_use_cases_by_organization(self, organization_id: str, 
                                          user_id: str) -> List[Dict[str, Any]]:
        """Get all use cases in an organization with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Get use cases by organization
            use_cases = await self.use_case_repo.get_use_cases_by_organization_id(organization_id)
            return use_cases
            
        except Exception as e:
            logger.error(f"Error getting use cases by organization: {e}")
            raise
    
    async def update_use_case(self, use_case_id: str, use_case_data: Dict[str, Any], 
                            user_id: str, organization_id: str) -> Dict[str, Any]:
        """Update use case with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Validate use case exists and belongs to organization
            use_case = await self.get_use_case(use_case_id, user_id, organization_id)
            if not use_case:
                raise ValueError(f"Use case {use_case_id} not found")
            
            # Update use case
            updated_use_case = await self.use_case_service.update_use_case(use_case_id, use_case_data)
            
            logger.info(f"Updated use case: {use_case_id} by user: {user_id}")
            return updated_use_case
            
        except Exception as e:
            logger.error(f"Error updating use case: {e}")
            raise
    
    async def delete_use_case(self, use_case_id: str, user_id: str, 
                            organization_id: str) -> bool:
        """Delete use case with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user and organization access
            await self._validate_user_access(user_id, organization_id)
            
            # Validate use case exists and belongs to organization
            use_case = await self.get_use_case(use_case_id, user_id, organization_id)
            if not use_case:
                raise ValueError(f"Use case {use_case_id} not found")
            
            # Delete use case
            success = await self.use_case_service.delete_use_case(use_case_id)
            
            if success:
                logger.info(f"Successfully deleted use case: {use_case_id} by user: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting use case: {e}")
            raise
    
    async def get_use_case_with_projects(self, use_case_id: str, user_id: str, 
                                       organization_id: str) -> Optional[Dict[str, Any]]:
        """Get use case with all its projects"""
        await self._ensure_initialized()
        
        try:
            # Get use case
            use_case = await self.get_use_case(use_case_id, user_id, organization_id)
            if not use_case:
                return None
            
            # Get projects for this use case
            projects = await self.use_case_repo.get_projects_by_use_case_id(use_case_id)
            
            return {
                **use_case,
                "projects": projects,
                "project_count": len(projects)
            }
            
        except Exception as e:
            logger.error(f"Error getting use case with projects: {e}")
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
