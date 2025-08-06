"""
Dashboard routes for HTML page rendering
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Get templates from app state or create new instance
def get_templates():
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    templates_dir = os.path.join(current_dir, "templates")
    return Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    templates = get_templates()
    
    # Define all available modules
    modules = [
        {
            "name": "AASX ETL Pipeline",
            "description": "Process and transform AASX files with intelligent ETL",
            "icon": "fas fa-cogs",
            "url": "/aasx"
        },
        {
            "name": "Digital Twin Registry",
            "description": "Manage and monitor digital twins in real-time",
            "icon": "fas fa-sync",
            "url": "/twin-registry"
        },
        {
            "name": "AI/RAG System",
            "description": "Intelligent analysis and retrieval with AI",
            "icon": "fas fa-robot",
            "url": "/ai-rag"
        },
        {
            "name": "Knowledge Graph",
            "description": "Explore relationships and connections in Neo4j",
            "icon": "fas fa-project-diagram",
            "url": "/kg-neo4j"
        },

        {
            "name": "Certificate Manager",
            "description": "Manage digital certificates and security",
            "icon": "fas fa-certificate",
            "url": "/certificate-manager"
        },
        {
            "name": "Federated Learning",
            "description": "Distributed machine learning across twins",
            "icon": "fas fa-network-wired",
            "url": "/federated-learning"
        },
        {
            "name": "Physics Modeling",
            "description": "Advanced physics simulation and modeling",
            "icon": "fas fa-atom",
            "url": "/physics-modeling"
        }
    ]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "modules": modules
    })


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page"""
    templates = get_templates()
    
    # Define all available modules
    modules = [
        {
            "name": "AASX ETL Pipeline",
            "description": "Process and transform AASX files with intelligent ETL",
            "icon": "fas fa-cogs",
            "url": "/aasx"
        },
        {
            "name": "Digital Twin Registry",
            "description": "Manage and monitor digital twins in real-time",
            "icon": "fas fa-sync",
            "url": "/twin-registry"
        },
        {
            "name": "AI/RAG System",
            "description": "Intelligent analysis and retrieval with AI",
            "icon": "fas fa-robot",
            "url": "/ai-rag"
        },
        {
            "name": "Knowledge Graph",
            "description": "Explore relationships and connections in Neo4j",
            "icon": "fas fa-project-diagram",
            "url": "/kg-neo4j"
        },

        {
            "name": "Certificate Manager",
            "description": "Manage digital certificates and security",
            "icon": "fas fa-certificate",
            "url": "/certificate-manager"
        },
        {
            "name": "Federated Learning",
            "description": "Distributed machine learning across twins",
            "icon": "fas fa-network-wired",
            "url": "/federated-learning"
        },
        {
            "name": "Physics Modeling",
            "description": "Advanced physics simulation and modeling",
            "icon": "fas fa-atom",
            "url": "/physics-modeling"
        }
    ]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "modules": modules
    })


@router.get("/twin-registry", response_class=HTMLResponse)
async def twin_registry_page(request: Request):
    """Twin Registry page"""
    templates = get_templates()
    return templates.TemplateResponse("twin_registry/index.html", {"request": request})


@router.get("/ai-rag", response_class=HTMLResponse)
async def ai_rag_page(request: Request):
    """AI/RAG page"""
    templates = get_templates()
    return templates.TemplateResponse("ai_rag/index.html", {"request": request})


@router.get("/kg-neo4j", response_class=HTMLResponse)
async def kg_neo4j_page(request: Request):
    """Knowledge Graph Neo4j page"""
    templates = get_templates()
    return templates.TemplateResponse("kg_neo4j/index.html", {"request": request})





@router.get("/certificate-manager", response_class=HTMLResponse)
async def certificate_manager_page(request: Request):
    """Certificate Manager page"""
    templates = get_templates()
    return templates.TemplateResponse("certificate_manager/index.html", {"request": request})


@router.get("/federated-learning", response_class=HTMLResponse)
async def federated_learning_page(request: Request):
    """Federated Learning page"""
    templates = get_templates()
    return templates.TemplateResponse("federated_learning/index.html", {"request": request})


@router.get("/physics-modeling", response_class=HTMLResponse)
async def physics_modeling_page(request: Request):
    """Physics Modeling page"""
    templates = get_templates()
    return templates.TemplateResponse("physics_modeling/index.html", {"request": request})


@router.get("/aasx", response_class=HTMLResponse)
async def aasx_page(request: Request):
    """AASX page"""
    templates = get_templates()
    return templates.TemplateResponse("aasx/index.html", {"request": request})


@router.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    """Authentication page"""
    templates = get_templates()
    return templates.TemplateResponse("auth/index.html", {"request": request})

# Flowchart pages
@router.get("/flowchart", response_class=HTMLResponse)
async def flowchart_page(request: Request):
    """Framework flowchart page"""
    templates = get_templates()
    return templates.TemplateResponse("flowchart/index.html", {"request": request})