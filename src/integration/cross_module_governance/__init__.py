"""
Cross-Module Governance Package

This package provides governance services for ensuring data integrity,
compliance, and quality across all external modules within the AAS
Data Modeling Engine.

The cross-module governance layer ensures:
- Data lineage tracking across module boundaries
- Compliance monitoring and enforcement
- Data quality monitoring across modules
- Governance policy enforcement
"""

from .cross_module_lineage import CrossModuleLineageService
from .module_compliance import ModuleComplianceService
from .data_quality_monitor import DataQualityMonitorService
from .governance_policy_enforcer import GovernancePolicyEnforcerService
from .models import (
    DataLineage,
    ComplianceRule,
    QualityMetric,
    GovernancePolicy,
    ComplianceStatus,
    QualityStatus,
    PolicySeverity,
    LineageType,
    PolicyViolation
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    "CrossModuleLineageService",
    "ModuleComplianceService", 
    "DataQualityMonitorService",
    "GovernancePolicyEnforcerService",
    "DataLineage",
    "ComplianceRule",
    "QualityMetric",
    "GovernancePolicy",
    "ComplianceStatus",
    "QualityStatus",
    "PolicySeverity",
    "LineageType",
    "PolicyViolation"
]
