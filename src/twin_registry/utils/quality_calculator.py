"""
Quality Calculator for Twin Registry Population
Provides quality scoring and assessment functions
"""

import logging
import math
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QualityMetric:
    """Quality metric definition"""
    name: str
    value: float
    weight: float = 1.0
    threshold: float = 0.0
    description: Optional[str] = None
    unit: Optional[str] = None


@dataclass
class QualityScore:
    """Quality score result"""
    overall_score: float
    metrics: Dict[str, QualityMetric]
    weighted_score: float
    passed_thresholds: int
    total_thresholds: int
    recommendations: List[str]
    timestamp: datetime


class QualityCalculator:
    """Quality calculator for twin registry data"""
    
    def __init__(self):
        # Default quality thresholds
        self.default_thresholds = {
            "completeness": 0.8,
            "accuracy": 0.9,
            "consistency": 0.85,
            "timeliness": 0.95,
            "validity": 0.9,
            "uniqueness": 0.95,
            "integrity": 0.9
        }
        
        # Default metric weights
        self.default_weights = {
            "completeness": 0.25,
            "accuracy": 0.25,
            "consistency": 0.20,
            "timeliness": 0.15,
            "validity": 0.10,
            "uniqueness": 0.03,
            "integrity": 0.02
        }
    
    def calculate_completeness_score(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        optional_fields: List[str]
    ) -> float:
        """Calculate completeness score based on field presence"""
        try:
            total_fields = len(required_fields) + len(optional_fields)
            if total_fields == 0:
                return 0.0
            
            score = 0.0
            
            # Check required fields (full weight)
            for field in required_fields:
                if field in data and data[field] is not None:
                    score += 1.0
            
            # Check optional fields (half weight)
            for field in optional_fields:
                if field in data and data[field] is not None:
                    score += 0.5
            
            # Calculate percentage
            completeness_score = score / total_fields
            
            return min(1.0, max(0.0, completeness_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate completeness score: {e}")
            return 0.0
    
    def calculate_accuracy_score(
        self,
        data: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> float:
        """Calculate accuracy score based on validation results"""
        try:
            if not validation_results:
                return 0.0
            
            total_validations = 0
            passed_validations = 0
            
            for field, result in validation_results.items():
                if isinstance(result, dict) and "valid" in result:
                    total_validations += 1
                    if result["valid"]:
                        passed_validations += 1
                elif isinstance(result, bool):
                    total_validations += 1
                    if result:
                        passed_validations += 1
            
            if total_validations == 0:
                return 0.0
            
            accuracy_score = passed_validations / total_validations
            return min(1.0, max(0.0, accuracy_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate accuracy score: {e}")
            return 0.0
    
    def calculate_consistency_score(
        self,
        data: Dict[str, Any],
        consistency_rules: Dict[str, Any]
    ) -> float:
        """Calculate consistency score based on consistency rules"""
        try:
            if not consistency_rules:
                return 1.0
            
            total_checks = 0
            passed_checks = 0
            
            for rule_name, rule_config in consistency_rules.items():
                if rule_config.get("enabled", True):
                    total_checks += 1
                    
                    # Check field type consistency
                    if "field_types" in rule_config:
                        for field, expected_type in rule_config["field_types"].items():
                            if field in data:
                                if self._check_field_type_consistency(data[field], expected_type):
                                    passed_checks += 1
                    
                    # Check value range consistency
                    if "value_ranges" in rule_config:
                        for field, value_range in rule_config["value_ranges"].items():
                            if field in data:
                                if self._check_value_range_consistency(data[field], value_range):
                                    passed_checks += 1
                    
                    # Check format consistency
                    if "formats" in rule_config:
                        for field, expected_format in rule_config["formats"].items():
                            if field in data:
                                if self._check_format_consistency(data[field], expected_format):
                                    passed_checks += 1
            
            if total_checks == 0:
                return 1.0
            
            consistency_score = passed_checks / total_checks
            return min(1.0, max(0.0, consistency_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate consistency score: {e}")
            return 0.0
    
    def _check_field_type_consistency(self, value: Any, expected_type: str) -> bool:
        """Check if field value matches expected type"""
        try:
            if expected_type == "string":
                return isinstance(value, str)
            elif expected_type == "integer":
                return isinstance(value, int)
            elif expected_type == "float":
                return isinstance(value, (int, float))
            elif expected_type == "boolean":
                return isinstance(value, bool)
            elif expected_type == "datetime":
                return isinstance(value, (str, datetime))
            elif expected_type == "json":
                return isinstance(value, (dict, list))
            elif expected_type == "array":
                return isinstance(value, (list, tuple))
            else:
                return True
        except Exception:
            return False
    
    def _check_value_range_consistency(self, value: Any, value_range: Dict[str, Any]) -> bool:
        """Check if field value is within expected range"""
        try:
            if not isinstance(value, (int, float)):
                return True
            
            if "min" in value_range and value < value_range["min"]:
                return False
            
            if "max" in value_range and value > value_range["max"]:
                return False
            
            return True
        except Exception:
            return True
    
    def _check_format_consistency(self, value: Any, expected_format: str) -> bool:
        """Check if field value matches expected format"""
        try:
            if not isinstance(value, str):
                return True
            
            if expected_format == "email":
                import re
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, value))
            elif expected_format == "url":
                import re
                pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
                return bool(re.match(pattern, value))
            elif expected_format == "uuid":
                import uuid
                try:
                    uuid.UUID(value)
                    return True
                except ValueError:
                    return False
            else:
                return True
        except Exception:
            return True
    
    def calculate_timeliness_score(
        self,
        data: Dict[str, Any],
        reference_time: Optional[datetime] = None
    ) -> float:
        """Calculate timeliness score based on data freshness"""
        try:
            if reference_time is None:
                reference_time = datetime.now(timezone.utc)
            
            # Look for timestamp fields
            timestamp_fields = ["created_at", "updated_at", "timestamp", "last_modified"]
            latest_timestamp = None
            
            for field in timestamp_fields:
                if field in data and data[field]:
                    try:
                        if isinstance(data[field], str):
                            dt = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                        elif isinstance(data[field], datetime):
                            dt = data[field]
                        else:
                            continue
                        
                        if latest_timestamp is None or dt > latest_timestamp:
                            latest_timestamp = dt
                    except Exception:
                        continue
            
            if latest_timestamp is None:
                return 0.5  # Default score if no timestamp found
            
            # Calculate time difference in hours
            time_diff = (reference_time - latest_timestamp).total_seconds() / 3600
            
            # Score based on recency (exponential decay)
            if time_diff <= 1:  # Within 1 hour
                return 1.0
            elif time_diff <= 24:  # Within 1 day
                return 0.95
            elif time_diff <= 168:  # Within 1 week
                return 0.8
            elif time_diff <= 720:  # Within 1 month
                return 0.6
            else:  # Older than 1 month
                return max(0.1, math.exp(-time_diff / 720))
            
        except Exception as e:
            logger.error(f"Failed to calculate timeliness score: {e}")
            return 0.5
    
    def calculate_validity_score(
        self,
        data: Dict[str, Any],
        validation_rules: Dict[str, Any]
    ) -> float:
        """Calculate validity score based on validation rules"""
        try:
            if not validation_rules:
                return 1.0
            
            total_rules = 0
            passed_rules = 0
            
            for field, rules in validation_rules.items():
                if field in data:
                    for rule_type, rule_value in rules.items():
                        total_rules += 1
                        
                        if rule_type == "required":
                            if rule_value and data[field] is not None:
                                passed_rules += 1
                        elif rule_type == "min_length":
                            if isinstance(data[field], str) and len(data[field]) >= rule_value:
                                passed_rules += 1
                        elif rule_type == "max_length":
                            if isinstance(data[field], str) and len(data[field]) <= rule_value:
                                passed_rules += 1
                        elif rule_type == "pattern":
                            import re
                            if isinstance(data[field], str) and re.match(rule_value, data[field]):
                                passed_rules += 1
                        elif rule_type == "enum":
                            if data[field] in rule_value:
                                passed_rules += 1
            
            if total_rules == 0:
                return 1.0
            
            validity_score = passed_rules / total_rules
            return min(1.0, max(0.0, validity_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate validity score: {e}")
            return 0.0
    
    def calculate_uniqueness_score(
        self,
        data: Dict[str, Any],
        uniqueness_fields: List[str]
    ) -> float:
        """Calculate uniqueness score based on field uniqueness"""
        try:
            if not uniqueness_fields:
                return 1.0
            
            # This is a simplified uniqueness check
            # In a real implementation, you would check against existing data
            unique_values = set()
            total_values = 0
            
            for field in uniqueness_fields:
                if field in data and data[field] is not None:
                    total_values += 1
                    unique_values.add(str(data[field]))
            
            if total_values == 0:
                return 1.0
            
            uniqueness_score = len(unique_values) / total_values
            return min(1.0, max(0.0, uniqueness_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate uniqueness score: {e}")
            return 1.0
    
    def calculate_integrity_score(
        self,
        data: Dict[str, Any],
        integrity_checks: Dict[str, Any]
    ) -> float:
        """Calculate integrity score based on integrity checks"""
        try:
            if not integrity_checks:
                return 1.0
            
            total_checks = 0
            passed_checks = 0
            
            for check_name, check_config in integrity_checks.items():
                if check_config.get("enabled", True):
                    total_checks += 1
                    
                    # Check referential integrity
                    if "foreign_keys" in check_config:
                        for field, reference in check_config["foreign_keys"].items():
                            if field in data and data[field] is not None:
                                # Simplified check - in real implementation, verify against reference table
                                if self._check_referential_integrity(data[field], reference):
                                    passed_checks += 1
                    
                    # Check constraint integrity
                    if "constraints" in check_config:
                        for field, constraint in check_config["constraints"].items():
                            if field in data and data[field] is not None:
                                if self._check_constraint_integrity(data[field], constraint):
                                    passed_checks += 1
            
            if total_checks == 0:
                return 1.0
            
            integrity_score = passed_checks / total_checks
            return min(1.0, max(0.0, integrity_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate integrity score: {e}")
            return 1.0
    
    def _check_referential_integrity(self, value: Any, reference: Dict[str, Any]) -> bool:
        """Check referential integrity (simplified)"""
        # In a real implementation, this would check against the reference table
        return True
    
    def _check_constraint_integrity(self, value: Any, constraint: Dict[str, Any]) -> bool:
        """Check constraint integrity"""
        try:
            if "not_null" in constraint and constraint["not_null"]:
                if value is None:
                    return False
            
            if "unique" in constraint and constraint["unique"]:
                # Simplified check - in real implementation, verify against existing data
                pass
            
            return True
        except Exception:
            return True
    
    def calculate_overall_quality_score(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        optional_fields: List[str],
        validation_results: Optional[Dict[str, Any]] = None,
        custom_weights: Optional[Dict[str, float]] = None,
        custom_thresholds: Optional[Dict[str, float]] = None
    ) -> QualityScore:
        """Calculate overall quality score"""
        try:
            # Use custom weights/thresholds or defaults
            weights = custom_weights or self.default_weights
            thresholds = custom_thresholds or self.default_thresholds
            
            # Calculate individual metric scores
            metrics = {}
            
            # Completeness
            completeness_score = self.calculate_completeness_score(data, required_fields, optional_fields)
            metrics["completeness"] = QualityMetric(
                name="completeness",
                value=completeness_score,
                weight=weights.get("completeness", 0.25),
                threshold=thresholds.get("completeness", 0.8),
                description="Data completeness based on field presence",
                unit="percentage"
            )
            
            # Accuracy
            accuracy_score = self.calculate_accuracy_score(data, validation_results or {})
            metrics["accuracy"] = QualityMetric(
                name="accuracy",
                value=accuracy_score,
                weight=weights.get("accuracy", 0.25),
                threshold=thresholds.get("accuracy", 0.9),
                description="Data accuracy based on validation results",
                unit="percentage"
            )
            
            # Consistency
            consistency_score = self.calculate_consistency_score(data, {})
            metrics["consistency"] = QualityMetric(
                name="consistency",
                value=consistency_score,
                weight=weights.get("consistency", 0.20),
                threshold=thresholds.get("consistency", 0.85),
                description="Data consistency based on rules",
                unit="percentage"
            )
            
            # Timeliness
            timeliness_score = self.calculate_timeliness_score(data)
            metrics["timeliness"] = QualityMetric(
                name="timeliness",
                value=timeliness_score,
                weight=weights.get("timeliness", 0.15),
                threshold=thresholds.get("timeliness", 0.95),
                description="Data timeliness based on freshness",
                unit="percentage"
            )
            
            # Validity
            validity_score = self.calculate_validity_score(data, {})
            metrics["validity"] = QualityMetric(
                name="validity",
                value=validity_score,
                weight=weights.get("validity", 0.10),
                threshold=thresholds.get("validity", 0.9),
                description="Data validity based on rules",
                unit="percentage"
            )
            
            # Uniqueness
            uniqueness_score = self.calculate_uniqueness_score(data, [])
            metrics["uniqueness"] = QualityMetric(
                name="uniqueness",
                value=uniqueness_score,
                weight=weights.get("uniqueness", 0.03),
                threshold=thresholds.get("uniqueness", 0.95),
                description="Data uniqueness",
                unit="percentage"
            )
            
            # Integrity
            integrity_score = self.calculate_integrity_score(data, {})
            metrics["integrity"] = QualityMetric(
                name="integrity",
                value=integrity_score,
                weight=weights.get("integrity", 0.02),
                threshold=thresholds.get("integrity", 0.9),
                description="Data integrity based on constraints",
                unit="percentage"
            )
            
            # Calculate weighted score
            weighted_score = sum(
                metric.value * metric.weight for metric in metrics.values()
            )
            
            # Calculate overall score (simple average)
            overall_score = sum(metric.value for metric in metrics.values()) / len(metrics)
            
            # Check thresholds
            passed_thresholds = sum(
                1 for metric in metrics.values() if metric.value >= metric.threshold
            )
            total_thresholds = len(metrics)
            
            # Generate recommendations
            recommendations = []
            for metric_name, metric in metrics.items():
                if metric.value < metric.threshold:
                    recommendations.append(
                        f"Improve {metric_name}: current {metric.value:.2%}, target {metric.threshold:.2%}"
                    )
            
            if not recommendations:
                recommendations.append("All quality metrics meet thresholds")
            
            # Create quality score result
            quality_score = QualityScore(
                overall_score=overall_score,
                metrics=metrics,
                weighted_score=weighted_score,
                passed_thresholds=passed_thresholds,
                total_thresholds=total_thresholds,
                recommendations=recommendations,
                timestamp=datetime.now(timezone.utc)
            )
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Failed to calculate overall quality score: {e}")
            
            # Return error result
            return QualityScore(
                overall_score=0.0,
                metrics={},
                weighted_score=0.0,
                passed_thresholds=0,
                total_thresholds=0,
                recommendations=[f"Error calculating quality score: {e}"],
                timestamp=datetime.now(timezone.utc)
            )
    
    def get_quality_summary(self, quality_score: QualityScore) -> Dict[str, Any]:
        """Get a summary of quality assessment"""
        try:
            summary = {
                "overall_score": round(quality_score.overall_score, 3),
                "weighted_score": round(quality_score.weighted_score, 3),
                "passed_thresholds": quality_score.passed_thresholds,
                "total_thresholds": quality_score.total_thresholds,
                "success_rate": round(
                    quality_score.passed_thresholds / quality_score.total_thresholds * 100, 1
                ) if quality_score.total_thresholds > 0 else 0,
                "recommendations": quality_score.recommendations,
                "timestamp": quality_score.timestamp.isoformat(),
                "metrics": {}
            }
            
            # Add individual metric details
            for metric_name, metric in quality_score.metrics.items():
                summary["metrics"][metric_name] = {
                    "value": round(metric.value, 3),
                    "weight": round(metric.weight, 3),
                    "threshold": round(metric.threshold, 3),
                    "passed": metric.value >= metric.threshold,
                    "description": metric.description,
                    "unit": metric.unit
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get quality summary: {e}")
            return {
                "error": str(e),
                "overall_score": 0.0
            }
