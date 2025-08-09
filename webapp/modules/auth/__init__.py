"""
Modern Authentication Module
===========================

Updated authentication module using the centralized database system.
Provides user authentication, authorization, and management capabilities.
"""

from .models import (
    UserCreate, UserLogin, UserResponse, UserUpdate, Token, 
    TokenData, PasswordReset, PasswordResetConfirm, UserActivity
)
from .database import AuthDatabase
from .utils import (
    get_current_user_from_token, get_current_user_data_from_token,
    create_access_token, authenticate_user, get_user_from_request,
    require_auth, require_admin, require_manager_or_admin,
    log_user_activity, validate_password_strength, sanitize_user_input,
    validate_email_format, get_user_permissions, has_permission
)
from .routes import router

__version__ = "2.0.0"
__author__ = "AASX Digital Twin Team"

__all__ = [
    # Models
    "UserCreate",
    "UserLogin", 
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenData",
    "PasswordReset",
    "PasswordResetConfirm",
    "UserActivity",
    
    # Database
    "AuthDatabase",
    
    # Utilities
    "get_current_user_from_token",
    "get_current_user_data_from_token", 
    "create_access_token",
    "authenticate_user",
    "get_user_from_request",
    "require_auth",
    "require_admin",
    "require_manager_or_admin",
    "log_user_activity",
    "validate_password_strength",
    "sanitize_user_input",
    "validate_email_format",
    "get_user_permissions",
    "has_permission",
    
    # Router
    "router"
] 