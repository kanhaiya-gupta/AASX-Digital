"""
Data Platform Module - Central Business Services Hub
===================================================

Central hub for all business operations including file management, project management,
use case management, and organization management. This module provides the business
services that all other modules depend on, replacing the old src/shared services.

Architecture: Integration services that delegate to backend engine services
Pattern: Lazy initialization with async patterns for world-class architecture
"""

# Import the router for module registration
from .routes import router

# Import integration services for external access
from .services import (
    FileManagementService,
    ProjectManagementService,
    UseCaseManagementService,
    OrganizationManagementService,
    UserManagementService,
    SearchService,
    AnalyticsService,
    NotificationService
)

__version__ = "1.0.0"
__author__ = "AASX Digital Twin Team"

__all__ = [
    # Router (main module export)
    "router",

    # Integration services (for external access)
    "FileManagementService",
    "ProjectManagementService",
    "UseCaseManagementService",
    "OrganizationManagementService",
    "UserManagementService",
    "SearchService",
    "AnalyticsService",
    "NotificationService"
]
