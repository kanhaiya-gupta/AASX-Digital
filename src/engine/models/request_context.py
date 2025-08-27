"""
Request Context Models - Engine Layer
====================================

Provides standardized models for request context, user context, and authentication state.
All models are pure async and designed for FastAPI integration.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from .enums import UserRole, SecurityLevel


class PermissionLevel(str, Enum):
    """Permission levels for access control."""
    READ = "read"
    WRITE = "write"
    MANAGE = "manage"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class SessionInfo(BaseModel):
    """Session information for user context."""
    session_id: str = Field(..., description="Unique session identifier")
    token: str = Field(..., description="Authentication token")
    created_at: datetime = Field(..., description="Session creation timestamp")
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    ip_address: Optional[str] = Field(None, description="IP address of session")
    user_agent: Optional[str] = Field(None, description="User agent string")
    is_active: bool = Field(True, description="Whether session is active")


class UserContext(BaseModel):
    """Standardized user context for request handling."""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="User's username")
    email: Optional[str] = Field(None, description="User's email address")
    role: UserRole = Field(..., description="User's primary role")
    organization_id: Optional[str] = Field(None, description="User's organization ID")
    department_id: Optional[str] = Field(None, description="User's department ID")
    permissions: Set[PermissionLevel] = Field(default_factory=set, description="User's permissions")
    security_level: SecurityLevel = Field(SecurityLevel.INTERNAL, description="User's security classification")
    is_active: bool = Field(True, description="Whether user account is active")
    session_info: Optional[SessionInfo] = Field(None, description="Current session information")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


class RequestContext(BaseModel):
    """Complete request context including user and request information."""
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    user_context: Optional[UserContext] = Field(None, description="User context if authenticated")
    is_authenticated: bool = Field(False, description="Whether request is authenticated")
    authentication_method: Optional[str] = Field(None, description="Method used for authentication")
    ip_address: Optional[str] = Field(None, description="Request IP address")
    user_agent: Optional[str] = Field(None, description="Request user agent")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    path_params: Dict[str, Any] = Field(default_factory=dict, description="Path parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional request metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


class AuthenticationResult(BaseModel):
    """Result of authentication attempt."""
    success: bool = Field(..., description="Whether authentication was successful")
    user_context: Optional[UserContext] = Field(None, description="User context if successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    requires_mfa: bool = Field(False, description="Whether MFA is required")
    session_info: Optional[SessionInfo] = Field(None, description="Session information if successful")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional authentication metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


class AuthorizationResult(BaseModel):
    """Result of authorization check."""
    success: bool = Field(..., description="Whether authorization was successful")
    allowed: bool = Field(False, description="Whether access is allowed")
    required_permissions: Set[PermissionLevel] = Field(default_factory=set, description="Required permissions")
    user_permissions: Set[PermissionLevel] = Field(default_factory=set, description="User's permissions")
    missing_permissions: Set[PermissionLevel] = Field(default_factory=set, description="Missing permissions")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional authorization metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


# Export all models
__all__ = [
    'PermissionLevel',
    'SessionInfo', 
    'UserContext',
    'RequestContext',
    'AuthenticationResult',
    'AuthorizationResult'
]
