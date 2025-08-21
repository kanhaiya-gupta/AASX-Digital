"""
Data Validator
=============

Validate data quality for federated learning.
"""

from typing import Dict, Any, List, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class DataValidator:
    """Validate data quality for federated learning"""
    
    def __init__(self):
        self.logger = logger
    
    def validate_features(self, features: List[float]) -> bool:
        """Validate extracted features"""
        try:
            if not features:
                self.logger.warning("No features provided for validation")
                return False
            
            # Check for NaN values
            if any(np.isnan(feature) for feature in features):
                self.logger.warning("Features contain NaN values")
                return False
            
            # Check for infinite values
            if any(np.isinf(feature) for feature in features):
                self.logger.warning("Features contain infinite values")
                return False
            
            # Check for reasonable range
            if any(abs(feature) > 1e6 for feature in features):
                self.logger.warning("Features contain extremely large values")
                return False
            
            # Check feature count
            if len(features) < 1:
                self.logger.warning("Too few features")
                return False
            
            if len(features) > 10000:
                self.logger.warning("Too many features")
                return False
            
            self.logger.info(f"Features validation passed: {len(features)} features")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating features: {str(e)}")
            return False
    
    def validate_training_data(self, training_data: Dict[str, Any]) -> bool:
        """Validate training data structure"""
        try:
            required_keys = ['features', 'training_samples', 'validation_samples']
            
            for key in required_keys:
                if key not in training_data:
                    self.logger.warning(f"Missing required key: {key}")
                    return False
            
            # Validate features
            features = training_data.get('features', [])
            if not self.validate_features(features):
                return False
            
            # Validate training samples
            training_samples = training_data.get('training_samples', [])
            if not self._validate_samples(training_samples):
                return False
            
            # Validate validation samples
            validation_samples = training_data.get('validation_samples', [])
            if not self._validate_samples(validation_samples):
                return False
            
            self.logger.info("Training data validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating training data: {str(e)}")
            return False
    
    def _validate_samples(self, samples: List[Dict[str, Any]]) -> bool:
        """Validate sample structure"""
        try:
            if not isinstance(samples, list):
                self.logger.warning("Samples must be a list")
                return False
            
            for i, sample in enumerate(samples):
                if not isinstance(sample, dict):
                    self.logger.warning(f"Sample {i} must be a dictionary")
                    return False
                
                # Check required keys
                required_keys = ['features', 'target']
                for key in required_keys:
                    if key not in sample:
                        self.logger.warning(f"Sample {i} missing required key: {key}")
                        return False
                
                # Validate features in sample
                sample_features = sample.get('features', [])
                if not self.validate_features(sample_features):
                    self.logger.warning(f"Sample {i} has invalid features")
                    return False
                
                # Validate target
                target = sample.get('target')
                if not isinstance(target, (int, float)) or np.isnan(target) or np.isinf(target):
                    self.logger.warning(f"Sample {i} has invalid target")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating samples: {str(e)}")
            return False
    
    def validate_model_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate model parameters"""
        try:
            if not isinstance(parameters, dict):
                self.logger.warning("Model parameters must be a dictionary")
                return False
            
            for key, value in parameters.items():
                if isinstance(value, (int, float)):
                    # Check for NaN or infinite values
                    if np.isnan(value) or np.isinf(value):
                        self.logger.warning(f"Parameter {key} has invalid value: {value}")
                        return False
                    
                    # Check for reasonable range
                    if abs(value) > 1e6:
                        self.logger.warning(f"Parameter {key} has extremely large value: {value}")
                        return False
                
                elif isinstance(value, list):
                    # Validate list parameters
                    if not self._validate_list_parameter(value):
                        self.logger.warning(f"Parameter {key} has invalid list value")
                        return False
                
                elif isinstance(value, dict):
                    # Recursively validate nested parameters
                    if not self.validate_model_parameters(value):
                        self.logger.warning(f"Nested parameter {key} validation failed")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating model parameters: {str(e)}")
            return False
    
    def _validate_list_parameter(self, param_list: List[Any]) -> bool:
        """Validate list parameter"""
        try:
            for i, value in enumerate(param_list):
                if isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        self.logger.warning(f"List parameter element {i} has invalid value: {value}")
                        return False
                    
                    if abs(value) > 1e6:
                        self.logger.warning(f"List parameter element {i} has extremely large value: {value}")
                        return False
                
                elif isinstance(value, list):
                    # Recursively validate nested lists
                    if not self._validate_list_parameter(value):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating list parameter: {str(e)}")
            return False
    
    def calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score"""
        try:
            score = 0.0
            checks = 0
            
            # Check data completeness
            if data:
                completeness_score = self._check_completeness(data)
                score += completeness_score
                checks += 1
            
            # Check data consistency
            consistency_score = self._check_consistency(data)
            score += consistency_score
            checks += 1
            
            # Check data validity
            validity_score = self._check_validity(data)
            score += validity_score
            checks += 1
            
            # Calculate average score
            if checks > 0:
                final_score = score / checks
            else:
                final_score = 0.0
            
            self.logger.info(f"Data quality score: {final_score:.3f}")
            return final_score
            
        except Exception as e:
            self.logger.error(f"Error calculating data quality score: {str(e)}")
            return 0.0
    
    def _check_completeness(self, data: Dict[str, Any]) -> float:
        """Check data completeness"""
        try:
            if not data:
                return 0.0
            
            # Count non-empty values
            total_keys = len(data)
            non_empty_keys = 0
            
            for key, value in data.items():
                if value is not None and value != "":
                    non_empty_keys += 1
            
            completeness = non_empty_keys / total_keys if total_keys > 0 else 0.0
            return completeness
            
        except Exception as e:
            self.logger.error(f"Error checking completeness: {str(e)}")
            return 0.0
    
    def _check_consistency(self, data: Dict[str, Any]) -> float:
        """Check data consistency"""
        try:
            if not data:
                return 0.0
            
            # Simple consistency check - count consistent data types
            data_types = {}
            for key, value in data.items():
                data_type = type(value).__name__
                data_types[data_type] = data_types.get(data_type, 0) + 1
            
            # Higher score for more consistent data types
            max_count = max(data_types.values()) if data_types else 0
            total_count = sum(data_types.values())
            
            consistency = max_count / total_count if total_count > 0 else 0.0
            return consistency
            
        except Exception as e:
            self.logger.error(f"Error checking consistency: {str(e)}")
            return 0.0
    
    def _check_validity(self, data: Dict[str, Any]) -> float:
        """Check data validity"""
        try:
            if not data:
                return 0.0
            
            valid_count = 0
            total_count = 0
            
            for key, value in data.items():
                total_count += 1
                
                # Check if value is valid
                if value is not None and value != "":
                    if isinstance(value, (int, float)):
                        if not np.isnan(value) and not np.isinf(value):
                            valid_count += 1
                    else:
                        valid_count += 1
            
            validity = valid_count / total_count if total_count > 0 else 0.0
            return validity
            
        except Exception as e:
            self.logger.error(f"Error checking validity: {str(e)}")
            return 0.0 