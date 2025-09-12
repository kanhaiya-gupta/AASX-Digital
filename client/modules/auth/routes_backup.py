"""
Authentication routes for AASX Digital Twin Analytics Framework
"""
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Any
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, Depends, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer
from PIL import Image
import io
#from sqlalchemy.exc import SQLAlchemyError

from .database import AuthDatabase
from .models import (
    UserCreate, UserLogin, UserUpdate, UserResponse, Token, TokenData, 
    PasswordReset, PasswordResetConfirm, PasswordChange, UserPreferences, UserUpdate,
    MFASetup, MFAVerify, MFARecovery, SessionInfo, PasswordChange, UserPreferences, UserUpdate,
    PublicProfile, PublicProfileUpdate, ProfileVerification, ProfileVerificationRequest, 
    ProfileVerificationConfirm, ProfileVerificationStatus, CustomRoleCreate, CustomRoleUpdate,
    OrganizationSettingsUpdate
)
from .utils import (
    get_current_user_data_from_token, authenticate_user, 
    get_user_from_request, require_manager_or_admin, 
    log_user_activity, validate_password_strength, 
    sanitize_user_input, validate_email_format, 
    get_user_permissions, has_permission
)
from .services.mfa_service import MFAService
from .services.session_service import SessionService
from .services.social_login_service import SocialLoginService
from .services.rate_limiting_service import RateLimitingService
from .services.audit_service import AuditService
from .shared_instance import shared_auth_db

logger = logging.getLogger(__name__)

# Use shared auth database instance
auth_db = shared_auth_db
mfa_service = MFAService(auth_db)
session_service = SessionService(auth_db)
social_login_service = SocialLoginService(auth_db)
rate_limiting_service = RateLimitingService(auth_db)
audit_service = AuditService(auth_db)

# Security scheme
security = HTTPBearer()

# Create single router for all auth routes
router = APIRouter(tags=["Authentication"])

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
            user = await get_user_from_request(request)
            logger.info(f"User from request: {user}")
        except Exception as e:
            logger.warning(f"Could not get user from request: {e}")
            user = None  # User not authenticated, which is fine for the dashboard
        
        # Get all users for admin section (if user is admin)
        users = []
        try:
            if user and has_permission(user["role"], "admin"):
                users = auth_db.get_all_users()
                logger.info(f"Retrieved {len(users)} users for admin")
        except Exception as e:
            logger.warning(f"Could not get users for admin section: {e}")
            users = []
        
        # Get all active organizations for signup/profile forms
        organizations = []
        try:
            organizations = auth_db.get_active_organizations()
            logger.info(f"Retrieved {len(organizations)} active organizations")
        except Exception as e:
            logger.warning(f"Could not get active organizations: {e}")
            organizations = []
        
        # Prepare template context with safe defaults
        template_context = {
            "request": request, 
            "title": "Authentication - AASX Digital Twin Analytics Framework",
            "current_user": user or {},
            "users": users or [],
            "organizations": organizations or []
        }
        
        logger.info(f"Template context prepared: {template_context.keys()}")
        
        # Try to render template
        try:
            return request.app.state.templates.TemplateResponse(
                "auth/index.html",
                template_context
            )
        except Exception as template_error:
            logger.error(f"Template rendering failed: {template_error}")
            # Try fallback template
            try:
                return request.app.state.templates.TemplateResponse(
                    "auth/index.html",
                    {
                        "request": request, 
                        "title": "Authentication - AASX Digital Twin Analytics Framework",
                        "current_user": {},
                        "users": [],
                        "organizations": [],
                        "error": "Some features are temporarily unavailable"
                    }
                )
            except:
                # If even the error template fails, return a simple HTML response
                return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head><title>Authentication</title></head>
                <body>
                    <h1>Authentication System</h1>
                    <p>Welcome to the AASX Digital Twin Analytics Framework</p>
                    <p><a href="/api/auth/login">Login</a> | <a href="/api/auth/signup">Sign Up</a></p>
                    <p><a href="/">Back to Home</a></p>
                </body>
                </html>
                """)
                
    except Exception as e:
        logger.error(f"Error rendering auth dashboard: {e}")
        # Return a simple error page instead of raising an exception
        try:
            return request.app.state.templates.TemplateResponse(
                "auth/index.html",
                {
                    "request": request, 
                    "title": "Authentication - AASX Digital Twin Analytics Framework",
                    "current_user": {},
                    "users": [],
                    "organizations": [],
                    "error": "Some features are temporarily unavailable"
                }
            )
        except:
            # If even the error template fails, return a simple HTML response
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head><title>Authentication</title></head>
            <body>
                <h1>Authentication System</h1>
                <p>Welcome to the AASX Digital Twin Analytics Framework</p>
                <p><a href="/api/auth/login">Login</a> | <a href="/api/auth/signup">Sign Up</a></p>
                <p><a href="/">Back to Home</a></p>
            </body>
            </html>
            """)

# ============================================================================
# API ROUTES (JSON responses)
# ============================================================================

@router.get("/config")
async def get_auth_config(request: Request):
    """Get authentication configuration for the frontend"""
    try:
        # Return basic auth configuration
        config = {
            "sessionTimeoutMinutes": 30,
            "autoRefreshIntervalMinutes": 5,
            "maxLoginAttempts": 5,
            "lockoutDurationMinutes": 15,
            "passwordMinLength": 8,
            "requireMFA": False,
            "socialLoginEnabled": False,
            "features": {
                "mfa": True,
                "social_login": False,
                "password_reset": True,
                "profile_verification": True,
                "audit_logs": True,
                "rate_limiting": True
            }
        }
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error(f"Error getting auth config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(login_data: UserLogin, request: Request):
    """Login API endpoint with rate limiting"""
    try:
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Sanitize inputs
        username = sanitize_user_input(login_data.username)
        password = login_data.password
        
        # 🔍 DEBUG: Log login attempt details (remove in production!)
        logger.info(f"🔍 DEBUG - Login attempt for username: {username}")
        logger.info(f"🔍 DEBUG - Password length: {len(password) if password else 0}")
        logger.info(f"🔍 DEBUG - Password preview: {password[:3] + '...' if password and len(password) > 3 else password}")
        logger.info(f"🔍 DEBUG - Client IP: {client_ip}")
        
        # Check rate limiting before authentication
        allowed, error_message = rate_limiting_service.check_login_rate_limit(username, client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message
            )
        
        # Check if account is locked
        if rate_limiting_service.is_account_locked(username):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to too many failed login attempts"
            )
        
        # Authenticate user
        user = auth_db.authenticate_user(username, password)
        if not user:
            # Record failed login attempt
            rate_limiting_service.record_login_attempt(username, client_ip, success=False)
            
            # Log security event
            auth_db.log_security_event(
                user_id="unknown",
                event_type="failed_login",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                details={"username": username}
            )
            
            # Log audit event
            audit_service.log_authentication_event(
                user_id="unknown",
                event_type="login_failed",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                details={"username": username}
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Record successful login attempt
        rate_limiting_service.record_login_attempt(username, client_ip, success=True)
        
        # Reset failed login attempts on successful login
        auth_db.reset_failed_login_attempts(username)
        
        # Create access token
        token_data = TokenData(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            organization_id=user.org_id
        )
        # Convert TokenData to dict for JWT creation
        token_dict = {
            "user_id": token_data.user_id,
            "username": token_data.username,
            "role": token_data.role,
            "organization_id": token_data.organization_id
        }
        access_token = auth_db.create_access_token(token_dict)
        
        # Update last login
        auth_db.update_last_login(user.user_id)
        
        # Log activity
        log_user_activity(request, user.user_id, "login", "User logged in successfully")
        
        # Log security event
        auth_db.log_security_event(
            user_id=user.user_id,
            event_type="successful_login",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent")
        )
        
        # Log audit event
        audit_service.log_authentication_event(
            user_id=user.user_id,
            event_type="login_success",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_shared_user(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/signup")
async def signup(user_data: UserCreate, request: Request):
    """Signup API endpoint"""
    try:
        # Validate password strength
        password_strength = validate_password_strength(user_data.password)
        if not password_strength["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password too weak: {password_strength['message']}"
            )
        
        # Validate email format
        if not validate_email_format(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check if username/email already exists
        if auth_db.check_username_exists(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        if auth_db.check_email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create user
        user = auth_db.create_user(user_data)
        
        # Log activity
        await log_user_activity(request, user.user_id, "signup", "New user registered")
        
        return {
            "success": True,
            "message": "User created successfully",
            "user": UserResponse.from_shared_user(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout(request: Request):
    """Logout API endpoint"""
    try:
        user = await get_user_from_request(request)
        if user:
            await log_user_activity(request, user.user_id, "logout", "User logged out")
        
        return {
            "success": True,
            "message": "Logout successful"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/profile")
async def get_profile(request: Request):
    """Get user profile API endpoint"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        return {
            "success": True,
            "user": UserResponse.from_shared_user(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/profile")
async def update_profile(request: Request, user_data: UserUpdate):
    """Update user profile API endpoint"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Convert Pydantic model to dict, excluding None values
        update_data = user_data.dict(exclude_unset=True, exclude_none=True)
        
        # Remove sensitive fields that should be handled separately
        update_data.pop('current_password', None)
        update_data.pop('new_password', None)
        
        # Update user
        updated_user = auth_db.update_user(user.user_id, update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        # Log activity
        await log_user_activity(request, user.user_id, "profile_update", "Profile updated")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": UserResponse.from_shared_user(updated_user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/profile/avatar")
async def upload_avatar(request: Request, avatar: UploadFile = File(...)):
    """Upload user avatar API endpoint"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Validate file
        if not avatar or not avatar.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if avatar.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed"
            )
        
        # Validate file size (max 5MB)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_size = 0
        file_content = b""
        
        # Read file content
        while chunk := await avatar.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large. Maximum size is 5MB"
                )
            file_content += chunk
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
        
        # Create avatars directory if it doesn't exist
        avatars_dir = Path("client/static/avatars")
        avatars_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(avatar.filename).suffix.lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_extension = '.jpg'
        
        avatar_filename = f"{user['user_id']}_{uuid.uuid4().hex}{file_extension}"
        avatar_path = avatars_dir / avatar_filename
        
        # Process and save image
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize image if too large (max 500x500)
            max_size = (500, 500)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save processed image
            image.save(avatar_path, quality=85, optimize=True)
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process image"
            )
        
        # Update user's avatar_url in database
        avatar_url = f"/static/avatars/{avatar_filename}"
        updated_user = auth_db.update_user(user["user_id"], {"avatar_url": avatar_url})
        
        if not updated_user:
            # Clean up uploaded file if database update fails
            if avatar_path.exists():
                avatar_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
        
        # Log activity
        await log_user_activity(request, user["user_id"], "avatar_upload", "Avatar uploaded")
        
        return {
            "success": True,
            "message": "Avatar uploaded successfully",
            "avatar_url": avatar_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/profile/avatar")
async def remove_avatar(request: Request):
    """Remove user avatar API endpoint"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get current avatar URL
        current_user = auth_db.get_user_by_id(user["user_id"])
        if not current_user or not current_user.avatar_url:
            return {
                "success": True,
                "message": "No avatar to remove"
            }
        
        # Remove avatar file if it exists
        avatar_path = Path("client/static/avatars") / Path(current_user.avatar_url).name
        if avatar_path.exists():
            try:
                avatar_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete avatar file {avatar_path}: {e}")
        
        # Update user's avatar_url in database
        updated_user = auth_db.update_user(user["user_id"], {"avatar_url": None})
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
        
        # Log activity
        await log_user_activity(request, user["user_id"], "avatar_removed", "Avatar removed")
        
        return {
            "success": True,
            "message": "Avatar removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar removal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/admin/users")
async def get_all_users(request: Request):
    """Get all users (admin only)"""
    try:
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        users = auth_db.get_all_users()
        return {
            "success": True,
            "users": [UserResponse.from_shared_user(u) for u in users]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/forgot-password")
async def forgot_password(email: str = Form(...), request: Request = None):
    """Forgot password API endpoint with rate limiting"""
    try:
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Validate email
        if not validate_email_format(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check rate limiting for password reset
        allowed, error_message = rate_limiting_service.check_password_reset_rate_limit(email, client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message
            )
        
        # Check if user exists
        user = auth_db.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists or not, but still record the attempt
            rate_limiting_service.record_password_reset_attempt(email, client_ip)
            return {
                "success": True,
                "message": "If the email exists, a reset link has been sent"
            }
        
        # Record password reset attempt
        rate_limiting_service.record_password_reset_attempt(email, client_ip)
        
        # Log security event
        auth_db.log_security_event(
            user_id=user.user_id,
            event_type="password_reset_requested",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        # Generate reset token and send email (simplified)
        # In production, implement proper email sending
        
        return {
            "success": True,
            "message": "Password reset link sent to email"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/reset-password")
async def reset_password(reset_data: PasswordResetConfirm, request: Request = None):
    """Reset password API endpoint"""
    try:
        # Validate password strength
        password_strength = validate_password_strength(reset_data.new_password)
        if not password_strength["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password too weak: {password_strength['message']}"
            )
        
        # Validate token and update password (simplified)
        # In production, implement proper token validation
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/change-password")
async def change_password(password_data: PasswordChange, request: Request):
    """Change password API endpoint with history and expiration checks"""
    try:
        # Get current user
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Verify current password
        user_obj = auth_db.get_user_by_id(user["user_id"])
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check current password
        if not auth_db.verify_password(password_data.current_password, user_obj.password_hash):
            # Log failed password change attempt
            auth_db.log_security_event(
                user_id=user["user_id"],
                event_type="password_change_failed",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
                details={"reason": "incorrect_current_password"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        password_strength = validate_password_strength(password_data.new_password)
        if not password_strength["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password too weak: {password_strength['message']}"
            )
        
        # Check password history (prevent reuse of recent passwords)
        new_password_hash = auth_db.get_password_hash(password_data.new_password)
        if auth_db.check_password_in_history(user["user_id"], new_password_hash, limit=5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot be the same as any of your last 5 passwords"
            )
        
        # Update password with history
        if not auth_db.update_password_with_history(user["user_id"], password_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        # Log successful password change
        auth_db.log_security_event(
            user_id=user["user_id"],
            event_type="password_changed",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            details={"password_strength": password_strength["score"]}
        )
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )



@router.get("/check-auth")
async def check_auth(request: Request):
    """Check authentication status"""
    try:
        user = await get_user_from_request(request)
        if user:
            return {
                "success": True,
                "authenticated": True,
                "user": UserResponse.from_shared_user(user)
            }
        else:
            return {
                "success": True,
                "authenticated": False,
                "user": None
            }
        
    except Exception as e:
        logger.error(f"Check auth error: {e}")
        return {
            "success": False,
            "authenticated": False,
            "user": None,
            "error": "Authentication check failed"
        }

# ============================================================================
# RATE LIMITING ROUTES (Phase 4: Security Enhancement)
# ============================================================================

@router.get("/rate-limit/status")
async def get_rate_limit_status(request: Request):
    """Get current rate limit status for the current user/IP"""
    try:
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Get current user if authenticated
        user = None
        try:
            user = await get_user_from_request(request)
        except:
            pass
        
        # Get rate limit status
        status = rate_limiting_service.get_rate_limit_status(
            username=user["username"] if user else None,
            ip_address=client_ip
        )
        
        return {
            "success": True,
            "rate_limit_status": status,
            "ip_address": client_ip
        }
        
    except Exception as e:
        logger.error(f"Rate limit status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/rate-limit/clear")
async def clear_rate_limits(request: Request, username: str = None, ip_address: str = None):
    """Clear rate limits for user/IP (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Clear rate limits
        rate_limiting_service.clear_rate_limits(username=username, ip_address=ip_address)
        
        return {
            "success": True,
            "message": "Rate limits cleared successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear rate limits error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/rate-limit/blacklist/ip")
async def add_ip_to_blacklist(request: Request, ip_address: str, reason: str = None):
    """Add IP to blacklist (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Add IP to blacklist
        success = rate_limiting_service.add_ip_to_blacklist(ip_address, reason)
        
        if success:
            return {
                "success": True,
                "message": f"IP {ip_address} added to blacklist"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add IP to blacklist"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add IP to blacklist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/rate-limit/blacklist/ip/{ip_address}")
async def remove_ip_from_blacklist(request: Request, ip_address: str):
    """Remove IP from blacklist (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Remove IP from blacklist
        success = rate_limiting_service.remove_ip_from_blacklist(ip_address)
        
        if success:
            return {
                "success": True,
                "message": f"IP {ip_address} removed from blacklist"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove IP from blacklist"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove IP from blacklist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/rate-limit/whitelist/ip")
async def add_ip_to_whitelist(request: Request, ip_address: str):
    """Add IP to whitelist (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Add IP to whitelist
        success = rate_limiting_service.add_ip_to_whitelist(ip_address)
        
        if success:
            return {
                "success": True,
                "message": f"IP {ip_address} added to whitelist"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add IP to whitelist"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add IP to whitelist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/rate-limit/whitelist/ip/{ip_address}")
async def remove_ip_from_whitelist(request: Request, ip_address: str):
    """Remove IP from whitelist (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Remove IP from whitelist
        success = rate_limiting_service.remove_ip_from_whitelist(ip_address)
        
        if success:
            return {
                "success": True,
                "message": f"IP {ip_address} removed from whitelist"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove IP from whitelist"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove IP from whitelist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ============================================================================
# AUDIT LOGGING ROUTES (Phase 4: Security Enhancement)
# ============================================================================

@router.get("/audit/logs")
async def get_audit_logs(request: Request, user_id: str = None, event_type: str = None,
                        start_date: str = None, end_date: str = None, limit: int = 100):
    """Get audit logs with optional filtering (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format"
                )
        
        # Get audit logs
        logs = audit_service.get_audit_logs(
            user_id=user_id,
            event_type=event_type,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return {
            "success": True,
            "audit_logs": logs,
            "total_count": len(logs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get audit logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/audit/security-events")
async def get_security_events(request: Request, user_id: str = None,
                             start_date: str = None, end_date: str = None, limit: int = 100):
    """Get security-specific events (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format"
                )
        
        # Get security events
        events = audit_service.get_security_events(
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return {
            "success": True,
            "security_events": events,
            "total_count": len(events)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get security events error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/audit/compliance-report")
async def get_compliance_report(request: Request, start_date: str = None, end_date: str = None):
    """Get compliance report for GDPR and other regulations (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format"
                )
        
        # Get compliance report
        report = audit_service.get_compliance_report(
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "success": True,
            "compliance_report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get compliance report error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/audit/cleanup")
async def cleanup_audit_logs(request: Request, days_to_keep: int = None):
    """Clean up old audit logs (admin function)"""
    try:
        # Check if user is admin
        user = await get_user_from_request(request)
        if not user or not has_permission(user["role"], "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permission required"
            )
        
        # Clean up old logs
        success = audit_service.cleanup_old_logs(days_to_keep)
        
        if success:
            return {
                "success": True,
                "message": f"Cleaned up audit logs older than {days_to_keep or 'default'} days"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cleanup audit logs"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cleanup audit logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/audit/log-data-access")
async def log_data_access(request: Request, data_type: str, action: str, 
                         resource_id: str = None, details: dict = None):
    """Log data access event for compliance"""
    try:
        # Get current user
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Log data access event
        success = audit_service.log_data_access(
            user_id=user["user_id"],
            data_type=data_type,
            action=action,
            resource_id=resource_id,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            details=details
        )
        
        if success:
            return {
                "success": True,
                "message": "Data access logged successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log data access"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Log data access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ============================================================================
# MFA ROUTES (Phase 2: Authentication Enhancement)
# ============================================================================

@router.post("/mfa/setup")
async def setup_mfa(mfa_data: MFASetup, request: Request):
    """Setup MFA for a user"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        result = mfa_service.setup_mfa(user["user_id"], mfa_data.mfa_type, **mfa_data.dict())
        
        if result["success"]:
            return {
                "success": True,
                "message": "MFA setup successful",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA setup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/mfa/verify")
async def verify_mfa(mfa_data: MFAVerify, request: Request):
    """Verify MFA code with rate limiting"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check MFA rate limiting
        allowed, error_message = rate_limiting_service.check_mfa_rate_limit(user["user_id"], client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message
            )
        
        if mfa_service.verify_mfa(user["user_id"], mfa_data.mfa_type, mfa_data.code):
            # Record successful MFA attempt
            rate_limiting_service.record_mfa_attempt(user["user_id"], client_ip, success=True)
            
            # Log security event
            auth_db.log_security_event(
                user_id=user["user_id"],
                event_type="mfa_verification_success",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent")
            )
            
            return {
                "success": True,
                "message": "MFA verification successful"
            }
        else:
            # Record failed MFA attempt
            rate_limiting_service.record_mfa_attempt(user["user_id"], client_ip, success=False)
            
            # Log security event
            auth_db.log_security_event(
                user_id=user["user_id"],
                event_type="mfa_verification_failed",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent")
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/mfa/recovery")
async def mfa_recovery(recovery_data: MFARecovery, request: Request):
    """Recover account using backup code"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if mfa_service.verify_backup_code(user["user_id"], recovery_data.backup_code):
            return {
                "success": True,
                "message": "Account recovery successful"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid backup code"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA recovery error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/mfa/status")
async def get_mfa_status(request: Request):
    """Get MFA status for current user"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        status_data = mfa_service.get_mfa_status(user["user_id"])
        return {
            "success": True,
            "mfa_status": status_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get MFA status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/mfa/disable")
async def disable_mfa(request: Request):
    """Disable MFA for current user"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if mfa_service.disable_mfa(user["user_id"]):
            return {
                "success": True,
                "message": "MFA disabled successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to disable MFA"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disable MFA error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ============================================================================
# SESSION MANAGEMENT ROUTES
# ============================================================================

@router.get("/sessions")
async def get_user_sessions(request: Request):
    """Get all active sessions for current user"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        sessions = session_service.get_user_sessions(user["user_id"])
        return {
            "success": True,
            "sessions": sessions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/sessions/{session_id}")
async def revoke_session(session_id: str, request: Request):
    """Revoke a specific session"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if session_service.revoke_session(session_id):
            return {
                "success": True,
                "message": "Session revoked successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke session"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revoke session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/sessions")
async def revoke_all_sessions(request: Request):
    """Revoke all sessions for current user"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if session_service.revoke_all_user_sessions(user["user_id"]):
            return {
                "success": True,
                "message": "All sessions revoked successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke sessions"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revoke all sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 

# ============================================================================
# SOCIAL LOGIN ROUTES (Phase 2: Social Login Integration)
# ============================================================================

@router.get("/social/{provider}/auth")
async def social_auth(provider: str, request: Request):
    """Generate OAuth authorization URL for social login"""
    try:
        # Validate provider
        if provider not in ["google", "facebook", "apple"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported provider"
            )
        
        # Generate redirect URI
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/auth/social/{provider}/callback"
        
        # Generate auth URL
        auth_url = social_login_service.get_auth_url(provider, redirect_uri)
        
        return {
            "success": True,
            "auth_url": auth_url,
            "provider": provider
        }
        
    except Exception as e:
        logger.error(f"Social auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/social/{provider}/callback")
async def social_callback(provider: str, code: str, state: str = None, request: Request = None):
    """Handle OAuth callback from social login providers"""
    try:
        # Validate provider
        if provider not in ["google", "facebook", "apple"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported provider"
            )
        
        # Generate redirect URI
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/auth/social/{provider}/callback"
        
        # Handle callback
        result = await social_login_service.handle_callback(provider, code, redirect_uri)
        
        if result["success"]:
            # Create access token for the user
            user = result["user"]
            token_data = TokenData(
                user_id=user["user_id"],
                username=user["username"],
                role=user["role"],
                organization_id=user.get("organization_id")
            )
            access_token = auth_db.create_access_token(token_data)
            
            # Update last login
            auth_db.update_last_login(user["user_id"])
            
            # Log activity
            await log_user_activity(request, user["user_id"], "social_login", f"Logged in via {provider}")
            
            return {
                "success": True,
                "message": f"Login successful via {provider}",
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse.from_shared_user(user)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Social callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/social/accounts")
async def get_social_accounts(request: Request):
    """Get all social accounts for the current user"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        social_accounts = social_login_service.get_social_accounts(user["user_id"])
        
        return {
            "success": True,
            "social_accounts": social_accounts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get social accounts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/social/{provider}/unlink")
async def unlink_social_account(provider: str, request: Request):
    """Unlink social account from user profile"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        success = social_login_service.unlink_account(user["user_id"], provider)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "social_account_unlinked", f"Unlinked {provider} account")
            
            return {
                "success": True,
                "message": f"{provider.capitalize()} account unlinked successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to unlink {provider} account"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Social account unlink error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ============================================================================
# USER PREFERENCES ROUTES
# ============================================================================

@router.get("/preferences")
async def get_user_preferences(request: Request):
    """Get user preferences"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        preferences = auth_db.get_user_preferences(user["user_id"])
        
        if preferences is None:
            # Return default preferences if none exist
            default_preferences = UserPreferences().dict()
            return {
                "success": True,
                "preferences": default_preferences
            }
        
        return {
            "success": True,
            "preferences": preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user preferences error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/preferences")
async def update_user_preferences(request: Request, preferences: UserPreferences):
    """Update user preferences"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Convert Pydantic model to dict
        preferences_dict = preferences.dict(exclude_unset=True)
        
        success = auth_db.update_user_preferences(user["user_id"], preferences_dict)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "preferences_updated", "User preferences updated")
            
            return {
                "success": True,
                "message": "Preferences updated successfully",
                "preferences": preferences_dict
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user preferences error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/preferences/{key}")
async def update_user_preference(request: Request, key: str, value: Any):
    """Update a specific user preference"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        success = auth_db.set_user_preference(user["user_id"], key, value)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "preference_updated", f"Updated preference: {key}")
            
            return {
                "success": True,
                "message": f"Preference {key} updated successfully",
                "key": key,
                "value": value
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preference"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user preference error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/preferences/{key}")
async def get_user_preference(request: Request, key: str):
    """Get a specific user preference"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        value = auth_db.get_user_preferences_by_key(user["user_id"], key)
        
        return {
            "success": True,
            "key": key,
            "value": value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user preference error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/preferences")
async def reset_user_preferences(request: Request):
    """Reset user preferences to default"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        success = auth_db.reset_user_preferences(user["user_id"])
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "preferences_reset", "User preferences reset to default")
            
            return {
                "success": True,
                "message": "Preferences reset to default successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset user preferences error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Public Profiles Routes
@router.get("/public-profile")
async def get_public_profile(request: Request):
    """Get current user's public profile"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        public_profile = auth_db.get_public_profile(user["user_id"])
        
        if not public_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Public profile not found"
            )
        
        return {
            "success": True,
            "public_profile": public_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get public profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/public-profile/{username}")
async def get_public_profile_by_username(username: str, request: Request):
    """Get public profile by username"""
    try:
        # Get user by username
        user = auth_db.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        public_profile = auth_db.get_public_profile(user.user_id)
        
        if not public_profile or not public_profile.get("is_public", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Public profile not found or not public"
            )
        
        return {
            "success": True,
            "public_profile": public_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get public profile by username error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/public-profile")
async def create_public_profile(request: Request, profile_data: PublicProfileUpdate):
    """Create or update public profile"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Convert Pydantic model to dict
        profile_dict = profile_data.dict(exclude_unset=True)
        
        success = auth_db.create_public_profile(user["user_id"], profile_dict)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "public_profile_created", "Public profile created/updated")
            
            return {
                "success": True,
                "message": "Public profile created/updated successfully",
                "public_profile": auth_db.get_public_profile(user["user_id"])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create/update public profile"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create public profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/public-profile")
async def update_public_profile(request: Request, profile_data: PublicProfileUpdate):
    """Update public profile"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Convert Pydantic model to dict
        profile_dict = profile_data.dict(exclude_unset=True)
        
        success = auth_db.update_public_profile(user["user_id"], profile_dict)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "public_profile_updated", "Public profile updated")
            
            return {
                "success": True,
                "message": "Public profile updated successfully",
                "public_profile": auth_db.get_public_profile(user["user_id"])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update public profile"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update public profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/public-profile")
async def delete_public_profile(request: Request):
    """Delete public profile"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        success = auth_db.delete_public_profile(user["user_id"])
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "public_profile_deleted", "Public profile deleted")
            
            return {
                "success": True,
                "message": "Public profile deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete public profile"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete public profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/public-profiles")
async def get_public_profiles(request: Request, limit: int = 50, offset: int = 0):
    """Get all public profiles"""
    try:
        public_profiles = auth_db.get_public_profiles(limit=limit, offset=offset)
        
        return {
            "success": True,
            "public_profiles": public_profiles,
            "total": len(public_profiles),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Get public profiles error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/public-profiles/search")
async def search_public_profiles(request: Request, q: str, limit: int = 50):
    """Search public profiles"""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search term must be at least 2 characters"
            )
        
        public_profiles = auth_db.search_public_profiles(q.strip(), limit=limit)
        
        return {
            "success": True,
            "public_profiles": public_profiles,
            "total": len(public_profiles),
            "search_term": q,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search public profiles error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 

# Profile Verification Routes
@router.get("/profile/verification/status")
async def get_profile_verification_status(request: Request):
    """Get profile verification status for current user"""
    try:
        # Get current user
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get verification status
        verification_status = auth_db.get_profile_verification_status(user["user_id"])
        
        return {
            "success": True,
            "verification_status": verification_status
        }
        
    except Exception as e:
        logger.error(f"Error getting profile verification status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/profile/verification/request")
async def request_profile_verification(
    verification_request: ProfileVerificationRequest,
    request: Request
):
    """Request profile verification"""
    try:
        # Get current user
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Create verification record
        success = auth_db.create_profile_verification(
            user["user_id"], 
            verification_request.verification_type,
            verification_request.verification_data
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create verification request")
        
        # For email/phone verification, send verification code
        if verification_request.verification_type in ['email', 'phone']:
            # Get the verification record to get the code
            verification = auth_db.get_profile_verification(user["user_id"], verification_request.verification_type)
            if verification and verification['verification_code']:
                # TODO: Send verification code via email/SMS
                logger.info(f"Verification code {verification['verification_code']} generated for {verification_request.verification_type}")
        
        return {
            "success": True,
            "message": f"Verification request created for {verification_request.verification_type}",
            "verification_type": verification_request.verification_type
        }
        
    except Exception as e:
        logger.error(f"Error requesting profile verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/profile/verification/confirm")
async def confirm_profile_verification(
    verification_confirm: ProfileVerificationConfirm,
    request: Request
):
    """Confirm profile verification"""
    try:
        # Get current user
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Verify the verification
        success = auth_db.verify_profile_verification(
            user["user_id"],
            verification_confirm.verification_type,
            verification_confirm.verification_code
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid verification code or verification expired")
        
        # Get updated verification status
        verification_status = auth_db.get_profile_verification_status(user["user_id"])
        
        return {
            "success": True,
            "message": f"{verification_confirm.verification_type.title()} verification completed successfully",
            "verification_status": verification_status
        }
        
    except Exception as e:
        logger.error(f"Error confirming profile verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/profile/verification/{verification_type}")
async def get_profile_verification(verification_type: str, request: Request):
    """Get profile verification details for a specific type"""
    try:
        # Get current user
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get verification details
        verification = auth_db.get_profile_verification(user["user_id"], verification_type)
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        return {
            "success": True,
            "verification": verification
        }
        
    except Exception as e:
        logger.error(f"Error getting profile verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/profile/verification/{verification_type}")
async def delete_profile_verification(verification_type: str, request: Request):
    """Delete profile verification"""
    try:
        # Get current user
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get verification details
        verification = auth_db.get_profile_verification(user["user_id"], verification_type)
        
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        # Update status to failed
        success = auth_db.update_profile_verification_status(verification['verification_id'], 'failed')
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete verification")
        
        return {
            "success": True,
            "message": f"Verification for {verification_type} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting profile verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 

# Custom Roles Routes
@router.get("/custom-roles")
async def get_custom_roles(request: Request):
    """Get all custom roles for the current user's organization"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to view roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        custom_roles = auth_db.get_custom_roles_by_organization(user["organization_id"])
        
        return {
            "success": True,
            "custom_roles": custom_roles
        }
        
    except Exception as e:
        logger.error(f"Error getting custom roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/custom-roles")
async def create_custom_role(
    role_data: CustomRoleCreate,
    request: Request
):
    """Create a new custom role"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to create roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Convert Pydantic model to dict
        role_dict = role_data.dict()
        
        role_id = auth_db.create_custom_role(user["organization_id"], role_dict)
        
        if role_id:
            # Log activity
            await log_user_activity(request, user["user_id"], "custom_role_created", "custom_role", role_id)
            
            return {
                "success": True,
                "message": "Custom role created successfully",
                "role_id": role_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create custom role")
            
    except Exception as e:
        logger.error(f"Error creating custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/custom-roles/{role_id}")
async def get_custom_role(role_id: str, request: Request):
    """Get a specific custom role"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to view roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        custom_role = auth_db.get_custom_role(role_id)
        
        if not custom_role:
            raise HTTPException(status_code=404, detail="Custom role not found")
        
        # Check if role belongs to user's organization
        if custom_role["organization_id"] != user["organization_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "custom_role": custom_role
        }
        
    except Exception as e:
        logger.error(f"Error getting custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/custom-roles/{role_id}")
async def update_custom_role(
    role_id: str,
    role_data: CustomRoleUpdate,
    request: Request
):
    """Update a custom role"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to update roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get existing role to check organization
        existing_role = auth_db.get_custom_role(role_id)
        if not existing_role:
            raise HTTPException(status_code=404, detail="Custom role not found")
        
        if existing_role["organization_id"] != user["organization_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert Pydantic model to dict
        role_dict = role_data.dict(exclude_unset=True)
        
        success = auth_db.update_custom_role(role_id, role_dict)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "custom_role_updated", "custom_role", role_id)
            
            return {
                "success": True,
                "message": "Custom role updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update custom role")
            
    except Exception as e:
        logger.error(f"Error updating custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/custom-roles/{role_id}")
async def delete_custom_role(role_id: str, request: Request):
    """Delete a custom role"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to delete roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get existing role to check organization
        existing_role = auth_db.get_custom_role(role_id)
        if not existing_role:
            raise HTTPException(status_code=404, detail="Custom role not found")
        
        if existing_role["organization_id"] != user["organization_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = auth_db.delete_custom_role(role_id)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "custom_role_deleted", "custom_role", role_id)
            
            return {
                "success": True,
                "message": "Custom role deleted successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Cannot delete role - it is assigned to users")
            
    except Exception as e:
        logger.error(f"Error deleting custom role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Role Assignment Routes
@router.post("/users/{user_id}/roles")
async def assign_role_to_user(
    user_id: str,
    role_assignment: dict,
    request: Request
):
    """Assign a role to a user"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to assign roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        role_id = role_assignment.get("role_id")
        if not role_id:
            raise HTTPException(status_code=400, detail="role_id is required")
        
        success = auth_db.assign_role_to_user(
            user_id=user_id,
            role_id=role_id,
            organization_id=user["organization_id"],
            assigned_by=user["user_id"]
        )
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "role_assigned", "user", user_id)
            
            return {
                "success": True,
                "message": "Role assigned successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to assign role")
            
    except Exception as e:
        logger.error(f"Error assigning role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    request: Request
):
    """Remove a role from a user"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to remove roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = auth_db.remove_role_from_user(
            user_id=user_id,
            role_id=role_id,
            organization_id=user["organization_id"]
        )
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "role_removed", "user", user_id)
            
            return {
                "success": True,
                "message": "Role removed successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to remove role")
            
    except Exception as e:
        logger.error(f"Error removing role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}/roles")
async def get_user_roles(user_id: str, request: Request):
    """Get all roles assigned to a user"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to view roles
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        roles = auth_db.get_user_roles(user_id, user["organization_id"])
        
        return {
            "success": True,
            "roles": roles
        }
        
    except Exception as e:
        logger.error(f"Error getting user roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 

# Organization Settings Routes
@router.get("/organization/settings")
async def get_organization_settings(request: Request):
    """Get organization settings for the current user's organization"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to view organization settings
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        settings = auth_db.get_organization_settings(user["organization_id"])
        
        if not settings:
            # Create default settings
            default_settings = {
                "branding": {
                    "logo_url": None,
                    "primary_color": "#1e3c72",
                    "secondary_color": "#2a5298",
                    "accent_color": "#ffd700",
                    "company_name": None,
                    "tagline": None
                },
                "configuration": {
                    "default_language": "en",
                    "default_timezone": "UTC",
                    "session_timeout": 30,
                    "require_mfa": False,
                    "allow_public_profiles": True,
                    "max_file_size_mb": 100,
                    "allowed_file_types": ["pdf", "doc", "docx", "xls", "xlsx", "txt", "json", "xml"]
                },
                "notifications": {
                    "email_notifications": True,
                    "sms_notifications": False,
                    "push_notifications": True,
                    "notification_frequency": "immediate"
                },
                "security": {
                    "password_policy": {
                        "min_length": 8,
                        "require_uppercase": True,
                        "require_lowercase": True,
                        "require_numbers": True,
                        "require_special_chars": False
                    },
                    "session_management": {
                        "max_concurrent_sessions": 5,
                        "session_timeout_minutes": 30,
                        "remember_me_days": 30
                    }
                }
            }
            auth_db.create_organization_settings(user["organization_id"], default_settings)
            settings = auth_db.get_organization_settings(user["organization_id"])
        
        return {
            "success": True,
            "settings": settings
        }
        
    except Exception as e:
        logger.error(f"Error getting organization settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/organization/settings")
async def update_organization_settings(
    settings_data: OrganizationSettingsUpdate,
    request: Request
):
    """Update organization settings"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to update organization settings
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Convert Pydantic model to dict
        settings_dict = settings_data.dict(exclude_unset=True)
        
        success = auth_db.update_organization_settings(user["organization_id"], settings_dict)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "organization_settings_updated", "organization", user["organization_id"])
            
            return {
                "success": True,
                "message": "Organization settings updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update organization settings")
            
    except Exception as e:
        logger.error(f"Error updating organization settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Organization Analytics Routes
@router.get("/organization/analytics")
async def get_organization_analytics(request: Request):
    """Get organization analytics for the current user's organization"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to view analytics
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        analytics = auth_db.get_organization_analytics(user["organization_id"])
        
        if not analytics:
            # Create default analytics
            default_analytics = {
                "user_analytics": {
                    "total_users": 0,
                    "active_users": 0,
                    "new_users_this_month": 0,
                    "user_growth_rate": 0.0
                },
                "usage_analytics": {
                    "total_projects": 0,
                    "total_files": 0,
                    "storage_used_gb": 0.0,
                    "storage_limit_gb": 10,
                    "api_requests_this_month": 0
                },
                "performance_metrics": {
                    "average_response_time_ms": 0,
                    "uptime_percentage": 99.9,
                    "error_rate": 0.0
                },
                "activity_insights": {
                    "most_active_users": [],
                    "most_used_features": [],
                    "peak_usage_hours": []
                }
            }
            auth_db.update_organization_analytics(user["organization_id"], default_analytics)
            analytics = auth_db.get_organization_analytics(user["organization_id"])
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting organization analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Organization Billing Routes
@router.get("/organization/billing")
async def get_organization_billing(request: Request):
    """Get organization billing information for the current user's organization"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to view billing
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        billing = auth_db.get_organization_billing(user["organization_id"])
        
        if not billing:
            # Create default billing
            default_billing = {
                "subscription": {
                    "tier": "basic",
                    "status": "active",
                    "start_date": None,
                    "end_date": None,
                    "auto_renew": True
                },
                "billing_info": {
                    "billing_email": None,
                    "billing_address": None,
                    "payment_method": None,
                    "tax_id": None
                },
                "usage_billing": {
                    "current_period_start": None,
                    "current_period_end": None,
                    "usage_amount": 0.0,
                    "billing_amount": 0.0,
                    "currency": "USD"
                },
                "payment_history": []
            }
            auth_db.update_organization_billing(user["organization_id"], default_billing)
            billing = auth_db.get_organization_billing(user["organization_id"])
        
        return {
            "success": True,
            "billing": billing
        }
        
    except Exception as e:
        logger.error(f"Error getting organization billing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/organization/billing")
async def update_organization_billing(
    billing_data: dict,
    request: Request
):
    """Update organization billing information"""
    try:
        user = get_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Check if user has permission to update billing
        if not has_permission(user["role"], "admin"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = auth_db.update_organization_billing(user["organization_id"], billing_data)
        
        if success:
            # Log activity
            await log_user_activity(request, user["user_id"], "organization_billing_updated", "organization", user["organization_id"])
            
            return {
                "success": True,
                "message": "Organization billing updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update organization billing")
            
    except Exception as e:
        logger.error(f"Error updating organization billing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# PERMISSIONS ENDPOINTS
# ============================================================================

@router.get("/permissions")
async def get_user_permissions_endpoint(request: Request):
    """Get current user's permissions and roles"""
    try:
        logger.info("🔍 Permissions endpoint called")
        
        user = get_user_from_request(request)
        if not user:
            logger.error("❌ No user found in request")
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        logger.info(f"👤 User found: {user}")
        logger.info(f"🔑 User role: {getattr(user, 'role', 'NO_ROLE')}")
        
        # Get user permissions based on role
        user_role = getattr(user, "role", "guest")
        logger.info(f"🎯 Getting permissions for role: {user_role}")
        
        user_permissions = get_user_permissions(user_role)
        logger.info(f"✅ Permissions retrieved: {user_permissions}")
        
        # Get user roles (for now, just the current role)
        user_roles = [user_role] if user_role else []
        
        result = {
            "success": True,
            "permissions": user_permissions,
            "roles": user_roles,
            "user_role": user_role
        }
        
        logger.info(f"🎉 Permissions endpoint result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting user permissions: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        logger.error(f"❌ Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")