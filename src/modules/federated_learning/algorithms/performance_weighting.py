"""
Performance Weighting Algorithm
==============================

Implementation of performance-based weighting for federated learning.
Provides intelligent participant selection and dynamic weighting strategies.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class PerformanceWeightingConfig:
    """Configuration for Performance Weighting algorithm"""
    # Weighting strategies
    weighting_strategy: str = "adaptive"  # adaptive, performance, quality, hybrid
    performance_metrics: List[str] = None  # accuracy, loss, convergence, stability
    
    # Threshold parameters
    min_performance_threshold: float = 0.5
    max_performance_threshold: float = 0.95
    performance_decay_factor: float = 0.1
    
    # Selection parameters
    participant_selection_method: str = "top_k"  # top_k, threshold, adaptive
    max_participants: int = 50
    min_participants: int = 5
    selection_ratio: float = 0.8  # Select top 80%
    
    # Performance tracking
    history_window_size: int = 10
    performance_memory_decay: float = 0.9
    enable_dynamic_adjustment: bool = True


@dataclass
class PerformanceWeightingMetrics:
    """Metrics for Performance Weighting algorithm performance"""
    # Weighting metrics
    total_weights_calculated: int = 0
    avg_weight_value: float = 0.0
    weight_distribution: Dict[str, float] = None
    
    # Performance metrics
    total_participants_evaluated: int = 0
    performance_improvement: float = 0.0
    selection_efficiency: float = 0.0
    
    # Quality metrics
    model_quality_score: float = 0.0
    convergence_speed: float = 0.0
    stability_improvement: float = 0.0
    
    # Resource metrics
    total_rounds: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0
    avg_processing_time: float = 0.0


class PerformanceWeightingAlgorithm:
    """Performance Weighting algorithm implementation"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[PerformanceWeightingConfig] = None
    ):
        """Initialize Performance Weighting algorithm"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or PerformanceWeightingConfig()
        
        # Initialize performance metrics if not provided
        if self.config.performance_metrics is None:
            self.config.performance_metrics = ['accuracy', 'loss', 'convergence', 'stability']
        
        # Algorithm state
        self.current_round = 0
        self.is_running = False
        self.participant_performance_history: Dict[str, List[float]] = {}
        self.weight_history: List[Dict[str, float]] = []
        
        # Metrics tracking
        self.metrics = PerformanceWeightingMetrics()
        self.metrics.weight_distribution = {
            'high_performance': 0.0,
            'medium_performance': 0.0,
            'low_performance': 0.0
        }
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.round_times: List[float] = []
    
    async def start_performance_weighting(self, federation_id: str) -> Dict[str, Any]:
        """Start performance weighting system"""
        try:
            self.start_time = datetime.now()
            self.is_running = True
            self.current_round = 0
            
            print(f"⚡ Starting Performance Weighting system: {federation_id}")
            
            # Initialize performance tracking
            await self._initialize_performance_tracking(federation_id)
            
            return {
                'status': 'started',
                'federation_id': federation_id,
                'start_time': self.start_time.isoformat(),
                'weighting_strategy': self.config.weighting_strategy,
                'performance_metrics': self.config.performance_metrics,
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to start performance weighting: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def calculate_performance_weights(
        self,
        federation_id: str,
        participant_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate performance-based weights for participants"""
        try:
            round_start_time = datetime.now()
            self.current_round += 1
            
            print(f"⚡ Performance Weighting Round {self.current_round}: Evaluating {len(participant_updates)} participants")
            
            # Validate inputs
            if not participant_updates:
                raise ValueError("No participant updates provided")
            
            # Evaluate participant performance
            performance_scores = await self._evaluate_participant_performance(participant_updates)
            
            # Calculate weights based on strategy
            weights = await self._calculate_weights_by_strategy(performance_scores)
            
            # Select participants based on weights
            selected_participants = await self._select_participants(weights)
            
            # Update performance history
            await self._update_performance_history(performance_scores)
            
            # Update metrics
            round_time = (datetime.now() - round_start_time).total_seconds()
            self.round_times.append(round_time)
            self.metrics.total_rounds = self.current_round
            self.metrics.successful_rounds += 1
            self.metrics.avg_processing_time = np.mean(self.round_times)
            
            print(f"✅ Performance Weighting Round {self.current_round} completed in {round_time:.2f}s")
            
            return {
                'status': 'success',
                'round': self.current_round,
                'weights': weights,
                'selected_participants': selected_participants,
                'performance_scores': performance_scores,
                'round_time': round_time
            }
            
        except Exception as e:
            print(f"❌ Performance weighting calculation failed: {e}")
            self.metrics.failed_rounds += 1
            return {'status': 'failed', 'error': str(e)}
    
    async def _evaluate_participant_performance(
        self,
        participant_updates: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Evaluate performance of each participant"""
        try:
            performance_scores = {}
            
            for update in participant_updates:
                participant_id = update.get('participant_id', 'unknown')
                
                try:
                    # Calculate performance score based on multiple metrics
                    score = await self._calculate_performance_score(update)
                    performance_scores[participant_id] = score
                    
                except Exception as e:
                    print(f"⚠️  Failed to evaluate participant {participant_id}: {e}")
                    performance_scores[participant_id] = 0.0
            
            # Update metrics
            self.metrics.total_participants_evaluated += len(performance_scores)
            
            return performance_scores
            
        except Exception as e:
            print(f"❌ Participant performance evaluation failed: {e}")
            raise
    
    async def _calculate_performance_score(self, update: Dict[str, Any]) -> float:
        """Calculate performance score for a single participant"""
        try:
            score = 0.0
            total_weight = 0.0
            
            # Evaluate accuracy
            if 'accuracy' in update:
                accuracy_score = min(update['accuracy'], 1.0)  # Normalize to [0, 1]
                score += accuracy_score * 0.4  # 40% weight
                total_weight += 0.4
            
            # Evaluate loss
            if 'loss' in update:
                # Lower loss is better, so invert and normalize
                loss_score = max(0, 1.0 - update['loss'])
                score += loss_score * 0.3  # 30% weight
                total_weight += 0.3
            
            # Evaluate convergence
            if 'convergence_rate' in update:
                convergence_score = min(update['convergence_rate'], 1.0)
                score += convergence_score * 0.2  # 20% weight
                total_weight += 0.2
            
            # Evaluate stability
            if 'stability_score' in update:
                stability_score = min(update['stability_score'], 1.0)
                score += stability_score * 0.1  # 10% weight
                total_weight += 0.1
            
            # Normalize score if weights were applied
            if total_weight > 0:
                score = score / total_weight
            else:
                # Default score if no metrics available
                score = 0.5
            
            # Apply performance thresholds
            score = max(self.config.min_performance_threshold, 
                       min(self.config.max_performance_threshold, score))
            
            return score
            
        except Exception as e:
            print(f"⚠️  Performance score calculation failed: {e}")
            return 0.5  # Default score
    
    async def _calculate_weights_by_strategy(
        self,
        performance_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate weights based on the configured strategy"""
        try:
            if self.config.weighting_strategy == "adaptive":
                weights = await self._calculate_adaptive_weights(performance_scores)
            elif self.config.weighting_strategy == "performance":
                weights = await self._calculate_performance_weights(performance_scores)
            elif self.config.weighting_strategy == "quality":
                weights = await self._calculate_quality_weights(performance_scores)
            elif self.config.weighting_strategy == "hybrid":
                weights = await self._calculate_hybrid_weights(performance_scores)
            else:
                weights = await self._calculate_adaptive_weights(performance_scores)
            
            # Normalize weights
            weights = await self._normalize_weights(weights)
            
            # Update metrics
            self.metrics.total_weights_calculated += len(weights)
            self.metrics.avg_weight_value = np.mean(list(weights.values()))
            
            return weights
            
        except Exception as e:
            print(f"❌ Weight calculation failed: {e}")
            raise
    
    async def _calculate_adaptive_weights(
        self,
        performance_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate adaptive weights based on performance history"""
        try:
            weights = {}
            
            for participant_id, current_score in performance_scores.items():
                # Get historical performance
                historical_scores = self.participant_performance_history.get(participant_id, [])
                
                if historical_scores:
                    # Calculate trend (improvement or decline)
                    if len(historical_scores) >= 2:
                        trend = (current_score - historical_scores[-2]) / max(historical_scores[-2], 0.001)
                        trend_factor = 1.0 + (trend * self.config.performance_decay_factor)
                    else:
                        trend_factor = 1.0
                    
                    # Combine current performance with trend
                    adaptive_score = current_score * trend_factor
                else:
                    adaptive_score = current_score
                
                weights[participant_id] = adaptive_score
            
            return weights
            
        except Exception as e:
            print(f"⚠️  Adaptive weight calculation failed: {e}")
            return performance_scores
    
    async def _calculate_performance_weights(
        self,
        performance_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate weights based purely on performance scores"""
        try:
            # Simple performance-based weighting
            weights = performance_scores.copy()
            
            # Apply exponential scaling for better differentiation
            for participant_id in weights:
                weights[participant_id] = np.exp(weights[participant_id])
            
            return weights
            
        except Exception as e:
            print(f"⚠️  Performance weight calculation failed: {e}")
            return performance_scores
    
    async def _calculate_quality_weights(
        self,
        performance_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate weights based on quality metrics"""
        try:
            weights = {}
            
            for participant_id, score in performance_scores.items():
                # Quality-based weighting with emphasis on consistency
                if participant_id in self.participant_performance_history:
                    historical_scores = self.participant_performance_history[participant_id]
                    
                    if len(historical_scores) >= 3:
                        # Calculate consistency (lower variance = higher quality)
                        variance = np.var(historical_scores)
                        consistency_factor = 1.0 / (1.0 + variance)
                        
                        # Combine current performance with consistency
                        quality_score = score * (0.7 + 0.3 * consistency_factor)
                    else:
                        quality_score = score
                else:
                    quality_score = score
                
                weights[participant_id] = quality_score
            
            return weights
            
        except Exception as e:
            print(f"⚠️  Quality weight calculation failed: {e}")
            return performance_scores
    
    async def _calculate_hybrid_weights(
        self,
        performance_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate hybrid weights combining multiple strategies"""
        try:
            # Get weights from different strategies
            adaptive_weights = await self._calculate_adaptive_weights(performance_scores)
            performance_weights = await self._calculate_performance_weights(performance_scores)
            quality_weights = await self._calculate_quality_weights(performance_scores)
            
            # Combine weights with configurable ratios
            hybrid_weights = {}
            
            for participant_id in performance_scores:
                adaptive_w = adaptive_weights.get(participant_id, 0.0)
                perf_w = performance_weights.get(participant_id, 0.0)
                quality_w = quality_weights.get(participant_id, 0.0)
                
                # Weighted combination (40% adaptive, 35% performance, 25% quality)
                hybrid_score = (0.4 * adaptive_w + 0.35 * perf_w + 0.25 * quality_w)
                hybrid_weights[participant_id] = hybrid_score
            
            return hybrid_weights
            
        except Exception as e:
            print(f"⚠️  Hybrid weight calculation failed: {e}")
            return performance_scores
    
    async def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to sum to 1.0"""
        try:
            total_weight = sum(weights.values())
            
            if total_weight > 0:
                normalized_weights = {
                    participant_id: weight / total_weight
                    for participant_id, weight in weights.items()
                }
            else:
                # Equal weights if total is zero
                num_participants = len(weights)
                normalized_weights = {
                    participant_id: 1.0 / num_participants
                    for participant_id in weights.keys()
                }
            
            return normalized_weights
            
        except Exception as e:
            print(f"⚠️  Weight normalization failed: {e}")
            return weights
    
    async def _select_participants(self, weights: Dict[str, float]) -> List[str]:
        """Select participants based on calculated weights"""
        try:
            if self.config.participant_selection_method == "top_k":
                # Select top k participants
                k = int(len(weights) * self.config.selection_ratio)
                k = max(self.config.min_participants, min(k, self.config.max_participants))
                
                # Sort by weight and select top k
                sorted_participants = sorted(weights.items(), key=lambda x: x[1], reverse=True)
                selected = [participant_id for participant_id, _ in sorted_participants[:k]]
                
            elif self.config.participant_selection_method == "threshold":
                # Select participants above threshold
                threshold = np.mean(list(weights.values()))
                selected = [
                    participant_id for participant_id, weight in weights.items()
                    if weight >= threshold
                ]
                
                # Ensure minimum and maximum constraints
                if len(selected) < self.config.min_participants:
                    # Add more participants to meet minimum
                    remaining = [p for p in weights.keys() if p not in selected]
                    selected.extend(remaining[:self.config.min_participants - len(selected)])
                elif len(selected) > self.config.max_participants:
                    # Limit to maximum
                    selected = selected[:self.config.max_participants]
                    
            elif self.config.participant_selection_method == "adaptive":
                # Adaptive selection based on performance distribution
                selected = await self._adaptive_participant_selection(weights)
                
            else:
                # Default to top_k
                selected = await self._select_participants(weights)
            
            return selected
            
        except Exception as e:
            print(f"⚠️  Participant selection failed: {e}")
            # Return all participants as fallback
            return list(weights.keys())
    
    async def _adaptive_participant_selection(self, weights: Dict[str, float]) -> List[str]:
        """Adaptive participant selection based on performance distribution"""
        try:
            # Calculate performance distribution
            weight_values = list(weights.values())
            mean_weight = np.mean(weight_values)
            std_weight = np.std(weight_values)
            
            # Select participants based on distribution
            selected = []
            
            for participant_id, weight in weights.items():
                # Include high performers
                if weight >= mean_weight + std_weight:
                    selected.append(participant_id)
                
                # Include some medium performers for diversity
                elif weight >= mean_weight and len(selected) < len(weights) * 0.6:
                    selected.append(participant_id)
                
                # Include some low performers for robustness
                elif weight < mean_weight and len(selected) < len(weights) * 0.8:
                    selected.append(participant_id)
            
            # Ensure constraints
            if len(selected) < self.config.min_participants:
                remaining = [p for p in weights.keys() if p not in selected]
                selected.extend(remaining[:self.config.min_participants - len(selected)])
            elif len(selected) > self.config.max_participants:
                selected = selected[:self.config.max_participants]
            
            return selected
            
        except Exception as e:
            print(f"⚠️  Adaptive participant selection failed: {e}")
            return list(weights.keys())
    
    async def _update_performance_history(self, performance_scores: Dict[str, float]):
        """Update performance history for participants"""
        try:
            for participant_id, score in performance_scores.items():
                if participant_id not in self.participant_performance_history:
                    self.participant_performance_history[participant_id] = []
                
                # Add current score
                self.participant_performance_history[participant_id].append(score)
                
                # Limit history size
                if len(self.participant_performance_history[participant_id]) > self.config.history_window_size:
                    self.participant_performance_history[participant_id] = \
                        self.participant_performance_history[participant_id][-self.config.history_window_size:]
            
            # Update weight distribution metrics
            await self._update_weight_distribution_metrics(performance_scores)
            
        except Exception as e:
            print(f"⚠️  Performance history update failed: {e}")
    
    async def _update_weight_distribution_metrics(self, performance_scores: Dict[str, float]):
        """Update weight distribution metrics"""
        try:
            scores = list(performance_scores.values())
            
            if scores:
                # Categorize performance levels
                high_performance = sum(1 for s in scores if s >= 0.8)
                medium_performance = sum(1 for s in scores if 0.5 <= s < 0.8)
                low_performance = sum(1 for s in scores if s < 0.5)
                
                total = len(scores)
                
                self.metrics.weight_distribution['high_performance'] = high_performance / total
                self.metrics.weight_distribution['medium_performance'] = medium_performance / total
                self.metrics.weight_distribution['low_performance'] = low_performance / total
            
        except Exception as e:
            print(f"⚠️  Weight distribution metrics update failed: {e}")
    
    async def _initialize_performance_tracking(self, federation_id: str):
        """Initialize performance tracking system"""
        try:
            print(f"⚡ Initializing performance tracking for: {federation_id}")
            
            # Reset performance history
            self.participant_performance_history.clear()
            self.weight_history.clear()
            
        except Exception as e:
            print(f"⚠️  Performance tracking initialization failed: {e}")
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance weighting report"""
        try:
            return {
                'performance_metrics': self.metrics.__dict__,
                'participant_history': self.participant_performance_history,
                'weight_history': self.weight_history,
                'current_config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Performance report generation failed: {e}")
            return {'error': str(e)}
    
    async def stop_performance_weighting(self) -> Dict[str, Any]:
        """Stop performance weighting system"""
        try:
            self.is_running = False
            
            # Generate final performance report
            performance_report = await self.get_performance_report()
            
            print(f"🛑 Performance Weighting system stopped after {self.current_round} rounds")
            
            return {
                'status': 'stopped',
                'total_rounds': self.current_round,
                'final_performance_report': performance_report
            }
            
        except Exception as e:
            print(f"❌ Failed to stop performance weighting: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'PerformanceWeighting',
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
        self.participant_performance_history.clear()
        self.weight_history.clear()
        self.round_times.clear()
        self.metrics = PerformanceWeightingMetrics()
        self.metrics.weight_distribution = {
            'high_performance': 0.0,
            'medium_performance': 0.0,
            'low_performance': 0.0
        }
        self.start_time = None
        
        print("🔄 Performance Weighting algorithm reset") 