"""
Validation Utilities
==================

Data and model validation utility functions for federated learning.
Handles schema validation, data quality checks, and model verification.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class ValidationConfig:
    """Configuration for validation utilities"""
    # Validation methods
    schema_validation_enabled: bool = True
    data_quality_validation_enabled: bool = True
    model_validation_enabled: bool = True
    cross_validation_enabled: bool = True
    
    # Schema validation settings
    strict_schema_checking: bool = True
    allow_extra_fields: bool = False
    allow_missing_fields: bool = False
    
    # Data quality settings
    min_completeness: float = 0.8
    max_outlier_percentage: float = 0.1
    min_data_points: int = 10
    
    # Model validation settings
    min_accuracy: float = 0.5
    max_loss: float = 10.0
    convergence_threshold: float = 0.001
    
    # Cross validation settings
    cv_folds: int = 5
    cv_strategy: str = "stratified"  # stratified, kfold, timeseries


@dataclass
class ValidationMetrics:
    """Metrics for validation operations"""
    # Validation results
    validation_passed: bool = False
    validation_score: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    
    # Schema validation metrics
    schema_errors: List[str] = None
    field_validation_results: Dict[str, bool] = None
    
    # Data quality metrics
    completeness_score: float = 0.0
    outlier_percentage: float = 0.0
    data_distribution_score: float = 0.0
    
    # Model validation metrics
    model_accuracy: float = 0.0
    model_loss: float = 0.0
    convergence_status: str = "unknown"
    
    # Performance metrics
    validation_time: float = 0.0
    memory_usage_mb: float = 0.0
    
    def __post_init__(self):
        if self.schema_errors is None:
            self.schema_errors = []
        if self.field_validation_results is None:
            self.field_validation_results = {}


class ValidationUtils:
    """Validation utility functions for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[ValidationConfig] = None
    ):
        """Initialize Validation Utils"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or ValidationConfig()
        
        # Validation state
        self.validation_history: List[Dict[str, Any]] = []
        self.custom_validators: Dict[str, Callable] = {}
        
        # Metrics tracking
        self.metrics = ValidationMetrics()
        
    async def validate_data(
        self,
        data: Union[List[Dict[str, Any]], np.ndarray, Dict[str, Any]],
        schema: Dict[str, Any] = None,
        validation_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Validate data according to specified criteria"""
        try:
            start_time = datetime.now()
            
            print(f"🔍 Starting {validation_type} data validation...")
            
            validation_results = {
                'validation_type': validation_type,
                'timestamp': datetime.now().isoformat(),
                'schema_validation': {},
                'quality_validation': {},
                'overall_result': False
            }
            
            # Schema validation
            if self.config.schema_validation_enabled and schema:
                schema_results = await self._validate_schema(data, schema)
                validation_results['schema_validation'] = schema_results
            
            # Data quality validation
            if self.config.data_quality_validation_enabled:
                quality_results = await self._validate_data_quality(data)
                validation_results['quality_validation'] = quality_results
            
            # Determine overall result
            overall_passed = True
            if 'schema_validation' in validation_results:
                overall_passed &= validation_results['schema_validation'].get('passed', True)
            if 'quality_validation' in validation_results:
                overall_passed &= validation_results['quality_validation'].get('passed', True)
            
            validation_results['overall_result'] = overall_passed
            
            # Update metrics
            await self._update_validation_metrics(validation_results, start_time)
            
            # Record validation history
            self.validation_history.append(validation_results)
            
            print(f"✅ Data validation completed: {'PASSED' if overall_passed else 'FAILED'}")
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Data validation failed: {e}")
            return {'error': str(e), 'overall_result': False}
    
    async def _validate_schema(
        self,
        data: Union[List[Dict[str, Any]], np.ndarray, Dict[str, Any]],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data against schema definition"""
        try:
            schema_results = {
                'passed': True,
                'errors': [],
                'field_results': {},
                'summary': {}
            }
            
            if isinstance(data, list):
                # Validate list of dictionaries
                for i, item in enumerate(data):
                    item_results = await self._validate_schema_item(item, schema, f"item_{i}")
                    schema_results['field_results'][f"item_{i}"] = item_results
                    
                    if not item_results['passed']:
                        schema_results['passed'] = False
                        schema_results['errors'].extend(item_results['errors'])
            
            elif isinstance(data, dict):
                # Validate single dictionary
                item_results = await self._validate_schema_item(data, schema, "root")
                schema_results['field_results']['root'] = item_results
                schema_results['passed'] = item_results['passed']
                schema_results['errors'] = item_results['errors']
            
            elif isinstance(data, np.ndarray):
                # Validate numpy array
                array_results = await self._validate_numpy_array(data, schema)
                schema_results['field_results']['array'] = array_results
                schema_results['passed'] = array_results['passed']
                schema_results['errors'] = array_results['errors']
            
            # Generate summary
            schema_results['summary'] = {
                'total_fields': len(schema_results['field_results']),
                'passed_fields': sum(1 for r in schema_results['field_results'].values() if r['passed']),
                'error_count': len(schema_results['errors'])
            }
            
            return schema_results
            
        except Exception as e:
            print(f"❌ Schema validation failed: {e}")
            return {'passed': False, 'errors': [str(e)], 'field_results': {}, 'summary': {}}
    
    async def _validate_schema_item(
        self,
        item: Dict[str, Any],
        schema: Dict[str, Any],
        item_name: str
    ) -> Dict[str, Any]:
        """Validate a single schema item"""
        try:
            item_results = {
                'passed': True,
                'errors': [],
                'field_validation': {}
            }
            
            # Check required fields
            for field_name, field_spec in schema.items():
                field_required = field_spec.get('required', True)
                field_type = field_spec.get('type')
                field_constraints = field_spec.get('constraints', {})
                
                # Check if field exists
                if field_name not in item:
                    if field_required:
                        error_msg = f"Required field '{field_name}' missing in {item_name}"
                        item_results['errors'].append(error_msg)
                        item_results['passed'] = False
                    continue
                
                # Validate field value
                field_value = item[field_name]
                field_validation = await self._validate_field_value(
                    field_value, field_type, field_constraints, field_name
                )
                
                item_results['field_validation'][field_name] = field_validation
                
                if not field_validation['passed']:
                    item_results['passed'] = False
                    item_results['errors'].extend(field_validation['errors'])
            
            # Check for extra fields
            if not self.config.allow_extra_fields:
                for field_name in item:
                    if field_name not in schema:
                        error_msg = f"Extra field '{field_name}' not allowed in schema"
                        item_results['errors'].append(error_msg)
                        item_results['passed'] = False
            
            return item_results
            
        except Exception as e:
            print(f"❌ Schema item validation failed: {e}")
            return {'passed': False, 'errors': [str(e)], 'field_validation': {}}
    
    async def _validate_field_value(
        self,
        value: Any,
        expected_type: str,
        constraints: Dict[str, Any],
        field_name: str
    ) -> Dict[str, Any]:
        """Validate a single field value"""
        try:
            field_results = {
                'passed': True,
                'errors': [],
                'value_type': type(value).__name__,
                'constraints_checked': []
            }
            
            # Type validation
            if expected_type:
                type_valid = await self._check_type_compatibility(value, expected_type)
                if not type_valid:
                    error_msg = f"Field '{field_name}' expected type {expected_type}, got {type(value).__name__}"
                    field_results['errors'].append(error_msg)
                    field_results['passed'] = False
            
            # Constraint validation
            for constraint_name, constraint_value in constraints.items():
                constraint_passed = await self._check_constraint(value, constraint_name, constraint_value)
                field_results['constraints_checked'].append(constraint_name)
                
                if not constraint_passed:
                    error_msg = f"Field '{field_name}' failed constraint {constraint_name}: {constraint_value}"
                    field_results['errors'].append(error_msg)
                    field_results['passed'] = False
            
            return field_results
            
        except Exception as e:
            print(f"❌ Field value validation failed: {e}")
            return {'passed': False, 'errors': [str(e)], 'value_type': 'unknown', 'constraints_checked': []}
    
    async def _check_type_compatibility(self, value: Any, expected_type: str) -> bool:
        """Check if value is compatible with expected type"""
        try:
            if expected_type == 'string':
                return isinstance(value, str)
            elif expected_type == 'integer':
                return isinstance(value, int) and not isinstance(value, bool)
            elif expected_type == 'float':
                return isinstance(value, (int, float)) and not isinstance(value, bool)
            elif expected_type == 'boolean':
                return isinstance(value, bool)
            elif expected_type == 'array':
                return isinstance(value, (list, np.ndarray))
            elif expected_type == 'object':
                return isinstance(value, dict)
            else:
                return True  # Unknown type, assume valid
                
        except Exception as e:
            print(f"⚠️  Type compatibility check failed: {e}")
            return False
    
    async def _check_constraint(self, value: Any, constraint_name: str, constraint_value: Any) -> bool:
        """Check if value satisfies a constraint"""
        try:
            if constraint_name == 'min':
                return value >= constraint_value
            elif constraint_name == 'max':
                return value <= constraint_value
            elif constraint_name == 'min_length':
                return len(value) >= constraint_value
            elif constraint_name == 'max_length':
                return len(value) <= constraint_value
            elif constraint_name == 'pattern':
                import re
                return bool(re.match(constraint_value, str(value)))
            elif constraint_name == 'enum':
                return value in constraint_value
            elif constraint_name == 'custom':
                # Custom validator function
                if constraint_value in self.custom_validators:
                    return await self.custom_validators[constraint_value](value)
                return True
            else:
                return True  # Unknown constraint, assume valid
                
        except Exception as e:
            print(f"⚠️  Constraint check failed: {e}")
            return False
    
    async def _validate_numpy_array(
        self,
        array: np.ndarray,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate numpy array against schema"""
        try:
            array_results = {
                'passed': True,
                'errors': [],
                'array_info': {}
            }
            
            # Check array shape
            if 'shape' in schema:
                expected_shape = schema['shape']
                if array.shape != expected_shape:
                    error_msg = f"Array shape mismatch: expected {expected_shape}, got {array.shape}"
                    array_results['errors'].append(error_msg)
                    array_results['passed'] = False
            
            # Check data type
            if 'dtype' in schema:
                expected_dtype = schema['dtype']
                if str(array.dtype) != expected_dtype:
                    error_msg = f"Array dtype mismatch: expected {expected_dtype}, got {array.dtype}"
                    array_results['errors'].append(error_msg)
                    array_results['passed'] = False
            
            # Check value range
            if 'min_value' in schema or 'max_value' in schema:
                min_val = schema.get('min_value', -np.inf)
                max_val = schema.get('max_value', np.inf)
                
                if np.any(array < min_val) or np.any(array > max_val):
                    error_msg = f"Array values outside range [{min_val}, {max_val}]"
                    array_results['errors'].append(error_msg)
                    array_results['passed'] = False
            
            # Store array information
            array_results['array_info'] = {
                'shape': array.shape,
                'dtype': str(array.dtype),
                'size': array.size,
                'min_value': float(np.min(array)),
                'max_value': float(np.max(array)),
                'mean_value': float(np.mean(array)),
                'std_value': float(np.std(array))
            }
            
            return array_results
            
        except Exception as e:
            print(f"❌ Numpy array validation failed: {e}")
            return {'passed': False, 'errors': [str(e)], 'array_info': {}}
    
    async def _validate_data_quality(self, data: Union[List[Dict[str, Any]], np.ndarray, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data quality metrics"""
        try:
            quality_results = {
                'passed': True,
                'completeness_score': 0.0,
                'outlier_percentage': 0.0,
                'distribution_score': 0.0,
                'quality_metrics': {}
            }
            
            if isinstance(data, list):
                # Validate list of dictionaries
                quality_results = await self._validate_list_quality(data)
            elif isinstance(data, np.ndarray):
                # Validate numpy array
                quality_results = await self._validate_array_quality(data)
            elif isinstance(data, dict):
                # Validate single dictionary
                quality_results = await self._validate_dict_quality(data)
            
            # Check quality thresholds
            if quality_results['completeness_score'] < self.config.min_completeness:
                quality_results['passed'] = False
                quality_results['errors'] = [f"Completeness score {quality_results['completeness_score']:.2f} below threshold {self.config.min_completeness}"]
            
            if quality_results['outlier_percentage'] > self.config.max_outlier_percentage:
                quality_results['passed'] = False
                if 'errors' not in quality_results:
                    quality_results['errors'] = []
                quality_results['errors'].append(f"Outlier percentage {quality_results['outlier_percentage']:.2f} above threshold {self.config.max_outlier_percentage}")
            
            return quality_results
            
        except Exception as e:
            print(f"❌ Data quality validation failed: {e}")
            return {'passed': False, 'error': str(e)}
    
    async def _validate_list_quality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate quality of list data"""
        try:
            if not data:
                return {'passed': False, 'error': 'Empty data list'}
            
            # Calculate completeness
            total_fields = len(data[0]) if data else 0
            missing_fields = 0
            
            for item in data:
                for value in item.values():
                    if value is None or value == "":
                        missing_fields += 1
            
            completeness_score = 1.0 - (missing_fields / (len(data) * total_fields)) if total_fields > 0 else 0.0
            
            # Calculate outlier percentage (simplified)
            outlier_percentage = 0.05  # Placeholder
            
            # Calculate distribution score
            distribution_score = 0.8  # Placeholder
            
            return {
                'passed': True,
                'completeness_score': completeness_score,
                'outlier_percentage': outlier_percentage,
                'distribution_score': distribution_score,
                'quality_metrics': {
                    'total_records': len(data),
                    'total_fields': total_fields,
                    'missing_fields': missing_fields
                }
            }
            
        except Exception as e:
            print(f"❌ List quality validation failed: {e}")
            return {'passed': False, 'error': str(e)}
    
    async def _validate_array_quality(self, array: np.ndarray) -> Dict[str, Any]:
        """Validate quality of numpy array"""
        try:
            if array.size == 0:
                return {'passed': False, 'error': 'Empty array'}
            
            # Calculate completeness (non-NaN values)
            completeness_score = 1.0 - (np.isnan(array).sum() / array.size)
            
            # Calculate outlier percentage using IQR method
            if array.size > 0:
                q1 = np.percentile(array, 25)
                q3 = np.percentile(array, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = np.sum((array < lower_bound) | (array > upper_bound))
                outlier_percentage = outliers / array.size
            else:
                outlier_percentage = 0.0
            
            # Calculate distribution score (coefficient of variation)
            if np.mean(array) != 0:
                distribution_score = 1.0 / (1.0 + np.std(array) / np.mean(array))
            else:
                distribution_score = 0.0
            
            return {
                'passed': True,
                'completeness_score': completeness_score,
                'outlier_percentage': outlier_percentage,
                'distribution_score': distribution_score,
                'quality_metrics': {
                    'array_size': array.size,
                    'array_shape': array.shape,
                    'data_type': str(array.dtype),
                    'min_value': float(np.min(array)),
                    'max_value': float(np.max(array)),
                    'mean_value': float(np.mean(array)),
                    'std_value': float(np.std(array))
                }
            }
            
        except Exception as e:
            print(f"❌ Array quality validation failed: {e}")
            return {'passed': False, 'error': str(e)}
    
    async def _validate_dict_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of dictionary data"""
        try:
            if not data:
                return {'passed': False, 'error': 'Empty dictionary'}
            
            # Calculate completeness
            total_fields = len(data)
            missing_fields = sum(1 for value in data.values() if value is None or value == "")
            completeness_score = 1.0 - (missing_fields / total_fields) if total_fields > 0 else 0.0
            
            # For single dict, set outlier and distribution scores to defaults
            outlier_percentage = 0.0
            distribution_score = 1.0
            
            return {
                'passed': True,
                'completeness_score': completeness_score,
                'outlier_percentage': outlier_percentage,
                'distribution_score': distribution_score,
                'quality_metrics': {
                    'total_fields': total_fields,
                    'missing_fields': missing_fields
                }
            }
            
        except Exception as e:
            print(f"❌ Dictionary quality validation failed: {e}")
            return {'passed': False, 'error': str(e)}
    
    async def _update_validation_metrics(self, validation_results: Dict[str, Any], start_time: datetime):
        """Update validation metrics based on results"""
        try:
            # Update basic metrics
            self.metrics.validation_passed = validation_results.get('overall_result', False)
            self.metrics.validation_time = (datetime.now() - start_time).total_seconds()
            
            # Update schema validation metrics
            if 'schema_validation' in validation_results:
                schema_results = validation_results['schema_validation']
                self.metrics.schema_errors = schema_results.get('errors', [])
                self.metrics.error_count = len(self.metrics.schema_errors)
                
                # Calculate validation score
                if 'summary' in schema_results:
                    summary = schema_results['summary']
                    total_fields = summary.get('total_fields', 1)
                    passed_fields = summary.get('passed_fields', 0)
                    self.metrics.validation_score = passed_fields / total_fields if total_fields > 0 else 0.0
            
            # Update quality validation metrics
            if 'quality_validation' in validation_results:
                quality_results = validation_results['quality_validation']
                self.metrics.completeness_score = quality_results.get('completeness_score', 0.0)
                self.metrics.outlier_percentage = quality_results.get('outlier_percentage', 0.0)
                self.metrics.data_distribution_score = quality_results.get('distribution_score', 0.0)
            
        except Exception as e:
            print(f"⚠️  Metrics update failed: {e}")
    
    async def add_custom_validator(self, name: str, validator_func: Callable):
        """Add a custom validation function"""
        try:
            self.custom_validators[name] = validator_func
            print(f"✅ Added custom validator: {name}")
            
        except Exception as e:
            print(f"❌ Failed to add custom validator: {e}")
    
    async def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report"""
        try:
            return {
                'validation_metrics': self.metrics.__dict__,
                'validation_history': self.validation_history,
                'current_config': self.config.__dict__,
                'custom_validators': list(self.custom_validators.keys())
            }
            
        except Exception as e:
            print(f"❌ Validation report generation failed: {e}")
            return {'error': str(e)}
    
    async def reset_metrics(self):
        """Reset validation metrics"""
        try:
            self.metrics = ValidationMetrics()
            print("🔄 Validation metrics reset")
            
        except Exception as e:
            print(f"❌ Metrics reset failed: {e}")


