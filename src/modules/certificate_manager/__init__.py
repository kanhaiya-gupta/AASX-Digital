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

# Main certificate manager instance - will be created when needed
certificate_manager = None

def get_certificate_manager(db_session=None) -> CertificateManager:
    """Get the main certificate manager instance."""
    global certificate_manager
    if certificate_manager is None and db_session is not None:
        certificate_manager = CertificateManager(db_session)
    elif certificate_manager is None:
        raise ValueError("Database session is required to initialize CertificateManager")
    return certificate_manager

def create_certificate(twin_id: str, db_session=None, **kwargs) -> Certificate:
    """Create a new certificate for a digital twin."""
    manager = get_certificate_manager(db_session)
    return manager.create_certificate(twin_id, **kwargs)

def get_certificate(certificate_id: str, db_session=None) -> Certificate:
    """Get a certificate by ID."""
    manager = get_certificate_manager(db_session)
    return manager.get_certificate(certificate_id)

def update_certificate(certificate_id: str, db_session=None, **kwargs) -> Certificate:
    """Update a certificate."""
    manager = get_certificate_manager(db_session)
    return manager.update_certificate(certificate_id, **kwargs)

def delete_certificate(certificate_id: str, db_session=None) -> bool:
    """Delete a certificate."""
    manager = get_certificate_manager(db_session)
    return manager.delete_certificate(certificate_id)

def list_certificates(db_session=None, **filters) -> list[Certificate]:
    """List certificates with optional filters."""
    manager = get_certificate_manager(db_session)
    return manager.list_certificates(**filters)

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