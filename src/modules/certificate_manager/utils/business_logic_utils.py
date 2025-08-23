"""
Business Logic Utilities

This module provides comprehensive business logic utilities for business rule management,
business metrics calculation, and business logic operations.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class BusinessRule(Enum):
    """Business rule types"""
    VALIDATION = "validation"
    CALCULATION = "calculation"
    TRANSFORMATION = "transformation"
    WORKFLOW = "workflow"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    SCHEDULING = "scheduling"
    ROUTING = "routing"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"


class BusinessMetric(Enum):
    """Business metric types"""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    RELIABILITY = "reliability"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"
    COST = "cost"
    REVENUE = "revenue"


@dataclass
class BusinessRuleConfig:
    """Configuration for business rules"""
    rule_type: BusinessRule = BusinessRule.VALIDATION
    priority: int = 1
    enabled: bool = True
    conditions: List[Dict[str, Any]] = None
    actions: List[Dict[str, Any]] = None
    timeout: int = 30
    retry_count: int = 3
    error_handling: str = "continue"


class BusinessLogicUtils:
    """
    Business logic utilities and management service
    
    Handles:
    - Business rule management and execution
    - Business metrics calculation and tracking
    - Business logic workflow orchestration
    - Rule-based decision making
    - Business process automation
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize the business logic utilities service"""
        self.business_rules = list(BusinessRule)
        self.business_metrics = list(BusinessMetric)
        
        # Business logic storage and metadata
        self.business_rules_config: Dict[str, Dict[str, Any]] = {}
        self.business_metrics_data: Dict[str, Dict[str, Any]] = {}
        self.business_logic_history: List[Dict[str, Any]] = []
        
        # Business logic locks and queues
        self.business_logic_locks: Dict[str, asyncio.Lock] = {}
        self.business_logic_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.business_logic_stats = {
            "total_rules_executed": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0.0,
            "total_metrics_calculated": 0
        }
        
        # Initialize default business rules
        self._initialize_default_rules()
        
        logger.info("Business logic utilities service initialized successfully")
    
    async def execute_business_rule(
        self,
        rule_name: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a business rule with the provided input data
        
        Args:
            rule_name: Name of the business rule to execute
            input_data: Input data for the rule
            context: Additional context for rule execution
            metadata: Additional metadata for the rule execution
            
        Returns:
            Dictionary containing rule execution results and metadata
        """
        start_time = time.time()
        rule_execution_id = f"rule_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_rule_execution_params(rule_name, input_data)
            
            # Get rule configuration
            rule_config = await self._get_business_rule_config(rule_name)
            
            # Prepare data for rule execution
            prepared_data = await self._prepare_data_for_rule_execution(input_data, rule_config)
            
            # Execute business rule
            rule_result = await self._execute_business_rule(prepared_data, rule_config, context)
            
            # Create metadata
            rule_metadata = await self._create_rule_execution_metadata(
                rule_execution_id, rule_name, input_data, rule_config, metadata
            )
            
            # Store rule execution results
            rule_execution_info = {
                "id": rule_execution_id,
                "rule_name": rule_name,
                "input_data": prepared_data,
                "rule_config": rule_config,
                "result": rule_result,
                "metadata": rule_metadata,
                "executed_at": time.time(),
                "execution_time": time.time() - start_time,
                "status": "success"
            }
            
            self.business_logic_history.append(rule_execution_info)
            
            # Update statistics
            await self._update_business_logic_stats(True, time.time() - start_time, 1)
            
            logger.info(f"Business rule executed successfully: {rule_execution_id}")
            return rule_execution_info
            
        except Exception as e:
            await self._update_business_logic_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to execute business rule: {str(e)}")
            raise
    
    async def execute_business_rules_batch(
        self,
        rules_data: List[Tuple[str, Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None,
        batch_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple business rules in batch
        
        Args:
            rules_data: List of tuples containing rule names and input data
            context: Additional context for rule execution
            batch_metadata: Additional metadata for the batch
            
        Returns:
            List of rule execution results
        """
        batch_id = f"batch_{int(time.time() * 1000)}"
        results = []
        
        logger.info(f"Starting batch business rule execution: {batch_id}")
        
        # Create tasks for concurrent rule execution
        tasks = []
        for i, (rule_name, input_data) in enumerate(rules_data):
            task = asyncio.create_task(
                self.execute_business_rule(rule_name, input_data, context, {
                    "batch_id": batch_id,
                    "batch_index": i,
                    **(batch_metadata or {})
                })
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to execute business rule {i} in batch {batch_id}: {str(result)}")
                results.append({
                    "id": f"failed_{batch_id}_{i}",
                    "status": "failed",
                    "error": str(result),
                    "batch_id": batch_id,
                    "batch_index": i
                })
            else:
                results.append(result)
        
        logger.info(f"Batch business rule execution completed: {batch_id}, {len(results)} results")
        return results
    
    async def calculate_business_metric(
        self,
        metric_name: str,
        data: Dict[str, Any],
        calculation_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate a business metric using the provided data
        
        Args:
            metric_name: Name of the business metric to calculate
            data: Data for metric calculation
            calculation_config: Configuration for metric calculation
            metadata: Additional metadata for the metric calculation
            
        Returns:
            Dictionary containing calculated metric and metadata
        """
        start_time = time.time()
        metric_calculation_id = f"metric_{int(time.time() * 1000)}"
        
        try:
            # Validate input parameters
            await self._validate_metric_calculation_params(metric_name, data)
            
            # Prepare data for metric calculation
            prepared_data = await self._prepare_data_for_metric_calculation(data, metric_name)
            
            # Calculate business metric
            metric_value = await self._calculate_business_metric(prepared_data, metric_name, calculation_config)
            
            # Create metadata
            metric_metadata = await self._create_metric_calculation_metadata(
                metric_calculation_id, metric_name, data, calculation_config, metadata
            )
            
            # Store metric calculation results
            metric_calculation_info = {
                "id": metric_calculation_id,
                "metric_name": metric_name,
                "input_data": prepared_data,
                "calculated_value": metric_value,
                "calculation_config": calculation_config,
                "metadata": metric_metadata,
                "calculated_at": time.time(),
                "calculation_time": time.time() - start_time,
                "status": "success"
            }
            
            self.business_metrics_data[metric_calculation_id] = metric_calculation_info
            self.business_logic_history.append(metric_calculation_info)
            
            # Update statistics
            await self._update_business_logic_stats(True, time.time() - start_time, 1)
            
            logger.info(f"Business metric calculated successfully: {metric_calculation_id}")
            return metric_calculation_info
            
        except Exception as e:
            await self._update_business_logic_stats(False, time.time() - start_time, 0)
            logger.error(f"Failed to calculate business metric: {str(e)}")
            raise
    
    async def create_business_rule(
        self,
        rule_name: str,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new business rule
        
        Args:
            rule_name: Name of the business rule
            rule_config: Rule configuration
            
        Returns:
            Rule creation result
        """
        if rule_name in self.business_rules_config:
            raise ValueError(f"Business rule already exists: {rule_name}")
        
        self.business_rules_config[rule_name] = rule_config
        
        return {
            "rule_name": rule_name,
            "config": rule_config,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def update_business_rule(
        self,
        rule_name: str,
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing business rule
        
        Args:
            rule_name: Name of the business rule to update
            rule_config: Updated rule configuration
            
        Returns:
            Rule update result
        """
        if rule_name not in self.business_rules_config:
            raise ValueError(f"Business rule not found: {rule_name}")
        
        self.business_rules_config[rule_name] = rule_config
        
        return {
            "rule_name": rule_name,
            "config": rule_config,
            "updated_at": time.time(),
            "status": "updated"
        }
    
    async def delete_business_rule(self, rule_name: str) -> Dict[str, Any]:
        """
        Delete a business rule
        
        Args:
            rule_name: Name of the business rule to delete
            
        Returns:
            Rule deletion result
        """
        if rule_name not in self.business_rules_config:
            raise ValueError(f"Business rule not found: {rule_name}")
        
        del self.business_rules_config[rule_name]
        
        return {
            "rule_name": rule_name,
            "deleted_at": time.time(),
            "status": "deleted"
        }
    
    async def get_business_rule_info(self, rule_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a business rule
        
        Args:
            rule_name: Name of the business rule
            
        Returns:
            Business rule information
        """
        if rule_name not in self.business_rules_config:
            raise ValueError(f"Business rule not found: {rule_name}")
        
        return self.business_rules_config[rule_name]
    
    async def list_business_rules(
        self,
        rule_type: Optional[BusinessRule] = None,
        enabled_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all business rules with optional filtering
        
        Args:
            rule_type: Filter by rule type
            enabled_only: Return only enabled rules
            
        Returns:
            List of business rules
        """
        rules = []
        
        for rule_name, rule_config in self.business_rules_config.items():
            if rule_type and rule_config.get("rule_type") != rule_type.value:
                continue
            
            if enabled_only and not rule_config.get("enabled", True):
                continue
            
            rules.append({
                "rule_name": rule_name,
                **rule_config
            })
        
        return rules
    
    async def get_business_logic_info(self, execution_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a business logic operation
        
        Args:
            execution_id: ID of the business logic operation
            
        Returns:
            Business logic operation information
        """
        for operation_info in self.business_logic_history:
            if operation_info.get("id") == execution_id:
                return operation_info
        
        raise ValueError(f"Business logic operation not found: {execution_id}")
    
    async def get_business_logic_history(
        self,
        rule_name: Optional[str] = None,
        rule_type: Optional[BusinessRule] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get business logic operation history
        
        Args:
            rule_name: Filter by rule name
            rule_type: Filter by rule type
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of business logic operation history entries
        """
        history = self.business_logic_history
        
        if rule_name:
            history = [h for h in history if h.get("rule_name") == rule_name]
        
        if rule_type:
            history = [h for h in history if h.get("rule_config", {}).get("rule_type") == rule_type.value]
        
        # Sort by execution time (newest first)
        history.sort(key=lambda x: x.get("executed_at", x.get("calculated_at", 0)), reverse=True)
        
        return history[offset:offset + limit]
    
    async def get_business_logic_statistics(self) -> Dict[str, Any]:
        """
        Get business logic operation statistics
        
        Returns:
            Business logic operation statistics
        """
        return self.business_logic_stats.copy()
    
    async def cleanup_expired_business_logic(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired business logic operations
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of operations cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_operations = []
        for operation_info in self.business_logic_history:
            operation_time = operation_info.get("executed_at", operation_info.get("calculated_at", 0))
            if current_time - operation_time > max_age_seconds:
                expired_operations.append(operation_info.get("id"))
        
        # Remove expired operations
        self.business_logic_history = [
            op for op in self.business_logic_history
            if op.get("id") not in expired_operations
        ]
        
        logger.info(f"Cleaned up {len(expired_operations)} expired business logic operations")
        return len(expired_operations)
    
    # Private helper methods
    
    def _initialize_default_rules(self):
        """Initialize default business rules"""
        # Certificate validation rule
        self.business_rules_config["certificate_validation"] = {
            "rule_type": "validation",
            "priority": 1,
            "enabled": True,
            "conditions": [
                {"field": "title", "operator": "required", "value": True},
                {"field": "content", "operator": "min_length", "value": 10},
                {"field": "signature", "operator": "required", "value": True}
            ],
            "actions": [
                {"action": "validate", "target": "certificate"},
                {"action": "log", "message": "Certificate validation completed"}
            ],
            "timeout": 30,
            "retry_count": 3,
            "error_handling": "continue"
        }
        
        # Performance calculation rule
        self.business_rules_config["performance_calculation"] = {
            "rule_type": "calculation",
            "priority": 2,
            "enabled": True,
            "conditions": [
                {"field": "metrics_data", "operator": "required", "value": True},
                {"field": "calculation_type", "operator": "in", "value": ["average", "sum", "max", "min"]}
            ],
            "actions": [
                {"action": "calculate", "target": "performance_metric"},
                {"action": "store", "target": "metrics_database"}
            ],
            "timeout": 60,
            "retry_count": 2,
            "error_handling": "retry"
        }
        
        # Workflow approval rule
        self.business_rules_config["workflow_approval"] = {
            "rule_type": "workflow",
            "priority": 3,
            "enabled": True,
            "conditions": [
                {"field": "approval_level", "operator": "required", "value": True},
                {"field": "approver_role", "operator": "in", "value": ["manager", "director", "admin"]}
            ],
            "actions": [
                {"action": "route", "target": "approval_workflow"},
                {"action": "notify", "target": "approver"}
            ],
            "timeout": 300,
            "retry_count": 1,
            "error_handling": "escalate"
        }
    
    async def _validate_rule_execution_params(
        self,
        rule_name: str,
        input_data: Dict[str, Any]
    ):
        """Validate rule execution parameters"""
        if not rule_name:
            raise ValueError("Rule name cannot be empty")
        
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary")
    
    async def _validate_metric_calculation_params(
        self,
        metric_name: str,
        data: Dict[str, Any]
    ):
        """Validate metric calculation parameters"""
        if not metric_name:
            raise ValueError("Metric name cannot be empty")
        
        if not data:
            raise ValueError("Data cannot be empty")
        
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
    
    async def _get_business_rule_config(self, rule_name: str) -> Dict[str, Any]:
        """Get business rule configuration"""
        if rule_name not in self.business_rules_config:
            raise ValueError(f"Business rule not found: {rule_name}")
        
        return self.business_rules_config[rule_name]
    
    async def _prepare_data_for_rule_execution(
        self,
        input_data: Dict[str, Any],
        rule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data for rule execution"""
        # Add rule context to input data
        prepared_data = input_data.copy()
        prepared_data["_rule_context"] = {
            "rule_name": rule_config.get("rule_name"),
            "rule_type": rule_config.get("rule_type"),
            "priority": rule_config.get("priority"),
            "timestamp": time.time()
        }
        return prepared_data
    
    async def _prepare_data_for_metric_calculation(
        self,
        data: Dict[str, Any],
        metric_name: str
    ) -> Dict[str, Any]:
        """Prepare data for metric calculation"""
        # Add metric context to data
        prepared_data = data.copy()
        prepared_data["_metric_context"] = {
            "metric_name": metric_name,
            "calculation_timestamp": time.time()
        }
        return prepared_data
    
    async def _execute_business_rule(
        self,
        data: Dict[str, Any],
        rule_config: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a business rule"""
        try:
            rule_type = rule_config.get("rule_type", "validation")
            
            if rule_type == "validation":
                return await self._execute_validation_rule(data, rule_config, context)
            elif rule_type == "calculation":
                return await self._execute_calculation_rule(data, rule_config, context)
            elif rule_type == "workflow":
                return await self._execute_workflow_rule(data, rule_config, context)
            else:
                return await self._execute_generic_rule(data, rule_config, context)
        
        except Exception as e:
            logger.error(f"Error executing business rule: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "rule_type": rule_type
            }
    
    async def _execute_validation_rule(
        self,
        data: Dict[str, Any],
        rule_config: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a validation rule"""
        conditions = rule_config.get("conditions", [])
        validation_results = []
        
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            expected_value = condition.get("value")
            
            if field in data:
                actual_value = data[field]
                is_valid = await self._evaluate_condition(actual_value, operator, expected_value)
                validation_results.append({
                    "field": field,
                    "operator": operator,
                    "expected_value": expected_value,
                    "actual_value": actual_value,
                    "is_valid": is_valid
                })
            else:
                validation_results.append({
                    "field": field,
                    "operator": operator,
                    "expected_value": expected_value,
                    "actual_value": None,
                    "is_valid": False,
                    "error": "Field not found"
                })
        
        overall_valid = all(r["is_valid"] for r in validation_results)
        
        return {
            "success": overall_valid,
            "rule_type": "validation",
            "validation_results": validation_results,
            "overall_valid": overall_valid
        }
    
    async def _execute_calculation_rule(
        self,
        data: Dict[str, Any],
        rule_config: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a calculation rule"""
        try:
            # Simulate calculation based on rule configuration
            calculation_result = {
                "success": True,
                "rule_type": "calculation",
                "calculated_value": f"CALCULATED_{data.get('calculation_type', 'default')}",
                "calculation_timestamp": time.time()
            }
            
            return calculation_result
        
        except Exception as e:
            return {
                "success": False,
                "rule_type": "calculation",
                "error": str(e)
            }
    
    async def _execute_workflow_rule(
        self,
        data: Dict[str, Any],
        rule_config: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a workflow rule"""
        try:
            # Simulate workflow execution based on rule configuration
            workflow_result = {
                "success": True,
                "rule_type": "workflow",
                "workflow_status": "initiated",
                "workflow_id": f"wf_{int(time.time() * 1000)}",
                "initiation_timestamp": time.time()
            }
            
            return workflow_result
        
        except Exception as e:
            return {
                "success": False,
                "rule_type": "workflow",
                "error": str(e)
            }
    
    async def _execute_generic_rule(
        self,
        data: Dict[str, Any],
        rule_config: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a generic rule"""
        try:
            # Simulate generic rule execution
            generic_result = {
                "success": True,
                "rule_type": "generic",
                "execution_timestamp": time.time(),
                "input_data_keys": list(data.keys())
            }
            
            return generic_result
        
        except Exception as e:
            return {
                "success": False,
                "rule_type": "generic",
                "error": str(e)
            }
    
    async def _evaluate_condition(
        self,
        actual_value: Any,
        operator: str,
        expected_value: Any
    ) -> bool:
        """Evaluate a condition"""
        try:
            if operator == "required":
                return actual_value is not None and actual_value != ""
            elif operator == "min_length":
                if isinstance(actual_value, (str, list, dict)):
                    return len(actual_value) >= expected_value
                return True
            elif operator == "max_length":
                if isinstance(actual_value, (str, list, dict)):
                    return len(actual_value) <= expected_value
                return True
            elif operator == "in":
                return actual_value in expected_value
            elif operator == "equals":
                return actual_value == expected_value
            elif operator == "greater_than":
                return actual_value > expected_value
            elif operator == "less_than":
                return actual_value < expected_value
            else:
                return True  # Unknown operator, assume valid
        
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False
    
    async def _calculate_business_metric(
        self,
        data: Dict[str, Any],
        metric_name: str,
        calculation_config: Optional[Dict[str, Any]]
    ) -> Any:
        """Calculate a business metric"""
        try:
            if metric_name == "performance":
                return await self._calculate_performance_metric(data, calculation_config)
            elif metric_name == "quality":
                return await self._calculate_quality_metric(data, calculation_config)
            elif metric_name == "efficiency":
                return await self._calculate_efficiency_metric(data, calculation_config)
            elif metric_name == "compliance":
                return await self._calculate_compliance_metric(data, calculation_config)
            else:
                return await self._calculate_generic_metric(data, metric_name, calculation_config)
        
        except Exception as e:
            logger.error(f"Error calculating business metric: {str(e)}")
            return f"CALCULATION_ERROR: {str(e)}"
    
    async def _calculate_performance_metric(
        self,
        data: Dict[str, Any],
        calculation_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate performance metric"""
        # Simulate performance calculation
        return {
            "metric_type": "performance",
            "value": 85.5,
            "unit": "percentage",
            "calculation_method": "weighted_average",
            "timestamp": time.time()
        }
    
    async def _calculate_quality_metric(
        self,
        data: Dict[str, Any],
        calculation_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate quality metric"""
        # Simulate quality calculation
        return {
            "metric_type": "quality",
            "value": 92.3,
            "unit": "score",
            "calculation_method": "quality_assessment",
            "timestamp": time.time()
        }
    
    async def _calculate_efficiency_metric(
        self,
        data: Dict[str, Any],
        calculation_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate efficiency metric"""
        # Simulate efficiency calculation
        return {
            "metric_type": "efficiency",
            "value": 78.9,
            "unit": "percentage",
            "calculation_method": "resource_utilization",
            "timestamp": time.time()
        }
    
    async def _calculate_compliance_metric(
        self,
        data: Dict[str, Any],
        calculation_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate compliance metric"""
        # Simulate compliance calculation
        return {
            "metric_type": "compliance",
            "value": 96.7,
            "unit": "percentage",
            "calculation_method": "compliance_check",
            "timestamp": time.time()
        }
    
    async def _calculate_generic_metric(
        self,
        data: Dict[str, Any],
        metric_name: str,
        calculation_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate generic metric"""
        # Simulate generic metric calculation
        return {
            "metric_type": metric_name,
            "value": f"GENERIC_{metric_name.upper()}",
            "unit": "custom",
            "calculation_method": "generic",
            "timestamp": time.time()
        }
    
    async def _create_rule_execution_metadata(
        self,
        rule_execution_id: str,
        rule_name: str,
        input_data: Dict[str, Any],
        rule_config: Dict[str, Any],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for rule execution operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "rule_name": rule_name,
            "rule_type": rule_config.get("rule_type"),
            "priority": rule_config.get("priority"),
            "config_hash": hash(str(rule_config)),
            "data_hash": hash(str(input_data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _create_metric_calculation_metadata(
        self,
        metric_calculation_id: str,
        metric_name: str,
        data: Dict[str, Any],
        calculation_config: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create metadata for metric calculation operations"""
        base_metadata = {
            "generator": "CertificateManager",
            "version": "1.0.0",
            "metric_name": metric_name,
            "calculation_config_hash": hash(str(calculation_config)) if calculation_config else 0,
            "data_hash": hash(str(data)),
            "timestamp": time.time()
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def _update_business_logic_stats(self, success: bool, execution_time: float, operations_count: int):
        """Update business logic statistics"""
        self.business_logic_stats["total_rules_executed"] += operations_count
        
        if success:
            self.business_logic_stats["successful"] += operations_count
        else:
            self.business_logic_stats["failed"] += operations_count
        
        # Update average execution time
        total_successful = self.business_logic_stats["successful"]
        if total_successful > 0:
            current_avg = self.business_logic_stats["average_time"]
            self.business_logic_stats["average_time"] = (
                (current_avg * (total_successful - operations_count) + execution_time) / total_successful
            )
