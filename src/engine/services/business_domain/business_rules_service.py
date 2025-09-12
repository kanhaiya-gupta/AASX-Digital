"""
Business Rules Engine Service

Business logic execution engine for complex business rule processing.
Provides rule-based decision making and business logic orchestration.

Features:
- Rule-based decision making
- Business logic execution
- Rule chaining and dependencies
- Rule performance monitoring
- Rule versioning and management
- Business workflow orchestration
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from ...monitoring.monitoring_config import MonitoringConfig


class RuleType(Enum):
    """Types of business rules"""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    DECISION = "decision"
    CALCULATION = "calculation"
    WORKFLOW = "workflow"
    COMPLIANCE = "compliance"
    BUSINESS_LOGIC = "business_logic"


class RulePriority(Enum):
    """Rule execution priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class RuleStatus(Enum):
    """Rule execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class BusinessRule:
    """Business rule definition"""
    id: str
    name: str
    description: str
    rule_type: RuleType
    priority: RulePriority = RulePriority.NORMAL
    version: str = "1.0.0"
    enabled: bool = True
    rule_definition: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RuleExecutionResult:
    """Result of rule execution"""
    rule_id: str
    rule_name: str
    status: RuleStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time: float = 0.0
    success: bool = False
    output: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BusinessRulesEngine:
    """
    Business rules engine for complex business logic execution and rule management.
    
    Provides:
    - Rule-based decision making
    - Business logic execution
    - Rule chaining and dependencies
    - Rule performance monitoring
    - Rule versioning and management
    """
    
    def __init__(self, config: MonitoringConfig):
        """
        Initialize the business rules engine.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.rules: Dict[str, BusinessRule] = {}
        self.rule_executors: Dict[str, Callable] = {}
        self.execution_history: List[RuleExecutionResult] = []
        self.max_history = config.business_rules.max_history if hasattr(config, 'business_rules') else 1000
        
        # Initialize built-in rule executors
        self._initialize_builtin_executors()
        
        # Load default business rules
        self._load_default_rules()
        
        self.logger.info("BusinessRulesEngine initialized with enterprise-grade business logic capabilities")
    
    def _initialize_builtin_executors(self):
        """Initialize built-in rule execution functions"""
        self.rule_executors.update({
            'validation_rule': self._execute_validation_rule,
            'transformation_rule': self._execute_transformation_rule,
            'decision_rule': self._execute_decision_rule,
            'calculation_rule': self._execute_calculation_rule,
            'workflow_rule': self._execute_workflow_rule,
            'compliance_rule': self._execute_compliance_rule
        })
    
    def _load_default_rules(self):
        """Load default business rules"""
        default_rules = [
            BusinessRule(
                id="file_size_validation",
                name="File Size Validation",
                description="Validate file size against business limits",
                rule_type=RuleType.VALIDATION,
                priority=RulePriority.HIGH,
                rule_definition={
                    'max_file_size_mb': 100,
                    'allowed_extensions': ['.aasx', '.json', '.yaml']
                },
                conditions=[
                    {
                        'field': 'file_size_mb',
                        'operator': '<=',
                        'value': 100
                    }
                ],
                actions=[
                    {
                        'action': 'approve',
                        'message': 'File size within limits'
                    }
                ]
            ),
            BusinessRule(
                id="priority_assignment",
                name="Priority Assignment",
                description="Automatically assign job priority based on business rules",
                rule_type=RuleType.DECISION,
                priority=RulePriority.NORMAL,
                rule_definition={
                    'priority_mapping': {
                        'urgent': ['critical', 'high'],
                        'normal': ['medium', 'low']
                    }
                },
                conditions=[
                    {
                        'field': 'job_type',
                        'operator': 'in',
                        'value': ['extraction', 'generation']
                    }
                ],
                actions=[
                    {
                        'action': 'set_priority',
                        'value': 'high'
                    }
                ]
            ),
            BusinessRule(
                id="compliance_check",
                name="Compliance Check",
                description="Check business compliance requirements",
                rule_type=RuleType.COMPLIANCE,
                priority=RulePriority.HIGH,
                rule_definition={
                    'compliance_frameworks': ['GDPR', 'ISO27001', 'SOX']
                },
                conditions=[
                    {
                        'field': 'data_sensitivity',
                        'operator': '==',
                        'value': 'high'
                    }
                ],
                actions=[
                    {
                        'action': 'require_approval',
                        'approver_role': 'compliance_officer'
                    }
                ]
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: BusinessRule) -> bool:
        """
        Add a business rule to the engine.
        
        Args:
            rule: Business rule to add
            
        Returns:
            True if rule was added successfully
        """
        try:
            # Validate rule
            if not self._validate_rule(rule):
                self.logger.error(f"Invalid rule: {rule.name}")
                return False
            
            # Check for conflicts
            if rule.id in self.rules:
                self.logger.warning(f"Rule {rule.id} already exists, updating")
            
            # Add/update rule
            self.rules[rule.id] = rule
            self.logger.info(f"Added business rule: {rule.name} (ID: {rule.id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding rule {rule.name}: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a business rule from the engine.
        
        Args:
            rule_id: ID of the rule to remove
            
        Returns:
            True if rule was removed successfully
        """
        try:
            if rule_id in self.rules:
                rule_name = self.rules[rule_id].name
                del self.rules[rule_id]
                self.logger.info(f"Removed business rule: {rule_name} (ID: {rule_id})")
                return True
            else:
                self.logger.warning(f"Rule {rule_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing rule {rule_id}: {e}")
            return False
    
    async def execute_rule(
        self,
        rule_name: str,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> RuleExecutionResult:
        """
        Execute a business rule.
        
        Args:
            rule_name: Name of the rule to execute
            rule_config: Rule configuration
            data: Input data for rule execution
            
        Returns:
            Rule execution result
        """
        start_time = datetime.now()
        
        # Find rule by name
        rule = self._find_rule_by_name(rule_name)
        if not rule:
            result = RuleExecutionResult(
                rule_id="unknown",
                rule_name=rule_name,
                status=RuleStatus.FAILED,
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                errors=[f"Rule '{rule_name}' not found"]
            )
            return result
        
        # Create execution result
        result = RuleExecutionResult(
            rule_id=rule.id,
            rule_name=rule.name,
            status=RuleStatus.RUNNING,
            start_time=start_time
        )
        
        try:
            # Check if rule is enabled
            if not rule.enabled:
                result.status = RuleStatus.SKIPPED
                result.success = True
                result.warnings.append("Rule is disabled")
                return result
            
            # Check dependencies
            if not await self._check_dependencies(rule, data):
                result.status = RuleStatus.FAILED
                result.success = False
                result.errors.append("Rule dependencies not met")
                return result
            
            # Check conditions
            if not await self._evaluate_conditions(rule.conditions, data):
                result.status = RuleStatus.SKIPPED
                result.success = True
                result.warnings.append("Rule conditions not met")
                return result
            
            # Execute rule
            executor = self._get_rule_executor(rule.rule_type)
            if executor:
                output = await executor(rule, rule_config, data)
                result.output = output
                result.success = True
                result.status = RuleStatus.COMPLETED
            else:
                result.status = RuleStatus.FAILED
                result.success = False
                result.errors.append(f"No executor found for rule type: {rule.rule_type.value}")
            
        except Exception as e:
            result.status = RuleStatus.FAILED
            result.success = False
            result.errors.append(f"Rule execution error: {str(e)}")
            self.logger.error(f"Error executing rule {rule.name}: {e}")
        
        finally:
            # Complete execution result
            result.end_time = datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            # Store in history
            self._store_execution_result(result)
        
        return result
    
    async def execute_rules_chain(
        self,
        rule_ids: List[str],
        data: Dict[str, Any],
        rule_configs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[RuleExecutionResult]:
        """
        Execute a chain of business rules in sequence.
        
        Args:
            rule_ids: List of rule IDs to execute
            data: Input data for rule execution
            rule_configs: Optional rule-specific configurations
            
        Returns:
            List of rule execution results
        """
        results = []
        current_data = data.copy()
        
        try:
            for rule_id in rule_ids:
                if rule_id not in self.rules:
                    self.logger.warning(f"Rule {rule_id} not found, skipping")
                    continue
                
                rule = self.rules[rule_id]
                rule_config = rule_configs.get(rule_id, {}) if rule_configs else {}
                
                # Execute rule
                result = await self.execute_rule(rule.name, rule_config, current_data)
                results.append(result)
                
                # Update data with rule output if successful
                if result.success and result.output:
                    current_data.update(result.output)
                
                # Stop chain if critical rule fails
                if not result.success and rule.priority == RulePriority.CRITICAL:
                    self.logger.warning(f"Critical rule {rule.name} failed, stopping chain")
                    break
            
        except Exception as e:
            self.logger.error(f"Error executing rules chain: {e}")
        
        return results
    
    def _validate_rule(self, rule: BusinessRule) -> bool:
        """Validate a business rule"""
        try:
            # Check required fields
            if not rule.id or not rule.name or not rule.rule_type:
                return False
            
            # Check rule definition
            if not rule.rule_definition:
                return False
            
            # Check conditions and actions
            if not rule.conditions or not rule.actions:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _find_rule_by_name(self, rule_name: str) -> Optional[BusinessRule]:
        """Find a rule by name"""
        for rule in self.rules.values():
            if rule.name == rule_name:
                return rule
        return None
    
    async def _check_dependencies(self, rule: BusinessRule, data: Dict[str, Any]) -> bool:
        """Check if rule dependencies are met"""
        try:
            for dependency in rule.dependencies:
                if dependency not in data:
                    self.logger.warning(f"Dependency {dependency} not found in data")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking dependencies: {e}")
            return False
    
    async def _evaluate_conditions(self, conditions: List[Dict[str, Any]], data: Dict[str, Any]) -> bool:
        """Evaluate rule conditions"""
        try:
            for condition in conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if field not in data:
                    return False
                
                field_value = data[field]
                
                # Evaluate condition
                if not self._evaluate_condition(field_value, operator, value):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {e}")
            return False
    
    def _evaluate_condition(self, field_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate a single condition"""
        try:
            if operator == '==':
                return field_value == expected_value
            elif operator == '!=':
                return field_value != expected_value
            elif operator == '>':
                return field_value > expected_value
            elif operator == '>=':
                return field_value >= expected_value
            elif operator == '<':
                return field_value < expected_value
            elif operator == '<=':
                return field_value <= expected_value
            elif operator == 'in':
                return field_value in expected_value
            elif operator == 'not_in':
                return field_value not in expected_value
            elif operator == 'contains':
                return expected_value in field_value
            elif operator == 'starts_with':
                return field_value.startswith(expected_value)
            elif operator == 'ends_with':
                return field_value.endswith(expected_value)
            else:
                self.logger.warning(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _get_rule_executor(self, rule_type: RuleType) -> Optional[Callable]:
        """Get the appropriate executor for a rule type"""
        executor_name = f"{rule_type.value}_rule"
        return self.rule_executors.get(executor_name)
    
    # Built-in rule executors
    async def _execute_validation_rule(
        self,
        rule: BusinessRule,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a validation rule"""
        try:
            # Apply validation logic based on rule definition
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Example: File size validation
            if 'max_file_size_mb' in rule.rule_definition:
                max_size = rule.rule_definition['max_file_size_mb']
                if 'file_size_mb' in data and data['file_size_mb'] > max_size:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"File size exceeds limit: {max_size}MB")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error executing validation rule: {e}")
            return {'valid': False, 'errors': [str(e)]}
    
    async def _execute_transformation_rule(
        self,
        rule: BusinessRule,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a transformation rule"""
        try:
            # Apply transformation logic
            transformed_data = data.copy()
            
            # Example: Data format transformation
            if 'format_transformations' in rule.rule_definition:
                for field, transformation in rule.rule_definition['format_transformations'].items():
                    if field in transformed_data:
                        if transformation == 'uppercase':
                            transformed_data[field] = str(transformed_data[field]).upper()
                        elif transformation == 'lowercase':
                            transformed_data[field] = str(transformed_data[field]).lower()
                        elif transformation == 'trim':
                            transformed_data[field] = str(transformed_data[field]).strip()
            
            return transformed_data
            
        except Exception as e:
            self.logger.error(f"Error executing transformation rule: {e}")
            return data
    
    async def _execute_decision_rule(
        self,
        rule: BusinessRule,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a decision rule"""
        try:
            # Apply decision logic
            decision_result = {
                'decision': 'approve',
                'reason': 'Default approval',
                'metadata': {}
            }
            
            # Example: Priority assignment
            if 'priority_mapping' in rule.rule_definition:
                priority_mapping = rule.rule_definition['priority_mapping']
                if 'job_type' in data:
                    job_type = data['job_type']
                    if job_type in priority_mapping.get('urgent', []):
                        decision_result['decision'] = 'high_priority'
                        decision_result['reason'] = f'Job type {job_type} requires urgent attention'
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Error executing decision rule: {e}")
            return {'decision': 'error', 'reason': str(e)}
    
    async def _execute_calculation_rule(
        self,
        rule: BusinessRule,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a calculation rule"""
        try:
            # Apply calculation logic
            calculation_result = {}
            
            # Example: Cost calculation
            if 'cost_calculation' in rule.rule_definition:
                base_cost = data.get('base_cost', 0)
                multiplier = rule.rule_definition['cost_calculation'].get('multiplier', 1.0)
                calculation_result['calculated_cost'] = base_cost * multiplier
            
            return calculation_result
            
        except Exception as e:
            self.logger.error(f"Error executing calculation rule: {e}")
            return {'error': str(e)}
    
    async def _execute_workflow_rule(
        self,
        rule: BusinessRule,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow rule"""
        try:
            # Apply workflow logic
            workflow_result = {
                'next_step': 'continue',
                'workflow_state': 'active',
                'actions_required': []
            }
            
            # Example: Approval workflow
            if 'approval_required' in rule.rule_definition:
                if data.get('data_sensitivity') == 'high':
                    workflow_result['next_step'] = 'require_approval'
                    workflow_result['actions_required'] = ['compliance_review', 'manager_approval']
            
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Error executing workflow rule: {e}")
            return {'error': str(e)}
    
    async def _execute_compliance_rule(
        self,
        rule: BusinessRule,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a compliance rule"""
        try:
            # Apply compliance logic
            compliance_result = {
                'compliant': True,
                'violations': [],
                'required_actions': []
            }
            
            # Example: Data retention compliance
            if 'retention_policy' in rule.rule_definition:
                retention_days = rule.rule_definition['retention_policy'].get('max_days', 365)
                if 'created_at' in data:
                    # Check if data exceeds retention period
                    # This is a simplified example
                    pass
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"Error executing compliance rule: {e}")
            return {'compliant': False, 'error': str(e)}
    
    def _store_execution_result(self, result: RuleExecutionResult):
        """Store rule execution result in history"""
        try:
            self.execution_history.append(result)
            
            # Enforce history limits
            if len(self.execution_history) > self.max_history:
                self.execution_history = self.execution_history[-self.max_history:]
                
        except Exception as e:
            self.logger.error(f"Error storing execution result: {e}")
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get business rules engine statistics"""
        return {
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled]),
            'disabled_rules': len([r for r in self.rules.values() if not r.enabled]),
            'rule_types': {rt.value: len([r for r in self.rules.values() if r.rule_type == rt]) for rt in RuleType},
            'execution_history_size': len(self.execution_history),
            'total_executors': len(self.rule_executors)
        }
    
    def get_rule_by_id(self, rule_id: str) -> Optional[BusinessRule]:
        """Get a rule by ID"""
        return self.rules.get(rule_id)
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[BusinessRule]:
        """Get all rules of a specific type"""
        return [r for r in self.rules.values() if r.rule_type == rule_type]
    
    def get_enabled_rules(self) -> List[BusinessRule]:
        """Get all enabled rules"""
        return [r for r in self.rules.values() if r.enabled]
