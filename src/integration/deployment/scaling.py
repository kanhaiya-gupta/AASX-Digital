"""
Auto-Scaling Support

This module provides comprehensive auto-scaling capabilities for the AAS Data
Modeling Engine integration layer, including scaling policies, resource
management, and performance optimization.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import statistics


logger = logging.getLogger(__name__)


class ScalingPolicy(str, Enum):
    """Scaling policy types."""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    CUSTOM_METRIC = "custom_metric"
    SCHEDULE_BASED = "schedule_based"
    HYBRID = "hybrid"


class ScalingAction(str, Enum):
    """Scaling action types."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_ACTION = "no_action"


class ResourceType(str, Enum):
    """Resource type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class ScalingThreshold:
    """Threshold configuration for scaling decisions."""
    
    resource_type: ResourceType
    upper_threshold: float  # Percentage (0-100)
    lower_threshold: float  # Percentage (0-100)
    cooldown_period: int = 300  # Seconds
    stabilization_period: int = 60  # Seconds


@dataclass
class ScalingPolicyConfig:
    """Configuration for a scaling policy."""
    
    name: str
    policy_type: ScalingPolicy
    thresholds: List[ScalingThreshold]
    min_replicas: int = 1
    max_replicas: int = 10
    target_replicas: int = 3
    scale_up_cooldown: int = 300  # Seconds
    scale_down_cooldown: int = 300  # Seconds
    scale_up_factor: float = 1.5
    scale_down_factor: float = 0.7
    enabled: bool = True
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceMetrics:
    """Resource usage metrics."""
    
    timestamp: datetime
    resource_type: ResourceType
    current_usage: float
    current_percentage: float
    average_usage: float
    peak_usage: float
    trend: str  # "increasing", "decreasing", "stable"


@dataclass
class ScalingDecision:
    """Result of a scaling decision."""
    
    action: ScalingAction
    current_replicas: int
    target_replicas: int
    reason: str
    metrics: Dict[str, Any]
    timestamp: datetime
    confidence: float  # 0.0 to 1.0


@dataclass
class ScalingHistory:
    """History of scaling actions."""
    
    timestamp: datetime
    action: ScalingAction
    from_replicas: int
    to_replicas: int
    reason: str
    metrics: Dict[str, Any]
    duration: float  # Seconds
    success: bool


class AutoScalingManager:
    """
    Auto-scaling management service.
    
    Provides comprehensive auto-scaling capabilities including:
    - Multi-metric scaling policies
    - Resource monitoring and analysis
    - Intelligent scaling decisions
    - Performance optimization
    - Scaling history and analytics
    """
    
    def __init__(self):
        """Initialize the auto-scaling manager."""
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.resource_metrics: Dict[str, List[ResourceMetrics]] = {}
        self.scaling_history: List[ScalingHistory] = []
        self.last_scaling_action: Dict[str, datetime] = {}
        self.metric_collectors: Dict[str, Callable] = {}
        self.scaling_callbacks: Dict[str, Callable] = {}
        
        # Initialize default policies
        self._setup_default_policies()
        
        logger.info("Auto-Scaling Manager initialized")
    
    def _setup_default_policies(self) -> None:
        """Setup default scaling policies."""
        # CPU-based scaling policy
        cpu_policy = ScalingPolicyConfig(
            name="cpu_scaling",
            policy_type=ScalingPolicy.CPU_BASED,
            thresholds=[
                ScalingThreshold(
                    resource_type=ResourceType.CPU,
                    upper_threshold=80.0,
                    lower_threshold=20.0,
                    cooldown_period=300,
                    stabilization_period=60
                )
            ],
            min_replicas=1,
            max_replicas=10,
            target_replicas=3,
            scale_up_cooldown=300,
            scale_down_cooldown=300
        )
        
        # Memory-based scaling policy
        memory_policy = ScalingPolicyConfig(
            name="memory_scaling",
            policy_type=ScalingPolicy.MEMORY_BASED,
            thresholds=[
                ScalingThreshold(
                    resource_type=ResourceType.MEMORY,
                    upper_threshold=85.0,
                    lower_threshold=30.0,
                    cooldown_period=300,
                    stabilization_period=60
                )
            ],
            min_replicas=1,
            max_replicas=10,
            target_replicas=3,
            scale_up_cooldown=300,
            scale_down_cooldown=300
        )
        
        # Hybrid scaling policy
        hybrid_policy = ScalingPolicyConfig(
            name="hybrid_scaling",
            policy_type=ScalingPolicy.HYBRID,
            thresholds=[
                ScalingThreshold(
                    resource_type=ResourceType.CPU,
                    upper_threshold=75.0,
                    lower_threshold=25.0,
                    cooldown_period=300,
                    stabilization_period=60
                ),
                ScalingThreshold(
                    resource_type=ResourceType.MEMORY,
                    upper_threshold=80.0,
                    lower_threshold=35.0,
                    cooldown_period=300,
                    stabilization_period=60
                )
            ],
            min_replicas=1,
            max_replicas=15,
            target_replicas=3,
            scale_up_cooldown=300,
            scale_down_cooldown=300
        )
        
        self.add_scaling_policy(cpu_policy)
        self.add_scaling_policy(memory_policy)
        self.add_scaling_policy(hybrid_policy)
    
    def add_scaling_policy(self, policy: ScalingPolicyConfig) -> None:
        """Add a scaling policy."""
        self.scaling_policies[policy.name] = policy
        logger.info(f"Scaling policy added: {policy.name}")
    
    def remove_scaling_policy(self, name: str) -> bool:
        """Remove a scaling policy."""
        if name in self.scaling_policies:
            del self.scaling_policies[name]
            logger.info(f"Scaling policy removed: {name}")
            return True
        return False
    
    def get_scaling_policy(self, name: str) -> Optional[ScalingPolicyConfig]:
        """Get a scaling policy by name."""
        return self.scaling_policies.get(name)
    
    def list_scaling_policy_configs(self) -> List[ScalingPolicyConfig]:
        """List all scaling policies."""
        return list(self.scaling_policies.values())
    
    def add_metric_collector(self, resource_type: ResourceType, collector: Callable) -> None:
        """Add a metric collector for a resource type."""
        self.metric_collectors[resource_type.value] = collector
        logger.info(f"Metric collector added for: {resource_type.value}")
    
    def add_scaling_callback(self, policy_name: str, callback: Callable) -> None:
        """Add a scaling callback for a policy."""
        self.scaling_callbacks[policy_name] = callback
        logger.info(f"Scaling callback added for policy: {policy_name}")
    
    async def collect_metrics(self, resource_type: ResourceType) -> Optional[ResourceMetrics]:
        """Collect metrics for a specific resource type."""
        try:
            collector = self.metric_collectors.get(resource_type.value)
            if collector:
                metrics_data = await collector()
                
                # Calculate additional metrics
                current_usage = metrics_data.get("current_usage", 0.0)
                current_percentage = metrics_data.get("current_percentage", 0.0)
                
                # Get historical metrics for trend analysis
                historical_metrics = self.resource_metrics.get(resource_type.value, [])
                
                if historical_metrics:
                    # Calculate average and peak usage
                    recent_metrics = historical_metrics[-10:]  # Last 10 data points
                    usage_values = [m.current_usage for m in recent_metrics]
                    average_usage = statistics.mean(usage_values)
                    peak_usage = max(usage_values)
                    
                    # Determine trend
                    if len(usage_values) >= 2:
                        trend = self._calculate_trend(usage_values)
                    else:
                        trend = "stable"
                else:
                    average_usage = current_usage
                    peak_usage = current_usage
                    trend = "stable"
                
                # Create metrics object
                metrics = ResourceMetrics(
                    timestamp=datetime.now(),
                    resource_type=resource_type,
                    current_usage=current_usage,
                    current_percentage=current_percentage,
                    average_usage=average_usage,
                    peak_usage=peak_usage,
                    trend=trend
                )
                
                # Store metrics
                if resource_type.value not in self.resource_metrics:
                    self.resource_metrics[resource_type.value] = []
                
                self.resource_metrics[resource_type.value].append(metrics)
                
                # Keep only last 1000 metrics per resource type
                if len(self.resource_metrics[resource_type.value]) > 1000:
                    self.resource_metrics[resource_type.value] = self.resource_metrics[resource_type.value][-1000:]
                
                return metrics
            else:
                logger.warning(f"No metric collector found for: {resource_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"Error collecting metrics for {resource_type.value}: {str(e)}")
            return None
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a list of values."""
        if len(values) < 2:
            return "stable"
        
        # Calculate linear regression slope
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * val for i, val in enumerate(values))
        x2_sum = sum(i * i for i in range(n))
        
        try:
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
            
            if slope > 0.01:  # Positive slope threshold
                return "increasing"
            elif slope < -0.01:  # Negative slope threshold
                return "decreasing"
            else:
                return "stable"
        except ZeroDivisionError:
            return "stable"
    
    async def evaluate_scaling_policy(self, policy_name: str, current_replicas: int) -> ScalingDecision:
        """Evaluate a scaling policy and make a decision."""
        try:
            policy = self.scaling_policies.get(policy_name)
            if not policy or not policy.enabled:
                return ScalingDecision(
                    action=ScalingAction.NO_ACTION,
                    current_replicas=current_replicas,
                    target_replicas=current_replicas,
                    reason="Policy not found or disabled",
                    metrics={},
                    timestamp=datetime.now(),
                    confidence=0.0
                )
            
            # Check cooldown periods
            last_action = self.last_scaling_action.get(policy_name)
            if last_action:
                time_since_last_action = (datetime.now() - last_action).total_seconds()
                
                if policy.policy_type == ScalingPolicy.CPU_BASED or policy.policy_type == ScalingPolicy.MEMORY_BASED:
                    if time_since_last_action < policy.scale_up_cooldown:
                        return ScalingDecision(
                            action=ScalingAction.NO_ACTION,
                            current_replicas=current_replicas,
                            target_replicas=current_replicas,
                            reason="Scale-up cooldown period active",
                            metrics={},
                            timestamp=datetime.now(),
                            confidence=0.0
                        )
                
                if time_since_last_action < policy.scale_down_cooldown:
                    return ScalingDecision(
                        action=ScalingAction.NO_ACTION,
                        current_replicas=current_replicas,
                        target_replicas=current_replicas,
                        reason="Scale-down cooldown period active",
                        metrics={},
                        timestamp=datetime.now(),
                        confidence=0.0
                    )
            
            # Collect current metrics
            current_metrics = {}
            scaling_reasons = []
            confidence_factors = []
            
            for threshold in policy.thresholds:
                metrics = await self.collect_metrics(threshold.resource_type)
                if metrics:
                    current_metrics[threshold.resource_type.value] = metrics
                    
                    # Check if scaling is needed
                    if metrics.current_percentage > threshold.upper_threshold:
                        scaling_reasons.append(f"{threshold.resource_type.value} usage high: {metrics.current_percentage:.1f}%")
                        confidence_factors.append(0.9)  # High confidence for scale-up
                    elif metrics.current_percentage < threshold.lower_threshold:
                        scaling_reasons.append(f"{threshold.resource_type.value} usage low: {metrics.current_percentage:.1f}%")
                        confidence_factors.append(0.7)  # Medium confidence for scale-down
                    else:
                        confidence_factors.append(0.5)  # Neutral confidence
            
            # Make scaling decision
            if not scaling_reasons:
                return ScalingDecision(
                    action=ScalingAction.NO_ACTION,
                    current_replicas=current_replicas,
                    target_replicas=current_replicas,
                    reason="All metrics within thresholds",
                    metrics=current_metrics,
                    timestamp=datetime.now(),
                    confidence=0.5
                )
            
            # Determine scaling action
            action = ScalingAction.NO_ACTION
            target_replicas = current_replicas
            
            # Check if we need to scale up
            scale_up_needed = any(
                metrics.current_percentage > threshold.upper_threshold
                for threshold in policy.thresholds
                for resource_type, metrics in current_metrics.items()
                if resource_type == threshold.resource_type.value
            )
            
            # Check if we need to scale down
            scale_down_needed = all(
                metrics.current_percentage < threshold.lower_threshold
                for threshold in policy.thresholds
                for resource_type, metrics in current_metrics.items()
                if resource_type == threshold.resource_type.value
            )
            
            if scale_up_needed and current_replicas < policy.max_replicas:
                action = ScalingAction.SCALE_UP
                target_replicas = min(
                    int(current_replicas * policy.scale_up_factor),
                    policy.max_replicas
                )
                scaling_reasons.append(f"Scaling up from {current_replicas} to {target_replicas} replicas")
            
            elif scale_down_needed and current_replicas > policy.min_replicas:
                action = ScalingAction.SCALE_DOWN
                target_replicas = max(
                    int(current_replicas * policy.scale_down_factor),
                    policy.min_replicas
                )
                scaling_reasons.append(f"Scaling down from {current_replicas} to {target_replicas} replicas")
            
            # Calculate overall confidence
            overall_confidence = statistics.mean(confidence_factors) if confidence_factors else 0.5
            
            # Create scaling decision
            decision = ScalingDecision(
                action=action,
                current_replicas=current_replicas,
                target_replicas=target_replicas,
                reason="; ".join(scaling_reasons),
                metrics=current_metrics,
                timestamp=datetime.now(),
                confidence=overall_confidence
            )
            
            # Execute scaling if needed
            if action != ScalingAction.NO_ACTION:
                await self._execute_scaling(policy_name, decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error evaluating scaling policy {policy_name}: {str(e)}")
            return ScalingDecision(
                action=ScalingAction.NO_ACTION,
                current_replicas=current_replicas,
                target_replicas=current_replicas,
                reason=f"Error evaluating policy: {str(e)}",
                metrics={},
                timestamp=datetime.now(),
                confidence=0.0
            )
    
    async def _execute_scaling(self, policy_name: str, decision: ScalingDecision) -> bool:
        """Execute a scaling decision."""
        try:
            logger.info(f"Executing scaling action: {decision.action} - {decision.reason}")
            
            # Call scaling callback if available
            callback = self.scaling_callbacks.get(policy_name)
            if callback:
                start_time = time.time()
                success = await callback(decision)
                duration = time.time() - start_time
                
                # Record scaling history
                history_entry = ScalingHistory(
                    timestamp=decision.timestamp,
                    action=decision.action,
                    from_replicas=decision.current_replicas,
                    to_replicas=decision.target_replicas,
                    reason=decision.reason,
                    metrics=decision.metrics,
                    duration=duration,
                    success=success
                )
                
                self.scaling_history.append(history_entry)
                
                # Keep only last 1000 history entries
                if len(self.scaling_history) > 1000:
                    self.scaling_history = self.scaling_history[-1000:]
                
                # Update last scaling action timestamp
                self.last_scaling_action[policy_name] = datetime.now()
                
                if success:
                    logger.info(f"Scaling action executed successfully: {decision.action}")
                else:
                    logger.error(f"Scaling action failed: {decision.action}")
                
                return success
            else:
                logger.warning(f"No scaling callback found for policy: {policy_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing scaling action: {str(e)}")
            return False
    
    async def auto_scale_all_policies(self, current_replicas: int) -> List[ScalingDecision]:
        """Evaluate all enabled scaling policies."""
        decisions = []
        
        for policy_name in self.scaling_policies:
            policy = self.scaling_policies[policy_name]
            if policy.enabled:
                decision = await self.evaluate_scaling_policy(policy_name, current_replicas)
                decisions.append(decision)
        
        return decisions
    
    def get_scaling_history(self, 
                          policy_name: Optional[str] = None,
                          action: Optional[ScalingAction] = None,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[ScalingHistory]:
        """Get scaling history with optional filters."""
        filtered_history = self.scaling_history
        
        if policy_name:
            # Filter by policy name (would need to add policy_name to ScalingHistory)
            pass
        
        if action:
            filtered_history = [h for h in filtered_history if h.action == action]
        
        if start_time:
            filtered_history = [h for h in filtered_history if h.timestamp >= start_time]
        
        if end_time:
            filtered_history = [h for h in filtered_history if h.timestamp <= end_time]
        
        return filtered_history
    
    def get_scaling_analytics(self) -> Dict[str, Any]:
        """Get analytics about scaling performance."""
        if not self.scaling_history:
            return {}
        
        total_actions = len(self.scaling_history)
        successful_actions = sum(1 for h in self.scaling_history if h.success)
        success_rate = successful_actions / total_actions if total_actions > 0 else 0
        
        # Calculate average scaling duration
        durations = [h.duration for h in self.scaling_history if h.success]
        avg_duration = statistics.mean(durations) if durations else 0
        
        # Count actions by type
        action_counts = {}
        for action in ScalingAction:
            action_counts[action.value] = sum(1 for h in self.scaling_history if h.action == action)
        
        # Calculate scaling frequency
        if len(self.scaling_history) >= 2:
            time_span = (self.scaling_history[-1].timestamp - self.scaling_history[0].timestamp).total_seconds()
            scaling_frequency = total_actions / (time_span / 3600) if time_span > 0 else 0  # Actions per hour
        else:
            scaling_frequency = 0
        
        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": success_rate,
            "average_duration": avg_duration,
            "action_counts": action_counts,
            "scaling_frequency": scaling_frequency,
            "last_action": self.scaling_history[-1].timestamp if self.scaling_history else None
        }
    
    def get_resource_metrics_summary(self, resource_type: ResourceType, hours: int = 24) -> Dict[str, Any]:
        """Get summary of resource metrics for a specific time period."""
        if resource_type.value not in self.resource_metrics:
            return {}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.resource_metrics[resource_type.value]
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        usage_values = [m.current_percentage for m in recent_metrics]
        usage_values_absolute = [m.current_usage for m in recent_metrics]
        
        return {
            "resource_type": resource_type.value,
            "time_period_hours": hours,
            "data_points": len(recent_metrics),
            "current_usage": recent_metrics[-1].current_percentage if recent_metrics else 0,
            "average_usage": statistics.mean(usage_values),
            "peak_usage": max(usage_values),
            "min_usage": min(usage_values),
            "usage_trend": recent_metrics[-1].trend if recent_metrics else "stable",
            "absolute_usage": {
                "current": recent_metrics[-1].current_usage if recent_metrics else 0,
                "average": statistics.mean(usage_values_absolute),
                "peak": max(usage_values_absolute),
                "min": min(usage_values_absolute)
            }
        }
    
    async def optimize_scaling_policies(self) -> Dict[str, Any]:
        """Optimize scaling policies based on historical data."""
        try:
            analytics = self.get_scaling_analytics()
            optimizations = {}
            
            for policy_name, policy in self.scaling_policies.items():
                policy_optimizations = {}
                
                # Analyze scaling frequency
                if analytics.get("scaling_frequency", 0) > 10:  # More than 10 actions per hour
                    policy_optimizations["high_frequency"] = {
                        "issue": "High scaling frequency detected",
                        "recommendation": "Increase cooldown periods or adjust thresholds",
                        "suggested_changes": {
                            "scale_up_cooldown": min(policy.scale_up_cooldown * 1.5, 900),
                            "scale_down_cooldown": min(policy.scale_down_cooldown * 1.5, 900)
                        }
                    }
                
                # Analyze success rate
                if analytics.get("success_rate", 1.0) < 0.8:  # Less than 80% success
                    policy_optimizations["low_success_rate"] = {
                        "issue": "Low scaling success rate detected",
                        "recommendation": "Review scaling thresholds and cooldown periods",
                        "suggested_changes": {
                            "upper_threshold": min(policy.thresholds[0].upper_threshold * 1.1, 95),
                            "lower_threshold": max(policy.thresholds[0].lower_threshold * 0.9, 5)
                        }
                    }
                
                # Analyze scaling factors
                if policy.scale_up_factor > 2.0:
                    policy_optimizations["aggressive_scale_up"] = {
                        "issue": "Aggressive scale-up factor detected",
                        "recommendation": "Reduce scale-up factor for more gradual scaling",
                        "suggested_changes": {
                            "scale_up_factor": max(policy.scale_up_factor * 0.8, 1.2)
                        }
                    }
                
                if policy.scale_down_factor < 0.5:
                    policy_optimizations["aggressive_scale_down"] = {
                        "issue": "Aggressive scale-down factor detected",
                        "recommendation": "Increase scale-down factor for more gradual scaling",
                        "suggested_changes": {
                            "scale_down_factor": min(policy.scale_down_factor * 1.2, 0.8)
                        }
                    }
                
                if policy_optimizations:
                    optimizations[policy_name] = policy_optimizations
            
            return {
                "optimizations_found": len(optimizations),
                "policy_optimizations": optimizations,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing scaling policies: {str(e)}")
            return {"error": str(e)}
    
    async def start_monitoring(self, interval_seconds: int = 60) -> None:
        """Start continuous monitoring and auto-scaling."""
        logger.info(f"Starting auto-scaling monitoring with {interval_seconds}s interval")
        
        try:
            while True:
                # Collect metrics for all resource types
                for resource_type in ResourceType:
                    await self.collect_metrics(resource_type)
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
        except asyncio.CancelledError:
            logger.info("Auto-scaling monitoring stopped")
        except Exception as e:
            logger.error(f"Error in auto-scaling monitoring: {str(e)}")
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        logger.info("Stopping auto-scaling monitoring")
        # This would be called from outside to cancel the monitoring task
