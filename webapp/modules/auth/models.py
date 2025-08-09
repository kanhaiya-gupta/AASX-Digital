"""
Modern Authentication Models
===========================

Updated authentication models using the centralized database system.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
import uuid

# Import the centralized user model
from src.shared.models.user import User as SharedUser

class UserCreate(BaseModel):
    """Model for user registration"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    confirm_password: str
    organization_id: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v

class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str
    remember_me: Optional[bool] = False

class UserUpdate(BaseModel):
    """Model for user profile updates"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    organization_id: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(BaseModel):
    """Model for user response (without sensitive data)"""
    user_id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    organization_id: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    role: str
    is_active: bool
    last_login: Optional[str] = None
    created_at: str
    updated_at: str
    mfa_enabled: Optional[bool] = False
    email_verified: Optional[bool] = False
    phone_verified: Optional[bool] = False
    
    @classmethod
    def from_shared_user(cls, user: SharedUser) -> 'UserResponse':
        """Create UserResponse from SharedUser"""
        return cls(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            organization_id=user.org_id,
            phone=getattr(user, 'phone', None),
            job_title=getattr(user, 'job_title', None),
            department=getattr(user, 'department', None),
            bio=getattr(user, 'bio', None),
            role=user.role,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
            mfa_enabled=getattr(user, 'mfa_enabled', False),
            email_verified=getattr(user, 'email_verified', False),
            phone_verified=getattr(user, 'phone_verified', False)
        )

class Token(BaseModel):
    """Model for authentication token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    """Model for token data"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = None

class PasswordReset(BaseModel):
    """Model for password reset"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Model for password reset confirmation"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class PasswordChange(BaseModel):
    """Model for password change"""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserPreferences(BaseModel):
    """Model for user preferences"""
    # UI/UX Preferences
    theme: str = "light"  # light, dark, auto
    language: str = "en"  # en, es, fr, de, etc.
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"  # YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY
    time_format: str = "24h"  # 12h, 24h
    
    # Notification Preferences
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    notification_frequency: str = "immediate"  # immediate, daily, weekly, never
    
    # Privacy Preferences
    profile_visibility: str = "private"  # public, private, friends
    data_sharing: bool = False
    analytics_tracking: bool = True
    
    # Security Preferences
    session_timeout: int = 30  # minutes
    require_mfa: bool = False
    login_notifications: bool = True
    
    # Application Preferences
    default_page_size: int = 20
    auto_save: bool = True
    show_tutorials: bool = True
    compact_mode: bool = False
    
    # Communication Preferences
    email_digest: bool = False
    digest_frequency: str = "weekly"  # daily, weekly, monthly
    marketing_emails: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme": "light",
                "language": "en",
                "timezone": "UTC",
                "date_format": "YYYY-MM-DD",
                "time_format": "24h",
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True,
                "notification_frequency": "immediate",
                "profile_visibility": "private",
                "data_sharing": False,
                "analytics_tracking": True,
                "session_timeout": 30,
                "require_mfa": False,
                "login_notifications": True,
                "default_page_size": 20,
                "auto_save": True,
                "show_tutorials": True,
                "compact_mode": False,
                "email_digest": False,
                "digest_frequency": "weekly",
                "marketing_emails": False
            }
        }

class UserActivity(BaseModel):
    """Model for user activity logging"""
    user_id: str
    activity_type: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = datetime.now()

# MFA-related models for Phase 2: Authentication Enhancement
class MFASetup(BaseModel):
    """Model for MFA setup"""
    mfa_type: str  # "totp", "sms", "email"
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class MFAVerify(BaseModel):
    """Model for MFA verification"""
    user_id: str
    mfa_type: str
    code: str
    remember_device: Optional[bool] = False

class MFABackupCodes(BaseModel):
    """Model for MFA backup codes"""
    user_id: str
    codes: List[str]
    generated_at: datetime = datetime.now()

class MFARecovery(BaseModel):
    """Model for MFA recovery"""
    user_id: str
    backup_code: str

class SessionInfo(BaseModel):
    """Model for session information"""
    session_id: str
    user_id: str
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = datetime.now()
    last_activity: datetime = datetime.now()
    expires_at: Optional[datetime] = None
    is_active: bool = True

class SocialLogin(BaseModel):
    """Model for social login"""
    provider: str  # "google", "facebook", "apple"
    access_token: str
    user_info: Optional[Dict[str, Any]] = None

class PublicProfile(BaseModel):
    """Model for public profile information"""
    user_id: str
    username: str
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    organization_name: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    is_public: bool = False
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "full_name": "John Doe",
                "job_title": "Software Engineer",
                "department": "Engineering",
                "bio": "Passionate software engineer with expertise in Python and web development.",
                "avatar_url": "/static/avatars/johndoe.jpg",
                "organization_name": "Tech Corp",
                "location": "San Francisco, CA",
                "website": "https://johndoe.dev",
                "social_links": {
                    "linkedin": "https://linkedin.com/in/johndoe",
                    "github": "https://github.com/johndoe",
                    "twitter": "https://twitter.com/johndoe"
                },
                "skills": ["Python", "FastAPI", "React", "Docker"],
                "interests": ["AI/ML", "Web Development", "Open Source"],
                "is_public": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class PublicProfileUpdate(BaseModel):
    """Model for updating public profile information"""
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    is_public: Optional[bool] = None
    
    @validator('website')
    def validate_website(cls, v):
        if v is not None and v:
            if not v.startswith(('http://', 'https://')):
                v = 'https://' + v
        return v
    
    @validator('social_links')
    def validate_social_links(cls, v):
        if v is not None:
            for platform, url in v.items():
                if url and not url.startswith(('http://', 'https://')):
                    v[platform] = 'https://' + url
        return v 

class ProfileVerification(BaseModel):
    """Model for profile verification information"""
    user_id: str
    verification_type: str  # 'email', 'phone', 'identity', 'address'
    status: str  # 'pending', 'verified', 'failed', 'expired'
    verification_data: Optional[Dict[str, Any]] = None
    verification_code: Optional[str] = None
    expires_at: Optional[str] = None
    verified_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "verification_type": "email",
                "status": "verified",
                "verification_data": {
                    "email": "user@example.com",
                    "verified_at": "2024-01-01T00:00:00Z"
                },
                "verification_code": None,
                "expires_at": None,
                "verified_at": "2024-01-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class ProfileVerificationRequest(BaseModel):
    """Model for requesting profile verification"""
    verification_type: str  # 'email', 'phone', 'identity', 'address'
    contact_info: Optional[str] = None  # email, phone, etc.
    verification_data: Optional[Dict[str, Any]] = None  # Additional data for verification
    
    @validator('verification_type')
    def validate_verification_type(cls, v):
        allowed_types = ['email', 'phone', 'identity', 'address']
        if v not in allowed_types:
            raise ValueError(f'Verification type must be one of: {allowed_types}')
        return v

class ProfileVerificationConfirm(BaseModel):
    """Model for confirming profile verification"""
    verification_type: str
    verification_code: str
    
    @validator('verification_type')
    def validate_verification_type(cls, v):
        allowed_types = ['email', 'phone', 'identity', 'address']
        if v not in allowed_types:
            raise ValueError(f'Verification type must be one of: {allowed_types}')
        return v

class ProfileVerificationStatus(BaseModel):
    """Model for profile verification status"""
    user_id: str
    email_verified: bool = False
    phone_verified: bool = False
    identity_verified: bool = False
    address_verified: bool = False
    overall_verification_status: str = "unverified"  # unverified, partial, verified
    verification_score: int = 0  # 0-100
    last_verification_update: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email_verified": True,
                "phone_verified": False,
                "identity_verified": False,
                "address_verified": False,
                "overall_verification_status": "partial",
                "verification_score": 25,
                "last_verification_update": "2024-01-01T00:00:00Z"
            }
        } 

class CustomRole(BaseModel):
    """Model for custom roles"""
    role_id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    inherits_from: Optional[str] = None  # Base role to inherit from
    is_active: bool = True
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "123e4567-e89b-12d3-a456-426614174000",
                "organization_id": "org123",
                "name": "Project Manager",
                "description": "Manages specific projects within the organization",
                "permissions": ["read", "write", "manage"],
                "inherits_from": "manager",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class CustomRoleCreate(BaseModel):
    """Model for creating custom roles"""
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    inherits_from: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Role name must be at least 2 characters long')
        if len(v) > 50:
            raise ValueError('Role name must be less than 50 characters')
        return v.strip()
    
    @validator('permissions')
    def validate_permissions(cls, v):
        valid_permissions = ["read", "write", "manage", "admin", "super_admin"]
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f'Invalid permission: {permission}. Must be one of: {valid_permissions}')
        return v

class CustomRoleUpdate(BaseModel):
    """Model for updating custom roles"""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    inherits_from: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Role name must be at least 2 characters long')
            if len(v) > 50:
                raise ValueError('Role name must be less than 50 characters')
            return v.strip()
        return v
    
    @validator('permissions')
    def validate_permissions(cls, v):
        if v is not None:
            valid_permissions = ["read", "write", "manage", "admin", "super_admin"]
            for permission in v:
                if permission not in valid_permissions:
                    raise ValueError(f'Invalid permission: {permission}. Must be one of: {valid_permissions}')
        return v

class RoleAssignment(BaseModel):
    """Model for role assignments"""
    assignment_id: str
    user_id: str
    role_id: str  # Can be either built-in role or custom role ID
    organization_id: str
    assigned_by: str
    assigned_at: str
    expires_at: Optional[str] = None
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user123",
                "role_id": "role456",
                "organization_id": "org123",
                "assigned_by": "admin123",
                "assigned_at": "2024-01-01T00:00:00Z",
                "expires_at": None,
                "is_active": True
            }
        } 

# Organization Settings Models
class OrganizationSettings(BaseModel):
    """Model for organization settings"""
    organization_id: str
    branding: Dict[str, Any] = {
        "logo_url": None,
        "primary_color": "#1e3c72",
        "secondary_color": "#2a5298",
        "accent_color": "#ffd700",
        "company_name": None,
        "tagline": None
    }
    configuration: Dict[str, Any] = {
        "default_language": "en",
        "default_timezone": "UTC",
        "session_timeout": 30,
        "require_mfa": False,
        "allow_public_profiles": True,
        "max_file_size_mb": 100,
        "allowed_file_types": ["pdf", "doc", "docx", "xls", "xlsx", "txt", "json", "xml"]
    }
    notifications: Dict[str, Any] = {
        "email_notifications": True,
        "sms_notifications": False,
        "push_notifications": True,
        "notification_frequency": "immediate"
    }
    security: Dict[str, Any] = {
        "password_policy": {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": False
        },
        "session_management": {
            "max_concurrent_sessions": 5,
            "session_timeout_minutes": 30,
            "remember_me_days": 30
        }
    }
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "branding": {
                    "logo_url": "https://example.com/logo.png",
                    "primary_color": "#1e3c72",
                    "secondary_color": "#2a5298",
                    "accent_color": "#ffd700",
                    "company_name": "Example Corp",
                    "tagline": "Building the future"
                },
                "configuration": {
                    "default_language": "en",
                    "default_timezone": "UTC",
                    "session_timeout": 30,
                    "require_mfa": False,
                    "allow_public_profiles": True,
                    "max_file_size_mb": 100,
                    "allowed_file_types": ["pdf", "doc", "docx", "xls", "xlsx", "txt", "json", "xml"]
                },
                "notifications": {
                    "email_notifications": True,
                    "sms_notifications": False,
                    "push_notifications": True,
                    "notification_frequency": "immediate"
                },
                "security": {
                    "password_policy": {
                        "min_length": 8,
                        "require_uppercase": True,
                        "require_lowercase": True,
                        "require_numbers": True,
                        "require_special_chars": False
                    },
                    "session_management": {
                        "max_concurrent_sessions": 5,
                        "session_timeout_minutes": 30,
                        "remember_me_days": 30
                    }
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class OrganizationSettingsUpdate(BaseModel):
    """Model for updating organization settings"""
    branding: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None

class OrganizationAnalytics(BaseModel):
    """Model for organization analytics"""
    organization_id: str
    user_analytics: Dict[str, Any] = {
        "total_users": 0,
        "active_users": 0,
        "new_users_this_month": 0,
        "user_growth_rate": 0.0
    }
    usage_analytics: Dict[str, Any] = {
        "total_projects": 0,
        "total_files": 0,
        "storage_used_gb": 0.0,
        "storage_limit_gb": 10,
        "api_requests_this_month": 0
    }
    performance_metrics: Dict[str, Any] = {
        "average_response_time_ms": 0,
        "uptime_percentage": 99.9,
        "error_rate": 0.0
    }
    activity_insights: Dict[str, Any] = {
        "most_active_users": [],
        "most_used_features": [],
        "peak_usage_hours": []
    }
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_analytics": {
                    "total_users": 150,
                    "active_users": 120,
                    "new_users_this_month": 15,
                    "user_growth_rate": 10.5
                },
                "usage_analytics": {
                    "total_projects": 45,
                    "total_files": 1200,
                    "storage_used_gb": 8.5,
                    "storage_limit_gb": 10,
                    "api_requests_this_month": 50000
                },
                "performance_metrics": {
                    "average_response_time_ms": 250,
                    "uptime_percentage": 99.9,
                    "error_rate": 0.1
                },
                "activity_insights": {
                    "most_active_users": ["user1", "user2", "user3"],
                    "most_used_features": ["file_upload", "data_analysis", "reporting"],
                    "peak_usage_hours": ["09:00", "14:00", "16:00"]
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class OrganizationBilling(BaseModel):
    """Model for organization billing"""
    organization_id: str
    subscription: Dict[str, Any] = {
        "tier": "professional",
        "status": "active",
        "start_date": None,
        "end_date": None,
        "auto_renew": True
    }
    billing_info: Dict[str, Any] = {
        "billing_email": None,
        "billing_address": None,
        "payment_method": None,
        "tax_id": None
    }
    usage_billing: Dict[str, Any] = {
        "current_period_start": None,
        "current_period_end": None,
        "usage_amount": 0.0,
        "billing_amount": 0.0,
        "currency": "USD"
    }
    payment_history: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "subscription": {
                    "tier": "professional",
                    "status": "active",
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-12-31T23:59:59Z",
                    "auto_renew": True
                },
                "billing_info": {
                    "billing_email": "billing@example.com",
                    "billing_address": "123 Main St, City, State 12345",
                    "payment_method": "credit_card",
                    "tax_id": "12-3456789"
                },
                "usage_billing": {
                    "current_period_start": "2024-01-01T00:00:00Z",
                    "current_period_end": "2024-01-31T23:59:59Z",
                    "usage_amount": 85.50,
                    "billing_amount": 99.00,
                    "currency": "USD"
                },
                "payment_history": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        } 