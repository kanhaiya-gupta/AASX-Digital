"""
Certificate Manager Core Package

Core orchestration and business logic services for certificate management.
"""

from .certificate_manager import CertificateManager
from .certificate_updater import CertificateUpdater
from .progress_tracker import ProgressTracker
from .certificate_generator import CertificateGenerator
from .module_summary_collector import ModuleSummaryCollector
from .lineage_tracker import LineageTracker
from .completion_validator import CompletionValidator
from .business_intelligence import BusinessIntelligence

__all__ = [
    "CertificateManager",
    "CertificateUpdater", 
    "ProgressTracker",
    "CertificateGenerator",
    "ModuleSummaryCollector",
    "LineageTracker",
    "CompletionValidator",
    "BusinessIntelligence"
]

__version__ = "1.0.0"
__author__ = "Certificate Manager Team"
__description__ = "Core orchestration services for Certificate Manager module" 