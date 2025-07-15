#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AASX Digital Twin Analytics Framework
Main FastAPI application for the AASX Digital Twin Analytics Framework.
"""

import os
# Set default SECRET_KEY for development
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import time
import json
from pathlib import Path
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="AASX Digital Twin Analytics Framework",
    description="A comprehensive framework for processing AASX files and building digital twin analytics with ETL, Knowledge Graph, and AI/RAG capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Import routers from individual modules (with error handling)
ai_rag_router = None
twin_registry_router = None
certificate_manager_router = None
qi_analytics_router = None
aasx_router = None
kg_neo4j_router = None
aasx_explorer_router = None

try:
    from webapp.ai_rag.routes import router as ai_rag_router
    app.include_router(ai_rag_router, prefix="/ai-rag", tags=["ai-rag"])
    print("✅ AI/RAG router loaded successfully")
except Exception as e:
    print(f"⚠️  AI/RAG router failed to load: {e}")

try:
    from webapp.kg_neo4j.routes import router as kg_neo4j_router
    app.include_router(kg_neo4j_router, prefix="/kg-neo4j", tags=["kg-neo4j"])
    print("✅ Knowledge Graph router loaded successfully")
except Exception as e:
    print(f"⚠️  Knowledge Graph router failed to load: {e}")

# Import twin registry router
try:
    from webapp.twin_registry.routes import router as twin_registry_router
    print("✅ Twin Registry router imported successfully")
    app.include_router(twin_registry_router, prefix="/twin-registry", tags=["twin-registry"])
except Exception as e:
    print(f"❌ Error importing Twin Registry router: {e}")
    twin_registry_router = None

try:
    from webapp.certificate_manager.routes import router as certificate_manager_router
    app.include_router(certificate_manager_router, prefix="/certificates", tags=["certificates"])
    print("✅ Certificate Manager router loaded successfully")
except Exception as e:
    print(f"⚠️  Certificate Manager router failed to load: {e}")

try:
    from webapp.qi_analytics.routes import router as qi_analytics_router
    app.include_router(qi_analytics_router, prefix="/analytics", tags=["analytics"])
    print("✅ QI Analytics router loaded successfully")
except Exception as e:
    print(f"⚠️  QI Analytics router failed to load: {e}")

try:
    from webapp.aasx.routes import router as aasx_router
    app.include_router(aasx_router, prefix="/aasx", tags=["aasx"])
    print("✅ AASX router loaded successfully")
except Exception as e:
    print(f"⚠️  AASX router failed to load: {e}")

try:
    from webapp.aasx_explorer.routes import router as aasx_explorer_router
    app.include_router(aasx_explorer_router, prefix="/aasx-explorer", tags=["aasx-explorer"])
    print("✅ AASX Explorer router loaded successfully")
except Exception as e:
    print(f"⚠️  AASX Explorer router failed to load: {e}")

# Main dashboard route
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "AASX Digital Twin Analytics Framework",
            "modules": [
                {
                    "id": "aasx-etl",
                    "name": "AASX ETL Pipeline",
                    "description": "Extract, Transform, Load AASX files into structured data",
                    "url": "/aasx",
                    "icon": "⚙️",
                    "available": aasx_router is not None
                },
                {
                    "id": "kg-neo4j",
                    "name": "Knowledge Graph",
                    "description": "Neo4j knowledge graph explorer and analytics",
                    "url": "/kg-neo4j",
                    "icon": "🕸️",
                    "available": kg_neo4j_router is not None
                },
                {
                    "id": "ai-rag",
                    "name": "AI/RAG System",
                    "description": "AI-powered analysis and insights for digital twins",
                    "url": "/ai-rag",
                    "icon": "🤖",
                    "available": ai_rag_router is not None
                },
                {
                    "id": "twin-registry",
                    "name": "Digital Twin Registry",
                    "description": "Manage and monitor digital twin registrations",
                    "url": "/twin-registry",
                    "icon": "🔄",
                    "available": twin_registry_router is not None
                },
                {
                    "id": "certificates",
                    "name": "Certificate Manager",
                    "description": "Digital certificates and compliance management",
                    "url": "/certificates",
                    "icon": "📜",
                    "available": certificate_manager_router is not None
                },
                {
                    "id": "analytics",
                    "name": "Analytics Dashboard",
                    "description": "Digital twin analytics and visualization",
                    "url": "/analytics",
                    "icon": "📊",
                    "available": qi_analytics_router is not None
                }
            ]
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "aasx-digital-twin-analytics-framework",
        "version": "1.0.0",
        "timestamp": time.time(),
        "modules": {
            "ai_rag": ai_rag_router is not None,
            "kg_neo4j": kg_neo4j_router is not None,
            "twin_registry": twin_registry_router is not None,
            "certificate_manager": certificate_manager_router is not None,
            "qi_analytics": qi_analytics_router is not None,
            "aasx": aasx_router is not None
        }
    }

# API status endpoint (for frontend compatibility)
@app.get("/api/status")
async def api_status():
    """API status endpoint for frontend compatibility"""
    return {
        "status": "available",
        "service": "aasx-digital-twin-analytics-framework",
        "version": "1.0.0",
        "timestamp": time.time(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "aasx": "/aasx",
            "kg_neo4j": "/kg-neo4j",
            "ai_rag": "/ai-rag",
            "twin_registry": "/twin-registry",
            "certificates": "/certificates",
            "analytics": "/analytics"
        }
    }

# PyTorch status endpoint (for frontend compatibility)
@app.get("/api/pytorch/status")
async def pytorch_status():
    """PyTorch status endpoint for frontend compatibility"""
    try:
        import torch
        return {
            "status": "available",
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "timestamp": time.time()
        }
    except ImportError:
        return {
            "status": "unavailable",
            "error": "PyTorch not installed",
            "timestamp": time.time()
        }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Send periodic status updates
            status_data = {
                "type": "status",
                "timestamp": time.time(),
                "services": {
                    "ai_rag": ai_rag_router is not None,
                    "kg_neo4j": kg_neo4j_router is not None,
                    "twin_registry": twin_registry_router is not None,
                    "certificate_manager": certificate_manager_router is not None,
                    "qi_analytics": qi_analytics_router is not None,
                    "aasx": aasx_router is not None
                }
            }
            await websocket.send_text(json.dumps(status_data))
            
            # Wait for 30 seconds before next update
            import asyncio
            await asyncio.sleep(30)
            
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

# ETL status endpoint (for frontend compatibility)
@app.get("/etl/status")
async def get_etl_status():
    """ETL pipeline status endpoint for frontend compatibility"""
    try:
        if aasx_router is None:
            return {
                "status": "unavailable",
                "error": "AASX router not loaded",
                "timestamp": time.time()
            }
        
        # Import the function from aasx routes
        from webapp.aasx.routes import get_etl_pipeline
        
        pipeline = get_etl_pipeline()
        
        # Get pipeline validation status
        validation_status = "unknown"
        try:
            validation_result = pipeline.validate_pipeline()
            validation_status = "valid" if validation_result else "invalid"
        except Exception:
            validation_status = "error"
        
        # Get pipeline stats
        stats = {}
        try:
            stats = pipeline.get_pipeline_stats()
        except Exception:
            stats = {"error": "Failed to get pipeline stats"}
        
        return {
            "status": "available",
            "pipeline": "ready",
            "validation": validation_status,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Twin Registry status endpoint (for frontend compatibility)
@app.get("/twin-registry/status")
async def get_twin_registry_status():
    """Twin registry status endpoint for frontend compatibility"""
    try:
        if twin_registry_router is None:
            return {
                "status": "unavailable",
                "error": "Twin registry router not loaded",
                "timestamp": time.time()
            }
        
        # Import the function from twin registry routes
        from webapp.twin_registry.routes import get_twin_registry_status as get_status
        
        return await get_status()
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# API documentation redirect
@app.get("/docs")
async def api_docs():
    """Redirect to API documentation"""
    return {"message": "API documentation available at /docs"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    try:
        return templates.TemplateResponse(
            "404.html",
            {
                "request": request,
                "title": "Page Not Found - AASX Digital Twin Analytics Framework"
            },
            status_code=404
        )
    except Exception:
        # Fallback to simple JSON response if template fails
        return {"error": "Page not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    try:
        return templates.TemplateResponse(
            "500.html",
            {
                "request": request,
                "title": "Internal Server Error - AASX Digital Twin Analytics Framework"
            },
            status_code=500
        )
    except Exception:
        # Fallback to simple JSON response if template fails
        return {"error": "Internal server error", "status_code": 500}

# Module-specific routes (with availability checks)
@app.get("/ai-rag", response_class=HTMLResponse)
async def ai_rag_page(request: Request):
    """AI/RAG System page"""
    if ai_rag_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "AI/RAG System - Not Available",
                "error": "AI/RAG module is not available. Please check the src services.",
                "back_url": "/"
            }
        )
    
    return templates.TemplateResponse(
        "ai_rag/index.html",
        {
            "request": request,
            "title": "AI/RAG System",
            "module_name": "AI/RAG System",
            "description": "AI-powered analysis and insights for digital twins"
        }
    )

@app.get("/twin-registry", response_class=HTMLResponse)
async def twin_registry_page(request: Request):
    """Twin registry page"""
    print(f"🔍 Twin Registry page requested. Router available: {twin_registry_router is not None}")
    
    if twin_registry_router is None:
        print("❌ Twin Registry router is None, showing error page")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework",
                "error": "Twin Registry module is not available."
            }
        )
    
    print("✅ Serving Twin Registry page")
    return templates.TemplateResponse(
        "twin_registry/index.html",
        {
            "request": request,
            "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/twin-registry-test", response_class=HTMLResponse)
async def twin_registry_test_page(request: Request):
    """Test twin registry template"""
    print("🧪 Serving Twin Registry test page")
    return templates.TemplateResponse(
        "twin_registry/test.html",
        {
            "request": request,
            "title": "Twin Registry Test"
        }
    )

@app.get("/certificates", response_class=HTMLResponse)
async def certificates_page(request: Request):
    """Certificate manager page"""
    if certificate_manager_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Certificate Manager - AASX Digital Twin Analytics Framework",
                "error": "Certificate Manager module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "certificate_manager/index.html",
        {
            "request": request,
            "title": "Certificate Manager - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard page"""
    if qi_analytics_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Analytics Dashboard - AASX Digital Twin Analytics Framework",
                "error": "Analytics module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "qi_analytics/index.html",
        {
            "request": request,
            "title": "Analytics Dashboard - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/kg-neo4j", response_class=HTMLResponse)
async def kg_neo4j_page(request: Request):
    """Knowledge Graph page"""
    if kg_neo4j_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Knowledge Graph - AASX Digital Twin Analytics Framework",
                "error": "Knowledge Graph module is not available. Please check Neo4j connection."
            }
        )
    
    return templates.TemplateResponse(
        "kg_neo4j/index.html",
        {
            "request": request,
            "title": "Knowledge Graph - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/flowchart", response_class=HTMLResponse)
async def flowchart_page(request: Request):
    """Flowchart page showing the complete framework processing flow with tabs"""
    return templates.TemplateResponse(
        "flowchart/framework_flowchart.html",
        {
            "request": request,
            "title": "Processing Flow - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/etl-flowchart", response_class=HTMLResponse)
async def etl_flowchart_page(request: Request):
    """ETL page flowchart showing detailed user journey and system architecture"""
    return templates.TemplateResponse(
        "flowchart/etl_page_flowchart.html",
        {
            "request": request,
            "title": "ETL Page Flowchart - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/aasx-integration-flowchart", response_class=HTMLResponse)
async def aasx_integration_flowchart_page(request: Request):
    """AASX Auto Integration flowchart showing digital twin registration process"""
    return templates.TemplateResponse(
        "flowchart/aasx_integration_flowchart.html",
        {
            "request": request,
            "title": "AASX Auto Integration Flowchart - Digital Twin Analytics Framework"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
