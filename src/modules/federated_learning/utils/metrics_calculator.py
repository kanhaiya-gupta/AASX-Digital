"""
Metrics Calculator
=================

Utility for calculating federated learning metrics.
"""

from typing import Dict, Any, List, Optional
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Utility for calculating federated learning metrics"""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_federation_metrics(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive federation metrics"""
        try:
            if not updates:
                return {}
            
            metrics = {}
            
            # Basic metrics
            metrics.update(self._calculate_basic_metrics(updates))
            
            # Performance metrics
            metrics.update(self._calculate_performance_metrics(updates))
            
            # Privacy metrics
            metrics.update(self._calculate_privacy_metrics(updates))
            
            # Quality metrics
            metrics.update(self._calculate_quality_metrics(updates))
            
            # Timestamp
            metrics['calculation_timestamp'] = datetime.now().isoformat()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating federation metrics: {str(e)}")
            return {}
    
    def _calculate_basic_metrics(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic federation metrics"""
        try:
            metrics = {
                'total_updates': len(updates),
                'participating_twins': len(set(update.get('twin_id') for update in updates if update.get('twin_id'))),
                'total_data_size': sum(update.get('data_size', 0) for update in updates),
                'avg_data_size': np.mean([update.get('data_size', 0) for update in updates]),
                'min_data_size': min([update.get('data_size', 0) for update in updates]),
                'max_data_size': max([update.get('data_size', 0) for update in updates])
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating basic metrics: {str(e)}")
            return {}
    
    def _calculate_performance_metrics(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        try:
            accuracies = [update.get('training_metrics', {}).get('accuracy', 0.0) for update in updates]
            losses = [update.get('training_metrics', {}).get('loss', 1.0) for update in updates]
            
            metrics = {
                'avg_accuracy': np.mean(accuracies),
                'min_accuracy': np.min(accuracies),
                'max_accuracy': np.max(accuracies),
                'std_accuracy': np.std(accuracies),
                'avg_loss': np.mean(losses),
                'min_loss': np.min(losses),
                'max_loss': np.max(losses),
                'std_loss': np.std(losses),
                'accuracy_range': np.max(accuracies) - np.min(accuracies),
                'loss_range': np.max(losses) - np.min(losses)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def _calculate_privacy_metrics(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate privacy metrics"""
        try:
            privacy_applied_count = sum(1 for update in updates if update.get('privacy_applied', False))
            noise_scales = [update.get('noise_scale', 0.0) for update in updates if update.get('noise_scale')]
            
            metrics = {
                'privacy_applied_ratio': privacy_applied_count / len(updates) if updates else 0.0,
                'avg_noise_scale': np.mean(noise_scales) if noise_scales else 0.0,
                'min_noise_scale': np.min(noise_scales) if noise_scales else 0.0,
                'max_noise_scale': np.max(noise_scales) if noise_scales else 0.0,
                'privacy_compliance_rate': privacy_applied_count / len(updates) if updates else 0.0
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating privacy metrics: {str(e)}")
            return {}
    
    def _calculate_quality_metrics(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics"""
        try:
            quality_scores = [update.get('quality_score', 0.0) for update in updates if update.get('quality_score')]
            validation_passed_count = sum(1 for update in updates if update.get('validation_passed', False))
            
            metrics = {
                'avg_quality_score': np.mean(quality_scores) if quality_scores else 0.0,
                'min_quality_score': np.min(quality_scores) if quality_scores else 0.0,
                'max_quality_score': np.max(quality_scores) if quality_scores else 0.0,
                'validation_pass_rate': validation_passed_count / len(updates) if updates else 0.0,
                'quality_compliance_rate': validation_passed_count / len(updates) if updates else 0.0
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {str(e)}")
            return {}
    
    def calculate_convergence_metrics(self, round_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate convergence metrics across rounds"""
        try:
            if len(round_metrics) < 2:
                return {}
            
            accuracies = [round_metric.get('avg_accuracy', 0.0) for round_metric in round_metrics]
            losses = [round_metric.get('avg_loss', 1.0) for round_metric in round_metrics]
            
            # Calculate convergence indicators
            accuracy_improvement = accuracies[-1] - accuracies[0] if len(accuracies) > 1 else 0.0
            loss_improvement = losses[0] - losses[-1] if len(losses) > 1 else 0.0
            
            # Calculate stability (variance in recent rounds)
            recent_rounds = min(5, len(round_metrics))
            recent_accuracies = accuracies[-recent_rounds:]
            recent_losses = losses[-recent_rounds:]
            
            metrics = {
                'total_rounds': len(round_metrics),
                'accuracy_improvement': accuracy_improvement,
                'loss_improvement': loss_improvement,
                'final_accuracy': accuracies[-1] if accuracies else 0.0,
                'final_loss': losses[-1] if losses else 1.0,
                'accuracy_stability': np.std(recent_accuracies),
                'loss_stability': np.std(recent_losses),
                'convergence_rate': self._calculate_convergence_rate(accuracies),
                'is_converged': self._check_convergence(accuracies, losses)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating convergence metrics: {str(e)}")
            return {}
    
    def _calculate_convergence_rate(self, accuracies: List[float]) -> float:
        """Calculate convergence rate"""
        try:
            if len(accuracies) < 2:
                return 0.0
            
            # Calculate average improvement per round
            improvements = [accuracies[i] - accuracies[i-1] for i in range(1, len(accuracies))]
            return np.mean(improvements)
            
        except Exception as e:
            self.logger.error(f"Error calculating convergence rate: {str(e)}")
            return 0.0
    
    def _check_convergence(self, accuracies: List[float], losses: List[float]) -> bool:
        """Check if federation has converged"""
        try:
            if len(accuracies) < 3 or len(losses) < 3:
                return False
            
            # Check if accuracy and loss have stabilized
            recent_accuracies = accuracies[-3:]
            recent_losses = losses[-3:]
            
            accuracy_stable = np.std(recent_accuracies) < 0.01  # Less than 1% variation
            loss_stable = np.std(recent_losses) < 0.01  # Less than 1% variation
            
            return accuracy_stable and loss_stable
            
        except Exception as e:
            self.logger.error(f"Error checking convergence: {str(e)}")
            return False
    
    def calculate_fairness_metrics(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate fairness metrics"""
        try:
            if not updates:
                return {}
            
            # Calculate weights for each update
            weights = []
            for update in updates:
                data_size = update.get('data_size', 1)
                accuracy = update.get('training_metrics', {}).get('accuracy', 0.5)
                weight = data_size * accuracy
                weights.append(weight)
            
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights] if total_weight > 0 else [1.0 / len(weights)] * len(weights)
            
            # Calculate fairness metrics
            metrics = {
                'weight_gini_coefficient': self._calculate_gini_coefficient(normalized_weights),
                'weight_entropy': self._calculate_entropy(normalized_weights),
                'weight_variance': np.var(normalized_weights),
                'max_weight_ratio': max(normalized_weights) / min(normalized_weights) if min(normalized_weights) > 0 else float('inf'),
                'fairness_score': 1.0 - self._calculate_gini_coefficient(normalized_weights)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating fairness metrics: {str(e)}")
            return {}
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for fairness measurement"""
        try:
            if not values:
                return 0.0
            
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            if n == 0 or sum(sorted_values) == 0:
                return 0.0
            
            cumsum = np.cumsum(sorted_values)
            return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
            
        except Exception as e:
            self.logger.error(f"Error calculating Gini coefficient: {str(e)}")
            return 0.0
    
    def _calculate_entropy(self, values: List[float]) -> float:
        """Calculate entropy for fairness measurement"""
        try:
            if not values:
                return 0.0
            
            # Filter out zero values
            non_zero_values = [v for v in values if v > 0]
            
            if not non_zero_values:
                return 0.0
            
            # Normalize to probabilities
            total = sum(non_zero_values)
            probabilities = [v / total for v in non_zero_values]
            
            # Calculate entropy
            entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
            
            return entropy
            
        except Exception as e:
            self.logger.error(f"Error calculating entropy: {str(e)}")
            return 0.0
    
    def generate_metrics_report(self, metrics: Dict[str, Any]) -> str:
        """Generate a human-readable metrics report"""
        try:
            report = "=== Federated Learning Metrics Report ===\n\n"
            
            # Basic metrics
            if 'total_updates' in metrics:
                report += "Basic Metrics:\n"
                report += f"  - Total Updates: {metrics.get('total_updates', 0)}\n"
                report += f"  - Participating Twins: {metrics.get('participating_twins', 0)}\n"
                report += f"  - Total Data Size: {metrics.get('total_data_size', 0):,}\n"
                report += f"  - Average Data Size: {metrics.get('avg_data_size', 0):.2f}\n\n"
            
            # Performance metrics
            if 'avg_accuracy' in metrics:
                report += "Performance Metrics:\n"
                report += f"  - Average Accuracy: {metrics.get('avg_accuracy', 0):.3f}\n"
                report += f"  - Accuracy Range: {metrics.get('accuracy_range', 0):.3f}\n"
                report += f"  - Average Loss: {metrics.get('avg_loss', 0):.3f}\n"
                report += f"  - Loss Range: {metrics.get('loss_range', 0):.3f}\n\n"
            
            # Privacy metrics
            if 'privacy_applied_ratio' in metrics:
                report += "Privacy Metrics:\n"
                report += f"  - Privacy Applied Ratio: {metrics.get('privacy_applied_ratio', 0):.2%}\n"
                report += f"  - Average Noise Scale: {metrics.get('avg_noise_scale', 0):.4f}\n"
                report += f"  - Privacy Compliance Rate: {metrics.get('privacy_compliance_rate', 0):.2%}\n\n"
            
            # Quality metrics
            if 'avg_quality_score' in metrics:
                report += "Quality Metrics:\n"
                report += f"  - Average Quality Score: {metrics.get('avg_quality_score', 0):.3f}\n"
                report += f"  - Validation Pass Rate: {metrics.get('validation_pass_rate', 0):.2%}\n"
                report += f"  - Quality Compliance Rate: {metrics.get('quality_compliance_rate', 0):.2%}\n\n"
            
            # Fairness metrics
            if 'fairness_score' in metrics:
                report += "Fairness Metrics:\n"
                report += f"  - Fairness Score: {metrics.get('fairness_score', 0):.3f}\n"
                report += f"  - Gini Coefficient: {metrics.get('weight_gini_coefficient', 0):.3f}\n"
                report += f"  - Weight Entropy: {metrics.get('weight_entropy', 0):.3f}\n\n"
            
            report += f"Report Generated: {metrics.get('calculation_timestamp', 'Unknown')}\n"
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating metrics report: {str(e)}")
            return "Error generating metrics report" 