"""
Certificate Manager Module

A comprehensive digital certificate system for AASX Digital Twin Analytics.
Automatically generates, maintains, and exports verifiable digital certificates
for every processed AASX sample.

Author: AASX Digital Twin Analytics Framework
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_root = Path(__file__).parent.parent
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

from .core.certificate_manager import CertificateManager
from .models.certificate import Certificate, CertificateStatus, CertificateVisibility, RetentionPolicy
from .models.certificate_version import CertificateVersion
from .models.certificate_event import CertificateEvent, EventType, EventStatus
from .models.certificate_export import CertificateExport, ExportFormat, ExportStatus

__version__ = "1.0.0"
__author__ = "AASX Digital Twin Analytics Framework"

# Main certificate manager instance
certificate_manager = CertificateManager()

def get_certificate_manager() -> CertificateManager:
    """Get the main certificate manager instance."""
    return certificate_manager

def create_certificate(twin_id: str, **kwargs) -> Certificate:
    """Create a new certificate for a digital twin."""
    return certificate_manager.create_certificate(twin_id, **kwargs)

def get_certificate(certificate_id: str) -> Certificate:
    """Get a certificate by ID."""
    return certificate_manager.get_certificate(certificate_id)

def update_certificate(certificate_id: str, **kwargs) -> Certificate:
    """Update a certificate."""
    return certificate_manager.update_certificate(certificate_id, **kwargs)

def delete_certificate(certificate_id: str) -> bool:
    """Delete a certificate."""
    return certificate_manager.delete_certificate(certificate_id)

def list_certificates(**filters) -> list[Certificate]:
    """List certificates with optional filters."""
    return certificate_manager.list_certificates(**filters)

__all__ = [
    'CertificateManager',
    'Certificate',
    'CertificateStatus',
    'CertificateVisibility',
    'RetentionPolicy',
    'CertificateVersion', 
    'CertificateEvent',
    'EventType',
    'EventStatus',
    'CertificateExport',
    'ExportFormat',
    'ExportStatus',
    'certificate_manager',
    'get_certificate_manager',
    'create_certificate',
    'get_certificate',
    'update_certificate',
    'delete_certificate',
    'list_certificates'
] 