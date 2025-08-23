"""
Performance Optimizer
====================

Performance optimization for federated learning operations.
Handles model performance tuning, hyperparameter optimization, and efficiency improvements.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization"""
    # Optimization methods
    hyperparameter_tuning: bool = True
    model_architecture_optimization: bool = True
    training_strategy_optimization: bool = True
    resource_allocation_optimization: bool = True
    
    # Hyperparameter tuning settings
    learning_rate_range: Tuple[float, float] = (1e-5, 1e-1)
    batch_size_range: Tuple[int, int] = (16, 512)
    epochs_range: Tuple[int, int] = (10, 100)
    optimizer_types: List[str] = None
    
    # Model architecture settings
    layer_sizes_range: Tuple[int, int] = (64, 1024)
    dropout_range: Tuple[float, float] = (0.1, 0.5)
    activation_functions: List[str] = None
    
    # Training strategy settings
    early_stopping_patience: int = 10
    learning_rate_scheduling: bool = True
    gradient_clipping: bool = True
    
    # Resource allocation settings
    gpu_memory_limit: float = 0.8
    cpu_cores_limit: int = 4
    memory_limit_gb: float = 8.0
    
    # Performance settings
    optimization_iterations: int = 50
    evaluation_metrics: List[str] = None
    
    def __post_init__(self):
        if self.optimizer_types is None:
            self.optimizer_types = ['adam', 'sgd', 'rmsprop', 'adamw']
        if self.activation_functions is None:
            self.activation_functions = ['relu', 'tanh', 'sigmoid', 'leaky_relu']
        if self.evaluation_metrics is None:
            self.evaluation_metrics = ['accuracy', 'loss', 'f1_score', 'precision', 'recall']


@dataclass
class PerformanceMetrics:
    """Metrics for performance optimization"""
    # Optimization progress
    current_iteration: int = 0
    best_performance_score: float = 0.0
    improvement_count: int = 0
    stagnation_count: int = 0
    
    # Performance scores
    baseline_performance: float = 0.0
    optimized_performance: float = 0.0
    performance_improvement: float = 0.0
    relative_improvement: float = 0.0
    
    # Resource utilization
    gpu_utilization: float = 0.0
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    training_time: float = 0.0
    
    # Optimization statistics
    hyperparameters_tested: int = 0
    architectures_evaluated: int = 0
    strategies_tested: int = 0
    total_evaluations: int = 0
    
    # Convergence metrics
    convergence_rate: float = 0.0
    stability_score: float = 0.0
    generalization_score: float = 0.0


class PerformanceOptimizer:
    """Performance optimization implementation for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[PerformanceConfig] = None
    ):
        """Initialize Performance Optimizer"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or PerformanceConfig()
        
        # Optimization state
        self.is_optimizing = False
        self.current_model = None
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = PerformanceMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        
        # Optimization state
        self.best_config = None
        self.best_model = None
        self.performance_history: List[float] = []
        
    async def start_optimization(
        self,
        model_id: str,
        baseline_performance: float
    ) -> Dict[str, Any]:
        """Start performance optimization process"""
        try:
            self.start_time = datetime.now()
            self.is_optimizing = True
            self.current_model = model_id
            self.metrics.baseline_performance = baseline_performance
            
            print(f"🚀 Starting performance optimization for model: {model_id}")
            print(f"📊 Baseline performance: {baseline_performance:.4f}")
            
            # Initialize optimization
            await self._initialize_optimization()
            
            # Run optimization iterations
            optimization_results = await self._run_optimization_loop()
            
            # Finalize optimization
            final_results = await self._finalize_optimization(optimization_results)
            
            return final_results
            
        except Exception as e:
            print(f"❌ Performance optimization failed: {e}")
            return {'status': 'failed', 'error': str(e)}
        finally:
            self.is_optimizing = False
    
    async def _initialize_optimization(self):
        """Initialize optimization process"""
        try:
            # Reset metrics
            self.metrics = PerformanceMetrics()
            self.metrics.baseline_performance = self.metrics.baseline_performance
            
            # Initialize best config
            self.best_config = {
                'hyperparameters': {},
                'architecture': {},
                'training_strategy': {},
                'resource_allocation': {}
            }
            
            # Initialize performance history
            self.performance_history = [self.metrics.baseline_performance]
            
            print("🔧 Optimization initialized")
            
        except Exception as e:
            print(f"❌ Optimization initialization failed: {e}")
            raise
    
    async def _run_optimization_loop(self) -> Dict[str, Any]:
        """Run the main optimization loop"""
        try:
            print(f"🔄 Running {self.config.optimization_iterations} optimization iterations...")
            
            for iteration in range(self.config.optimization_iterations):
                self.metrics.current_iteration = iteration + 1
                
                # Generate candidate configuration
                candidate_config = await self._generate_candidate_config()
                
                # Evaluate candidate
                performance_score = await self._evaluate_candidate(candidate_config)
                
                # Update best configuration if improved
                if performance_score > self.metrics.best_performance_score:
                    self.metrics.best_performance_score = performance_score
                    self.best_config = candidate_config
                    self.metrics.improvement_count += 1
                    print(f"✨ Iteration {iteration + 1}: New best performance: {performance_score:.4f}")
                else:
                    self.metrics.stagnation_count += 1
                
                # Update performance history
                self.performance_history.append(performance_score)
                
                # Check for early stopping
                if await self._should_stop_early():
                    print(f"⏹️  Early stopping at iteration {iteration + 1}")
                    break
                
                # Progress update
                if (iteration + 1) % 10 == 0:
                    print(f"📈 Progress: {iteration + 1}/{self.config.optimization_iterations}")
            
            return {
                'best_config': self.best_config,
                'best_performance': self.metrics.best_performance_score,
                'total_iterations': self.metrics.current_iteration,
                'performance_history': self.performance_history
            }
            
        except Exception as e:
            print(f"❌ Optimization loop failed: {e}")
            raise
    
    async def _generate_candidate_config(self) -> Dict[str, Any]:
        """Generate a candidate configuration for evaluation"""
        try:
            config = {}
            
            # Hyperparameter tuning
            if self.config.hyperparameter_tuning:
                config['hyperparameters'] = {
                    'learning_rate': np.random.uniform(*self.config.learning_rate_range),
                    'batch_size': np.random.choice(self.config.batch_size_range),
                    'epochs': np.random.randint(*self.config.epochs_range),
                    'optimizer': np.random.choice(self.config.optimizer_types)
                }
            
            # Model architecture optimization
            if self.config.model_architecture_optimization:
                config['architecture'] = {
                    'layer_size': np.random.randint(*self.config.layer_sizes_range),
                    'dropout': np.random.uniform(*self.config.dropout_range),
                    'activation': np.random.choice(self.config.activation_functions)
                }
            
            # Training strategy optimization
            if self.config.training_strategy_optimization:
                config['training_strategy'] = {
                    'early_stopping_patience': self.config.early_stopping_patience,
                    'learning_rate_scheduling': self.config.learning_rate_scheduling,
                    'gradient_clipping': self.config.gradient_clipping
                }
            
            # Resource allocation optimization
            if self.config.resource_allocation_optimization:
                config['resource_allocation'] = {
                    'gpu_memory_limit': np.random.uniform(0.5, self.config.gpu_memory_limit),
                    'cpu_cores': np.random.randint(1, self.config.cpu_cores_limit + 1),
                    'memory_limit_gb': np.random.uniform(2.0, self.config.memory_limit_gb)
                }
            
            return config
            
        except Exception as e:
            print(f"❌ Candidate config generation failed: {e}")
            return {}
    
    async def _evaluate_candidate(self, config: Dict[str, Any]) -> float:
        """Evaluate a candidate configuration"""
        try:
            # Simulate performance evaluation
            # In practice, this would train and evaluate the model
            
            # Base performance score
            base_score = self.metrics.baseline_performance
            
            # Hyperparameter impact
            if 'hyperparameters' in config:
                lr_factor = 1.0 / (1.0 + abs(config['hyperparameters']['learning_rate'] - 0.001))
                batch_factor = 1.0 / (1.0 + abs(config['hyperparameters']['batch_size'] - 64) / 64)
                config_score = (lr_factor + batch_factor) / 2
                base_score *= config_score
            
            # Architecture impact
            if 'architecture' in config:
                layer_factor = 1.0 / (1.0 + abs(config['architecture']['layer_size'] - 256) / 256)
                dropout_factor = 1.0 / (1.0 + abs(config['architecture']['dropout'] - 0.3) / 0.3)
                arch_score = (layer_factor + dropout_factor) / 2
                base_score *= arch_score
            
            # Add some randomness to simulate real evaluation
            noise = np.random.normal(0, 0.01)
            final_score = base_score + noise
            
            # Ensure score is positive
            final_score = max(0.0, final_score)
            
            # Update metrics
            self.metrics.hyperparameters_tested += 1
            self.metrics.architectures_evaluated += 1
            self.metrics.total_evaluations += 1
            
            return final_score
            
        except Exception as e:
            print(f"❌ Candidate evaluation failed: {e}")
            return 0.0
    
    async def _should_stop_early(self) -> bool:
        """Check if optimization should stop early"""
        try:
            # Stop if no improvement for several iterations
            if self.metrics.stagnation_count >= 15:
                return True
            
            # Stop if performance improvement is minimal
            if len(self.performance_history) >= 10:
                recent_improvement = max(self.performance_history[-10:]) - min(self.performance_history[-10:])
                if recent_improvement < 0.001:
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Early stopping check failed: {e}")
            return False
    
    async def _finalize_optimization(self, optimization_results: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize optimization and calculate final metrics"""
        try:
            # Calculate final metrics
            self.metrics.optimized_performance = self.metrics.best_performance_score
            self.metrics.performance_improvement = self.metrics.optimized_performance - self.metrics.baseline_performance
            self.metrics.relative_improvement = self.metrics.performance_improvement / self.metrics.baseline_performance
            
            # Calculate convergence metrics
            if len(self.performance_history) > 1:
                self.metrics.convergence_rate = self._calculate_convergence_rate()
                self.metrics.stability_score = self._calculate_stability_score()
            
            # Calculate processing time
            processing_time = (datetime.now() - self.start_time).total_seconds()
            self.metrics.training_time = processing_time
            
            # Record optimization history
            self.optimization_history.append({
                'model_id': self.current_model,
                'timestamp': datetime.now().isoformat(),
                'optimization_results': optimization_results,
                'final_metrics': self.metrics.__dict__,
                'processing_time': processing_time
            })
            
            print(f"✅ Performance optimization completed in {processing_time:.2f}s")
            print(f"📈 Performance improvement: {self.metrics.performance_improvement:.4f} ({self.metrics.relative_improvement:.2%})")
            
            return {
                'status': 'success',
                'model_id': self.current_model,
                'best_config': self.best_config,
                'optimization_results': optimization_results,
                'final_metrics': self.metrics.__dict__,
                'processing_time': processing_time
            }
            
        except Exception as e:
            print(f"❌ Optimization finalization failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _calculate_convergence_rate(self) -> float:
        """Calculate convergence rate from performance history"""
        try:
            if len(self.performance_history) < 2:
                return 0.0
            
            # Calculate average improvement per iteration
            improvements = [self.performance_history[i] - self.performance_history[i-1] 
                          for i in range(1, len(self.performance_history))]
            
            positive_improvements = [imp for imp in improvements if imp > 0]
            if not positive_improvements:
                return 0.0
            
            return np.mean(positive_improvements)
            
        except Exception as e:
            print(f"⚠️  Convergence rate calculation failed: {e}")
            return 0.0
    
    def _calculate_stability_score(self) -> float:
        """Calculate stability score from performance history"""
        try:
            if len(self.performance_history) < 2:
                return 0.0
            
            # Calculate coefficient of variation (lower is more stable)
            mean_performance = np.mean(self.performance_history)
            std_performance = np.std(self.performance_history)
            
            if mean_performance == 0:
                return 0.0
            
            cv = std_performance / mean_performance
            stability_score = 1.0 / (1.0 + cv)  # Convert to 0-1 scale where 1 is most stable
            
            return stability_score
            
        except Exception as e:
            print(f"⚠️  Stability score calculation failed: {e}")
            return 0.0
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        try:
            return {
                'optimization_metrics': self.metrics.__dict__,
                'optimization_history': self.optimization_history,
                'current_config': self.config.__dict__,
                'best_config': self.best_config,
                'performance_history': self.performance_history
            }
            
        except Exception as e:
            print(f"❌ Optimization report generation failed: {e}")
            return {'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'PerformanceOptimizer',
            'is_optimizing': self.is_optimizing,
            'current_model': self.current_model,
            'metrics': self.metrics.__dict__,
            'config': self.config.__dict__
        }
    
    async def reset_optimizer(self):
        """Reset optimizer state and metrics"""
        self.is_optimizing = False
        self.current_model = None
        self.optimization_history.clear()
        self.metrics = PerformanceMetrics()
        self.start_time = None
        self.best_config = None
        self.best_model = None
        self.performance_history.clear()
        
        print("🔄 Performance Optimizer reset")
