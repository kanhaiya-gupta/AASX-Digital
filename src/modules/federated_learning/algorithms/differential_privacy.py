"""
Differential Privacy Algorithm
=============================

Implementation of differential privacy mechanisms for federated learning.
"""

from typing import Dict, Any, Optional, List, Union
import logging
import numpy as np
import random

logger = logging.getLogger(__name__)

class DifferentialPrivacy:
    """Differential privacy mechanisms for federated learning"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
        self.logger = logger
    
    def apply_laplace_noise(self, value: Union[float, List[float], np.ndarray], 
                          sensitivity: float = 1.0) -> Union[float, List[float], np.ndarray]:
        """Apply Laplace noise for differential privacy"""
        try:
            # Calculate noise scale
            scale = sensitivity / self.epsilon
            
            if isinstance(value, (int, float)):
                # Single value
                noise = np.random.laplace(0, scale)
                return value + noise
            
            elif isinstance(value, list):
                # List of values
                noisy_values = []
                for v in value:
                    if isinstance(v, (int, float)):
                        noise = np.random.laplace(0, scale)
                        noisy_values.append(v + noise)
                    else:
                        noisy_values.append(v)
                return noisy_values
            
            elif isinstance(value, np.ndarray):
                # NumPy array
                noise = np.random.laplace(0, scale, value.shape)
                return value + noise
            
            else:
                # Unsupported type
                return value
                
        except Exception as e:
            self.logger.error(f"Error applying Laplace noise: {str(e)}")
            return value
    
    def apply_gaussian_noise(self, value: Union[float, List[float], np.ndarray], 
                           sensitivity: float = 1.0) -> Union[float, List[float], np.ndarray]:
        """Apply Gaussian noise for differential privacy"""
        try:
            # Calculate noise scale for Gaussian mechanism
            scale = np.sqrt(2 * np.log(1.25 / self.delta)) * sensitivity / self.epsilon
            
            if isinstance(value, (int, float)):
                # Single value
                noise = np.random.normal(0, scale)
                return value + noise
            
            elif isinstance(value, list):
                # List of values
                noisy_values = []
                for v in value:
                    if isinstance(v, (int, float)):
                        noise = np.random.normal(0, scale)
                        noisy_values.append(v + noise)
                    else:
                        noisy_values.append(v)
                return noisy_values
            
            elif isinstance(value, np.ndarray):
                # NumPy array
                noise = np.random.normal(0, scale, value.shape)
                return value + noise
            
            else:
                # Unsupported type
                return value
                
        except Exception as e:
            self.logger.error(f"Error applying Gaussian noise: {str(e)}")
            return value
    
    def privatize_model_parameters(self, parameters: Dict[str, Any], 
                                 method: str = "laplace") -> Dict[str, Any]:
        """Apply differential privacy to model parameters"""
        try:
            privatized_params = {}
            
            for key, value in parameters.items():
                if isinstance(value, (int, float)):
                    # Numeric parameter
                    if method == "laplace":
                        privatized_params[key] = self.apply_laplace_noise(value)
                    elif method == "gaussian":
                        privatized_params[key] = self.apply_gaussian_noise(value)
                    else:
                        privatized_params[key] = value
                
                elif isinstance(value, list):
                    # List of numeric values
                    if all(isinstance(v, (int, float)) for v in value):
                        if method == "laplace":
                            privatized_params[key] = self.apply_laplace_noise(value)
                        elif method == "gaussian":
                            privatized_params[key] = self.apply_gaussian_noise(value)
                        else:
                            privatized_params[key] = value
                    else:
                        privatized_params[key] = value
                
                elif isinstance(value, dict):
                    # Recursively privatize nested dictionaries
                    privatized_params[key] = self.privatize_model_parameters(value, method)
                
                else:
                    # Non-numeric values remain unchanged
                    privatized_params[key] = value
            
            return privatized_params
            
        except Exception as e:
            self.logger.error(f"Error privatizing model parameters: {str(e)}")
            return parameters
    
    def calculate_sensitivity(self, parameters: Dict[str, Any]) -> float:
        """Calculate sensitivity of model parameters"""
        try:
            max_sensitivity = 0.0
            
            for key, value in parameters.items():
                if isinstance(value, (int, float)):
                    # For numeric values, sensitivity is the maximum absolute value
                    sensitivity = abs(value)
                    max_sensitivity = max(max_sensitivity, sensitivity)
                
                elif isinstance(value, list):
                    # For lists, sensitivity is the maximum absolute value
                    if all(isinstance(v, (int, float)) for v in value):
                        sensitivity = max(abs(v) for v in value)
                        max_sensitivity = max(max_sensitivity, sensitivity)
                
                elif isinstance(value, dict):
                    # Recursively calculate sensitivity for nested dictionaries
                    nested_sensitivity = self.calculate_sensitivity(value)
                    max_sensitivity = max(max_sensitivity, nested_sensitivity)
            
            return max_sensitivity
            
        except Exception as e:
            self.logger.error(f"Error calculating sensitivity: {str(e)}")
            return 1.0  # Default sensitivity
    
    def compose_privacy_budgets(self, epsilons: List[float], deltas: List[float] = None) -> Dict[str, float]:
        """Compose multiple privacy budgets"""
        try:
            if deltas is None:
                deltas = [self.delta] * len(epsilons)
            
            if len(epsilons) != len(deltas):
                raise ValueError("Number of epsilons must match number of deltas")
            
            # Basic composition
            total_epsilon = sum(epsilons)
            total_delta = sum(deltas)
            
            # Advanced composition (if needed)
            # This is a simplified version - in practice, you might use more sophisticated composition
            
            return {
                'total_epsilon': total_epsilon,
                'total_delta': total_delta,
                'composition_method': 'basic'
            }
            
        except Exception as e:
            self.logger.error(f"Error composing privacy budgets: {str(e)}")
            return {'total_epsilon': 0.0, 'total_delta': 0.0, 'composition_method': 'error'}
    
    def check_privacy_guarantees(self, epsilon: float, delta: float) -> Dict[str, Any]:
        """Check if privacy guarantees are satisfied"""
        try:
            guarantees = {
                'epsilon': epsilon,
                'delta': delta,
                'privacy_level': self._determine_privacy_level(epsilon, delta),
                'is_acceptable': epsilon <= 10.0 and delta <= 1e-5,  # Common thresholds
                'recommendations': []
            }
            
            # Add recommendations
            if epsilon > 10.0:
                guarantees['recommendations'].append("Epsilon too high - consider reducing noise")
            
            if delta > 1e-5:
                guarantees['recommendations'].append("Delta too high - consider reducing noise")
            
            if epsilon < 0.1:
                guarantees['recommendations'].append("Epsilon very low - privacy may be too restrictive")
            
            return guarantees
            
        except Exception as e:
            self.logger.error(f"Error checking privacy guarantees: {str(e)}")
            return {'error': str(e)}
    
    def _determine_privacy_level(self, epsilon: float, delta: float) -> str:
        """Determine privacy level based on epsilon and delta"""
        if epsilon <= 0.1 and delta <= 1e-6:
            return "very_high"
        elif epsilon <= 1.0 and delta <= 1e-5:
            return "high"
        elif epsilon <= 5.0 and delta <= 1e-4:
            return "medium"
        elif epsilon <= 10.0 and delta <= 1e-3:
            return "low"
        else:
            return "very_low"
    
    def get_noise_statistics(self, original_values: List[float], 
                           noisy_values: List[float]) -> Dict[str, float]:
        """Get statistics about added noise"""
        try:
            if len(original_values) != len(noisy_values):
                raise ValueError("Original and noisy values must have same length")
            
            # Calculate noise
            noise_values = [noisy - original for original, noisy in zip(original_values, noisy_values)]
            
            # Calculate statistics
            noise_array = np.array(noise_values)
            
            statistics = {
                'mean_noise': float(np.mean(noise_array)),
                'std_noise': float(np.std(noise_array)),
                'max_noise': float(np.max(noise_array)),
                'min_noise': float(np.min(noise_array)),
                'noise_range': float(np.max(noise_array) - np.min(noise_array)),
                'privacy_epsilon': self.epsilon,
                'privacy_delta': self.delta
            }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Error calculating noise statistics: {str(e)}")
            return {} 