"""
Security Models
==============

Data models for security and authentication components.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone


class PermissionLevel(Enum):
    """Permission levels for access control"""
    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4


class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    LOCKED = "locked"


class AuthenticationMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    JWT = "jwt"
    OAUTH = "oauth"
    LDAP = "ldap"
    MFA = "mfa"
    API_KEY = "api_key"


@dataclass
class Permission:
    """Permission definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    resource: str = ""  # Resource this permission applies to
    actions: Set[str] = field(default_factory=set)  # Allowed actions
    level: PermissionLevel = PermissionLevel.NONE
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditional logic
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if isinstance(self.actions, list):
            self.actions = set(self.actions)
    
    def has_action(self, action: str) -> bool:
        """Check if permission allows specific action"""
        return action in self.actions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'actions': list(self.actions),
            'level': self.level.value,
            'conditions': self.conditions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class Role:
    """Role definition with permissions"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    permissions: List[Permission] = field(default_factory=list)
    parent_roles: List[str] = field(default_factory=list)  # Role inheritance
    is_system: bool = False  # System roles cannot be deleted
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_permission(self, permission: Permission) -> None:
        """Add permission to role"""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_permission(self, permission_id: str) -> bool:
        """Remove permission from role"""
        for i, perm in enumerate(self.permissions):
            if perm.id == permission_id:
                self.permissions.pop(i)
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if role has specific permission"""
        return any(perm.name == permission_name for perm in self.permissions)
    
    def get_permissions_for_resource(self, resource: str) -> List[Permission]:
        """Get permissions for specific resource"""
        return [perm for perm in self.permissions if perm.resource == resource]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': [perm.to_dict() for perm in self.permissions],
            'parent_roles': self.parent_roles,
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class User:
    """User model with authentication and authorization data"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    password_hash: str = ""
    salt: str = ""
    roles: List[str] = field(default_factory=list)  # Role IDs
    status: UserStatus = UserStatus.ACTIVE
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: str = ""
    api_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_active(self) -> bool:
        """Check if user account is active"""
        if self.status != UserStatus.ACTIVE:
            return False
        
        if self.locked_until and self.locked_until > datetime.now(timezone.utc):
            return False
        
        return True
    
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        return self.locked_until and self.locked_until > datetime.now(timezone.utc)
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def reset_failed_login(self) -> None:
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.updated_at = datetime.now(timezone.utc)
    
    def add_role(self, role_id: str) -> None:
        """Add role to user"""
        if role_id not in self.roles:
            self.roles.append(role_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_role(self, role_id: str) -> bool:
        """Remove role from user"""
        if role_id in self.roles:
            self.roles.remove(role_id)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'roles': self.roles,
            'status': self.status.value,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'mfa_enabled': self.mfa_enabled,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    password_policy: Dict[str, Any] = field(default_factory=dict)
    session_policy: Dict[str, Any] = field(default_factory=dict)
    mfa_policy: Dict[str, Any] = field(default_factory=dict)
    rate_limit_policy: Dict[str, Any] = field(default_factory=dict)
    audit_policy: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_password_requirements(self) -> Dict[str, Any]:
        """Get password requirements from policy"""
        return self.password_policy.get('requirements', {})
    
    def get_session_timeout(self) -> int:
        """Get session timeout in seconds"""
        return self.session_policy.get('timeout_seconds', 3600)
    
    def is_mfa_required(self) -> bool:
        """Check if MFA is required"""
        return self.mfa_policy.get('required', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'password_policy': self.password_policy,
            'session_policy': self.session_policy,
            'mfa_policy': self.mfa_policy,
            'rate_limit_policy': self.rate_limit_policy,
            'audit_policy': self.audit_policy,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class SecurityContext:
    """Security context for current operation"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    permissions: List[Permission] = field(default_factory=list)
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_role(self, role_name: str) -> bool:
        """Check if context has specific role"""
        return role_name in self.roles
    
    def has_permission(self, permission_name: str, resource: str = None) -> bool:
        """Check if context has specific permission"""
        for perm in self.permissions:
            if perm.name == permission_name:
                if resource is None or perm.resource == resource:
                    return True
        return False
    
    def can_perform_action(self, action: str, resource: str) -> bool:
        """Check if context can perform action on resource"""
        for perm in self.permissions:
            if perm.resource == resource and perm.has_action(action):
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'roles': self.roles,
            'permissions': [perm.to_dict() for perm in self.permissions],
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class AuthenticationResult:
    """Result of authentication attempt"""
    success: bool = False
    user: Optional[User] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str = ""
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if authentication result is valid"""
        if not self.success:
            return False
        
        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'user': self.user.to_dict() if self.user else None,
            'token': self.token,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'message': self.message,
            'error_code': self.error_code,
            'metadata': self.metadata
        }


@dataclass
class AuthorizationResult:
    """Result of authorization check"""
    allowed: bool = False
    user_id: Optional[str] = None
    resource: str = ""
    action: str = ""
    required_permissions: List[str] = field(default_factory=list)
    granted_permissions: List[str] = field(default_factory=list)
    message: str = ""
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'allowed': self.allowed,
            'user_id': self.user_id,
            'resource': self.resource,
            'action': self.action,
            'required_permissions': self.required_permissions,
            'granted_permissions': self.granted_permissions,
            'message': self.message,
            'error_code': self.error_code,
            'metadata': self.metadata
        }
