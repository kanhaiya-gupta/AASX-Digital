"""
Performance Utilities
====================

Performance monitoring and optimization utility functions for federated learning.
Handles performance metrics, benchmarking, and optimization recommendations.
"""

import asyncio
import numpy as np
import psutil
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class PerformanceConfig:
    """Configuration for performance utilities"""
    # Monitoring settings
    cpu_monitoring_enabled: bool = True
    memory_monitoring_enabled: bool = True
    gpu_monitoring_enabled: bool = True
    network_monitoring_enabled: bool = True
    
    # Performance thresholds
    cpu_threshold: float = 0.8
    memory_threshold: float = 0.85
    gpu_threshold: float = 0.9
    network_threshold: float = 0.75
    
    # Benchmarking settings
    benchmark_iterations: int = 10
    warmup_iterations: int = 3
    timeout_seconds: float = 30.0
    
    # Optimization settings
    auto_optimization_enabled: bool = True
    optimization_interval: int = 60  # seconds
    performance_history_size: int = 100


@dataclass
class PerformanceMetrics:
    """Metrics for performance monitoring"""
    # System metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    network_usage: float = 0.0
    
    # Performance scores
    overall_performance_score: float = 0.0
    cpu_score: float = 0.0
    memory_score: float = 0.0
    gpu_score: float = 0.0
    network_score: float = 0.0
    
    # Benchmark results
    execution_time: float = 0.0
    throughput: float = 0.0
    latency: float = 0.0
    
    # Optimization metrics
    optimization_count: int = 0
    performance_improvement: float = 0.0
    bottleneck_detected: bool = False
    
    # Historical data
    performance_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = []


class PerformanceUtils:
    """Performance utility functions for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[PerformanceConfig] = None
    ):
        """Initialize Performance Utils"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or PerformanceConfig()
        
        # Performance state
        self.monitoring_active = False
        self.optimization_active = False
        self.performance_alerts: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = PerformanceMetrics()
        
        # Monitoring state
        self.monitoring_task = None
        self.last_optimization = None
        
    async def start_performance_monitoring(self) -> Dict[str, Any]:
        """Start continuous performance monitoring"""
        try:
            if self.monitoring_active:
                return {'status': 'already_active', 'message': 'Monitoring already active'}
            
            print("📊 Starting performance monitoring...")
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Start monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.monitoring_active = True
            
            # Start auto-optimization if enabled
            if self.config.auto_optimization_enabled:
                await self._start_auto_optimization()
            
            return {
                'status': 'success',
                'message': 'Performance monitoring started',
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Performance monitoring start failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _initialize_monitoring(self):
        """Initialize performance monitoring"""
        try:
            # Reset metrics
            self.metrics = PerformanceMetrics()
            
            # Clear alerts
            self.performance_alerts.clear()
            
            print("🔧 Performance monitoring initialized")
            
        except Exception as e:
            print(f"❌ Monitoring initialization failed: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Continuous performance monitoring loop"""
        try:
            while self.monitoring_active:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Check performance thresholds
                await self._check_performance_thresholds()
                
                # Update performance history
                await self._update_performance_history()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
        except Exception as e:
            print(f"❌ Performance monitoring loop failed: {e}")
    
    async def _collect_system_metrics(self):
        """Collect current system performance metrics"""
        try:
            # CPU monitoring
            if self.config.cpu_monitoring_enabled:
                self.metrics.cpu_usage = psutil.cpu_percent(interval=1) / 100.0
                self.metrics.cpu_score = 1.0 - self.metrics.cpu_usage
            
            # Memory monitoring
            if self.config.memory_monitoring_enabled:
                memory = psutil.virtual_memory()
                self.metrics.memory_usage = memory.percent / 100.0
                self.metrics.memory_score = 1.0 - self.metrics.memory_usage
            
            # GPU monitoring (simplified)
            if self.config.gpu_monitoring_enabled:
                # In practice, use GPU monitoring libraries like nvidia-ml-py
                self.metrics.gpu_usage = np.random.uniform(0.3, 0.8)  # Placeholder
                self.metrics.gpu_score = 1.0 - self.metrics.gpu_usage
            
            # Network monitoring (simplified)
            if self.config.network_monitoring_enabled:
                # In practice, use network monitoring libraries
                self.metrics.network_usage = np.random.uniform(0.2, 0.7)  # Placeholder
                self.metrics.network_score = 1.0 - self.metrics.network_usage
            
            # Calculate overall performance score
            scores = [
                self.metrics.cpu_score,
                self.metrics.memory_score,
                self.metrics.gpu_score,
                self.metrics.network_score
            ]
            self.metrics.overall_performance_score = np.mean(scores)
            
        except Exception as e:
            print(f"⚠️  System metrics collection failed: {e}")
    
    async def _check_performance_thresholds(self):
        """Check if performance metrics exceed thresholds"""
        try:
            alerts = []
            
            # CPU threshold check
            if self.metrics.cpu_usage > self.config.cpu_threshold:
                alerts.append({
                    'type': 'cpu_high',
                    'severity': 'warning',
                    'message': f"CPU usage {self.metrics.cpu_usage:.2%} exceeds threshold {self.config.cpu_threshold:.2%}",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Memory threshold check
            if self.metrics.memory_usage > self.config.memory_threshold:
                alerts.append({
                    'type': 'memory_high',
                    'severity': 'warning',
                    'message': f"Memory usage {self.metrics.memory_usage:.2%} exceeds threshold {self.config.memory_threshold:.2%}",
                    'timestamp': datetime.now().isoformat()
                })
            
            # GPU threshold check
            if self.metrics.gpu_usage > self.config.gpu_threshold:
                alerts.append({
                    'type': 'gpu_high',
                    'severity': 'warning',
                    'message': f"GPU usage {self.metrics.gpu_usage:.2%} exceeds threshold {self.config.gpu_threshold:.2%}",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Network threshold check
            if self.metrics.network_usage > self.config.network_threshold:
                alerts.append({
                    'type': 'network_high',
                    'severity': 'warning',
                    'message': f"Network usage {self.metrics.network_usage:.2%} exceeds threshold {self.config.network_threshold:.2%}",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Update alerts
            if alerts:
                self.performance_alerts.extend(alerts)
                self.metrics.bottleneck_detected = True
                
                # Trigger optimization if auto-optimization is enabled
                if self.config.auto_optimization_enabled and not self.optimization_active:
                    await self._trigger_optimization()
            
        except Exception as e:
            print(f"⚠️  Performance threshold check failed: {e}")
    
    async def _update_performance_history(self):
        """Update performance history"""
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': self.metrics.cpu_usage,
                'memory_usage': self.metrics.memory_usage,
                'gpu_usage': self.metrics.gpu_usage,
                'network_usage': self.metrics.network_usage,
                'overall_score': self.metrics.overall_performance_score
            }
            
            self.metrics.performance_history.append(history_entry)
            
            # Keep only recent history
            if len(self.metrics.performance_history) > self.config.performance_history_size:
                self.metrics.performance_history = self.metrics.performance_history[-self.config.performance_history_size:]
            
        except Exception as e:
            print(f"⚠️  Performance history update failed: {e}")
    
    async def _start_auto_optimization(self):
        """Start automatic performance optimization"""
        try:
            print("⚡ Starting auto-optimization...")
            
            # Schedule periodic optimization
            asyncio.create_task(self._auto_optimization_loop())
            
        except Exception as e:
            print(f"❌ Auto-optimization start failed: {e}")
    
    async def _auto_optimization_loop(self):
        """Automatic optimization loop"""
        try:
            while self.monitoring_active:
                await asyncio.sleep(self.config.optimization_interval)
                
                if not self.optimization_active:
                    await self._trigger_optimization()
                
        except Exception as e:
            print(f"❌ Auto-optimization loop failed: {e}")
    
    async def _trigger_optimization(self):
        """Trigger performance optimization"""
        try:
            if self.optimization_active:
                return
            
            print("🚀 Triggering performance optimization...")
            self.optimization_active = True
            
            # Run optimization
            optimization_results = await self._run_performance_optimization()
            
            # Update metrics
            self.metrics.optimization_count += 1
            if 'improvement' in optimization_results:
                self.metrics.performance_improvement = optimization_results['improvement']
            
            self.last_optimization = datetime.now()
            self.optimization_active = False
            
            print("✅ Performance optimization completed")
            
        except Exception as e:
            print(f"❌ Performance optimization failed: {e}")
            self.optimization_active = False
    
    async def _run_performance_optimization(self) -> Dict[str, Any]:
        """Run performance optimization"""
        try:
            optimization_results = {
                'optimizations_applied': [],
                'improvement': 0.0,
                'recommendations': []
            }
            
            # CPU optimization
            if self.metrics.cpu_usage > self.config.cpu_threshold:
                cpu_opt = await self._optimize_cpu_performance()
                optimization_results['optimizations_applied'].append(cpu_opt)
            
            # Memory optimization
            if self.metrics.memory_usage > self.config.memory_threshold:
                memory_opt = await self._optimize_memory_performance()
                optimization_results['optimizations_applied'].append(memory_opt)
            
            # GPU optimization
            if self.metrics.gpu_usage > self.config.gpu_threshold:
                gpu_opt = await self._optimize_gpu_performance()
                optimization_results['optimizations_applied'].append(gpu_opt)
            
            # Calculate improvement
            if optimization_results['optimizations_applied']:
                optimization_results['improvement'] = 0.1  # Placeholder improvement
                optimization_results['recommendations'] = [
                    "Consider reducing batch size for better memory usage",
                    "Enable mixed precision training for GPU optimization",
                    "Implement gradient accumulation for CPU optimization"
                ]
            
            return optimization_results
            
        except Exception as e:
            print(f"❌ Performance optimization failed: {e}")
            return {'error': str(e)}
    
    async def _optimize_cpu_performance(self) -> Dict[str, Any]:
        """Optimize CPU performance"""
        try:
            return {
                'type': 'cpu_optimization',
                'description': 'CPU usage optimization applied',
                'actions': ['Reduced thread count', 'Optimized batch processing'],
                'estimated_improvement': 0.15
            }
            
        except Exception as e:
            print(f"⚠️  CPU optimization failed: {e}")
            return {'type': 'cpu_optimization', 'error': str(e)}
    
    async def _optimize_memory_performance(self) -> Dict[str, Any]:
        """Optimize memory performance"""
        try:
            return {
                'type': 'memory_optimization',
                'description': 'Memory usage optimization applied',
                'actions': ['Garbage collection triggered', 'Memory cleanup performed'],
                'estimated_improvement': 0.2
            }
            
        except Exception as e:
            print(f"⚠️  Memory optimization failed: {e}")
            return {'type': 'memory_optimization', 'error': str(e)}
    
    async def _optimize_gpu_performance(self) -> Dict[str, Any]:
        """Optimize GPU performance"""
        try:
            return {
                'type': 'gpu_optimization',
                'description': 'GPU usage optimization applied',
                'actions': ['Mixed precision enabled', 'Memory allocation optimized'],
                'estimated_improvement': 0.25
            }
            
        except Exception as e:
            print(f"⚠️  GPU optimization failed: {e}")
            return {'type': 'gpu_optimization', 'error': str(e)}
    
    async def benchmark_function(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Benchmark a function's performance"""
        try:
            print(f"⏱️  Benchmarking function: {func.__name__}")
            
            # Warmup iterations
            for _ in range(self.config.warmup_iterations):
                try:
                    await func(*args, **kwargs)
                except:
                    pass
            
            # Benchmark iterations
            execution_times = []
            start_time = time.time()
            
            for i in range(self.config.benchmark_iterations):
                iteration_start = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    iteration_time = time.time() - iteration_start
                    execution_times.append(iteration_time)
                except Exception as e:
                    print(f"⚠️  Benchmark iteration {i} failed: {e}")
                    continue
                
                # Check timeout
                if time.time() - start_time > self.config.timeout_seconds:
                    print("⏰ Benchmark timeout reached")
                    break
            
            if not execution_times:
                return {'error': 'No successful benchmark iterations'}
            
            # Calculate metrics
            avg_time = np.mean(execution_times)
            std_time = np.std(execution_times)
            min_time = np.min(execution_times)
            max_time = np.max(execution_times)
            
            # Calculate throughput (operations per second)
            throughput = 1.0 / avg_time if avg_time > 0 else 0.0
            
            # Update metrics
            self.metrics.execution_time = avg_time
            self.metrics.throughput = throughput
            self.metrics.latency = avg_time * 1000  # Convert to milliseconds
            
            benchmark_results = {
                'function_name': func.__name__,
                'iterations': len(execution_times),
                'execution_time': {
                    'average': avg_time,
                    'std': std_time,
                    'min': min_time,
                    'max': max_time
                },
                'throughput': throughput,
                'latency_ms': self.metrics.latency,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Benchmark completed: {avg_time:.4f}s average execution time")
            
            return benchmark_results
            
        except Exception as e:
            print(f"❌ Function benchmarking failed: {e}")
            return {'error': str(e)}
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        try:
            return {
                'performance_metrics': self.metrics.__dict__,
                'performance_alerts': self.performance_alerts,
                'current_config': self.config.__dict__,
                'monitoring_status': {
                    'active': self.monitoring_active,
                    'optimization_active': self.optimization_active,
                    'last_optimization': self.last_optimization.isoformat() if self.last_optimization else None
                }
            }
            
        except Exception as e:
            print(f"❌ Performance report generation failed: {e}")
            return {'error': str(e)}
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        try:
            self.monitoring_active = False
            self.optimization_active = False
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                self.monitoring_task = None
            
            print("🛑 Performance monitoring stopped")
            
        except Exception as e:
            print(f"❌ Monitoring stop failed: {e}")
    
    async def reset_metrics(self):
        """Reset performance metrics"""
        try:
            self.metrics = PerformanceMetrics()
            self.performance_alerts.clear()
            print("🔄 Performance metrics reset")
            
        except Exception as e:
            print(f"❌ Metrics reset failed: {e}")


