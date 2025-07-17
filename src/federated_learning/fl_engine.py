"""
Federated Learning Engine for Digital Twin Analytics Framework
=============================================================

This module implements the core federated learning functionality for the
AASX Digital Twin Analytics Framework, enabling collaborative learning
across multiple digital twins while preserving data privacy.

Based on the Federated Learning Roadmap for 3 Digital Twins:
- Twin 1: Additive Manufacturing (77% health score)
- Twin 2: Smart Grid Substation (80.9% health score) 
- Twin 3: Hydrogen Filling Station (80.4% health score)
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TwinPerformanceMetrics:
    """Performance metrics for each twin"""
    twin_id: str
    health_score: float
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    uptime: str
    status: str

@dataclass
class FederatedUpdate:
    """Structure for federated learning updates"""
    twin_id: str
    model_updates: Dict[str, Any]
    loss: float
    data_size: int
    twin_type: str
    privacy_metrics: Dict[str, Any]
    performance_metrics: TwinPerformanceMetrics
    optimization_insights: Dict[str, Any]
    timestamp: datetime

class QualityAssessor:
    """Assesses quality of federated learning updates"""
    
    def __init__(self):
        self.quality_threshold = 0.7
        
    def assess_updates(self, updates: List[FederatedUpdate]) -> Dict[str, float]:
        """Assess quality of updates from each twin"""
        quality_scores = {}
        
        for update in updates:
            # Calculate quality score based on multiple factors
            data_quality = min(update.data_size / 1000, 1.0)  # Normalize data size
            loss_quality = max(0, 1 - update.loss)  # Lower loss = higher quality
            performance_quality = update.performance_metrics.health_score / 100
            
            # Combined quality score
            quality_score = (
                data_quality * 0.3 +
                loss_quality * 0.4 +
                performance_quality * 0.3
            )
            
            quality_scores[update.twin_id] = quality_score
            
        return quality_scores

class SecurityValidator:
    """Validates security and privacy of federated updates"""
    
    def __init__(self):
        self.privacy_threshold = 0.8
        
    def validate_updates(self, updates: List[FederatedUpdate]) -> List[FederatedUpdate]:
        """Validate updates for security and privacy compliance"""
        validated_updates = []
        
        for update in updates:
            # Check privacy metrics
            privacy_score = self.calculate_privacy_score(update.privacy_metrics)
            
            if privacy_score >= self.privacy_threshold:
                validated_updates.append(update)
                logger.info(f"✅ Update from {update.twin_id} validated (privacy score: {privacy_score:.2f})")
            else:
                logger.warning(f"⚠️ Update from {update.twin_id} rejected (privacy score: {privacy_score:.2f})")
                
        return validated_updates
    
    def calculate_privacy_score(self, privacy_metrics: Dict[str, Any]) -> float:
        """Calculate privacy score based on privacy metrics"""
        # Simplified privacy scoring - in real implementation, this would be more sophisticated
        differential_privacy = privacy_metrics.get('differential_privacy_epsilon', 1.0)
        anonymization = privacy_metrics.get('data_anonymization', False)
        local_processing = privacy_metrics.get('local_processing_only', False)
        
        # Higher epsilon = lower privacy, so we invert it
        dp_score = max(0, 1 - differential_privacy / 2)
        anon_score = 1.0 if anonymization else 0.5
        local_score = 1.0 if local_processing else 0.5
        
        return (dp_score * 0.4 + anon_score * 0.3 + local_score * 0.3)

class PerformanceOptimizer:
    """Optimizes performance based on twin characteristics"""
    
    def __init__(self):
        self.twin_targets = {
            'twin_1': {
                'health_score_target': 85.0,
                'current_health_score': 77.0,
                'cpu_usage_target': 15.0,
                'memory_usage_target': 35.0
            },
            'twin_2': {
                'health_score_target': 85.0,
                'current_health_score': 80.9,
                'cpu_usage_target': 8.0,
                'memory_usage_target': 40.0
            },
            'twin_3': {
                'health_score_target': 85.0,
                'current_health_score': 80.4,
                'cpu_usage_target': 15.0,
                'memory_usage_target': 45.0,
                'response_time_target': 0.05
            }
        }
    
    def get_optimization_insights(self, twin_id: str) -> Dict[str, Any]:
        """Get optimization insights for a specific twin"""
        if twin_id not in self.twin_targets:
            return {}
            
        targets = self.twin_targets[twin_id]
        
        if twin_id == 'twin_1':  # Additive Manufacturing
            return {
                'health_score_target': targets['health_score_target'],
                'current_health_score': targets['current_health_score'],
                'optimization_focus': 'quality_control_and_efficiency',
                'expected_improvement': '8% health score increase',
                'strategy': 'Improve manufacturing quality control and material efficiency'
            }
        elif twin_id == 'twin_2':  # Smart Grid
            return {
                'health_score_target': targets['health_score_target'],
                'current_health_score': targets['current_health_score'],
                'optimization_focus': 'resource_efficiency_and_stability',
                'expected_improvement': '5% resource optimization',
                'strategy': 'Optimize grid stability and energy efficiency'
            }
        elif twin_id == 'twin_3':  # Hydrogen Station
            return {
                'health_score_target': targets['health_score_target'],
                'current_health_score': targets['current_health_score'],
                'optimization_focus': 'safety_and_efficiency',
                'expected_improvement': '5% efficiency improvement',
                'strategy': 'Enhance safety protocols and operational efficiency'
            }

class FederationServer:
    """Main federated learning server for aggregating models"""
    
    def __init__(self):
        self.global_model = self.initialize_global_model()
        self.aggregation_round = 0
        self.twin_contributions = {}
        self.quality_assessor = QualityAssessor()
        self.security_validator = SecurityValidator()
        self.performance_optimizer = PerformanceOptimizer()
        self.federation_history = []
        
    def initialize_global_model(self) -> Dict[str, Any]:
        """Initialize global federated model"""
        # In a real implementation, this would be a proper ML model
        # For now, we'll use a simple structure
        return {
            'model_type': 'federated_rag',
            'version': '1.0.0',
            'parameters': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'federation_rounds': 0
            }
        }
    
    def aggregate_twin_models(self, local_updates: List[FederatedUpdate]) -> Dict[str, Any]:
        """Aggregate models from all twins with performance-based weighting"""
        
        logger.info(f"🔄 Starting federated aggregation round {self.aggregation_round + 1}")
        
        # Security validation
        validated_updates = self.security_validator.validate_updates(local_updates)
        
        if not validated_updates:
            logger.error("❌ No valid updates to aggregate")
            return self.global_model
        
        # Quality assessment
        quality_scores = self.quality_assessor.assess_updates(validated_updates)
        
        # Performance-based weighting
        weights = self.calculate_performance_based_weights(validated_updates, quality_scores)
        
        # Secure aggregation (simplified FedAvg)
        aggregated_model = self.secure_aggregation(validated_updates, weights)
        
        # Update global model
        self.global_model = aggregated_model
        self.aggregation_round += 1
        
        # Track twin contributions and performance
        self.track_federation_metrics(validated_updates, quality_scores)
        
        logger.info(f"✅ Federated aggregation round {self.aggregation_round} completed")
        
        return self.global_model
    
    def calculate_performance_based_weights(self, updates: List[FederatedUpdate], 
                                          quality_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate weights based on twin performance and health scores"""
        weights = {}
        total_weight = 0
        
        for update in updates:
            twin_id = update.twin_id
            performance_metrics = update.performance_metrics
            
            # Multi-factor weight calculation
            data_quality = quality_scores[twin_id]
            data_volume = update.data_size
            health_score = performance_metrics.health_score
            response_time = performance_metrics.response_time
            error_rate = performance_metrics.error_rate
            
            # Performance-based weight formula
            # Higher health score = higher weight
            # Lower response time = higher weight (for real-time twins)
            # Lower error rate = higher weight
            
            performance_score = (
                health_score * 0.3 +
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
        
        logger.info(f"📊 Performance-based weights: {weights}")
        return weights
    
    def secure_aggregation(self, updates: List[FederatedUpdate], 
                          weights: Dict[str, float]) -> Dict[str, Any]:
        """Perform secure aggregation of model updates"""
        
        # Simplified aggregation - in real implementation, this would be more sophisticated
        aggregated_model = {
            'model_type': 'federated_rag',
            'version': '1.0.0',
            'parameters': {},
            'metadata': {
                'aggregation_round': self.aggregation_round,
                'aggregated_at': datetime.now().isoformat(),
                'participating_twins': [update.twin_id for update in updates],
                'weights_used': weights
            }
        }
        
        return aggregated_model
    
    def track_federation_metrics(self, updates: List[FederatedUpdate], 
                                quality_scores: Dict[str, float]):
        """Track federation metrics and twin contributions"""
        
        for update in updates:
            twin_id = update.twin_id
            
            contribution = {
                'round': self.aggregation_round,
                'timestamp': update.timestamp.isoformat(),
                'data_size': update.data_size,
                'loss': update.loss,
                'quality_score': quality_scores[twin_id],
                'performance_metrics': {
                    'health_score': update.performance_metrics.health_score,
                    'cpu_usage': update.performance_metrics.cpu_usage,
                    'memory_usage': update.performance_metrics.memory_usage,
                    'response_time': update.performance_metrics.response_time,
                    'error_rate': update.performance_metrics.error_rate
                },
                'optimization_insights': update.optimization_insights
            }
            
            if twin_id not in self.twin_contributions:
                self.twin_contributions[twin_id] = []
            
            self.twin_contributions[twin_id].append(contribution)
        
        # Store federation history
        federation_record = {
            'round': self.aggregation_round,
            'timestamp': datetime.now().isoformat(),
            'participating_twins': len(updates),
            'average_quality_score': np.mean(list(quality_scores.values())),
            'total_data_size': sum(update.data_size for update in updates)
        }
        
        self.federation_history.append(federation_record)

class LocalTrainer:
    """Local trainer for each twin"""
    
    def __init__(self, twin_id: str):
        self.twin_id = twin_id
        self.local_data = self.load_twin_specific_data()
        self.rag_model = self.initialize_rag_model()
        self.training_config = self.get_twin_training_config()
        self.privacy_config = self.get_privacy_config()
        self.performance_metrics = self.get_current_performance()
        
    def load_twin_specific_data(self) -> List[Dict[str, Any]]:
        """Load twin-specific data for training"""
        # In real implementation, this would load actual twin data
        # For now, we'll use mock data based on twin characteristics
        
        if self.twin_id == 'twin_1':  # Additive Manufacturing
            return [
                {'type': 'manufacturing_metrics', 'data': 'mock_manufacturing_data'},
                {'type': 'quality_control', 'data': 'mock_quality_data'},
                {'type': 'material_data', 'data': 'mock_material_data'}
            ]
        elif self.twin_id == 'twin_2':  # Smart Grid
            return [
                {'type': 'power_metrics', 'data': 'mock_power_data'},
                {'type': 'grid_stability', 'data': 'mock_stability_data'},
                {'type': 'energy_efficiency', 'data': 'mock_efficiency_data'}
            ]
        elif self.twin_id == 'twin_3':  # Hydrogen Station
            return [
                {'type': 'safety_metrics', 'data': 'mock_safety_data'},
                {'type': 'pressure_data', 'data': 'mock_pressure_data'},
                {'type': 'flow_rates', 'data': 'mock_flow_data'}
            ]
        else:
            return []
    
    def initialize_rag_model(self) -> Dict[str, Any]:
        """Initialize RAG model for the twin"""
        return {
            'model_type': 'local_rag',
            'twin_id': self.twin_id,
            'parameters': {},
            'metadata': {
                'initialized_at': datetime.now().isoformat()
            }
        }
    
    def get_twin_training_config(self) -> Dict[str, Any]:
        """Get training configuration specific to the twin"""
        configs = {
            'twin_1': {
                'learning_rate': 0.001,
                'batch_size': 32,
                'epochs': 10,
                'focus': 'quality_control_and_efficiency'
            },
            'twin_2': {
                'learning_rate': 0.0005,
                'batch_size': 64,
                'epochs': 15,
                'focus': 'stability_and_efficiency'
            },
            'twin_3': {
                'learning_rate': 0.001,
                'batch_size': 16,
                'epochs': 12,
                'focus': 'safety_and_efficiency'
            }
        }
        
        return configs.get(self.twin_id, {})
    
    def get_privacy_config(self) -> Dict[str, Any]:
        """Get privacy configuration for the twin"""
        configs = {
            'twin_1': {
                'differential_privacy_epsilon': 1.0,
                'data_anonymization': True,
                'local_processing_only': True
            },
            'twin_2': {
                'differential_privacy_epsilon': 0.5,  # Higher privacy for critical infrastructure
                'data_anonymization': True,
                'local_processing_only': True,
                'critical_infrastructure': True
            },
            'twin_3': {
                'differential_privacy_epsilon': 0.3,  # Highest privacy for safety-critical data
                'data_anonymization': True,
                'local_processing_only': True,
                'safety_critical': True
            }
        }
        
        return configs.get(self.twin_id, {})
    
    def get_current_performance(self) -> TwinPerformanceMetrics:
        """Get current performance metrics for the twin"""
        metrics = {
            'twin_1': TwinPerformanceMetrics(
                twin_id='twin_1',
                health_score=77.0,
                cpu_usage=18.0,
                memory_usage=38.0,
                response_time=2.0,
                error_rate=1.5,
                uptime='6d 0h 0m',
                status='good'
            ),
            'twin_2': TwinPerformanceMetrics(
                twin_id='twin_2',
                health_score=80.9,
                cpu_usage=5.0,
                memory_usage=43.4,
                response_time=2.0,
                error_rate=0.5,
                uptime='1h 0m',
                status='good'
            ),
            'twin_3': TwinPerformanceMetrics(
                twin_id='twin_3',
                health_score=80.4,
                cpu_usage=18.0,
                memory_usage=47.2,
                response_time=0.1,
                error_rate=1.5,
                uptime='3d 0h 0m',
                status='good'
            )
        }
        
        return metrics.get(self.twin_id)
    
    def train_local_model(self, global_model_weights: Dict[str, Any]) -> FederatedUpdate:
        """Train RAG model on local twin data with performance optimization"""
        
        logger.info(f"🏭 Training local model for {self.twin_id}")
        
        # Load global model weights (simplified)
        self.rag_model.update(global_model_weights)
        
        # Apply privacy-preserving training (simplified)
        local_loss = self.train_with_privacy(self.local_data)
        
        # Compute secure model updates (simplified)
        model_updates = self.compute_secure_updates()
        
        # Include performance optimization insights
        optimization_insights = self.generate_optimization_insights()
        
        # Create federated update
        update = FederatedUpdate(
            twin_id=self.twin_id,
            model_updates=model_updates,
            loss=local_loss,
            data_size=len(self.local_data),
            twin_type=self.get_twin_type(),
            privacy_metrics=self.privacy_config,
            performance_metrics=self.performance_metrics,
            optimization_insights=optimization_insights,
            timestamp=datetime.now()
        )
        
        logger.info(f"✅ Local training completed for {self.twin_id} (loss: {local_loss:.4f})")
        
        return update
    
    def train_with_privacy(self, local_data: List[Dict[str, Any]]) -> float:
        """Train model with privacy protection (simplified)"""
        # In real implementation, this would apply differential privacy
        # For now, we'll simulate training with a simple loss calculation
        
        # Simulate training loss based on data quality and twin performance
        base_loss = 0.5
        data_quality_factor = len(local_data) / 10  # More data = lower loss
        performance_factor = self.performance_metrics.health_score / 100  # Higher health = lower loss
        
        loss = base_loss * (1 - data_quality_factor * 0.3 - performance_factor * 0.2)
        
        return max(0.1, loss)  # Ensure loss is positive
    
    def compute_secure_updates(self) -> Dict[str, Any]:
        """Compute secure model updates (simplified)"""
        # In real implementation, this would compute actual model gradients
        # For now, we'll return a simple structure
        
        return {
            'gradients': {},
            'metadata': {
                'computed_at': datetime.now().isoformat(),
                'twin_id': self.twin_id
            }
        }
    
    def generate_optimization_insights(self) -> Dict[str, Any]:
        """Generate optimization insights based on twin performance"""
        if self.twin_id == 'twin_1':  # Additive Manufacturing
            return {
                'health_score_target': 85.0,
                'current_health_score': 77.0,
                'optimization_focus': 'quality_control_and_efficiency',
                'expected_improvement': '8% health score increase',
                'strategy': 'Improve manufacturing quality control and material efficiency'
            }
        elif self.twin_id == 'twin_2':  # Smart Grid
            return {
                'health_score_target': 85.0,
                'current_health_score': 80.9,
                'optimization_focus': 'resource_efficiency_and_stability',
                'expected_improvement': '5% resource optimization',
                'strategy': 'Optimize grid stability and energy efficiency'
            }
        elif self.twin_id == 'twin_3':  # Hydrogen Station
            return {
                'health_score_target': 85.0,
                'current_health_score': 80.4,
                'optimization_focus': 'safety_and_efficiency',
                'expected_improvement': '5% efficiency improvement',
                'strategy': 'Enhance safety protocols and operational efficiency'
            }
        else:
            return {}
    
    def get_twin_type(self) -> str:
        """Get the type of the twin"""
        types = {
            'twin_1': 'additive_manufacturing',
            'twin_2': 'smart_grid_substation',
            'twin_3': 'hydrogen_filling_station'
        }
        
        return types.get(self.twin_id, 'unknown')
    
    def update_model(self, global_model: Dict[str, Any]):
        """Update local model with global model"""
        self.rag_model = global_model
        logger.info(f"🔄 Updated local model for {self.twin_id}")

class FederatedLearningInfrastructure:
    """Main federated learning infrastructure"""
    
    def __init__(self):
        self.twins = ['twin_1', 'twin_2', 'twin_3']
        self.federation_server = FederationServer()
        self.local_trainers = {}
        self.monitoring_system = None  # Will be implemented later
        self.performance_tracker = None  # Will be implemented later
        
        # Initialize local trainers for each twin
        for twin_id in self.twins:
            self.local_trainers[twin_id] = LocalTrainer(twin_id)
        
        logger.info("🚀 Federated Learning Infrastructure initialized")
    
    def setup_federation(self):
        """Setup federated learning for all twins"""
        logger.info("🔧 Setting up federated learning infrastructure")
        
        # Configure communication protocols based on twin performance
        # Twin 2 (Smart Grid) - High priority, critical infrastructure
        # Twin 3 (Hydrogen) - Fast response time advantage
        # Twin 1 (Additive) - Optimization focus for health score improvement
        
        logger.info("✅ Federated learning setup completed")
    
    def run_federated_learning_cycle(self) -> Dict[str, Any]:
        """Run one complete federated learning cycle"""
        
        cycle_start_time = time.time()
        logger.info("🔄 Starting federated learning cycle")
        
        # Step 1: Local training on each twin
        local_updates = []
        for twin_id, trainer in self.local_trainers.items():
            logger.info(f"🏭 Training local model for {twin_id}")
            
            update = trainer.train_local_model(
                self.federation_server.global_model
            )
            local_updates.append(update)
        
        # Step 2: Federated aggregation
        logger.info("🔄 Aggregating models from all twins")
        global_model = self.federation_server.aggregate_twin_models(local_updates)
        
        # Step 3: Distribute enhanced model back to twins
        for twin_id, trainer in self.local_trainers.items():
            trainer.update_model(global_model)
        
        cycle_duration = time.time() - cycle_start_time
        
        logger.info(f"✅ Federated learning cycle completed in {cycle_duration:.2f}s")
        
        return {
            'global_model': global_model,
            'twin_contributions': self.federation_server.twin_contributions,
            'cycle_duration': cycle_duration,
            'aggregation_round': self.federation_server.aggregation_round,
            'participating_twins': len(local_updates)
        }
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get current federation status"""
        return {
            'federation_round': self.federation_server.aggregation_round,
            'active_twins': len(self.twins),
            'twin_status': {
                twin_id: {
                    'performance': trainer.performance_metrics.__dict__,
                    'optimization_insights': trainer.generate_optimization_insights()
                }
                for twin_id, trainer in self.local_trainers.items()
            },
            'federation_history': self.federation_server.federation_history[-5:],  # Last 5 rounds
            'last_cycle': {
                'timestamp': datetime.now().isoformat(),
                'status': 'ready'
            }
        } 