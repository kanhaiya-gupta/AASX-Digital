"""
Modern Authentication Utilities
==============================

Updated authentication utilities using the centralized database system.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .database import AuthDatabase
from .models import TokenData, UserResponse

logger = logging.getLogger(__name__)

# Initialize auth database
auth_db = AuthDatabase()

# Security scheme
security = HTTPBearer()

def get_current_user_from_token(token: str) -> Optional[str]:
    """Get current user from JWT token"""
    try:
        payload = auth_db.verify_token(token)
        if payload is None:
            return None
        
        username: str = payload.get("username")
        if username is None:
            return None
        
        return username
    except Exception as e:
        logger.error(f"Error getting user from token: {e}")
        return None

def get_current_user_data_from_token(token: str) -> Optional[TokenData]:
    """Get current user data from JWT token"""
    try:
        payload = auth_db.verify_token(token)
        if payload is None:
            return None
        
        return TokenData(
            username=payload.get("username"),
            user_id=payload.get("user_id"),
            role=payload.get("role"),
            organization_id=payload.get("organization_id")
        )
    except Exception as e:
        logger.error(f"Error getting user data from token: {e}")
        return None

def create_access_token(user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token for user"""
    try:
        to_encode = {
            "username": user_data["username"],
            "user_id": user_data["user_id"],
            "role": user_data["role"],
            "organization_id": user_data.get("organization_id")
        }
        
        return auth_db.create_access_token(to_encode, expires_delta)
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(status_code=500, detail="Could not create access token")

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username and password"""
    try:
        user = auth_db.authenticate_user(username, password)
        if user:
            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "organization_id": user.organization_id,
                "is_active": user.is_active
            }
        return None
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None

def get_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """Get user from request (from token or session)"""
    try:
        # Try to get token from cookies first
        token = request.cookies.get("access_token")
        if not token:
            # Try to get from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return None
        
        username = get_current_user_from_token(token)
        if not username:
            return None
        
        user = auth_db.get_user_by_username(username)
        if not user or not user.is_active:
            return None
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": user.organization_id,
            "is_active": user.is_active,
            "last_login": user.last_login
        }
    except Exception as e:
        logger.error(f"Error getting user from request: {e}")
        return None

def require_auth(request: Request) -> Dict[str, Any]:
    """Require authentication - raise exception if not authenticated"""
    user = get_user_from_request(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

def require_admin(request: Request) -> Dict[str, Any]:
    """Require admin role"""
    user = require_auth(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def require_manager_or_admin(request: Request) -> Dict[str, Any]:
    """Require manager or admin role"""
    user = require_auth(request)
    if user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Manager or admin access required")
    return user

def log_user_activity(request: Request, user_id: str, activity_type: str, 
                     resource_type: str = None, resource_id: str = None, 
                     details: dict = None) -> bool:
    """Log user activity with request context"""
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        
        return auth_db.log_user_activity(
            user_id=user_id,
            activity_type=activity_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        return False

def validate_password_strength(password: str) -> dict:
    """Validate password strength and return result with message"""
    if len(password) < 8:
        return {"is_valid": False, "message": "Password must be at least 8 characters long"}
    if not any(c.isupper() for c in password):
        return {"is_valid": False, "message": "Password must contain at least one uppercase letter"}
    if not any(c.islower() for c in password):
        return {"is_valid": False, "message": "Password must contain at least one lowercase letter"}
    if not any(c.isdigit() for c in password):
        return {"is_valid": False, "message": "Password must contain at least one digit"}
    return {"is_valid": True, "message": "Password meets strength requirements"}

def get_password_strength_message(password: str) -> str:
    """Get password strength validation message"""
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one digit"
    return "Password meets strength requirements"

def sanitize_user_input(input_str: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
    sanitized = input_str
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def validate_email_format(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_user_permissions(user_role: str) -> list:
    """Get user permissions based on role with inheritance"""
    # Define role hierarchy and permissions
    role_hierarchy = {
        "super_admin": {
            "permissions": ["read", "write", "manage", "admin", "super_admin"],
            "inherits": []
        },
        "admin": {
            "permissions": ["read", "write", "manage", "admin"],
            "inherits": ["manager"]
        },
        "manager": {
            "permissions": ["read", "write", "manage"],
            "inherits": ["user"]
        },
        "user": {
            "permissions": ["read", "write"],
            "inherits": ["viewer"]
        },
        "viewer": {
            "permissions": ["read"],
            "inherits": []
        }
    }
    
    def get_inherited_permissions(role: str, visited: set = None) -> set:
        """Recursively get all inherited permissions for a role"""
        if visited is None:
            visited = set()
        
        if role in visited:
            return set()  # Prevent circular inheritance
        
        visited.add(role)
        role_config = role_hierarchy.get(role, {"permissions": [], "inherits": []})
        
        # Get direct permissions
        permissions = set(role_config["permissions"])
        
        # Get inherited permissions
        for inherited_role in role_config["inherits"]:
            inherited_permissions = get_inherited_permissions(inherited_role, visited.copy())
            permissions.update(inherited_permissions)
        
        return permissions
    
    # Get all permissions including inherited ones
    all_permissions = get_inherited_permissions(user_role)
    return list(all_permissions)

def has_permission(user_role: str, required_permission: str) -> bool:
    """Check if user has required permission (with inheritance)"""
    user_permissions = get_user_permissions(user_role)
    return required_permission in user_permissions

def get_role_hierarchy() -> dict:
    """Get the complete role hierarchy"""
    return {
        "super_admin": {
            "name": "Super Administrator",
            "description": "Full system access with all permissions",
            "permissions": ["read", "write", "manage", "admin", "super_admin"],
            "inherits": [],
            "level": 5
        },
        "admin": {
            "name": "Administrator", 
            "description": "Organization-level administration",
            "permissions": ["read", "write", "manage", "admin"],
            "inherits": ["manager"],
            "level": 4
        },
        "manager": {
            "name": "Manager",
            "description": "Team and project management",
            "permissions": ["read", "write", "manage"],
            "inherits": ["user"],
            "level": 3
        },
        "user": {
            "name": "User",
            "description": "Standard user with basic access",
            "permissions": ["read", "write"],
            "inherits": ["viewer"],
            "level": 2
        },
        "viewer": {
            "name": "Viewer",
            "description": "Read-only access",
            "permissions": ["read"],
            "inherits": [],
            "level": 1
        }
    }

def can_manage_role(user_role: str, target_role: str) -> bool:
    """Check if a user can manage users with the target role"""
    hierarchy = get_role_hierarchy()
    
    user_level = hierarchy.get(user_role, {}).get("level", 0)
    target_level = hierarchy.get(target_role, {}).get("level", 0)
    
    # Users can only manage roles at a lower level
    return user_level > target_level

def get_manageable_roles(user_role: str) -> list:
    """Get list of roles that the user can manage"""
    hierarchy = get_role_hierarchy()
    user_level = hierarchy.get(user_role, {}).get("level", 0)
    
    manageable_roles = []
    for role, config in hierarchy.items():
        if config.get("level", 0) < user_level:
            manageable_roles.append({
                "role": role,
                "name": config.get("name", role),
                "description": config.get("description", ""),
                "level": config.get("level", 0)
            })
    
    return manageable_roles 