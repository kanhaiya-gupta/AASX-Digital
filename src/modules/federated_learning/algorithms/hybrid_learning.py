"""
Hybrid Learning Algorithm
=========================

Implementation of hybrid learning strategies for federated learning.
Combines multiple algorithms and approaches for optimal performance.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class HybridLearningConfig:
    """Configuration for Hybrid Learning algorithm"""
    # Algorithm combination
    primary_algorithm: str = "fedavg"  # fedavg, secure_aggregation, differential_privacy
    secondary_algorithm: str = "performance_weighting"  # performance_weighting, adaptive
    combination_strategy: str = "ensemble"  # ensemble, sequential, adaptive
    
    # Ensemble parameters
    ensemble_weights: List[float] = None  # Weights for each algorithm
    ensemble_threshold: float = 0.7  # Threshold for ensemble decision
    
    # Sequential parameters
    algorithm_switching_criteria: str = "performance"  # performance, convergence, stability
    switching_threshold: float = 0.1  # Threshold for algorithm switching
    
    # Adaptive parameters
    adaptation_rate: float = 0.1  # Rate of algorithm adaptation
    adaptation_window: int = 5  # Window size for adaptation decisions
    
    # Performance parameters
    max_iterations: int = 100
    convergence_tolerance: float = 0.001
    enable_early_stopping: bool = True


@dataclass
class HybridLearningMetrics:
    """Metrics for Hybrid Learning algorithm performance"""
    # Algorithm performance
    primary_algorithm_performance: float = 0.0
    secondary_algorithm_performance: float = 0.0
    ensemble_performance: float = 0.0
    
    # Combination metrics
    algorithm_switches: int = 0
    ensemble_decisions: int = 0
    adaptation_events: int = 0
    
    # Quality metrics
    overall_accuracy: float = 0.0
    convergence_speed: float = 0.0
    stability_score: float = 0.0
    
    # Resource metrics
    total_rounds: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0
    avg_processing_time: float = 0.0


class HybridLearningAlgorithm:
    """Hybrid Learning algorithm implementation"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[HybridLearningConfig] = None
    ):
        """Initialize Hybrid Learning algorithm"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or HybridLearningConfig()
        
        # Initialize ensemble weights if not provided
        if self.config.ensemble_weights is None:
            self.config.ensemble_weights = [0.6, 0.4]  # 60% primary, 40% secondary
        
        # Algorithm state
        self.current_round = 0
        self.is_running = False
        self.current_algorithm = self.config.primary_algorithm
        self.algorithm_performance_history: Dict[str, List[float]] = {}
        self.ensemble_decisions: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = HybridLearningMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.round_times: List[float] = []
    
    async def start_hybrid_learning(self, federation_id: str) -> Dict[str, Any]:
        """Start hybrid learning system"""
        try:
            self.start_time = datetime.now()
            self.is_running = True
            self.current_round = 0
            
            print(f"🔄 Starting Hybrid Learning system: {federation_id}")
            
            # Initialize hybrid learning state
            await self._initialize_hybrid_state(federation_id)
            
            return {
                'status': 'started',
                'federation_id': federation_id,
                'start_time': self.start_time.isoformat(),
                'primary_algorithm': self.config.primary_algorithm,
                'secondary_algorithm': self.config.secondary_algorithm,
                'combination_strategy': self.config.combination_strategy,
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to start hybrid learning: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def execute_hybrid_learning(
        self,
        federation_id: str,
        model_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute hybrid learning with multiple algorithms"""
        try:
            round_start_time = datetime.now()
            self.current_round += 1
            
            print(f"🔄 Hybrid Learning Round {self.current_round}: Processing {len(model_updates)} updates")
            
            # Validate inputs
            if not model_updates:
                raise ValueError("No model updates provided")
            
            # Execute based on combination strategy
            if self.config.combination_strategy == "ensemble":
                result = await self._execute_ensemble_learning(model_updates)
            elif self.config.combination_strategy == "sequential":
                result = await self._execute_sequential_learning(model_updates)
            elif self.config.combination_strategy == "adaptive":
                result = await self._execute_adaptive_learning(model_updates)
            else:
                result = await self._execute_ensemble_learning(model_updates)
            
            # Update algorithm performance history
            await self._update_algorithm_performance(result)
            
            # Adapt algorithm selection if enabled
            if self.config.enable_early_stopping:
                await self._adapt_algorithm_selection()
            
            # Update metrics
            round_time = (datetime.now() - round_start_time).total_seconds()
            self.round_times.append(round_time)
            self.metrics.total_rounds = self.current_round
            self.metrics.successful_rounds += 1
            self.metrics.avg_processing_time = np.mean(self.round_times)
            
            print(f"✅ Hybrid Learning Round {self.current_round} completed in {round_time:.2f}s")
            
            return {
                'status': 'success',
                'round': self.current_round,
                'result': result,
                'current_algorithm': self.current_algorithm,
                'round_time': round_time
            }
            
        except Exception as e:
            print(f"❌ Hybrid learning execution failed: {e}")
            self.metrics.failed_rounds += 1
            return {'status': 'failed', 'error': str(e)}
    
    async def _execute_ensemble_learning(
        self,
        model_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute ensemble learning combining multiple algorithms"""
        try:
            print(f"🎯 Executing ensemble learning with {self.config.primary_algorithm} and {self.config.secondary_algorithm}")
            
            # Execute primary algorithm
            primary_result = await self._execute_algorithm(
                self.config.primary_algorithm, model_updates
            )
            
            # Execute secondary algorithm
            secondary_result = await self._execute_algorithm(
                self.config.secondary_algorithm, model_updates
            )
            
            # Combine results using ensemble weights
            ensemble_result = await self._combine_ensemble_results(
                primary_result, secondary_result
            )
            
            # Record ensemble decision
            self.ensemble_decisions.append({
                'round': self.current_round,
                'primary_result': primary_result,
                'secondary_result': secondary_result,
                'ensemble_result': ensemble_result,
                'weights_used': self.config.ensemble_weights
            })
            
            self.metrics.ensemble_decisions += 1
            
            return ensemble_result
            
        except Exception as e:
            print(f"❌ Ensemble learning execution failed: {e}")
            raise
    
    async def _execute_sequential_learning(
        self,
        model_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute sequential learning with algorithm switching"""
        try:
            print(f"🔄 Executing sequential learning with algorithm switching")
            
            # Start with primary algorithm
            current_result = await self._execute_algorithm(
                self.current_algorithm, model_updates
            )
            
            # Check if switching criteria are met
            if await self._should_switch_algorithm(current_result):
                # Switch to secondary algorithm
                old_algorithm = self.current_algorithm
                self.current_algorithm = (
                    self.config.secondary_algorithm 
                    if self.current_algorithm == self.config.primary_algorithm
                    else self.config.primary_algorithm
                )
                
                print(f"🔄 Switching from {old_algorithm} to {self.current_algorithm}")
                
                # Execute with new algorithm
                current_result = await self._execute_algorithm(
                    self.current_algorithm, model_updates
                )
                
                self.metrics.algorithm_switches += 1
            
            return current_result
            
        except Exception as e:
            print(f"❌ Sequential learning execution failed: {e}")
            raise
    
    async def _execute_adaptive_learning(
        self,
        model_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute adaptive learning with dynamic algorithm selection"""
        try:
            print(f"🎯 Executing adaptive learning with dynamic selection")
            
            # Evaluate current algorithm performance
            current_performance = await self._evaluate_algorithm_performance(
                self.current_algorithm
            )
            
            # Calculate adaptation probability
            adaptation_prob = await self._calculate_adaptation_probability(current_performance)
            
            if adaptation_prob > self.config.adaptation_rate:
                # Adapt algorithm selection
                await self._adapt_algorithm_selection()
                self.metrics.adaptation_events += 1
            
            # Execute with current algorithm
            result = await self._execute_algorithm(
                self.current_algorithm, model_updates
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Adaptive learning execution failed: {e}")
            raise
    
    async def _execute_algorithm(
        self,
        algorithm_name: str,
        model_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a specific algorithm"""
        try:
            # Simulate algorithm execution
            # In real implementation, this would call the actual algorithm
            
            if algorithm_name == "fedavg":
                result = await self._simulate_fedavg(model_updates)
            elif algorithm_name == "secure_aggregation":
                result = await self._simulate_secure_aggregation(model_updates)
            elif algorithm_name == "differential_privacy":
                result = await self._simulate_differential_privacy(model_updates)
            elif algorithm_name == "performance_weighting":
                result = await self._simulate_performance_weighting(model_updates)
            else:
                result = await self._simulate_fedavg(model_updates)
            
            return {
                'algorithm': algorithm_name,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Algorithm execution failed: {e}")
            raise
    
    async def _simulate_fedavg(self, model_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate FedAvg algorithm execution"""
        try:
            # Simple simulation of FedAvg
            num_updates = len(model_updates)
            avg_accuracy = np.mean([
                update.get('accuracy', 0.5) for update in model_updates
            ])
            
            return {
                'method': 'fedavg',
                'participants': num_updates,
                'accuracy': avg_accuracy,
                'convergence': min(0.9, avg_accuracy + 0.1)
            }
            
        except Exception as e:
            print(f"⚠️  FedAvg simulation failed: {e}")
            return {'method': 'fedavg', 'error': str(e)}
    
    async def _simulate_secure_aggregation(self, model_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate Secure Aggregation algorithm execution"""
        try:
            # Simple simulation of Secure Aggregation
            num_updates = len(model_updates)
            avg_accuracy = np.mean([
                update.get('accuracy', 0.5) for update in model_updates
            ])
            
            return {
                'method': 'secure_aggregation',
                'participants': num_updates,
                'accuracy': avg_accuracy * 0.95,  # Slight degradation due to security
                'security_level': 'high'
            }
            
        except Exception as e:
            print(f"⚠️  Secure Aggregation simulation failed: {e}")
            return {'method': 'secure_aggregation', 'error': str(e)}
    
    async def _simulate_differential_privacy(self, model_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate Differential Privacy algorithm execution"""
        try:
            # Simple simulation of Differential Privacy
            num_updates = len(model_updates)
            avg_accuracy = np.mean([
                update.get('accuracy', 0.5) for update in model_updates
            ])
            
            return {
                'method': 'differential_privacy',
                'participants': num_updates,
                'accuracy': avg_accuracy * 0.9,  # Some degradation due to privacy
                'privacy_guarantee': 0.95
            }
            
        except Exception as e:
            print(f"⚠️  Differential Privacy simulation failed: {e}")
            return {'method': 'differential_privacy', 'error': str(e)}
    
    async def _simulate_performance_weighting(self, model_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate Performance Weighting algorithm execution"""
        try:
            # Simple simulation of Performance Weighting
            num_updates = len(model_updates)
            accuracies = [update.get('accuracy', 0.5) for update in model_updates]
            
            # Weight by performance
            weights = np.array(accuracies) / sum(accuracies)
            weighted_accuracy = np.sum(np.array(accuracies) * weights)
            
            return {
                'method': 'performance_weighting',
                'participants': num_updates,
                'accuracy': weighted_accuracy,
                'selection_efficiency': 0.85
            }
            
        except Exception as e:
            print(f"⚠️  Performance Weighting simulation failed: {e}")
            return {'method': 'performance_weighting', 'error': str(e)}
    
    async def _combine_ensemble_results(
        self,
        primary_result: Dict[str, Any],
        secondary_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine results from multiple algorithms using ensemble weights"""
        try:
            # Extract key metrics
            primary_accuracy = primary_result.get('result', {}).get('accuracy', 0.5)
            secondary_accuracy = secondary_result.get('result', {}).get('accuracy', 0.5)
            
            # Apply ensemble weights
            ensemble_accuracy = (
                self.config.ensemble_weights[0] * primary_accuracy +
                self.config.ensemble_weights[1] * secondary_accuracy
            )
            
            return {
                'method': 'ensemble',
                'primary_algorithm': primary_result.get('algorithm'),
                'secondary_algorithm': secondary_result.get('algorithm'),
                'ensemble_accuracy': ensemble_accuracy,
                'weights_used': self.config.ensemble_weights,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Ensemble result combination failed: {e}")
            raise
    
    async def _should_switch_algorithm(self, current_result: Dict[str, Any]) -> bool:
        """Determine if algorithm switching criteria are met"""
        try:
            if self.config.algorithm_switching_criteria == "performance":
                # Switch based on performance threshold
                accuracy = current_result.get('result', {}).get('accuracy', 0.5)
                return accuracy < self.config.switching_threshold
                
            elif self.config.algorithm_switching_criteria == "convergence":
                # Switch based on convergence rate
                convergence = current_result.get('result', {}).get('convergence', 0.5)
                return convergence < self.config.switching_threshold
                
            elif self.config.algorithm_switching_criteria == "stability":
                # Switch based on stability
                stability = current_result.get('result', {}).get('stability', 0.5)
                return stability < self.config.switching_threshold
                
            else:
                return False
                
        except Exception as e:
            print(f"⚠️  Algorithm switching criteria check failed: {e}")
            return False
    
    async def _evaluate_algorithm_performance(self, algorithm_name: str) -> float:
        """Evaluate performance of a specific algorithm"""
        try:
            if algorithm_name in self.algorithm_performance_history:
                recent_performance = self.algorithm_performance_history[algorithm_name][-self.config.adaptation_window:]
                if recent_performance:
                    return np.mean(recent_performance)
            
            return 0.5  # Default performance
            
        except Exception as e:
            print(f"⚠️  Algorithm performance evaluation failed: {e}")
            return 0.5
    
    async def _calculate_adaptation_probability(self, current_performance: float) -> float:
        """Calculate probability of algorithm adaptation"""
        try:
            # Higher performance = lower adaptation probability
            base_prob = 0.1
            performance_factor = 1.0 - current_performance
            adaptation_prob = base_prob + (performance_factor * 0.3)
            
            return min(0.5, max(0.05, adaptation_prob))
            
        except Exception as e:
            print(f"⚠️  Adaptation probability calculation failed: {e}")
            return 0.1
    
    async def _adapt_algorithm_selection(self):
        """Adapt algorithm selection based on performance"""
        try:
            # Evaluate both algorithms
            primary_perf = await self._evaluate_algorithm_performance(self.config.primary_algorithm)
            secondary_perf = await self._evaluate_algorithm_performance(self.config.secondary_algorithm)
            
            # Switch if secondary is significantly better
            if secondary_perf > primary_perf + self.config.adaptation_rate:
                self.current_algorithm = self.config.secondary_algorithm
                print(f"🔄 Adapted to {self.current_algorithm} (performance: {secondary_perf:.3f})")
            
        except Exception as e:
            print(f"⚠️  Algorithm adaptation failed: {e}")
    
    async def _update_algorithm_performance(self, result: Dict[str, Any]):
        """Update algorithm performance history"""
        try:
            algorithm_name = result.get('current_algorithm', 'unknown')
            
            if algorithm_name not in self.algorithm_performance_history:
                self.algorithm_performance_history[algorithm_name] = []
            
            # Extract performance metric
            if 'result' in result:
                performance = result['result'].get('accuracy', 0.5)
            else:
                performance = 0.5
            
            self.algorithm_performance_history[algorithm_name].append(performance)
            
            # Limit history size
            if len(self.algorithm_performance_history[algorithm_name]) > self.config.adaptation_window * 2:
                self.algorithm_performance_history[algorithm_name] = \
                    self.algorithm_performance_history[algorithm_name][-self.config.adaptation_window * 2:]
            
        except Exception as e:
            print(f"⚠️  Algorithm performance update failed: {e}")
    
    async def _initialize_hybrid_state(self, federation_id: str):
        """Initialize hybrid learning state"""
        try:
            print(f"🔄 Initializing hybrid learning state for: {federation_id}")
            
            # Reset state
            self.algorithm_performance_history.clear()
            self.ensemble_decisions.clear()
            
            # Initialize performance history for both algorithms
            self.algorithm_performance_history[self.config.primary_algorithm] = []
            self.algorithm_performance_history[self.config.secondary_algorithm] = []
            
        except Exception as e:
            print(f"⚠️  Hybrid state initialization failed: {e}")
    
    async def get_hybrid_report(self) -> Dict[str, Any]:
        """Get comprehensive hybrid learning report"""
        try:
            return {
                'hybrid_metrics': self.metrics.__dict__,
                'algorithm_performance': self.algorithm_performance_history,
                'ensemble_decisions': self.ensemble_decisions,
                'current_config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Hybrid report generation failed: {e}")
            return {'error': str(e)}
    
    async def stop_hybrid_learning(self) -> Dict[str, Any]:
        """Stop hybrid learning system"""
        try:
            self.is_running = False
            
            # Generate final hybrid report
            hybrid_report = await self.get_hybrid_report()
            
            print(f"🛑 Hybrid Learning system stopped after {self.current_round} rounds")
            
            return {
                'status': 'stopped',
                'total_rounds': self.current_round,
                'final_hybrid_report': hybrid_report
            }
            
        except Exception as e:
            print(f"❌ Failed to stop hybrid learning: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'HybridLearning',
            'current_round': self.current_round,
            'is_running': self.is_running,
            'metrics': self.metrics.__dict__,
            'round_times': self.round_times,
            'config': self.config.__dict__
        }
    
    async def reset_algorithm(self):
        """Reset algorithm state and metrics"""
        self.current_round = 0
        self.is_running = False
        self.current_algorithm = self.config.primary_algorithm
        self.algorithm_performance_history.clear()
        self.ensemble_decisions.clear()
        self.round_times.clear()
        self.metrics = HybridLearningMetrics()
        self.start_time = None
        
        print("🔄 Hybrid Learning algorithm reset")
