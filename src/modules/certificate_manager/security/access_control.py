"""
Access Control for Certificate Manager

Handles permissions, authentication, and authorization for certificates.
Provides role-based access control and permission management.
"""

import asyncio
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for certificate access"""
    NONE = "none"           # No access
    READ = "read"           # Read-only access
    WRITE = "write"         # Read and write access
    ADMIN = "admin"         # Full administrative access
    OWNER = "owner"         # Owner with full control


class AccessStatus(Enum):
    """Access control status values"""
    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class AccessControl:
    """
    Access control and permission management service
    
    Handles:
    - User authentication and authorization
    - Role-based access control (RBAC)
    - Permission management and validation
    - Access token generation and validation
    - Session management
    - Audit logging for access attempts
    """
    
    def __init__(self):
        """Initialize the access control service"""
        self.permission_levels = list(PermissionLevel)
        self.access_statuses = list(AccessStatus)
        
        # User and permission storage
        self.users: Dict[str, Dict[str, Any]] = {}
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.permissions: Dict[str, Dict[str, Any]] = {}
        self.access_tokens: Dict[str, Dict[str, Any]] = {}
        self.access_history: List[Dict[str, Any]] = []
        
        # Access control locks
        self.access_locks: Dict[str, asyncio.Lock] = {}
        
        # Access control settings
        self.access_settings = self._initialize_access_settings()
        
        # Initialize default roles and permissions
        self._initialize_default_roles()
        
        logger.info("Access Control service initialized successfully")
    
    def _initialize_access_settings(self) -> Dict[str, Any]:
        """Initialize access control settings"""
        return {
            "default_session_timeout_hours": 24,
            "max_failed_login_attempts": 5,
            "account_lockout_duration_minutes": 30,
            "password_min_length": 8,
            "require_strong_password": True,
            "max_concurrent_sessions": 3,
            "access_token_expiry_hours": 12,
            "audit_log_retention_days": 90
        }
    
    def _initialize_default_roles(self) -> None:
        """Initialize default roles and permissions"""
        # Default roles
        self.roles = {
            "viewer": {
                "name": "Viewer",
                "description": "Read-only access to certificates",
                "permissions": ["read_certificates", "view_metadata"],
                "level": PermissionLevel.READ.value
            },
            "editor": {
                "name": "Editor",
                "description": "Read and write access to certificates",
                "permissions": ["read_certificates", "write_certificates", "view_metadata", "edit_metadata"],
                "level": PermissionLevel.WRITE.value
            },
            "manager": {
                "name": "Manager",
                "description": "Full access to certificates and basic administration",
                "permissions": ["read_certificates", "write_certificates", "delete_certificates", "view_metadata", "edit_metadata", "manage_users"],
                "level": PermissionLevel.ADMIN.value
            },
            "administrator": {
                "name": "Administrator",
                "description": "Full system administration access",
                "permissions": ["*"],  # All permissions
                "level": PermissionLevel.ADMIN.value
            }
        }
        
        # Default permissions
        self.permissions = {
            "read_certificates": {
                "name": "Read Certificates",
                "description": "Ability to read certificate data",
                "level": PermissionLevel.READ.value
            },
            "write_certificates": {
                "name": "Write Certificates",
                "description": "Ability to create and modify certificates",
                "level": PermissionLevel.WRITE.value
            },
            "delete_certificates": {
                "name": "Delete Certificates",
                "description": "Ability to delete certificates",
                "level": PermissionLevel.ADMIN.value
            },
            "view_metadata": {
                "name": "View Metadata",
                "description": "Ability to view certificate metadata",
                "level": PermissionLevel.READ.value
            },
            "edit_metadata": {
                "name": "Edit Metadata",
                "description": "Ability to edit certificate metadata",
                "level": PermissionLevel.WRITE.value
            },
            "manage_users": {
                "name": "Manage Users",
                "description": "Ability to manage user accounts",
                "level": PermissionLevel.ADMIN.value
            },
            "manage_roles": {
                "name": "Manage Roles",
                "description": "Ability to manage roles and permissions",
                "level": PermissionLevel.ADMIN.value
            },
            "view_audit_logs": {
                "name": "View Audit Logs",
                "description": "Ability to view audit logs",
                "level": PermissionLevel.ADMIN.value
            }
        }
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "viewer",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user account
        
        Args:
            username: Unique username
            email: User email address
            password: User password
            role: User role (defaults to viewer)
            metadata: Additional user metadata
            
        Returns:
            Dictionary containing user information
        """
        # Validate input parameters
        await self._validate_user_creation(username, email, password, role)
        
        # Check if user already exists
        if username in self.users:
            raise ValueError(f"User '{username}' already exists")
        
        # Hash password
        password_hash = await self._hash_password(password)
        
        # Create user record
        user_id = f"user_{secrets.token_hex(8)}"
        user_record = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "status": "active",
            "created_at": asyncio.get_event_loop().time(),
            "last_login": None,
            "failed_login_attempts": 0,
            "account_locked_until": None,
            "metadata": metadata or {}
        }
        
        # Store user
        self.users[username] = user_record
        
        # Record in history
        self.access_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "action": "create_user",
            "username": username,
            "role": role,
            "status": "success"
        })
        
        logger.info(f"User '{username}' created with role '{role}'")
        
        return user_record
    
    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Dictionary containing authentication result and access token
        """
        # Check if user exists
        if username not in self.users:
            await self._record_failed_login(username, "User not found")
            raise ValueError("Invalid username or password")
        
        user = self.users[username]
        
        # Check if account is locked
        if await self._is_account_locked(user):
            await self._record_failed_login(username, "Account locked")
            raise ValueError("Account is temporarily locked due to multiple failed login attempts")
        
        # Verify password
        if not await self._verify_password(password, user["password_hash"]):
            await self._record_failed_login(username, "Invalid password")
            raise ValueError("Invalid username or password")
        
        # Reset failed login attempts
        user["failed_login_attempts"] = 0
        user["account_locked_until"] = None
        
        # Update last login
        user["last_login"] = asyncio.get_event_loop().time()
        
        # Generate access token
        access_token = await self._generate_access_token(user)
        
        # Record successful login
        self.access_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "action": "login",
            "username": username,
            "status": "success"
        })
        
        logger.info(f"User '{username}' authenticated successfully")
        
        return {
            "user_id": user["user_id"],
            "username": username,
            "role": user["role"],
            "access_token": access_token,
            "permissions": await self._get_user_permissions(user),
            "expires_at": self.access_tokens[access_token]["expires_at"]
        }
    
    async def validate_access_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate access token and return user information
        
        Args:
            access_token: Access token to validate
            
        Returns:
            Dictionary containing user information and permissions
        """
        # Check if token exists and is valid
        if access_token not in self.access_tokens:
            raise ValueError("Invalid access token")
        
        token_info = self.access_tokens[access_token]
        
        # Check if token is expired
        if asyncio.get_event_loop().time() > token_info["expires_at"]:
            # Remove expired token
            del self.access_tokens[access_token]
            raise ValueError("Access token has expired")
        
        # Get user information
        username = token_info["username"]
        if username not in self.users:
            raise ValueError("User associated with token not found")
        
        user = self.users[username]
        
        # Check if user is still active
        if user["status"] != "active":
            raise ValueError("User account is not active")
        
        return {
            "user_id": user["user_id"],
            "username": username,
            "role": user["role"],
            "permissions": await self._get_user_permissions(user),
            "token_expires_at": token_info["expires_at"]
        }
    
    async def check_permission(
        self,
        access_token: str,
        permission: str,
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if user has specific permission
        
        Args:
            access_token: Valid access token
            permission: Permission to check
            resource_id: Optional resource ID for resource-specific permissions
            
        Returns:
            Dictionary containing permission check result
        """
        try:
            # Validate access token
            user_info = await self.validate_access_token(access_token)
            username = user_info["username"]
            user_permissions = user_info["permissions"]
            
            # Check if user has the permission
            has_permission = permission in user_permissions or "*" in user_permissions
            
            # Record permission check
            self.access_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "check_permission",
                "username": username,
                "permission": permission,
                "resource_id": resource_id,
                "granted": has_permission,
                "status": "success"
            })
            
            return {
                "has_permission": has_permission,
                "username": username,
                "permission": permission,
                "resource_id": resource_id,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            # Record failed permission check
            self.access_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "check_permission",
                "permission": permission,
                "resource_id": resource_id,
                "granted": False,
                "status": "failed",
                "error": str(e)
            })
            
            raise
    
    async def revoke_access_token(self, access_token: str) -> bool:
        """Revoke an access token"""
        if access_token in self.access_tokens:
            token_info = self.access_tokens[access_token]
            username = token_info["username"]
            
            # Remove token
            del self.access_tokens[access_token]
            
            # Record revocation
            self.access_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "revoke_token",
                "username": username,
                "status": "success"
            })
            
            logger.info(f"Access token revoked for user '{username}'")
            return True
        
        return False
    
    async def update_user_role(
        self,
        admin_token: str,
        username: str,
        new_role: str
    ) -> Dict[str, Any]:
        """
        Update user role (requires admin permission)
        
        Args:
            admin_token: Admin access token
            username: Username to update
            new_role: New role for the user
            
        Returns:
            Dictionary containing updated user information
        """
        # Check admin permission
        await self.check_permission(admin_token, "manage_users")
        
        # Validate role
        if new_role not in self.roles:
            raise ValueError(f"Invalid role: {new_role}")
        
        # Check if user exists
        if username not in self.users:
            raise ValueError(f"User '{username}' not found")
        
        # Update user role
        old_role = self.users[username]["role"]
        self.users[username]["role"] = new_role
        self.users[username]["updated_at"] = asyncio.get_event_loop().time()
        
        # Record role update
        self.access_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "action": "update_user_role",
            "admin_username": (await self.validate_access_token(admin_token))["username"],
            "target_username": username,
            "old_role": old_role,
            "new_role": new_role,
            "status": "success"
        })
        
        logger.info(f"User '{username}' role updated from '{old_role}' to '{new_role}'")
        
        return self.users[username]
    
    async def create_role(
        self,
        admin_token: str,
        role_name: str,
        description: str,
        permissions: List[str]
    ) -> Dict[str, Any]:
        """
        Create a new role (requires admin permission)
        
        Args:
            admin_token: Admin access token
            role_name: Name of the new role
            description: Role description
            permission: List of permissions for the role
            
        Returns:
            Dictionary containing new role information
        """
        # Check admin permission
        await self.check_permission(admin_token, "manage_roles")
        
        # Check if role already exists
        if role_name in self.roles:
            raise ValueError(f"Role '{role_name}' already exists")
        
        # Validate permissions
        for permission in permissions:
            if permission != "*" and permission not in self.permissions:
                raise ValueError(f"Invalid permission: {permission}")
        
        # Create role
        role_record = {
            "name": role_name,
            "description": description,
            "permissions": permissions,
            "created_at": asyncio.get_event_loop().time(),
            "created_by": (await self.validate_access_token(admin_token))["username"]
        }
        
        self.roles[role_name] = role_record
        
        # Record role creation
        self.access_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "action": "create_role",
            "admin_username": (await self.validate_access_token(admin_token))["username"],
            "role_name": role_name,
            "status": "success"
        })
        
        logger.info(f"Role '{role_name}' created successfully")
        
        return role_record
    
    async def _validate_user_creation(
        self,
        username: str,
        email: str,
        password: str,
        role: str
    ) -> None:
        """Validate user creation parameters"""
        # Validate username
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not username.isalnum():
            raise ValueError("Username must contain only alphanumeric characters")
        
        # Validate email
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        
        # Validate password
        if len(password) < self.access_settings["password_min_length"]:
            raise ValueError(f"Password must be at least {self.access_settings['password_min_length']} characters long")
        
        if self.access_settings["require_strong_password"]:
            if not await self._is_strong_password(password):
                raise ValueError("Password does not meet strength requirements")
        
        # Validate role
        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}")
    
    async def _is_strong_password(self, password: str) -> bool:
        """Check if password meets strength requirements"""
        # Check length
        if len(password) < 8:
            return False
        
        # Check for mixed case
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        
        # Check for digits
        has_digit = any(c.isdigit() for c in password)
        
        # Check for special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        has_special = any(c in special_chars for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    async def _hash_password(self, password: str) -> str:
        """Hash password using secure algorithm"""
        # In a real implementation, this would use bcrypt or similar
        # For now, we'll use a simple hash with salt
        salt = secrets.token_hex(16)
        password_with_salt = password + salt
        password_hash = hashlib.sha256(password_with_salt.encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    async def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_part = stored_hash.split(":", 1)
            password_with_salt = password + salt
            computed_hash = hashlib.sha256(password_with_salt.encode()).hexdigest()
            return computed_hash == hash_part
        except:
            return False
    
    async def _is_account_locked(self, user: Dict[str, Any]) -> bool:
        """Check if user account is locked"""
        if user["account_locked_until"] is None:
            return False
        
        current_time = asyncio.get_event_loop().time()
        return current_time < user["account_locked_until"]
    
    async def _record_failed_login(self, username: str, reason: str) -> None:
        """Record failed login attempt"""
        if username in self.users:
            user = self.users[username]
            user["failed_login_attempts"] += 1
            
            # Lock account if too many failed attempts
            if user["failed_login_attempts"] >= self.access_settings["max_failed_login_attempts"]:
                lockout_duration = self.access_settings["account_lockout_duration_minutes"] * 60
                user["account_locked_until"] = asyncio.get_event_loop().time() + lockout_duration
                
                logger.warning(f"Account '{username}' locked for {self.access_settings['account_lockout_duration_minutes']} minutes")
            
            # Record failed login
            self.access_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "action": "failed_login",
                "username": username,
                "reason": reason,
                "failed_attempts": user["failed_login_attempts"],
                "status": "failed"
            })
    
    async def _generate_access_token(self, user: Dict[str, Any]) -> str:
        """Generate access token for user"""
        # Generate unique token
        token = secrets.token_hex(32)
        
        # Calculate expiry time
        expiry_hours = self.access_settings["access_token_expiry_hours"]
        expires_at = asyncio.get_event_loop().time() + (expiry_hours * 3600)
        
        # Store token information
        self.access_tokens[token] = {
            "username": user["username"],
            "user_id": user["user_id"],
            "role": user["role"],
            "created_at": asyncio.get_event_loop().time(),
            "expires_at": expires_at
        }
        
        return token
    
    async def _get_user_permissions(self, user: Dict[str, Any]) -> List[str]:
        """Get permissions for user based on their role"""
        role = user["role"]
        if role not in self.roles:
            return []
        
        return self.roles[role]["permissions"]
    
    async def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username"""
        return self.users.get(username)
    
    async def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get all users with a specific role"""
        return [
            user for user in self.users.values()
            if user.get("role") == role
        ]
    
    async def get_active_users(self) -> List[Dict[str, Any]]:
        """Get all active users"""
        return [
            user for user in self.users.values()
            if user.get("status") == "active"
        ]
    
    async def get_access_statistics(self) -> Dict[str, Any]:
        """Get access control statistics"""
        total_users = len(self.users)
        active_users = len([u for u in self.users.values() if u.get("status") == "active"])
        locked_users = len([u for u in self.users.values() if u.get("account_locked_until") is not None])
        
        # Count by role
        users_by_role = {}
        for user in self.users.values():
            role = user.get("role", "unknown")
            users_by_role[role] = users_by_role.get(role, 0) + 1
        
        # Count active sessions
        active_sessions = len(self.access_tokens)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "locked_users": locked_users,
            "users_by_role": users_by_role,
            "active_sessions": active_sessions,
            "total_roles": len(self.roles),
            "total_permissions": len(self.permissions),
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def get_access_history(
        self,
        username: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get access control history with optional filtering"""
        history = self.access_history.copy()
        
        # Filter by username
        if username:
            history = [h for h in history if h.get("username") == username]
        
        # Filter by action
        if action:
            history = [h for h in history if h.get("action") == action]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired access tokens and return count of cleaned tokens"""
        current_time = asyncio.get_event_loop().time()
        expired_tokens = []
        
        for token, token_info in self.access_tokens.items():
            if current_time > token_info["expires_at"]:
                expired_tokens.append(token)
        
        # Remove expired tokens
        for token in expired_tokens:
            del self.access_tokens[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired access tokens")
        
        return len(expired_tokens)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the access control service"""
        return {
            "status": "healthy",
            "permission_levels": [level.value for level in self.permission_levels],
            "access_statuses": [status.value for status in self.access_statuses],
            "users_count": len(self.users),
            "roles_count": len(self.roles),
            "permissions_count": len(self.permissions),
            "active_tokens_count": len(self.access_tokens),
            "access_history_size": len(self.access_history),
            "access_settings": {
                "default_session_timeout_hours": self.access_settings["default_session_timeout_hours"],
                "max_failed_login_attempts": self.access_settings["max_failed_login_attempts"],
                "account_lockout_duration_minutes": self.access_settings["account_lockout_duration_minutes"],
                "password_min_length": self.access_settings["password_min_length"]
            },
            "timestamp": asyncio.get_event_loop().time()
        }
