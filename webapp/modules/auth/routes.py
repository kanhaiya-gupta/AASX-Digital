"""
Authentication routes for AASX Digital Twin Analytics Framework
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer
#from sqlalchemy.exc import SQLAlchemyError

from .database import AuthDatabase
from .models import (
    UserCreate, UserResponse, TokenData, UserLogin, 
    PasswordReset, PasswordResetConfirm, UserActivity
)
from .utils import (
    get_current_user_data_from_token, authenticate_user, 
    get_user_from_request, require_manager_or_admin, 
    log_user_activity, validate_password_strength, 
    sanitize_user_input, validate_email_format, 
    get_user_permissions, has_permission
)

logger = logging.getLogger(__name__)

# Initialize auth database
auth_db = AuthDatabase()

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
        except:
            pass  # User not authenticated, which is fine for the dashboard
        
        # Get all users for admin section (if user is admin)
        users = []
        if user and has_permission(user, "admin"):
            users = auth_db.get_all_users()
        
        # Get all active organizations for signup/profile forms
        organizations = auth_db.get_active_organizations()
        
        return request.app.state.templates.TemplateResponse(
            "auth/index.html",
            {
                "request": request, 
                "title": "Authentication - AASX Digital Twin Analytics Framework",
                "current_user": user,
                "users": users,
                "organizations": organizations
            }
        )
    except Exception as e:
        logger.error(f"Error rendering auth dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# API ROUTES (JSON responses)
# ============================================================================

@router.post("/login")
async def login(login_data: UserLogin, request: Request):
    """Login API endpoint"""
    try:
        # Sanitize inputs
        username = sanitize_user_input(login_data.username)
        password = login_data.password
        
        # Authenticate user
        user = auth_db.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create access token
        token_data = TokenData(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            organization_id=user.org_id
        )
        access_token = auth_db.create_access_token(token_data)
        
        # Update last login
        auth_db.update_last_login(user.user_id)
        
        # Log activity
        await log_user_activity(request, user.user_id, "login", "User logged in successfully")
        
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
        user = await get_user_from_request(request)
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
async def update_profile(request: Request, user_data: dict):
    """Update user profile API endpoint"""
    try:
        user = await get_user_from_request(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Update user
        updated_user = auth_db.update_user(user.user_id, user_data)
        
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

@router.get("/admin/users")
async def get_all_users(request: Request):
    """Get all users (admin only)"""
    try:
        user = await get_user_from_request(request)
        if not user or not has_permission(user, "admin"):
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
    """Forgot password API endpoint"""
    try:
        # Validate email
        if not validate_email_format(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check if user exists
        user = auth_db.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists or not
            return {
                "success": True,
                "message": "If the email exists, a reset link has been sent"
            }
        
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