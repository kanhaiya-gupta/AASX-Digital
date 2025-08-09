"""
Modern Authentication Models
===========================

Updated authentication models using the centralized database system.
"""

from typing import Optional, Dict, Any
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

class UserUpdate(BaseModel):
    """Model for user profile updates"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    organization_id: Optional[str] = None
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
    role: str
    is_active: bool
    last_login: Optional[str] = None
    created_at: str
    updated_at: str
    
    @classmethod
    def from_shared_user(cls, user: SharedUser) -> 'UserResponse':
        """Create UserResponse from SharedUser"""
        return cls(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            organization_id=user.org_id,
            role=user.role,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )

class Token(BaseModel):
    """Model for authentication token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

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