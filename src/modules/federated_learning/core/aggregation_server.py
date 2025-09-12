"""
Aggregation Server
=================

Server for aggregating federated updates.
"""

from typing import List, Dict, Any, Optional
import logging
import numpy as np
from datetime import datetime

from ..algorithms.fedavg import FedAvgAlgorithm
from ..algorithms.secure_aggregation import SecureAggregationAlgorithm
from ..algorithms.performance_weighting import PerformanceWeightingAlgorithm

logger = logging.getLogger(__name__)

class AggregationServer:
    """Server for aggregating federated updates"""
    
    def __init__(self):
        self.fedavg_algorithm = FedAvgAlgorithm()
        self.secure_aggregation = SecureAggregationAlgorithm()
        self.performance_weighting = PerformanceWeightingAlgorithm()
    
    def aggregate_models(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate model updates using FedAvg"""
        try:
            logger.info(f"Aggregating {len(updates)} model updates")
            
            if not updates:
                raise ValueError("No updates provided for aggregation")
            
            # Extract model parameters from updates
            model_parameters = []
            twin_ids = []
            weights = []
            
            for update in updates:
                twin_id = update.get('twin_id')
                parameters = update.get('model_parameters', {})
                
                if twin_id and parameters:
                    model_parameters.append(parameters)
                    twin_ids.append(twin_id)
                    
                    # Calculate weight based on data size or performance
                    data_size = update.get('data_size', 1)
                    performance = update.get('training_metrics', {}).get('accuracy', 0.5)
                    weight = self._calculate_weight(data_size, performance)
                    weights.append(weight)
            
            if not model_parameters:
                raise ValueError("No valid model parameters found in updates")
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                normalized_weights = [w / total_weight for w in weights]
            else:
                normalized_weights = [1.0 / len(weights)] * len(weights)
            
            # Perform federated averaging
            aggregated_parameters = self.fedavg_algorithm.aggregate(
                model_parameters, 
                normalized_weights
            )
            
            # Create aggregated model
            aggregated_model = {
                'model_parameters': aggregated_parameters,
                'aggregation_metadata': {
                    'method': 'fedavg',
                    'participating_twins': twin_ids,
                    'weights': normalized_weights,
                    'aggregation_timestamp': datetime.now().isoformat(),
                    'total_updates': len(updates)
                },
                'model_type': 'federated_model',
                'version': '1.0.0'
            }
            
            logger.info(f"Successfully aggregated {len(updates)} model updates")
            
            return aggregated_model
            
        except Exception as e:
            logger.error(f"Error aggregating models: {str(e)}")
            raise
    
    def calculate_weights(self, updates: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance-based weights"""
        try:
            logger.info("Calculating performance-based weights")
            
            weights = {}
            
            for update in updates:
                twin_id = update.get('twin_id')
                if not twin_id:
                    continue
                
                # Get performance metrics
                training_metrics = update.get('training_metrics', {})
                accuracy = training_metrics.get('accuracy', 0.5)
                loss = training_metrics.get('loss', 1.0)
                data_size = update.get('data_size', 1)
                
                # Calculate weight using performance weighting algorithm
                weight = self.performance_weighting.calculate_weight(
                    accuracy=accuracy,
                    loss=loss,
                    data_size=data_size
                )
                
                weights[twin_id] = weight
            
            logger.info(f"Calculated weights for {len(weights)} twins")
            
            return weights
            
        except Exception as e:
            logger.error(f"Error calculating weights: {str(e)}")
            return {}
    
    def secure_aggregation(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform secure aggregation with privacy"""
        try:
            logger.info("Performing secure aggregation")
            
            # Apply secure aggregation protocol
            secure_updates = self.secure_aggregation.secure_aggregate(updates)
            
            # Aggregate the secure updates
            aggregated_model = self.aggregate_models(secure_updates)
            
            # Add security metadata
            aggregated_model['security_metadata'] = {
                'secure_aggregation': True,
                'privacy_level': 'high',
                'encryption_method': 'homomorphic_encryption'
            }
            
            logger.info("Secure aggregation completed successfully")
            
            return aggregated_model
            
        except Exception as e:
            logger.error(f"Error in secure aggregation: {str(e)}")
            raise
    
    def update_global_model(self, global_model: Dict[str, Any], aggregated: Dict[str, Any]) -> Dict[str, Any]:
        """Update global model with aggregated updates"""
        try:
            logger.info("Updating global model with aggregated updates")
            
            if not global_model:
                # Initialize new global model
                global_model = {
                    'model_type': 'federated_model',
                    'version': '1.0.0',
                    'parameters': {},
                    'created_at': datetime.now().isoformat(),
                    'update_history': []
                }
            
            # Update model parameters
            old_parameters = global_model.get('parameters', {})
            new_parameters = aggregated.get('model_parameters', {})
            
            # Merge parameters (simple averaging for now)
            updated_parameters = self._merge_parameters(old_parameters, new_parameters)
            
            # Update global model
            updated_global_model = global_model.copy()
            updated_global_model['parameters'] = updated_parameters
            updated_global_model['last_updated'] = datetime.now().isoformat()
            updated_global_model['version'] = self._increment_version(global_model.get('version', '1.0.0'))
            
            # Add to update history
            update_history = updated_global_model.get('update_history', [])
            update_history.append({
                'timestamp': datetime.now().isoformat(),
                'aggregation_metadata': aggregated.get('aggregation_metadata', {}),
                'participating_twins': aggregated.get('aggregation_metadata', {}).get('participating_twins', [])
            })
            updated_global_model['update_history'] = update_history[-10:]  # Keep last 10 updates
            
            logger.info("Global model updated successfully")
            
            return updated_global_model
            
        except Exception as e:
            logger.error(f"Error updating global model: {str(e)}")
            raise
    
    def _calculate_weight(self, data_size: int, performance: float) -> float:
        """Calculate weight based on data size and performance"""
        # Simple weight calculation
        # In practice, this could be more sophisticated
        size_weight = min(data_size / 1000.0, 1.0)  # Normalize data size
        performance_weight = max(performance, 0.1)  # Ensure minimum weight
        
        # Combine weights (can be adjusted based on requirements)
        combined_weight = 0.7 * size_weight + 0.3 * performance_weight
        
        return combined_weight
    
    def _merge_parameters(self, old_params: Dict[str, Any], new_params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge old and new parameters"""
        merged_params = old_params.copy()
        
        for key, new_value in new_params.items():
            if key in merged_params:
                old_value = merged_params[key]
                
                # If both are numeric, average them
                if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                    merged_params[key] = (old_value + new_value) / 2.0
                else:
                    # For non-numeric values, use the new value
                    merged_params[key] = new_value
            else:
                # New parameter
                merged_params[key] = new_value
        
        return merged_params
    
    def _increment_version(self, version: str) -> str:
        """Increment version number"""
        try:
            # Simple version increment (e.g., "1.0.0" -> "1.0.1")
            parts = version.split('.')
            if len(parts) >= 3:
                major, minor, patch = parts[0], parts[1], int(parts[2])
                return f"{major}.{minor}.{patch + 1}"
            else:
                return f"{version}.1"
        except:
            return "1.0.1" 