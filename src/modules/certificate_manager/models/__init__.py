"""
Certificate Manager Models Package
Data models and database schema for certificate management
"""

# ============================================================================
# MAIN MODELS
# ============================================================================

from .certificates_registry import (
    CertificateRegistry,
    ModuleStatusTracking,
    QualityAssessment,
    ComplianceTracking,
    SecurityMetrics,
    BusinessContext,
    ModuleSummaries,
    DigitalTrust
)

from .certificates_versions import (
    CertificateVersions,
    VersionMetadata,
    DataSnapshots,
    ChangeTracking,
    ApprovalWorkflow,
    DigitalVerification,
    BusinessIntelligence
)

from .certificates_metrics import (
    CertificateMetrics,
    PerformanceMetrics,
    UsageAnalytics,
    QualityAnalytics,
    BusinessMetrics,
    EnterpriseAnalytics,
    RealTimeMetrics
)

# ============================================================================
# ENUMS
# ============================================================================

from .certificates_registry import (
    ModuleStatus,
    CertificateStatus,
    QualityLevel,
    ComplianceStatus,
    SecurityLevel,
    ApprovalStatus
)

from .certificates_versions import (
    VersionType,
    ChangeImpact,
    ChangeCategory,
    ReviewStatus,
    PublicationStatus
)

from .certificates_metrics import (
    MetricCategory,
    MetricPriority,
    PerformanceTrend,
    MetricUnit,
    AlertLevel
)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main Models
    "CertificateRegistry",
    "CertificateVersion", 
    "CertificateMetrics",
    
    # Registry Components
    "ModuleStatusTracking",
    "QualityAssessment",
    "ComplianceTracking",
    "SecurityMetrics",
    "BusinessContext",
    "ModuleSummaries",
    "DigitalTrust",
    
    # Version Components
    "VersionMetadata",
    "DataSnapshots",
    "ChangeTracking",
    "ApprovalWorkflow",
    "DigitalVerification",
    "BusinessIntelligence",
    
    # Metrics Components
    "PerformanceMetrics",
    "UsageAnalytics",
    "QualityAnalytics",
    "BusinessMetrics",
    "EnterpriseAnalytics",
    "RealTimeMetrics",
    
    # Enums
    "ModuleStatus",
    "CertificateStatus",
    "QualityLevel",
    "ComplianceStatus",
    "SecurityLevel",
    "ApprovalStatus",
    "VersionType",
    "ChangeImpact",
    "ChangeCategory",
    "ReviewStatus",
    "PublicationStatus",
    "MetricCategory",
    "MetricPriority",
    "PerformanceTrend",
    "MetricUnit",
    "AlertLevel"
]

__version__ = "1.0.0"
__author__ = "Certificate Manager Team"
__description__ = "Data models and database schema for Certificate Manager module" 