"""
Data Models for Cross-Module Governance

This module defines the core data structures used by the cross-module
governance layer for tracking data lineage, ensuring compliance,
monitoring quality, and enforcing governance policies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4


class ComplianceStatus(str, Enum):
    """Status of compliance checks."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    ERROR = "error"
    UNKNOWN = "unknown"


class QualityStatus(str, Enum):
    """Status of data quality checks."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class PolicySeverity(str, Enum):
    """Severity levels for policy violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LineageType(str, Enum):
    """Types of data lineage relationships."""
    DATA_FLOW = "data_flow"
    TRANSFORMATION = "transformation"
    DERIVATION = "derivation"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"
    ENRICHMENT = "enrichment"


@dataclass
class DataLineage:
    """Represents data lineage across module boundaries."""
    
    lineage_id: UUID = field(default_factory=uuid4)
    source_module: str = ""
    target_module: str = ""
    source_data_id: str = ""
    target_data_id: str = ""
    lineage_type: LineageType = LineageType.DATA_FLOW
    transformation_details: Dict[str, Any] = field(default_factory=dict)
    data_schema: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    compliance_status: ComplianceStatus = ComplianceStatus.UNKNOWN
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "lineage_id": str(self.lineage_id),
            "source_module": self.source_module,
            "target_module": self.target_module,
            "source_data_id": self.source_data_id,
            "target_data_id": self.target_data_id,
            "lineage_type": self.lineage_type.value,
            "transformation_details": self.transformation_details,
            "data_schema": self.data_schema,
            "quality_metrics": self.quality_metrics,
            "compliance_status": self.compliance_status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ComplianceRule:
    """Represents a compliance rule for cross-module governance."""
    
    rule_id: UUID = field(default_factory=uuid4)
    rule_name: str = ""
    rule_description: str = ""
    rule_type: str = ""  # data_privacy, data_quality, business_rules, etc.
    applicable_modules: List[str] = field(default_factory=list)
    rule_conditions: Dict[str, Any] = field(default_factory=dict)
    rule_actions: List[str] = field(default_factory=list)
    severity: PolicySeverity = PolicySeverity.MEDIUM
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "rule_id": str(self.rule_id),
            "rule_name": self.rule_name,
            "rule_description": self.rule_description,
            "rule_type": self.rule_type,
            "applicable_modules": self.applicable_modules,
            "rule_conditions": self.rule_conditions,
            "rule_actions": self.rule_actions,
            "severity": self.severity.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class QualityMetric:
    """Represents a data quality metric."""
    
    metric_id: UUID = field(default_factory=uuid4)
    metric_name: str = ""
    metric_description: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    target_value: Optional[float] = None
    quality_status: QualityStatus = QualityStatus.UNKNOWN
    module_name: str = ""
    data_id: str = ""
    measured_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metric_id": str(self.metric_id),
            "metric_name": self.metric_name,
            "metric_description": self.metric_description,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max,
            "target_value": self.target_value,
            "quality_status": self.quality_status.value,
            "module_name": self.module_name,
            "data_id": self.data_id,
            "measured_at": self.measured_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class GovernancePolicy:
    """Represents a governance policy for cross-module operations."""
    
    policy_id: UUID = field(default_factory=uuid4)
    policy_name: str = ""
    policy_description: str = ""
    policy_type: str = ""  # data_governance, access_control, audit, etc.
    applicable_modules: List[str] = field(default_factory=list)
    policy_rules: List[ComplianceRule] = field(default_factory=list)
    enforcement_level: str = "strict"  # strict, advisory, warning
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "policy_id": str(self.policy_id),
            "policy_name": self.policy_name,
            "policy_description": self.policy_description,
            "policy_type": self.policy_type,
            "applicable_modules": self.applicable_modules,
            "policy_rules": [rule.to_dict() for rule in self.policy_rules],
            "enforcement_level": self.enforcement_level,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class PolicyViolation:
    """Represents a violation of a governance policy."""
    
    violation_id: UUID = field(default_factory=uuid4)
    policy_id: UUID = field(default_factory=uuid4)
    rule_id: UUID = field(default_factory=uuid4)
    module_name: str = ""
    data_id: str = ""
    violation_type: str = ""
    violation_description: str = ""
    severity: PolicySeverity = PolicySeverity.MEDIUM
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    is_resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "violation_id": str(self.violation_id),
            "policy_id": str(self.policy_id),
            "rule_id": str(self.rule_id),
            "module_name": self.module_name,
            "data_id": self.data_id,
            "violation_type": self.violation_type,
            "violation_description": self.violation_description,
            "severity": self.severity.value,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
            "is_resolved": self.is_resolved,
            "metadata": self.metadata
        }
