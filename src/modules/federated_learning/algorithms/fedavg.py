"""
FedAvg Algorithm
===============

Implementation of Federated Averaging (FedAvg) algorithm.
"""

from typing import List, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FedAvg:
    """Federated Averaging (FedAvg) algorithm implementation"""
    
    def __init__(self):
        self.logger = logger
    
    def aggregate(self, model_parameters: List[Dict[str, Any]], weights: List[float]) -> Dict[str, Any]:
        """Aggregate model parameters using weighted averaging"""
        try:
            if not model_parameters or not weights:
                raise ValueError("Model parameters and weights cannot be empty")
            
            if len(model_parameters) != len(weights):
                raise ValueError("Number of model parameters must match number of weights")
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight <= 0:
                raise ValueError("Total weight must be positive")
            
            normalized_weights = [w / total_weight for w in weights]
            
            # Initialize aggregated parameters
            aggregated_params = {}
            
            # Get all parameter keys from all models
            all_keys = set()
            for params in model_parameters:
                all_keys.update(params.keys())
            
            # Aggregate each parameter
            for key in all_keys:
                aggregated_value = self._aggregate_parameter(
                    [params.get(key) for params in model_parameters],
                    normalized_weights
                )
                aggregated_params[key] = aggregated_value
            
            self.logger.info(f"Successfully aggregated {len(model_parameters)} models using FedAvg")
            
            return aggregated_params
            
        except Exception as e:
            self.logger.error(f"Error in FedAvg aggregation: {str(e)}")
            raise
    
    def _aggregate_parameter(self, values: List[Any], weights: List[float]) -> Any:
        """Aggregate a single parameter across all models"""
        if not values or not weights:
            return None
        
        # Filter out None values
        valid_values = []
        valid_weights = []
        
        for value, weight in zip(values, weights):
            if value is not None:
                valid_values.append(value)
                valid_weights.append(weight)
        
        if not valid_values:
            return None
        
        # Normalize weights for valid values
        total_weight = sum(valid_weights)
        if total_weight <= 0:
            return valid_values[0]  # Return first value if no valid weights
        
        normalized_weights = [w / total_weight for w in valid_weights]
        
        # Handle different data types
        first_value = valid_values[0]
        
        if isinstance(first_value, (int, float)):
            # Numeric values - weighted average
            return sum(v * w for v, w in zip(valid_values, normalized_weights))
        
        elif isinstance(first_value, list):
            # Lists - element-wise weighted average
            return self._aggregate_list(valid_values, normalized_weights)
        
        elif isinstance(first_value, dict):
            # Dictionaries - recursive aggregation
            return self._aggregate_dict(valid_values, normalized_weights)
        
        elif isinstance(first_value, np.ndarray):
            # NumPy arrays - weighted average
            return self._aggregate_numpy_array(valid_values, normalized_weights)
        
        else:
            # Other types - return most common value or first value
            return self._get_most_common_value(valid_values, normalized_weights)
    
    def _aggregate_list(self, lists: List[List], weights: List[float]) -> List:
        """Aggregate lists element-wise"""
        if not lists:
            return []
        
        # Find maximum length
        max_length = max(len(lst) for lst in lists)
        
        # Pad shorter lists with None
        padded_lists = []
        for lst in lists:
            padded = lst + [None] * (max_length - len(lst))
            padded_lists.append(padded)
        
        # Aggregate each position
        aggregated = []
        for i in range(max_length):
            values_at_position = [lst[i] for lst in padded_lists]
            aggregated_value = self._aggregate_parameter(values_at_position, weights)
            aggregated.append(aggregated_value)
        
        return aggregated
    
    def _aggregate_dict(self, dicts: List[Dict], weights: List[float]) -> Dict:
        """Aggregate dictionaries recursively"""
        if not dicts:
            return {}
        
        # Get all keys
        all_keys = set()
        for d in dicts:
            all_keys.update(d.keys())
        
        # Aggregate each key
        aggregated = {}
        for key in all_keys:
            values = [d.get(key) for d in dicts]
            aggregated_value = self._aggregate_parameter(values, weights)
            aggregated[key] = aggregated_value
        
        return aggregated
    
    def _aggregate_numpy_array(self, arrays: List[np.ndarray], weights: List[float]) -> np.ndarray:
        """Aggregate NumPy arrays"""
        if not arrays:
            return np.array([])
        
        # Ensure all arrays have the same shape
        shapes = [arr.shape for arr in arrays]
        if len(set(shapes)) > 1:
            raise ValueError("All NumPy arrays must have the same shape")
        
        # Weighted average
        weighted_sum = np.zeros_like(arrays[0], dtype=float)
        for arr, weight in zip(arrays, weights):
            weighted_sum += arr * weight
        
        return weighted_sum
    
    def _get_most_common_value(self, values: List[Any], weights: List[float]) -> Any:
        """Get the most common value, weighted by weights"""
        if not values:
            return None
        
        # Count occurrences weighted by weights
        value_counts = {}
        for value, weight in zip(values, weights):
            if value in value_counts:
                value_counts[value] += weight
            else:
                value_counts[value] = weight
        
        # Return value with highest weight
        return max(value_counts.items(), key=lambda x: x[1])[0]
    
    def calculate_weights(self, data_sizes: List[int], accuracies: List[float] = None) -> List[float]:
        """Calculate aggregation weights based on data size and accuracy"""
        if not data_sizes:
            return []
        
        # Base weights from data size
        size_weights = np.array(data_sizes, dtype=float)
        
        if accuracies and len(accuracies) == len(data_sizes):
            # Combine data size and accuracy
            accuracy_weights = np.array(accuracies, dtype=float)
            
            # Normalize both
            size_weights = size_weights / np.sum(size_weights) if np.sum(size_weights) > 0 else size_weights
            accuracy_weights = accuracy_weights / np.sum(accuracy_weights) if np.sum(accuracy_weights) > 0 else accuracy_weights
            
            # Combine (70% data size, 30% accuracy)
            combined_weights = 0.7 * size_weights + 0.3 * accuracy_weights
        else:
            # Use only data size
            combined_weights = size_weights
        
        # Normalize
        if np.sum(combined_weights) > 0:
            combined_weights = combined_weights / np.sum(combined_weights)
        else:
            # Equal weights if all are zero
            combined_weights = np.ones(len(data_sizes)) / len(data_sizes)
        
        return combined_weights.tolist() 