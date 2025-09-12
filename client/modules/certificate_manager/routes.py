#!/usr/bin/env python3
"""
Certificate Manager Routes - Phase 1 Frontend

Basic web routes for certificate management interface.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging

# Import authentication decorators and user context
from src.integration.api.dependencies import require_auth, get_current_user
from src.engine.models.request_context import UserContext

# Import services
from .services.certificate_service import CertificateService
from .services.export_service import ExportService
from .services.template_service import TemplateService
from .services.user_specific_service import CertificateManagerUserSpecificService
from .services.organization_service import CertificateManagerOrganizationService

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
async def certificate_dashboard(
    request: Request,
    user_context: UserContext = Depends(require_auth)
):
    """Main certificate dashboard page."""
    try:
        logger.info(f"Loading certificate dashboard for user {getattr(user_context, 'user_id', 'unknown')}")
        
        # Initialize user-specific and organization services
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        organization_service = CertificateManagerOrganizationService(user_context)
        
        # Get user-specific and organization data
        user_certificates = await user_specific_service.get_user_certificates()
        user_stats = await user_specific_service.get_user_certificate_stats()
        user_templates = await user_specific_service.get_user_templates()
        organization_stats = await organization_service.get_organization_stats()
        organization_health = await organization_service.get_organization_health()
        
        # Check user permissions
        can_create_certificate = user_specific_service.can_create_certificate()
        can_manage_org = organization_service.can_manage_organization()
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Certificate Manager Dashboard",
                "module": "certificate_manager",
                "user_context": user_context,
                "can_create_certificate": can_create_certificate,
                "can_manage_org": can_manage_org,
                "is_independent": getattr(user_context, 'is_independent', None),
                "user_type": getattr(user_context, 'get_user_type', lambda: 'independent')(),
                "user_certificates": user_certificates,
                "user_stats": user_stats,
                "user_templates": user_templates,
                "organization_stats": organization_stats,
                "organization_health": organization_health
            }
        )
    except Exception as e:
        logger.error(f"Failed to load certificate dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")


@router.get("/viewer/{certificate_id}", response_class=HTMLResponse)
async def certificate_viewer(
    request: Request, 
    certificate_id: str,
    user_context: UserContext = Depends(require_auth)
):
    """Certificate viewer page."""
    try:
        logger.info(f"Loading certificate viewer for {certificate_id} by user {getattr(user_context, 'user_id', 'unknown')}")
        
        # Initialize user-specific service to check access
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Check if user can access this certificate
        if not user_specific_service.can_access_certificate(certificate_id):
            raise HTTPException(status_code=403, detail="Access denied to this certificate")
        
        return templates.TemplateResponse(
            "viewer.html",
            {
                "request": request,
                "title": f"Certificate Viewer - {certificate_id}",
                "certificate_id": certificate_id,
                "module": "certificate_manager",
                "user_context": user_context,
                "can_export": user_specific_service.can_export_certificate(certificate_id),
                "can_update": user_specific_service.can_update_certificate(certificate_id),
                "can_delete": user_specific_service.can_delete_certificate(certificate_id)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load certificate viewer: {e}")
        raise HTTPException(status_code=500, detail="Failed to load certificate viewer")


@router.get("/export", response_class=HTMLResponse)
async def export_page(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Export options page."""
    try:
        logger.info(f"Loading export page for user {getattr(user_context, 'user_id', 'unknown')}")
        
        # Initialize user-specific service
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Get user export history and limits
        export_history = await user_specific_service.get_user_export_history()
        export_limits = user_specific_service.get_user_certificate_limits()
        
        return templates.TemplateResponse(
            "export.html",
            {
                "request": request,
                "title": "Certificate Export",
                "module": "certificate_manager",
                "user_context": user_context,
                "export_history": export_history,
                "export_limits": export_limits,
                "can_export": True  # Basic export permission
            }
        )
    except Exception as e:
        logger.error(f"Failed to load export page: {e}")
        raise HTTPException(status_code=500, detail="Failed to load export page")


# API Routes
@router.get("/certificates")
async def get_certificates(user_context: UserContext = Depends(get_current_user)):
    """Get all certificates."""
    try:
        # Initialize user-specific service
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Return user-specific certificates
        user_certificates = await user_specific_service.get_user_certificates()
        return {
            "certificates": user_certificates,
            "count": len(user_certificates),
            "timestamp": "2024-01-15T10:30:00Z",
            "user_id": getattr(user_context, 'user_id', None),
            "organization_id": getattr(user_context, 'organization_id', None)
        }
    except Exception as e:
        logger.error(f"Failed to get certificates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get certificates")


@router.get("/certificates/{certificate_id}")
async def get_certificate(
    certificate_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get specific certificate by ID."""
    try:
        # Initialize user-specific service to check access
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Check if user can access this certificate
        if not user_specific_service.can_access_certificate(certificate_id):
            raise HTTPException(status_code=403, detail="Access denied to this certificate")
        
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
async def create_certificate(
    certificate_data: dict,
    user_context: UserContext = Depends(get_current_user)
):
    """Create a new certificate."""
    try:
        # Initialize user-specific service to check permissions
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Check if user can create certificates
        if not user_specific_service.can_create_certificate():
            raise HTTPException(status_code=403, detail="Insufficient permissions to create certificates")
        
        # Add user context to certificate data
        enhanced_data = {
            **certificate_data,
            "created_by": getattr(user_context, 'user_id', None),
            "organization_id": getattr(user_context, 'organization_id', None)
        }
        
        return await certificate_service.create_certificate(enhanced_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create certificate: {e}")
        raise HTTPException(status_code=500, detail="Failed to create certificate")


@router.put("/certificates/{certificate_id}")
async def update_certificate(
    certificate_id: str, 
    updates: dict,
    user_context: UserContext = Depends(get_current_user)
):
    """Update certificate data."""
    try:
        # Initialize user-specific service to check permissions
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Check if user can update this certificate
        if not user_specific_service.can_update_certificate(certificate_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to update this certificate")
        
        return await certificate_service.update_certificate(certificate_id, updates)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update certificate {certificate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update certificate")


@router.delete("/certificates/{certificate_id}")
async def delete_certificate(
    certificate_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Delete a certificate."""
    try:
        # Initialize user-specific service to check permissions
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Check if user can delete this certificate
        if not user_specific_service.can_delete_certificate(certificate_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to delete this certificate")
        
        return await certificate_service.delete_certificate(certificate_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete certificate {certificate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete certificate")


@router.get("/certificates/stats")
async def get_certificate_stats(user_context: UserContext = Depends(get_current_user)):
    """Get certificate statistics."""
    try:
        # Initialize user-specific and organization services
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        organization_service = CertificateManagerOrganizationService(user_context)
        
        # Get user-specific and organization stats
        user_stats = await user_specific_service.get_user_certificate_stats()
        organization_stats = await organization_service.get_organization_stats()
        
        # Combine stats
        combined_stats = {
            "user_stats": user_stats,
            "organization_stats": organization_stats,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        return combined_stats
    except Exception as e:
        logger.error(f"Failed to get certificate stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get certificate stats")


@router.get("/certificates/search")
async def search_certificates(
    query: str, 
    status: str = None, 
    visibility: str = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Search certificates with filters."""
    try:
        # Initialize user-specific service
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Get user-specific certificates first
        user_certificates = await user_specific_service.get_user_certificates()
        
        # Apply search filters to user-accessible certificates
        filtered_certificates = []
        for cert in user_certificates:
            # Basic text search
            if query.lower() in cert.get("name", "").lower():
                # Apply status filter
                if status and cert.get("status") != status:
                    continue
                # Apply visibility filter
                if visibility and cert.get("visibility") != visibility:
                    continue
                filtered_certificates.append(cert)
        
        return {
            "certificates": filtered_certificates,
            "count": len(filtered_certificates),
            "query": query,
            "filters": {"status": status, "visibility": visibility},
            "user_id": getattr(user_context, 'user_id', None)
        }
    except Exception as e:
        logger.error(f"Failed to search certificates: {e}")
        raise HTTPException(status_code=500, detail="Failed to search certificates")


@router.post("/certificates/{certificate_id}/export")
async def export_certificate(
    certificate_id: str, 
    format: str = "html", 
    template: str = "default",
    user_context: UserContext = Depends(get_current_user)
):
    """Export certificate in specified format."""
    try:
        # Initialize user-specific service to check access
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Check if user can export this certificate
        if not user_specific_service.can_export_certificate(certificate_id):
            raise HTTPException(status_code=403, detail="Access denied to export this certificate")
        
        return await export_service.export_certificate(certificate_id, format, template)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export certificate {certificate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export certificate")


@router.get("/export/formats")
async def get_export_formats(user_context: UserContext = Depends(get_current_user)):
    """Get available export formats."""
    try:
        return await export_service.get_available_formats()
    except Exception as e:
        logger.error(f"Failed to get export formats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get export formats")


@router.get("/templates")
async def get_templates(user_context: UserContext = Depends(get_current_user)):
    """Get all available templates."""
    try:
        # Initialize user-specific service
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Return user-specific templates
        user_templates = await user_specific_service.get_user_templates()
        return {
            "templates": user_templates,
            "count": len(user_templates),
            "user_id": getattr(user_context, 'user_id', None),
            "organization_id": getattr(user_context, 'organization_id', None)
        }
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get specific template by ID."""
    try:
        # Initialize user-specific service
        user_specific_service = CertificateManagerUserSpecificService(user_context)
        
        # Get user templates to check access
        user_templates = await user_specific_service.get_user_templates()
        template_ids = [t["id"] for t in user_templates]
        
        # Check if user has access to this template
        if template_id not in template_ids:
            raise HTTPException(status_code=403, detail="Access denied to this template")
        
        template = await template_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template") 