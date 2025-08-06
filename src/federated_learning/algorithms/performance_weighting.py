"""
Performance Weighting Algorithm
==============================

Implementation of performance-based weighting for federated learning.
"""

from typing import Dict, Any, Optional, List
import logging
import numpy as np

logger = logging.getLogger(__name__)

class PerformanceWeighting:
    """Performance-based weighting for federated learning"""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_weight(self, accuracy: float, loss: float, data_size: int) -> float:
        """Calculate weight based on performance metrics"""
        try:
            # Normalize metrics to [0, 1] range
            normalized_accuracy = max(0.0, min(1.0, accuracy))
            normalized_loss = max(0.0, min(1.0, 1.0 - loss))  # Convert loss to gain
            normalized_data_size = min(1.0, data_size / 10000.0)  # Normalize to 10k samples
            
            # Calculate individual component weights
            accuracy_weight = self._calculate_accuracy_weight(normalized_accuracy)
            loss_weight = self._calculate_loss_weight(normalized_loss)
            data_weight = self._calculate_data_weight(normalized_data_size)
            
            # Combine weights (configurable weights)
            combined_weight = (
                0.4 * accuracy_weight +
                0.3 * loss_weight +
                0.3 * data_weight
            )
            
            # Ensure weight is in valid range
            final_weight = max(0.0, min(1.0, combined_weight))
            
            self.logger.debug(f"Weight calculation: accuracy={accuracy_weight:.3f}, "
                            f"loss={loss_weight:.3f}, data={data_weight:.3f}, "
                            f"final={final_weight:.3f}")
            
            return final_weight
            
        except Exception as e:
            self.logger.error(f"Error calculating performance weight: {str(e)}")
            return 0.5  # Default weight
    
    def calculate_weights_batch(self, metrics_list: List[Dict[str, Any]]) -> List[float]:
        """Calculate weights for a batch of twins"""
        try:
            weights = []
            
            for metrics in metrics_list:
                accuracy = metrics.get('accuracy', 0.5)
                loss = metrics.get('loss', 1.0)
                data_size = metrics.get('data_size', 1000)
                
                weight = self.calculate_weight(accuracy, loss, data_size)
                weights.append(weight)
            
            # Normalize weights to sum to 1
            total_weight = sum(weights)
            if total_weight > 0:
                normalized_weights = [w / total_weight for w in weights]
            else:
                # Equal weights if all are zero
                normalized_weights = [1.0 / len(weights)] * len(weights)
            
            return normalized_weights
            
        except Exception as e:
            self.logger.error(f"Error calculating batch weights: {str(e)}")
            return [1.0 / len(metrics_list)] * len(metrics_list)
    
    def _calculate_accuracy_weight(self, accuracy: float) -> float:
        """Calculate weight based on accuracy"""
        # Use sigmoid function for smooth weighting
        # Higher accuracy gets exponentially higher weight
        return 1.0 / (1.0 + np.exp(-5.0 * (accuracy - 0.5)))
    
    def _calculate_loss_weight(self, loss_gain: float) -> float:
        """Calculate weight based on loss (converted to gain)"""
        # Linear weighting for loss
        return loss_gain
    
    def _calculate_data_weight(self, data_size: float) -> float:
        """Calculate weight based on data size"""
        # Logarithmic weighting for data size
        # Prevents very large datasets from dominating
        return np.log(1.0 + data_size) / np.log(1.0 + 1.0)
    
    def get_performance_ranking(self, twins_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank twins by performance"""
        try:
            ranked_twins = []
            
            for i, metrics in enumerate(twins_metrics):
                accuracy = metrics.get('accuracy', 0.5)
                loss = metrics.get('loss', 1.0)
                data_size = metrics.get('data_size', 1000)
                
                weight = self.calculate_weight(accuracy, loss, data_size)
                
                ranked_twin = {
                    'twin_id': metrics.get('twin_id', f'twin_{i}'),
                    'accuracy': accuracy,
                    'loss': loss,
                    'data_size': data_size,
                    'weight': weight,
                    'overall_score': self._calculate_overall_score(accuracy, loss, data_size)
                }
                
                ranked_twins.append(ranked_twin)
            
            # Sort by overall score (descending)
            ranked_twins.sort(key=lambda x: x['overall_score'], reverse=True)
            
            # Add ranking
            for i, twin in enumerate(ranked_twins):
                twin['rank'] = i + 1
            
            return ranked_twins
            
        except Exception as e:
            self.logger.error(f"Error ranking twins by performance: {str(e)}")
            return []
    
    def _calculate_overall_score(self, accuracy: float, loss: float, data_size: int) -> float:
        """Calculate overall performance score"""
        # Normalize metrics
        normalized_accuracy = max(0.0, min(1.0, accuracy))
        normalized_loss = max(0.0, min(1.0, 1.0 - loss))
        normalized_data_size = min(1.0, data_size / 10000.0)
        
        # Calculate weighted score
        score = (
            0.5 * normalized_accuracy +
            0.3 * normalized_loss +
            0.2 * normalized_data_size
        )
        
        return score
    
    def get_weight_distribution(self, weights: List[float]) -> Dict[str, float]:
        """Get statistics about weight distribution"""
        try:
            if not weights:
                return {}
            
            weights_array = np.array(weights)
            
            distribution = {
                'mean': float(np.mean(weights_array)),
                'std': float(np.std(weights_array)),
                'min': float(np.min(weights_array)),
                'max': float(np.max(weights_array)),
                'median': float(np.median(weights_array)),
                'total': float(np.sum(weights_array)),
                'count': len(weights)
            }
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"Error calculating weight distribution: {str(e)}")
            return {}
    
    def adjust_weights_for_fairness(self, weights: List[float], fairness_factor: float = 0.1) -> List[float]:
        """Adjust weights to ensure fairness"""
        try:
            if not weights:
                return weights
            
            # Calculate current distribution
            distribution = self.get_weight_distribution(weights)
            
            # Apply fairness adjustment
            adjusted_weights = []
            for weight in weights:
                # Reduce extreme weights
                if weight > distribution['mean'] + distribution['std']:
                    adjusted_weight = weight * (1.0 - fairness_factor)
                elif weight < distribution['mean'] - distribution['std']:
                    adjusted_weight = weight * (1.0 + fairness_factor)
                else:
                    adjusted_weight = weight
                
                adjusted_weights.append(adjusted_weight)
            
            # Renormalize
            total_weight = sum(adjusted_weights)
            if total_weight > 0:
                normalized_weights = [w / total_weight for w in adjusted_weights]
            else:
                normalized_weights = [1.0 / len(weights)] * len(weights)
            
            return normalized_weights
            
        except Exception as e:
            self.logger.error(f"Error adjusting weights for fairness: {str(e)}")
            return weights 