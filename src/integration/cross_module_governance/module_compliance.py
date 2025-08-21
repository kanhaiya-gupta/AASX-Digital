"""
Module Compliance Service

This service ensures that all external modules comply with governance
policies and business rules, providing compliance monitoring and
enforcement across the AAS Data Modeling Engine.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from .models import (
    ComplianceRule, 
    ComplianceStatus, 
    PolicySeverity,
    GovernancePolicy
)


logger = logging.getLogger(__name__)


class ModuleComplianceService:
    """
    Service for ensuring module compliance with governance policies.
    
    This service provides:
    - Compliance rule management and enforcement
    - Policy violation detection and tracking
    - Compliance reporting and monitoring
    - Automated compliance checks
    """
    
    def __init__(self):
        """Initialize the module compliance service."""
        self.compliance_rules: Dict[UUID, ComplianceRule] = {}
        self.governance_policies: Dict[UUID, GovernancePolicy] = {}
        self.module_compliance: Dict[str, Dict[str, Any]] = {}  # module_name -> compliance_data
        self.violation_history: List[Dict[str, Any]] = []
        self.is_monitoring = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def start_compliance_monitoring(self) -> None:
        """Start automatic compliance monitoring."""
        if self.is_monitoring:
            logger.warning("Compliance monitoring is already running")
            return
        
        self.is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._compliance_monitoring_loop())
        logger.info("Started module compliance monitoring")
    
    async def stop_compliance_monitoring(self) -> None:
        """Stop automatic compliance monitoring."""
        self.is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped module compliance monitoring")
    
    async def _compliance_monitoring_loop(self) -> None:
        """Background task for monitoring compliance."""
        while self.is_monitoring:
            try:
                await self._perform_compliance_checks()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in compliance monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def _perform_compliance_checks(self) -> None:
        """Perform compliance checks for all modules."""
        logger.debug("Performing compliance checks...")
        
        # This would typically check compliance across all registered modules
        # For now, we'll just log that we're monitoring
        pass
    
    def add_compliance_rule(self, rule: ComplianceRule) -> bool:
        """
        Add a new compliance rule.
        
        Args:
            rule: Compliance rule to add
            
        Returns:
            True if added successfully, False otherwise
        """
        if rule.rule_id in self.compliance_rules:
            logger.warning(f"Compliance rule already exists: {rule.rule_id}")
            return False
        
        self.compliance_rules[rule.rule_id] = rule
        logger.info(f"Added compliance rule: {rule.rule_name}")
        return True
    
    def remove_compliance_rule(self, rule_id: UUID) -> bool:
        """
        Remove a compliance rule.
        
        Args:
            rule_id: ID of the rule to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if rule_id not in self.compliance_rules:
            logger.warning(f"Compliance rule not found: {rule_id}")
            return False
        
        rule_name = self.compliance_rules[rule_id].rule_name
        del self.compliance_rules[rule_id]
        logger.info(f"Removed compliance rule: {rule_name}")
        return True
    
    def add_governance_policy(self, policy: GovernancePolicy) -> bool:
        """
        Add a new governance policy.
        
        Args:
            policy: Governance policy to add
            
        Returns:
            True if added successfully, False otherwise
        """
        if policy.policy_id in self.governance_policies:
            logger.warning(f"Governance policy already exists: {policy.policy_id}")
            return False
        
        self.governance_policies[policy.policy_id] = policy
        logger.info(f"Added governance policy: {policy.policy_name}")
        return True
    
    def check_module_compliance(
        self,
        module_name: str,
        data_id: str,
        data_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check compliance for a specific module and data.
        
        Args:
            module_name: Name of the module to check
            data_id: ID of the data being processed
            data_context: Context information about the data
            
        Returns:
            Compliance check results
        """
        applicable_rules = self._get_applicable_rules(module_name)
        violations = []
        compliance_score = 100.0
        
        for rule in applicable_rules:
            if not rule.is_active:
                continue
            
            rule_result = self._evaluate_rule(rule, data_context)
            if not rule_result["compliant"]:
                violations.append({
                    "rule_id": str(rule.rule_id),
                    "rule_name": rule.rule_name,
                    "rule_type": rule.rule_type,
                    "severity": rule.severity.value,
                    "violation_details": rule_result["details"]
                })
                
                # Reduce compliance score based on severity
                if rule.severity == PolicySeverity.CRITICAL:
                    compliance_score -= 25
                elif rule.severity == PolicySeverity.HIGH:
                    compliance_score -= 15
                elif rule.severity == PolicySeverity.MEDIUM:
                    compliance_score -= 10
                elif rule.severity == PolicySeverity.LOW:
                    compliance_score -= 5
        
        compliance_score = max(0.0, compliance_score)
        
        # Determine overall compliance status
        if violations:
            if any(v["severity"] == "critical" for v in violations):
                status = ComplianceStatus.NON_COMPLIANT
            elif any(v["severity"] == "high" for v in violations):
                status = ComplianceStatus.NON_COMPLIANT
            else:
                status = ComplianceStatus.PENDING
        else:
            status = ComplianceStatus.COMPLIANT
        
        # Update module compliance tracking
        if module_name not in self.module_compliance:
            self.module_compliance[module_name] = {}
        
        self.module_compliance[module_name][data_id] = {
            "status": status.value,
            "compliance_score": compliance_score,
            "violations": violations,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        # Log violations
        if violations:
            logger.warning(f"Module {module_name} has {len(violations)} compliance violations for data {data_id}")
            self._record_violations(module_name, data_id, violations)
        
        return {
            "module_name": module_name,
            "data_id": data_id,
            "compliance_status": status.value,
            "compliance_score": compliance_score,
            "violations": violations,
            "total_rules_checked": len(applicable_rules),
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def _get_applicable_rules(self, module_name: str) -> List[ComplianceRule]:
        """Get all compliance rules applicable to a module."""
        applicable_rules = []
        
        for rule in self.compliance_rules.values():
            if not rule.is_active:
                continue
            
            # Check if rule applies to this module
            if not rule.applicable_modules or module_name in rule.applicable_modules:
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _evaluate_rule(self, rule: ComplianceRule, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a compliance rule against data context.
        
        Args:
            rule: Compliance rule to evaluate
            data_context: Data context to evaluate against
            
        Returns:
            Rule evaluation results
        """
        try:
            # Simple rule evaluation based on conditions
            # In a real implementation, this would use a rule engine
            conditions = rule.rule_conditions
            compliant = True
            details = []
            
            for condition_key, expected_value in conditions.items():
                actual_value = data_context.get(condition_key)
                
                if actual_value != expected_value:
                    compliant = False
                    details.append(f"Condition '{condition_key}' failed: expected {expected_value}, got {actual_value}")
            
            return {
                "compliant": compliant,
                "details": details
            }
            
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_name}: {e}")
            return {
                "compliant": False,
                "details": [f"Rule evaluation error: {str(e)}"]
            }
    
    def _record_violations(self, module_name: str, data_id: str, violations: List[Dict[str, Any]]) -> None:
        """Record policy violations for tracking."""
        for violation in violations:
            violation_record = {
                "module_name": module_name,
                "data_id": data_id,
                "rule_id": violation["rule_id"],
                "rule_name": violation["rule_name"],
                "severity": violation["severity"],
                "detected_at": datetime.utcnow().isoformat(),
                "details": violation["violation_details"]
            }
            self.violation_history.append(violation_record)
    
    def get_module_compliance_status(self, module_name: str) -> Dict[str, Any]:
        """Get compliance status for a specific module."""
        if module_name not in self.module_compliance:
            return {
                "module_name": module_name,
                "status": "unknown",
                "compliance_score": 0.0,
                "total_checks": 0,
                "last_check": None
            }
        
        module_data = self.module_compliance[module_name]
        total_checks = len(module_data)
        
        if total_checks == 0:
            return {
                "module_name": module_name,
                "status": "unknown",
                "compliance_score": 0.0,
                "total_checks": 0,
                "last_check": None
            }
        
        # Calculate average compliance score
        total_score = sum(check["compliance_score"] for check in module_data.values())
        avg_score = total_score / total_checks
        
        # Determine overall status
        if avg_score >= 90:
            overall_status = "excellent"
        elif avg_score >= 75:
            overall_status = "good"
        elif avg_score >= 60:
            overall_status = "acceptable"
        else:
            overall_status = "poor"
        
        # Get last check time
        last_check = max(check["checked_at"] for check in module_data.values())
        
        return {
            "module_name": module_name,
            "status": overall_status,
            "compliance_score": round(avg_score, 2),
            "total_checks": total_checks,
            "last_check": last_check
        }
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get summary of all compliance information."""
        total_rules = len(self.compliance_rules)
        total_policies = len(self.governance_policies)
        total_modules = len(self.module_compliance)
        total_violations = len(self.violation_history)
        
        # Count active rules
        active_rules = sum(1 for rule in self.compliance_rules.values() if rule.is_active)
        
        # Count active policies
        active_policies = sum(1 for policy in self.governance_policies.values() if policy.is_active)
        
        # Calculate overall compliance score
        if total_modules == 0:
            overall_score = 100.0
        else:
            module_scores = []
            for module_name in self.module_compliance:
                module_status = self.get_module_compliance_status(module_name)
                module_scores.append(module_status["compliance_score"])
            
            overall_score = sum(module_scores) / len(module_scores) if module_scores else 100.0
        
        return {
            "total_compliance_rules": total_rules,
            "active_compliance_rules": active_rules,
            "total_governance_policies": total_policies,
            "active_governance_policies": active_policies,
            "modules_monitored": total_modules,
            "total_violations": total_violations,
            "overall_compliance_score": round(overall_score, 2),
            "is_monitoring": self.is_monitoring
        }
    
    def export_compliance_report(self, format: str = "json") -> str:
        """
        Export compliance report in specified format.
        
        Args:
            format: Export format (json, csv, etc.)
            
        Returns:
            Exported report as string
        """
        if format.lower() == "json":
            import json
            data = {
                "summary": self.get_compliance_summary(),
                "module_compliance": self.module_compliance,
                "violation_history": self.violation_history,
                "exported_at": datetime.utcnow().isoformat()
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_old_violations(self, days_old: int = 90) -> int:
        """
        Clean up old violation records.
        
        Args:
            days_old: Remove violations older than this many days
            
        Returns:
            Number of violations removed
        """
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
        
        violations_to_remove = []
        for i, violation in enumerate(self.violation_history):
            detected_at = datetime.fromisoformat(violation["detected_at"])
            if detected_at < cutoff_date:
                violations_to_remove.append(i)
        
        # Remove from end to avoid index issues
        for i in reversed(violations_to_remove):
            del self.violation_history[i]
        
        logger.info(f"Cleaned up {len(violations_to_remove)} old violations")
        return len(violations_to_remove)
