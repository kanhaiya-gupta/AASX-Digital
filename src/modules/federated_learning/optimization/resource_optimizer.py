"""
Resource Optimizer
================

Resource optimization for federated learning operations.
Handles computational resource allocation, memory management, and efficiency improvements.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class ResourceConfig:
    """Configuration for resource optimization"""
    # Resource types to optimize
    cpu_optimization: bool = True
    memory_optimization: bool = True
    gpu_optimization: bool = True
    network_optimization: bool = True
    
    # CPU optimization settings
    cpu_cores_available: int = 8
    cpu_utilization_target: float = 0.8
    cpu_load_balancing: bool = True
    cpu_affinity: bool = True
    
    # Memory optimization settings
    memory_limit_gb: float = 16.0
    memory_utilization_target: float = 0.75
    memory_cleanup_interval: int = 300  # seconds
    garbage_collection: bool = True
    
    # GPU optimization settings
    gpu_memory_limit_gb: float = 8.0
    gpu_utilization_target: float = 0.85
    gpu_memory_fraction: float = 0.9
    gpu_mixed_precision: bool = True
    
    # Network optimization settings
    bandwidth_limit_mbps: float = 1000.0
    network_latency_target_ms: float = 50.0
    connection_pooling: bool = True
    compression_enabled: bool = True
    
    # Optimization strategies
    adaptive_allocation: bool = True
    predictive_scaling: bool = True
    load_balancing: bool = True
    resource_monitoring: bool = True
    
    # Performance settings
    optimization_interval: int = 60  # seconds
    monitoring_frequency: int = 10   # seconds
    alert_threshold: float = 0.9


@dataclass
class ResourceMetrics:
    """Metrics for resource optimization"""
    # Current resource utilization
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    gpu_utilization: float = 0.0
    network_utilization: float = 0.0
    
    # Resource allocation
    cpu_cores_allocated: int = 0
    memory_allocated_gb: float = 0.0
    gpu_memory_allocated_gb: float = 0.0
    bandwidth_allocated_mbps: float = 0.0
    
    # Performance metrics
    cpu_efficiency: float = 0.0
    memory_efficiency: float = 0.0
    gpu_efficiency: float = 0.0
    network_efficiency: float = 0.0
    
    # Optimization statistics
    optimization_count: int = 0
    resource_reallocations: int = 0
    performance_improvements: int = 0
    bottleneck_resolutions: int = 0
    
    # Monitoring data
    resource_history: List[Dict[str, Any]] = None
    bottleneck_history: List[Dict[str, Any]] = None
    optimization_history: List[Dict[str, Any]] = None
    
    # Alert status
    cpu_alert: bool = False
    memory_alert: bool = False
    gpu_alert: bool = False
    network_alert: bool = False
    
    def __post_init__(self):
        if self.resource_history is None:
            self.resource_history = []
        if self.bottleneck_history is None:
            self.bottleneck_history = []
        if self.optimization_history is None:
            self.optimization_history = []


class ResourceOptimizer:
    """Resource optimization implementation for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[ResourceConfig] = None
    ):
        """Initialize Resource Optimizer"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or ResourceConfig()
        
        # Optimization state
        self.is_optimizing = False
        self.current_session = None
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = ResourceMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        
        # Resource state
        self.resource_pools = {}
        self.bottleneck_detected = False
        self.optimization_scheduled = False
        
        # Monitoring state
        self.monitoring_task = None
        self.last_optimization = None
        
    async def start_resource_optimization(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Start resource optimization process"""
        try:
            self.start_time = datetime.now()
            self.is_optimizing = True
            self.current_session = session_id
            
            print(f"🚀 Starting resource optimization for session: {session_id}")
            
            # Initialize resource pools
            await self._initialize_resource_pools()
            
            # Start resource monitoring
            await self._start_resource_monitoring()
            
            # Run initial optimization
            optimization_results = await self._run_resource_optimization()
            
            # Schedule periodic optimization
            await self._schedule_periodic_optimization()
            
            return optimization_results
            
        except Exception as e:
            print(f"❌ Resource optimization failed: {e}")
            return {'status': 'failed', 'error': str(e)}
        finally:
            self.is_optimizing = False
    
    async def _initialize_resource_pools(self):
        """Initialize resource pools for optimization"""
        try:
            # CPU pool
            self.resource_pools['cpu'] = {
                'total_cores': self.config.cpu_cores_available,
                'allocated_cores': 0,
                'available_cores': self.config.cpu_cores_available,
                'utilization': 0.0,
                'efficiency': 1.0
            }
            
            # Memory pool
            self.resource_pools['memory'] = {
                'total_gb': self.config.memory_limit_gb,
                'allocated_gb': 0.0,
                'available_gb': self.config.memory_limit_gb,
                'utilization': 0.0,
                'efficiency': 1.0
            }
            
            # GPU pool
            self.resource_pools['gpu'] = {
                'total_gb': self.config.gpu_memory_limit_gb,
                'allocated_gb': 0.0,
                'available_gb': self.config.gpu_memory_limit_gb,
                'utilization': 0.0,
                'efficiency': 1.0
            }
            
            # Network pool
            self.resource_pools['network'] = {
                'total_mbps': self.config.bandwidth_limit_mbps,
                'allocated_mbps': 0.0,
                'available_mbps': self.config.bandwidth_limit_mbps,
                'utilization': 0.0,
                'efficiency': 1.0
            }
            
            print("🔧 Resource pools initialized")
            
        except Exception as e:
            print(f"❌ Resource pool initialization failed: {e}")
            raise
    
    async def _start_resource_monitoring(self):
        """Start continuous resource monitoring"""
        try:
            print("📊 Starting resource monitoring...")
            
            # Start monitoring task
            self.monitoring_task = asyncio.create_task(self._monitor_resources())
            
            print("✅ Resource monitoring started")
            
        except Exception as e:
            print(f"❌ Resource monitoring start failed: {e}")
            raise
    
    async def _monitor_resources(self):
        """Continuous resource monitoring loop"""
        try:
            while self.is_optimizing or self.optimization_scheduled:
                # Collect current resource metrics
                await self._collect_resource_metrics()
                
                # Check for bottlenecks
                await self._check_bottlenecks()
                
                # Update resource history
                await self._update_resource_history()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.config.monitoring_frequency)
                
        except Exception as e:
            print(f"❌ Resource monitoring failed: {e}")
    
    async def _collect_resource_metrics(self):
        """Collect current resource utilization metrics"""
        try:
            # Simulate resource monitoring
            # In practice, this would use system monitoring tools
            
            # CPU metrics
            if self.config.cpu_optimization:
                self.metrics.cpu_utilization = np.random.uniform(0.3, 0.9)
                self.resource_pools['cpu']['utilization'] = self.metrics.cpu_utilization
                self.resource_pools['cpu']['efficiency'] = 1.0 - abs(self.metrics.cpu_utilization - self.config.cpu_utilization_target)
            
            # Memory metrics
            if self.config.memory_optimization:
                self.metrics.memory_utilization = np.random.uniform(0.4, 0.85)
                self.resource_pools['memory']['utilization'] = self.metrics.memory_utilization
                self.resource_pools['memory']['efficiency'] = 1.0 - abs(self.metrics.memory_utilization - self.config.memory_utilization_target)
            
            # GPU metrics
            if self.config.gpu_optimization:
                self.metrics.gpu_utilization = np.random.uniform(0.5, 0.9)
                self.resource_pools['gpu']['utilization'] = self.metrics.gpu_utilization
                self.resource_pools['gpu']['efficiency'] = 1.0 - abs(self.metrics.gpu_utilization - self.config.gpu_utilization_target)
            
            # Network metrics
            if self.config.network_optimization:
                self.metrics.network_utilization = np.random.uniform(0.2, 0.8)
                self.resource_pools['network']['utilization'] = self.metrics.network_utilization
                self.resource_pools['network']['efficiency'] = 1.0 - abs(self.metrics.network_utilization - 0.5)  # Target 50% for network
            
        except Exception as e:
            print(f"⚠️  Resource metrics collection failed: {e}")
    
    async def _check_bottlenecks(self):
        """Check for resource bottlenecks"""
        try:
            bottlenecks = []
            
            # Check CPU bottleneck
            if self.metrics.cpu_utilization > self.config.alert_threshold:
                self.metrics.cpu_alert = True
                bottlenecks.append({
                    'resource': 'cpu',
                    'utilization': self.metrics.cpu_utilization,
                    'threshold': self.config.alert_threshold,
                    'severity': 'high'
                })
            else:
                self.metrics.cpu_alert = False
            
            # Check memory bottleneck
            if self.metrics.memory_utilization > self.config.alert_threshold:
                self.metrics.memory_alert = True
                bottlenecks.append({
                    'resource': 'memory',
                    'utilization': self.metrics.memory_utilization,
                    'threshold': self.config.alert_threshold,
                    'severity': 'high'
                })
            else:
                self.metrics.memory_alert = False
            
            # Check GPU bottleneck
            if self.metrics.gpu_utilization > self.config.alert_threshold:
                self.metrics.gpu_alert = True
                bottlenecks.append({
                    'resource': 'gpu',
                    'utilization': self.metrics.gpu_utilization,
                    'threshold': self.config.alert_threshold,
                    'severity': 'high'
                })
            else:
                self.metrics.gpu_alert = False
            
            # Check network bottleneck
            if self.metrics.network_utilization > self.config.alert_threshold:
                self.metrics.network_alert = True
                bottlenecks.append({
                    'resource': 'network',
                    'utilization': self.metrics.network_utilization,
                    'threshold': self.config.alert_threshold,
                    'severity': 'high'
                })
            else:
                self.metrics.network_alert = False
            
            # Update bottleneck history
            if bottlenecks:
                self.bottleneck_detected = True
                self.metrics.bottleneck_history.extend(bottlenecks)
                print(f"⚠️  Resource bottlenecks detected: {len(bottlenecks)}")
                
                # Trigger immediate optimization if severe
                if any(b['severity'] == 'high' for b in bottlenecks):
                    await self._trigger_immediate_optimization()
            else:
                self.bottleneck_detected = False
            
        except Exception as e:
            print(f"⚠️  Bottleneck check failed: {e}")
    
    async def _trigger_immediate_optimization(self):
        """Trigger immediate resource optimization"""
        try:
            if not self.is_optimizing:
                print("🚨 Triggering immediate resource optimization due to bottlenecks")
                await self._run_resource_optimization()
            
        except Exception as e:
            print(f"❌ Immediate optimization trigger failed: {e}")
    
    async def _update_resource_history(self):
        """Update resource utilization history"""
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'cpu_utilization': self.metrics.cpu_utilization,
                'memory_utilization': self.metrics.memory_utilization,
                'gpu_utilization': self.metrics.gpu_utilization,
                'network_utilization': self.metrics.network_utilization,
                'bottleneck_detected': self.bottleneck_detected
            }
            
            self.metrics.resource_history.append(history_entry)
            
            # Keep only recent history (last 100 entries)
            if len(self.metrics.resource_history) > 100:
                self.metrics.resource_history = self.metrics.resource_history[-100:]
            
        except Exception as e:
            print(f"⚠️  Resource history update failed: {e}")
    
    async def _run_resource_optimization(self) -> Dict[str, Any]:
        """Run resource optimization process"""
        try:
            print("🔄 Running resource optimization...")
            
            optimization_results = {
                'cpu_optimizations': [],
                'memory_optimizations': [],
                'gpu_optimizations': [],
                'network_optimizations': [],
                'overall_improvements': []
            }
            
            # CPU optimization
            if self.config.cpu_optimization:
                cpu_results = await self._optimize_cpu_resources()
                optimization_results['cpu_optimizations'] = cpu_results
            
            # Memory optimization
            if self.config.memory_optimization:
                memory_results = await self._optimize_memory_resources()
                optimization_results['memory_optimizations'] = memory_results
            
            # GPU optimization
            if self.config.gpu_optimization:
                gpu_results = await self._optimize_gpu_resources()
                optimization_results['gpu_optimizations'] = gpu_results
            
            # Network optimization
            if self.config.network_optimization:
                network_results = await self._optimize_network_resources()
                optimization_results['network_optimizations'] = network_results
            
            # Calculate overall improvements
            overall_improvement = await self._calculate_overall_improvement(optimization_results)
            optimization_results['overall_improvements'] = overall_improvement
            
            # Update optimization metrics
            self.metrics.optimization_count += 1
            self.metrics.performance_improvements += len(overall_improvement)
            
            # Record optimization history
            self.optimization_history.append({
                'session_id': self.current_session,
                'timestamp': datetime.now().isoformat(),
                'optimization_results': optimization_results,
                'metrics': self.metrics.__dict__
            })
            
            print("✅ Resource optimization completed")
            
            return optimization_results
            
        except Exception as e:
            print(f"❌ Resource optimization failed: {e}")
            return {'error': str(e)}
    
    async def _optimize_cpu_resources(self) -> List[Dict[str, Any]]:
        """Optimize CPU resource allocation"""
        try:
            optimizations = []
            
            # Check if CPU utilization is too high
            if self.metrics.cpu_utilization > self.config.cpu_utilization_target:
                # Reduce CPU allocation or redistribute load
                if self.config.cpu_load_balancing:
                    optimizations.append({
                        'type': 'load_balancing',
                        'description': 'Redistributing CPU load across cores',
                        'impact': 'medium',
                        'estimated_improvement': 0.1
                    })
                
                if self.config.cpu_affinity:
                    optimizations.append({
                        'type': 'cpu_affinity',
                        'description': 'Optimizing CPU affinity for better cache utilization',
                        'impact': 'low',
                        'estimated_improvement': 0.05
                    })
            
            # Check if CPU utilization is too low
            elif self.metrics.cpu_utilization < self.config.cpu_utilization_target * 0.5:
                # Increase CPU allocation
                optimizations.append({
                    'type': 'allocation_increase',
                    'description': 'Increasing CPU allocation for better performance',
                    'impact': 'medium',
                    'estimated_improvement': 0.15
                })
            
            return optimizations
            
        except Exception as e:
            print(f"⚠️  CPU optimization failed: {e}")
            return []
    
    async def _optimize_memory_resources(self) -> List[Dict[str, Any]]:
        """Optimize memory resource allocation"""
        try:
            optimizations = []
            
            # Check if memory utilization is too high
            if self.metrics.memory_utilization > self.config.memory_utilization_target:
                # Memory cleanup and optimization
                if self.config.garbage_collection:
                    optimizations.append({
                        'type': 'garbage_collection',
                        'description': 'Triggering garbage collection to free memory',
                        'impact': 'high',
                        'estimated_improvement': 0.2
                    })
                
                optimizations.append({
                    'type': 'memory_cleanup',
                    'description': 'Cleaning up unused memory allocations',
                    'impact': 'medium',
                    'estimated_improvement': 0.1
                })
            
            # Check if memory utilization is too low
            elif self.metrics.memory_utilization < self.config.memory_utilization_target * 0.5:
                # Increase memory allocation
                optimizations.append({
                    'type': 'allocation_increase',
                    'description': 'Increasing memory allocation for better performance',
                    'impact': 'medium',
                    'estimated_improvement': 0.1
                })
            
            return optimizations
            
        except Exception as e:
            print(f"⚠️  Memory optimization failed: {e}")
            return []
    
    async def _optimize_gpu_resources(self) -> List[Dict[str, Any]]:
        """Optimize GPU resource allocation"""
        try:
            optimizations = []
            
            # Check if GPU utilization is too high
            if self.metrics.gpu_utilization > self.config.gpu_utilization_target:
                # GPU optimization strategies
                if self.config.gpu_mixed_precision:
                    optimizations.append({
                        'type': 'mixed_precision',
                        'description': 'Enabling mixed precision for better GPU efficiency',
                        'impact': 'high',
                        'estimated_improvement': 0.25
                    })
                
                optimizations.append({
                    'type': 'memory_optimization',
                    'description': 'Optimizing GPU memory allocation',
                    'impact': 'medium',
                    'estimated_improvement': 0.15
                })
            
            # Check if GPU utilization is too low
            elif self.metrics.gpu_utilization < self.config.gpu_utilization_target * 0.5:
                # Increase GPU allocation
                optimizations.append({
                    'type': 'allocation_increase',
                    'description': 'Increasing GPU allocation for better performance',
                    'impact': 'medium',
                    'estimated_improvement': 0.2
                })
            
            return optimizations
            
        except Exception as e:
            print(f"⚠️  GPU optimization failed: {e}")
            return []
    
    async def _optimize_network_resources(self) -> List[Dict[str, Any]]:
        """Optimize network resource allocation"""
        try:
            optimizations = []
            
            # Check if network utilization is too high
            if self.metrics.network_utilization > 0.8:
                # Network optimization strategies
                if self.config.compression_enabled:
                    optimizations.append({
                        'type': 'compression',
                        'description': 'Enabling data compression to reduce network load',
                        'impact': 'medium',
                        'estimated_improvement': 0.2
                    })
                
                if self.config.connection_pooling:
                    optimizations.append({
                        'type': 'connection_pooling',
                        'description': 'Optimizing connection pooling for better network efficiency',
                        'impact': 'low',
                        'estimated_improvement': 0.1
                    })
            
            # Check if network utilization is too low
            elif self.metrics.network_utilization < 0.3:
                # Increase network allocation
                optimizations.append({
                    'type': 'allocation_increase',
                    'description': 'Increasing network allocation for better performance',
                    'impact': 'medium',
                    'estimated_improvement': 0.15
                })
            
            return optimizations
            
        except Exception as e:
            print(f"⚠️  Network optimization failed: {e}")
            return []
    
    async def _calculate_overall_improvement(self, optimization_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate overall improvement from optimizations"""
        try:
            improvements = []
            
            # Aggregate improvements from all resource types
            total_improvement = 0.0
            optimization_count = 0
            
            for resource_type, optimizations in optimization_results.items():
                if resource_type != 'overall_improvements':
                    for opt in optimizations:
                        total_improvement += opt.get('estimated_improvement', 0.0)
                        optimization_count += 1
            
            if optimization_count > 0:
                avg_improvement = total_improvement / optimization_count
                overall_score = min(avg_improvement, 1.0)
                
                improvements.append({
                    'type': 'overall_optimization',
                    'description': f'Overall resource optimization with {optimization_count} improvements',
                    'impact': 'high',
                    'estimated_improvement': overall_score,
                    'resource_count': optimization_count
                })
            
            return improvements
            
        except Exception as e:
            print(f"⚠️  Overall improvement calculation failed: {e}")
            return []
    
    async def _schedule_periodic_optimization(self):
        """Schedule periodic resource optimization"""
        try:
            print(f"⏰ Scheduling periodic optimization every {self.config.optimization_interval} seconds")
            
            # Schedule periodic optimization task
            asyncio.create_task(self._periodic_optimization_loop())
            
        except Exception as e:
            print(f"❌ Periodic optimization scheduling failed: {e}")
    
    async def _periodic_optimization_loop(self):
        """Periodic optimization loop"""
        try:
            while self.optimization_scheduled:
                await asyncio.sleep(self.config.optimization_interval)
                
                if not self.is_optimizing:
                    print("🔄 Running scheduled resource optimization...")
                    await self._run_resource_optimization()
                
        except Exception as e:
            print(f"❌ Periodic optimization loop failed: {e}")
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        try:
            return {
                'optimization_metrics': self.metrics.__dict__,
                'optimization_history': self.optimization_history,
                'current_config': self.config.__dict__,
                'resource_pools': self.resource_pools,
                'bottleneck_detected': self.bottleneck_detected
            }
            
        except Exception as e:
            print(f"❌ Optimization report generation failed: {e}")
            return {'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'ResourceOptimizer',
            'is_optimizing': self.is_optimizing,
            'current_session': self.current_session,
            'metrics': self.metrics.__dict__,
            'config': self.config.__dict__
        }
    
    async def stop_optimization(self):
        """Stop resource optimization and monitoring"""
        try:
            self.is_optimizing = False
            self.optimization_scheduled = False
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                self.monitoring_task = None
            
            print("🛑 Resource optimization stopped")
            
        except Exception as e:
            print(f"❌ Optimization stop failed: {e}")
    
    async def reset_optimizer(self):
        """Reset optimizer state and metrics"""
        await self.stop_optimization()
        
        self.current_session = None
        self.optimization_history.clear()
        self.metrics = ResourceMetrics()
        self.start_time = None
        self.resource_pools.clear()
        self.bottleneck_detected = False
        self.optimization_scheduled = False
        
        print("🔄 Resource Optimizer reset")
