"""
Validation Processor
===================

Data validation utilities for federated learning.
Handles data quality checks, schema validation, and integrity verification.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class ValidationRule:
    """Individual validation rule configuration"""
    name: str
    field_path: str  # Dot notation for nested fields
    rule_type: str  # required, type, range, pattern, custom
    parameters: Dict[str, Any] = None
    error_message: str = ""
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationConfig:
    """Configuration for data validation"""
    # Validation modes
    strict_mode: bool = True
    stop_on_first_error: bool = False
    include_warnings: bool = True
    
    # Rule sets
    predefined_rules: List[ValidationRule] = None
    custom_rules: List[ValidationRule] = None
    
    # Performance settings
    batch_validation: bool = True
    batch_size: int = 1000
    parallel_validation: bool = True
    
    # Output settings
    detailed_reports: bool = True
    save_validation_logs: bool = True


@dataclass
class ValidationMetrics:
    """Metrics for validation performance"""
    # Validation statistics
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    warning_records: int = 0
    
    # Rule statistics
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    warning_rules: int = 0
    
    # Performance metrics
    validation_time: float = 0.0
    avg_validation_time_per_record: float = 0.0
    memory_usage_mb: float = 0.0
    
    # Quality metrics
    overall_quality_score: float = 0.0
    data_integrity_score: float = 0.0


class ValidationProcessor:
    """Data validation implementation for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[ValidationConfig] = None
    ):
        """Initialize Validation Processor"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or ValidationConfig()
        
        # Initialize default rules if not provided
        if self.config.predefined_rules is None:
            self.config.predefined_rules = self._get_default_validation_rules()
        
        # Validation state
        self.is_validating = False
        self.current_dataset = None
        self.validation_history: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = ValidationMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        
        # Rule registry
        self.rule_registry: Dict[str, Callable] = self._register_validation_rules()
    
    async def validate_dataset(
        self,
        dataset: Union[np.ndarray, List[Dict[str, Any]], Dict[str, Any]],
        dataset_name: str = "unknown",
        custom_rules: Optional[List[ValidationRule]] = None
    ) -> Dict[str, Any]:
        """Validate a dataset using configured rules"""
        try:
            self.start_time = datetime.now()
            self.is_validating = True
            self.current_dataset = dataset_name
            
            print(f"🔍 Starting data validation for: {dataset_name}")
            
            # Prepare dataset for validation
            prepared_data = await self._prepare_data_for_validation(dataset)
            
            # Update metrics
            self.metrics.total_records = len(prepared_data)
            self.metrics.total_rules = len(self.config.predefined_rules)
            
            # Add custom rules if provided
            if custom_rules:
                self.metrics.total_rules += len(custom_rules)
                all_rules = self.config.predefined_rules + custom_rules
            else:
                all_rules = self.config.predefined_rules
            
            # Perform validation
            validation_results = await self._execute_validation(prepared_data, all_rules)
            
            # Process validation results
            processed_results = await self._process_validation_results(validation_results)
            
            # Calculate final metrics
            await self._calculate_final_metrics(processed_results)
            
            # Calculate validation time
            validation_time = (datetime.now() - self.start_time).total_seconds()
            self.metrics.validation_time = validation_time
            self.metrics.avg_validation_time_per_record = validation_time / max(1, self.metrics.total_records)
            
            # Record validation history
            self.validation_history.append({
                'dataset_name': dataset_name,
                'timestamp': datetime.now().isoformat(),
                'results': processed_results,
                'metrics': self.metrics.__dict__,
                'config': self.config.__dict__
            })
            
            print(f"✅ Data validation completed in {validation_time:.2f}s")
            
            return {
                'status': 'success',
                'dataset_name': dataset_name,
                'validation_results': processed_results,
                'metrics': self.metrics.__dict__,
                'validation_time': validation_time
            }
            
        except Exception as e:
            print(f"❌ Data validation failed: {e}")
            return {'status': 'failed', 'error': str(e)}
        finally:
            self.is_validating = False
    
    async def _prepare_data_for_validation(
        self,
        dataset: Union[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prepare dataset in a format suitable for validation"""
        try:
            if isinstance(dataset, np.ndarray):
                # Convert numpy array to list of dicts
                return [{'value': row.tolist()} for row in dataset]
            elif isinstance(dataset, list):
                # Ensure list contains dictionaries
                if dataset and isinstance(dataset[0], dict):
                    return dataset
                else:
                    return [{'value': item} for item in dataset]
            elif isinstance(dataset, dict):
                # Convert dict to list with single item
                return [dataset]
            else:
                raise ValueError(f"Unsupported dataset type: {type(dataset)}")
                
        except Exception as e:
            print(f"❌ Data preparation for validation failed: {e}")
            raise
    
    async def _execute_validation(
        self,
        data: List[Dict[str, Any]],
        rules: List[ValidationRule]
    ) -> List[Dict[str, Any]]:
        """Execute validation rules on the dataset"""
        try:
            validation_results = []
            
            if self.config.batch_validation:
                # Process in batches
                for i in range(0, len(data), self.config.batch_size):
                    batch = data[i:i + self.config.batch_size]
                    batch_results = await self._validate_batch(batch, rules)
                    validation_results.extend(batch_results)
            else:
                # Process all records at once
                validation_results = await self._validate_batch(data, rules)
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Validation execution failed: {e}")
            raise
    
    async def _validate_batch(
        self,
        batch: List[Dict[str, Any]],
        rules: List[ValidationRule]
    ) -> List[Dict[str, Any]]:
        """Validate a batch of records"""
        try:
            batch_results = []
            
            for record_index, record in enumerate(batch):
                record_results = {
                    'record_index': record_index,
                    'record_data': record,
                    'rule_results': [],
                    'is_valid': True,
                    'errors': [],
                    'warnings': []
                }
                
                # Apply each validation rule
                for rule in rules:
                    rule_result = await self._apply_validation_rule(record, rule)
                    record_results['rule_results'].append(rule_result)
                    
                    # Update record validity
                    if rule_result['status'] == 'failed':
                        record_results['is_valid'] = False
                        record_results['errors'].append(rule_result)
                        if self.config.strict_mode and self.config.stop_on_first_error:
                            break
                    elif rule_result['status'] == 'warning':
                        record_results['warnings'].append(rule_result)
                
                batch_results.append(record_results)
            
            return batch_results
            
        except Exception as e:
            print(f"❌ Batch validation failed: {e}")
            raise
    
    async def _apply_validation_rule(
        self,
        record: Dict[str, Any],
        rule: ValidationRule
    ) -> Dict[str, Any]:
        """Apply a single validation rule to a record"""
        try:
            # Extract field value using dot notation
            field_value = self._extract_field_value(record, rule.field_path)
            
            # Get validation function
            validation_func = self.rule_registry.get(rule.rule_type)
            if not validation_func:
                return {
                    'rule_name': rule.name,
                    'status': 'error',
                    'message': f"Unknown validation rule type: {rule.rule_type}",
                    'field_path': rule.field_path,
                    'field_value': field_value
                }
            
            # Execute validation
            validation_result = await validation_func(field_value, rule.parameters or {})
            
            # Format result
            return {
                'rule_name': rule.name,
                'status': validation_result['status'],
                'message': validation_result.get('message', rule.error_message),
                'field_path': rule.field_path,
                'field_value': field_value,
                'severity': rule.severity
            }
            
        except Exception as e:
            return {
                'rule_name': rule.name,
                'status': 'error',
                'message': f"Validation rule execution failed: {str(e)}",
                'field_path': rule.field_path,
                'field_value': None
            }
    
    def _extract_field_value(self, record: Dict[str, Any], field_path: str) -> Any:
        """Extract field value using dot notation"""
        try:
            if '.' not in field_path:
                return record.get(field_path)
            
            current = record
            for part in field_path.split('.'):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            
            return current
            
        except Exception as e:
            print(f"⚠️  Field extraction failed: {e}")
            return None
    
    async def _process_validation_results(
        self,
        validation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process and summarize validation results"""
        try:
            summary = {
                'total_records': len(validation_results),
                'valid_records': 0,
                'invalid_records': 0,
                'warning_records': 0,
                'error_details': [],
                'warning_details': [],
                'quality_metrics': {}
            }
            
            for result in validation_results:
                if result['is_valid']:
                    summary['valid_records'] += 1
                else:
                    summary['invalid_records'] += 1
                
                # Collect errors and warnings
                for error in result['errors']:
                    summary['error_details'].append({
                        'record_index': result['record_index'],
                        'rule_name': error['rule_name'],
                        'message': error['message'],
                        'field_path': error['field_path']
                    })
                
                for warning in result['warnings']:
                    summary['warning_details'].append({
                        'record_index': result['record_index'],
                        'rule_name': warning['rule_name'],
                        'message': warning['message'],
                        'field_path': warning['field_path']
                    })
            
            # Calculate quality metrics
            summary['quality_metrics'] = {
                'completeness': summary['valid_records'] / max(1, summary['total_records']),
                'error_rate': summary['invalid_records'] / max(1, summary['total_records']),
                'warning_rate': summary['warning_records'] / max(1, summary['total_records'])
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Validation results processing failed: {e}")
            raise
    
    async def _calculate_final_metrics(self, processed_results: Dict[str, Any]):
        """Calculate final validation metrics"""
        try:
            self.metrics.valid_records = processed_results['valid_records']
            self.metrics.invalid_records = processed_results['invalid_records']
            self.metrics.warning_records = processed_results['warning_records']
            
            # Calculate quality scores
            self.metrics.overall_quality_score = processed_results['quality_metrics']['completeness']
            self.metrics.data_integrity_score = 1.0 - processed_results['quality_metrics']['error_rate']
            
            # Update rule statistics
            self.metrics.passed_rules = self.metrics.total_rules * self.metrics.valid_records
            self.metrics.failed_rules = len(processed_results['error_details'])
            self.metrics.warning_rules = len(processed_results['warning_details'])
            
        except Exception as e:
            print(f"⚠️  Final metrics calculation failed: {e}")
    
    def _get_default_validation_rules(self) -> List[ValidationRule]:
        """Get default validation rules"""
        return [
            ValidationRule(
                name="required_field",
                field_path="value",
                rule_type="required",
                error_message="Field is required"
            ),
            ValidationRule(
                name="numeric_type",
                field_path="value",
                rule_type="type",
                parameters={"expected_type": "numeric"},
                error_message="Field must be numeric"
            ),
            ValidationRule(
                name="value_range",
                field_path="value",
                rule_type="range",
                parameters={"min": -1000, "max": 1000},
                error_message="Value must be between -1000 and 1000"
            )
        ]
    
    def _register_validation_rules(self) -> Dict[str, Callable]:
        """Register validation rule functions"""
        return {
            'required': self._validate_required,
            'type': self._validate_type,
            'range': self._validate_range,
            'pattern': self._validate_pattern,
            'custom': self._validate_custom
        }
    
    async def _validate_required(self, value: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that a field is required (not None/empty)"""
        try:
            is_valid = value is not None and value != ""
            
            if isinstance(value, (list, np.ndarray)):
                is_valid = len(value) > 0
            
            return {
                'status': 'passed' if is_valid else 'failed',
                'message': 'Field is present' if is_valid else 'Field is required'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _validate_type(self, value: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate field type"""
        try:
            expected_type = parameters.get('expected_type', 'any')
            
            if expected_type == 'numeric':
                is_valid = isinstance(value, (int, float, np.number))
            elif expected_type == 'string':
                is_valid = isinstance(value, str)
            elif expected_type == 'list':
                is_valid = isinstance(value, (list, np.ndarray))
            elif expected_type == 'dict':
                is_valid = isinstance(value, dict)
            else:
                is_valid = True  # Any type is valid
            
            return {
                'status': 'passed' if is_valid else 'failed',
                'message': f'Type validation passed' if is_valid else f'Expected {expected_type}, got {type(value).__name__}'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _validate_range(self, value: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate value range"""
        try:
            if not isinstance(value, (int, float, np.number)):
                return {'status': 'failed', 'message': 'Value must be numeric for range validation'}
            
            min_val = parameters.get('min', float('-inf'))
            max_val = parameters.get('max', float('inf'))
            
            is_valid = min_val <= value <= max_val
            
            return {
                'status': 'passed' if is_valid else 'failed',
                'message': f'Value {value} is within range [{min_val}, {max_val}]' if is_valid else f'Value {value} is outside range [{min_val}, {max_val}]'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _validate_pattern(self, value: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pattern matching (for strings)"""
        try:
            if not isinstance(value, str):
                return {'status': 'failed', 'message': 'Pattern validation only applies to strings'}
            
            import re
            pattern = parameters.get('pattern', '.*')
            
            is_valid = bool(re.match(pattern, value))
            
            return {
                'status': 'passed' if is_valid else 'failed',
                'message': f'String matches pattern {pattern}' if is_valid else f'String does not match pattern {pattern}'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _validate_custom(self, value: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using custom validation function"""
        try:
            custom_func = parameters.get('validation_function')
            if not callable(custom_func):
                return {'status': 'error', 'message': 'Custom validation function not provided'}
            
            # Execute custom validation
            result = custom_func(value, parameters)
            
            if isinstance(result, dict):
                return result
            elif isinstance(result, bool):
                return {
                    'status': 'passed' if result else 'failed',
                    'message': 'Custom validation passed' if result else 'Custom validation failed'
                }
            else:
                return {'status': 'error', 'message': 'Invalid custom validation result'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report"""
        try:
            return {
                'validation_metrics': self.metrics.__dict__,
                'validation_history': self.validation_history,
                'current_config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Validation report generation failed: {e}")
            return {'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'ValidationProcessor',
            'is_validating': self.is_validating,
            'current_dataset': self.current_dataset,
            'metrics': self.metrics.__dict__,
            'config': self.config.__dict__
        }
    
    async def reset_processor(self):
        """Reset processor state and metrics"""
        self.is_validating = False
        self.current_dataset = None
        self.validation_history.clear()
        self.metrics = ValidationMetrics()
        self.start_time = None
        
        print("🔄 Validation Processor reset")
