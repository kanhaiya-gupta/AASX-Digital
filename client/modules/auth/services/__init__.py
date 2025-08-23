"""
Auth Services Package - Integration Layer
========================================

This package contains integration services that provide a "soft connection"
between the webapp frontend and the backend engine services.

All business logic is delegated to the backend, while these services handle
frontend-specific concerns like data formatting, validation, and UI logic.
"""

# Import all integration services
from .auth_integration_service import AuthIntegrationService
from .security_integration_service import SecurityIntegrationService
from .user_preferences_service import UserPreferencesService
from .profile_management_service import ProfileManagementService
from .profile_verification_service import ProfileVerificationService
from .custom_role_service import CustomRoleService
from .organization_management_service import OrganizationManagementService
from .session_management_service import SessionManagementService
from .compliance_service import ComplianceService

# Export all services
__all__ = [
    # Core integration services
    'AuthIntegrationService',
    'SecurityIntegrationService',
    
    # User management services
    'UserPreferencesService',
    'ProfileManagementService',
    'ProfileVerificationService',
    
    # Role and organization services
    'CustomRoleService',
    'OrganizationManagementService',
    
    # Session and compliance services
    'SessionManagementService',
    'ComplianceService'
]

# Service descriptions for documentation
SERVICE_DESCRIPTIONS = {
    'AuthIntegrationService': 'Handles user authentication, registration, and basic user operations',
    'SecurityIntegrationService': 'Manages MFA, OAuth, and password security operations',
    'UserPreferencesService': 'Handles user preferences and settings management',
    'ProfileManagementService': 'Manages public profiles and profile operations',
    'ProfileVerificationService': 'Handles email/phone verification and verification codes',
    'CustomRoleService': 'Manages custom roles and role assignments',
    'OrganizationManagementService': 'Handles organization settings, analytics, and billing',
    'SessionManagementService': 'Manages user sessions and session tracking',
    'ComplianceService': 'Handles audit logs, compliance reporting, and GDPR requirements'
}
