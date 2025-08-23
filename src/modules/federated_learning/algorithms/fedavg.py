"""
Federated Averaging (FedAvg) Algorithm
======================================

Implementation of the classic federated averaging algorithm.
Provides weighted averaging of local model updates from participating nodes.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class FedAvgConfig:
    """Configuration for FedAvg algorithm"""
    # Aggregation parameters
    min_participants: int = 3
    max_participants: int = 100
    aggregation_threshold: float = 0.8  # 80% of participants must complete
    
    # Weighting parameters
    use_data_size_weighting: bool = True
    use_performance_weighting: bool = False
    use_quality_weighting: bool = True
    
    # Convergence parameters
    max_rounds: int = 100
    convergence_threshold: float = 0.001
    patience: int = 10
    
    # Performance parameters
    timeout_seconds: int = 300
    batch_size: int = 32
    parallel_aggregation: bool = True


@dataclass
class FedAvgMetrics:
    """Metrics for FedAvg algorithm performance"""
    # Aggregation metrics
    total_rounds: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0
    
    # Performance metrics
    avg_aggregation_time: float = 0.0
    avg_convergence_time: float = 0.0
    total_participants: int = 0
    
    # Quality metrics
    final_accuracy: float = 0.0
    convergence_rate: float = 0.0
    stability_score: float = 0.0
    
    # Resource metrics
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_usage_mb: float = 0.0


class FedAvgAlgorithm:
    """Federated Averaging algorithm implementation"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[FedAvgConfig] = None
    ):
        """Initialize FedAvg algorithm"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or FedAvgConfig()
        
        # Algorithm state
        self.current_round = 0
        self.is_running = False
        self.convergence_history: List[float] = []
        
        # Metrics tracking
        self.metrics = FedAvgMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.round_times: List[float] = []
    
    async def start_federation(self, federation_id: str) -> Dict[str, Any]:
        """Start a new federation round"""
        try:
            self.start_time = datetime.now()
            self.is_running = True
            self.current_round = 0
            
            print(f"🚀 Starting FedAvg federation: {federation_id}")
            
            # Initialize federation state
            await self._initialize_federation_state(federation_id)
            
            return {
                'status': 'started',
                'federation_id': federation_id,
                'start_time': self.start_time.isoformat(),
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to start federation: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def aggregate_models(
        self,
        federation_id: str,
        local_updates: List[Dict[str, Any]],
        weights: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Aggregate local model updates using FedAvg"""
        try:
            round_start_time = datetime.now()
            self.current_round += 1
            
            print(f"🔄 FedAvg Round {self.current_round}: Aggregating {len(local_updates)} models")
            
            # Validate inputs
            if not local_updates:
                raise ValueError("No local updates provided")
            
            if len(local_updates) < self.config.min_participants:
                raise ValueError(f"Insufficient participants: {len(local_updates)} < {self.config.min_participants}")
            
            # Calculate weights if not provided
            if weights is None:
                weights = await self._calculate_weights(local_updates)
            
            # Perform weighted aggregation
            aggregated_model = await self._perform_weighted_aggregation(local_updates, weights)
            
            # Update metrics
            round_time = (datetime.now() - round_start_time).total_seconds()
            self.round_times.append(round_time)
            self.metrics.total_rounds = self.current_round
            self.metrics.successful_rounds += 1
            self.metrics.avg_aggregation_time = np.mean(self.round_times)
            
            # Check convergence
            convergence_achieved = await self._check_convergence(aggregated_model)
            
            print(f"✅ FedAvg Round {self.current_round} completed in {round_time:.2f}s")
            
            return {
                'status': 'success',
                'round': self.current_round,
                'aggregated_model': aggregated_model,
                'weights': weights,
                'convergence_achieved': convergence_achieved,
                'round_time': round_time,
                'participants': len(local_updates)
            }
            
        except Exception as e:
            print(f"❌ FedAvg aggregation failed: {e}")
            self.metrics.failed_rounds += 1
            return {'status': 'failed', 'error': str(e)}
    
    async def _calculate_weights(self, local_updates: List[Dict[str, Any]]) -> List[float]:
        """Calculate aggregation weights for local updates"""
        try:
            if self.config.use_data_size_weighting:
                # Weight by data size
                data_sizes = [update.get('data_size', 1) for update in local_updates]
                total_size = sum(data_sizes)
                weights = [size / total_size for size in data_sizes]
                
            elif self.config.use_performance_weighting:
                # Weight by performance metrics
                performances = [update.get('performance_score', 0.5) for update in local_updates]
                total_performance = sum(performances)
                weights = [perf / total_performance for perf in performances]
                
            elif self.config.use_quality_weighting:
                # Weight by model quality
                qualities = [update.get('quality_score', 0.5) for update in local_updates]
                total_quality = sum(qualities)
                weights = [qual / total_quality for qual in qualities]
                
            else:
                # Equal weighting
                weights = [1.0 / len(local_updates)] * len(local_updates)
            
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            return weights
            
        except Exception as e:
            print(f"⚠️  Weight calculation failed, using equal weights: {e}")
            return [1.0 / len(local_updates)] * len(local_updates)
    
    async def _perform_weighted_aggregation(
        self,
        local_updates: List[Dict[str, Any]],
        weights: List[float]
    ) -> Dict[str, Any]:
        """Perform weighted aggregation of local model updates"""
        try:
            # Extract model parameters
            model_params = []
            for update in local_updates:
                if 'model_parameters' in update:
                    model_params.append(update['model_parameters'])
                else:
                    # Handle case where model parameters are not in expected format
                    model_params.append(update)
            
            # Perform weighted averaging
            aggregated_params = {}
            
            for param_name in model_params[0].keys():
                if isinstance(model_params[0][param_name], np.ndarray):
                    # Handle numpy arrays
                    weighted_sum = np.zeros_like(model_params[0][param_name])
                    for i, params in enumerate(model_params):
                        weighted_sum += weights[i] * params[param_name]
                    aggregated_params[param_name] = weighted_sum
                else:
                    # Handle scalar values
                    weighted_sum = sum(weights[i] * params[param_name] for i, params in enumerate(model_params))
                    aggregated_params[param_name] = weighted_sum
            
            return {
                'model_parameters': aggregated_params,
                'aggregation_method': 'fedavg',
                'weights_used': weights,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Weighted aggregation failed: {e}")
            raise
    
    async def _check_convergence(self, aggregated_model: Dict[str, Any]) -> bool:
        """Check if the federation has converged"""
        try:
            if self.current_round < 2:
                return False
            
            # Calculate convergence metric (e.g., parameter change)
            current_metric = self._calculate_convergence_metric(aggregated_model)
            self.convergence_history.append(current_metric)
            
            # Check convergence threshold
            if len(self.convergence_history) >= 2:
                recent_change = abs(self.convergence_history[-1] - self.convergence_history[-2])
                if recent_change < self.config.convergence_threshold:
                    self.metrics.convergence_rate = 1.0 / self.current_round
                    return True
            
            # Check patience (early stopping)
            if len(self.convergence_history) > self.config.patience:
                recent_metrics = self.convergence_history[-self.config.patience:]
                if all(abs(recent_metrics[i] - recent_metrics[i-1]) < self.config.convergence_threshold 
                       for i in range(1, len(recent_metrics))):
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Convergence check failed: {e}")
            return False
    
    def _calculate_convergence_metric(self, aggregated_model: Dict[str, Any]) -> float:
        """Calculate convergence metric for the aggregated model"""
        try:
            # Simple metric: sum of parameter values
            params = aggregated_model.get('model_parameters', {})
            total_sum = 0.0
            
            for param_name, param_value in params.items():
                if isinstance(param_value, np.ndarray):
                    total_sum += np.sum(param_value)
                else:
                    total_sum += float(param_value)
            
            return total_sum
            
        except Exception as e:
            print(f"⚠️  Convergence metric calculation failed: {e}")
            return 0.0
    
    async def _initialize_federation_state(self, federation_id: str):
        """Initialize federation state in database"""
        try:
            # This would typically initialize federation tracking
            # For now, we'll just log the initialization
            print(f"📊 Initializing federation state for: {federation_id}")
            
        except Exception as e:
            print(f"⚠️  Federation state initialization failed: {e}")
    
    async def stop_federation(self) -> Dict[str, Any]:
        """Stop the current federation"""
        try:
            self.is_running = False
            
            # Calculate final metrics
            if self.start_time:
                total_time = (datetime.now() - self.start_time).total_seconds()
                self.metrics.avg_convergence_time = total_time / self.current_round if self.current_round > 0 else 0
            
            print(f"🛑 FedAvg federation stopped after {self.current_round} rounds")
            
            return {
                'status': 'stopped',
                'total_rounds': self.current_round,
                'total_time': total_time if self.start_time else 0,
                'final_metrics': self.metrics.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to stop federation: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'FedAvg',
            'current_round': self.current_round,
            'is_running': self.is_running,
            'metrics': self.metrics.__dict__,
            'convergence_history': self.convergence_history,
            'round_times': self.round_times,
            'config': self.config.__dict__
        }
    
    async def reset_algorithm(self):
        """Reset algorithm state and metrics"""
        self.current_round = 0
        self.is_running = False
        self.convergence_history.clear()
        self.round_times.clear()
        self.metrics = FedAvgMetrics()
        self.start_time = None
        
        print("🔄 FedAvg algorithm reset") 