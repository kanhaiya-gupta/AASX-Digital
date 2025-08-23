"""
Modern Authentication Module
===========================

Updated authentication module using the integration service architecture.
Provides user authentication, authorization, and management capabilities
through thin integration services that delegate to the backend engine.
"""

# Import the router for module registration
from .routes import router

# Import integration services for external access if needed
from .services import (
    AuthIntegrationService,
    SecurityIntegrationService,
    UserPreferencesService,
    ProfileManagementService,
    ProfileVerificationService,
    CustomRoleService,
    OrganizationManagementService,
    SessionManagementService,
    ComplianceService
)

__version__ = "2.0.0"
__author__ = "AASX Digital Twin Team"

__all__ = [
    # Router (main module export)
    "router",
    
    # Integration services (for external access)
    "AuthIntegrationService",
    "SecurityIntegrationService",
    "UserPreferencesService",
    "ProfileManagementService",
    "ProfileVerificationService",
    "CustomRoleService",
    "OrganizationManagementService",
    "SessionManagementService",
    "ComplianceService"
] 