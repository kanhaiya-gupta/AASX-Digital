"""
Auth Integration Service - Soft Connection to Backend
====================================================

Thin integration layer that connects webapp to backend auth services.
Handles frontend-specific logic while delegating business logic to backend.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import Request

# Import from backend engine - ONLY auth models
from src.engine.services.auth.auth_service import AuthService
from src.engine.services.auth.user_service import UserService
from src.engine.services.auth.role_service import RoleService
from src.engine.repositories.auth_repository import AuthRepository
from src.engine.models.auth import User, CustomRole

# Import business domain services for organization/department operations
from src.engine.services.business_domain.organization_service import OrganizationService

logger = logging.getLogger(__name__)


class AuthIntegrationService:
    """Integration service for authentication operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._auth_repo = None
        self._user_service = None
        self._role_service = None
        self._auth_service = None
        self._organization_service = None
        
        logger.info("✅ Auth integration service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            self._role_service = RoleService(self._auth_repo)
            self._auth_service = AuthService(self._auth_repo, self._user_service, self._role_service)
            
            # Initialize business domain services for org/dept operations
            self._organization_service = OrganizationService()
            
            self._initialized = True
            logger.info("✅ Auth integration service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize auth integration service: {e}")
            raise
    
    @property
    def auth_repo(self):
        """Get auth repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_repo
    
    @property
    def user_service(self):
        """Get user service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._user_service
    
    @property
    def role_service(self):
        """Get role service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._role_service
    
    @property
    def auth_service(self):
        """Get auth service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_service
    
    @property
    def organization_service(self):
        """Get organization service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._organization_service
    
    async def authenticate_user(self, username: str, password: str, ip_address: str = None, 
                              user_agent: str = None) -> Dict[str, Any]:
        """Authenticate user via backend"""
        await self._ensure_initialized()
        try:
            result = await self.auth_service.authenticate_user(username, password, ip_address, user_agent)
            
            if result.success:
                return {
                    "success": True,
                    "user": result.user,
                    "session": result.session,
                    "token": result.token,
                    "requires_mfa": result.requires_mfa,
                    "metadata": result.metadata
                }
            else:
                return {
                    "success": False,
                    "error_message": result.error_message,
                    "requires_mfa": result.requires_mfa
                }
                
        except Exception as e:
            logger.error(f"Error in auth integration: {e}")
            return {
                "success": False,
                "error_message": "Authentication service unavailable"
            }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from backend"""
        await self._ensure_initialized()
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if user:
                return user.dict() if hasattr(user, 'dict') else user
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username from backend"""
        await self._ensure_initialized()
        try:
            user = await self.user_service.get_user_by_username(username)
            if user:
                return user.dict() if hasattr(user, 'dict') else user
            return None
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create user via backend"""
        await self._ensure_initialized()
        try:
            user = await self.user_service.create_user(user_data)
            if user:
                return user.dict() if hasattr(user, 'dict') else user
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user via backend"""
        await self._ensure_initialized()
        try:
            return await self.user_service.update_user(user_id, updates)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from backend"""
        await self._ensure_initialized()
        try:
            users = await self.user_service.get_all_users()
            return [user.dict() if hasattr(user, 'dict') else user for user in users]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_active_organizations(self) -> List[Dict[str, Any]]:
        """Get active organizations from backend business domain service"""
        await self._ensure_initialized()
        try:
            organizations = await self.organization_service.get_active_organizations()
            return [org.dict() if hasattr(org, 'dict') else org for org in organizations]
        except Exception as e:
            logger.error(f"Error getting organizations: {e}")
            return []
    
    async def get_departments_for_organization(self, org_id: str) -> List[Dict[str, Any]]:
        """Get departments for a specific organization from backend business domain service"""
        await self._ensure_initialized()
        try:
            departments = await self.organization_service.get_organization_departments(org_id)
            return [dept.dict() if hasattr(dept, 'dict') else dept for dept in departments]
        except Exception as e:
            logger.error(f"Error getting departments for organization {org_id}: {e}")
            return []
    
    async def get_user_organization_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's organization and department details from backend business domain service"""
        await self._ensure_initialized()
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if not user or not user.org_id:
                return None
            
            # Get organization details
            org = await self.organization_service.get_organization_by_id(user.org_id)
            if not org:
                return None
            
            # Get department details if user has a department
            dept = None
            if user.dept_id:
                dept = await self.organization_service.get_department(user.dept_id)
            
            return {
                "organization": org.dict() if hasattr(org, 'dict') else org,
                "department": dept.dict() if hasattr(dept, 'dict') else dept if dept else None
            }
        except Exception as e:
            logger.error(f"Error getting organization details for user {user_id}: {e}")
            return None
    
    async def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token via backend"""
        await self._ensure_initialized()
        try:
            result = await self.auth_service.authenticate_with_token(token)
            
            if result.success:
                return {
                    "success": True,
                    "user": result.user,
                    "session": result.session
                }
            else:
                return {
                    "success": False,
                    "error_message": result.error_message
                }
                
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return {
                "success": False,
                "error_message": "Session validation failed"
            }
    
    async def logout_user(self, token: str) -> bool:
        """Logout user via backend"""
        await self._ensure_initialized()
        try:
            # This would need to be implemented in the backend auth service
            # For now, return success
            return True
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            return False
    
    async def get_current_user_from_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get current user from request (for routes)"""
        await self._ensure_initialized()
        try:
            # Extract token from request headers
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            result = await self.validate_session(token)
            
            if result and result.get("success"):
                return result.get("user")
            return None
            
        except Exception as e:
            logger.error(f"Error getting current user from request: {e}")
            return None
    
    async def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration"""
        await self._ensure_initialized()
        try:
            return {
                "mfa_enabled": True,
                "social_login_enabled": True,
                "password_policy": {
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special": False
                },
                "session_timeout": 30,
                "max_login_attempts": 5
            }
        except Exception as e:
            logger.error(f"Error getting auth config: {e}")
            return {}


# Export the integration service
__all__ = [
    'AuthIntegrationService'
]
