"""
FastAPI application factory for AASX Digital Twin Analytics Framework
"""
import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from webapp.config.settings import settings
from webapp.config.middleware import setup_middleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="A comprehensive framework for processing AASX files and building digital twin analytics with ETL, Knowledge Graph, and AI/RAG capabilities",
        version=settings.app_version,
        debug=settings.debug
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Mount static files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(os.path.dirname(current_dir), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Setup templates
    templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
    templates = Jinja2Templates(directory=templates_dir)
    
    # Store templates in app state for access in routes
    app.state.templates = templates
    
    return app


def include_routers(app: FastAPI) -> None:
    """Include all routers in the application"""
    
    # Import and include system routes
    try:
        from webapp.api.routes import health, dashboard, websocket, system
        app.include_router(health.router, prefix="/api", tags=["Health"])
        app.include_router(dashboard.router, tags=["Dashboard"])
        app.include_router(websocket.router, tags=["WebSocket"])
        app.include_router(system.router, prefix="/api", tags=["System"])
        logger.info("✅ Loaded system routes")
    except ImportError as e:
        logger.warning(f"Could not import system routes: {e}")
    
    # Import and include AUTH routes (single router approach)
    try:
        from webapp.modules.auth.routes import router as auth_router
        
        # Include auth routes at /api/auth/ (for both pages and API)
        app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
        
        logger.info("✅ Loaded authentication module")
    except ImportError as e:
        logger.error(f"❌ CRITICAL: Could not import auth module: {e}")
        logger.error("Authentication system is required for the application to function properly")
    except Exception as e:
        logger.error(f"❌ CRITICAL: Error loading auth module: {e}")
    
    # Import and include module routes (with error handling)
    modules_config = {
        "aasx": {"enabled": settings.aasx_enabled, "prefix": "/api/aasx-etl", "tags": ["AASX"]},
        "ai_rag": {"enabled": settings.ai_rag_enabled, "prefix": "/api/ai-rag", "tags": ["AI/RAG"]},
        "twin_registry": {"enabled": settings.twin_registry_enabled, "prefix": "/api/twin-registry", "tags": ["Twin Registry"]},
        "certificate_manager": {"enabled": settings.certificate_manager_enabled, "prefix": "/api/certificate-manager", "tags": ["Certificate Manager"]},
        "kg_neo4j": {"enabled": settings.kg_neo4j_enabled, "prefix": "/api/kg-neo4j", "tags": ["Knowledge Graph"]},
        "federated_learning": {"enabled": settings.federated_learning_enabled, "prefix": "/api/federated-learning", "tags": ["Federated Learning"]},
        "physics_modeling": {"enabled": settings.physics_modeling_enabled, "prefix": "/api/physics-modeling", "tags": ["Physics Modeling"]}
    }
    
    for module_name, config in modules_config.items():
        if config["enabled"]:
            try:
                module = __import__(f"webapp.modules.{module_name}.routes", fromlist=["router"])
                app.include_router(
                    module.router,
                    prefix=config["prefix"],
                    tags=config["tags"]
                )
                logger.info(f"✅ Loaded {module_name} module")
            except ImportError as e:
                logger.warning(f"Could not import {module_name} module: {e}")
            except AttributeError as e:
                logger.warning(f"{module_name} module missing router: {e}")
            except Exception as e:
                logger.error(f"Error loading {module_name} module: {e}")


def initialize_auth_system() -> None:
    """Initialize the authentication system"""
    try:
        from webapp.modules.auth.database import AuthDatabase
        
        # Initialize the auth database
        auth_db = AuthDatabase()
        logger.info("✅ Authentication system initialized successfully")
        
        # Create default super admin user if no users exist
        users = auth_db.get_all_users()
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
                "organization_id": None  # Super admin is not tied to any organization
            }
            
            created_user = auth_db.create_user(super_admin_data)
            if created_user:
                logger.info("✅ Default super admin user created successfully")
                logger.warning("⚠️  IMPORTANT: Change the default super admin password on first login!")
                logger.info("🔑 Super Admin Credentials:")
                logger.info("   Username: super_admin")
                logger.info("   Password: SuperAdmin123!")
                logger.info("   Email: developer@aasx-digital.de")
            else:
                logger.error("❌ Failed to create default super admin user")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize authentication system: {e}")
        raise


def create_app_with_routers() -> FastAPI:
    """Create app and include all routers"""
    app = create_app()
    
    # Initialize authentication system
    initialize_auth_system()
    
    # Include all routers
    include_routers(app)
    
    logger.info("🚀 AASX Digital Twin Analytics Framework initialized successfully")
    return app 