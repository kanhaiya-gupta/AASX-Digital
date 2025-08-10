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
            "url": "/api/aasx-etl"
        },
        {
            "name": "Digital Twin Registry",
            "description": "Manage and monitor digital twins in real-time",
            "icon": "fas fa-sync",
            "url": "/api/twin-registry"
        },
        {
            "name": "AI/RAG System",
            "description": "Intelligent analysis and retrieval with AI",
            "icon": "fas fa-robot",
            "url": "/api/ai-rag"
        },
        {
            "name": "Knowledge Graph",
            "description": "Explore relationships and connections in Neo4j",
            "icon": "fas fa-project-diagram",
            "url": "/api/kg-neo4j"
        },

        {
            "name": "Certificate Manager",
            "description": "Manage digital certificates and security",
            "icon": "fas fa-certificate",
            "url": "/api/certificate-manager"
        },
        {
            "name": "Federated Learning",
            "description": "Distributed machine learning across twins",
            "icon": "fas fa-network-wired",
            "url": "/api/federated-learning"
        },
        {
            "name": "Physics Modeling",
            "description": "Advanced physics simulation and modeling",
            "icon": "fas fa-atom",
            "url": "/api/physics-modeling"
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
            "url": "/api/aasx-etl"
        },
        {
            "name": "Digital Twin Registry",
            "description": "Manage and monitor digital twins in real-time",
            "icon": "fas fa-sync",
            "url": "/api/twin-registry"
        },
        {
            "name": "AI/RAG System",
            "description": "Intelligent analysis and retrieval with AI",
            "icon": "fas fa-robot",
            "url": "/api/ai-rag"
        },
        {
            "name": "Knowledge Graph",
            "description": "Explore relationships and connections in Neo4j",
            "icon": "fas fa-project-diagram",
            "url": "/api/kg-neo4j"
        },

        {
            "name": "Certificate Manager",
            "description": "Manage digital certificates and security",
            "icon": "fas fa-certificate",
            "url": "/api/certificate-manager"
        },
        {
            "name": "Federated Learning",
            "description": "Distributed machine learning across twins",
            "icon": "fas fa-network-wired",
            "url": "/api/federated-learning"
        },
        {
            "name": "Physics Modeling",
            "description": "Advanced physics simulation and modeling",
            "icon": "fas fa-atom",
            "url": "/api/physics-modeling"
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


@router.get("/aasx-etl", response_class=HTMLResponse)
async def aasx_page(request: Request):
    """AASX page"""
    templates = get_templates()
    return templates.TemplateResponse("aasx/index.html", {"request": request})


# Flowchart pages
@router.get("/flowchart", response_class=HTMLResponse)
async def flowchart_page(request: Request):
    """Framework flowchart page"""
    templates = get_templates()
    return templates.TemplateResponse("flowchart/index.html", {"request": request})


# API endpoints for dashboard data
@router.get("/api/dashboard/charts")
async def get_dashboard_charts():
    """Get dashboard charts data"""
    # Mock data for now - replace with actual data source
    charts_data = {
        "charts": [
            {
                "id": "system_health",
                "type": "line",
                "title": "System Health",
                "data": {
                    "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
                    "datasets": [{
                        "label": "CPU Usage",
                        "data": [45, 52, 38, 65, 72, 58],
                        "borderColor": "#007bff"
                    }]
                }
            },
            {
                "id": "active_twins",
                "type": "bar",
                "title": "Active Digital Twins",
                "data": {
                    "labels": ["AASX", "Twin Registry", "AI/RAG", "Knowledge Graph"],
                    "datasets": [{
                        "label": "Active Count",
                        "data": [12, 8, 15, 6],
                        "backgroundColor": ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
                    }]
                }
            }
        ]
    }
    return charts_data


@router.get("/api/dashboard/kpis")
async def get_dashboard_kpis():
    """Get dashboard KPI data"""
    # Mock data for now - replace with actual data source
    kpi_data = {
        "kpis": [
            {
                "id": "total_twins",
                "title": "Total Digital Twins",
                "value": 156,
                "change": "+12",
                "change_type": "positive",
                "icon": "fas fa-sync"
            },
            {
                "id": "active_processes",
                "title": "Active Processes",
                "value": 23,
                "change": "-3",
                "change_type": "negative",
                "icon": "fas fa-cogs"
            },
            {
                "id": "system_uptime",
                "title": "System Uptime",
                "value": "99.8%",
                "change": "+0.2%",
                "change_type": "positive",
                "icon": "fas fa-server"
            },
            {
                "id": "data_processed",
                "title": "Data Processed (GB)",
                "value": "2.4",
                "change": "+0.8",
                "change_type": "positive",
                "icon": "fas fa-database"
            }
        ]
    }
    return kpi_data


@router.get("/api/dashboard/activity")
async def get_dashboard_activity():
    """Get dashboard activity feed"""
    # Mock data for now - replace with actual data source
    activity_data = {
        "activities": [
            {
                "id": 1,
                "type": "info",
                "message": "New AASX file uploaded and processed",
                "timestamp": "2025-08-10T21:30:00Z",
                "user": "System"
            },
            {
                "id": 2,
                "type": "success",
                "message": "Digital twin synchronization completed",
                "timestamp": "2025-08-10T21:25:00Z",
                "user": "Auto-Sync"
            },
            {
                "id": 3,
                "type": "warning",
                "message": "High CPU usage detected on server-02",
                "timestamp": "2025-08-10T21:20:00Z",
                "user": "Monitoring"
            }
        ]
    }
    return activity_data


@router.get("/api/activity/latest")
async def get_latest_activity():
    """Get latest activity feed data"""
    # Mock data for now - replace with actual data source
    activity_data = {
        "activities": [
            {
                "id": 1,
                "type": "info",
                "message": "New AASX file uploaded and processed",
                "timestamp": "2025-08-10T21:30:00Z",
                "user": "System"
            },
            {
                "id": 2,
                "type": "success",
                "message": "Digital twin synchronization completed",
                "timestamp": "2025-08-10T21:25:00Z",
                "user": "Auto-Sync"
            },
            {
                "id": 3,
                "type": "warning",
                "message": "High CPU usage detected on server-02",
                "timestamp": "2025-08-10T21:20:00Z",
                "user": "Monitoring"
            }
        ]
    }
    return activity_data