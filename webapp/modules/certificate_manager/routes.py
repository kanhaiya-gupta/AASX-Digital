"""
Certificate Manager Routes
FastAPI router for digital certificate management functionality.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os

# Create router
router = APIRouter(prefix="/certificates", tags=["certificates"])

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Pydantic models
class CertificateCreate(BaseModel):
    name: str
    type: str
    issuer: str
    digitalTwinId: str
    expiryDate: str
    description: Optional[str] = None

class CertificateResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    issuedDate: str
    expiryDate: str
    issuer: str
    digitalTwinId: str
    description: Optional[str] = None

# Mock data storage (replace with database)
CERTIFICATES_DB = [
    {
        "id": "cert-001",
        "name": "Quality Certificate - Additive Manufacturing",
        "type": "quality_certificate",
        "status": "active",
        "issuedDate": "2024-01-15",
        "expiryDate": "2025-01-15",
        "issuer": "QI Authority",
        "digitalTwinId": "dt-001",
        "description": "Quality certification for additive manufacturing processes"
    },
    {
        "id": "cert-002",
        "name": "Safety Certificate - Hydrogen Station",
        "type": "safety_certificate",
        "status": "active",
        "issuedDate": "2024-02-20",
        "expiryDate": "2025-02-20",
        "issuer": "Safety Authority",
        "digitalTwinId": "dt-002",
        "description": "Safety certification for hydrogen filling station operations"
    }
]

@router.get("/", response_class=HTMLResponse)
async def certificate_dashboard(request: Request):
    """Certificate management dashboard"""
    return templates.TemplateResponse(
        "certificate_manager/index.html",
        {
            "request": request,
            "title": "Certificate Manager - QI Digital Platform",
            "certificates": CERTIFICATES_DB
        }
    )

@router.get("/api/certificates", response_model=List[CertificateResponse])
async def get_certificates():
    """Get all certificates"""
    return CERTIFICATES_DB

@router.post("/api/certificates", response_model=CertificateResponse)
async def create_certificate(certificate: CertificateCreate):
    """Create a new certificate"""
    new_certificate = {
        "id": f"cert-{int(datetime.now().timestamp())}",
        "name": certificate.name,
        "type": certificate.type,
        "status": "active",
        "issuedDate": datetime.now().strftime("%Y-%m-%d"),
        "expiryDate": certificate.expiryDate,
        "issuer": certificate.issuer,
        "digitalTwinId": certificate.digitalTwinId,
        "description": certificate.description
    }
    
    CERTIFICATES_DB.append(new_certificate)
    return new_certificate

@router.get("/api/certificates/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(certificate_id: str):
    """Get certificate by ID"""
    for cert in CERTIFICATES_DB:
        if cert["id"] == certificate_id:
            return cert
    
    raise HTTPException(status_code=404, detail="Certificate not found")

@router.put("/api/certificates/{certificate_id}", response_model=CertificateResponse)
async def update_certificate(certificate_id: str, certificate: CertificateCreate):
    """Update certificate"""
    for i, cert in enumerate(CERTIFICATES_DB):
        if cert["id"] == certificate_id:
            updated_cert = {
                **cert,
                "name": certificate.name,
                "type": certificate.type,
                "issuer": certificate.issuer,
                "digitalTwinId": certificate.digitalTwinId,
                "expiryDate": certificate.expiryDate,
                "description": certificate.description
            }
            CERTIFICATES_DB[i] = updated_cert
            return updated_cert
    
    raise HTTPException(status_code=404, detail="Certificate not found")

@router.delete("/api/certificates/{certificate_id}")
async def delete_certificate(certificate_id: str):
    """Delete certificate"""
    for i, cert in enumerate(CERTIFICATES_DB):
        if cert["id"] == certificate_id:
            del CERTIFICATES_DB[i]
            return {"message": "Certificate deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Certificate not found")

@router.get("/api/certificates/twin/{twin_id}", response_model=List[CertificateResponse])
async def get_certificates_by_twin(twin_id: str):
    """Get certificates for a specific digital twin"""
    return [cert for cert in CERTIFICATES_DB if cert["digitalTwinId"] == twin_id]

@router.get("/api/certificates/type/{cert_type}", response_model=List[CertificateResponse])
async def get_certificates_by_type(cert_type: str):
    """Get certificates by type"""
    return [cert for cert in CERTIFICATES_DB if cert["type"] == cert_type] 