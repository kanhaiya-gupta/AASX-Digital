"""
Aggregation Utilities
====================

Model aggregation utility functions for federated learning.
Handles model parameter aggregation, weighting, and quality assessment.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class AggregationConfig:
    """Configuration for aggregation utilities"""
    # Aggregation methods
    fedavg_enabled: bool = True
    weighted_averaging_enabled: bool = True
    secure_aggregation_enabled: bool = True
    quality_based_weighting: bool = True
    
    # Weighting strategies
    data_size_weighting: bool = True
    performance_weighting: bool = True
    quality_weighting: bool = True
    time_weighting: bool = True
    
    # Quality thresholds
    min_quality_score: float = 0.5
    min_data_size: int = 100
    max_age_hours: float = 24.0
    
    # Aggregation parameters
    convergence_threshold: float = 0.001
    max_iterations: int = 100
    batch_size: int = 1000


@dataclass
class AggregationMetrics:
    """Metrics for aggregation operations"""
    # Aggregation statistics
    models_aggregated: int = 0
    total_parameters: int = 0
    aggregation_time: float = 0.0
    
    # Quality metrics
    average_quality_score: float = 0.0
    quality_improvement: float = 0.0
    convergence_rate: float = 0.0
    
    # Performance metrics
    memory_usage_mb: float = 0.0
    processing_efficiency: float = 0.0
    
    # Weighting metrics
    weight_distribution: Dict[str, float] = None
    outlier_detection_count: int = 0
    
    def __post_init__(self):
        if self.weight_distribution is None:
            self.weight_distribution = {}


class AggregationUtils:
    """Aggregation utility functions for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[AggregationConfig] = None
    ):
        """Initialize Aggregation Utils"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or AggregationConfig()
        
        # Aggregation state
        self.aggregation_history: List[Dict[str, Any]] = []
        self.weight_cache: Dict[str, float] = {}
        
        # Metrics tracking
        self.metrics = AggregationMetrics()
        
    async def aggregate_models(
        self,
        model_updates: List[Dict[str, Any]],
        aggregation_method: str = "fedavg"
    ) -> Dict[str, Any]:
        """Aggregate multiple model updates into a single model"""
        try:
            start_time = datetime.now()
            
            if not model_updates:
                return {'error': 'No model updates provided'}
            
            print(f"🔄 Aggregating {len(model_updates)} models using {aggregation_method}")
            
            # Validate model updates
            validated_updates = await self._validate_model_updates(model_updates)
            
            if not validated_updates:
                return {'error': 'No valid model updates found'}
            
            # Calculate aggregation weights
            weights = await self._calculate_aggregation_weights(validated_updates)
            
            # Perform aggregation based on method
            if aggregation_method == "fedavg":
                aggregated_model = await self._federated_averaging(validated_updates, weights)
            elif aggregation_method == "weighted":
                aggregated_model = await self._weighted_averaging(validated_updates, weights)
            elif aggregation_method == "secure":
                aggregated_model = await self._secure_aggregation(validated_updates, weights)
            else:
                return {'error': f'Unknown aggregation method: {aggregation_method}'}
            
            # Calculate aggregation metrics
            await self._calculate_aggregation_metrics(validated_updates, weights, start_time)
            
            # Record aggregation history
            self.aggregation_history.append({
                'timestamp': datetime.now().isoformat(),
                'method': aggregation_method,
                'models_count': len(validated_updates),
                'weights': weights,
                'metrics': self.metrics.__dict__
            })
            
            return {
                'status': 'success',
                'aggregated_model': aggregated_model,
                'aggregation_metrics': self.metrics.__dict__,
                'method': aggregation_method,
                'models_processed': len(validated_updates)
            }
            
        except Exception as e:
            print(f"❌ Model aggregation failed: {e}")
            return {'error': str(e)}
    
    async def _validate_model_updates(self, model_updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate model updates and filter out invalid ones"""
        try:
            validated_updates = []
            
            for update in model_updates:
                # Check required fields
                if not all(key in update for key in ['model_id', 'parameters', 'metadata']):
                    print(f"⚠️  Skipping invalid model update: missing required fields")
                    continue
                
                # Check quality threshold
                quality_score = update.get('metadata', {}).get('quality_score', 0.0)
                if quality_score < self.config.min_quality_score:
                    print(f"⚠️  Skipping model {update['model_id']}: quality score {quality_score} below threshold")
                    continue
                
                # Check data size threshold
                data_size = update.get('metadata', {}).get('data_size', 0)
                if data_size < self.config.min_data_size:
                    print(f"⚠️  Skipping model {update['model_id']}: data size {data_size} below threshold")
                    continue
                
                # Check age threshold
                timestamp = update.get('metadata', {}).get('timestamp')
                if timestamp:
                    try:
                        update_time = datetime.fromisoformat(timestamp)
                        age_hours = (datetime.now() - update_time).total_seconds() / 3600
                        if age_hours > self.config.max_age_hours:
                            print(f"⚠️  Skipping model {update['model_id']}: too old ({age_hours:.1f} hours)")
                            continue
                    except:
                        pass
                
                validated_updates.append(update)
            
            print(f"✅ Validated {len(validated_updates)} out of {len(model_updates)} model updates")
            return validated_updates
            
        except Exception as e:
            print(f"❌ Model update validation failed: {e}")
            return []
    
    async def _calculate_aggregation_weights(self, model_updates: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate aggregation weights for each model"""
        try:
            weights = {}
            total_weight = 0.0
            
            for update in model_updates:
                model_id = update['model_id']
                metadata = update.get('metadata', {})
                
                # Initialize weight
                weight = 1.0
                
                # Data size weighting
                if self.config.data_size_weighting:
                    data_size = metadata.get('data_size', 100)
                    weight *= np.sqrt(data_size)  # Square root to reduce extreme differences
                
                # Performance weighting
                if self.config.performance_weighting:
                    performance_score = metadata.get('performance_score', 0.5)
                    weight *= (1.0 + performance_score)  # Boost high-performing models
                
                # Quality weighting
                if self.config.quality_weighting:
                    quality_score = metadata.get('quality_score', 0.5)
                    weight *= quality_score
                
                # Time weighting
                if self.config.time_weighting:
                    timestamp = metadata.get('timestamp')
                    if timestamp:
                        try:
                            update_time = datetime.fromisoformat(timestamp)
                            age_hours = (datetime.now() - update_time).total_seconds() / 3600
                            time_factor = max(0.1, 1.0 - age_hours / self.config.max_age_hours)
                            weight *= time_factor
                        except:
                            pass
                
                weights[model_id] = weight
                total_weight += weight
            
            # Normalize weights
            if total_weight > 0:
                for model_id in weights:
                    weights[model_id] /= total_weight
            
            # Cache weights for metrics
            self.weight_cache = weights.copy()
            
            return weights
            
        except Exception as e:
            print(f"❌ Weight calculation failed: {e}")
            # Return equal weights as fallback
            return {update['model_id']: 1.0 / len(model_updates) for update in model_updates}
    
    async def _federated_averaging(
        self,
        model_updates: List[Dict[str, Any]],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Perform federated averaging aggregation"""
        try:
            print("📊 Performing federated averaging...")
            
            # Get first model to determine structure
            first_model = model_updates[0]
            aggregated_parameters = {}
            
            # Aggregate each parameter
            for param_name, param_value in first_model['parameters'].items():
                if isinstance(param_value, np.ndarray):
                    # Handle numpy arrays
                    aggregated_parameters[param_name] = await self._aggregate_parameter_arrays(
                        model_updates, param_name, weights
                    )
                elif isinstance(param_value, (int, float)):
                    # Handle scalar values
                    aggregated_parameters[param_name] = await self._aggregate_parameter_scalars(
                        model_updates, param_name, weights
                    )
                else:
                    # Handle other types (use first model's value)
                    aggregated_parameters[param_name] = param_value
            
            return {
                'model_id': f"aggregated_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'parameters': aggregated_parameters,
                'metadata': {
                    'aggregation_method': 'fedavg',
                    'timestamp': datetime.now().isoformat(),
                    'source_models': [update['model_id'] for update in model_updates],
                    'weights': weights
                }
            }
            
        except Exception as e:
            print(f"❌ Federated averaging failed: {e}")
            raise
    
    async def _weighted_averaging(
        self,
        model_updates: List[Dict[str, Any]],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Perform weighted averaging aggregation"""
        try:
            print("⚖️  Performing weighted averaging...")
            
            # Similar to federated averaging but with explicit weight application
            first_model = model_updates[0]
            aggregated_parameters = {}
            
            for param_name, param_value in first_model['parameters'].items():
                if isinstance(param_value, np.ndarray):
                    aggregated_parameters[param_name] = await self._aggregate_parameter_arrays(
                        model_updates, param_name, weights
                    )
                elif isinstance(param_value, (int, float)):
                    aggregated_parameters[param_name] = await self._aggregate_parameter_scalars(
                        model_updates, param_name, weights
                    )
                else:
                    aggregated_parameters[param_name] = param_value
            
            return {
                'model_id': f"weighted_aggregated_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'parameters': aggregated_parameters,
                'metadata': {
                    'aggregation_method': 'weighted',
                    'timestamp': datetime.now().isoformat(),
                    'source_models': [update['model_id'] for update in model_updates],
                    'weights': weights
                }
            }
            
        except Exception as e:
            print(f"❌ Weighted averaging failed: {e}")
            raise
    
    async def _secure_aggregation(
        self,
        model_updates: List[Dict[str, Any]],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Perform secure aggregation (simplified implementation)"""
        try:
            print("🔒 Performing secure aggregation...")
            
            # Simplified secure aggregation
            # In practice, this would use cryptographic techniques like homomorphic encryption
            
            # For now, use weighted averaging with noise addition
            first_model = model_updates[0]
            aggregated_parameters = {}
            
            for param_name, param_value in first_model['parameters'].items():
                if isinstance(param_value, np.ndarray):
                    # Add noise for privacy
                    base_aggregation = await self._aggregate_parameter_arrays(
                        model_updates, param_name, weights
                    )
                    noise = np.random.normal(0, 0.01, base_aggregation.shape)
                    aggregated_parameters[param_name] = base_aggregation + noise
                elif isinstance(param_value, (int, float)):
                    base_aggregation = await self._aggregate_parameter_scalars(
                        model_updates, param_name, weights
                    )
                    noise = np.random.normal(0, 0.01)
                    aggregated_parameters[param_name] = base_aggregation + noise
                else:
                    aggregated_parameters[param_name] = param_value
            
            return {
                'model_id': f"secure_aggregated_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'parameters': aggregated_parameters,
                'metadata': {
                    'aggregation_method': 'secure',
                    'timestamp': datetime.now().isoformat(),
                    'source_models': [update['model_id'] for update in model_updates],
                    'weights': weights,
                    'privacy_noise_added': True
                }
            }
            
        except Exception as e:
            print(f"❌ Secure aggregation failed: {e}")
            raise
    
    async def _aggregate_parameter_arrays(
        self,
        model_updates: List[Dict[str, Any]],
        param_name: str,
        weights: Dict[str, Any]
    ) -> np.ndarray:
        """Aggregate parameter arrays using weighted averaging"""
        try:
            # Initialize with zeros
            first_array = model_updates[0]['parameters'][param_name]
            aggregated_array = np.zeros_like(first_array, dtype=np.float64)
            
            # Weighted sum
            for update in model_updates:
                model_id = update['model_id']
                weight = weights.get(model_id, 1.0 / len(model_updates))
                param_array = update['parameters'][param_name]
                
                # Ensure arrays have same shape
                if param_array.shape == first_array.shape:
                    aggregated_array += weight * param_array.astype(np.float64)
                else:
                    print(f"⚠️  Shape mismatch for parameter {param_name} in model {model_id}")
            
            return aggregated_array
            
        except Exception as e:
            print(f"❌ Parameter array aggregation failed: {e}")
            raise
    
    async def _aggregate_parameter_scalars(
        self,
        model_updates: List[Dict[str, Any]],
        param_name: str,
        weights: Dict[str, Any]
    ) -> float:
        """Aggregate scalar parameters using weighted averaging"""
        try:
            aggregated_value = 0.0
            
            for update in model_updates:
                model_id = update['model_id']
                weight = weights.get(model_id, 1.0 / len(model_updates))
                param_value = update['parameters'][param_name]
                
                if isinstance(param_value, (int, float)):
                    aggregated_value += weight * float(param_value)
            
            return aggregated_value
            
        except Exception as e:
            print(f"❌ Parameter scalar aggregation failed: {e}")
            raise
    
    async def _calculate_aggregation_metrics(
        self,
        model_updates: List[Dict[str, Any]],
        weights: Dict[str, float],
        start_time: datetime
    ):
        """Calculate aggregation performance metrics"""
        try:
            # Update basic metrics
            self.metrics.models_aggregated = len(model_updates)
            self.metrics.aggregation_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate total parameters
            total_params = 0
            for update in model_updates:
                params = update.get('parameters', {})
                for param_name, param_value in params.items():
                    if isinstance(param_value, np.ndarray):
                        total_params += param_value.size
                    else:
                        total_params += 1
            
            self.metrics.total_parameters = total_params
            
            # Calculate quality metrics
            quality_scores = [update.get('metadata', {}).get('quality_score', 0.5) for update in model_updates]
            self.metrics.average_quality_score = np.mean(quality_scores)
            
            # Calculate weight distribution
            self.metrics.weight_distribution = weights.copy()
            
            # Calculate processing efficiency
            if self.metrics.aggregation_time > 0:
                self.metrics.processing_efficiency = self.metrics.total_parameters / self.metrics.aggregation_time
            
        except Exception as e:
            print(f"⚠️  Metrics calculation failed: {e}")
    
    async def detect_outliers(
        self,
        model_updates: List[Dict[str, Any]],
        threshold: float = 2.0
    ) -> List[str]:
        """Detect outlier models based on quality scores"""
        try:
            outlier_models = []
            
            if len(model_updates) < 3:
                return outlier_models
            
            # Extract quality scores
            quality_scores = []
            model_ids = []
            
            for update in model_updates:
                quality_score = update.get('metadata', {}).get('quality_score', 0.5)
                quality_scores.append(quality_score)
                model_ids.append(update['model_id'])
            
            # Calculate statistics
            mean_quality = np.mean(quality_scores)
            std_quality = np.std(quality_scores)
            
            if std_quality == 0:
                return outlier_models
            
            # Detect outliers using z-score
            for i, quality_score in enumerate(quality_scores):
                z_score = abs(quality_score - mean_quality) / std_quality
                if z_score > threshold:
                    outlier_models.append(model_ids[i])
                    self.metrics.outlier_detection_count += 1
            
            return outlier_models
            
        except Exception as e:
            print(f"❌ Outlier detection failed: {e}")
            return []
    
    async def get_aggregation_report(self) -> Dict[str, Any]:
        """Get comprehensive aggregation report"""
        try:
            return {
                'aggregation_metrics': self.metrics.__dict__,
                'aggregation_history': self.aggregation_history,
                'current_config': self.config.__dict__,
                'weight_cache': self.weight_cache
            }
            
        except Exception as e:
            print(f"❌ Aggregation report generation failed: {e}")
            return {'error': str(e)}
    
    async def reset_metrics(self):
        """Reset aggregation metrics"""
        try:
            self.metrics = AggregationMetrics()
            self.weight_cache.clear()
            print("🔄 Aggregation metrics reset")
            
        except Exception as e:
            print(f"❌ Metrics reset failed: {e}")


