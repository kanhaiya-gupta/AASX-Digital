"""
Certificate Manager Repositories Package

This package provides database access layer for the Certificate Manager module.
It includes repositories for all three main tables: certificates_registry, 
certificates_versions, and certificates_metrics.
"""

from .certificates_registry_repository import CertificatesRegistryRepository
from .certificates_versions_repository import CertificatesVersionsRepository
from .certificates_metrics_repository import CertificatesMetricsRepository

__all__ = [
    "CertificatesRegistryRepository",
    "CertificatesVersionsRepository", 
    "CertificatesMetricsRepository"
]

__version__ = "1.0.0"
__author__ = "Certificate Manager Team"
__description__ = "Database access layer for Certificate Manager module"
