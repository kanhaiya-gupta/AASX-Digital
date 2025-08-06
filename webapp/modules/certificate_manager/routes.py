#!/usr/bin/env python3
"""
Certificate Manager Routes - Phase 1 Frontend

Basic web routes for certificate management interface.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging

# Import services
from .services.certificate_service import CertificateService
from .services.export_service import ExportService
from .services.template_service import TemplateService

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/certificate-manager", tags=["Certificate Manager"])

# Setup templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Initialize services
certificate_service = CertificateService()
export_service = ExportService()
template_service = TemplateService()


# HTML Page Routes
@router.get("/", response_class=HTMLResponse)
async def certificate_dashboard(request: Request):
    """Main certificate dashboard page."""
    try:
        logger.info("Loading certificate dashboard")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Certificate Manager Dashboard",
                "module": "certificate_manager"
            }
        )
    except Exception as e:
        logger.error(f"Failed to load certificate dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")


@router.get("/viewer/{certificate_id}", response_class=HTMLResponse)
async def certificate_viewer(request: Request, certificate_id: str):
    """Certificate viewer page."""
    try:
        logger.info(f"Loading certificate viewer for {certificate_id}")
        return templates.TemplateResponse(
            "viewer.html",
            {
                "request": request,
                "title": f"Certificate Viewer - {certificate_id}",
                "certificate_id": certificate_id,
                "module": "certificate_manager"
            }
        )
    except Exception as e:
        logger.error(f"Failed to load certificate viewer: {e}")
        raise HTTPException(status_code=500, detail="Failed to load certificate viewer")


@router.get("/export", response_class=HTMLResponse)
async def export_page(request: Request):
    """Export options page."""
    try:
        logger.info("Loading export page")
        return templates.TemplateResponse(
            "export.html",
            {
                "request": request,
                "title": "Certificate Export",
                "module": "certificate_manager"
            }
        )
    except Exception as e:
        logger.error(f"Failed to load export page: {e}")
        raise HTTPException(status_code=500, detail="Failed to load export page")


# API Routes
@router.get("/certificates")
async def get_certificates():
    """Get all certificates."""
    try:
        return await certificate_service.get_all_certificates()
    except Exception as e:
        logger.error(f"Failed to get certificates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get certificates")


@router.get("/certificates/{certificate_id}")
async def get_certificate(certificate_id: str):
    """Get specific certificate by ID."""
    try:
        certificate = await certificate_service.get_certificate_by_id(certificate_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        return certificate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get certificate {certificate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get certificate")


@router.post("/certificates")
async def create_certificate(certificate_data: dict):
    """Create a new certificate."""
    try:
        return await certificate_service.create_certificate(certificate_data)
    except Exception as e:
        logger.error(f"Failed to create certificate: {e}")
        raise HTTPException(status_code=500, detail="Failed to create certificate")


@router.put("/certificates/{certificate_id}")
async def update_certificate(certificate_id: str, updates: dict):
    """Update certificate data."""
    try:
        return await certificate_service.update_certificate(certificate_id, updates)
    except Exception as e:
        logger.error(f"Failed to update certificate {certificate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update certificate")


@router.delete("/certificates/{certificate_id}")
async def delete_certificate(certificate_id: str):
    """Delete a certificate."""
    try:
        return await certificate_service.delete_certificate(certificate_id)
    except Exception as e:
        logger.error(f"Failed to delete certificate {certificate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete certificate")


@router.get("/certificates/stats")
async def get_certificate_stats():
    """Get certificate statistics."""
    try:
        return await certificate_service.get_certificate_stats()
    except Exception as e:
        logger.error(f"Failed to get certificate stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get certificate stats")


@router.get("/certificates/search")
async def search_certificates(query: str, status: str = None, visibility: str = None):
    """Search certificates with filters."""
    try:
        filters = {"query": query}
        if status:
            filters["status"] = status
        if visibility:
            filters["visibility"] = visibility
        return await certificate_service.search_certificates(filters)
    except Exception as e:
        logger.error(f"Failed to search certificates: {e}")
        raise HTTPException(status_code=500, detail="Failed to search certificates")


@router.post("/certificates/{certificate_id}/export")
async def export_certificate(certificate_id: str, format: str = "html", template: str = "default"):
    """Export certificate in specified format."""
    try:
        return await export_service.export_certificate(certificate_id, format, template)
    except Exception as e:
        logger.error(f"Failed to export certificate {certificate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export certificate")


@router.get("/export/formats")
async def get_export_formats():
    """Get available export formats."""
    try:
        return await export_service.get_available_formats()
    except Exception as e:
        logger.error(f"Failed to get export formats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get export formats")


@router.get("/templates")
async def get_templates():
    """Get all available templates."""
    try:
        return await template_service.get_all_templates()
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get specific template by ID."""
    try:
        template = await template_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template") 