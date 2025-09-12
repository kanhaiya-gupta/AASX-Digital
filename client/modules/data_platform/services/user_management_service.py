"""
User Management Service - Data Platform Integration Service
=========================================================

Integration service for user management operations that delegates to backend
engine services while handling frontend-specific logic and maintaining clean
architecture.

Pattern: Lazy initialization with async services for world-class standards
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import hashlib
import secrets

# Import from backend engine
from src.engine.services.auth.user_service import UserService
from src.engine.repositories.auth_repository import AuthRepository

# Import user and organization services
from src.engine.services.business_domain.organization_service import OrganizationService

logger = logging.getLogger(__name__)


class UserManagementService:
    """Integration service for user management operations"""
    
    def __init__(self):
        """Initialize with backend services - lazy initialization to avoid async issues"""
        self._initialized = False
        self._user_service = None
        self._auth_repo = None
        self._organization_service = None
        
        logger.info("✅ User management service created (lazy initialization)")
    
    async def _ensure_initialized(self):
        """Ensure services are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Initialize backend services
            self._auth_repo = AuthRepository()
            self._user_service = UserService(self._auth_repo)
            self._organization_service = OrganizationService()
            
            self._initialized = True
            logger.info("✅ User management service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize user management service: {e}")
            raise
    
    @property
    def user_service(self):
        """Get user service (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._user_service
    
    @property
    def auth_repo(self):
        """Get auth repository (lazy initialization)"""
        if not self._initialized:
            raise RuntimeError("Service not initialized. Call _ensure_initialized() first.")
        return self._auth_repo
    
    async def create_user(self, user_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Create a new user with admin validation"""
        await self._ensure_initialized()
        
        try:
            # Validate admin user exists and has privileges
            admin_user = await self.user_service.get_user_by_id(admin_user_id)
            if not admin_user:
                raise ValueError(f"Admin user {admin_user_id} not found")
            
            if admin_user.get("role") not in ["admin", "super_admin"]:
                raise ValueError(f"User {admin_user_id} does not have admin privileges")
            
            # Generate unique user ID
            user_id = str(uuid.uuid4())
            user_data["user_id"] = user_id
            user_data["created_by"] = admin_user_id
            user_data["created_at"] = datetime.utcnow().isoformat()
            
            # Hash password if provided
            if user_data.get("password"):
                user_data["password_hash"] = self._hash_password(user_data["password"])
                del user_data["password"]  # Remove plain text password
            
            # Create user using backend service
            user_info = await self.user_service.create_user(user_data)
            
            logger.info(f"Created user: {user_data.get('username', 'Unknown')} by admin: {admin_user_id}")
            return user_info
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user(self, user_id: str, requesting_user_id: str) -> Optional[Dict[str, Any]]:
        """Get user with access validation"""
        await self._ensure_initialized()
        
        try:
            # Users can only access their own data, or admins can access any user
            requesting_user = await self.user_service.get_user_by_id(requesting_user_id)
            if not requesting_user:
                raise ValueError(f"Requesting user {requesting_user_id} not found")
            
            # Check if user is requesting their own data or has admin privileges
            if (requesting_user_id != user_id and 
                requesting_user.get("role") not in ["admin", "super_admin"]):
                raise ValueError(f"User {requesting_user_id} does not have permission to access user {user_id}")
            
            # Get user information
            user = await self.user_service.get_user_by_id(user_id)
            return user
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise
    
    async def get_users_by_organization(self, organization_id: str, 
                                      requesting_user_id: str) -> List[Dict[str, Any]]:
        """Get all users in an organization with admin validation"""
        await self._ensure_initialized()
        
        try:
            # Validate requesting user has admin privileges
            requesting_user = await self.user_service.get_user_by_id(requesting_user_id)
            if not requesting_user:
                raise ValueError(f"Requesting user {requesting_user_id} not found")
            
            if requesting_user.get("role") not in ["admin", "super_admin"]:
                raise ValueError(f"User {requesting_user_id} does not have admin privileges")
            
            # Validate requesting user belongs to organization
            if requesting_user.get("organization_id") != organization_id:
                raise ValueError(f"User {requesting_user_id} does not belong to organization {organization_id}")
            
            # Get users by organization
            users = await self.auth_repo.get_users_by_organization_id(organization_id)
            return users
            
        except Exception as e:
            logger.error(f"Error getting users by organization: {e}")
            raise
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any], 
                         requesting_user_id: str) -> Dict[str, Any]:
        """Update user with access validation"""
        await self._ensure_initialized()
        
        try:
            # Users can only update their own data, or admins can update any user
            requesting_user = await self.user_service.get_user_by_id(requesting_user_id)
            if not requesting_user:
                raise ValueError(f"Requesting user {requesting_user_id} not found")
            
            # Check if user is updating their own data or has admin privileges
            if (requesting_user_id != user_id and 
                requesting_user.get("role") not in ["admin", "super_admin"]):
                raise ValueError(f"User {requesting_user_id} does not have permission to update user {user_id}")
            
            # Hash password if provided
            if user_data.get("password"):
                user_data["password_hash"] = self._hash_password(user_data["password"])
                del user_data["password"]  # Remove plain text password
            
            # Update user
            updated_user = await self.user_service.update_user(user_id, user_data)
            
            logger.info(f"Updated user: {user_id} by user: {requesting_user_id}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise
    
    async def delete_user(self, user_id: str, requesting_user_id: str) -> bool:
        """Delete user with admin access validation"""
        await self._ensure_initialized()
        
        try:
            # Only admins can delete users
            requesting_user = await self.user_service.get_user_by_id(requesting_user_id)
            if not requesting_user:
                raise ValueError(f"Requesting user {requesting_user_id} not found")
            
            if requesting_user.get("role") not in ["admin", "super_admin"]:
                raise ValueError(f"User {requesting_user_id} does not have admin privileges")
            
            # Prevent admin from deleting themselves
            if requesting_user_id == user_id:
                raise ValueError("Admin users cannot delete themselves")
            
            # Delete user
            success = await self.user_service.delete_user(user_id)
            
            if success:
                logger.info(f"Successfully deleted user: {user_id} by admin: {requesting_user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        await self._ensure_initialized()
        
        try:
            # Get user by username
            user = await self.auth_repo.get_user_by_username(username)
            if not user:
                logger.warning(f"Authentication failed: user {username} not found")
                return None
            
            # Verify password
            if not self._verify_password(password, user.get("password_hash", "")):
                logger.warning(f"Authentication failed: invalid password for user {username}")
                return None
            
            # Generate session token
            session_token = self._generate_session_token()
            
            # Update last login
            await self.user_service.update_user(user["user_id"], {
                "last_login": datetime.utcnow().isoformat(),
                "session_token": session_token
            })
            
            logger.info(f"User {username} authenticated successfully")
            return {
                "user": user,
                "session_token": session_token
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    async def change_password(self, user_id: str, current_password: str, 
                            new_password: str) -> bool:
        """Change user password with current password verification"""
        await self._ensure_initialized()
        
        try:
            # Get user
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Verify current password
            if not self._verify_password(current_password, user.get("password_hash", "")):
                raise ValueError("Current password is incorrect")
            
            # Hash new password
            new_password_hash = self._hash_password(new_password)
            
            # Update password
            success = await self.user_service.update_user(user_id, {
                "password_hash": new_password_hash,
                "password_changed_at": datetime.utcnow().isoformat()
            })
            
            if success:
                logger.info(f"Password changed successfully for user: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """Hash password using secure algorithm"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000  # iterations
        )
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            if not stored_hash or ':' not in stored_hash:
                return False
            
            salt, hash_value = stored_hash.split(':', 1)
            password_hash = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode('utf-8'), 
                salt.encode('utf-8'), 
                100000  # iterations
            )
            return password_hash.hex() == hash_value
        except Exception:
            return False
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    async def get_user_organization_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's organization and department information"""
        await self._ensure_initialized()
        
        try:
            # Get user information
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return None
            
            # Get organization information
            organization = None
            if user.get("organization_id"):
                organization = await self.organization_service.get_organization_by_id(
                    user.get("organization_id")
                )
            
            return {
                "user_id": user_id,
                "organization_id": user.get("organization_id"),
                "organization_name": organization.get("name") if organization else None,
                "department": user.get("department"),
                "job_title": user.get("job_title"),
                "role": user.get("role")
            }
            
        except Exception as e:
            logger.error(f"Error getting user organization info: {e}")
            raise
    
    async def get_users_by_department(self, organization_id: str, department: str, 
                                    requesting_user_id: str) -> List[Dict[str, Any]]:
        """Get all users in a specific department"""
        await self._ensure_initialized()
        
        try:
            # Validate requesting user has access
            await self._validate_user_access(requesting_user_id, organization_id)
            
            # Get users by department
            users = await self.auth_repo.get_users_by_department(organization_id, department)
            return users
            
        except Exception as e:
            logger.error(f"Error getting users by department: {e}")
            raise
