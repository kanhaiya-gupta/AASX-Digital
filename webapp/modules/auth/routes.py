"""
Authentication routes
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from .models import UserCreate, UserLogin, UserResponse, UserUpdate, Token
from .utils import get_password_hash, verify_password, create_access_token, get_current_user_from_token
from .database import AuthDatabase

# Create router
router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory="webapp/templates")

# Initialize database
auth_db = AuthDatabase()

# Dependency to get current user from session
def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    username = get_current_user_from_token(token)
    if not username:
        return None
    
    return auth_db.get_user_by_username(username)

# Dependency to require authentication
def require_auth(request: Request) -> dict:
    """Require authentication - redirect to login if not authenticated"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Dependency to require admin role
def require_admin(request: Request) -> dict:
    """Require admin role"""
    user = require_auth(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ==================== PAGE ROUTES ====================

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse("auth/profile.html", {
        "request": request,
        "user": user
    })

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request):
    """Admin users management page"""
    user = require_admin(request)
    users = auth_db.get_all_users()
    
    return templates.TemplateResponse("auth/admin_users.html", {
        "request": request,
        "current_user": user,
        "users": users
    })

# ==================== API ROUTES ====================

@router.post("/api/login")
async def login_api(request: Request, response: Response):
    """API login endpoint"""
    try:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        
        if not username or not password:
            return JSONResponse(
                status_code=400,
                content={"error": "Username and password are required"}
            )
        
        # Get user from database
        user = auth_db.get_user_by_username(username)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid username or password"}
            )
        
        # Verify password
        if not verify_password(password, user["password_hash"]):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid username or password"}
            )
        
        # Check if user is active
        if user["status"] != "active":
            return JSONResponse(
                status_code=401,
                content={"error": "Account is not active"}
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["username"]})
        
        # Update last login
        auth_db.update_last_login(user["user_id"])
        
        # Log activity
        auth_db.log_user_activity(
            user["user_id"], 
            "login", 
            "system", 
            details={"ip": request.client.host if request.client else "unknown"}
        )
        
        # Set cookie
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=1800,  # 30 minutes
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Login failed: {str(e)}"}
        )

@router.post("/api/signup")
async def signup_api(request: Request):
    """API signup endpoint"""
    try:
        form_data = await request.form()
        username = form_data.get("username")
        email = form_data.get("email")
        password = form_data.get("password")
        confirm_password = form_data.get("confirm_password")
        full_name = form_data.get("full_name", "")
        
        # Validate input
        if not all([username, email, password, confirm_password]):
            return JSONResponse(
                status_code=400,
                content={"error": "All fields are required"}
            )
        
        if password != confirm_password:
            return JSONResponse(
                status_code=400,
                content={"error": "Passwords do not match"}
            )
        
        if len(password) < 8:
            return JSONResponse(
                status_code=400,
                content={"error": "Password must be at least 8 characters long"}
            )
        
        # Check if username already exists
        existing_user = auth_db.get_user_by_username(username)
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={"error": "Username already exists"}
            )
        
        # Check if email already exists
        existing_email = auth_db.get_user_by_email(email)
        if existing_email:
            return JSONResponse(
                status_code=400,
                content={"error": "Email already registered"}
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = get_password_hash(password)
        created_at = datetime.now().isoformat()
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "role": "user",
            "status": "active",
            "created_at": created_at
        }
        
        success = auth_db.create_user(user_data)
        if not success:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to create user"}
            )
        
        # Log activity
        auth_db.log_user_activity(
            user_id, 
            "user_create", 
            "user", 
            user_id,
            details={"username": username, "email": email}
        )
        
        return JSONResponse(content={"message": "User created successfully"})
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Signup failed: {str(e)}"}
        )

@router.post("/api/logout")
async def logout_api(request: Request, response: Response):
    """API logout endpoint"""
    user = get_current_user(request)
    if user:
        auth_db.log_user_activity(
            user["user_id"], 
            "logout", 
            "system"
        )
    
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    return response

@router.get("/api/profile")
async def get_profile_api(request: Request):
    """Get user profile API"""
    user = require_auth(request)
    
    return JSONResponse(content={
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "status": user["status"],
        "created_at": user["created_at"],
        "last_login": user["last_login"]
    })

@router.put("/api/profile")
async def update_profile_api(request: Request):
    """Update user profile API"""
    user = require_auth(request)
    
    try:
        form_data = await request.form()
        updates = {}
        
        # Update full name
        if "full_name" in form_data:
            updates["full_name"] = form_data["full_name"]
        
        # Update email
        if "email" in form_data:
            new_email = form_data["email"]
            # Check if email is already taken by another user
            existing_user = auth_db.get_user_by_email(new_email)
            if existing_user and existing_user["user_id"] != user["user_id"]:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Email already registered"}
                )
            updates["email"] = new_email
        
        # Update password
        if "current_password" in form_data and "new_password" in form_data:
            current_password = form_data["current_password"]
            new_password = form_data["new_password"]
            
            # Verify current password
            if not verify_password(current_password, user["password_hash"]):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Current password is incorrect"}
                )
            
            # Validate new password
            if len(new_password) < 8:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Password must be at least 8 characters long"}
                )
            
            updates["password_hash"] = get_password_hash(new_password)
        
        if updates:
            success = auth_db.update_user_profile(user["user_id"], updates)
            if not success:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to update profile"}
                )
            
            # Log activity
            auth_db.log_user_activity(
                user["user_id"], 
                "profile_update", 
                "user", 
                user["user_id"],
                details={"updated_fields": list(updates.keys())}
            )
        
        return JSONResponse(content={"message": "Profile updated successfully"})
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Profile update failed: {str(e)}"}
        )

@router.get("/api/admin/users")
async def get_users_api(request: Request):
    """Get all users (admin only)"""
    require_admin(request)
    users = auth_db.get_all_users()
    return JSONResponse(content={"users": users})

# ==================== UTILITY ROUTES ====================

@router.get("/check-auth")
async def check_auth(request: Request):
    """Check if user is authenticated"""
    user = get_current_user(request)
    if user:
        return JSONResponse(content={
            "authenticated": True,
            "user": {
                "username": user["username"],
                "role": user["role"],
                "full_name": user["full_name"]
            }
        })
    else:
        return JSONResponse(content={"authenticated": False}) 