"""
Authentication routes for AASX Digital Twin Analytics Framework
Clean routes that delegate business logic to integration services
"""
import logging
from typing import Optional, List, Any
from fastapi import APIRouter, Request, HTTPException, Depends, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer

# Import our integration services
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

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Create single router for all auth routes
router = APIRouter(tags=["Authentication"])

# Initialize services
auth_service = AuthIntegrationService()
security_service = SecurityIntegrationService()
user_preferences_service = UserPreferencesService()
profile_management_service = ProfileManagementService()
profile_verification_service = ProfileVerificationService()
custom_role_service = CustomRoleService()
organization_management_service = OrganizationManagementService()
session_management_service = SessionManagementService()
compliance_service = ComplianceService()

# ============================================================================
# PAGE ROUTES (HTML responses)
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def auth_dashboard(request: Request):
    """Main authentication dashboard page with tabs"""
    try:
        # Get current user if authenticated
        user = None
        try:
            # This will be handled by the auth integration service
            user = await auth_service.get_current_user_from_request(request)
        except Exception as e:
            logger.warning(f"Could not get user from request: {e}")
            user = None
        
        # Get all users for admin section (if user is admin)
        users = []
        try:
            if user and user.get("role") in ["admin", "super_admin"]:
                users = await auth_service.get_all_users()
        except Exception as e:
            logger.warning(f"Could not get users for admin section: {e}")
            users = []
        
        # Get all active organizations for signup/profile forms
        organizations = []
        try:
            organizations = await auth_service.get_active_organizations()
        except Exception as e:
            logger.warning(f"Could not get active organizations: {e}")
            organizations = []
        
        # Prepare template context
        template_context = {
            "request": request, 
            "title": "Authentication - AASX Digital Twin Analytics Framework",
            "current_user": user or {},
            "users": users or [],
            "organizations": organizations or []
        }
        
        return request.app.state.templates.TemplateResponse(
            "auth/index.html",
            template_context
        )
        
    except Exception as e:
        logger.error(f"Error rendering auth dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/config")
async def get_auth_config():
    """Get authentication configuration"""
    try:
        config = await auth_service.get_auth_config()
        return config
    except Exception as e:
        logger.error(f"Error getting auth config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False)
):
    """User login endpoint"""
    try:
        result = await auth_service.authenticate_user(username, password, remember_me)
        return result
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    organization_id: Optional[str] = Form(None),
    department_id: Optional[str] = Form(None)
):
    """User registration endpoint"""
    try:
        result = await auth_service.register_user(
            username, email, password, full_name, 
            organization_id, department_id
        )
        return result
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout(request: Request):
    """User logout endpoint"""
    try:
        result = await auth_service.logout_user(request)
        return result
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# PROFILE MANAGEMENT ROUTES
# ============================================================================

@router.get("/profile")
async def get_profile(request: Request):
    """Get user profile"""
    try:
        profile = await profile_management_service.get_public_profile(request)
        return profile
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/profile")
async def update_profile(
    request: Request,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    website: Optional[str] = Form(None)
):
    """Update user profile"""
    try:
        result = await profile_management_service.update_public_profile(
            request, full_name, email, bio, location, website
        )
        return result
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/profile/avatar")
async def upload_avatar(
    request: Request,
    avatar: UploadFile = File(...)
):
    """Upload user avatar"""
    try:
        result = await profile_management_service.upload_avatar(request, avatar)
        return result
    except Exception as e:
        logger.error(f"Error uploading avatar: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/profile/avatar")
async def remove_avatar(request: Request):
    """Remove user avatar"""
    try:
        result = await profile_management_service.remove_avatar(request)
        return result
    except Exception as e:
        logger.error(f"Error removing avatar: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# ADMIN ROUTES
# ============================================================================

@router.get("/admin/users")
async def admin_get_users(request: Request):
    """Admin endpoint to get all users"""
    try:
        users = await auth_service.get_all_users()
        return {"users": users}
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# PASSWORD MANAGEMENT ROUTES
# ============================================================================

@router.post("/forgot-password")
async def forgot_password(email: str = Form(...)):
    """Request password reset"""
    try:
        result = await security_service.request_password_reset(email)
        return result
    except Exception as e:
        logger.error(f"Error requesting password reset: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...)
):
    """Reset password with token"""
    try:
        result = await security_service.reset_password(token, new_password)
        return result
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...)
):
    """Change password for authenticated user"""
    try:
        result = await security_service.change_password(request, current_password, new_password)
        return result
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# AUTHENTICATION STATUS ROUTES
# ============================================================================

@router.get("/check-auth")
async def check_auth(request: Request):
    """Check if user is authenticated"""
    try:
        result = await auth_service.check_authentication_status(request)
        return result
    except Exception as e:
        logger.error(f"Error checking auth: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# RATE LIMITING ROUTES (now handled by backend)
# ============================================================================

@router.get("/rate-limit/status")
async def get_rate_limit_status(request: Request):
    """Get rate limit status for current user/IP"""
    try:
        # This is now handled by the backend engine
        return {"message": "Rate limiting is handled by the backend engine"}
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/rate-limit/clear")
async def clear_rate_limits(request: Request):
    """Clear rate limits for current user/IP"""
    try:
        # This is now handled by the backend engine
        return {"message": "Rate limiting is handled by the backend engine"}
    except Exception as e:
        logger.error(f"Error clearing rate limits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/rate-limit/blacklist/ip")
async def blacklist_ip(
    request: Request,
    ip_address: str = Form(...),
    reason: Optional[str] = Form(None)
):
    """Blacklist an IP address"""
    try:
        # This is now handled by the backend engine
        return {"message": "IP blacklisting is handled by the backend engine"}
    except Exception as e:
        logger.error(f"Error blacklisting IP: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/rate-limit/blacklist/ip/{ip_address}")
async def remove_blacklisted_ip(
    request: Request,
    ip_address: str
):
    """Remove IP from blacklist"""
    try:
        # This is now handled by the backend engine
        return {"message": "IP blacklist removal is handled by the backend engine"}
    except Exception as e:
        logger.error(f"Error removing blacklisted IP: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/rate-limit/whitelist/ip")
async def whitelist_ip(
    request: Request,
    ip_address: str = Form(...),
    reason: Optional[str] = Form(None)
):
    """Whitelist an IP address"""
    try:
        # This is now handled by the backend engine
        return {"message": "IP whitelisting is handled by the backend engine"}
    except Exception as e:
        logger.error(f"Error whitelisting IP: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/rate-limit/whitelist/ip/{ip_address}")
async def remove_whitelisted_ip(
    request: Request,
    ip_address: str
):
    """Remove IP from whitelist"""
    try:
        # This is now handled by the backend engine
        return {"message": "IP whitelist removal is handled by the backend engine"}
    except Exception as e:
        logger.error(f"Error removing whitelisted IP: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# AUDIT AND COMPLIANCE ROUTES
# ============================================================================

@router.get("/audit/logs")
async def get_audit_logs(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100
):
    """Get audit logs"""
    try:
        logs = await compliance_service.get_audit_logs(
            request, start_date, end_date, user_id, action, limit
        )
        return logs
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/audit/security-events")
async def get_security_events(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
):
    """Get security events"""
    try:
        events = await compliance_service.get_security_events(
            request, start_date, end_date, event_type, severity, limit
        )
        return events
    except Exception as e:
        logger.error(f"Error getting security events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/audit/compliance-report")
async def get_compliance_report(
    request: Request,
    report_type: str = "general",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get compliance report"""
    try:
        report = await compliance_service.get_compliance_report(
            request, report_type, start_date, end_date
        )
        return report
    except Exception as e:
        logger.error(f"Error getting compliance report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/audit/cleanup")
async def cleanup_audit_logs(
    request: Request,
    older_than_days: int = 90
):
    """Clean up old audit logs"""
    try:
        result = await compliance_service.cleanup_audit_logs(request, older_than_days)
        return result
    except Exception as e:
        logger.error(f"Error cleaning up audit logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/audit/log-data-access")
async def log_data_access(
    request: Request,
    data_type: str = Form(...),
    action: str = Form(...),
    details: Optional[str] = Form(None)
):
    """Log data access for compliance"""
    try:
        result = await compliance_service.log_data_access(
            request, data_type, action, details
        )
        return result
    except Exception as e:
        logger.error(f"Error logging data access: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# MFA ROUTES
# ============================================================================

@router.post("/mfa/setup")
async def setup_mfa(request: Request):
    """Setup MFA for user"""
    try:
        result = await security_service.setup_mfa(request)
        return result
    except Exception as e:
        logger.error(f"Error setting up MFA: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/mfa/verify")
async def verify_mfa(
    request: Request,
    code: str = Form(...)
):
    """Verify MFA code"""
    try:
        result = await security_service.verify_mfa(request, code)
        return result
    except Exception as e:
        logger.error(f"Error verifying MFA: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/mfa/recovery")
async def mfa_recovery(
    request: Request,
    backup_code: str = Form(...)
):
    """Use MFA backup code"""
    try:
        result = await security_service.mfa_recovery(request, backup_code)
        return result
    except Exception as e:
        logger.error(f"Error using MFA recovery: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/mfa/status")
async def get_mfa_status(request: Request):
    """Get MFA status for user"""
    try:
        result = await security_service.get_mfa_status(request)
        return result
    except Exception as e:
        logger.error(f"Error getting MFA status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/mfa/disable")
async def disable_mfa(request: Request):
    """Disable MFA for user"""
    try:
        result = await security_service.disable_mfa(request)
        return result
    except Exception as e:
        logger.error(f"Error disabling MFA: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# SESSION MANAGEMENT ROUTES
# ============================================================================

@router.get("/sessions")
async def get_user_sessions(request: Request):
    """Get all active sessions for user"""
    try:
        sessions = await session_management_service.get_user_sessions(request)
        return sessions
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/sessions/{session_id}")
async def revoke_session(
    request: Request,
    session_id: str
):
    """Revoke specific session"""
    try:
        result = await session_management_service.revoke_session(request, session_id)
        return result
    except Exception as e:
        logger.error(f"Error revoking session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/sessions")
async def revoke_all_sessions(request: Request):
    """Revoke all sessions for user"""
    try:
        result = await session_management_service.revoke_all_user_sessions(request)
        return result
    except Exception as e:
        logger.error(f"Error revoking all sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# SOCIAL LOGIN ROUTES
# ============================================================================

@router.get("/social/{provider}/auth")
async def social_auth(
    request: Request,
    provider: str
):
    """Initiate social login"""
    try:
        result = await security_service.initiate_social_login(request, provider)
        return result
    except Exception as e:
        logger.error(f"Error initiating social login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/social/{provider}/callback")
async def social_callback(
    request: Request,
    provider: str,
    code: str,
    state: Optional[str] = None
):
    """Handle social login callback"""
    try:
        result = await security_service.handle_social_callback(request, provider, code, state)
        return result
    except Exception as e:
        logger.error(f"Error handling social callback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/social/accounts")
async def get_social_accounts(request: Request):
    """Get linked social accounts"""
    try:
        accounts = await security_service.get_linked_social_accounts(request)
        return accounts
    except Exception as e:
        logger.error(f"Error getting social accounts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/social/{provider}/unlink")
async def unlink_social_account(
    request: Request,
    provider: str
):
    """Unlink social account"""
    try:
        result = await security_service.unlink_social_account(request, provider)
        return result
    except Exception as e:
        logger.error(f"Error unlinking social account: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# USER PREFERENCES ROUTES
# ============================================================================

@router.get("/preferences")
async def get_user_preferences(request: Request):
    """Get user preferences"""
    try:
        preferences = await user_preferences_service.get_user_preferences(request)
        return preferences
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/preferences")
async def update_user_preferences(
    request: Request,
    preferences: dict
):
    """Update user preferences"""
    try:
        result = await user_preferences_service.update_user_preferences(request, preferences)
        return result
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/preferences/{key}")
async def set_user_preference(
    request: Request,
    key: str,
    value: str = Form(...)
):
    """Set specific user preference"""
    try:
        result = await user_preferences_service.set_user_preference(request, key, value)
        return result
    except Exception as e:
        logger.error(f"Error setting user preference: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/preferences/{key}")
async def get_user_preference(
    request: Request,
    key: str
):
    """Get specific user preference"""
    try:
        preference = await user_preferences_service.get_user_preference(request, key)
        return preference
    except Exception as e:
        logger.error(f"Error getting user preference: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/preferences")
async def reset_user_preferences(request: Request):
    """Reset user preferences to defaults"""
    try:
        result = await user_preferences_service.reset_user_preferences(request)
        return result
    except Exception as e:
        logger.error(f"Error resetting user preferences: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# PUBLIC PROFILE ROUTES
# ============================================================================

@router.get("/public-profile")
async def get_own_public_profile(request: Request):
    """Get current user's public profile"""
    try:
        profile = await profile_management_service.get_public_profile(request)
        return profile
    except Exception as e:
        logger.error(f"Error getting public profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/public-profile/{username}")
async def get_public_profile_by_username(
    request: Request,
    username: str
):
    """Get public profile by username"""
    try:
        profile = await profile_management_service.get_public_profile_by_username(username)
        return profile
    except Exception as e:
        logger.error(f"Error getting public profile by username: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/public-profile")
async def create_public_profile(
    request: Request,
    bio: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    social_links: Optional[str] = Form(None)
):
    """Create public profile"""
    try:
        result = await profile_management_service.create_public_profile(
            request, bio, location, website, social_links
        )
        return result
    except Exception as e:
        logger.error(f"Error creating public profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/public-profile")
async def update_public_profile(
    request: Request,
    bio: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    social_links: Optional[str] = Form(None)
):
    """Update public profile"""
    try:
        result = await profile_management_service.update_public_profile(
            request, bio, location, website, social_links
        )
        return result
    except Exception as e:
        logger.error(f"Error updating public profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/public-profile")
async def delete_public_profile(request: Request):
    """Delete public profile"""
    try:
        result = await profile_management_service.delete_public_profile(request)
        return result
    except Exception as e:
        logger.error(f"Error deleting public profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/public-profiles")
async def get_public_profiles(
    request: Request,
    limit: int = 20,
    offset: int = 0
):
    """Get list of public profiles"""
    try:
        profiles = await profile_management_service.get_public_profiles(request, limit, offset)
        return profiles
    except Exception as e:
        logger.error(f"Error getting public profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/public-profiles/search")
async def search_public_profiles(
    request: Request,
    query: str,
    limit: int = 20,
    offset: int = 0
):
    """Search public profiles"""
    try:
        profiles = await profile_management_service.search_public_profiles(
            request, query, limit, offset
        )
        return profiles
    except Exception as e:
        logger.error(f"Error searching public profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# PROFILE VERIFICATION ROUTES
# ============================================================================

@router.get("/profile/verification/status")
async def get_verification_status(request: Request):
    """Get verification status for user"""
    try:
        status = await profile_verification_service.get_verification_status(request)
        return status
    except Exception as e:
        logger.error(f"Error getting verification status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/profile/verification/request")
async def request_verification(
    request: Request,
    verification_type: str = Form(...),
    contact_info: str = Form(...)
):
    """Request profile verification"""
    try:
        result = await profile_verification_service.create_verification_request(
            request, verification_type, contact_info
        )
        return result
    except Exception as e:
        logger.error(f"Error requesting verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/profile/verification/confirm")
async def confirm_verification(
    request: Request,
    verification_id: str = Form(...),
    code: str = Form(...)
):
    """Confirm verification with code"""
    try:
        result = await profile_verification_service.verify_verification_code(
            request, verification_id, code
        )
        return result
    except Exception as e:
        logger.error(f"Error confirming verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/profile/verification/{verification_type}")
async def get_verification_details(
    request: Request,
    verification_type: str
):
    """Get verification details for specific type"""
    try:
        details = await profile_verification_service.get_verification_details(
            request, verification_type
        )
        return details
    except Exception as e:
        logger.error(f"Error getting verification details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/profile/verification/{verification_type}")
async def cancel_verification(
    request: Request,
    verification_type: str
):
    """Cancel verification request"""
    try:
        result = await profile_verification_service.cancel_verification(
            request, verification_type
        )
        return result
    except Exception as e:
        logger.error(f"Error canceling verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# CUSTOM ROLE ROUTES
# ============================================================================

@router.get("/custom-roles")
async def get_custom_roles(
    request: Request,
    organization_id: Optional[str] = None
):
    """Get custom roles for organization"""
    try:
        roles = await custom_role_service.get_custom_roles_by_organization(
            request, organization_id
        )
        return roles
    except Exception as e:
        logger.error(f"Error getting custom roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/custom-roles")
async def create_custom_role(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    permissions: str = Form(...),
    organization_id: Optional[str] = Form(None)
):
    """Create custom role"""
    try:
        result = await custom_role_service.create_custom_role(
            request, name, description, permissions, organization_id
        )
        return result
    except Exception as e:
        logger.error(f"Error creating custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/custom-roles/{role_id}")
async def get_custom_role(
    request: Request,
    role_id: str
):
    """Get specific custom role"""
    try:
        role = await custom_role_service.get_custom_role(request, role_id)
        return role
    except Exception as e:
        logger.error(f"Error getting custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/custom-roles/{role_id}")
async def update_custom_role(
    request: Request,
    role_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    permissions: Optional[str] = Form(None)
):
    """Update custom role"""
    try:
        result = await custom_role_service.update_custom_role(
            request, role_id, name, description, permissions
        )
        return result
    except Exception as e:
        logger.error(f"Error updating custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/custom-roles/{role_id}")
async def delete_custom_role(
    request: Request,
    role_id: str
):
    """Delete custom role"""
    try:
        result = await custom_role_service.delete_custom_role(request, role_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/users/{user_id}/roles")
async def assign_role_to_user(
    request: Request,
    user_id: str,
    role_id: str = Form(...)
):
    """Assign role to user"""
    try:
        result = await custom_role_service.assign_role_to_user(
            request, user_id, role_id
        )
        return result
    except Exception as e:
        logger.error(f"Error assigning role to user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    request: Request,
    user_id: str,
    role_id: str
):
    """Remove role from user"""
    try:
        result = await custom_role_service.remove_role_from_user(
            request, user_id, role_id
        )
        return result
    except Exception as e:
        logger.error(f"Error removing role from user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}/roles")
async def get_user_roles(
    request: Request,
    user_id: str
):
    """Get roles for specific user"""
    try:
        roles = await custom_role_service.get_user_roles(request, user_id)
        return roles
    except Exception as e:
        logger.error(f"Error getting user roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# ORGANIZATION MANAGEMENT ROUTES
# ============================================================================

@router.get("/organization/settings")
async def get_organization_settings(request: Request):
    """Get organization settings"""
    try:
        settings = await organization_management_service.get_organization_settings(request)
        return settings
    except Exception as e:
        logger.error(f"Error getting organization settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/organization/settings")
async def update_organization_settings(
    request: Request,
    settings: dict
):
    """Update organization settings"""
    try:
        result = await organization_management_service.update_organization_settings(
            request, settings
        )
        return result
    except Exception as e:
        logger.error(f"Error updating organization settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/organization/analytics")
async def get_organization_analytics(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metrics: Optional[str] = None
):
    """Get organization analytics"""
    try:
        analytics = await organization_management_service.get_organization_analytics(
            request, start_date, end_date, metrics
        )
        return analytics
    except Exception as e:
        logger.error(f"Error getting organization analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/organization/billing")
async def get_organization_billing(request: Request):
    """Get organization billing information"""
    try:
        billing = await organization_management_service.get_organization_billing(request)
        return billing
    except Exception as e:
        logger.error(f"Error getting organization billing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/organization/billing")
async def update_organization_billing(
    request: Request,
    billing_info: dict
):
    """Update organization billing information"""
    try:
        result = await organization_management_service.update_organization_billing(
            request, billing_info
        )
        return result
    except Exception as e:
        logger.error(f"Error updating organization billing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# PERMISSIONS ROUTES
# ============================================================================

@router.get("/permissions")
async def get_permissions(request: Request):
    """Get available permissions"""
    try:
        permissions = await auth_service.get_available_permissions(request)
        return permissions
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
