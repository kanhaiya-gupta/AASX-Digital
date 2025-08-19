"""
User Model
=========

Data model for users in the AAS Data Modeling framework.
"""

import uuid
from typing import Optional
from datetime import datetime
from .base_model import BaseModel
from pydantic import Field

class User(BaseModel):
    """User data model with comprehensive user management fields."""
    
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique user identifier")
    username: str = Field(..., description="Username for login")
    email: Optional[str] = Field(default=None, description="User email address")
    full_name: Optional[str] = Field(default=None, description="User's full name")
    org_id: Optional[str] = Field(default=None, description="Organization ID")
    phone: Optional[str] = Field(default=None, description="Phone number")
    job_title: Optional[str] = Field(default=None, description="Job title")
    department: Optional[str] = Field(default=None, description="Department")
    bio: Optional[str] = Field(default=None, description="User biography")
    password_hash: Optional[str] = Field(default=None, description="Hashed password")
    role: str = Field(default="user", description="User role")
    is_active: bool = Field(default=True, description="Account active status")
    last_login: Optional[str] = Field(default=None, description="Last login timestamp")
    is_verified: bool = Field(default=False, description="Account verification status")
    email_verified: bool = Field(default=False, description="Email verification status")
    phone_verified: bool = Field(default=False, description="Phone verification status")
    mfa_enabled: bool = Field(default=False, description="Multi-factor authentication enabled")
    mfa_secret: Optional[str] = Field(default=None, description="MFA secret key")
    last_password_change: Optional[str] = Field(default=None, description="Last password change timestamp")
    failed_login_attempts: int = Field(default=0, description="Failed login attempts count")
    account_locked_until: Optional[str] = Field(default=None, description="Account lock expiration")
    preferences: str = Field(default="{}", description="User preferences (JSON)")
    avatar_url: Optional[str] = Field(default=None, description="Avatar image URL")
    timezone: str = Field(default="UTC", description="User timezone")
    language: str = Field(default="en", description="Preferred language")
    verification_token: Optional[str] = Field(default=None, description="Email verification token")
    reset_token: Optional[str] = Field(default=None, description="Password reset token")
    reset_token_expires: Optional[datetime] = Field(default=None, description="Reset token expiration")
    
    # User Consent & Privacy Management
    consent_version: str = Field(default="1.0", description="Current consent agreement version")
    consent_granted_at: Optional[datetime] = Field(default=None, description="When consent was given")
    consent_revoked_at: Optional[datetime] = Field(default=None, description="When consent was withdrawn")
    privacy_preferences: str = Field(default="{}", description="Privacy settings (JSON)")
    data_processing_consent: str = Field(default="{}", description="Specific consent types (JSON)")
    marketing_consent: bool = Field(default=False, description="Marketing communications consent")
    third_party_sharing_consent: bool = Field(default=False, description="Data sharing permissions")
    data_retention_consent: bool = Field(default=False, description="Data retention consent")
    
    # Advanced User Management
    last_activity: Optional[datetime] = Field(default=None, description="Last user activity timestamp")
    session_count: int = Field(default=0, description="Number of active sessions")
    ip_whitelist: str = Field(default="[]", description="Allowed IP addresses (JSON)")
    device_fingerprint: Optional[str] = Field(default=None, description="Device identification")
    
    # Compliance & Audit
    data_access_level: str = Field(default="standard", description="Data sensitivity access level")
    compliance_requirements: str = Field(default="[]", description="Regulatory requirements (JSON)")
    audit_log_enabled: bool = Field(default=True, description="Audit trail settings")
    data_classification: str = Field(default="internal", description="Data sensitivity classification")
    
    created_at: Optional[datetime] = Field(default=None, description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    def validate(self) -> bool:
        """Validate user data."""
        if not self.username or not self.username.strip():
            raise ValueError("Username is required")
        
        if len(self.username) > 50:
            raise ValueError("Username must be less than 50 characters")
        
        if self.email and len(self.email) > 255:
            raise ValueError("Email must be less than 255 characters")
        
        if self.full_name and len(self.full_name) > 100:
            raise ValueError("Full name must be less than 100 characters")
        
        if self.phone and len(self.phone) > 20:
            raise ValueError("Phone number must be less than 20 characters")
        
        if self.job_title and len(self.job_title) > 100:
            raise ValueError("Job title must be less than 100 characters")
        
        if self.department and len(self.department) > 100:
            raise ValueError("Department must be less than 100 characters")
        
        if self.bio and len(self.bio) > 1000:
            raise ValueError("Bio must be less than 1000 characters")
        
        valid_roles = ["super_admin", "admin", "manager", "user", "viewer"]
        if self.role not in valid_roles:
            raise ValueError(f"Role must be one of: {valid_roles}")
        
        # Validate data access level
        valid_access_levels = ["restricted", "standard", "elevated", "admin"]
        if self.data_access_level not in valid_access_levels:
            raise ValueError(f"Data access level must be one of: {valid_access_levels}")
        
        # Validate data classification
        valid_classifications = ["public", "internal", "confidential", "restricted"]
        if self.data_classification not in valid_classifications:
            raise ValueError(f"Data classification must be one of: {valid_classifications}")
        
        # Validate consent version format
        if not self.consent_version or not self.consent_version.strip():
            raise ValueError("Consent version is required")
        
        # Validate session count
        if self.session_count < 0:
            raise ValueError("Session count cannot be negative")
        
        return True
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now().isoformat()
        self.updated_at = datetime.now()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission based on role."""
        if not self.is_active:
            return False
        
        role_permissions = {
            "viewer": ["read"],
            "user": ["read", "write"],
            "manager": ["read", "write", "manage"],
            "admin": ["read", "write", "manage", "admin"],
            "super_admin": ["read", "write", "manage", "admin", "super_admin"]
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return permission in user_permissions
    
    def grant_consent(self, consent_type: str = "general", version: str = None) -> None:
        """Grant consent for data processing."""
        from datetime import datetime
        import json
        
        if version:
            self.consent_version = version
        
        self.consent_granted_at = datetime.now().isoformat()
        self.consent_revoked_at = None
        
        # Update data processing consent
        try:
            current_consent = json.loads(self.data_processing_consent) if self.data_processing_consent else {}
            current_consent[consent_type] = {
                "granted_at": self.consent_granted_at,
                "version": self.consent_version,
                "status": "active"
            }
            self.data_processing_consent = json.dumps(current_consent)
        except json.JSONDecodeError:
            self.data_processing_consent = json.dumps({
                consent_type: {
                    "granted_at": self.consent_granted_at,
                    "version": self.consent_version,
                    "status": "active"
                }
            })
    
    def revoke_consent(self, consent_type: str = "general") -> None:
        """Revoke consent for data processing."""
        from datetime import datetime
        import json
        
        self.consent_revoked_at = datetime.now().isoformat()
        
        # Update data processing consent
        try:
            current_consent = json.loads(self.data_processing_consent) if self.data_processing_consent else {}
            if consent_type in current_consent:
                current_consent[consent_type]["status"] = "revoked"
                current_consent[consent_type]["revoked_at"] = self.consent_revoked_at
            self.data_processing_consent = json.dumps(current_consent)
        except json.JSONDecodeError:
            pass
    
    def has_valid_consent(self, consent_type: str = "general") -> bool:
        """Check if user has valid consent for data processing."""
        if not self.consent_granted_at:
            return False
        
        if self.consent_revoked_at:
            return False
        
        # Check specific consent type
        try:
            import json
            current_consent = json.loads(self.data_processing_consent) if self.data_processing_consent else {}
            if consent_type in current_consent:
                return current_consent[consent_type].get("status") == "active"
        except json.JSONDecodeError:
            pass
        
        return True
    
    def can_access_data_level(self, required_level: str) -> bool:
        """Check if user can access data at a specific sensitivity level."""
        access_hierarchy = {
            "restricted": 0,
            "standard": 1,
            "elevated": 2,
            "admin": 3
        }
        
        user_level = access_hierarchy.get(self.data_access_level, 0)
        required_level_num = access_hierarchy.get(required_level, 0)
        
        return user_level >= required_level_num
    
    def update_activity(self) -> None:
        """Update user activity timestamp and session count."""
        from datetime import datetime
        self.last_activity = datetime.now().isoformat()
        self.updated_at = datetime.now()
    
    def add_session(self) -> None:
        """Increment session count."""
        self.session_count += 1
        self.update_activity()
    
    def remove_session(self) -> None:
        """Decrement session count."""
        if self.session_count > 0:
            self.session_count -= 1
        self.update_activity() 