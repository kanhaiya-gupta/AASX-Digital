"""
Performance Profiler

Advanced performance profiling and tracing system for the AAS Data Modeling Engine.
Provides operation timing, slow query detection, and performance analytics.
"""

import time
import asyncio
import functools
from typing import Dict, Any, List, Optional, Callable, Awaitable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging
import traceback
import json
from pathlib import Path

from .monitoring_config import MonitoringConfig


@dataclass
class OperationTrace:
    """Individual operation trace with timing and metadata"""
    operation_id: str
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    parent_operation: Optional[str] = None
    child_operations: List[str] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """Aggregated performance metrics for operations"""
    operation_name: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    total_duration: float
    min_duration: float
    max_duration: float
    avg_duration: float
    p50_duration: float
    p95_duration: float
    p99_duration: float
    slow_operations: int
    error_rate: float
    last_updated: datetime


class PerformanceProfiler:
    """Advanced performance profiling and tracing system"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Performance data storage
        self.operation_traces: Dict[str, OperationTrace] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.slow_operations: deque = deque(maxlen=config.performance.max_traces)
        
        # Profiling state
        self._profiling_enabled = config.performance.enabled
        self._sampling_rate = config.performance.sampling_rate
        self._slow_query_threshold = config.performance.slow_query_threshold
        self._active_operations: Dict[str, float] = {}
        
        # Initialize default operation tracking
        self._init_default_operations()
    
    def _init_default_operations(self):
        """Initialize tracking for default operations"""
        default_operations = [
            "database.query",
            "database.transaction",
            "cache.get",
            "cache.set",
            "cache.delete",
            "api.request",
            "api.response",
            "security.auth",
            "security.encrypt",
            "security.decrypt",
            "messaging.publish",
            "messaging.consume",
            "etl.transform",
            "etl.load",
            "digital_twin.update",
            "digital_twin.query"
        ]
        
        for op_name in default_operations:
            self._init_operation_metrics(op_name)
    
    def _init_operation_metrics(self, operation_name: str):
        """Initialize performance metrics for an operation"""
        if operation_name not in self.performance_metrics:
            self.performance_metrics[operation_name] = PerformanceMetrics(
                operation_name=operation_name,
                total_operations=0,
                successful_operations=0,
                failed_operations=0,
                total_duration=0.0,
                min_duration=float('inf'),
                max_duration=0.0,
                avg_duration=0.0,
                p50_duration=0.0,
                p95_duration=0.0,
                p99_duration=0.0,
                slow_operations=0,
                error_rate=0.0,
                last_updated=datetime.now()
            )
    
    def start_operation(self, operation_name: str, operation_id: Optional[str] = None, 
                       tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None,
                       parent_operation: Optional[str] = None) -> str:
        """Start timing an operation"""
        if not self._profiling_enabled:
            return ""
        
        # Apply sampling if enabled
        if self._sampling_rate < 1.0 and hash(operation_name) % 100 >= int(self._sampling_rate * 100):
            return ""
        
        if operation_id is None:
            operation_id = f"{operation_name}_{int(time.time() * 1000000)}"
        
        start_time = time.time()
        self._active_operations[operation_id] = start_time
        
        # Create trace
        trace = OperationTrace(
            operation_id=operation_id,
            operation_name=operation_name,
            start_time=start_time,
            end_time=0.0,
            duration=0.0,
            success=False,
            tags=tags or [],
            metadata=metadata or {},
            parent_operation=parent_operation
        )
        
        self.operation_traces[operation_id] = trace
        
        # Update parent operation if exists
        if parent_operation and parent_operation in self.operation_traces:
            self.operation_traces[parent_operation].child_operations.append(operation_id)
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, 
                     error_message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """End timing an operation"""
        if not operation_id or operation_id not in self._active_operations:
            return
        
        end_time = time.time()
        start_time = self._active_operations.pop(operation_id, end_time)
        duration = end_time - start_time
        
        if operation_id in self.operation_traces:
            trace = self.operation_traces[operation_id]
            trace.end_time = end_time
            trace.duration = duration
            trace.success = success
            trace.error_message = error_message
            
            if metadata:
                trace.metadata.update(metadata)
            
            # Update performance metrics
            self._update_performance_metrics(trace)
            
            # Check for slow operations
            if duration > self._slow_query_threshold:
                self._record_slow_operation(trace)
            
            # Cleanup old traces if needed
            self._cleanup_old_traces()
    
    def _update_performance_metrics(self, trace: OperationTrace):
        """Update performance metrics for an operation"""
        op_name = trace.operation_name
        
        if op_name not in self.performance_metrics:
            self._init_operation_metrics(op_name)
        
        metrics = self.performance_metrics[op_name]
        
        # Update basic counts
        metrics.total_operations += 1
        if trace.success:
            metrics.successful_operations += 1
        else:
            metrics.failed_operations += 1
        
        # Update duration statistics
        metrics.total_duration += trace.duration
        metrics.min_duration = min(metrics.min_duration, trace.duration)
        metrics.max_duration = max(metrics.max_duration, trace.duration)
        metrics.avg_duration = metrics.total_duration / metrics.total_operations
        
        # Update error rate
        metrics.error_rate = metrics.failed_operations / metrics.total_operations
        
        # Update slow operations count
        if trace.duration > self._slow_query_threshold:
            metrics.slow_operations += 1
        
        # Update percentiles (simplified calculation)
        self._update_percentiles(metrics, trace.duration)
        
        metrics.last_updated = datetime.now()
    
    def _update_percentiles(self, metrics: PerformanceMetrics, duration: float):
        """Update percentile calculations (simplified)"""
        # This is a simplified percentile calculation
        # In production, you might want to use a more sophisticated approach
        
        # For now, we'll use a simple moving average approach
        if metrics.total_operations <= 1:
            metrics.p50_duration = duration
            metrics.p95_duration = duration
            metrics.p99_duration = duration
        else:
            # Simple percentile approximation
            metrics.p50_duration = metrics.avg_duration
            metrics.p95_duration = metrics.avg_duration * 1.5
            metrics.p99_duration = metrics.avg_duration * 2.0
    
    def _record_slow_operation(self, trace: OperationTrace):
        """Record a slow operation for analysis"""
        self.slow_operations.append(trace)
        
        # Log slow operation
        self.logger.warning(
            f"Slow operation detected: {trace.operation_name} "
            f"took {trace.duration:.3f}s (threshold: {self._slow_query_threshold:.3f}s)"
        )
    
    def _cleanup_old_traces(self):
        """Clean up old operation traces"""
        if len(self.operation_traces) > self.config.performance.max_traces:
            # Remove oldest traces
            sorted_traces = sorted(
                self.operation_traces.items(),
                key=lambda x: x[1].start_time
            )
            
            # Keep only the most recent traces
            traces_to_remove = len(sorted_traces) - self.config.performance.max_traces
            for i in range(traces_to_remove):
                trace_id = sorted_traces[i][0]
                del self.operation_traces[trace_id]
    
    def profile_function(self, operation_name: Optional[str] = None, tags: Optional[List[str]] = None):
        """Decorator to profile a function"""
        def decorator(func):
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                op_id = self.start_operation(op_name, tags=tags)
                
                try:
                    result = func(*args, **kwargs)
                    self.end_operation(op_id, success=True)
                    return result
                except Exception as e:
                    self.end_operation(op_id, success=False, error_message=str(e))
                    raise
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                op_id = self.start_operation(op_name, tags=tags)
                
                try:
                    result = await func(*args, **kwargs)
                    self.end_operation(op_id, success=True)
                    return result
                except Exception as e:
                    self.end_operation(op_id, success=False, error_message=str(e))
                    raise
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def profile_context(self, operation_name: str, tags: Optional[List[str]] = None, 
                       metadata: Optional[Dict[str, Any]] = None):
        """Context manager for profiling operations"""
        return OperationProfilerContext(self, operation_name, tags, metadata)
    
    def get_operation_trace(self, operation_id: str) -> Optional[OperationTrace]:
        """Get a specific operation trace"""
        return self.operation_traces.get(operation_id)
    
    async def get_performance_metrics(self, operation_name: Optional[str] = None) -> Union[Dict[str, PerformanceMetrics], Dict[str, Any]]:
        """Get performance metrics for operations"""
        if operation_name:
            metrics = self.performance_metrics.get(operation_name)
            if metrics is None:
                return {
                    "operation_name": operation_name,
                    "status": "no_data",
                    "message": "No performance data available for this operation",
                    "timestamp": datetime.now().isoformat()
                }
            return metrics
        else:
            if not self.performance_metrics:
                return {
                    "status": "no_data",
                    "message": "No performance data available",
                    "timestamp": datetime.now().isoformat(),
                    "total_operations": 0
                }
            return self.performance_metrics.copy()
    
    def get_slow_operations(self, limit: Optional[int] = None) -> List[OperationTrace]:
        """Get list of slow operations"""
        if limit is None:
            return list(self.slow_operations)
        else:
            return list(self.slow_operations)[-limit:]
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get summary of all operations"""
        summary = {
            "total_operations": len(self.operation_traces),
            "active_operations": len(self._active_operations),
            "slow_operations": len(self.slow_operations),
            "performance_metrics": {},
            "slowest_operations": [],
            "most_error_prone_operations": []
        }
        
        # Add performance metrics
        for op_name, metrics in self.performance_metrics.items():
            summary["performance_metrics"][op_name] = {
                "total_operations": metrics.total_operations,
                "success_rate": 1 - metrics.error_rate,
                "avg_duration": metrics.avg_duration,
                "slow_operations": metrics.slow_operations
            }
        
        # Find slowest operations
        slowest_ops = sorted(
            self.performance_metrics.values(),
            key=lambda x: x.avg_duration,
            reverse=True
        )[:10]
        
        summary["slowest_operations"] = [
            {
                "operation": op.operation_name,
                "avg_duration": op.avg_duration,
                "total_operations": op.total_operations
            }
            for op in slowest_ops
        ]
        
        # Find most error-prone operations
        error_prone_ops = sorted(
            self.performance_metrics.values(),
            key=lambda x: x.error_rate,
            reverse=True
        )[:10]
        
        summary["most_error_prone_operations"] = [
            {
                "operation": op.operation_name,
                "error_rate": op.error_rate,
                "total_operations": op.total_operations
            }
            for op in error_prone_ops
        ]
        
        return summary
    
    def export_performance_data(self, format: str = "json", filepath: Optional[Path] = None) -> Path:
        """Export performance data to file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_{timestamp}.{format}"
            filepath = self.config.export.export_directory / filename
        
        if format == "json":
            self._export_json(filepath)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Exported performance data to {filepath}")
        return filepath
    
    def _export_json(self, filepath: Path):
        """Export performance data to JSON format"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "performance_summary": self.get_operation_summary(),
            "operation_traces": {},
            "performance_metrics": {}
        }
        
        # Export operation traces
        for trace_id, trace in self.operation_traces.items():
            export_data["operation_traces"][trace_id] = {
                "operation_name": trace.operation_name,
                "start_time": trace.start_time,
                "end_time": trace.end_time,
                "duration": trace.duration,
                "success": trace.success,
                "error_message": trace.error_message,
                "tags": trace.tags,
                "metadata": trace.metadata,
                "parent_operation": trace.parent_operation,
                "child_operations": trace.child_operations
            }
        
        # Export performance metrics
        for op_name, metrics in self.performance_metrics.items():
            export_data["performance_metrics"][op_name] = {
                "total_operations": metrics.total_operations,
                "successful_operations": metrics.successful_operations,
                "failed_operations": metrics.failed_operations,
                "total_duration": metrics.total_duration,
                "min_duration": metrics.min_duration,
                "max_duration": metrics.max_duration,
                "avg_duration": metrics.avg_duration,
                "p50_duration": metrics.p50_duration,
                "p95_duration": metrics.p95_duration,
                "p99_duration": metrics.p99_duration,
                "slow_operations": metrics.slow_operations,
                "error_rate": metrics.error_rate,
                "last_updated": metrics.last_updated.isoformat()
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def reset_performance_data(self):
        """Reset all performance data"""
        self.operation_traces.clear()
        self.performance_metrics.clear()
        self.slow_operations.clear()
        self._active_operations.clear()
        
        # Reinitialize default operations
        self._init_default_operations()
        
        self.logger.info("All performance data reset")
    
    def enable_profiling(self):
        """Enable performance profiling"""
        self._profiling_enabled = True
        self.logger.info("Performance profiling enabled")
    
    def disable_profiling(self):
        """Disable performance profiling"""
        self._profiling_enabled = False
        self.logger.info("Performance profiling disabled")
    
    def set_sampling_rate(self, rate: float):
        """Set the sampling rate for operations (0.0 to 1.0)"""
        if 0.0 <= rate <= 1.0:
            self._sampling_rate = rate
            self.logger.info(f"Sampling rate set to {rate}")
        else:
            raise ValueError("Sampling rate must be between 0.0 and 1.0")
    
    def set_slow_query_threshold(self, threshold: float):
        """Set the slow query threshold in seconds"""
        if threshold > 0:
            self._slow_query_threshold = threshold
            self.logger.info(f"Slow query threshold set to {threshold}s")
        else:
            raise ValueError("Slow query threshold must be positive")
    
    async def cleanup(self):
        """Cleanup performance profiler resources"""
        try:
            # Cleanup old traces
            self._cleanup_old_traces()
            
            # Clear active operations
            self._active_operations.clear()
            
            # Clear performance metrics
            self.performance_metrics.clear()
            
            # Clear slow operations
            self.slow_operations.clear()
            
            self.logger.info("Performance profiler cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to cleanup performance profiler: {e}")
            raise


class OperationProfilerContext:
    """Context manager for profiling operations"""
    
    def __init__(self, profiler: PerformanceProfiler, operation_name: str, 
                 tags: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None):
        self.profiler = profiler
        self.operation_name = operation_name
        self.tags = tags
        self.metadata = metadata
        self.operation_id = None
    
    def __enter__(self):
        self.operation_id = self.profiler.start_operation(
            self.operation_name, 
            tags=self.tags, 
            metadata=self.metadata
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.operation_id:
            success = exc_type is None
            error_message = str(exc_val) if exc_val else None
            self.profiler.end_operation(
                self.operation_id, 
                success=success, 
                error_message=error_message
            )
    
    async def __aenter__(self):
        self.operation_id = self.profiler.start_operation(
            self.operation_name, 
            tags=self.tags, 
            metadata=self.metadata
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.operation_id:
            success = exc_type is None
            error_message = str(exc_val) if exc_val else None
            self.profiler.end_operation(
                self.operation_id, 
                success=success, 
                error_message=error_message
            )
