"""
Population Validator

Handles data validation and quality checks during the population process.
Ensures data integrity, validates field values, and performs quality assessments
before and after population operations.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Enumeration of validation levels."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    CUSTOM = "custom"


class ValidationResult(Enum):
    """Enumeration of validation results."""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


class PopulationValidator:
    """
    Validates data during population process.
    
    Handles:
    - Field validation
    - Data type validation
    - Business rule validation
    - Quality scoring
    - Validation reporting
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """Initialize the population validator."""
        self.validation_level = validation_level
        self.validation_rules = self._load_validation_rules()
        self.quality_thresholds = self._load_quality_thresholds()
        
        logger.info(f"Population Validator initialized with level: {validation_level.value}")
    
    async def validate_basic_registry_data(
        self,
        registry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate basic registry data before creation.
        
        Args:
            registry_data: Basic registry data to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            logger.info("Validating basic registry data")
            
            validation_results = {
                "overall_result": ValidationResult.PASSED.value,
                "validation_level": self.validation_level.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "field_validations": {},
                "quality_score": 0,
                "warnings": [],
                "errors": []
            }
            
            # Validate required fields
            required_fields = self._get_required_fields()
            for field in required_fields:
                field_result = self._validate_required_field(field, registry_data)
                validation_results["field_validations"][field] = field_result
                
                if field_result["result"] == ValidationResult.FAILED.value:
                    validation_results["errors"].append(field_result["message"])
                    validation_results["overall_result"] = ValidationResult.FAILED.value
                elif field_result["result"] == ValidationResult.WARNING.value:
                    validation_results["warnings"].append(field_result["message"])
            
            # Validate field values
            field_validations = self._validate_field_values(registry_data)
            validation_results["field_validations"].update(field_validations)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(validation_results["field_validations"])
            validation_results["quality_score"] = quality_score
            
            # Check if validation passed
            if validation_results["overall_result"] == ValidationResult.PASSED.value:
                if quality_score < self.quality_thresholds["minimum_quality"]:
                    validation_results["overall_result"] = ValidationResult.WARNING.value
                    validation_results["warnings"].append(
                        f"Quality score {quality_score} below threshold {self.quality_thresholds['minimum_quality']}"
                    )
            
            logger.info(f"Basic registry validation completed: {validation_results['overall_result']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Basic registry validation failed: {e}")
            return {
                "overall_result": ValidationResult.FAILED.value,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def validate_etl_enhancement_data(
        self,
        etl_data: Dict[str, Any],
        registry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate ETL enhancement data before updating registry.
        
        Args:
            etl_data: ETL processing results to validate
            registry_data: Current registry data for comparison
            
        Returns:
            Dict containing validation results
        """
        try:
            logger.info("Validating ETL enhancement data")
            
            validation_results = {
                "overall_result": ValidationResult.PASSED.value,
                "validation_level": self.validation_level.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "etl_validations": {},
                "registry_validations": {},
                "consistency_checks": {},
                "quality_score": 0,
                "warnings": [],
                "errors": []
            }
            
            # Validate ETL data
            etl_validations = self._validate_etl_data(etl_data)
            validation_results["etl_validations"] = etl_validations
            
            # Validate registry consistency
            consistency_checks = self._validate_registry_consistency(etl_data, registry_data)
            validation_results["consistency_checks"] = consistency_checks
            
            # Check for validation failures
            for field, result in etl_validations.items():
                if result["result"] == ValidationResult.FAILED.value:
                    validation_results["errors"].append(result["message"])
                    validation_results["overall_result"] = ValidationResult.FAILED.value
            
            for check, result in consistency_checks.items():
                if result["result"] == ValidationResult.FAILED.value:
                    validation_results["errors"].append(result["message"])
                    validation_results["overall_result"] = ValidationResult.FAILED.value
            
            # Calculate quality score
            quality_score = self._calculate_enhancement_quality_score(
                etl_validations, consistency_checks
            )
            validation_results["quality_score"] = quality_score
            
            logger.info(f"ETL enhancement validation completed: {validation_results['overall_result']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"ETL enhancement validation failed: {e}")
            return {
                "overall_result": ValidationResult.FAILED.value,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def validate_population_completion(
        self,
        registry_data: Dict[str, Any],
        population_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate population completion and final data quality.
        
        Args:
            registry_data: Final registry data after population
            population_metadata: Metadata about the population process
            
        Returns:
            Dict containing final validation results
        """
        try:
            logger.info("Validating population completion")
            
            validation_results = {
                "overall_result": ValidationResult.PASSED.value,
                "validation_level": self.validation_level.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "completion_validations": {},
                "data_quality_checks": {},
                "business_rule_validations": {},
                "final_quality_score": 0,
                "warnings": [],
                "errors": []
            }
            
            # Validate completion requirements
            completion_validations = self._validate_completion_requirements(registry_data)
            validation_results["completion_validations"] = completion_validations
            
            # Check data quality
            data_quality_checks = self._validate_data_quality(registry_data)
            validation_results["data_quality_checks"] = data_quality_checks
            
            # Validate business rules
            business_rule_validations = self._validate_business_rules(registry_data)
            validation_results["business_rule_validations"] = business_rule_validations
            
            # Check for validation failures
            for validation_type, results in [
                ("completion", completion_validations),
                ("data_quality", data_quality_checks),
                ("business_rules", business_rule_validations)
            ]:
                for field, result in results.items():
                    if result["result"] == ValidationResult.FAILED.value:
                        validation_results["errors"].append(result["message"])
                        validation_results["overall_result"] = ValidationResult.FAILED.value
            
            # Calculate final quality score
            final_quality_score = self._calculate_final_quality_score(
                completion_validations, data_quality_checks, business_rule_validations
            )
            validation_results["final_quality_score"] = final_quality_score
            
            logger.info(f"Population completion validation completed: {validation_results['overall_result']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Population completion validation failed: {e}")
            return {
                "overall_result": ValidationResult.FAILED.value,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules based on validation level."""
        base_rules = {
            "required_fields": [
                "twin_name", "registry_name", "registry_type", "workflow_source",
                "user_id", "org_id"
            ],
            "field_constraints": {
                "twin_name": {"min_length": 1, "max_length": 100},
                "registry_name": {"min_length": 1, "max_length": 100},
                "overall_health_score": {"min_value": 0, "max_value": 100},
                "twin_version": {"pattern": r"^\d+\.\d+\.\d+$"}
            },
            "enum_values": {
                "registry_type": ["extraction", "generation", "hybrid"],
                "workflow_source": ["aasx_file", "structured_data", "both"],
                "twin_category": ["manufacturing", "energy", "component", "facility", "process", "generic"],
                "twin_type": ["physical", "virtual", "hybrid", "composite"],
                "twin_priority": ["low", "normal", "high", "critical", "emergency"]
            }
        }
        
        if self.validation_level == ValidationLevel.STRICT:
            base_rules["field_constraints"].update({
                "twin_name": {"min_length": 3, "max_length": 100},
                "registry_name": {"min_length": 3, "max_length": 100}
            })
        
        return base_rules
    
    def _load_quality_thresholds(self) -> Dict[str, Any]:
        """Load quality thresholds for validation."""
        return {
            "minimum_quality": 70,
            "warning_threshold": 80,
            "excellent_threshold": 90,
            "field_weights": {
                "required_fields": 0.4,
                "field_constraints": 0.3,
                "enum_values": 0.2,
                "data_consistency": 0.1
            }
        }
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for validation."""
        return self.validation_rules["required_fields"]
    
    def _validate_required_field(
        self,
        field: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a required field."""
        if field not in data or data[field] is None:
            return {
                "result": ValidationResult.FAILED.value,
                "message": f"Required field '{field}' is missing or null",
                "field": field
            }
        
        if isinstance(data[field], str) and not data[field].strip():
            return {
                "result": ValidationResult.FAILED.value,
                "message": f"Required field '{field}' is empty",
                "field": field
            }
        
        return {
            "result": ValidationResult.PASSED.value,
            "message": f"Required field '{field}' is present",
            "field": field
        }
    
    def _validate_field_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate field values against constraints."""
        validations = {}
        
        for field, constraints in self.validation_rules["field_constraints"].items():
            if field not in data:
                continue
            
            field_value = data[field]
            field_validations = []
            
            # Check length constraints
            if "min_length" in constraints and isinstance(field_value, str):
                if len(field_value) < constraints["min_length"]:
                    field_validations.append({
                        "result": ValidationResult.FAILED.value,
                        "message": f"Field '{field}' length {len(field_value)} below minimum {constraints['min_length']}"
                    })
            
            if "max_length" in constraints and isinstance(field_value, str):
                if len(field_value) > constraints["max_length"]:
                    field_validations.append({
                        "result": ValidationResult.FAILED.value,
                        "message": f"Field '{field}' length {len(field_value)} above maximum {constraints['max_length']}"
                    })
            
            # Check numeric constraints
            if "min_value" in constraints and isinstance(field_value, (int, float)):
                if field_value < constraints["min_value"]:
                    field_validations.append({
                        "result": ValidationResult.FAILED.value,
                        "message": f"Field '{field}' value {field_value} below minimum {constraints['min_value']}"
                    })
            
            if "max_value" in constraints and isinstance(field_value, (int, float)):
                if field_value > constraints["max_value"]:
                    field_validations.append({
                        "result": ValidationResult.FAILED.value,
                        "message": f"Field '{field}' value {field_value} above maximum {constraints['max_value']}"
                    })
            
            # Check pattern constraints
            if "pattern" in constraints and isinstance(field_value, str):
                import re
                if not re.match(constraints["pattern"], field_value):
                    field_validations.append({
                        "result": ValidationResult.FAILED.value,
                        "message": f"Field '{field}' value does not match pattern {constraints['pattern']}"
                    })
            
            # Determine overall result for field
            if field_validations:
                failed_validations = [v for v in field_validations if v["result"] == ValidationResult.FAILED.value]
                if failed_validations:
                    validations[field] = {
                        "result": ValidationResult.FAILED.value,
                        "validations": field_validations,
                        "message": f"Field '{field}' validation failed"
                    }
                else:
                    validations[field] = {
                        "result": ValidationResult.PASSED.value,
                        "validations": field_validations,
                        "message": f"Field '{field}' validation passed with warnings"
                    }
            else:
                validations[field] = {
                    "result": ValidationResult.PASSED.value,
                    "validations": [],
                    "message": f"Field '{field}' validation passed"
                }
        
        return validations
    
    def _validate_etl_data(self, etl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ETL processing data."""
        validations = {}
        
        # Validate required ETL fields
        required_etl_fields = ["processing_time", "assets_count", "output_formats"]
        for field in required_etl_fields:
            if field not in etl_data:
                validations[field] = {
                    "result": ValidationResult.FAILED.value,
                    "message": f"Required ETL field '{field}' is missing"
                }
            else:
                validations[field] = {
                    "result": ValidationResult.PASSED.value,
                    "message": f"ETL field '{field}' is present"
                }
        
        # Validate data quality
        if "quality_score" in etl_data:
            quality_score = etl_data["quality_score"]
            if not isinstance(quality_score, (int, float)) or quality_score < 0 or quality_score > 1:
                validations["quality_score"] = {
                    "result": ValidationResult.FAILED.value,
                    "message": f"Invalid quality score: {quality_score}. Must be between 0 and 1"
                }
            else:
                validations["quality_score"] = {
                    "result": ValidationResult.PASSED.value,
                    "message": f"Quality score {quality_score} is valid"
                }
        
        return validations
    
    def _validate_registry_consistency(
        self,
        etl_data: Dict[str, Any],
        registry_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate consistency between ETL data and registry data."""
        consistency_checks = {}
        
        # Check if registry type matches ETL job type
        if "job_type" in etl_data and "registry_type" in registry_data:
            etl_job_type = etl_data["job_type"]
            registry_type = registry_data["registry_type"]
            
            if etl_job_type == "extraction" and registry_type != "extraction":
                consistency_checks["registry_type_consistency"] = {
                    "result": ValidationResult.FAILED.value,
                    "message": f"Registry type '{registry_type}' does not match ETL job type '{etl_job_type}'"
                }
            elif etl_job_type == "generation" and registry_type != "generation":
                consistency_checks["registry_type_consistency"] = {
                    "result": ValidationResult.FAILED.value,
                    "message": f"Registry type '{registry_type}' does not match ETL job type '{etl_job_type}'"
                }
            else:
                consistency_checks["registry_type_consistency"] = {
                    "result": ValidationResult.PASSED.value,
                    "message": f"Registry type '{registry_type}' matches ETL job type '{etl_job_type}'"
                }
        
        return consistency_checks
    
    def _validate_completion_requirements(self, registry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that population completion requirements are met."""
        completion_checks = {}
        
        # Check required completion fields
        required_completion_fields = [
            "integration_status", "lifecycle_status", "overall_health_score"
        ]
        
        for field in required_completion_fields:
            if field not in registry_data:
                completion_checks[field] = {
                    "result": ValidationResult.FAILED.value,
                    "message": f"Completion field '{field}' is missing"
                }
            else:
                completion_checks[field] = {
                    "result": ValidationResult.PASSED.value,
                    "message": f"Completion field '{field}' is present"
                }
        
        # Check integration status
        if "integration_status" in registry_data:
            status = registry_data["integration_status"]
            if status not in ["active", "completed"]:
                completion_checks["integration_status_value"] = {
                    "result": ValidationResult.FAILED.value,
                    "message": f"Integration status '{status}' is not a completion status"
                }
            else:
                completion_checks["integration_status_value"] = {
                    "result": ValidationResult.PASSED.value,
                    "message": f"Integration status '{status}' indicates completion"
                }
        
        return completion_checks
    
    def _validate_data_quality(self, registry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overall data quality of the registry."""
        quality_checks = {}
        
        # Check health score
        if "overall_health_score" in registry_data:
            health_score = registry_data["overall_health_score"]
            if health_score < 50:
                quality_checks["health_score"] = {
                    "result": ValidationResult.WARNING.value,
                    "message": f"Health score {health_score} is below recommended threshold"
                }
            else:
                quality_checks["health_score"] = {
                    "result": ValidationResult.PASSED.value,
                    "message": f"Health score {health_score} is acceptable"
                }
        
        # Check data completeness
        required_fields = self._get_required_fields()
        present_fields = sum(1 for field in required_fields if field in registry_data and registry_data[field] is not None)
        completeness_ratio = present_fields / len(required_fields)
        
        if completeness_ratio < 0.8:
            quality_checks["data_completeness"] = {
                "result": ValidationResult.WARNING.value,
                "message": f"Data completeness {completeness_ratio:.1%} is below recommended threshold"
            }
        else:
            quality_checks["data_completeness"] = {
                "result": ValidationResult.PASSED.value,
                "message": f"Data completeness {completeness_ratio:.1%} is acceptable"
            }
        
        return quality_checks
    
    def _validate_business_rules(self, registry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business rules and constraints."""
        business_checks = {}
        
        # Check if registry has been activated
        if "activated_at" in registry_data and registry_data["activated_at"]:
            business_checks["activation"] = {
                "result": ValidationResult.PASSED.value,
                "message": "Registry has been activated"
            }
        else:
            business_checks["activation"] = {
                "result": ValidationResult.WARNING.value,
                "message": "Registry has not been activated"
            }
        
        # Check if steward is assigned for high-priority twins
        if registry_data.get("twin_priority") in ["critical", "emergency"]:
            if "steward_user_id" in registry_data and registry_data["steward_user_id"]:
                business_checks["steward_assignment"] = {
                    "result": ValidationResult.PASSED.value,
                    "message": "High-priority twin has assigned steward"
                }
            else:
                business_checks["steward_assignment"] = {
                    "result": ValidationResult.WARNING.value,
                    "message": "High-priority twin should have assigned steward"
                }
        
        return business_checks
    
    def _calculate_quality_score(self, field_validations: Dict[str, Any]) -> float:
        """Calculate quality score based on field validations."""
        if not field_validations:
            return 0.0
        
        passed_count = sum(
            1 for result in field_validations.values()
            if result["result"] == ValidationResult.PASSED.value
        )
        
        total_count = len(field_validations)
        return (passed_count / total_count) * 100
    
    def _calculate_enhancement_quality_score(
        self,
        etl_validations: Dict[str, Any],
        consistency_checks: Dict[str, Any]
    ) -> float:
        """Calculate quality score for ETL enhancement."""
        etl_score = self._calculate_quality_score(etl_validations)
        consistency_score = self._calculate_quality_score(consistency_checks)
        
        # Weight ETL validations more heavily
        return (etl_score * 0.7) + (consistency_score * 0.3)
    
    def _calculate_final_quality_score(
        self,
        completion_validations: Dict[str, Any],
        data_quality_checks: Dict[str, Any],
        business_rule_validations: Dict[str, Any]
    ) -> float:
        """Calculate final quality score for population completion."""
        completion_score = self._calculate_quality_score(completion_validations)
        data_quality_score = self._calculate_quality_score(data_quality_checks)
        business_rule_score = self._calculate_quality_score(business_rule_validations)
        
        # Weight completion and data quality more heavily
        return (completion_score * 0.4) + (data_quality_score * 0.4) + (business_rule_score * 0.2)
    
    def set_validation_level(self, level: ValidationLevel):
        """Set the validation level."""
        self.validation_level = level
        self.validation_rules = self._load_validation_rules()
        logger.info(f"Validation level set to: {level.value}")
    
    def get_validation_summary(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of validation results."""
        if "overall_result" not in validation_results:
            return {"error": "Invalid validation results"}
        
        summary = {
            "overall_result": validation_results["overall_result"],
            "validation_level": validation_results.get("validation_level", "unknown"),
            "timestamp": validation_results.get("timestamp"),
            "quality_score": validation_results.get("quality_score", 0),
            "total_checks": 0,
            "passed_checks": 0,
            "warning_checks": 0,
            "failed_checks": 0,
            "error_count": len(validation_results.get("errors", [])),
            "warning_count": len(validation_results.get("warnings", []))
        }
        
        # Count validation results
        for validation_type in ["field_validations", "etl_validations", "completion_validations", 
                               "data_quality_checks", "business_rule_validations"]:
            if validation_type in validation_results:
                for field, result in validation_results[validation_type].items():
                    summary["total_checks"] += 1
                    if result["result"] == ValidationResult.PASSED.value:
                        summary["passed_checks"] += 1
                    elif result["result"] == ValidationResult.WARNING.value:
                        summary["warning_checks"] += 1
                    elif result["result"] == ValidationResult.FAILED.value:
                        summary["failed_checks"] += 1
        
        return summary
