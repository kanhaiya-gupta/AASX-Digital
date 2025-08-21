"""
Authentication Services Package.

This package provides comprehensive authentication and authorization services
for the AAS Data Modeling Engine, including user management, role-based
access control, session management, and metrics collection.
"""

# Import all services and models
from .user_service import UserService, UserProfile, UserPreferences
from .role_service import RoleService, Role, Permission, PermissionLevel, RoleAssignment
from .auth_service import AuthService, Session, AuthResult, SecurityPolicy
from .metrics_service import MetricsService, UserMetrics, SystemMetrics, ActivityMetrics, PerformanceMetrics

__all__ = [
    # User Service
    "UserService",
    "UserProfile", 
    "UserPreferences",
    
    # Role Service
    "RoleService",
    "Role",
    "Permission",
    "PermissionLevel",
    "RoleAssignment",
    
    # Auth Service
    "AuthService",
    "Session",
    "AuthResult",
    "SecurityPolicy",
    
    # Metrics Service
    "MetricsService",
    "UserMetrics",
    "SystemMetrics",
    "ActivityMetrics",
    "PerformanceMetrics",
]

# Version information
__version__ = "1.0.0"
__author__ = "AAS Data Modeling Engine Team"
__description__ = "Authentication and Authorization Services for AAS Data Modeling Engine"
