"""
Core System Models - World-Class Implementation
=============================================

Core system models with comprehensive business logic, validation,
and enterprise patterns for the AAS Data Modeling Engine.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
import re

from pydantic import Field, field_validator, model_validator

from .base_model import BaseModel, AuditInfo
from .enums import (
    SystemCategory, SystemType, SystemPriority, RegistryType, WorkflowSource,
    SecurityLevel, HealthStatus, BusinessConstants, ValidationRules, StatusMappings, EventType
)


class CoreSystemRegistry(BaseModel):
    """
    Core System Registry with world-class features.
    
    Features:
    - Comprehensive validation with business rules
    - Health status calculation and monitoring
    - Security level enforcement
    - Performance metrics tracking
    - Audit trail and compliance
    """
    
    # Required fields
    registry_id: str = Field(..., description="Unique registry identifier")
    system_name: str = Field(..., description="Name of the system")
    registry_name: str = Field(..., description="Name of the registry")
    
    # Optional fields with defaults
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp")
    
    # System classification
    system_category: Optional[str] = Field(default="infrastructure", description="System category")
    system_type: Optional[str] = Field(default="microservice", description="System type")
    system_priority: Optional[str] = Field(default="medium", description="System priority level")
    
    # Registry configuration
    registry_type: Optional[str] = Field(default="hybrid", description="Registry type")
    workflow_source: Optional[str] = Field(default="both", description="Workflow source type")
    
    # Security and compliance
    security_level: Optional[str] = Field(default="internal", description="Security classification level")
    compliance_standards: Optional[List[str]] = Field(default_factory=list, description="Compliance standards")
    
    # Performance and health
    health_score: Optional[float] = Field(default=100.0, description="System health score (0-100)")
    performance_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Performance metrics")
    
    # Business context
    organization_id: Optional[str] = Field(None, description="Owning organization ID")
    user_id: Optional[str] = Field(None, description="Owning user ID")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    
    # Metadata and configuration
    description: Optional[str] = Field(default="", description="System description")
    tags: Optional[List[str]] = Field(default_factory=list, description="System tags")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="System configuration")
    
    # Audit information
    audit_info: Optional[AuditInfo] = Field(None, description="Audit information")
    
    # Business rule validation
    @field_validator('system_name')
    @classmethod
    def validate_system_name(cls, v: str) -> str:
        """Validate system name according to business rules."""
        if not v or len(v.strip()) < 3:
            raise ValueError("System name must be at least 3 characters long")
        if len(v) > 100:
            raise ValueError("System name cannot exceed 100 characters")
        return v.strip()
    
    @field_validator('health_score')
    @classmethod
    def validate_health_score(cls, v: float) -> float:
        """Validate health score according to business rules."""
        if not (BusinessConstants.HEALTH_SCORE_MIN <= v <= BusinessConstants.HEALTH_SCORE_MAX):
            raise ValueError(f"Health score must be between {BusinessConstants.HEALTH_SCORE_MIN} and {BusinessConstants.HEALTH_SCORE_MAX}")
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags according to business rules."""
        if len(v) > ValidationRules.MAX_TAGS_PER_ENTITY:
            raise ValueError(f"Maximum {ValidationRules.MAX_TAGS_PER_ENTITY} tags allowed")
        
        # Validate individual tag lengths
        for tag in v:
            if len(tag) > ValidationRules.TAG_MAX_LENGTH:
                raise ValueError(f"Tag '{tag}' exceeds maximum length of {ValidationRules.TAG_MAX_LENGTH}")
        
        return v
    
    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate business rules after model creation."""
        self._validate_business_rule_system_priority()
        self._validate_business_rule_security_compliance()
        self._validate_business_rule_registry_configuration()
        return self
    
    def _validate_business_rule_system_priority(self):
        """Validate system priority business rules."""
        if self.system_priority == SystemPriority.CRITICAL.value:
            if not self.compliance_standards:
                raise ValueError("Critical systems must have compliance standards defined")
            if self.security_level not in [SecurityLevel.CONFIDENTIAL.value, SecurityLevel.SECRET.value, SecurityLevel.TOP_SECRET.value]:
                raise ValueError("Critical systems must have high security level")
    
    def _validate_business_rule_security_compliance(self):
        """Validate security and compliance business rules."""
        if self.security_level == SecurityLevel.TOP_SECRET.value:
            if not self.audit_info or not self.audit_info.created_by:
                raise ValueError("Top secret systems must have audit trail with creator")
    
    def _validate_business_rule_registry_configuration(self):
        """Validate registry configuration business rules."""
        if self.registry_type == RegistryType.FEDERATED.value:
            if not self.organization_id:
                raise ValueError("Federated registries must have organization ID")
    
    # Business Logic Methods
    
    def calculate_health_status(self) -> HealthStatus:
        """Calculate health status based on health score."""
        for score_range, status in StatusMappings.HEALTH_STATUS_MAPPING.items():
            if score_range[0] <= self.health_score <= score_range[1]:
                return status
        return HealthStatus.UNKNOWN
    
    def update_health_score(self, new_score: float, reason: str = None):
        """Update health score with business rule validation."""
        if not (BusinessConstants.HEALTH_SCORE_MIN <= new_score <= BusinessConstants.HEALTH_SCORE_MAX):
            raise ValueError(f"Health score must be between {BusinessConstants.HEALTH_SCORE_MIN} and {BusinessConstants.HEALTH_SCORE_MAX}")
        
        old_score = self.health_score
        self.health_score = new_score
        
        # Update audit info
        if self.audit_info:
            self.audit_info.change_reason = f"Health score updated from {old_score} to {new_score}. Reason: {reason}"
        
        # Notify observers of health change
        self._notify_observers(EventType.SYSTEM_HEALTH_CHANGED, old_score=old_score, new_score=new_score, reason=reason)
    
    def add_compliance_standard(self, standard: str):
        """Add compliance standard with validation."""
        if standard not in self.compliance_standards:
            if len(self.compliance_standards) >= 10:  # Business rule: max 10 standards
                raise ValueError("Maximum 10 compliance standards allowed")
            self.compliance_standards.append(standard)
            
            # Update audit info
            if self.audit_info:
                self.audit_info.change_reason = f"Added compliance standard: {standard}"
    
    def remove_compliance_standard(self, standard: str):
        """Remove compliance standard with validation."""
        if standard in self.compliance_standards:
            if self.system_priority == SystemPriority.CRITICAL.value and len(self.compliance_standards) <= 1:
                raise ValueError("Critical systems must have at least one compliance standard")
            
            self.compliance_standards.remove(standard)
            
            # Update audit info
            if self.audit_info:
                self.audit_info.change_reason = f"Removed compliance standard: {standard}"
    
    def add_tag(self, tag: str):
        """Add tag with business rule validation."""
        if tag not in self.tags:
            if len(self.tags) >= ValidationRules.MAX_TAGS_PER_ENTITY:
                raise ValueError(f"Maximum {ValidationRules.MAX_TAGS_PER_ENTITY} tags allowed")
            if len(tag) > ValidationRules.TAG_MAX_LENGTH:
                raise ValueError(f"Tag exceeds maximum length of {ValidationRules.TAG_MAX_LENGTH}")
            
            self.tags.append(tag)
            
            # Update audit info
            if self.audit_info:
                self.audit_info.change_reason = f"Added tag: {tag}"
    
    def remove_tag(self, tag: str):
        """Remove tag."""
        if tag in self.tags:
            self.tags.remove(tag)
            
            # Update audit info
            if self.audit_info:
                self.audit_info.change_reason = f"Removed tag: {tag}"
    
    def update_configuration(self, key: str, value: Any):
        """Update configuration with validation."""
        # Business rule: configuration keys must be alphanumeric with underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', key):
            raise ValueError("Configuration keys must be alphanumeric with underscores only")
        
        self.configuration[key] = value
        
        # Update audit info
        if self.audit_info:
            self.audit_info.change_reason = f"Updated configuration: {key} = {value}"
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary with lazy loading."""
        return self.lazy_load_property(
            'performance_summary',
            lambda: self._compute_performance_summary()
        )
    
    def _compute_performance_summary(self) -> Dict[str, Any]:
        """Compute performance summary."""
        return {
            'health_score': self.health_score,
            'health_status': self.calculate_health_status().value,
            'metrics_count': len(self.performance_metrics),
            'last_updated': self.updated_at,
            'compliance_score': len(self.compliance_standards) * 10,  # Simple scoring
            'security_level': self.security_level
        }
    
    def is_critical_system(self) -> bool:
        """Check if this is a critical system."""
        return self.system_priority == SystemPriority.CRITICAL.value
    
    def requires_audit_trail(self) -> bool:
        """Check if audit trail is required."""
        return (self.security_level in [SecurityLevel.SECRET.value, SecurityLevel.TOP_SECRET.value] or
                self.system_priority == SystemPriority.CRITICAL.value)
    
    def get_security_requirements(self) -> List[str]:
        """Get security requirements based on classification."""
        requirements = []
        
        if self.security_level == SecurityLevel.TOP_SECRET.value:
            requirements.extend([
                "Full audit trail required",
                "Encryption at rest and in transit",
                "Multi-factor authentication",
                "Regular security assessments"
            ])
        elif self.security_level == SecurityLevel.SECRET.value:
            requirements.extend([
                "Audit trail required",
                "Encryption at rest",
                "Strong authentication"
            ])
        
        if self.system_priority == SystemPriority.CRITICAL.value:
            requirements.extend([
                "24/7 monitoring",
                "Automated alerting",
                "Disaster recovery plan",
                "Regular compliance reviews"
            ])
        
        return requirements


class CoreSystemMetrics(BaseModel):
    """
    Core System Metrics with world-class features.
    
    Features:
    - Comprehensive metric collection and validation
    - Performance analysis and trending
    - Anomaly detection
    - Metric aggregation and reporting
    """
    
    # Required fields
    metric_id: Optional[str] = Field(None, description="Unique metric identifier")
    registry_id: str = Field(..., description="Associated registry ID")
    metric_type: str = Field(..., description="Type of metric")
    
    # Optional fields with defaults
    metric_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Metric timestamp")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp")
    
    # Metric data
    metric_value: Optional[Union[int, float, str]] = Field(None, description="Metric value")
    metric_unit: Optional[str] = Field(None, description="Unit of measurement")
    metric_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metric metadata")
    
    # Performance context
    performance_context: Optional[str] = Field(None, description="Performance context (e.g., 'normal', 'peak', 'off-peak')")
    threshold_values: Optional[Dict[str, Union[int, float]]] = Field(default_factory=dict, description="Threshold values")
    alert_levels: Optional[Dict[str, str]] = Field(default_factory=dict, description="Alert level definitions")
    
    # Business context
    user_id: Optional[str] = Field(None, description="User who generated the metric")
    organization_id: Optional[str] = Field(None, description="Organization context")
    
    # Audit information
    audit_info: Optional[AuditInfo] = Field(None, description="Audit information")
    
    # Business rule validation
    @field_validator('metric_type')
    @classmethod
    def validate_metric_type(cls, v: str) -> str:
        """Validate metric type according to business rules."""
        valid_types = ['performance', 'security', 'availability', 'usage', 'business', 'technical', 'user', 'system']
        if v not in valid_types:
            raise ValueError(f"Invalid metric type. Must be one of: {', '.join(valid_types)}")
        return v
    
    @field_validator('metric_value')
    @classmethod
    def validate_metric_value(cls, v: Any) -> Any:
        """Validate metric value according to business rules."""
        if v is not None:
            if isinstance(v, (int, float)) and v < 0:
                raise ValueError("Metric value cannot be negative")
            if isinstance(v, str) and len(v) > 1000:
                raise ValueError("String metric value cannot exceed 1000 characters")
        return v
    
    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate business rules after model creation."""
        self._validate_business_rule_threshold_configuration()
        self._validate_business_rule_metadata_size()
        return self
    
    def _validate_business_rule_threshold_configuration(self):
        """Validate threshold configuration business rules."""
        if self.threshold_values and self.alert_levels:
            # Ensure alert levels have corresponding thresholds
            for alert_level in self.alert_levels.keys():
                if alert_level not in self.threshold_values:
                    raise ValueError(f"Alert level '{alert_level}' must have corresponding threshold value")
    
    def _validate_business_rule_metadata_size(self):
        """Validate metadata size business rules."""
        if self.metric_metadata:
            metadata_size = len(str(self.metric_metadata))
            if metadata_size > 5000:  # 5KB limit
                raise ValueError("Metric metadata size exceeds 5KB limit")
    
    # Business Logic Methods
    
    def is_above_threshold(self, threshold_name: str) -> bool:
        """Check if metric value is above a specific threshold."""
        if not self.threshold_values or threshold_name not in self.threshold_values:
            return False
        
        threshold = self.threshold_values[threshold_name]
        if isinstance(self.metric_value, (int, float)) and isinstance(threshold, (int, float)):
            return self.metric_value > threshold
        return False
    
    def is_below_threshold(self, threshold_name: str) -> bool:
        """Check if metric value is below a specific threshold."""
        if not self.threshold_values or threshold_name not in self.threshold_values:
            return False
        
        threshold = self.threshold_values[threshold_name]
        if isinstance(self.metric_value, (int, float)) and isinstance(threshold, (int, float)):
            return self.metric_value < threshold
        return False
    
    def get_alert_level(self) -> Optional[str]:
        """Get current alert level based on metric value and thresholds."""
        if not self.threshold_values or not self.alert_levels:
            return None
        
        for alert_level, threshold_name in self.alert_levels.items():
            if threshold_name in self.threshold_values:
                threshold = self.threshold_values[threshold_name]
                if isinstance(self.metric_value, (int, float)) and isinstance(threshold, (int, float)):
                    if self.metric_value > threshold:
                        return alert_level
        
        return None
    
    def add_threshold(self, threshold_name: str, value: Union[int, float]):
        """Add threshold with validation."""
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Threshold value must be a non-negative number")
        
        self.threshold_values[threshold_name] = value
        
        # Update audit info
        if self.audit_info:
            self.audit_info.change_reason = f"Added threshold: {threshold_name} = {value}"
    
    def remove_threshold(self, threshold_name: str):
        """Remove threshold."""
        if threshold_name in self.threshold_values:
            del self.threshold_values[threshold_name]
            
            # Update audit info
            if self.audit_info:
                self.audit_info.change_reason = f"Removed threshold: {threshold_name}"
    
    def add_alert_level(self, alert_level: str, threshold_name: str):
        """Add alert level with validation."""
        if threshold_name not in self.threshold_values:
            raise ValueError(f"Threshold '{threshold_name}' must exist before adding alert level")
        
        self.alert_levels[alert_level] = threshold_name
        
        # Update audit info
        if self.audit_info:
            self.audit_info.change_reason = f"Added alert level: {alert_level} -> {threshold_name}"
    
    def get_metric_summary(self) -> Dict[str, Any]:
        """Get metric summary with lazy loading."""
        return self.lazy_load_property(
            'metric_summary',
            lambda: self._compute_metric_summary()
        )
    
    def _compute_metric_summary(self) -> Dict[str, Any]:
        """Compute metric summary."""
        return {
            'metric_id': self.metric_id,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'timestamp': self.metric_timestamp,
            'alert_level': self.get_alert_level(),
            'thresholds_count': len(self.threshold_values),
            'alert_levels_count': len(self.alert_levels),
            'metadata_keys': list(self.metric_metadata.keys()) if self.metric_metadata else []
        }
    
    def is_anomaly(self, baseline_value: Union[int, float], tolerance_percent: float = 10.0) -> bool:
        """Check if metric value is an anomaly compared to baseline."""
        if not isinstance(self.metric_value, (int, float)) or not isinstance(baseline_value, (int, float)):
            return False
        
        if baseline_value == 0:
            return False
        
        deviation = abs(self.metric_value - baseline_value) / abs(baseline_value) * 100
        return deviation > tolerance_percent
    
    def get_trend_direction(self, previous_value: Union[int, float]) -> str:
        """Get trend direction compared to previous value."""
        if not isinstance(self.metric_value, (int, float)) or not isinstance(previous_value, (int, float)):
            return "unknown"
        
        if self.metric_value > previous_value:
            return "increasing"
        elif self.metric_value < previous_value:
            return "decreasing"
        else:
            return "stable"


# Export the models
__all__ = [
    'CoreSystemRegistry', 'CoreSystemMetrics'
]
