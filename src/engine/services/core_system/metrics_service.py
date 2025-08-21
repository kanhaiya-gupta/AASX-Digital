"""
Metrics Service - Core System Service
====================================

Provides centralized metrics collection, aggregation, and analysis for the entire system.
This service extends the base service infrastructure with comprehensive metrics capabilities.

Features:
- Performance metrics collection
- Business metrics aggregation
- Metrics storage and retrieval
- Metrics analysis and reporting
- Real-time metrics streaming
- Historical metrics analysis
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics supported."""
    COUNTER = "counter"           # Incremental values (e.g., request count)
    GAUGE = "gauge"               # Current values (e.g., memory usage)
    HISTOGRAM = "histogram"       # Distribution of values (e.g., response times)
    SUMMARY = "summary"           # Statistical summaries (e.g., percentiles)


@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    labels: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricValue:
    """A single metric value."""
    metric_name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """Aggregated metric data."""
    metric_name: str
    count: int
    sum: float
    min: float
    max: float
    mean: float
    median: float
    std_dev: float
    percentiles: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsService(BaseService[BaseModel, BaseRepository]):
    """
    Core metrics service for system-wide metrics management.
    
    Provides:
    - Metrics collection and storage
    - Metrics aggregation and analysis
    - Real-time metrics streaming
    - Historical metrics retrieval
    - Performance monitoring
    - Business intelligence
    """

    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository, "MetricsService")
        
        # Metrics storage
        self._metrics: Dict[str, List[MetricValue]] = {}
        self._metric_definitions: Dict[str, MetricDefinition] = {}
        self._aggregations: Dict[str, List[MetricAggregation]] = {}
        
        # Real-time streaming
        self._subscribers: Dict[str, List[Callable]] = {}
        self._streaming_enabled = True
        
        # Aggregation settings
        self._aggregation_interval = timedelta(minutes=5)
        self._retention_period = timedelta(days=30)
        self._max_metrics_per_name = 10000
        
        # Performance tracking
        self._collection_stats = {
            'total_metrics_collected': 0,
            'total_metrics_stored': 0,
            'total_aggregations': 0,
            'last_cleanup': datetime.now()
        }
        
        logger.info("Metrics service initialized")

    async def _initialize_service_resources(self) -> None:
        """Initialize metrics service resources."""
        # Start metrics aggregation
        await self._start_metrics_aggregation()
        
        # Start metrics cleanup
        await self._start_metrics_cleanup()
        
        # Initialize default metrics
        await self._initialize_default_metrics()
        
        logger.info("Metrics service resources initialized")

    async def _cleanup_service_resources(self) -> None:
        """Cleanup metrics service resources."""
        # Stop metrics aggregation
        await self._stop_metrics_aggregation()
        
        # Stop metrics cleanup
        await self._stop_metrics_cleanup()
        
        # Cleanup metrics storage
        await self._cleanup_metrics_storage()
        
        logger.info("Metrics service resources cleaned up")

    async def get_service_info(self) -> Dict[str, Any]:
        """Get metrics service information."""
        return {
            'service_name': self.service_name,
            'total_metrics': len(self._metrics),
            'total_definitions': len(self._metric_definitions),
            'total_aggregations': len(self._aggregations),
            'collection_stats': self._collection_stats,
            'health_status': self.health_status,
            'uptime': str(self.get_uptime()),
            'last_health_check': self.last_health_check.isoformat()
        }

    # Metric Definition Management

    async def define_metric(self, name: str, metric_type: MetricType, 
                           description: str, unit: str = "", 
                           labels: List[str] = None, 
                           tags: Dict[str, str] = None) -> bool:
        """
        Define a new metric.
        
        Args:
            name: Metric name
            metric_type: Type of metric
            description: Metric description
            unit: Unit of measurement
            labels: List of label names
            tags: Key-value tags
            
        Returns:
            True if definition successful, False otherwise
        """
        try:
            if name in self._metric_definitions:
                logger.warning(f"Metric {name} already defined, updating")
            
            metric_def = MetricDefinition(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit,
                labels=labels or [],
                tags=tags or {}
            )
            
            self._metric_definitions[name] = metric_def
            
            # Initialize storage for this metric
            if name not in self._metrics:
                self._metrics[name] = []
            
            if name not in self._aggregations:
                self._aggregations[name] = []
            
            logger.info(f"Metric {name} defined successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to define metric {name}: {e}")
            return False

    async def get_metric_definition(self, name: str) -> Optional[MetricDefinition]:
        """Get metric definition by name."""
        return self._metric_definitions.get(name)

    async def list_metric_definitions(self) -> List[MetricDefinition]:
        """List all metric definitions."""
        return list(self._metric_definitions.values())

    # Metrics Collection

    async def record_metric(self, name: str, value: Union[int, float], 
                           labels: Dict[str, str] = None, 
                           tags: Dict[str, str] = None) -> bool:
        """
        Record a metric value.
        
        Args:
            name: Metric name
            value: Metric value
            labels: Key-value labels
            tags: Key-value tags
            
        Returns:
            True if recording successful, False otherwise
        """
        try:
            # Validate metric exists
            if name not in self._metric_definitions:
                logger.warning(f"Recording metric {name} that is not defined")
                # Auto-define as gauge if not defined
                await self.define_metric(name, MetricType.GAUGE, f"Auto-defined metric: {name}")
            
            # Create metric value
            metric_value = MetricValue(
                metric_name=name,
                value=value,
                timestamp=datetime.now(),
                labels=labels or {},
                tags=tags or {}
            )
            
            # Store metric
            if name not in self._metrics:
                self._metrics[name] = []
            
            self._metrics[name].append(metric_value)
            
            # Enforce storage limits
            if len(self._metrics[name]) > self._max_metrics_per_name:
                self._metrics[name] = self._metrics[name][-self._max_metrics_per_name:]
            
            # Update collection stats
            self._collection_stats['total_metrics_collected'] += 1
            self._collection_stats['total_metrics_stored'] += 1
            
            # Notify subscribers
            await self._notify_subscribers(name, metric_value)
            
            logger.debug(f"Recorded metric {name}: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric {name}: {e}")
            return False

    async def record_counter(self, name: str, increment: int = 1, 
                           labels: Dict[str, str] = None, 
                           tags: Dict[str, str] = None) -> bool:
        """Record a counter metric increment."""
        return await self.record_metric(name, increment, labels, tags)

    async def record_gauge(self, name: str, value: float, 
                          labels: Dict[str, str] = None, 
                          tags: Dict[str, str] = None) -> bool:
        """Record a gauge metric value."""
        return await self.record_metric(name, value, labels, tags)

    async def record_histogram(self, name: str, value: float, 
                              labels: Dict[str, str] = None, 
                              tags: Dict[str, str] = None) -> bool:
        """Record a histogram metric value."""
        return await self.record_metric(name, value, labels, tags)

    # Metrics Retrieval

    async def get_metric_values(self, name: str, 
                               start_time: datetime = None, 
                               end_time: datetime = None,
                               labels: Dict[str, str] = None) -> List[MetricValue]:
        """
        Get metric values for a specific metric.
        
        Args:
            name: Metric name
            start_time: Start time filter
            end_time: End time filter
            labels: Label filter
            
        Returns:
            List of matching metric values
        """
        try:
            if name not in self._metrics:
                return []
            
            values = self._metrics[name]
            
            # Apply time filters
            if start_time:
                values = [v for v in values if v.timestamp >= start_time]
            if end_time:
                values = [v for v in values if v.timestamp <= end_time]
            
            # Apply label filters
            if labels:
                values = [v for v in values if all(
                    v.labels.get(k) == v for k, v in labels.items()
                )]
            
            return values
            
        except Exception as e:
            logger.error(f"Failed to get metric values for {name}: {e}")
            return []

    async def get_latest_metric_value(self, name: str) -> Optional[MetricValue]:
        """Get the latest value for a metric."""
        try:
            if name not in self._metrics or not self._metrics[name]:
                return None
            
            return self._metrics[name][-1]
            
        except Exception as e:
            logger.error(f"Failed to get latest metric value for {name}: {e}")
            return None

    async def get_metric_summary(self, name: str, 
                                start_time: datetime = None, 
                                end_time: datetime = None) -> Optional[MetricAggregation]:
        """
        Get aggregated summary for a metric.
        
        Args:
            name: Metric name
            start_time: Start time for aggregation
            end_time: End time for aggregation
            
        Returns:
            Metric aggregation or None if no data
        """
        try:
            values = await self.get_metric_values(name, start_time, end_time)
            
            if not values:
                return None
            
            # Extract numeric values
            numeric_values = [v.value for v in values if isinstance(v.value, (int, float))]
            
            if not numeric_values:
                return None
            
            # Calculate statistics
            count = len(numeric_values)
            sum_val = sum(numeric_values)
            min_val = min(numeric_values)
            max_val = max(numeric_values)
            mean_val = sum_val / count
            median_val = statistics.median(numeric_values)
            std_dev_val = statistics.stdev(numeric_values) if count > 1 else 0
            
            # Calculate percentiles
            percentiles = {}
            for p in [50, 75, 90, 95, 99]:
                try:
                    percentiles[f"p{p}"] = statistics.quantiles(numeric_values, n=100)[p-1]
                except:
                    percentiles[f"p{p}"] = max_val
            
            return MetricAggregation(
                metric_name=name,
                count=count,
                sum=sum_val,
                min=min_val,
                max=max_val,
                mean=mean_val,
                median=median_val,
                std_dev=std_dev_val,
                percentiles=percentiles,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to get metric summary for {name}: {e}")
            return None

    # Metrics Aggregation

    async def _start_metrics_aggregation(self) -> None:
        """Start periodic metrics aggregation."""
        logger.info("Starting metrics aggregation")
        
        # Schedule periodic aggregation
        asyncio.create_task(self._metrics_aggregation_loop())

    async def _stop_metrics_aggregation(self) -> None:
        """Stop metrics aggregation."""
        logger.info("Stopping metrics aggregation")

    async def _metrics_aggregation_loop(self) -> None:
        """Main metrics aggregation loop."""
        while self.is_active:
            try:
                await self._aggregate_all_metrics()
                await asyncio.sleep(self._aggregation_interval.total_seconds())
            except Exception as e:
                logger.error(f"Metrics aggregation error: {e}")
                await asyncio.sleep(60)

    async def _aggregate_all_metrics(self) -> None:
        """Aggregate all metrics."""
        try:
            for metric_name in self._metric_definitions.keys():
                await self._aggregate_metric(metric_name)
            
            self._collection_stats['total_aggregations'] += 1
            logger.debug("Completed metrics aggregation cycle")
            
        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")

    async def _aggregate_metric(self, metric_name: str) -> None:
        """Aggregate a specific metric."""
        try:
            # Get recent values (last aggregation interval)
            end_time = datetime.now()
            start_time = end_time - self._aggregation_interval
            
            aggregation = await self.get_metric_summary(metric_name, start_time, end_time)
            
            if aggregation:
                self._aggregations[metric_name].append(aggregation)
                
                # Keep only recent aggregations
                if len(self._aggregations[metric_name]) > 100:
                    self._aggregations[metric_name] = self._aggregations[metric_name][-100:]
                
                logger.debug(f"Aggregated metric {metric_name}: {aggregation.count} values")
            
        except Exception as e:
            logger.error(f"Failed to aggregate metric {metric_name}: {e}")

    # Metrics Cleanup

    async def _start_metrics_cleanup(self) -> None:
        """Start periodic metrics cleanup."""
        logger.info("Starting metrics cleanup")
        
        # Schedule periodic cleanup
        asyncio.create_task(self._metrics_cleanup_loop())

    async def _stop_metrics_cleanup(self) -> None:
        """Stop metrics cleanup."""
        logger.info("Stopping metrics cleanup")

    async def _metrics_cleanup_loop(self) -> None:
        """Main metrics cleanup loop."""
        while self.is_active:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Cleanup every hour
            except Exception as e:
                logger.error(f"Metrics cleanup error: {e}")
                await asyncio.sleep(300)

    async def _cleanup_old_metrics(self) -> None:
        """Cleanup old metrics based on retention period."""
        try:
            cutoff_time = datetime.now() - self._retention_period
            
            for metric_name in list(self._metrics.keys()):
                # Remove old values
                self._metrics[metric_name] = [
                    v for v in self._metrics[metric_name] 
                    if v.timestamp >= cutoff_time
                ]
                
                # Remove empty metrics
                if not self._metrics[metric_name]:
                    del self._metrics[metric_name]
            
            # Cleanup old aggregations
            for metric_name in list(self._aggregations.keys()):
                self._aggregations[metric_name] = [
                    a for a in self._aggregations[metric_name] 
                    if a.timestamp >= cutoff_time
                ]
                
                if not self._aggregations[metric_name]:
                    del self._aggregations[metric_name]
            
            self._collection_stats['last_cleanup'] = datetime.now()
            logger.info("Completed metrics cleanup")
            
        except Exception as e:
            logger.error(f"Failed to cleanup metrics: {e}")

    # Real-time Streaming

    async def subscribe_to_metric(self, metric_name: str, 
                                callback: Callable[[str, MetricValue], None]) -> bool:
        """
        Subscribe to real-time metric updates.
        
        Args:
            metric_name: Metric name to subscribe to
            callback: Callback function to receive updates
            
        Returns:
            True if subscription successful, False otherwise
        """
        try:
            if metric_name not in self._subscribers:
                self._subscribers[metric_name] = []
            
            self._subscribers[metric_name].append(callback)
            logger.info(f"Subscribed to metric {metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to metric {metric_name}: {e}")
            return False

    async def unsubscribe_from_metric(self, metric_name: str, 
                                    callback: Callable[[str, MetricValue], None]) -> bool:
        """Unsubscribe from metric updates."""
        try:
            if metric_name in self._subscribers:
                if callback in self._subscribers[metric_name]:
                    self._subscribers[metric_name].remove(callback)
                    logger.info(f"Unsubscribed from metric {metric_name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from metric {metric_name}: {e}")
            return False

    async def _notify_subscribers(self, metric_name: str, metric_value: MetricValue) -> None:
        """Notify all subscribers of a metric update."""
        if not self._streaming_enabled:
            return
        
        try:
            if metric_name in self._subscribers:
                for callback in self._subscribers[metric_name]:
                    try:
                        # Check if callback is a coroutine and await it
                        if asyncio.iscoroutinefunction(callback):
                            await callback(metric_name, metric_value)
                        else:
                            callback(metric_name, metric_value)
                    except Exception as e:
                        logger.error(f"Subscriber callback error for {metric_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to notify subscribers for {metric_name}: {e}")

    # Business Intelligence

    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide metrics overview."""
        try:
            overview = {
                'timestamp': datetime.now().isoformat(),
                'total_metrics': len(self._metrics),
                'total_definitions': len(self._metric_definitions),
                'collection_stats': self._collection_stats,
                'top_metrics': await self._get_top_metrics(),
                'recent_activity': await self._get_recent_activity()
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"Failed to get system overview: {e}")
            return {'error': str(e)}

    async def _get_top_metrics(self) -> List[Dict[str, Any]]:
        """Get top metrics by activity."""
        try:
            metric_activity = []
            
            for name, values in self._metrics.items():
                if values:
                    latest_value = values[-1]
                    metric_activity.append({
                        'name': name,
                        'latest_value': latest_value.value,
                        'latest_timestamp': latest_value.timestamp.isoformat(),
                        'total_values': len(values)
                    })
            
            # Sort by total values (most active first)
            metric_activity.sort(key=lambda x: x['total_values'], reverse=True)
            
            return metric_activity[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Failed to get top metrics: {e}")
            return []

    async def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent metrics activity."""
        try:
            now = datetime.now()
            recent_cutoff = now - timedelta(hours=1)
            
            recent_metrics = 0
            recent_aggregations = 0
            
            for values in self._metrics.values():
                recent_metrics += sum(1 for v in values if v.timestamp >= recent_cutoff)
            
            for aggregations in self._aggregations.values():
                recent_aggregations += sum(1 for a in aggregations if a.timestamp >= recent_cutoff)
            
            return {
                'recent_metrics': recent_metrics,
                'recent_aggregations': recent_aggregations,
                'time_period': '1 hour'
            }
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return {}

    # Default Metrics

    async def _initialize_default_metrics(self) -> None:
        """Initialize default system metrics."""
        try:
            # System performance metrics
            await self.define_metric(
                "system.cpu_usage", 
                MetricType.GAUGE, 
                "System CPU usage percentage", 
                "percent"
            )
            
            await self.define_metric(
                "system.memory_usage", 
                MetricType.GAUGE, 
                "System memory usage percentage", 
                "percent"
            )
            
            await self.define_metric(
                "system.disk_usage", 
                MetricType.GAUGE, 
                "System disk usage percentage", 
                "percent"
            )
            
            # Service metrics
            await self.define_metric(
                "service.requests_total", 
                MetricType.COUNTER, 
                "Total service requests", 
                "requests"
            )
            
            await self.define_metric(
                "service.response_time", 
                MetricType.HISTOGRAM, 
                "Service response time", 
                "milliseconds"
            )
            
            await self.define_metric(
                "service.error_rate", 
                MetricType.GAUGE, 
                "Service error rate", 
                "percent"
            )
            
            logger.info("Default metrics initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default metrics: {e}")

    # Cleanup

    async def _cleanup_metrics_storage(self) -> None:
        """Cleanup metrics storage."""
        try:
            self._metrics.clear()
            self._aggregations.clear()
            self._subscribers.clear()
            logger.info("Metrics storage cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup metrics storage: {e}")

    # Export and Import

    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics data."""
        try:
            if format.lower() == "json":
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'metrics': self._metrics,
                    'definitions': self._metric_definitions,
                    'aggregations': self._aggregations
                }
                return json.dumps(export_data, default=str, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return ""

    async def import_metrics(self, data: str, format: str = "json") -> bool:
        """Import metrics data."""
        try:
            if format.lower() == "json":
                import_data = json.loads(data)
                
                # Import definitions
                for name, definition in import_data.get('definitions', {}).items():
                    await self.define_metric(
                        name, 
                        MetricType(definition['metric_type']), 
                        definition['description'],
                        definition.get('unit', ''),
                        definition.get('labels', []),
                        definition.get('tags', {})
                    )
                
                # Import metrics
                for name, values in import_data.get('metrics', {}).items():
                    for value_data in values:
                        await self.record_metric(
                            name,
                            value_data['value'],
                            value_data.get('labels', {}),
                            value_data.get('tags', {})
                        )
                
                logger.info("Metrics imported successfully")
                return True
            else:
                raise ValueError(f"Unsupported import format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to import metrics: {e}")
            return False
