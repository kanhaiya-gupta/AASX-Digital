"""
Federation Server
Aggregates models from all twins with performance-based weighting
"""

import logging
import random
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class FederationServer:
    """Federation server for aggregating models from all twins"""
    
    def __init__(self):
        self.global_rag_model = self.initialize_global_rag_model()
        self.aggregation_round = 0
        self.twin_contributions = {}
        self.quality_assessor = QualityAssessor()
        self.security_validator = SecurityValidator()
        self.performance_optimizer = PerformanceOptimizer()
        self.federation_history = []
        
        logger.info("🔗 Federation Server initialized")
    
    def initialize_global_rag_model(self) -> Dict[str, Any]:
        """Initialize global RAG model"""
        return {
            'encoder': {
                'weights': [random.random() for _ in range(100)],
                'architecture': 'transformer',
                'parameters': 1000000
            },
            'retriever': {
                'weights': [random.random() for _ in range(50)],
                'architecture': 'dense_retriever',
                'parameters': 500000
            },
            'generator': {
                'weights': [random.random() for _ in range(75)],
                'architecture': 'gpt_style',
                'parameters': 750000
            },
            'twin_adapters': {
                'twin_1': {'weights': [random.random() for _ in range(25)]},
                'twin_2': {'weights': [random.random() for _ in range(25)]},
                'twin_3': {'weights': [random.random() for _ in range(25)]}
            }
        }
    
    def initialize_federation(self, twins: Dict[str, Any]):
        """Initialize federation with twin information"""
        self.twins = twins
        logger.info(f"✅ Federation initialized with {len(twins)} twins")
    
    def get_global_model_weights(self) -> Dict[str, Any]:
        """Get current global model weights"""
        return self.global_rag_model
    
    def aggregate_twin_models(self, local_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate models from all twins with performance-based weighting"""
        logger.info(f"🔄 Aggregating models from {len(local_updates)} twins")
        
        # Security validation
        validated_updates = self.security_validator.validate_updates(local_updates)
        
        # Quality assessment
        quality_scores = self.quality_assessor.assess_updates(validated_updates)
        
        # Performance-based weighting
        weights = self.calculate_performance_based_weights(validated_updates, quality_scores)
        
        # FedAvg aggregation with differential privacy
        aggregated_weights = self.secure_aggregation(validated_updates, weights)
        
        # Update global model
        self.global_rag_model.update(aggregated_weights)
        self.aggregation_round += 1
        
        # Track twin contributions and performance
        self.track_federation_metrics(validated_updates, quality_scores)
        
        logger.info(f"✅ Model aggregation completed for round {self.aggregation_round}")
        
        return self.global_rag_model
    
    def calculate_performance_based_weights(self, updates: List[Dict], quality_scores: Dict) -> Dict[str, float]:
        """Calculate weights based on twin performance and health scores"""
        weights = {}
        total_weight = 0
        
        for update in updates:
            twin_id = update['twin_id']
            performance_metrics = update.get('performance_metrics', {})
            
            # Multi-factor weight calculation
            data_quality = quality_scores.get(twin_id, 0.5)
            data_volume = update.get('data_size', 1000)
            health_score = performance_metrics.get('health_score', 75.0)
            response_time = performance_metrics.get('response_time', 2.0)
            error_rate = performance_metrics.get('error_rate', 1.0)
            
            # Performance-based weight formula
            # Higher health score = higher weight
            # Lower response time = higher weight (for real-time twins)
            # Lower error rate = higher weight
            
            performance_score = (
                (health_score / 100) * 0.3 +
                (1 / (1 + response_time)) * 0.2 +
                (1 - error_rate/100) * 0.2 +
                data_quality * 0.3
            )
            
            weights[twin_id] = performance_score
            total_weight += performance_score
        
        # Normalize weights
        if total_weight > 0:
            for twin_id in weights:
                weights[twin_id] /= total_weight
        
        logger.info(f"📊 Calculated weights: {weights}")
        return weights
    
    def secure_aggregation(self, updates: List[Dict], weights: Dict[str, float]) -> Dict[str, Any]:
        """Perform secure aggregation with differential privacy"""
        aggregated_weights = {
            'encoder': {'weights': [0.0] * 100},
            'retriever': {'weights': [0.0] * 50},
            'generator': {'weights': [0.0] * 75},
            'twin_adapters': {
                'twin_1': {'weights': [0.0] * 25},
                'twin_2': {'weights': [0.0] * 25},
                'twin_3': {'weights': [0.0] * 25}
            }
        }
        
        # Weighted aggregation
        for update in updates:
            twin_id = update['twin_id']
            weight = weights.get(twin_id, 0.0)
            updates_data = update.get('updates', {})
            
            # Aggregate encoder weights
            if 'encoder_updates' in updates_data:
                for i, update_val in enumerate(updates_data['encoder_updates']):
                    if i < len(aggregated_weights['encoder']['weights']):
                        aggregated_weights['encoder']['weights'][i] += update_val * weight
            
            # Aggregate retriever weights
            if 'retriever_updates' in updates_data:
                for i, update_val in enumerate(updates_data['retriever_updates']):
                    if i < len(aggregated_weights['retriever']['weights']):
                        aggregated_weights['retriever']['weights'][i] += update_val * weight
            
            # Aggregate generator weights
            if 'generator_updates' in updates_data:
                for i, update_val in enumerate(updates_data['generator_updates']):
                    if i < len(aggregated_weights['generator']['weights']):
                        aggregated_weights['generator']['weights'][i] += update_val * weight
        
        # Apply differential privacy noise
        aggregated_weights = self.apply_differential_privacy(aggregated_weights)
        
        return aggregated_weights
    
    def apply_differential_privacy(self, weights: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential privacy noise to aggregated weights"""
        epsilon = 1.0  # Privacy parameter
        
        for component in weights:
            if isinstance(weights[component], dict) and 'weights' in weights[component]:
                noise_scale = 1.0 / epsilon
                for i in range(len(weights[component]['weights'])):
                    noise = random.gauss(0, noise_scale)
                    weights[component]['weights'][i] += noise
        
        return weights
    
    def track_federation_metrics(self, updates: List[Dict], quality_scores: Dict):
        """Track federation metrics and twin contributions"""
        for update in updates:
            twin_id = update['twin_id']
            self.twin_contributions[twin_id] = {
                'last_contribution': datetime.now().isoformat(),
                'data_size': update.get('data_size', 0),
                'loss': update.get('loss', 0),
                'quality_score': quality_scores.get(twin_id, 0),
                'performance_metrics': update.get('performance_metrics', {}),
                'optimization_insights': update.get('optimization_insights', {})
            }
        
        # Record federation history
        self.federation_history.append({
            'round': self.aggregation_round,
            'timestamp': datetime.now().isoformat(),
            'twin_contributions': self.twin_contributions.copy(),
            'quality_scores': quality_scores
        })
    
    def get_twin_contributions(self) -> Dict[str, Any]:
        """Get twin contributions"""
        return self.twin_contributions
    
    def get_federation_history(self) -> List[Dict[str, Any]]:
        """Get federation history"""
        return self.federation_history
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get federation server status"""
        return {
            'aggregation_round': self.aggregation_round,
            'active_twins': len(self.twin_contributions),
            'last_aggregation': self.federation_history[-1] if self.federation_history else None,
            'model_size': self.calculate_model_size(),
            'federation_health': self.calculate_federation_health()
        }
    
    def calculate_model_size(self) -> int:
        """Calculate global model size"""
        total_params = 0
        for component in self.global_rag_model.values():
            if isinstance(component, dict) and 'parameters' in component:
                total_params += component['parameters']
        return total_params
    
    def calculate_federation_health(self) -> float:
        """Calculate federation health score"""
        if not self.twin_contributions:
            return 0.0
        
        health_scores = []
        for twin_data in self.twin_contributions.values():
            performance = twin_data.get('performance_metrics', {})
            health_score = performance.get('health_score', 75.0)
            health_scores.append(health_score)
        
        return sum(health_scores) / len(health_scores)


class QualityAssessor:
    """Assess quality of model updates from twins"""
    
    def assess_updates(self, updates: List[Dict]) -> Dict[str, float]:
        """Assess quality of updates from each twin"""
        quality_scores = {}
        
        for update in updates:
            twin_id = update['twin_id']
            
            # Quality assessment factors
            data_size = update.get('data_size', 1000)
            loss = update.get('loss', 0.5)
            performance_metrics = update.get('performance_metrics', {})
            
            # Calculate quality score
            data_quality = min(data_size / 5000, 1.0)  # Normalize data size
            loss_quality = max(0, 1 - loss)  # Lower loss = higher quality
            performance_quality = performance_metrics.get('health_score', 75) / 100
            
            # Weighted quality score
            quality_score = (
                data_quality * 0.4 +
                loss_quality * 0.3 +
                performance_quality * 0.3
            )
            
            quality_scores[twin_id] = quality_score
        
        return quality_scores


class SecurityValidator:
    """Validate security of model updates"""
    
    def validate_updates(self, updates: List[Dict]) -> List[Dict]:
        """Validate updates for security compliance"""
        validated_updates = []
        
        for update in updates:
            # Basic security checks
            if self.is_update_secure(update):
                validated_updates.append(update)
            else:
                logger.warning(f"⚠️ Insecure update rejected from {update.get('twin_id', 'unknown')}")
        
        return validated_updates
    
    def is_update_secure(self, update: Dict) -> bool:
        """Check if update is secure"""
        # Basic security validation
        required_fields = ['twin_id', 'updates', 'loss']
        
        for field in required_fields:
            if field not in update:
                return False
        
        # Check for reasonable values
        if update.get('loss', 0) < 0 or update.get('loss', 0) > 10:
            return False
        
        return True


class PerformanceOptimizer:
    """Optimize performance based on twin characteristics"""
    
    def get_optimization_insights(self, twin_id: str) -> Dict[str, Any]:
        """Get optimization insights for a specific twin"""
        optimization_strategies = {
            'twin_1': {
                'focus': 'quality_control_and_efficiency',
                'target_improvement': '8% health score increase',
                'strategies': [
                    'Optimize print parameters',
                    'Improve material efficiency',
                    'Enhance quality control'
                ]
            },
            'twin_2': {
                'focus': 'resource_efficiency_and_stability',
                'target_improvement': '5% resource optimization',
                'strategies': [
                    'Optimize grid stability',
                    'Improve energy efficiency',
                    'Enhance fault detection'
                ]
            },
            'twin_3': {
                'focus': 'safety_and_efficiency',
                'target_improvement': '5% efficiency improvement',
                'strategies': [
                    'Enhance safety protocols',
                    'Optimize pressure control',
                    'Improve flow efficiency'
                ]
            }
        }
        
        return optimization_strategies.get(twin_id, {}) 