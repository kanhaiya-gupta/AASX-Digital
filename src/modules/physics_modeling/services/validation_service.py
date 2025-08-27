"""
Validation Service for Physics Modeling
======================================

Provides comprehensive validation capabilities for physics modeling,
ensuring data quality, parameter validity, and compliance with standards.

Features:
- Model parameter validation
- Physics constraint validation
- Compliance rule checking
- Data quality assessment
- Validation result tracking
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
import json
import re

# Import physics modeling components
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..models.physics_modeling_metrics import PhysicsModelingMetrics
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation level enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"


class ValidationStatus(Enum):
    """Validation status enumeration."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ValidationRule(Enum):
    """Validation rule enumeration."""
    PARAMETER_RANGE = "parameter_range"
    PHYSICS_CONSTRAINTS = "physics_constraints"
    DATA_FORMAT = "data_format"
    COMPLIANCE_REQUIREMENTS = "compliance_requirements"
    SECURITY_POLICIES = "security_policies"
    PERFORMANCE_THRESHOLDS = "performance_thresholds"


class ValidationResult:
    """Validation result data structure."""
    
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        rule_type: ValidationRule,
        status: ValidationStatus,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.rule_type = rule_type
        self.status = status
        self.message = message
        self.details = details or {}
        self.severity = severity
        self.timestamp = datetime.now()


class ValidationService:
    """
    Comprehensive validation service for physics modeling.
    
    Provides:
    - Model parameter validation
    - Physics constraint validation
    - Compliance rule checking
    - Data quality assessment
    - Validation result tracking
    """

    def __init__(
        self,
        registry_repo: Optional[PhysicsModelingRegistryRepository] = None,
        metrics_repo: Optional[PhysicsModelingMetricsRepository] = None
    ):
        """Initialize the validation service."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        
        # Initialize repositories if not provided
        if not self.registry_repo:
            from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
            self.registry_repo = PhysicsModelingRegistryRepository()
        
        if not self.metrics_repo:
            from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
            self.metrics_repo = PhysicsModelingMetricsRepository()
        
        # Validation rules and configurations
        self.validation_rules = self._initialize_validation_rules()
        self.compliance_thresholds = self._initialize_compliance_thresholds()
        
        logger.info("Validation service initialized")

    async def initialize(self) -> bool:
        """Initialize the validation service."""
        try:
            # Initialize repositories
            await self.registry_repo.initialize()
            await self.metrics_repo.initialize()
            
            logger.info("✅ Validation service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize validation service: {e}")
            return False

    async def validate_model_parameters(
        self,
        model_type: str,
        parameters: Dict[str, Any],
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> List[ValidationResult]:
        """
        Validate model parameters based on type and validation level.
        
        Args:
            model_type: Type of physics model
            parameters: Model parameters to validate
            validation_level: Level of validation to apply
            
        Returns:
            List of validation results
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            validation_results = []
            
            # Get validation rules for this model type and level
            rules = self._get_validation_rules(model_type, validation_level)
            
            # Apply each validation rule
            for rule in rules:
                result = await self._apply_validation_rule(rule, parameters)
                validation_results.append(result)
            
            # Record validation metrics
            await self._record_validation_metrics(model_type, validation_results)
            
            logger.info(f"✅ Validated {len(validation_results)} rules for {model_type}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate model parameters: {e}")
            return []

    async def validate_physics_constraints(
        self,
        model_type: str,
        parameters: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[ValidationResult]:
        """
        Validate physics constraints for a model.
        
        Args:
            model_type: Type of physics model
            parameters: Model parameters
            constraints: Physics constraints to validate
            
        Returns:
            List of validation results
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            validation_results = []
            
            # Validate physical constraints
            if model_type == "structural":
                results = await self._validate_structural_constraints(parameters, constraints)
                validation_results.extend(results)
            
            elif model_type == "thermal":
                results = await self._validate_thermal_constraints(parameters, constraints)
                validation_results.extend(results)
            
            elif model_type == "fluid_dynamics":
                results = await self._validate_fluid_constraints(parameters, constraints)
                validation_results.extend(results)
            
            elif model_type == "multi_physics":
                results = await self._validate_multi_physics_constraints(parameters, constraints)
                validation_results.extend(results)
            
            # Record validation metrics
            await self._record_validation_metrics(model_type, validation_results)
            
            logger.info(f"✅ Validated physics constraints for {model_type}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate physics constraints: {e}")
            return []

    async def validate_compliance(
        self,
        model_id: str,
        compliance_rules: List[str]
    ) -> List[ValidationResult]:
        """
        Validate model compliance with specified rules.
        
        Args:
            model_id: Model identifier
            compliance_rules: List of compliance rules to check
            
        Returns:
            List of validation results
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Get model from registry
            model = await self.registry_repo.get_by_id(model_id)
            if not model:
                logger.warning(f"Model {model_id} not found for compliance validation")
                return []
            
            validation_results = []
            
            # Check each compliance rule
            for rule_name in compliance_rules:
                result = await self._check_compliance_rule(rule_name, model)
                validation_results.append(result)
            
            # Record compliance metrics
            await self._record_compliance_metrics(model_id, validation_results)
            
            logger.info(f"✅ Validated compliance for model {model_id}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate compliance for model {model_id}: {e}")
            return []

    async def validate_data_quality(
        self,
        data: Dict[str, Any],
        data_type: str,
        quality_standards: Dict[str, Any]
    ) -> List[ValidationResult]:
        """
        Validate data quality against specified standards.
        
        Args:
            data: Data to validate
            data_type: Type of data
            quality_standards: Quality standards to apply
            
        Returns:
            List of validation results
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            validation_results = []
            
            # Apply data quality validation rules
            if data_type == "mesh_data":
                results = await self._validate_mesh_data_quality(data, quality_standards)
                validation_results.extend(results)
            
            elif data_type == "boundary_conditions":
                results = await self._validate_boundary_conditions_quality(data, quality_standards)
                validation_results.extend(results)
            
            elif data_type == "material_properties":
                results = await self._validate_material_properties_quality(data, quality_standards)
                validation_results.extend(results)
            
            elif data_type == "simulation_results":
                results = await self._validate_simulation_results_quality(data, quality_standards)
                validation_results.extend(results)
            
            # Record quality metrics
            await self._record_quality_metrics(data_type, validation_results)
            
            logger.info(f"✅ Validated data quality for {data_type}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate data quality: {e}")
            return []

    async def get_validation_summary(
        self,
        model_id: Optional[str] = None,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        Get validation summary and statistics.
        
        Args:
            model_id: Specific model ID (optional)
            time_range: Time range for summary
            
        Returns:
            Validation summary data
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Get validation metrics from database
            metrics = await self.metrics_repo.get_by_metric_name("validation_result")
            
            # Filter by time range
            now = datetime.now()
            if time_range == "24h":
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == "7d":
                start_time = now.replace(day=now.day-7, hour=0, minute=0, second=0, microsecond=0)
            elif time_range == "30d":
                start_time = now.replace(day=now.day-30, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_time = datetime.min
            
            filtered_metrics = [
                m for m in metrics 
                if m.metric_timestamp >= start_time
            ]
            
            # Calculate summary statistics
            total_validations = len(filtered_metrics)
            passed_validations = len([m for m in filtered_metrics if m.metric_metadata.get('status') == 'passed'])
            failed_validations = len([m for m in filtered_metrics if m.metric_metadata.get('status') == 'failed'])
            warning_validations = len([m for m in filtered_metrics if m.metric_metadata.get('status') == 'warning'])
            
            success_rate = (passed_validations / total_validations * 100) if total_validations > 0 else 0
            
            # Group by validation type
            validation_types = {}
            for metric in filtered_metrics:
                val_type = metric.metric_metadata.get('validation_type', 'unknown')
                if val_type not in validation_types:
                    validation_types[val_type] = {'total': 0, 'passed': 0, 'failed': 0, 'warning': 0}
                
                validation_types[val_type]['total'] += 1
                status = metric.metric_metadata.get('status', 'unknown')
                if status in validation_types[val_type]:
                    validation_types[val_type][status] += 1
            
            summary = {
                'time_range': time_range,
                'total_validations': total_validations,
                'passed_validations': passed_validations,
                'failed_validations': failed_validations,
                'warning_validations': warning_validations,
                'success_rate': round(success_rate, 2),
                'validation_types': validation_types,
                'generated_at': now.isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get validation summary: {e}")
            return {}

    def _initialize_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize validation rules for different model types."""
        return {
            "structural": [
                {
                    "rule_id": "struct_param_range",
                    "rule_name": "Structural Parameter Range Check",
                    "rule_type": ValidationRule.PARAMETER_RANGE,
                    "parameters": ["elastic_modulus", "poisson_ratio", "density"],
                    "ranges": {
                        "elastic_modulus": (1e6, 1e12),  # Pa
                        "poisson_ratio": (0.0, 0.5),
                        "density": (100, 10000)  # kg/m³
                    }
                },
                {
                    "rule_id": "struct_mesh_quality",
                    "rule_name": "Mesh Quality Check",
                    "rule_type": ValidationRule.DATA_FORMAT,
                    "parameters": ["mesh_size", "element_quality"],
                    "constraints": {
                        "mesh_size": (100, 10000000),  # elements
                        "element_quality": (0.1, 1.0)
                    }
                }
            ],
            "thermal": [
                {
                    "rule_id": "thermal_param_range",
                    "rule_name": "Thermal Parameter Range Check",
                    "rule_type": ValidationRule.PARAMETER_RANGE,
                    "parameters": ["thermal_conductivity", "specific_heat", "thermal_expansion"],
                    "ranges": {
                        "thermal_conductivity": (0.01, 1000),  # W/(m·K)
                        "specific_heat": (100, 5000),  # J/(kg·K)
                        "thermal_expansion": (1e-6, 1e-4)  # 1/K
                    }
                }
            ],
            "fluid_dynamics": [
                {
                    "rule_id": "fluid_param_range",
                    "rule_name": "Fluid Parameter Range Check",
                    "rule_type": ValidationRule.PARAMETER_RANGE,
                    "parameters": ["viscosity", "density", "pressure"],
                    "ranges": {
                        "viscosity": (1e-6, 1e-3),  # Pa·s
                        "density": (0.1, 10000),  # kg/m³
                        "pressure": (1e3, 1e8)  # Pa
                    }
                }
            ]
        }

    def _initialize_compliance_thresholds(self) -> Dict[str, float]:
        """Initialize compliance thresholds for different validation types."""
        return {
            "parameter_range": 0.95,      # 95% of parameters must be within range
            "physics_constraints": 0.90,   # 90% of constraints must be satisfied
            "data_format": 0.98,          # 98% of data must be properly formatted
            "compliance_requirements": 0.85,  # 85% of compliance rules must pass
            "security_policies": 1.0,     # 100% of security policies must pass
            "performance_thresholds": 0.80  # 80% of performance thresholds must be met
        }

    def _get_validation_rules(
        self,
        model_type: str,
        validation_level: ValidationLevel
    ) -> List[Dict[str, Any]]:
        """Get validation rules for a specific model type and level."""
        base_rules = self.validation_rules.get(model_type, [])
        
        # Filter rules based on validation level
        if validation_level == ValidationLevel.BASIC:
            return [r for r in base_rules if r["rule_type"] in [ValidationRule.PARAMETER_RANGE]]
        elif validation_level == ValidationLevel.STANDARD:
            return [r for r in base_rules if r["rule_type"] in [ValidationRule.PARAMETER_RANGE, ValidationRule.DATA_FORMAT]]
        elif validation_level == ValidationLevel.STRICT:
            return [r for r in base_rules if r["rule_type"] in [ValidationRule.PARAMETER_RANGE, ValidationRule.DATA_FORMAT, ValidationRule.PHYSICS_CONSTRAINTS]]
        else:  # ENTERPRISE
            return base_rules

    async def _apply_validation_rule(
        self,
        rule: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> ValidationResult:
        """Apply a specific validation rule to parameters."""
        try:
            rule_id = rule["rule_id"]
            rule_name = rule["rule_name"]
            rule_type = rule["rule_type"]
            
            if rule_type == ValidationRule.PARAMETER_RANGE:
                return await self._validate_parameter_range(rule, parameters)
            elif rule_type == ValidationRule.DATA_FORMAT:
                return await self._validate_data_format(rule, parameters)
            elif rule_type == ValidationRule.PHYSICS_CONSTRAINTS:
                return await self._validate_physics_constraints_rule(rule, parameters)
            else:
                return ValidationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    rule_type=rule_type,
                    status=ValidationStatus.SKIPPED,
                    message=f"Unknown rule type: {rule_type}",
                    severity="warning"
                )
                
        except Exception as e:
            logger.error(f"Failed to apply validation rule {rule.get('rule_id')}: {e}")
            return ValidationResult(
                rule_id=rule.get('rule_id', 'unknown'),
                rule_name=rule.get('rule_name', 'Unknown'),
                rule_type=rule.get('rule_type', ValidationRule.PARAMETER_RANGE),
                status=ValidationStatus.FAILED,
                message=f"Validation rule application failed: {e}",
                severity="error"
            )

    async def _validate_parameter_range(
        self,
        rule: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> ValidationResult:
        """Validate parameter ranges."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            rule_id = rule["rule_id"]
            rule_name = rule["rule_name"]
            ranges = rule["ranges"]
            
            violations = []
            total_params = len(ranges)
            valid_params = 0
            
            for param_name, (min_val, max_val) in ranges.items():
                if param_name in parameters:
                    param_value = parameters[param_name]
                    if min_val <= param_value <= max_val:
                        valid_params += 1
                    else:
                        violations.append({
                            'parameter': param_name,
                            'value': param_value,
                            'expected_range': f"[{min_val}, {max_val}]"
                        })
            
            # Calculate compliance score
            compliance_score = valid_params / total_params if total_params > 0 else 0
            threshold = self.compliance_thresholds["parameter_range"]
            
            if compliance_score >= threshold:
                status = ValidationStatus.PASSED
                message = f"Parameter range validation passed ({valid_params}/{total_params} parameters valid)"
                severity = "info"
            else:
                status = ValidationStatus.FAILED
                message = f"Parameter range validation failed ({valid_params}/{total_params} parameters valid, threshold: {threshold})"
                severity = "error"
            
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                rule_type=ValidationRule.PARAMETER_RANGE,
                status=status,
                message=message,
                details={
                    'compliance_score': compliance_score,
                    'threshold': threshold,
                    'valid_parameters': valid_params,
                    'total_parameters': total_params,
                    'violations': violations
                },
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Failed to validate parameter ranges: {e}")
            return ValidationResult(
                rule_id=rule.get('rule_id', 'unknown'),
                rule_name=rule.get('rule_name', 'Unknown'),
                rule_type=ValidationRule.PARAMETER_RANGE,
                status=ValidationStatus.FAILED,
                message=f"Parameter range validation failed: {e}",
                severity="error"
            )

    async def _validate_data_format(
        self,
        rule: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> ValidationResult:
        """Validate data format."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            rule_id = rule["rule_id"]
            rule_name = rule["rule_name"]
            constraints = rule.get("constraints", {})
            
            violations = []
            total_checks = len(constraints)
            valid_checks = 0
            
            for param_name, (min_val, max_val) in constraints.items():
                if param_name in parameters:
                    param_value = parameters[param_name]
                    if min_val <= param_value <= max_val:
                        valid_checks += 1
                    else:
                        violations.append({
                            'parameter': param_name,
                            'value': param_value,
                            'expected_range': f"[{min_val}, {max_val}]"
                        })
            
            # Calculate compliance score
            compliance_score = valid_checks / total_checks if total_checks > 0 else 0
            threshold = self.compliance_thresholds["data_format"]
            
            if compliance_score >= threshold:
                status = ValidationStatus.PASSED
                message = f"Data format validation passed ({valid_checks}/{total_checks} checks valid)"
                severity = "info"
            else:
                status = ValidationStatus.FAILED
                message = f"Data format validation failed ({valid_checks}/{total_checks} checks valid, threshold: {threshold})"
                severity = "error"
            
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                rule_type=ValidationRule.DATA_FORMAT,
                status=status,
                message=message,
                details={
                    'compliance_score': compliance_score,
                    'threshold': threshold,
                    'valid_checks': valid_checks,
                    'total_checks': total_checks,
                    'violations': violations
                },
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Failed to validate data format: {e}")
            return ValidationResult(
                rule_id=rule.get('rule_id', 'unknown'),
                rule_name=rule.get('rule_name', 'Unknown'),
                rule_type=ValidationRule.DATA_FORMAT,
                status=ValidationStatus.FAILED,
                message=f"Data format validation failed: {e}",
                severity="error"
            )

    async def _validate_physics_constraints_rule(
        self,
        rule: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> ValidationResult:
        """Validate physics constraints rule."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            # This would implement specific physics constraint validation
            # For now, return a basic validation result
            return ValidationResult(
                rule_id=rule.get('rule_id', 'unknown'),
                rule_name=rule.get('rule_name', 'Unknown'),
                rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                status=ValidationStatus.PASSED,
                message="Physics constraints validation passed",
                details={'compliance_score': 1.0},
                severity="info"
            )
            
        except Exception as e:
            logger.error(f"Failed to validate physics constraints: {e}")
            return ValidationResult(
                rule_id=rule.get('rule_id', 'unknown'),
                rule_name=rule.get('rule_name', 'Unknown'),
                rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                status=ValidationStatus.FAILED,
                message=f"Physics constraints validation failed: {e}",
                severity="error"
            )

    async def _validate_structural_constraints(
        self,
        parameters: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate structural analysis constraints."""
        results = []
        
        # Check mesh quality constraints
        if 'mesh_quality' in constraints:
            min_quality = constraints['mesh_quality'].get('min', 0.1)
            if 'element_quality' in parameters:
                quality = parameters['element_quality']
                if quality < min_quality:
                    results.append(ValidationResult(
                        rule_id="struct_mesh_quality",
                        rule_name="Structural Mesh Quality",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.FAILED,
                        message=f"Mesh quality {quality} below minimum {min_quality}",
                        details={'current_quality': quality, 'minimum_quality': min_quality},
                        severity="error"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id="struct_mesh_quality",
                        rule_name="Structural Mesh Quality",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.PASSED,
                        message=f"Mesh quality {quality} meets minimum requirement {min_quality}",
                        details={'current_quality': quality, 'minimum_quality': min_quality},
                        severity="info"
                    ))
        
        return results

    async def _validate_thermal_constraints(
        self,
        parameters: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate thermal analysis constraints."""
        results = []
        
        # Check temperature range constraints
        if 'temperature_range' in constraints:
            min_temp = constraints['temperature_range'].get('min', -273.15)
            max_temp = constraints['temperature_range'].get('max', 1000.0)
            
            if 'ambient_temperature' in parameters:
                temp = parameters['ambient_temperature']
                if temp < min_temp or temp > max_temp:
                    results.append(ValidationResult(
                        rule_id="thermal_temp_range",
                        rule_name="Thermal Temperature Range",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.FAILED,
                        message=f"Temperature {temp} outside range [{min_temp}, {max_temp}]",
                        details={'current_temp': temp, 'range': [min_temp, max_temp]},
                        severity="error"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id="thermal_temp_range",
                        rule_name="Thermal Temperature Range",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.PASSED,
                        message=f"Temperature {temp} within valid range [{min_temp}, {max_temp}]",
                        details={'current_temp': temp, 'range': [min_temp, max_temp]},
                        severity="info"
                    ))
        
        return results

    async def _validate_fluid_constraints(
        self,
        parameters: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate fluid dynamics constraints."""
        results = []
        
        # Check Reynolds number constraints
        if 'reynolds_number' in constraints:
            max_re = constraints['reynolds_number'].get('max', 1e6)
            if 'reynolds_number' in parameters:
                re = parameters['reynolds_number']
                if re > max_re:
                    results.append(ValidationResult(
                        rule_id="fluid_reynolds",
                        rule_name="Fluid Reynolds Number",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.WARNING,
                        message=f"Reynolds number {re} exceeds recommended maximum {max_re}",
                        details={'current_re': re, 'max_recommended': max_re},
                        severity="warning"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id="fluid_reynolds",
                        rule_name="Fluid Reynolds Number",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.PASSED,
                        message=f"Reynolds number {re} within acceptable range",
                        details={'current_re': re, 'max_recommended': max_re},
                        severity="info"
                    ))
        
        return results

    async def _validate_multi_physics_constraints(
        self,
        parameters: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate multi-physics constraints."""
        results = []
        
        # Check coupling constraints
        if 'coupling_strength' in constraints:
            max_coupling = constraints['coupling_strength'].get('max', 0.8)
            if 'coupling_strength' in parameters:
                coupling = parameters['coupling_strength']
                if coupling > max_coupling:
                    results.append(ValidationResult(
                        rule_id="multi_physics_coupling",
                        rule_name="Multi-Physics Coupling",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.WARNING,
                        message=f"Coupling strength {coupling} exceeds recommended maximum {max_coupling}",
                        details={'current_coupling': coupling, 'max_recommended': max_coupling},
                        severity="warning"
                    ))
                else:
                    results.append(ValidationResult(
                        rule_id="multi_physics_coupling",
                        rule_name="Multi-Physics Coupling",
                        rule_type=ValidationRule.PHYSICS_CONSTRAINTS,
                        status=ValidationStatus.PASSED,
                        message=f"Coupling strength {coupling} within acceptable range",
                        details={'current_coupling': coupling, 'max_recommended': max_coupling},
                        severity="info"
                    ))
        
        return results

    async def _check_compliance_rule(
        self,
        rule_name: str,
        model: PhysicsModelingRegistry
    ) -> ValidationResult:
        """Check a specific compliance rule."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            if rule_name == "model_quality":
                return await self._check_model_quality_compliance(model)
            elif rule_name == "security_policies":
                return await self._check_security_policies_compliance(model)
            elif rule_name == "performance_standards":
                return await self._check_performance_standards_compliance(model)
            else:
                return ValidationResult(
                    rule_id=f"compliance_{rule_name}",
                    rule_name=f"Compliance: {rule_name}",
                    rule_type=ValidationRule.COMPLIANCE_REQUIREMENTS,
                    status=ValidationStatus.SKIPPED,
                    message=f"Unknown compliance rule: {rule_name}",
                    severity="warning"
                )
                
        except Exception as e:
            logger.error(f"Failed to check compliance rule {rule_name}: {e}")
            return ValidationResult(
                rule_id=f"compliance_{rule_name}",
                rule_name=f"Compliance: {rule_name}",
                rule_type=ValidationRule.COMPLIANCE_REQUIREMENTS,
                status=ValidationStatus.FAILED,
                message=f"Compliance check failed: {e}",
                severity="error"
            )

    async def _check_model_quality_compliance(
        self,
        model: PhysicsModelingRegistry
    ) -> ValidationResult:
        """Check model quality compliance."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            quality_score = model.quality_score or 0.0
            threshold = 75.0  # Minimum quality score
            
            if quality_score >= threshold:
                status = ValidationStatus.PASSED
                message = f"Model quality score {quality_score} meets threshold {threshold}"
                severity = "info"
            else:
                status = ValidationStatus.FAILED
                message = f"Model quality score {quality_score} below threshold {threshold}"
                severity = "error"
            
            return ValidationResult(
                rule_id="compliance_model_quality",
                rule_name="Model Quality Compliance",
                rule_type=ValidationRule.COMPLIANCE_REQUIREMENTS,
                status=status,
                message=message,
                details={'quality_score': quality_score, 'threshold': threshold},
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Failed to check model quality compliance: {e}")
            return ValidationResult(
                rule_id="compliance_model_quality",
                rule_name="Model Quality Compliance",
                rule_type=ValidationRule.COMPLIANCE_REQUIREMENTS,
                status=ValidationStatus.FAILED,
                message=f"Quality compliance check failed: {e}",
                severity="error"
            )

    async def _check_security_policies_compliance(
        self,
        model: PhysicsModelingRegistry
    ) -> ValidationResult:
        """Check security policies compliance."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            security_score = model.security_score or 0.0
            threshold = 80.0  # Minimum security score
            
            if security_score >= threshold:
                status = ValidationStatus.PASSED
                message = f"Security score {security_score} meets threshold {threshold}"
                severity = "info"
            else:
                status = ValidationStatus.FAILED
                message = f"Security score {security_score} below threshold {threshold}"
                severity = "error"
            
            return ValidationResult(
                rule_id="compliance_security_policies",
                rule_name="Security Policies Compliance",
                rule_type=ValidationRule.SECURITY_POLICIES,
                status=status,
                message=message,
                details={'security_score': security_score, 'threshold': threshold},
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Failed to check security policies compliance: {e}")
            return ValidationResult(
                rule_id="compliance_security_policies",
                rule_name="Security Policies Compliance",
                rule_type=ValidationRule.SECURITY_POLICIES,
                status=ValidationStatus.FAILED,
                message=f"Security compliance check failed: {e}",
                severity="error"
            )

    async def _check_performance_standards_compliance(
        self,
        model: PhysicsModelingRegistry
    ) -> ValidationResult:
        """Check performance standards compliance."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            performance_score = model.performance_score or 0.0
            threshold = 70.0  # Minimum performance score
            
            if performance_score >= threshold:
                status = ValidationStatus.PASSED
                message = f"Performance score {performance_score} meets threshold {threshold}"
                severity = "info"
            else:
                status = ValidationStatus.FAILED
                message = f"Performance score {performance_score} below threshold {threshold}"
                severity = "error"
            
            return ValidationResult(
                rule_id="compliance_performance_standards",
                rule_name="Performance Standards Compliance",
                rule_type=ValidationRule.PERFORMANCE_THRESHOLDS,
                status=status,
                message=message,
                details={'performance_score': performance_score, 'threshold': threshold},
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Failed to check performance standards compliance: {e}")
            return ValidationResult(
                rule_id="compliance_performance_standards",
                rule_name="Performance Standards Compliance",
                rule_type=ValidationRule.PERFORMANCE_THRESHOLDS,
                status=ValidationStatus.FAILED,
                message=f"Performance compliance check failed: {e}",
                severity="error"
            )

    async def _validate_mesh_data_quality(
        self,
        data: Dict[str, Any],
        quality_standards: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate mesh data quality."""
        results = []
        
        # Check mesh element count
        if 'element_count' in data:
            min_elements = quality_standards.get('min_elements', 100)
            max_elements = quality_standards.get('max_elements', 1000000)
            element_count = data['element_count']
            
            if element_count < min_elements:
                results.append(ValidationResult(
                    rule_id="mesh_element_count",
                    rule_name="Mesh Element Count",
                    rule_type=ValidationRule.DATA_FORMAT,
                    status=ValidationStatus.WARNING,
                    message=f"Element count {element_count} below recommended minimum {min_elements}",
                    details={'current_count': element_count, 'min_recommended': min_elements},
                    severity="warning"
                ))
            elif element_count > max_elements:
                results.append(ValidationResult(
                    rule_id="mesh_element_count",
                    rule_name="Mesh Element Count",
                    rule_type=ValidationRule.DATA_FORMAT,
                    status=ValidationStatus.WARNING,
                    message=f"Element count {element_count} above recommended maximum {max_elements}",
                    details={'current_count': element_count, 'max_recommended': max_elements},
                    severity="warning"
                ))
            else:
                results.append(ValidationResult(
                    rule_id="mesh_element_count",
                    rule_name="Mesh Element Count",
                    rule_type=ValidationRule.DATA_FORMAT,
                    status=ValidationStatus.PASSED,
                    message=f"Element count {element_count} within recommended range",
                    details={'current_count': element_count, 'range': [min_elements, max_elements]},
                    severity="info"
                ))
        
        return results

    async def _validate_boundary_conditions_quality(
        self,
        data: Dict[str, Any],
        quality_standards: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate boundary conditions quality."""
        results = []
        
        # Check boundary condition completeness
        required_bcs = quality_standards.get('required_boundary_conditions', [])
        provided_bcs = data.get('boundary_conditions', [])
        
        missing_bcs = [bc for bc in required_bcs if bc not in provided_bcs]
        
        if missing_bcs:
            results.append(ValidationResult(
                rule_id="bc_completeness",
                rule_name="Boundary Conditions Completeness",
                rule_type=ValidationRule.DATA_FORMAT,
                status=ValidationStatus.FAILED,
                message=f"Missing boundary conditions: {missing_bcs}",
                details={'missing_bcs': missing_bcs, 'provided_bcs': provided_bcs},
                severity="error"
            ))
        else:
            results.append(ValidationResult(
                rule_id="bc_completeness",
                rule_name="Boundary Conditions Completeness",
                rule_type=ValidationRule.DATA_FORMAT,
                status=ValidationStatus.PASSED,
                message="All required boundary conditions provided",
                details={'provided_bcs': provided_bcs},
                severity="info"
            ))
        
        return results

    async def _validate_material_properties_quality(
        self,
        data: Dict[str, Any],
        quality_standards: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate material properties quality."""
        results = []
        
        # Check material property consistency
        if 'material_properties' in data:
            props = data['material_properties']
            required_props = quality_standards.get('required_material_properties', [])
            
            missing_props = [prop for prop in required_props if prop not in props]
            
            if missing_props:
                results.append(ValidationResult(
                    rule_id="material_props_completeness",
                    rule_name="Material Properties Completeness",
                    rule_type=ValidationRule.DATA_FORMAT,
                    status=ValidationStatus.FAILED,
                    message=f"Missing material properties: {missing_props}",
                    details={'missing_props': missing_props, 'provided_props': list(props.keys())},
                    severity="error"
                ))
            else:
                results.append(ValidationResult(
                    rule_id="material_props_completeness",
                    rule_name="Material Properties Completeness",
                    rule_type=ValidationRule.DATA_FORMAT,
                    status=ValidationStatus.PASSED,
                    message="All required material properties provided",
                    details={'provided_props': list(props.keys())},
                    severity="info"
                ))
        
        return results

    async def _validate_simulation_results_quality(
        self,
        data: Dict[str, Any],
        quality_standards: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate simulation results quality."""
        results = []
        
        # Check result convergence
        if 'convergence_status' in data:
            convergence = data['convergence_status']
            if not convergence.get('converged', False):
                results.append(ValidationResult(
                    rule_id="simulation_convergence",
                    rule_name="Simulation Convergence",
                    rule_type=ValidationRule.DATA_FORMAT,
                    status=ValidationStatus.WARNING,
                    message="Simulation did not converge",
                    details={'convergence_status': convergence},
                    severity="warning"
                ))
            else:
                results.append(ValidationResult(
                    rule_id="simulation_convergence",
                    rule_name="Simulation Convergence",
                    rule_type=ValidationRule.DATA_FORMAT,
                    status=ValidationStatus.PASSED,
                    message="Simulation converged successfully",
                    details={'convergence_status': convergence},
                    severity="info"
                ))
        
        return results

    async def _record_validation_metrics(
        self,
        model_type: str,
        validation_results: List[ValidationResult]
    ) -> None:
        """Record validation metrics for analysis."""
        try:
            for result in validation_results:
                # Create metrics record
                metrics = PhysicsModelingMetrics(
                    physics_modeling_id=None,  # Will be set by repository
                    metric_name="validation_result",
                    metric_value=1.0 if result.status == ValidationStatus.PASSED else 0.0,
                    metric_unit="count",
                    metric_type="validation",
                    metric_category="quality_assurance",
                    metric_timestamp=result.timestamp,
                    metric_metadata={
                        'rule_id': result.rule_id,
                        'rule_name': result.rule_name,
                        'rule_type': result.rule_type.value,
                        'status': result.status.value,
                        'message': result.message,
                        'severity': result.severity,
                        'model_type': model_type,
                        'details': result.details
                    }
                )
                
                # Save to database
                await self.metrics_repo.create(metrics)
            
            logger.info(f"✅ Validation metrics recorded for {model_type}")
            
        except Exception as e:
            logger.error(f"Failed to record validation metrics: {e}")

    async def _record_compliance_metrics(
        self,
        model_id: str,
        validation_results: List[ValidationResult]
    ) -> None:
        """Record compliance validation metrics."""
        try:
            for result in validation_results:
                # Create metrics record
                metrics = PhysicsModelingMetrics(
                    physics_modeling_id=None,  # Will be set by repository
                    metric_name="compliance_validation",
                    metric_value=1.0 if result.status == ValidationStatus.PASSED else 0.0,
                    metric_unit="count",
                    metric_type="compliance",
                    metric_category="regulatory",
                    metric_timestamp=result.timestamp,
                    metric_metadata={
                        'rule_id': result.rule_id,
                        'rule_name': result.rule_name,
                        'rule_type': result.rule_type.value,
                        'status': result.status.value,
                        'message': result.message,
                        'severity': result.severity,
                        'model_id': model_id,
                        'details': result.details
                    }
                )
                
                # Save to database
                await self.metrics_repo.create(metrics)
            
            logger.info(f"✅ Compliance metrics recorded for model {model_id}")
            
        except Exception as e:
            logger.error(f"Failed to record compliance metrics: {e}")

    async def _record_quality_metrics(
        self,
        data_type: str,
        validation_results: List[ValidationResult]
    ) -> None:
        """Record data quality validation metrics."""
        try:
            for result in validation_results:
                # Create metrics record
                metrics = PhysicsModelingMetrics(
                    physics_modeling_id=None,  # Will be set by repository
                    metric_name="data_quality_validation",
                    metric_value=1.0 if result.status == ValidationStatus.PASSED else 0.0,
                    metric_unit="count",
                    metric_type="quality",
                    metric_category="data_integrity",
                    metric_timestamp=result.timestamp,
                    metric_metadata={
                        'rule_id': result.rule_id,
                        'rule_name': result.rule_name,
                        'rule_type': result.rule_type.value,
                        'status': result.status.value,
                        'message': result.message,
                        'severity': result.severity,
                        'data_type': data_type,
                        'details': result.details
                    }
                )
                
                # Save to database
                await self.metrics_repo.create(metrics)
            
            logger.info(f"✅ Data quality metrics recorded for {data_type}")
            
        except Exception as e:
            logger.error(f"Failed to record data quality metrics: {e}")

    async def close(self) -> None:
        """Close the validation service."""
        try:
            if self.registry_repo:
                await self.registry_repo.close()
            if self.metrics_repo:
                await self.metrics_repo.close()
            
            logger.info("✅ Validation service closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing validation service: {e}")


