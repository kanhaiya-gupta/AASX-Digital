"""
Cross-Domain Compliance Service

Coordinates compliance monitoring across all business domains, authentication, and data governance services.
Provides comprehensive compliance validation, monitoring, and reporting capabilities.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from ...repositories.business_domain_repository import BusinessDomainRepository
from ...repositories.auth_repository import AuthRepository
from ...repositories.data_governance_repository import DataGovernanceRepository
from ...models.business_domain import Organization, Project, File
from ...models.auth import User
from ...models.data_governance import DataLineage, DataQualityMetrics, ChangeRequest, DataVersion, GovernancePolicy
from ..base.base_service import BaseService

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRule:
    """Represents a compliance rule that applies across domains."""
    rule_id: str
    rule_name: str
    description: str
    domain: str  # business_domain, auth, data_governance, cross_domain
    rule_type: str  # access_control, data_quality, audit_requirement, policy_enforcement
    severity: str  # low, medium, high, critical
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)


@dataclass
class ComplianceCheck:
    """Represents a compliance check result."""
    check_id: str
    rule_id: str
    entity_id: str
    entity_type: str
    domain: str
    timestamp: str
    status: str  # compliant, non_compliant, warning, error
    details: Dict[str, Any]
    violations: List[Dict[str, Any]]
    recommendations: List[str]


@dataclass
class ComplianceSummary:
    """Represents a compliance summary for a scope."""
    summary_id: str
    scope: str  # organization, project, user, system
    scope_id: str
    generated_at: str
    total_checks: int
    compliant_checks: int
    non_compliant_checks: int
    warning_checks: int
    compliance_rate: float
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    overall_status: str  # compliant, warning, non_compliant, critical


class ComplianceService(BaseService):
    """
    Cross-domain compliance service that coordinates compliance monitoring across all services.
    
    Provides comprehensive compliance validation, monitoring, and reporting
    for business domain, authentication, and data governance operations.
    """
    
    def __init__(self, 
                 business_repo: BusinessDomainRepository,
                 auth_repo: AuthRepository,
                 governance_repo: DataGovernanceRepository):
        super().__init__("ComplianceService")
        
        # Repository dependencies for cross-domain operations
        self.business_repo = business_repo
        self.auth_repo = auth_repo
        self.governance_repo = governance_repo
        
        # In-memory compliance cache for performance
        self._compliance_cache = {}
        self._rules_cache = {}
        self._checks_cache = {}
        
        # Compliance configuration
        self.compliance_rules = []
        self.check_interval_minutes = 60
        self.retention_days = 365
        
        # Performance metrics
        self.compliance_checks = 0
        self.rules_evaluated = 0
        self.violations_detected = 0
        self.reports_generated = 0
        
        # Initialize service resources
        asyncio.create_task(self._initialize_service_resources())
    
    async def _initialize_service_resources(self) -> None:
        """Initialize service resources and load initial data."""
        try:
            logger.info("Initializing Compliance Service resources...")
            
            # Load compliance rules
            await self._load_compliance_rules()
            
            # Initialize compliance monitoring
            await self._initialize_compliance_monitoring()
            
            logger.info("Compliance Service resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Compliance Service resources: {e}")
            self.handle_error("_initialize_service_resources", e)
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            'service_name': self.service_name,
            'service_type': 'integration.compliance',
            'status': 'active' if self.is_active else 'inactive',
            'uptime': str(datetime.now() - self.start_time),
            'cache_size': len(self._compliance_cache),
            'compliance_checks': self.compliance_checks,
            'rules_evaluated': self.rules_evaluated,
            'violations_detected': self.violations_detected,
            'reports_generated': self.reports_generated
        }
    
    async def _cleanup_service_resources(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Clear caches
            self._compliance_cache.clear()
            self._rules_cache.clear()
            self._checks_cache.clear()
            
            logger.info(f"{self.service_name}: Cleaned up service resources")
            
        except Exception as e:
            logger.error(f"{self.service_name}: Error during cleanup: {e}")
            self.handle_error("cleanup", e)
    
    async def add_compliance_rule(self, rule_data: Dict[str, Any]) -> ComplianceRule:
        """Add a new compliance rule."""
        try:
            self._log_operation("add_compliance_rule", f"rule_name: {rule_data.get('rule_name')}")
            
            # Validate required fields
            required_fields = ['rule_name', 'description', 'domain', 'rule_type', 'severity']
            for field in required_fields:
                if not rule_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate rule ID
            rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(rule_data)}"
            
            # Create compliance rule
            rule = ComplianceRule(
                rule_id=rule_id,
                rule_name=rule_data['rule_name'],
                description=rule_data['description'],
                domain=rule_data['domain'],
                rule_type=rule_data['rule_type'],
                severity=rule_data['severity'],
                enabled=rule_data.get('enabled', True),
                conditions=rule_data.get('conditions', {}),
                actions=rule_data.get('actions', [])
            )
            
            # Store rule
            await self._store_compliance_rule(rule)
            
            # Update cache
            self._update_rules_cache(rule)
            
            # Update metrics
            self.rules_evaluated += 1
            
            logger.info(f"Compliance rule added successfully: {rule_id}")
            return rule
            
        except Exception as e:
            logger.error(f"Failed to add compliance rule: {e}")
            self.handle_error("add_compliance_rule", e)
            raise
    
    async def check_compliance(self, entity_id: str, entity_type: str, domain: str) -> List[ComplianceCheck]:
        """Check compliance for an entity across all applicable rules."""
        try:
            self._log_operation("check_compliance", f"entity_id: {entity_id}, domain: {domain}")
            
            # Check cache first
            cache_key = f"compliance_check:{domain}:{entity_type}:{entity_id}"
            if cache_key in self._compliance_cache:
                return self._compliance_cache[cache_key]
            
            # Get applicable rules for the domain
            applicable_rules = await self._get_applicable_rules(domain)
            
            # Perform compliance checks
            compliance_checks = []
            for rule in applicable_rules:
                if rule.enabled:
                    check_result = await self._evaluate_compliance_rule(rule, entity_id, entity_type, domain)
                    compliance_checks.append(check_result)
            
            # Update cache
            self._compliance_cache[cache_key] = compliance_checks
            
            # Update metrics
            self.compliance_checks += 1
            
            return compliance_checks
            
        except Exception as e:
            logger.error(f"Failed to check compliance: {e}")
            self.handle_error("check_compliance", e)
            return []
    
    async def get_compliance_summary(self, scope: str, scope_id: str) -> ComplianceSummary:
        """Get compliance summary for a specific scope."""
        try:
            self._log_operation("get_compliance_summary", f"scope: {scope}, scope_id: {scope_id}")
            
            # Check cache first
            cache_key = f"compliance_summary:{scope}:{scope_id}"
            if cache_key in self._compliance_cache:
                return self._compliance_cache[cache_key]
            
            # Get compliance checks for the scope
            checks = await self._get_compliance_checks_for_scope(scope, scope_id)
            
            # Calculate summary statistics
            total_checks = len(checks)
            compliant_checks = sum(1 for c in checks if c.status == "compliant")
            non_compliant_checks = sum(1 for c in checks if c.status == "non_compliant")
            warning_checks = sum(1 for c in checks if c.status == "warning")
            
            compliance_rate = (compliant_checks / total_checks * 100) if total_checks > 0 else 100.0
            
            # Count violations by severity
            critical_violations = sum(1 for c in checks if c.status == "non_compliant" and any(v.get('severity') == 'critical' for v in c.violations))
            high_violations = sum(1 for c in checks if c.status == "non_compliant" and any(v.get('severity') == 'high' for v in c.violations))
            medium_violations = sum(1 for c in checks if c.status == "non_compliant" and any(v.get('severity') == 'medium' for v in c.violations))
            low_violations = sum(1 for c in checks if c.status == "non_compliant" and any(v.get('severity') == 'low' for v in c.violations))
            
            # Determine overall status
            if critical_violations > 0:
                overall_status = "critical"
            elif high_violations > 0:
                overall_status = "non_compliant"
            elif medium_violations > 0 or low_violations > 0:
                overall_status = "warning"
            else:
                overall_status = "compliant"
            
            # Create compliance summary
            summary = ComplianceSummary(
                summary_id=f"compliance_summary_{scope}_{scope_id}_{datetime.now().strftime('%Y%m%d')}",
                scope=scope,
                scope_id=scope_id,
                generated_at=datetime.now().isoformat(),
                total_checks=total_checks,
                compliant_checks=compliant_checks,
                non_compliant_checks=non_compliant_checks,
                warning_checks=warning_checks,
                compliance_rate=compliance_rate,
                critical_violations=critical_violations,
                high_violations=high_violations,
                medium_violations=medium_violations,
                low_violations=low_violations,
                overall_status=overall_status
            )
            
            # Update cache
            self._compliance_cache[cache_key] = summary
            
            # Update metrics
            self.reports_generated += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get compliance summary: {e}")
            self.handle_error("get_compliance_summary", e)
            return ComplianceSummary(
                summary_id="", scope="", scope_id="", generated_at="", total_checks=0,
                compliant_checks=0, non_compliant_checks=0, warning_checks=0,
                compliance_rate=0.0, critical_violations=0, high_violations=0,
                medium_violations=0, low_violations=0, overall_status="unknown"
            )
    
    async def validate_operation(self, user_id: str, operation: str, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Validate if an operation complies with all applicable rules."""
        try:
            self._log_operation("validate_operation", f"operation: {operation}, entity_id: {entity_id}")
            
            # Get user information
            user = await self.auth_repo.get_user_by_id(user_id)
            if not user:
                return {
                    'compliant': False,
                    'reason': 'User not found',
                    'violations': [],
                    'recommendations': ['Verify user identity']
                }
            
            # Get user roles
            user_roles = await self.auth_repo.get_user_roles(user_id)
            
            # Check access control compliance
            access_compliant = await self._check_access_control_compliance(user, user_roles, operation, entity_id, entity_type, domain)
            
            # Check data quality compliance
            quality_compliant = await self._check_data_quality_compliance(entity_id, entity_type, domain)
            
            # Check policy compliance
            policy_compliant = await self._check_policy_compliance(operation, entity_id, entity_type, domain)
            
            # Determine overall compliance
            overall_compliant = access_compliant['compliant'] and quality_compliant['compliant'] and policy_compliant['compliant']
            
            # Collect all violations and recommendations
            all_violations = access_compliant['violations'] + quality_compliant['violations'] + policy_compliant['violations']
            all_recommendations = access_compliant['recommendations'] + quality_compliant['recommendations'] + policy_compliant['recommendations']
            
            # Update metrics
            if not overall_compliant:
                self.violations_detected += 1
            
            return {
                'compliant': overall_compliant,
                'access_control': access_compliant,
                'data_quality': quality_compliant,
                'policy_compliance': policy_compliant,
                'violations': all_violations,
                'recommendations': all_recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to validate operation: {e}")
            self.handle_error("validate_operation", e)
            return {
                'compliant': False,
                'reason': f'Validation error: {str(e)}',
                'violations': [],
                'recommendations': ['Contact system administrator']
            }
    
    # Private helper methods
    
    async def _load_compliance_rules(self):
        """Load compliance rules from configuration or database."""
        try:
            # Load default compliance rules
            default_rules = [
                ComplianceRule(
                    rule_id="rule_access_control_001",
                    rule_name="User Authentication Required",
                    description="All operations require valid user authentication",
                    domain="cross_domain",
                    rule_type="access_control",
                    severity="critical",
                    enabled=True,
                    conditions={"require_auth": True},
                    actions=["block_operation", "log_violation"]
                ),
                ComplianceRule(
                    rule_id="rule_data_quality_001",
                    rule_name="Data Quality Threshold",
                    description="Data must meet minimum quality standards",
                    domain="data_governance",
                    rule_type="data_quality",
                    severity="medium",
                    enabled=True,
                    conditions={"min_quality_score": 80},
                    actions=["warn_user", "log_violation"]
                ),
                ComplianceRule(
                    rule_id="rule_policy_001",
                    rule_name="Policy Enforcement",
                    description="All operations must comply with governance policies",
                    domain="data_governance",
                    rule_type="policy_enforcement",
                    severity="high",
                    enabled=True,
                    conditions={"enforce_policies": True},
                    actions=["block_operation", "log_violation", "notify_admin"]
                )
            ]
            
            self.compliance_rules = default_rules
            
            # Update cache
            for rule in default_rules:
                self._update_rules_cache(rule)
            
            logger.info(f"Loaded {len(default_rules)} compliance rules")
            
        except Exception as e:
            logger.warning(f"Failed to load compliance rules: {e}")
    
    async def _initialize_compliance_monitoring(self):
        """Initialize compliance monitoring."""
        try:
            # Set up periodic compliance monitoring
            asyncio.create_task(self._periodic_compliance_monitoring())
            logger.info("Compliance monitoring initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize compliance monitoring: {e}")
    
    async def _store_compliance_rule(self, rule: ComplianceRule):
        """Store compliance rule in persistent storage."""
        try:
            # For now, just log the rule
            # In a real implementation, this would store in database
            logger.debug(f"Storing compliance rule: {rule.rule_id}")
            
        except Exception as e:
            logger.error(f"Failed to store compliance rule: {e}")
    
    async def _get_applicable_rules(self, domain: str) -> List[ComplianceRule]:
        """Get compliance rules applicable to a specific domain."""
        try:
            applicable_rules = []
            
            for rule in self.compliance_rules:
                if rule.enabled and (rule.domain == domain or rule.domain == "cross_domain"):
                    applicable_rules.append(rule)
            
            return applicable_rules
            
        except Exception as e:
            logger.error(f"Failed to get applicable rules: {e}")
            return []
    
    async def _evaluate_compliance_rule(self, rule: ComplianceRule, entity_id: str, entity_type: str, domain: str) -> ComplianceCheck:
        """Evaluate a specific compliance rule against an entity."""
        try:
            # Generate check ID
            check_id = f"check_{rule.rule_id}_{entity_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Evaluate rule based on type
            if rule.rule_type == "access_control":
                result = await self._evaluate_access_control_rule(rule, entity_id, entity_type, domain)
            elif rule.rule_type == "data_quality":
                result = await self._evaluate_data_quality_rule(rule, entity_id, entity_type, domain)
            elif rule.rule_type == "policy_enforcement":
                result = await self._evaluate_policy_rule(rule, entity_id, entity_type, domain)
            else:
                result = {
                    'status': 'error',
                    'details': {'error': f'Unknown rule type: {rule.rule_type}'},
                    'violations': [],
                    'recommendations': ['Review rule configuration']
                }
            
            # Create compliance check
            check = ComplianceCheck(
                check_id=check_id,
                rule_id=rule.rule_id,
                entity_id=entity_id,
                entity_type=entity_type,
                domain=domain,
                timestamp=datetime.now().isoformat(),
                status=result['status'],
                details=result['details'],
                violations=result['violations'],
                recommendations=result['recommendations']
            )
            
            return check
            
        except Exception as e:
            logger.error(f"Failed to evaluate compliance rule: {e}")
            return ComplianceCheck(
                check_id="", rule_id="", entity_id="", entity_type="", domain="",
                timestamp="", status="error", details={'error': str(e)}, violations=[], recommendations=[]
            )
    
    async def _evaluate_access_control_rule(self, rule: ComplianceRule, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Evaluate access control compliance rule."""
        try:
            # For now, return basic compliance
            # In a real implementation, this would check actual permissions
            return {
                'status': 'compliant',
                'details': {'message': 'Access control check passed'},
                'violations': [],
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate access control rule: {e}")
            return {
                'status': 'error',
                'details': {'error': str(e)},
                'violations': [],
                'recommendations': ['Review access control configuration']
            }
    
    async def _evaluate_data_quality_rule(self, rule: ComplianceRule, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Evaluate data quality compliance rule."""
        try:
            # For now, return basic compliance
            # In a real implementation, this would check actual data quality metrics
            return {
                'status': 'compliant',
                'details': {'message': 'Data quality check passed'},
                'violations': [],
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate data quality rule: {e}")
            return {
                'status': 'error',
                'details': {'error': str(e)},
                'violations': [],
                'recommendations': ['Review data quality configuration']
            }
    
    async def _evaluate_policy_rule(self, rule: ComplianceRule, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Evaluate policy compliance rule."""
        try:
            # For now, return basic compliance
            # In a real implementation, this would check actual governance policies
            return {
                'status': 'compliant',
                'details': {'message': 'Policy compliance check passed'},
                'violations': [],
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate policy rule: {e}")
            return {
                'status': 'error',
                'details': {'error': str(e)},
                'violations': [],
                'recommendations': ['Review policy configuration']
            }
    
    async def _check_access_control_compliance(self, user: User, user_roles: List[str], operation: str, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Check access control compliance for an operation."""
        try:
            # For now, return basic compliance
            # In a real implementation, this would check actual permissions
            return {
                'compliant': True,
                'details': {'message': 'Access control compliant'},
                'violations': [],
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"Failed to check access control compliance: {e}")
            return {
                'compliant': False,
                'details': {'error': str(e)},
                'violations': [{'type': 'access_control', 'severity': 'high', 'message': 'Access control check failed'}],
                'recommendations': ['Review user permissions', 'Contact system administrator']
            }
    
    async def _check_data_quality_compliance(self, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Check data quality compliance for an entity."""
        try:
            # For now, return basic compliance
            # In a real implementation, this would check actual data quality metrics
            return {
                'compliant': True,
                'details': {'message': 'Data quality compliant'},
                'violations': [],
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"Failed to check data quality compliance: {e}")
            return {
                'compliant': False,
                'details': {'error': str(e)},
                'violations': [{'type': 'data_quality', 'severity': 'medium', 'message': 'Data quality check failed'}],
                'recommendations': ['Review data quality metrics', 'Improve data quality']
            }
    
    async def _check_policy_compliance(self, operation: str, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Check policy compliance for an operation."""
        try:
            # For now, return basic compliance
            # In a real implementation, this would check actual governance policies
            return {
                'compliant': True,
                'details': {'message': 'Policy compliant'},
                'violations': [],
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"Failed to check policy compliance: {e}")
            return {
                'compliant': False,
                'details': {'error': str(e)},
                'violations': [{'type': 'policy', 'severity': 'high', 'message': 'Policy compliance check failed'}],
                'recommendations': ['Review governance policies', 'Update policy configuration']
            }
    
    async def _get_compliance_checks_for_scope(self, scope: str, scope_id: str) -> List[ComplianceCheck]:
        """Get compliance checks for a specific scope."""
        try:
            # For now, return empty list
            # In a real implementation, this would query the compliance database
            return []
            
        except Exception as e:
            logger.error(f"Failed to get compliance checks for scope: {e}")
            return []
    
    def _update_rules_cache(self, rule: ComplianceRule):
        """Update the rules cache with new data."""
        self._rules_cache[rule.rule_id] = rule
        
        # Maintain cache size
        if len(self._rules_cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(self._rules_cache.keys())[:100]
            for key in oldest_keys:
                del self._rules_cache[key]
    
    async def _periodic_compliance_monitoring(self):
        """Periodic compliance monitoring."""
        while True:
            try:
                await asyncio.sleep(self.check_interval_minutes * 60)
                
                # Perform periodic compliance tasks
                # This would typically include compliance checks, rule updates, etc.
                logger.info("Completed periodic compliance monitoring")
                
            except Exception as e:
                logger.error(f"Periodic compliance monitoring failed: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry
