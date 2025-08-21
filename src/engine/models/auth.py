"""
Authentication Models
====================

Pydantic models for authentication and authorization entities in the AAS Data Modeling Engine.
These models represent users, roles, role assignments, and user metrics.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import hashlib
import secrets

from .base_model import BaseModel as BaseModelParent


class User(BaseModelParent):
    """User data model with comprehensive authentication and business profile fields."""
    
    # Required fields (no defaults)
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    password_hash: str = Field(..., description="Hashed password")
    role: str = Field(..., description="User role")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    is_active: Optional[bool] = Field(default=True, description="Active status")
    org_id: Optional[str] = Field(default=None, description="Organization ID")
    dept_id: Optional[str] = Field(default=None, description="Department ID")
    last_login: Optional[str] = Field(default=None, description="Last login timestamp")
    
    # Business profile information
    bio: Optional[str] = Field(default=None, description="User biography")
    location: Optional[str] = Field(default=None, description="User location")
    website: Optional[str] = Field(default=None, description="User website")
    skills: Optional[str] = Field(default="{}", description="User skills")
    interests: Optional[str] = Field(default="{}", description="User interests")
    is_public_profile: Optional[bool] = Field(default=False, description="Public profile visibility")
    
    # MFA and security settings
    mfa_enabled: Optional[bool] = Field(default=False, description="MFA enabled")
    mfa_secret: Optional[str] = Field(default=None, description="MFA secret")
    mfa_backup_codes: Optional[str] = Field(default="{}", description="MFA backup codes")
    mfa_last_used: Optional[str] = Field(default=None, description="MFA last used timestamp")
    
    # Verification and password management
    email_verified: Optional[bool] = Field(default=False, description="Email verification status")
    email_verification_code: Optional[str] = Field(default=None, description="Email verification code")
    email_verification_expires: Optional[str] = Field(default=None, description="Email verification expiry")
    password_reset_code: Optional[str] = Field(default=None, description="Password reset code")
    password_reset_expires: Optional[str] = Field(default=None, description="Password reset expiry")
    password_changed_at: Optional[str] = Field(default=None, description="Password change timestamp")
    password_expires_at: Optional[str] = Field(default=None, description="Password expiry timestamp")
    
    # Social authentication
    social_provider: Optional[str] = Field(default=None, description="Social provider")
    social_provider_id: Optional[str] = Field(default=None, description="Social provider ID")
    social_access_token: Optional[str] = Field(default=None, description="Social access token")
    social_refresh_token: Optional[str] = Field(default=None, description="Social refresh token")
    social_token_expires: Optional[str] = Field(default=None, description="Social token expiry")
    social_profile_data: Optional[str] = Field(default="{}", description="Social profile data")
    social_links: Optional[str] = Field(default="{}", description="Social media links")
    
    # Role and permission management
    custom_role_id: Optional[str] = Field(default=None, description="Custom role ID")
    role_assignment_id: Optional[str] = Field(default=None, description="Role assignment ID")
    permissions: Optional[str] = Field(default="{}", description="User permissions")
    role_inheritance: Optional[str] = Field(default="{}", description="Role inheritance")
    
    # Organization settings
    org_settings: Optional[str] = Field(default="{}", description="Organization settings")
    org_permissions: Optional[str] = Field(default="{}", description="Organization permissions")
    org_role: Optional[str] = Field(default=None, description="Organization role")
    
    # Security and compliance
    security_questions: Optional[str] = Field(default="{}", description="Security questions")
    two_factor_method: Optional[str] = Field(default=None, description="Two-factor method")
    login_history: Optional[str] = Field(default="{}", description="Login history")
    failed_login_attempts: Optional[int] = Field(default=0, description="Failed login attempts")
    account_locked_until: Optional[str] = Field(default=None, description="Account lock expiry")
    
    # Audit and tracking
    last_password_change: Optional[str] = Field(default=None, description="Last password change")
    last_role_change: Optional[str] = Field(default=None, description="Last role change")
    last_permission_change: Optional[str] = Field(default=None, description="Last permission change")
    last_security_event: Optional[str] = Field(default=None, description="Last security event")
    created_by: Optional[str] = Field(default=None, description="Creator user ID")
    updated_by: Optional[str] = Field(default=None, description="Updater user ID")
    
    # Metadata and configuration
    preferences: Optional[str] = Field(default="{}", description="User preferences")
    notification_settings: Optional[str] = Field(default="{}", description="Notification settings")
    language: Optional[str] = Field(default="en", description="Language preference")
    timezone: Optional[str] = Field(default="UTC", description="Timezone preference")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if v and '@' not in v:
            raise ValueError("Invalid email format")
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate user role."""
        valid_roles = ['user', 'admin', 'moderator', 'guest']
        if v and v not in valid_roles:
            raise ValueError(f"role must be one of {valid_roles}")
        return v

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using secure hashing."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}"

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        if not self.password_hash or '$' not in self.password_hash:
            return False
        
        salt, stored_hash = self.password_hash.split('$', 1)
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        return hash_obj.hexdigest() == stored_hash

    def get_skills(self) -> Dict[str, List[str]]:
        """Get user skills as a dictionary."""
        # This would need to be implemented based on how skills are stored
        # For now, return empty dict
        return {}

    def get_permissions(self) -> Dict[str, bool]:
        """Get user permissions as a dictionary."""
        # This would need to be implemented based on how permissions are stored
        # For now, return empty dict
        return {}

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        permissions = self.get_permissions()
        return permissions.get(permission, False)


class CustomRole(BaseModelParent):
    """Custom role data model for role management."""
    
    # Required fields (no defaults)
    role_id: str = Field(..., description="Unique role identifier")
    role_name: str = Field(..., description="Role name")
    role_type: str = Field(..., description="Role type")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    role_description: Optional[str] = Field(default=None, description="Role description")
    role_level: Optional[int] = Field(default=1, description="Hierarchy level")
    is_active: Optional[bool] = Field(default=True, description="Active status")
    created_by: Optional[str] = Field(default=None, description="Creator user ID")
    updated_by: Optional[str] = Field(default=None, description="Updater user ID")
    role_metadata: Optional[str] = Field(default="{}", description="Additional role data")

    @field_validator('role_type')
    @classmethod
    def validate_role_type(cls, v):
        """Validate role type field."""
        valid_types = ['system', 'custom', 'inherited']
        if v and v not in valid_types:
            raise ValueError(f"role_type must be one of {valid_types}")
        return v


class RoleAssignment(BaseModelParent):
    """Role assignment data model for user-role mapping."""
    
    # Required fields (no defaults)
    assignment_id: str = Field(..., description="Unique assignment identifier")
    user_id: str = Field(..., description="User ID")
    role_id: str = Field(..., description="Role ID")
    assignment_type: str = Field(..., description="Assignment type")
    assigned_at: str = Field(..., description="Assignment timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    # Optional fields with defaults
    organization_id: Optional[str] = Field(default=None, description="Organization ID")
    expires_at: Optional[str] = Field(default=None, description="Expiry timestamp")
    assigned_by: Optional[str] = Field(default=None, description="Assigner user ID")
    is_active: Optional[bool] = Field(default=True, description="Active status")
    assignment_metadata: Optional[str] = Field(default="{}", description="Additional assignment data")

    @field_validator('assignment_type')
    @classmethod
    def validate_assignment_type(cls, v):
        """Validate assignment type field."""
        valid_types = ['direct', 'inherited', 'temporary']
        if v and v not in valid_types:
            raise ValueError(f"assignment_type must be one of {valid_types}")
        return v


class UserMetrics(BaseModelParent):
    """User metrics data model for performance and security tracking."""
    
    # Required fields (no defaults)
    metric_id: str = Field(..., description="Unique metric identifier")
    user_id: str = Field(..., description="User ID")
    metric_type: str = Field(..., description="Metric type")
    metric_timestamp: str = Field(..., description="Metric timestamp")
    
    # Optional fields with defaults
    login_attempts: Optional[int] = Field(default=0, description="Login attempts")
    successful_logins: Optional[int] = Field(default=0, description="Successful logins")
    failed_logins: Optional[int] = Field(default=0, description="Failed logins")
    login_duration_ms: Optional[int] = Field(default=None, description="Login duration in milliseconds")
    login_source: Optional[str] = Field(default=None, description="Login source")
    login_ip_address: Optional[str] = Field(default=None, description="Login IP address")
    login_user_agent: Optional[str] = Field(default=None, description="Login user agent")

    @field_validator('metric_type')
    @classmethod
    def validate_metric_type(cls, v):
        """Validate metric type field."""
        valid_types = ['login', 'password_change', 'role_change', 'permission_change', 'security_event']
        if v and v not in valid_types:
            raise ValueError(f"metric_type must be one of {valid_types}")
        return v
