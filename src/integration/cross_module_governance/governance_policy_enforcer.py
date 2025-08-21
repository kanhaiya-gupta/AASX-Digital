"""
Governance Policy Enforcer Service

This service enforces governance policies across all external modules,
providing policy validation, violation handling, and automated
enforcement actions for the AAS Data Modeling Engine.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from .models import (
    GovernancePolicy, 
    ComplianceRule, 
    PolicyViolation, 
    PolicySeverity,
    ComplianceStatus
)


logger = logging.getLogger(__name__)


class GovernancePolicyEnforcerService:
    """
    Service for enforcing governance policies across all modules.
    
    This service provides:
    - Policy validation and enforcement
    - Violation detection and handling
    - Automated enforcement actions
    - Policy compliance reporting
    """
    
    def __init__(self):
        """Initialize the governance policy enforcer service."""
        self.policies: Dict[UUID, GovernancePolicy] = {}
        self.active_policies: Set[UUID] = set()
        self.policy_violations: Dict[UUID, PolicyViolation] = {}
        self.enforcement_actions: List[Dict[str, Any]] = []
        self.is_enforcing = False
        self._enforcement_task: Optional[asyncio.Task] = None
        
    async def start_policy_enforcement(self) -> None:
        """Start automatic policy enforcement."""
        if self.is_enforcing:
            logger.warning("Policy enforcement is already running")
            return
        
        self.is_enforcing = True
        self._enforcement_task = asyncio.create_task(self._policy_enforcement_loop())
        logger.info("Started governance policy enforcement")
    
    async def stop_policy_enforcement(self) -> None:
        """Stop automatic policy enforcement."""
        self.is_enforcing = False
        
        if self._enforcement_task:
            self._enforcement_task.cancel()
            try:
                await self._enforcement_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped governance policy enforcement")
    
    async def _policy_enforcement_loop(self) -> None:
        """Background task for policy enforcement."""
        while self.is_enforcing:
            try:
                await self._enforce_policies()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in policy enforcement loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def _enforce_policies(self) -> None:
        """Enforce all active policies."""
        logger.debug("Enforcing governance policies...")
        
        # This would typically check policy compliance across all modules
        # For now, we'll just log that we're enforcing
        pass
    
    def add_policy(self, policy: GovernancePolicy) -> bool:
        """
        Add a new governance policy.
        
        Args:
            policy: Governance policy to add
            
        Returns:
            True if added successfully, False otherwise
        """
        if policy.policy_id in self.policies:
            logger.warning(f"Governance policy already exists: {policy.policy_id}")
            return False
        
        self.policies[policy.policy_id] = policy
        
        if policy.is_active:
            self.active_policies.add(policy.policy_id)
        
        logger.info(f"Added governance policy: {policy.policy_name}")
        return True
    
    def remove_policy(self, policy_id: UUID) -> bool:
        """
        Remove a governance policy.
        
        Args:
            policy_id: ID of the policy to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if policy_id not in self.policies:
            logger.warning(f"Governance policy not found: {policy_id}")
            return False
        
        policy_name = self.policies[policy_id].policy_name
        del self.policies[policy_id]
        self.active_policies.discard(policy_id)
        
        logger.info(f"Removed governance policy: {policy_name}")
        return True
    
    def activate_policy(self, policy_id: UUID) -> bool:
        """
        Activate a governance policy.
        
        Args:
            policy_id: ID of the policy to activate
            
        Returns:
            True if activated successfully, False otherwise
        """
        if policy_id not in self.policies:
            logger.warning(f"Governance policy not found: {policy_id}")
            return False
        
        policy = self.policies[policy_id]
        policy.is_active = True
        self.active_policies.add(policy_id)
        
        logger.info(f"Activated governance policy: {policy.policy_name}")
        return True
    
    def deactivate_policy(self, policy_id: UUID) -> bool:
        """
        Deactivate a governance policy.
        
        Args:
            policy_id: ID of the policy to deactivate
            
        Returns:
            True if deactivated successfully, False otherwise
        """
        if policy_id not in self.policies:
            logger.warning(f"Governance policy not found: {policy_id}")
            return False
        
        policy = self.policies[policy_id]
        policy.is_active = False
        self.active_policies.discard(policy_id)
        
        logger.info(f"Deactivated governance policy: {policy.policy_name}")
        return True
    
    def validate_operation(
        self,
        module_name: str,
        operation_type: str,
        data_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate an operation against applicable policies.
        
        Args:
            module_name: Name of the module performing the operation
            operation_type: Type of operation being performed
            data_context: Context information about the operation
            
        Returns:
            Validation results
        """
        applicable_policies = self._get_applicable_policies(module_name, operation_type)
        violations = []
        is_allowed = True
        
        for policy in applicable_policies:
            if not policy.is_active:
                continue
            
            policy_result = self._validate_policy(policy, data_context)
            if not policy_result["compliant"]:
                violations.extend(policy_result["violations"])
                
                # Check enforcement level
                if policy.enforcement_level == "strict":
                    is_allowed = False
        
        # Record violations if any
        if violations:
            for violation in violations:
                self._record_policy_violation(violation)
        
        return {
            "operation_allowed": is_allowed,
            "module_name": module_name,
            "operation_type": operation_type,
            "policies_checked": len(applicable_policies),
            "violations": violations,
            "validation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_applicable_policies(self, module_name: str, operation_type: str) -> List[GovernancePolicy]:
        """Get all policies applicable to a module and operation."""
        applicable_policies = []
        
        for policy in self.policies.values():
            if not policy.is_active:
                continue
            
            # Check if policy applies to this module
            if not policy.applicable_modules or module_name in policy.applicable_modules:
                # Check if policy applies to this operation type
                if self._policy_applies_to_operation(policy, operation_type):
                    applicable_policies.append(policy)
        
        return applicable_policies
    
    def _policy_applies_to_operation(self, policy: GovernancePolicy, operation_type: str) -> bool:
        """Check if a policy applies to a specific operation type."""
        # Simple check - in a real implementation, this would be more sophisticated
        # For now, we'll assume all policies apply to all operations
        return True
    
    def _validate_policy(self, policy: GovernancePolicy, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a policy against data context.
        
        Args:
            policy: Governance policy to validate
            data_context: Data context to validate against
            
        Returns:
            Policy validation results
        """
        violations = []
        
        for rule in policy.policy_rules:
            if not rule.is_active:
                continue
            
            rule_result = self._evaluate_compliance_rule(rule, data_context)
            if not rule_result["compliant"]:
                violation = PolicyViolation(
                    policy_id=policy.policy_id,
                    rule_id=rule.rule_id,
                    module_name=data_context.get("module_name", "unknown"),
                    data_id=data_context.get("data_id", "unknown"),
                    violation_type=rule.rule_type,
                    violation_description=f"Policy {policy.policy_name} rule {rule.rule_name} violated",
                    severity=rule.severity
                )
                violations.append(violation)
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _evaluate_compliance_rule(self, rule: ComplianceRule, data_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a compliance rule against data context.
        
        Args:
            rule: Compliance rule to evaluate
            data_context: Data context to evaluate against
            
        Returns:
            Rule evaluation results
        """
        try:
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
            logger.error(f"Error evaluating compliance rule {rule.rule_name}: {e}")
            return {
                "compliant": False,
                "details": [f"Rule evaluation error: {str(e)}"]
            }
    
    def _record_policy_violation(self, violation: PolicyViolation) -> None:
        """Record a policy violation."""
        self.policy_violations[violation.violation_id] = violation
        
        # Log the violation
        logger.warning(f"Policy violation detected: {violation.violation_description} (Severity: {violation.severity.value})")
        
        # Record enforcement action
        action = {
            "action_id": str(UUID.uuid4()),
            "violation_id": str(violation.violation_id),
            "action_type": "violation_recorded",
            "module_name": violation.module_name,
            "severity": violation.severity.value,
            "action_timestamp": datetime.utcnow().isoformat(),
            "details": violation.violation_description
        }
        self.enforcement_actions.append(action)
    
    def resolve_violation(
        self,
        violation_id: UUID,
        resolution_notes: str,
        resolved_by: str = "system"
    ) -> bool:
        """
        Mark a policy violation as resolved.
        
        Args:
            violation_id: ID of the violation to resolve
            resolution_notes: Notes about how the violation was resolved
            resolved_by: Who resolved the violation
            
        Returns:
            True if resolved successfully, False otherwise
        """
        if violation_id not in self.policy_violations:
            logger.warning(f"Policy violation not found: {violation_id}")
            return False
        
        violation = self.policy_violations[violation_id]
        violation.is_resolved = True
        violation.resolved_at = datetime.utcnow()
        violation.resolution_notes = resolution_notes
        
        # Record enforcement action
        action = {
            "action_id": str(UUID.uuid4()),
            "violation_id": str(violation_id),
            "action_type": "violation_resolved",
            "module_name": violation.module_name,
            "severity": violation.severity.value,
            "action_timestamp": datetime.utcnow().isoformat(),
            "details": f"Violation resolved by {resolved_by}: {resolution_notes}"
        }
        self.enforcement_actions.append(action)
        
        logger.info(f"Policy violation resolved: {violation_id}")
        return True
    
    def get_policy_violations(
        self,
        module_name: Optional[str] = None,
        severity: Optional[PolicySeverity] = None,
        resolved_only: Optional[bool] = None
    ) -> List[PolicyViolation]:
        """
        Get policy violations with optional filtering.
        
        Args:
            module_name: Filter by module name
            severity: Filter by severity level
            resolved_only: Filter by resolution status
            
        Returns:
            List of policy violations
        """
        violations = list(self.policy_violations.values())
        
        # Apply filters
        if module_name:
            violations = [v for v in violations if v.module_name == module_name]
        
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        if resolved_only is not None:
            violations = [v for v in violations if v.is_resolved == resolved_only]
        
        # Sort by detection time (newest first)
        violations.sort(key=lambda v: v.detected_at, reverse=True)
        
        return violations
    
    def get_enforcement_summary(self) -> Dict[str, Any]:
        """Get summary of policy enforcement activities."""
        total_policies = len(self.policies)
        active_policies = len(self.active_policies)
        total_violations = len(self.policy_violations)
        resolved_violations = sum(1 for v in self.policy_violations.values() if v.is_resolved)
        unresolved_violations = total_violations - resolved_violations
        total_actions = len(self.enforcement_actions)
        
        # Count violations by severity
        severity_counts = {}
        for violation in self.policy_violations.values():
            severity = violation.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count violations by module
        module_counts = {}
        for violation in self.policy_violations.values():
            module = violation.module_name
            module_counts[module] = module_counts.get(module, 0) + 1
        
        return {
            "total_policies": total_policies,
            "active_policies": active_policies,
            "total_violations": total_violations,
            "resolved_violations": resolved_violations,
            "unresolved_violations": unresolved_violations,
            "total_enforcement_actions": total_actions,
            "violations_by_severity": severity_counts,
            "violations_by_module": module_counts,
            "is_enforcing": self.is_enforcing
        }
    
    def export_enforcement_report(self, format: str = "json") -> str:
        """
        Export enforcement report in specified format.
        
        Args:
            format: Export format (json, csv, etc.)
            
        Returns:
            Exported report as string
        """
        if format.lower() == "json":
            import json
            data = {
                "summary": self.get_enforcement_summary(),
                "policy_violations": [v.to_dict() for v in self.policy_violations.values()],
                "enforcement_actions": self.enforcement_actions,
                "exported_at": datetime.utcnow().isoformat()
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_old_violations(self, days_old: int = 90) -> int:
        """
        Clean up old policy violations.
        
        Args:
            days_old: Remove violations older than this many days
            
        Returns:
            Number of violations removed
        """
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
        
        violations_to_remove = []
        for violation_id, violation in self.policy_violations.items():
            if violation.detected_at < cutoff_date:
                violations_to_remove.append(violation_id)
        
        for violation_id in violations_to_remove:
            del self.policy_violations[violation_id]
        
        logger.info(f"Cleaned up {len(violations_to_remove)} old policy violations")
        return len(violations_to_remove)
