"""
Completion Validator - Certificate Completion Validation Service

Handles certificate completion validation, quality checks, and
final approval workflows. Validates that all required modules
have completed successfully and meet quality standards before
marking certificates as complete.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    CertificateStatus,
    QualityLevel,
    ComplianceStatus,
    SecurityLevel
)
from ..models.certificates_metrics import CertificateMetrics, MetricCategory
from ..services.certificates_registry_service import CertificatesRegistryService
from ..services.certificates_metrics_service import CertificatesMetricsService

logger = logging.getLogger(__name__)


class ValidationStatus(str, Enum):
    """Certificate validation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"


class ValidationRule(str, Enum):
    """Validation rule types"""
    MODULE_COMPLETION = "module_completion"
    QUALITY_THRESHOLD = "quality_threshold"
    COMPLIANCE_CHECK = "compliance_check"
    SECURITY_VALIDATION = "security_validation"
    DATA_FRESHNESS = "data_freshness"
    INTEGRITY_CHECK = "integrity_check"


class ValidationSeverity(str, Enum):
    """Validation rule severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CompletionValidator:
    """
    Certificate completion validation service
    
    Handles:
    - Module completion validation
    - Quality threshold checks
    - Compliance and security validation
    - Data integrity verification
    - Final approval workflows
    - Validation rule management
    """
    
    def __init__(
        self,
        registry_service: CertificatesRegistryService,
        metrics_service: CertificatesMetricsService
    ):
        """Initialize the completion validator"""
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Validation status tracking
        self.validation_status: Dict[str, ValidationStatus] = {}
        
        # Validation rules and thresholds
        self.validation_rules = self._initialize_validation_rules()
        
        # Validation locks per certificate
        self.validation_locks: Dict[str, asyncio.Lock] = {}
        
        # Validation history
        self.validation_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Approval workflows
        self.approval_workflows: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Completion Validator initialized successfully")
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules and thresholds"""
        return {
            ValidationRule.MODULE_COMPLETION: {
                "severity": ValidationSeverity.CRITICAL,
                "description": "All required modules must be completed successfully",
                "threshold": 100.0,  # 100% module completion required
                "enabled": True
            },
            ValidationRule.QUALITY_THRESHOLD: {
                "severity": ValidationSeverity.HIGH,
                "description": "Overall quality score must meet minimum threshold",
                "threshold": 80.0,  # 80% quality score required
                "enabled": True
            },
            ValidationRule.COMPLIANCE_CHECK: {
                "severity": ValidationSeverity.HIGH,
                "description": "Certificate must be compliant with regulations",
                "threshold": ComplianceStatus.COMPLIANT,
                "enabled": True
            },
            ValidationRule.SECURITY_VALIDATION: {
                "severity": ValidationSeverity.HIGH,
                "description": "Security score must meet minimum threshold",
                "threshold": 70.0,  # 70% security score required
                "enabled": True
            },
            ValidationRule.DATA_FRESHNESS: {
                "severity": ValidationSeverity.MEDIUM,
                "description": "Data must be fresh (not older than 24 hours)",
                "threshold": 24,  # 24 hours maximum age
                "enabled": True
            },
            ValidationRule.INTEGRITY_CHECK: {
                "severity": ValidationSeverity.CRITICAL,
                "description": "Data integrity must be verified",
                "threshold": True,  # Must pass integrity check
                "enabled": True
            }
        }
    
    async def start_validation(
        self,
        certificate_id: str,
        auto_approve: bool = False
    ) -> bool:
        """
        Start completion validation for a certificate
        
        This is the main entry point for certificate validation.
        Runs all validation rules and determines if the certificate
        meets completion requirements.
        """
        try:
            # Acquire validation lock for this certificate
            if certificate_id not in self.validation_locks:
                self.validation_locks[certificate_id] = asyncio.Lock()
            
            async with self.validation_locks[certificate_id]:
                logger.info(f"Starting completion validation for certificate: {certificate_id}")
                
                # Check if validation is already in progress
                if (certificate_id in self.validation_status and 
                    self.validation_status[certificate_id] == ValidationStatus.IN_PROGRESS):
                    logger.info(f"Validation already in progress for certificate: {certificate_id}")
                    return True
                
                # Initialize validation status
                self.validation_status[certificate_id] = ValidationStatus.IN_PROGRESS
                
                # Get certificate details
                certificate = await self.registry_service.get_certificate(certificate_id)
                if not certificate:
                    logger.error(f"Certificate not found: {certificate_id}")
                    self.validation_status[certificate_id] = ValidationStatus.FAILED
                    return False
                
                # Run all validation rules
                validation_results = await self._run_validation_rules(certificate)
                
                # Analyze validation results
                validation_summary = await self._analyze_validation_results(validation_results)
                
                # Determine final validation status
                if validation_summary["all_passed"]:
                    if auto_approve:
                        self.validation_status[certificate_id] = ValidationStatus.APPROVED
                        await self._auto_approve_certificate(certificate_id)
                    else:
                        self.validation_status[certificate_id] = ValidationStatus.VALIDATED
                        await self._initiate_approval_workflow(certificate_id, validation_summary)
                else:
                    self.validation_status[certificate_id] = ValidationStatus.FAILED
                
                # Record validation history
                await self._record_validation_history(certificate_id, validation_results, validation_summary)
                
                logger.info(f"Completion validation completed for certificate: {certificate_id} - Status: {self.validation_status[certificate_id].value}")
                return True
                
        except Exception as e:
            logger.error(f"Error starting completion validation: {e}")
            self.validation_status[certificate_id] = ValidationStatus.FAILED
            return False
    
    async def _run_validation_rules(self, certificate: CertificateRegistry) -> Dict[str, Dict[str, Any]]:
        """Run all validation rules against a certificate"""
        try:
            validation_results = {}
            
            # Run each validation rule
            for rule_name, rule_config in self.validation_rules.items():
                if not rule_config["enabled"]:
                    continue
                
                logger.info(f"Running validation rule: {rule_name.value}")
                
                if rule_name == ValidationRule.MODULE_COMPLETION:
                    result = await self._validate_module_completion(certificate, rule_config)
                elif rule_name == ValidationRule.QUALITY_THRESHOLD:
                    result = await self._validate_quality_threshold(certificate, rule_config)
                elif rule_name == ValidationRule.COMPLIANCE_CHECK:
                    result = await self._validate_compliance_check(certificate, rule_config)
                elif rule_name == ValidationRule.SECURITY_VALIDATION:
                    result = await self._validate_security_validation(certificate, rule_config)
                elif rule_name == ValidationRule.DATA_FRESHNESS:
                    result = await self._validate_data_freshness(certificate, rule_config)
                elif rule_name == ValidationRule.INTEGRITY_CHECK:
                    result = await self._validate_integrity_check(certificate, rule_config)
                else:
                    result = {
                        "passed": False,
                        "message": f"Unknown validation rule: {rule_name.value}",
                        "severity": ValidationSeverity.LOW
                    }
                
                validation_results[rule_name.value] = result
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error running validation rules: {e}")
            return {}
    
    async def _validate_module_completion(
        self,
        certificate: CertificateRegistry,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that all modules are completed"""
        try:
            module_status = certificate.module_status
            
            # Check if all modules are active (completed)
            required_modules = [
                module_status.aasx_module,
                module_status.twin_registry,
                module_status.ai_rag,
                module_status.kg_neo4j,
                module_status.physics_modeling,
                module_status.federated_learning,
                module_status.data_governance
            ]
            
            completed_modules = sum(1 for status in required_modules if status == ModuleStatus.ACTIVE)
            total_modules = len(required_modules)
            completion_percentage = (completed_modules / total_modules) * 100
            
            threshold = rule_config["threshold"]
            passed = completion_percentage >= threshold
            
            return {
                "passed": passed,
                "message": f"Module completion: {completed_modules}/{total_modules} ({completion_percentage:.1f}%)",
                "severity": rule_config["severity"],
                "details": {
                    "completed_modules": completed_modules,
                    "total_modules": total_modules,
                    "completion_percentage": completion_percentage,
                    "threshold": threshold,
                    "module_statuses": {
                        "aasx_module": module_status.aasx_module.value,
                        "twin_registry": module_status.twin_registry.value,
                        "ai_rag": module_status.ai_rag.value,
                        "kg_neo4j": module_status.kg_neo4j.value,
                        "physics_modeling": module_status.physics_modeling.value,
                        "federated_learning": module_status.federated_learning.value,
                        "data_governance": module_status.data_governance.value
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating module completion: {e}")
            return {
                "passed": False,
                "message": f"Error validating module completion: {e}",
                "severity": rule_config["severity"]
            }
    
    async def _validate_quality_threshold(
        self,
        certificate: CertificateRegistry,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate quality threshold requirements"""
        try:
            quality_assessment = certificate.quality_assessment
            overall_quality_score = quality_assessment.overall_quality_score
            
            threshold = rule_config["threshold"]
            passed = overall_quality_score >= threshold
            
            return {
                "passed": passed,
                "message": f"Quality score: {overall_quality_score:.1f}% (threshold: {threshold}%)",
                "severity": rule_config["severity"],
                "details": {
                    "overall_quality_score": overall_quality_score,
                    "threshold": threshold,
                    "quality_level": quality_assessment.quality_level.value,
                    "data_completeness_score": quality_assessment.data_completeness_score,
                    "validation_rate": quality_assessment.validation_rate,
                    "coverage_score": quality_assessment.coverage_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating quality threshold: {e}")
            return {
                "passed": False,
                "message": f"Error validating quality threshold: {e}",
                "severity": rule_config["severity"]
            }
    
    async def _validate_compliance_check(
        self,
        certificate: CertificateRegistry,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate compliance requirements"""
        try:
            compliance_tracking = certificate.compliance_tracking
            compliance_status = compliance_tracking.compliance_status
            
            threshold = rule_config["threshold"]
            passed = compliance_status == threshold
            
            return {
                "passed": passed,
                "message": f"Compliance status: {compliance_status.value} (required: {threshold.value})",
                "severity": rule_config["severity"],
                "details": {
                    "compliance_status": compliance_status.value,
                    "compliance_score": compliance_tracking.compliance_score,
                    "regulatory_framework": compliance_tracking.regulatory_framework,
                    "last_audit": compliance_tracking.last_audit.isoformat() if compliance_tracking.last_audit else None,
                    "next_audit": compliance_tracking.next_audit.isoformat() if compliance_tracking.next_audit else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating compliance check: {e}")
            return {
                "passed": False,
                "message": f"Error validating compliance check: {e}",
                "severity": rule_config["severity"]
            }
    
    async def _validate_security_validation(
        self,
        certificate: CertificateRegistry,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate security requirements"""
        try:
            security_metrics = certificate.security_metrics
            security_score = security_metrics.security_score
            
            threshold = rule_config["threshold"]
            passed = security_score >= threshold
            
            return {
                "passed": passed,
                "message": f"Security score: {security_score:.1f}% (threshold: {threshold}%)",
                "severity": rule_config["severity"],
                "details": {
                    "security_score": security_score,
                    "threshold": threshold,
                    "security_level": security_metrics.security_level.value,
                    "threat_level": security_metrics.threat_level.value,
                    "security_events_count": len(security_metrics.security_events),
                    "last_assessment": security_metrics.last_security_assessment.isoformat() if security_metrics.last_security_assessment else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating security validation: {e}")
            return {
                "passed": False,
                "message": f"Error validating security validation: {e}",
                "severity": rule_config["severity"]
            }
    
    async def _validate_data_freshness(
        self,
        certificate: CertificateRegistry,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data freshness requirements"""
        try:
            # Get latest update time from certificate
            latest_update = certificate.updated_at
            current_time = datetime.utcnow()
            
            # Calculate age in hours
            age_hours = (current_time - latest_update).total_seconds() / 3600
            
            threshold = rule_config["threshold"]  # hours
            passed = age_hours <= threshold
            
            return {
                "passed": passed,
                "message": f"Data age: {age_hours:.1f} hours (threshold: {threshold} hours)",
                "severity": rule_config["severity"],
                "details": {
                    "data_age_hours": age_hours,
                    "threshold_hours": threshold,
                    "last_updated": latest_update.isoformat(),
                    "current_time": current_time.isoformat(),
                    "freshness_status": "fresh" if passed else "stale"
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating data freshness: {e}")
            return {
                "passed": False,
                "message": f"Error validating data freshness: {e}",
                "severity": rule_config["severity"]
            }
    
    async def _validate_integrity_check(
        self,
        certificate: CertificateRegistry,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data integrity requirements"""
        try:
            digital_trust = certificate.digital_trust
            
            # Check if digital signature exists
            has_signature = bool(digital_trust.digital_signature)
            has_hash = bool(digital_trust.hash_value)
            has_qr_code = bool(digital_trust.qr_code)
            
            # Basic integrity checks
            integrity_checks = [
                has_signature,
                has_hash,
                has_qr_code
            ]
            
            passed = all(integrity_checks)
            
            return {
                "passed": passed,
                "message": f"Integrity checks: {'PASSED' if passed else 'FAILED'}",
                "severity": rule_config["severity"],
                "details": {
                    "has_digital_signature": has_signature,
                    "has_hash_value": has_hash,
                    "has_qr_code": has_qr_code,
                    "integrity_score": sum(integrity_checks) / len(integrity_checks) * 100,
                    "signature_timestamp": digital_trust.signature_timestamp.isoformat() if digital_trust.signature_timestamp else None,
                    "certificate_authority": digital_trust.certificate_authority
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating integrity check: {e}")
            return {
                "passed": False,
                "message": f"Error validating integrity check: {e}",
                "severity": rule_config["severity"]
            }
    
    async def _analyze_validation_results(
        self,
        validation_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze validation results and generate summary"""
        try:
            total_rules = len(validation_results)
            passed_rules = sum(1 for result in validation_results.values() if result.get("passed", False))
            failed_rules = total_rules - passed_rules
            
            # Check for critical failures
            critical_failures = [
                rule_name for rule_name, result in validation_results.items()
                if (not result.get("passed", False) and 
                    result.get("severity") == ValidationSeverity.CRITICAL)
            ]
            
            # Check for high severity failures
            high_failures = [
                rule_name for rule_name, result in validation_results.items()
                if (not result.get("passed", False) and 
                    result.get("severity") == ValidationSeverity.HIGH)
            ]
            
            # Determine overall validation status
            all_passed = failed_rules == 0
            has_critical_failures = len(critical_failures) > 0
            has_high_failures = len(high_failures) > 0
            
            # Calculate validation score
            validation_score = (passed_rules / total_rules) * 100 if total_rules > 0 else 0
            
            summary = {
                "total_rules": total_rules,
                "passed_rules": passed_rules,
                "failed_rules": failed_rules,
                "validation_score": round(validation_score, 2),
                "all_passed": all_passed,
                "has_critical_failures": has_critical_failures,
                "has_high_failures": has_high_failures,
                "critical_failures": critical_failures,
                "high_failures": high_failures,
                "validation_results": validation_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error analyzing validation results: {e}")
            return {
                "all_passed": False,
                "error": str(e)
            }
    
    async def _auto_approve_certificate(self, certificate_id: str) -> None:
        """Automatically approve a validated certificate"""
        try:
            # Update certificate status to completed
            await self.registry_service.mark_certificate_complete(certificate_id)
            
            # Create approval record
            self.approval_workflows[certificate_id] = {
                "status": "auto_approved",
                "approved_at": datetime.utcnow().isoformat(),
                "approved_by": "system",
                "approval_reason": "All validation rules passed with auto-approval enabled"
            }
            
            logger.info(f"Certificate {certificate_id} auto-approved successfully")
            
        except Exception as e:
            logger.error(f"Error auto-approving certificate: {e}")
    
    async def _initiate_approval_workflow(self, certificate_id: str, validation_summary: Dict[str, Any]) -> None:
        """Initiate manual approval workflow for validated certificate"""
        try:
            # Create approval workflow
            self.approval_workflows[certificate_id] = {
                "status": "pending_approval",
                "created_at": datetime.utcnow().isoformat(),
                "validation_summary": validation_summary,
                "approval_required": True,
                "approvers": [],  # Would be populated based on business rules
                "approval_deadline": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            logger.info(f"Approval workflow initiated for certificate: {certificate_id}")
            
        except Exception as e:
            logger.error(f"Error initiating approval workflow: {e}")
    
    async def _record_validation_history(
        self,
        certificate_id: str,
        validation_results: Dict[str, Dict[str, Any]],
        validation_summary: Dict[str, Any]
    ) -> None:
        """Record validation history"""
        try:
            if certificate_id not in self.validation_history:
                self.validation_history[certificate_id] = []
            
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "validation_status": self.validation_status[certificate_id].value,
                "validation_score": validation_summary.get("validation_score", 0),
                "passed_rules": validation_summary.get("passed_rules", 0),
                "failed_rules": validation_summary.get("failed_rules", 0),
                "critical_failures": validation_summary.get("critical_failures", []),
                "high_failures": validation_summary.get("high_failures", []),
                "validation_results": validation_results
            }
            
            self.validation_history[certificate_id].append(history_entry)
            
            # Keep only last 10 entries
            if len(self.validation_history[certificate_id]) > 10:
                self.validation_history[certificate_id] = self.validation_history[certificate_id][-10:]
                
        except Exception as e:
            logger.error(f"Error recording validation history: {e}")
    
    async def approve_certificate(
        self,
        certificate_id: str,
        approver: str,
        approval_reason: str = ""
    ) -> bool:
        """Approve a validated certificate"""
        try:
            if certificate_id not in self.approval_workflows:
                logger.error(f"No approval workflow found for certificate: {certificate_id}")
                return False
            
            workflow = self.approval_workflows[certificate_id]
            
            if workflow["status"] != "pending_approval":
                logger.error(f"Certificate {certificate_id} is not pending approval")
                return False
            
            # Update approval workflow
            workflow.update({
                "status": "approved",
                "approved_at": datetime.utcnow().isoformat(),
                "approved_by": approver,
                "approval_reason": approval_reason
            })
            
            # Mark certificate as completed
            await self.registry_service.mark_certificate_complete(certificate_id)
            
            # Update validation status
            self.validation_status[certificate_id] = ValidationStatus.APPROVED
            
            logger.info(f"Certificate {certificate_id} approved by {approver}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving certificate: {e}")
            return False
    
    async def reject_certificate(
        self,
        certificate_id: str,
        rejector: str,
        rejection_reason: str
    ) -> bool:
        """Reject a validated certificate"""
        try:
            if certificate_id not in self.approval_workflows:
                logger.error(f"No approval workflow found for certificate: {certificate_id}")
                return False
            
            workflow = self.approval_workflows[certificate_id]
            
            if workflow["status"] != "pending_approval":
                logger.error(f"Certificate {certificate_id} is not pending approval")
                return False
            
            # Update approval workflow
            workflow.update({
                "status": "rejected",
                "rejected_at": datetime.utcnow().isoformat(),
                "rejected_by": rejector,
                "rejection_reason": rejection_reason
            })
            
            # Update validation status
            self.validation_status[certificate_id] = ValidationStatus.REJECTED
            
            logger.info(f"Certificate {certificate_id} rejected by {rejector}")
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting certificate: {e}")
            return False
    
    async def get_validation_status(self, certificate_id: str) -> Optional[ValidationStatus]:
        """Get validation status for a certificate"""
        try:
            return self.validation_status.get(certificate_id)
        except Exception as e:
            logger.error(f"Error getting validation status: {e}")
            return None
    
    async def get_validation_history(self, certificate_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get validation history for a certificate"""
        try:
            return self.validation_history.get(certificate_id, [])[-limit:]
        except Exception as e:
            logger.error(f"Error getting validation history: {e}")
            return []
    
    async def get_approval_workflow(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Get approval workflow for a certificate"""
        try:
            return self.approval_workflows.get(certificate_id)
        except Exception as e:
            logger.error(f"Error getting approval workflow: {e}")
            return None
    
    async def update_validation_rule(
        self,
        rule_name: str,
        enabled: bool = None,
        threshold: Any = None,
        severity: ValidationSeverity = None
    ) -> bool:
        """Update validation rule configuration"""
        try:
            if rule_name not in self.validation_rules:
                logger.error(f"Validation rule not found: {rule_name}")
                return False
            
            rule = self.validation_rules[rule_name]
            
            if enabled is not None:
                rule["enabled"] = enabled
            
            if threshold is not None:
                rule["threshold"] = threshold
            
            if severity is not None:
                rule["severity"] = severity
            
            logger.info(f"Updated validation rule: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating validation rule: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the completion validator"""
        try:
            health_status = {
                "status": "healthy",
                "active_validations": sum(1 for s in self.validation_status.values() if s == ValidationStatus.IN_PROGRESS),
                "validated_certificates": sum(1 for s in self.validation_status.values() if s == ValidationStatus.VALIDATED),
                "approved_certificates": sum(1 for s in self.validation_status.values() if s == ValidationStatus.APPROVED),
                "failed_validations": sum(1 for s in self.validation_status.values() if s == ValidationStatus.FAILED),
                "active_locks": len(self.validation_locks),
                "validation_history_size": sum(len(h) for h in self.validation_history.values()),
                "active_approval_workflows": len([w for w in self.approval_workflows.values() if w["status"] == "pending_approval"]),
                "enabled_validation_rules": sum(1 for r in self.validation_rules.values() if r["enabled"]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
