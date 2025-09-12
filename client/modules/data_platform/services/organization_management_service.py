"""
Organization Management Service - Data Platform Integration Service
=================================================================

Integration service for organization management operations that delegates to backend
engine services while handling frontend-specific logic and maintaining clean
architecture.

Pattern: Lazy initialization with async services for world-class standards
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Import from backend engine
from src.engine.services.business_domain.organization_service import OrganizationService
from src.engine.repositories.business_domain_repository import BusinessDomainRepository

# Import user and organization services
from src.engine.services.auth.user_service import UserService
from src.engine.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class OrganizationManagementService:
    """Integration service for organization management operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._organization_service = None
        self._business_domain_repo = None
        self._user_service = None
        self._auth_repo = None
        
        logger.info("✅ Organization management service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            self._business_domain_repo = BusinessDomainRepository()
            self._organization_service = OrganizationService()
            
            self._initialized = True
            logger.info("✅ Organization management service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize organization management service: {e}")
            raise
    
    @property
    def organization_service(self):
        """Get organization service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._organization_service
    
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
    
    async def create_organization(self, organization_data: Dict[str, Any], 
                                admin_user_id: str) -> Dict[str, Any]:
        """Create a new organization with admin user"""
        await self._ensure_initialized()
        
        try:
            # Validate admin user exists
            admin_user = await self.user_service.get_user_by_id(admin_user_id)
            if not admin_user:
                raise ValueError(f"Admin user {admin_user_id} not found")
            
            # Generate unique organization ID
            organization_id = str(uuid.uuid4())
            organization_data["organization_id"] = organization_id
            organization_data["admin_user_id"] = admin_user_id
            organization_data["created_at"] = datetime.utcnow().isoformat()
            
            # Create organization using backend service
            organization_info = await self.organization_service.create_organization(organization_data)
            
            logger.info(f"Created organization: {organization_data.get('name', 'Unknown')} by admin: {admin_user_id}")
            return organization_info
            
        except Exception as e:
            logger.error(f"Error creating organization: {e}")
            raise
    
    async def get_organization(self, organization_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get organization with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Get user information
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Validate user belongs to organization
            if user.get("organization_id") != organization_id:
                raise ValueError(f"User {user_id} does not belong to organization {organization_id}")
            
            # Get organization information
            organization = await self.organization_service.get_organization_by_id(organization_id)
            return organization
            
        except Exception as e:
            logger.error(f"Error getting organization: {e}")
            raise
    
    async def get_organization_with_stats(self, organization_id: str, 
                                        user_id: str) -> Optional[Dict[str, Any]]:
        """Get organization with statistics (users, projects, use cases, files)"""
        await self._ensure_initialized()
        
        try:
            # Get basic organization info
            organization = await self.get_organization(organization_id, user_id)
            if not organization:
                return None
            
            # Get organization statistics
            stats = await self._get_organization_statistics(organization_id)
            
            return {
                **organization,
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting organization with stats: {e}")
            raise
    
    async def update_organization(self, organization_id: str, organization_data: Dict[str, Any], 
                                user_id: str) -> Dict[str, Any]:
        """Update organization with user access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user has admin privileges
            await self._validate_admin_access(user_id, organization_id)
            
            # Update organization
            updated_organization = await self.organization_service.update_organization(
                organization_id, organization_data
            )
            
            logger.info(f"Updated organization: {organization_id} by user: {user_id}")
            return updated_organization
            
        except Exception as e:
            logger.error(f"Error updating organization: {e}")
            raise
    
    async def delete_organization(self, organization_id: str, user_id: str) -> bool:
        """Delete organization with admin access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate user has admin privileges
            await self._validate_admin_access(user_id, organization_id)
            
            # Delete organization
            success = await self.organization_service.delete_organization(organization_id)
            
            if success:
                logger.info(f"Successfully deleted organization: {organization_id} by user: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting organization: {e}")
            raise
    
    async def add_user_to_organization(self, organization_id: str, user_id: str, 
                                     admin_user_id: str, role: str = "user") -> bool:
        """Add user to organization with admin access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate admin user has access
            await self._validate_admin_access(admin_user_id, organization_id)
            
            # Add user to organization
            success = await self.organization_service.add_user_to_organization(
                organization_id, user_id, role
            )
            
            if success:
                logger.info(f"Added user {user_id} to organization {organization_id} by admin {admin_user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding user to organization: {e}")
            raise
    
    async def remove_user_from_organization(self, organization_id: str, user_id: str, 
                                          admin_user_id: str) -> bool:
        """Remove user from organization with admin access validation"""
        await self._ensure_initialized()
        
        try:
            # Validate admin user has access
            await self._validate_admin_access(admin_user_id, organization_id)
            
            # Remove user from organization
            success = await self.organization_service.remove_user_from_organization(
                organization_id, user_id
            )
            
            if success:
                logger.info(f"Removed user {user_id} from organization {organization_id} by admin {admin_user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error removing user from organization: {e}")
            raise
    
    async def _validate_admin_access(self, user_id: str, organization_id: str):
        """Validate user has admin access to the organization"""
        try:
            # Get user information
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Validate user belongs to organization
            if user.get("organization_id") != organization_id:
                raise ValueError(f"User {user_id} does not belong to organization {organization_id}")
            
            # Validate user has admin role
            if user.get("role") not in ["admin", "super_admin"]:
                raise ValueError(f"User {user_id} does not have admin privileges")
            
            logger.debug(f"Admin access validated: {user_id} -> {organization_id}")
            
        except Exception as e:
            logger.error(f"Admin access validation failed: {e}")
            raise
    
    async def _get_organization_statistics(self, organization_id: str) -> Dict[str, Any]:
        """Get organization statistics"""
        try:
            # Get counts from repositories
            user_count = await self.organization_repo.get_user_count(organization_id)
            project_count = await self.organization_repo.get_project_count(organization_id)
            use_case_count = await self.organization_repo.get_use_case_count(organization_id)
            file_count = await self.organization_repo.get_file_count(organization_id)
            
            return {
                "user_count": user_count,
                "project_count": project_count,
                "use_case_count": use_case_count,
                "file_count": file_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error getting organization statistics: {e}")
            return {
                "user_count": 0,
                "project_count": 0,
                "use_case_count": 0,
                "file_count": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
