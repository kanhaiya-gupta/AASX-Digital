"""
Convergence Optimizer
====================

Convergence optimization for federated learning operations.
Handles training convergence, learning rate scheduling, and stability improvements.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class ConvergenceConfig:
    """Configuration for convergence optimization"""
    # Convergence methods
    learning_rate_scheduling: bool = True
    adaptive_optimization: bool = True
    momentum_optimization: bool = True
    gradient_clipping: bool = True
    
    # Learning rate scheduling settings
    initial_learning_rate: float = 0.001
    min_learning_rate: float = 1e-6
    decay_factor: float = 0.95
    patience: int = 5
    cooldown: int = 3
    
    # Adaptive optimization settings
    adaptive_factor: float = 1.1
    patience_factor: float = 0.5
    min_improvement: float = 0.001
    
    # Momentum optimization settings
    initial_momentum: float = 0.9
    max_momentum: float = 0.99
    momentum_increase: float = 0.01
    
    # Gradient clipping settings
    max_gradient_norm: float = 1.0
    clip_threshold: float = 0.5
    
    # Convergence detection settings
    convergence_threshold: float = 0.001
    stability_window: int = 10
    max_iterations: int = 1000
    
    # Performance settings
    evaluation_frequency: int = 10
    early_stopping: bool = True


@dataclass
class ConvergenceMetrics:
    """Metrics for convergence optimization"""
    # Convergence progress
    current_iteration: int = 0
    convergence_status: str = "not_converged"
    convergence_iteration: int = 0
    
    # Learning rate metrics
    current_learning_rate: float = 0.001
    learning_rate_changes: int = 0
    learning_rate_history: List[float] = None
    
    # Loss metrics
    current_loss: float = 0.0
    best_loss: float = float('inf')
    loss_history: List[float] = None
    loss_improvement: float = 0.0
    
    # Stability metrics
    loss_variance: float = 0.0
    stability_score: float = 0.0
    oscillation_count: int = 0
    
    # Optimization metrics
    gradient_norm: float = 0.0
    momentum_value: float = 0.9
    adaptive_factor_current: float = 1.0
    
    # Performance metrics
    training_time: float = 0.0
    convergence_time: float = 0.0
    efficiency_score: float = 0.0
    
    def __post_init__(self):
        if self.learning_rate_history is None:
            self.learning_rate_history = []
        if self.loss_history is None:
            self.loss_history = []


class ConvergenceOptimizer:
    """Convergence optimization implementation for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[ConvergenceConfig] = None
    ):
        """Initialize Convergence Optimizer"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or ConvergenceConfig()
        
        # Optimization state
        self.is_optimizing = False
        self.current_model = None
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = ConvergenceMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        
        # Convergence state
        self.convergence_detected = False
        self.stability_buffer: List[float] = []
        self.improvement_buffer: List[float] = []
        
        # Initialize metrics
        self.metrics.current_learning_rate = self.config.initial_learning_rate
        self.metrics.momentum_value = self.config.initial_momentum
        
    async def start_convergence_optimization(
        self,
        model_id: str,
        initial_loss: float
    ) -> Dict[str, Any]:
        """Start convergence optimization process"""
        try:
            self.start_time = datetime.now()
            self.is_optimizing = True
            self.current_model = model_id
            self.metrics.current_loss = initial_loss
            self.metrics.best_loss = initial_loss
            
            print(f"🚀 Starting convergence optimization for model: {model_id}")
            print(f"📊 Initial loss: {initial_loss:.6f}")
            
            # Initialize optimization
            await self._initialize_convergence_optimization()
            
            # Run convergence optimization loop
            optimization_results = await self._run_convergence_loop()
            
            # Finalize optimization
            final_results = await self._finalize_convergence_optimization(optimization_results)
            
            return final_results
            
        except Exception as e:
            print(f"❌ Convergence optimization failed: {e}")
            return {'status': 'failed', 'error': str(e)}
        finally:
            self.is_optimizing = False
    
    async def _initialize_convergence_optimization(self):
        """Initialize convergence optimization process"""
        try:
            # Reset convergence state
            self.convergence_detected = False
            self.stability_buffer.clear()
            self.improvement_buffer.clear()
            
            # Initialize metrics
            self.metrics.current_learning_rate = self.config.initial_learning_rate
            self.metrics.momentum_value = self.config.initial_momentum
            self.metrics.adaptive_factor_current = 1.0
            
            # Initialize history
            self.metrics.learning_rate_history = [self.config.initial_learning_rate]
            self.metrics.loss_history = [self.metrics.current_loss]
            
            print("🔧 Convergence optimization initialized")
            
        except Exception as e:
            print(f"❌ Convergence optimization initialization failed: {e}")
            raise
    
    async def _run_convergence_loop(self) -> Dict[str, Any]:
        """Run the main convergence optimization loop"""
        try:
            print(f"🔄 Running convergence optimization (max {self.config.max_iterations} iterations)...")
            
            for iteration in range(self.config.max_iterations):
                self.metrics.current_iteration = iteration + 1
                
                # Simulate training step and get new loss
                new_loss = await self._simulate_training_step()
                
                # Update loss metrics
                self.metrics.current_loss = new_loss
                self.metrics.loss_history.append(new_loss)
                
                # Check for improvement
                if new_loss < self.metrics.best_loss:
                    self.metrics.best_loss = new_loss
                    self.metrics.loss_improvement = self.metrics.best_loss - new_loss
                    self.improvement_buffer.append(self.metrics.loss_improvement)
                    
                    # Update adaptive factor
                    if self.config.adaptive_optimization:
                        await self._update_adaptive_factor()
                
                # Apply learning rate scheduling
                if self.config.learning_rate_scheduling:
                    await self._update_learning_rate()
                
                # Apply momentum optimization
                if self.config.momentum_optimization:
                    await self._update_momentum()
                
                # Apply gradient clipping
                if self.config.gradient_clipping:
                    await self._apply_gradient_clipping()
                
                # Check convergence
                if await self._check_convergence():
                    self.convergence_detected = True
                    self.metrics.convergence_status = "converged"
                    self.metrics.convergence_iteration = iteration + 1
                    print(f"🎯 Convergence detected at iteration {iteration + 1}")
                    break
                
                # Check early stopping
                if self.config.early_stopping and await self._should_stop_early():
                    print(f"⏹️  Early stopping at iteration {iteration + 1}")
                    break
                
                # Progress update
                if (iteration + 1) % 50 == 0:
                    print(f"📈 Progress: {iteration + 1}/{self.config.max_iterations}, Loss: {new_loss:.6f}")
            
            return {
                'convergence_detected': self.convergence_detected,
                'final_iteration': self.metrics.current_iteration,
                'final_loss': self.metrics.current_loss,
                'best_loss': self.metrics.best_loss,
                'convergence_iteration': self.metrics.convergence_iteration
            }
            
        except Exception as e:
            print(f"❌ Convergence loop failed: {e}")
            raise
    
    async def _simulate_training_step(self) -> float:
        """Simulate a training step and return new loss"""
        try:
            # Simulate training with current configuration
            # In practice, this would be an actual training step
            
            # Base loss reduction
            base_reduction = 0.01
            
            # Learning rate impact
            lr_impact = self.metrics.current_learning_rate * 10
            
            # Momentum impact
            momentum_impact = self.metrics.momentum_value * 0.1
            
            # Adaptive factor impact
            adaptive_impact = self.metrics.adaptive_factor_current * 0.05
            
            # Calculate new loss
            total_reduction = base_reduction + lr_impact + momentum_impact + adaptive_impact
            
            # Add some randomness to simulate real training
            noise = np.random.normal(0, 0.001)
            new_loss = max(0.0, self.metrics.current_loss - total_reduction + noise)
            
            return new_loss
            
        except Exception as e:
            print(f"❌ Training step simulation failed: {e}")
            return self.metrics.current_loss
    
    async def _update_learning_rate(self):
        """Update learning rate based on performance"""
        try:
            if len(self.metrics.loss_history) < self.config.patience + 1:
                return
            
            # Check if loss has improved recently
            recent_losses = self.metrics.loss_history[-self.config.patience:]
            if len(recent_losses) < 2:
                return
            
            # Calculate improvement
            improvement = recent_losses[0] - recent_losses[-1]
            
            if improvement < self.config.min_improvement:
                # Reduce learning rate
                new_lr = self.metrics.current_learning_rate * self.config.decay_factor
                new_lr = max(new_lr, self.config.min_learning_rate)
                
                if new_lr != self.metrics.current_learning_rate:
                    self.metrics.current_learning_rate = new_lr
                    self.metrics.learning_rate_history.append(new_lr)
                    self.metrics.learning_rate_changes += 1
                    print(f"📉 Learning rate reduced to: {new_lr:.6f}")
            
        except Exception as e:
            print(f"⚠️  Learning rate update failed: {e}")
    
    async def _update_momentum(self):
        """Update momentum based on performance"""
        try:
            if len(self.metrics.loss_history) < 5:
                return
            
            # Check recent performance
            recent_losses = self.metrics.loss_history[-5:]
            if len(recent_losses) < 2:
                return
            
            # Calculate trend
            trend = recent_losses[-1] - recent_losses[0]
            
            if trend < 0:  # Improving
                # Increase momentum
                new_momentum = min(
                    self.metrics.momentum_value + self.config.momentum_increase,
                    self.config.max_momentum
                )
                if new_momentum != self.metrics.momentum_value:
                    self.metrics.momentum_value = new_momentum
                    print(f"📈 Momentum increased to: {new_momentum:.3f}")
            else:  # Stagnating or worsening
                # Decrease momentum
                new_momentum = max(
                    self.metrics.momentum_value * 0.95,
                    0.5
                )
                if new_momentum != self.metrics.momentum_value:
                    self.metrics.momentum_value = new_momentum
                    print(f"📉 Momentum decreased to: {new_momentum:.3f}")
            
        except Exception as e:
            print(f"⚠️  Momentum update failed: {e}")
    
    async def _update_adaptive_factor(self):
        """Update adaptive factor based on improvement"""
        try:
            if len(self.improvement_buffer) < 3:
                return
            
            # Calculate recent improvement trend
            recent_improvements = self.improvement_buffer[-3:]
            avg_improvement = np.mean(recent_improvements)
            
            if avg_improvement > self.config.min_improvement:
                # Good improvement, increase adaptive factor
                self.metrics.adaptive_factor_current = min(
                    self.metrics.adaptive_factor_current * self.config.adaptive_factor,
                    2.0
                )
            else:
                # Poor improvement, decrease adaptive factor
                self.metrics.adaptive_factor_current = max(
                    self.metrics.adaptive_factor_current * self.config.patience_factor,
                    0.5
                )
            
        except Exception as e:
            print(f"⚠️  Adaptive factor update failed: {e}")
    
    async def _apply_gradient_clipping(self):
        """Apply gradient clipping"""
        try:
            # Simulate gradient norm calculation
            # In practice, this would be calculated from actual gradients
            
            # Simulate gradient norm
            self.metrics.gradient_norm = np.random.exponential(0.5)
            
            # Apply clipping if needed
            if self.metrics.gradient_norm > self.config.max_gradient_norm:
                clip_factor = self.config.max_gradient_norm / self.metrics.gradient_norm
                self.metrics.gradient_norm *= clip_factor
                
                if self.metrics.gradient_norm > self.config.clip_threshold:
                    print(f"✂️  Gradient clipped: {self.metrics.gradient_norm:.4f}")
            
        except Exception as e:
            print(f"⚠️  Gradient clipping failed: {e}")
    
    async def _check_convergence(self) -> bool:
        """Check if convergence criteria are met"""
        try:
            if len(self.metrics.loss_history) < self.config.stability_window:
                return False
            
            # Get recent losses
            recent_losses = self.metrics.loss_history[-self.config.stability_window:]
            
            # Check if loss is stable (low variance)
            loss_variance = np.var(recent_losses)
            self.metrics.loss_variance = loss_variance
            
            # Check if loss is below threshold
            current_loss = self.metrics.current_loss
            convergence_threshold = self.config.convergence_threshold
            
            # Check stability
            is_stable = loss_variance < convergence_threshold * 0.1
            is_low_loss = current_loss < convergence_threshold
            
            # Update stability score
            self.metrics.stability_score = 1.0 / (1.0 + loss_variance)
            
            # Check for oscillations
            if len(recent_losses) >= 3:
                oscillations = sum(1 for i in range(1, len(recent_losses))
                if oscillations > 0:
                    self.metrics.oscillation_count += 1
            
            return is_stable and is_low_loss
            
        except Exception as e:
            print(f"⚠️  Convergence check failed: {e}")
            return False
    
    async def _should_stop_early(self) -> bool:
        """Check if optimization should stop early"""
        try:
            # Stop if no improvement for several iterations
            if len(self.metrics.loss_history) >= 20:
                recent_losses = self.metrics.loss_history[-20:]
                if max(recent_losses) - min(recent_losses) < self.config.convergence_threshold:
                    return True
            
            # Stop if learning rate is too small
            if self.metrics.current_learning_rate < self.config.min_learning_rate * 2:
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Early stopping check failed: {e}")
            return False
    
    async def _finalize_convergence_optimization(self, optimization_results: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize convergence optimization and calculate final metrics"""
        try:
            # Calculate final metrics
            if self.convergence_detected:
                convergence_time = (datetime.now() - self.start_time).total_seconds()
                self.metrics.convergence_time = convergence_time
                
                # Calculate efficiency score
                self.metrics.efficiency_score = self._calculate_efficiency_score()
            
            # Calculate training time
            training_time = (datetime.now() - self.start_time).total_seconds()
            self.metrics.training_time = training_time
            
            # Record optimization history
            self.optimization_history.append({
                'model_id': self.current_model,
                'timestamp': datetime.now().isoformat(),
                'optimization_results': optimization_results,
                'final_metrics': self.metrics.__dict__,
                'training_time': training_time,
                'convergence_detected': self.convergence_detected
            })
            
            print(f"✅ Convergence optimization completed in {training_time:.2f}s")
            if self.convergence_detected:
                print(f"🎯 Converged at iteration {self.metrics.convergence_iteration}")
                print(f"📊 Final loss: {self.metrics.current_loss:.6f}")
            else:
                print(f"⚠️  Did not converge within {self.config.max_iterations} iterations")
            
            return {
                'status': 'success',
                'model_id': self.current_model,
                'convergence_detected': self.convergence_detected,
                'optimization_results': optimization_results,
                'final_metrics': self.metrics.__dict__,
                'training_time': training_time
            }
            
        except Exception as e:
            print(f"❌ Convergence optimization finalization failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate efficiency score based on convergence speed and final performance"""
        try:
            if not self.convergence_detected:
                return 0.0
            
            # Factors for efficiency score
            convergence_speed = 1.0 / (self.metrics.convergence_iteration / self.config.max_iterations)
            final_performance = 1.0 / (1.0 + self.metrics.current_loss)
            stability = self.metrics.stability_score
            
            # Weighted average
            efficiency_score = (0.4 * convergence_speed + 0.4 * final_performance + 0.2 * stability)
            
            return min(efficiency_score, 1.0)
            
        except Exception as e:
            print(f"⚠️  Efficiency score calculation failed: {e}")
            return 0.0
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        try:
            return {
                'optimization_metrics': self.metrics.__dict__,
                'optimization_history': self.optimization_history,
                'current_config': self.config.__dict__,
                'convergence_detected': self.convergence_detected
            }
            
        except Exception as e:
            print(f"❌ Optimization report generation failed: {e}")
            return {'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'ConvergenceOptimizer',
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
        self.metrics = ConvergenceMetrics()
        self.start_time = None
        self.convergence_detected = False
        self.stability_buffer.clear()
        self.improvement_buffer.clear()
        
        # Reinitialize metrics
        self.metrics.current_learning_rate = self.config.initial_learning_rate
        self.metrics.momentum_value = self.config.initial_momentum
        
        print("🔄 Convergence Optimizer reset")
