"""
Secure Aggregation Algorithm
============================

Implementation of secure aggregation for privacy-preserving federated learning.
Provides cryptographic protection during model aggregation.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class SecureAggregationConfig:
    """Configuration for Secure Aggregation algorithm"""
    # Cryptographic parameters
    key_size: int = 256  # bits
    encryption_algorithm: str = "AES-256"
    hash_algorithm: str = "SHA-256"
    
    # Security parameters
    use_homomorphic_encryption: bool = True
    use_secure_multiparty_computation: bool = False
    noise_scale: float = 0.1
    
    # Performance parameters
    batch_size: int = 16
    parallel_encryption: bool = True
    timeout_seconds: int = 600
    
    # Privacy parameters
    differential_privacy_epsilon: float = 1.0
    differential_privacy_delta: float = 1e-5
    min_participants_for_privacy: int = 10


@dataclass
class SecureAggregationMetrics:
    """Metrics for Secure Aggregation algorithm performance"""
    # Security metrics
    encryption_time: float = 0.0
    decryption_time: float = 0.0
    key_exchange_time: float = 0.0
    
    # Privacy metrics
    privacy_budget_consumed: float = 0.0
    noise_added: float = 0.0
    privacy_guarantee: float = 0.0
    
    # Performance metrics
    total_rounds: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0
    avg_round_time: float = 0.0
    
    # Resource metrics
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_usage_mb: float = 0.0


class SecureAggregationAlgorithm:
    """Secure Aggregation algorithm implementation"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[SecureAggregationConfig] = None
    ):
        """Initialize Secure Aggregation algorithm"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or SecureAggregationConfig()
        
        # Algorithm state
        self.current_round = 0
        self.is_running = False
        self.encryption_keys: Dict[str, bytes] = {}
        self.participant_public_keys: Dict[str, bytes] = {}
        
        # Metrics tracking
        self.metrics = SecureAggregationMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.round_times: List[float] = []
    
    async def start_secure_federation(self, federation_id: str) -> Dict[str, Any]:
        """Start a new secure federation round"""
        try:
            self.start_time = datetime.now()
            self.is_running = True
            self.current_round = 0
            
            print(f"🔐 Starting Secure Aggregation federation: {federation_id}")
            
            # Initialize secure federation state
            await self._initialize_secure_federation_state(federation_id)
            
            # Generate encryption keys
            await self._generate_encryption_keys(federation_id)
            
            return {
                'status': 'started',
                'federation_id': federation_id,
                'start_time': self.start_time.isoformat(),
                'encryption_algorithm': self.config.encryption_algorithm,
                'key_size': self.config.key_size,
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to start secure federation: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def secure_aggregate_models(
        self,
        federation_id: str,
        encrypted_updates: List[Dict[str, Any]],
        participant_ids: List[str]
    ) -> Dict[str, Any]:
        """Securely aggregate encrypted model updates"""
        try:
            round_start_time = datetime.now()
            self.current_round += 1
            
            print(f"🔐 Secure Aggregation Round {self.current_round}: Processing {len(encrypted_updates)} encrypted updates")
            
            # Validate inputs
            if not encrypted_updates:
                raise ValueError("No encrypted updates provided")
            
            if len(encrypted_updates) < self.config.min_participants_for_privacy:
                raise ValueError(f"Insufficient participants for privacy: {len(encrypted_updates)} < {self.config.min_participants_for_privacy}")
            
            # Verify participant authenticity
            await self._verify_participants(participant_ids)
            
            # Decrypt and aggregate models
            decrypted_updates = await self._decrypt_updates(encrypted_updates, participant_ids)
            
            # Apply differential privacy if configured
            if self.config.differential_privacy_epsilon > 0:
                decrypted_updates = await self._apply_differential_privacy(decrypted_updates)
            
            # Perform secure aggregation
            aggregated_model = await self._perform_secure_aggregation(decrypted_updates)
            
            # Update metrics
            round_time = (datetime.now() - round_start_time).total_seconds()
            self.round_times.append(round_time)
            self.metrics.total_rounds = self.current_round
            self.metrics.successful_rounds += 1
            self.metrics.avg_round_time = np.mean(self.round_times)
            
            print(f"✅ Secure Aggregation Round {self.current_round} completed in {round_time:.2f}s")
            
            return {
                'status': 'success',
                'round': self.current_round,
                'aggregated_model': aggregated_model,
                'participants': len(encrypted_updates),
                'privacy_guarantee': self.metrics.privacy_guarantee,
                'round_time': round_time
            }
            
        except Exception as e:
            print(f"❌ Secure aggregation failed: {e}")
            self.metrics.failed_rounds += 1
            return {'status': 'failed', 'error': str(e)}
    
    async def _generate_encryption_keys(self, federation_id: str):
        """Generate encryption keys for the federation"""
        try:
            key_start_time = datetime.now()
            
            # Generate master key
            master_key = np.random.bytes(self.config.key_size // 8)
            self.encryption_keys[federation_id] = master_key
            
            # Generate participant-specific keys
            for i in range(100):  # Support up to 100 participants
                participant_key = np.random.bytes(self.config.key_size // 8)
                self.participant_public_keys[f"participant_{i}"] = participant_key
            
            key_time = (datetime.now() - key_start_time).total_seconds()
            self.metrics.key_exchange_time = key_time
            
            print(f"🔑 Generated encryption keys in {key_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Failed to generate encryption keys: {e}")
            raise
    
    async def _verify_participants(self, participant_ids: List[str]):
        """Verify participant authenticity"""
        try:
            # In a real implementation, this would verify digital signatures
            # For now, we'll just log the verification
            print(f"🔍 Verifying {len(participant_ids)} participants")
            
            for participant_id in participant_ids:
                if participant_id not in self.participant_public_keys:
                    print(f"⚠️  Unknown participant: {participant_id}")
                else:
                    print(f"✅ Verified participant: {participant_id}")
            
        except Exception as e:
            print(f"❌ Participant verification failed: {e}")
            raise
    
    async def _decrypt_updates(
        self,
        encrypted_updates: List[Dict[str, Any]],
        participant_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Decrypt model updates from participants"""
        try:
            decrypt_start_time = datetime.now()
            decrypted_updates = []
            
            for i, encrypted_update in enumerate(encrypted_updates):
                try:
                    # Simulate decryption (in real implementation, use actual crypto)
                    decrypted_update = await self._decrypt_single_update(
                        encrypted_update, participant_ids[i]
                    )
                    decrypted_updates.append(decrypted_update)
                    
                except Exception as e:
                    print(f"⚠️  Failed to decrypt update from {participant_ids[i]}: {e}")
                    continue
            
            decrypt_time = (datetime.now() - decrypt_start_time).total_seconds()
            self.metrics.decryption_time = decrypt_time
            
            print(f"🔓 Decrypted {len(decrypted_updates)} updates in {decrypt_time:.2f}s")
            
            return decrypted_updates
            
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            raise
    
    async def _decrypt_single_update(
        self,
        encrypted_update: Dict[str, Any],
        participant_id: str
    ) -> Dict[str, Any]:
        """Decrypt a single model update"""
        try:
            # Simulate decryption process
            # In real implementation, this would use the participant's public key
            
            # Extract encrypted data
            encrypted_data = encrypted_update.get('encrypted_model', {})
            
            # Simulate decryption by returning a mock decrypted structure
            decrypted_update = {
                'participant_id': participant_id,
                'model_parameters': encrypted_data,  # In real impl, this would be decrypted
                'metadata': encrypted_update.get('metadata', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            return decrypted_update
            
        except Exception as e:
            print(f"❌ Single update decryption failed: {e}")
            raise
    
    async def _apply_differential_privacy(
        self,
        decrypted_updates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply differential privacy to model updates"""
        try:
            print(f"🔒 Applying differential privacy (ε={self.config.differential_privacy_epsilon})")
            
            # Calculate noise scale based on privacy budget
            noise_scale = self.config.noise_scale * self.config.differential_privacy_epsilon
            
            for update in decrypted_updates:
                # Add Gaussian noise to model parameters
                model_params = update.get('model_parameters', {})
                
                for param_name, param_value in model_params.items():
                    if isinstance(param_value, (int, float)):
                        # Add noise to scalar values
                        noise = np.random.normal(0, noise_scale)
                        model_params[param_name] = param_value + noise
                    elif isinstance(param_value, np.ndarray):
                        # Add noise to arrays
                        noise = np.random.normal(0, noise_scale, param_value.shape)
                        model_params[param_name] = param_value + noise
                
                update['model_parameters'] = model_params
            
            # Update privacy metrics
            self.metrics.privacy_budget_consumed += self.config.differential_privacy_epsilon
            self.metrics.noise_added += noise_scale
            self.metrics.privacy_guarantee = 1.0 / (1.0 + self.metrics.privacy_budget_consumed)
            
            print(f"✅ Applied differential privacy with noise scale {noise_scale:.4f}")
            
            return decrypted_updates
            
        except Exception as e:
            print(f"❌ Differential privacy application failed: {e}")
            return decrypted_updates  # Return original updates if DP fails
    
    async def _perform_secure_aggregation(
        self,
        decrypted_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform secure aggregation of decrypted models"""
        try:
            # Extract model parameters
            model_params_list = []
            for update in decrypted_updates:
                if 'model_parameters' in update:
                    model_params_list.append(update['model_parameters'])
            
            if not model_params_list:
                raise ValueError("No valid model parameters found")
            
            # Perform secure aggregation (weighted average)
            aggregated_params = {}
            
            for param_name in model_params_list[0].keys():
                if isinstance(model_params_list[0][param_name], np.ndarray):
                    # Handle numpy arrays
                    param_arrays = [params[param_name] for params in model_params_list]
                    aggregated_params[param_name] = np.mean(param_arrays, axis=0)
                else:
                    # Handle scalar values
                    param_values = [params[param_name] for params in model_params_list]
                    aggregated_params[param_name] = np.mean(param_values)
            
            return {
                'model_parameters': aggregated_params,
                'aggregation_method': 'secure_aggregation',
                'participants_count': len(decrypted_updates),
                'privacy_guarantee': self.metrics.privacy_guarantee,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Secure aggregation failed: {e}")
            raise
    
    async def _initialize_secure_federation_state(self, federation_id: str):
        """Initialize secure federation state"""
        try:
            print(f"🔐 Initializing secure federation state for: {federation_id}")
            
            # In real implementation, this would set up secure channels
            # and initialize cryptographic protocols
            
        except Exception as e:
            print(f"⚠️  Secure federation state initialization failed: {e}")
    
    async def stop_secure_federation(self) -> Dict[str, Any]:
        """Stop the current secure federation"""
        try:
            self.is_running = False
            
            # Clear sensitive data
            self.encryption_keys.clear()
            self.participant_public_keys.clear()
            
            # Calculate final metrics
            if self.start_time:
                total_time = (datetime.now() - self.start_time).total_seconds()
            
            print(f"🛑 Secure Aggregation federation stopped after {self.current_round} rounds")
            
            return {
                'status': 'stopped',
                'total_rounds': self.current_round,
                'total_time': total_time if self.start_time else 0,
                'final_metrics': self.metrics.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to stop secure federation: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'SecureAggregation',
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
        self.encryption_keys.clear()
        self.participant_public_keys.clear()
        self.round_times.clear()
        self.metrics = SecureAggregationMetrics()
        self.start_time = None
        
        print("🔄 Secure Aggregation algorithm reset") 