"""
Performance utilities for AI RAG module
Provides performance monitoring, optimization, and metrics collection functions
"""

import time
import psutil
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.enabled = True
    
    def start_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start monitoring an operation.
        
        Args:
            operation_name: Name of the operation
            metadata: Additional metadata for the operation
            
        Returns:
            Operation ID for tracking
        """
        if not self.enabled:
            return ""
        
        operation_id = f"{operation_name}_{int(time.time() * 1000000)}"
        
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        self.metrics.append(metrics)
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, error_message: Optional[str] = None) -> None:
        """
        End monitoring an operation.
        
        Args:
            operation_id: Operation ID from start_operation
            success: Whether the operation was successful
            error_message: Error message if operation failed
        """
        if not self.enabled or not operation_id:
            return
        
        # Find the operation by ID
        for metrics in self.metrics:
            if f"{metrics.operation_name}_{int(metrics.start_time.timestamp() * 1000000)}" == operation_id:
                metrics.end_time = datetime.now()
                metrics.duration = (metrics.end_time - metrics.start_time).total_seconds()
                metrics.success = success
                metrics.error_message = error_message
                
                # Capture system metrics
                try:
                    process = psutil.Process()
                    metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                    metrics.cpu_usage_percent = process.cpu_percent()
                except Exception as e:
                    logger.warning(f"Failed to capture system metrics: {e}")
                
                break
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all collected metrics.
        
        Returns:
            Dictionary containing metrics summary
        """
        if not self.metrics:
            return {}
        
        successful_ops = [m for m in self.metrics if m.success]
        failed_ops = [m for m in self.metrics if not m.success]
        
        total_duration = sum(m.duration or 0 for m in self.metrics)
        avg_duration = total_duration / len(self.metrics) if self.metrics else 0
        
        return {
            'total_operations': len(self.metrics),
            'successful_operations': len(successful_ops),
            'failed_operations': len(failed_ops),
            'success_rate': len(successful_ops) / len(self.metrics) if self.metrics else 0,
            'total_duration': total_duration,
            'average_duration': avg_duration,
            'operations': [
                {
                    'name': m.operation_name,
                    'duration': m.duration,
                    'success': m.success,
                    'memory_mb': m.memory_usage_mb,
                    'cpu_percent': m.cpu_usage_percent,
                    'metadata': m.metadata
                }
                for m in self.metrics
            ]
        }
    
    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self.metrics.clear()
    
    def export_metrics(self, file_path: str) -> bool:
        """
        Export metrics to a file.
        
        Args:
            file_path: Path to export metrics to
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            import json
            
            summary = self.get_metrics_summary()
            with open(file_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Metrics exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return False


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def measure_execution_time(func: Callable) -> Callable:
    """
    Decorator to measure execution time of a function.
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function with timing
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Function {func.__name__} executed in {duration:.4f} seconds")
            
            # Add to performance monitor
            operation_id = performance_monitor.start_operation(func.__name__)
            performance_monitor.end_operation(operation_id, success, error_message)
        
        return result
    
    return wrapper


def measure_async_execution_time(func: Callable) -> Callable:
    """
    Decorator to measure execution time of an async function.
    
    Args:
        func: Async function to measure
        
    Returns:
        Wrapped async function with timing
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            success = True
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Async function {func.__name__} executed in {duration:.4f} seconds")
            
            # Add to performance monitor
            operation_id = performance_monitor.start_operation(func.__name__)
            performance_monitor.end_operation(operation_id, success, error_message)
        
        return result
    
    return wrapper


@contextmanager
def track_memory_usage(operation_name: str):
    """
    Context manager to track memory usage during an operation.
    
    Args:
        operation_name: Name of the operation being tracked
    """
    if not performance_monitor.enabled:
        yield
        return
    
    operation_id = performance_monitor.start_operation(operation_name)
    
    try:
        # Get initial memory usage
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        yield
        
        # Get final memory usage
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_delta = final_memory - initial_memory
        
        logger.info(f"Operation {operation_name} memory usage: {memory_delta:+.2f} MB")
        
        performance_monitor.end_operation(operation_id, True)
        
    except Exception as e:
        performance_monitor.end_operation(operation_id, False, str(e))
        raise


def get_system_metrics() -> Dict[str, Any]:
    """
    Get current system metrics.
    
    Returns:
        Dictionary containing system metrics
    """
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_metrics = {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_gb': memory.used / (1024**3),
            'percent_used': memory.percent
        }
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_metrics = {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent_used': (disk.used / disk.total) * 100
        }
        
        # Network metrics
        network = psutil.net_io_counters()
        network_metrics = {
            'bytes_sent_mb': network.bytes_sent / (1024**2),
            'bytes_recv_mb': network.bytes_recv / (1024**2)
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': memory_metrics,
            'disk': disk_metrics,
            'network': network_metrics
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {}


def optimize_batch_size(
    initial_batch_size: int,
    target_duration: float,
    current_duration: float,
    min_batch_size: int = 1,
    max_batch_size: int = 1000
) -> int:
    """
    Optimize batch size based on performance metrics.
    
    Args:
        initial_batch_size: Current batch size
        target_duration: Target execution duration
        current_duration: Current execution duration
        min_batch_size: Minimum allowed batch size
        max_batch_size: Maximum allowed batch size
        
    Returns:
        Optimized batch size
    """
    if current_duration <= 0:
        return initial_batch_size
    
    # Calculate ratio of target to current duration
    ratio = target_duration / current_duration
    
    # Adjust batch size proportionally
    new_batch_size = int(initial_batch_size * ratio)
    
    # Ensure within bounds
    new_batch_size = max(min_batch_size, min(max_batch_size, new_batch_size))
    
    logger.info(f"Batch size optimized from {initial_batch_size} to {new_batch_size}")
    return new_batch_size


def create_performance_report(
    metrics: List[PerformanceMetrics],
    output_file: Optional[str] = None
) -> str:
    """
    Create a comprehensive performance report.
    
    Args:
        metrics: List of performance metrics
        output_file: Optional file path to save report
        
    Returns:
        Formatted performance report string
    """
    if not metrics:
        return "No performance metrics available."
    
    # Group metrics by operation
    operation_groups = {}
    for metric in metrics:
        if metric.operation_name not in operation_groups:
            operation_groups[metric.operation_name] = []
        operation_groups[metric.operation_name].append(metric)
    
    # Generate report
    report_lines = [
        "=" * 60,
        "AI RAG PERFORMANCE REPORT",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Operations: {len(metrics)}",
        ""
    ]
    
    for operation_name, operation_metrics in operation_groups.items():
        report_lines.extend([
            f"Operation: {operation_name}",
            "-" * 40,
            f"  Count: {len(operation_metrics)}",
            f"  Success Rate: {sum(1 for m in operation_metrics if m.success) / len(operation_metrics) * 100:.1f}%",
            f"  Average Duration: {sum(m.duration or 0 for m in operation_metrics) / len(operation_metrics):.4f}s",
            f"  Total Duration: {sum(m.duration or 0 for m in operation_metrics):.4f}s",
            ""
        ])
    
    # Add system metrics
    system_metrics = get_system_metrics()
    if system_metrics:
        report_lines.extend([
            "System Metrics:",
            "-" * 40,
            f"  CPU Usage: {system_metrics.get('cpu', {}).get('percent', 'N/A')}%",
            f"  Memory Used: {system_metrics.get('memory', {}).get('used_gb', 'N/A'):.2f} GB",
            f"  Disk Used: {system_metrics.get('disk', {}).get('percent_used', 'N/A'):.1f}%",
            ""
        ])
    
    report_lines.append("=" * 60)
    
    report = "\n".join(report_lines)
    
    # Save to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(report)
            logger.info(f"Performance report saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save performance report: {e}")
    
    return report





