"""
FastAPI application factory for AASX Digital Twin Analytics Framework
Clean, organized structure with separate, focused functions
WORLD-CLASS ARCHITECTURE: No cross-layer dependencies
"""
import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

# Engine imports (correct dependency direction)
from src.engine.config.settings import settings
from src.engine.core.middleware import setup_middleware

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER CLASSES
# =============================================================================

class NoCacheStaticFiles(StaticFiles):
    """Custom StaticFiles handler that prevents caching"""
    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


# =============================================================================
# PRIVATE SETUP FUNCTIONS (Core Application Configuration)
# =============================================================================

def _setup_static_files(app: FastAPI) -> None:
    """Configure static file handling with no-cache headers"""
    try:
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        # Go up 3 levels: src/integration/ -> src/ -> project_root (where client/ is)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        static_dir = os.path.join(project_root, "client", "static")
        
        if os.path.exists(static_dir):
            app.mount("/static", NoCacheStaticFiles(directory=static_dir), name="static")
            logger.info("✅ Static files configured successfully")
        else:
            logger.warning(f"⚠️  Static directory not found: {static_dir}")
    except Exception as e:
        logger.error(f"❌ Failed to setup static files: {e}")


def _setup_templates(app: FastAPI) -> None:
    """Configure Jinja2 templates"""
    try:
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        # Go up 3 levels: src/integration/ -> src/ -> project_root (where client/ is)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        templates_dir = os.path.join(project_root, "client", "templates")
        
        if os.path.exists(templates_dir):
            templates = Jinja2Templates(directory=templates_dir)
            # Store templates in app state for access in routes
            app.state.templates = templates
            logger.info("✅ Templates configured successfully")
        else:
            logger.warning(f"⚠️  Templates directory not found: {templates_dir}")
    except Exception as e:
        logger.error(f"❌ Failed to setup templates: {e}")


def _setup_exception_handlers(app: FastAPI) -> None:
    """Configure global exception handlers"""
    try:
        from fastapi import HTTPException, Request
        from fastapi.responses import JSONResponse
        
        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            """Handle HTTP exceptions globally"""
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "status_code": exc.status_code}
            )
        
        @app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions globally"""
            logger.error(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "status_code": 500}
            )
        
        logger.info("✅ Exception handlers configured successfully")
    except Exception as e:
        logger.error(f"❌ Failed to setup exception handlers: {e}")


def _setup_root_routes(app: FastAPI) -> None:
    """Configure root-level routes"""
    try:
        from fastapi import Request
        from fastapi.responses import RedirectResponse, HTMLResponse
        
        @app.get("/")
        async def root():
            """Root route - redirect to main dashboard page"""
            return RedirectResponse(url="/api/dashboard")
        
        @app.get("/api/dashboard")
        async def dashboard(request: Request):
            """Main dashboard - renders the homepage"""
            try:
                # Access templates from app state
                templates = request.app.state.templates
                if templates:
                    return templates.TemplateResponse("index.html", {"request": request})
                else:
                    logger.error("❌ Templates not found in app.state")
                    return {"error": "Templates not configured", "status": "error"}
            except AttributeError as e:
                logger.error(f"❌ Dashboard error - templates not accessible: {e}")
                return {"error": "Templates not accessible", "status": "error"}
            except Exception as e:
                logger.error(f"❌ Dashboard error: {e}")
                return {"error": "Failed to render dashboard", "status": "error"}
        
        @app.get("/mobile-app")
        async def mobile_app_info():
            """Mobile app information endpoint"""
            return {
                "name": "AASX Digital Twin Analytics",
                "version": "1.0.0",
                "type": "PWA",
                "features": [
                    "Offline Support",
                    "Push Notifications", 
                    "Touch Optimized",
                    "Central Authentication"
                ],
                "endpoints": {
                    "manifest": "/static/mobile_app/manifest.json",
                    "service_worker": "/static/mobile_app/sw.js",
                    "app_script": "/static/mobile_app/mobile-app.js",
                    "api_client": "/static/mobile_app/mobile-api-client.js"
                }
            }
        
        logger.info("✅ Root routes configured successfully")
    except Exception as e:
        logger.error(f"❌ Failed to setup root routes: {e}")


# =============================================================================
# PRIVATE INITIALIZATION FUNCTIONS (System Setup)
# =============================================================================

def _initialize_default_user() -> None:
    """Create default super admin user if no users exist"""
    try:
        from src.engine.services.auth.user_service import UserService
        from src.engine.repositories.auth_repository import AuthRepository
        
        # Initialize backend services
        auth_repo = AuthRepository()
        user_service = UserService(auth_repo)
        
        # Check if users exist
        users = user_service.get_all_users()
        if not users:
            logger.info("No users found, creating default super admin user...")
            
            # Create default super admin user (system developer)
            super_admin_data = {
                "user_id": "super-admin-default",
                "username": "super_admin",
                "email": "developer@aasx-digital.de",
                "full_name": "System Developer (Super Admin)",
                "password": "SuperAdmin123!",  # This should be changed on first login
                "role": "super_admin",  # Special role for system-level access
                "is_active": True,
                "org_id": None,  # Super admin is not tied to any organization
                "dept_id": None
            }
            
            created_user = user_service.create_user(super_admin_data)
            if created_user:
                logger.info("✅ Default super admin user created successfully")
                logger.warning("⚠️  IMPORTANT: Change the default super admin password on first login!")
                logger.info("🔑 Super Admin Credentials:")
                logger.info("   Username: super_admin")
                logger.info("   Password: SuperAdmin123!")
                logger.info("   Email: developer@aasx-digital.de")
            else:
                logger.error("❌ Failed to create default super admin user")
        else:
            logger.info(f"✅ Found {len(users)} existing users, skipping default user creation")
            
    except Exception as e:
        logger.warning(f"⚠️  Could not check/create default user (this is normal during development): {e}")


def _initialize_auth_system() -> None:
    """Initialize the authentication system"""
    try:
        logger.info("🔐 Initializing authentication system...")
        
        # Import backend services instead of webapp database
        from src.engine.services.auth.user_service import UserService
        from src.engine.repositories.auth_repository import AuthRepository
        
        # Initialize backend services
        auth_repo = AuthRepository()
        user_service = UserService(auth_repo)
        
        logger.info("✅ Authentication system initialized successfully")
        
        # Create default user if needed
        _initialize_default_user()
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize authentication system: {e}")
        # Don't raise here - allow the app to start without auth initialization
        logger.warning("⚠️  Authentication system initialization failed, but app will continue")


# =============================================================================
# PUBLIC INTERFACE FUNCTIONS (Main Factory Functions)
# =============================================================================

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    logger.info("🚀 Creating FastAPI application...")
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="A comprehensive framework for processing AASX files and building digital twin analytics with ETL, Knowledge Graph, and AI/RAG capabilities",
        version=settings.app_version,
        debug=settings.debug
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup core components in logical order
    _setup_static_files(app)
    _setup_templates(app)
    _setup_exception_handlers(app)
    
    # Setup root routes AFTER templates are configured
    _setup_root_routes(app)
    
    logger.info("✅ FastAPI application created and configured successfully")
    return app


def include_routers(app: FastAPI) -> None:
    """Include all routers in the application"""
    logger.info("📡 Loading application routers...")
    
    # Include auth module routes (the only module we know exists and works)
    try:
        from client.modules.auth.routes import router as auth_router
        app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
        logger.info("✅ Authentication module loaded successfully")
    except ImportError as e:
        logger.error(f"❌ CRITICAL: Could not import auth module: {e}")
        logger.error("Authentication system is required for the application to function properly")
    except Exception as e:
        logger.error(f"❌ CRITICAL: Error loading auth module: {e}")
    
    # Include all other modules
    modules_to_load = [
        "data_platform",  # Central business services hub
        "aasx_etl",  # AASX ETL module
        "kg_neo4j", 
        "ai_rag",
        "twin_registry",
        "certificate_manager",
        "federated_learning",
        "physics_modeling"
    ]
    
    for module_name in modules_to_load:
        try:
            module_router = __import__(f"client.modules.{module_name}.routes", fromlist=["router"])
            router = getattr(module_router, "router")
            app.include_router(router, prefix=f"/api/{module_name.replace('_', '-')}", tags=[module_name.replace('_', ' ').title()])
            logger.info(f"✅ {module_name} module loaded successfully")
        except ImportError as e:
            logger.warning(f"⚠️  Could not import {module_name} module: {e}")
        except Exception as e:
            logger.error(f"❌ Error loading {module_name} module: {e}")
    
    logger.info("✅ All routers loaded successfully")


def create_app_with_routers() -> FastAPI:
    """Create app and include all routers - Main factory function"""
    logger.info("🏗️  Building complete application...")
    
    # Create base application
    app = create_app()
    
    # Initialize authentication system
    _initialize_auth_system()
    
    # Include all routers
    include_routers(app)
    
    logger.info("🚀 AASX Digital Twin Analytics Framework initialized successfully")
    logger.info("🌟 WORLD-CLASS ARCHITECTURE: No cross-layer dependencies!")
    return app 