"""
Differential Privacy Algorithm
==============================

Implementation of differential privacy mechanisms for federated learning.
Provides advanced privacy protection with configurable privacy budgets.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class DifferentialPrivacyConfig:
    """Configuration for Differential Privacy algorithm"""
    # Privacy parameters
    epsilon: float = 1.0  # Privacy budget
    delta: float = 1e-5   # Privacy parameter
    sensitivity: float = 1.0  # Global sensitivity
    
    # Noise mechanisms
    noise_mechanism: str = "gaussian"  # gaussian, laplace, exponential
    noise_scale: float = 0.1
    adaptive_noise: bool = True
    
    # Budget management
    total_privacy_budget: float = 10.0
    budget_allocation_strategy: str = "uniform"  # uniform, adaptive, decay
    min_epsilon_per_round: float = 0.1
    
    # Performance parameters
    parallel_noise_generation: bool = True
    batch_size: int = 32
    timeout_seconds: int = 300


@dataclass
class DifferentialPrivacyMetrics:
    """Metrics for Differential Privacy algorithm performance"""
    # Privacy metrics
    privacy_budget_consumed: float = 0.0
    remaining_budget: float = 0.0
    privacy_loss: float = 0.0
    privacy_guarantee: float = 0.0
    
    # Noise metrics
    total_noise_added: float = 0.0
    avg_noise_per_parameter: float = 0.0
    noise_distribution: Dict[str, float] = None
    
    # Performance metrics
    total_rounds: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0
    avg_processing_time: float = 0.0
    
    # Quality metrics
    utility_loss: float = 0.0
    accuracy_impact: float = 0.0
    convergence_impact: float = 0.0


class DifferentialPrivacyAlgorithm:
    """Differential Privacy algorithm implementation"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[DifferentialPrivacyConfig] = None
    ):
        """Initialize Differential Privacy algorithm"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or DifferentialPrivacyConfig()
        
        # Algorithm state
        self.current_round = 0
        self.is_running = False
        self.privacy_budget_history: List[float] = []
        self.noise_history: List[float] = []
        
        # Metrics tracking
        self.metrics = DifferentialPrivacyMetrics()
        self.metrics.remaining_budget = self.config.total_privacy_budget
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.round_times: List[float] = []
    
    async def start_differential_privacy(self, federation_id: str) -> Dict[str, Any]:
        """Start differential privacy protection"""
        try:
            self.start_time = datetime.now()
            self.is_running = True
            self.current_round = 0
            
            print(f"🔒 Starting Differential Privacy protection: {federation_id}")
            
            # Initialize privacy state
            await self._initialize_privacy_state(federation_id)
            
            # Allocate initial privacy budget
            await self._allocate_privacy_budget()
            
            return {
                'status': 'started',
                'federation_id': federation_id,
                'start_time': self.start_time.isoformat(),
                'epsilon': self.config.epsilon,
                'delta': self.config.delta,
                'total_budget': self.config.total_privacy_budget,
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to start differential privacy: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def apply_differential_privacy(
        self,
        federation_id: str,
        model_updates: List[Dict[str, Any]],
        round_epsilon: Optional[float] = None
    ) -> Dict[str, Any]:
        """Apply differential privacy to model updates"""
        try:
            round_start_time = datetime.now()
            self.current_round += 1
            
            print(f"🔒 DP Round {self.current_round}: Protecting {len(model_updates)} model updates")
            
            # Validate inputs
            if not model_updates:
                raise ValueError("No model updates provided")
            
            # Check privacy budget
            if not await self._check_privacy_budget(round_epsilon):
                raise ValueError("Insufficient privacy budget")
            
            # Calculate noise parameters
            noise_params = await self._calculate_noise_parameters(round_epsilon)
            
            # Apply differential privacy
            protected_updates = await self._protect_model_updates(model_updates, noise_params)
            
            # Update privacy budget
            await self._update_privacy_budget(round_epsilon or self.config.epsilon)
            
            # Update metrics
            round_time = (datetime.now() - round_start_time).total_seconds()
            self.round_times.append(round_time)
            self.metrics.total_rounds = self.current_round
            self.metrics.successful_rounds += 1
            self.metrics.avg_processing_time = np.mean(self.round_times)
            
            print(f"✅ DP Round {self.current_round} completed in {round_time:.2f}s")
            
            return {
                'status': 'success',
                'round': self.current_round,
                'protected_updates': protected_updates,
                'noise_parameters': noise_params,
                'privacy_budget_used': round_epsilon or self.config.epsilon,
                'remaining_budget': self.metrics.remaining_budget,
                'round_time': round_time
            }
            
        except Exception as e:
            print(f"❌ Differential privacy application failed: {e}")
            self.metrics.failed_rounds += 1
            return {'status': 'failed', 'error': str(e)}
    
    async def _initialize_privacy_state(self, federation_id: str):
        """Initialize privacy protection state"""
        try:
            print(f"🔒 Initializing privacy state for: {federation_id}")
            
            # Reset privacy metrics
            self.privacy_budget_history.clear()
            self.noise_history.clear()
            
            # Initialize noise distribution tracking
            self.metrics.noise_distribution = {
                'gaussian': 0.0,
                'laplace': 0.0,
                'exponential': 0.0
            }
            
        except Exception as e:
            print(f"⚠️  Privacy state initialization failed: {e}")
    
    async def _allocate_privacy_budget(self):
        """Allocate privacy budget for the federation"""
        try:
            if self.config.budget_allocation_strategy == "uniform":
                # Uniform allocation across expected rounds
                expected_rounds = 10  # Default expectation
                self.config.epsilon = self.config.total_privacy_budget / expected_rounds
                
            elif self.config.budget_allocation_strategy == "adaptive":
                # Adaptive allocation based on progress
                self.config.epsilon = self.config.total_privacy_budget * 0.1  # Start with 10%
                
            elif self.config.budget_allocation_strategy == "decay":
                # Decay allocation (more budget early, less later)
                self.config.epsilon = self.config.total_privacy_budget * 0.2  # Start with 20%
            
            # Ensure minimum epsilon
            self.config.epsilon = max(self.config.epsilon, self.config.min_epsilon_per_round)
            
            print(f"💰 Allocated privacy budget: ε={self.config.epsilon:.4f}")
            
        except Exception as e:
            print(f"⚠️  Privacy budget allocation failed: {e}")
    
    async def _check_privacy_budget(self, round_epsilon: Optional[float]) -> bool:
        """Check if sufficient privacy budget is available"""
        try:
            epsilon_to_use = round_epsilon or self.config.epsilon
            
            if self.metrics.remaining_budget < epsilon_to_use:
                print(f"⚠️  Insufficient privacy budget: {self.metrics.remaining_budget:.4f} < {epsilon_to_use:.4f}")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️  Privacy budget check failed: {e}")
            return False
    
    async def _calculate_noise_parameters(self, round_epsilon: Optional[float]) -> Dict[str, Any]:
        """Calculate noise parameters for differential privacy"""
        try:
            epsilon = round_epsilon or self.config.epsilon
            
            if self.config.noise_mechanism == "gaussian":
                # Gaussian noise parameters
                sigma = np.sqrt(2 * np.log(1.25 / self.config.delta)) / epsilon
                noise_params = {
                    'mechanism': 'gaussian',
                    'sigma': sigma,
                    'epsilon': epsilon,
                    'delta': self.config.delta
                }
                
            elif self.config.noise_mechanism == "laplace":
                # Laplace noise parameters
                scale = self.config.sensitivity / epsilon
                noise_params = {
                    'mechanism': 'laplace',
                    'scale': scale,
                    'epsilon': epsilon
                }
                
            elif self.config.noise_mechanism == "exponential":
                # Exponential mechanism parameters
                noise_params = {
                    'mechanism': 'exponential',
                    'epsilon': epsilon,
                    'sensitivity': self.config.sensitivity
                }
            
            # Apply adaptive noise scaling if enabled
            if self.config.adaptive_noise:
                noise_params = await self._apply_adaptive_noise_scaling(noise_params)
            
            return noise_params
            
        except Exception as e:
            print(f"❌ Noise parameter calculation failed: {e}")
            raise
    
    async def _apply_adaptive_noise_scaling(self, noise_params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply adaptive noise scaling based on model complexity"""
        try:
            # Simple adaptive scaling based on round number
            scaling_factor = 1.0 + (self.current_round * 0.1)
            
            if 'sigma' in noise_params:
                noise_params['sigma'] *= scaling_factor
            elif 'scale' in noise_params:
                noise_params['scale'] *= scaling_factor
            
            noise_params['adaptive_scaling'] = scaling_factor
            
            return noise_params
            
        except Exception as e:
            print(f"⚠️  Adaptive noise scaling failed: {e}")
            return noise_params
    
    async def _protect_model_updates(
        self,
        model_updates: List[Dict[str, Any]],
        noise_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply differential privacy protection to model updates"""
        try:
            protected_updates = []
            
            for update in model_updates:
                try:
                    # Protect single model update
                    protected_update = await self._protect_single_update(update, noise_params)
                    protected_updates.append(protected_update)
                    
                except Exception as e:
                    print(f"⚠️  Failed to protect update: {e}")
                    continue
            
            return protected_updates
            
        except Exception as e:
            print(f"❌ Model update protection failed: {e}")
            raise
    
    async def _protect_single_update(
        self,
        update: Dict[str, Any],
        noise_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Protect a single model update with differential privacy"""
        try:
            protected_update = update.copy()
            model_params = update.get('model_parameters', {})
            protected_params = {}
            
            # Add noise to each parameter
            for param_name, param_value in model_params.items():
                if isinstance(param_value, (int, float)):
                    # Scalar values
                    noise = await self._generate_noise(noise_params)
                    protected_params[param_name] = param_value + noise
                    
                elif isinstance(param_value, np.ndarray):
                    # Array values
                    noise = await self._generate_array_noise(param_value.shape, noise_params)
                    protected_params[param_name] = param_value + noise
                    
                else:
                    # Other types - keep as is
                    protected_params[param_name] = param_value
            
            # Update the protected update
            protected_update['model_parameters'] = protected_params
            protected_update['privacy_protection'] = {
                'mechanism': noise_params['mechanism'],
                'epsilon_used': noise_params['epsilon'],
                'timestamp': datetime.now().isoformat()
            }
            
            return protected_update
            
        except Exception as e:
            print(f"❌ Single update protection failed: {e}")
            raise
    
    async def _generate_noise(self, noise_params: Dict[str, Any]) -> float:
        """Generate noise based on the specified mechanism"""
        try:
            if noise_params['mechanism'] == 'gaussian':
                noise = np.random.normal(0, noise_params['sigma'])
            elif noise_params['mechanism'] == 'laplace':
                noise = np.random.laplace(0, noise_params['scale'])
            elif noise_params['mechanism'] == 'exponential':
                noise = np.random.exponential(noise_params['sensitivity'] / noise_params['epsilon'])
            else:
                noise = 0.0
            
            # Track noise statistics
            self.noise_history.append(abs(noise))
            self.metrics.total_noise_added += abs(noise)
            
            return noise
            
        except Exception as e:
            print(f"⚠️  Noise generation failed: {e}")
            return 0.0
    
    async def _generate_array_noise(
        self,
        shape: Tuple[int, ...],
        noise_params: Dict[str, Any]
    ) -> np.ndarray:
        """Generate noise array for numpy arrays"""
        try:
            if noise_params['mechanism'] == 'gaussian':
                noise = np.random.normal(0, noise_params['sigma'], shape)
            elif noise_params['mechanism'] == 'laplace':
                noise = np.random.laplace(0, noise_params['scale'], shape)
            elif noise_params['mechanism'] == 'exponential':
                noise = np.random.exponential(noise_params['sensitivity'] / noise_params['epsilon'], shape)
            else:
                noise = np.zeros(shape)
            
            # Track noise statistics
            self.noise_history.append(np.mean(np.abs(noise)))
            self.metrics.total_noise_added += np.sum(np.abs(noise))
            
            return noise
            
        except Exception as e:
            print(f"⚠️  Array noise generation failed: {e}")
            return np.zeros(shape)
    
    async def _update_privacy_budget(self, epsilon_used: float):
        """Update privacy budget after using epsilon"""
        try:
            self.metrics.privacy_budget_consumed += epsilon_used
            self.metrics.remaining_budget -= epsilon_used
            self.privacy_budget_history.append(self.metrics.remaining_budget)
            
            # Update privacy guarantee
            self.metrics.privacy_guarantee = 1.0 / (1.0 + self.metrics.privacy_budget_consumed)
            
            print(f"💰 Privacy budget updated: {epsilon_used:.4f} used, {self.metrics.remaining_budget:.4f} remaining")
            
        except Exception as e:
            print(f"⚠️  Privacy budget update failed: {e}")
    
    async def get_privacy_report(self) -> Dict[str, Any]:
        """Get comprehensive privacy protection report"""
        try:
            # Calculate additional metrics
            if self.noise_history:
                self.metrics.avg_noise_per_parameter = np.mean(self.noise_history)
            
            # Update noise distribution
            if self.config.noise_mechanism == 'gaussian':
                self.metrics.noise_distribution['gaussian'] = 1.0
            elif self.config.noise_mechanism == 'laplace':
                self.metrics.noise_distribution['laplace'] = 1.0
            elif self.config.noise_mechanism == 'exponential':
                self.metrics.noise_distribution['exponential'] = 1.0
            
            return {
                'privacy_metrics': self.metrics.__dict__,
                'budget_history': self.privacy_budget_history,
                'noise_history': self.noise_history,
                'current_config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Privacy report generation failed: {e}")
            return {'error': str(e)}
    
    async def stop_differential_privacy(self) -> Dict[str, Any]:
        """Stop differential privacy protection"""
        try:
            self.is_running = False
            
            # Generate final privacy report
            privacy_report = await self.get_privacy_report()
            
            print(f"🛑 Differential Privacy protection stopped after {self.current_round} rounds")
            
            return {
                'status': 'stopped',
                'total_rounds': self.current_round,
                'final_privacy_report': privacy_report
            }
            
        except Exception as e:
            print(f"❌ Failed to stop differential privacy: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'DifferentialPrivacy',
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
        self.privacy_budget_history.clear()
        self.noise_history.clear()
        self.round_times.clear()
        self.metrics = DifferentialPrivacyMetrics()
        self.metrics.remaining_budget = self.config.total_privacy_budget
        self.start_time = None
        
        print("🔄 Differential Privacy algorithm reset") 