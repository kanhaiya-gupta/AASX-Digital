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
    """Get user permissions based on role"""
    role_permissions = {
        "viewer": ["read"],
        "user": ["read", "write"],
        "manager": ["read", "write", "manage"],
        "admin": ["read", "write", "manage", "admin"]
    }
    return role_permissions.get(user_role, [])

def has_permission(user_role: str, required_permission: str) -> bool:
    """Check if user has required permission"""
    user_permissions = get_user_permissions(user_role)
    return required_permission in user_permissions 