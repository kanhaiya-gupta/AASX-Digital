"""
User Model
=========

Data model for users in the AAS Data Modeling framework.
"""

import uuid
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from .base_model import BaseModel

@dataclass
class User(BaseModel):
    """User data model."""
    
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    org_id: Optional[str] = None
    password_hash: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    last_login: Optional[str] = None
    
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
        
        valid_roles = ["super_admin", "admin", "manager", "user", "viewer"]
        if self.role not in valid_roles:
            raise ValueError(f"Role must be one of: {valid_roles}")
        
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