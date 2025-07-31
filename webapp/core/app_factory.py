"""
FastAPI application factory for AASX Digital Twin Analytics Framework
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from webapp.config.settings import settings
from webapp.config.middleware import setup_middleware


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
    except ImportError as e:
        print(f"Warning: Could not import system routes: {e}")
    
    # Import and include module routes (with error handling)
    modules_config = {
        "aasx": {"enabled": settings.aasx_enabled, "prefix": "/api/aasx", "tags": ["AASX"]},
        "ai_rag": {"enabled": settings.ai_rag_enabled, "prefix": "/api/ai-rag", "tags": ["AI/RAG"]},
        "twin_registry": {"enabled": settings.twin_registry_enabled, "prefix": "/api/twin-registry", "tags": ["Twin Registry"]},
        "certificate_manager": {"enabled": settings.certificate_manager_enabled, "prefix": "/api/certificates", "tags": ["Certificate Manager"]},
        "qi_analytics": {"enabled": settings.qi_analytics_enabled, "prefix": "/api/qi-analytics", "tags": ["QI Analytics"]},
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
                print(f"✅ Loaded {module_name} module")
            except ImportError as e:
                print(f"⚠️  Could not import {module_name} module: {e}")
            except AttributeError as e:
                print(f"⚠️  {module_name} module missing router: {e}")


def create_app_with_routers() -> FastAPI:
    """Create app and include all routers"""
    app = create_app()
    include_routers(app)
    return app 