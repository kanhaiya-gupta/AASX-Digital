"""
Solver Management Service for Physics Modeling
=============================================

Provides comprehensive solver management capabilities for physics modeling,
ensuring efficient solver optimization and resource management.

Features:
- Solver lifecycle management
- Solver optimization and tuning
- Resource allocation and monitoring
- Performance benchmarking
- Solver selection and routing
- Parallel processing management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import psutil
import threading
import os

# Import physics modeling components
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..models.physics_modeling_metrics import PhysicsModelingMetrics
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
from ..solvers.base_solver import BaseSolver

logger = logging.getLogger(__name__)


class SolverStatus(Enum):
    """Solver status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    OPTIMIZING = "optimizing"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class SolverType(Enum):
    """Solver type enumeration."""
    FINITE_ELEMENT = "finite_element"
    FINITE_DIFFERENCE = "finite_difference"
    FINITE_VOLUME = "finite_volume"
    SPECTRAL = "spectral"
    MESH_FREE = "mesh_free"
    MACHINE_LEARNING = "machine_learning"
    HYBRID = "hybrid"


class ResourceType(Enum):
    """Resource type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"


class SolverInstance:
    """Solver instance information."""
    
    def __init__(
        self,
        instance_id: str,
        solver_type: SolverType,
        solver_name: str,
        version: str,
        capabilities: List[str]
    ):
        self.instance_id = instance_id
        self.solver_type = solver_type
        self.solver_name = solver_name
        self.version = version
        self.capabilities = capabilities
        self.status = SolverStatus.IDLE
        self.current_task = None
        self.start_time = None
        self.resource_usage = {}
        self.performance_metrics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'average_execution_time': 0.0,
            'last_execution_time': None
        }


class SolverManagementService:
    """
    Comprehensive solver management service for physics modeling.
    
    Provides:
    - Solver lifecycle management
    - Solver optimization and tuning
    - Resource allocation and monitoring
    - Performance benchmarking
    - Solver selection and routing
    - Parallel processing management
    """

    def __init__(
        self,
        registry_repo: Optional[PhysicsModelingRegistryRepository] = None,
        metrics_repo: Optional[PhysicsModelingMetricsRepository] = None
    ):
        """Initialize the solver management service."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        
        # Initialize repositories if not provided
        if not self.registry_repo:
            from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
            self.registry_repo = PhysicsModelingRegistryRepository()
        
        if not self.metrics_repo:
            from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
            self.metrics_repo = PhysicsModelingMetricsRepository()
        
        # Solver management
        self.solver_instances: Dict[str, SolverInstance] = {}
        self.solver_queue: List[Dict[str, Any]] = []
        self.active_solvers: Dict[str, SolverInstance] = {}
        self.solver_performance: Dict[str, Dict[str, Any]] = {}
        
        # Resource management
        self.resource_monitors: Dict[ResourceType, Dict[str, Any]] = {}
        self.resource_limits = {
            ResourceType.CPU: 80.0,      # 80% CPU usage limit
            ResourceType.MEMORY: 85.0,   # 85% memory usage limit
            ResourceType.GPU: 90.0,      # 90% GPU usage limit
            ResourceType.STORAGE: 95.0   # 95% storage usage limit
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_solver_requests': 0,
            'successful_solver_requests': 0,
            'failed_solver_requests': 0,
            'average_solver_execution_time': 0.0,
            'total_optimizations': 0
        }
        
        logger.info("Solver management service initialized")

    async def initialize(self) -> bool:
        """Initialize the solver management service."""
        try:
            # Initialize repositories
            await self.registry_repo.initialize()
            await self.metrics_repo.initialize()
            
            # Initialize resource monitoring
            await self._initialize_resource_monitoring()
            
            # Discover available solvers
            await self.discover_solvers()
            
            logger.info("✅ Solver management service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize solver management service: {e}")
            return False

    async def discover_solvers(self) -> List[str]:
        """
        Discover available solvers in the system.
        
        Returns:
            List of discovered solver IDs
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            discovered_solvers = []
            
            # Discover solvers from different sources
            solvers = await self._discover_solver_modules()
            discovered_solvers.extend(solvers)
            
            # Discover external solver services
            external_solvers = await self._discover_external_solvers()
            discovered_solvers.extend(external_solvers)
            
            logger.info(f"✅ Discovered {len(discovered_solvers)} solvers")
            return discovered_solvers
            
        except Exception as e:
            logger.error(f"Failed to discover solvers: {e}")
            return []

    async def register_solver(
        self,
        solver_type: SolverType,
        solver_name: str,
        version: str,
        capabilities: List[str],
        solver_class: Optional[type] = None
    ) -> str:
        """
        Register a new solver in the system.
        
        Args:
            solver_type: Type of solver
            solver_name: Name of the solver
            version: Solver version
            capabilities: List of solver capabilities
            solver_class: Solver class (optional)
            
        Returns:
            Solver instance ID
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Generate solver instance ID
            instance_id = f"{solver_type.value}_{solver_name}_{version}".replace('.', '_').replace('-', '_')
            
            # Check if solver already exists
            if instance_id in self.solver_instances:
                logger.warning(f"Solver {instance_id} already registered")
                return instance_id
            
            # Create solver instance
            solver_instance = SolverInstance(
                instance_id=instance_id,
                solver_type=solver_type,
                solver_name=solver_name,
                version=version,
                capabilities=capabilities
            )
            
            # Register solver
            self.solver_instances[instance_id] = solver_instance
            
            # Initialize performance tracking
            self.solver_performance[instance_id] = {
                'execution_times': [],
                'resource_usage_history': [],
                'optimization_history': [],
                'last_optimization': None
            }
            
            # Create registry record
            await self._create_solver_registry_record(solver_instance)
            
            logger.info(f"✅ Solver {solver_name} registered successfully")
            return instance_id
            
        except Exception as e:
            logger.error(f"Failed to register solver {solver_name}: {e}")
            raise

    async def start_solver(
        self,
        solver_id: str,
        task_config: Dict[str, Any],
        priority: int = 0
    ) -> str:
        """
        Start a solver with a specific task.
        
        Args:
            solver_id: Solver identifier
            task_config: Task configuration
            priority: Task priority
            
        Returns:
            Task ID
        """
        try:
            if solver_id not in self.solver_instances:
                raise ValueError(f"Solver {solver_id} not found")
            
            solver_instance = self.solver_instances[solver_id]
            
            # Check solver availability
            if solver_instance.status != SolverStatus.IDLE:
                raise ValueError(f"Solver {solver_id} is not available (status: {solver_instance.status.value})")
            
            # Check resource availability
            if not await self._check_resource_availability(task_config):
                raise ValueError("Insufficient resources for solver task")
            
            # Generate task ID
            task_id = f"task_{int(datetime.now().timestamp())}_{solver_id}"
            
            # Create task
            task = {
                'task_id': task_id,
                'solver_id': solver_id,
                'config': task_config,
                'priority': priority,
                'status': 'pending',
                'created_at': datetime.now(),
                'started_at': None,
                'completed_at': None,
                'result': None,
                'error': None
            }
            
            # Add to queue
            self.solver_queue.append(task)
            self.solver_queue.sort(key=lambda x: x['priority'], reverse=True)
            
            # Update solver status
            solver_instance.status = SolverStatus.RUNNING
            solver_instance.current_task = task_id
            solver_instance.start_time = datetime.now()
            
            # Add to active solvers
            self.active_solvers[task_id] = solver_instance
            
            # Update performance metrics
            self.performance_metrics['total_solver_requests'] += 1
            
            logger.info(f"✅ Solver {solver_instance.solver_name} started with task {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to start solver {solver_id}: {e}")
            raise

    async def stop_solver(self, task_id: str) -> bool:
        """
        Stop a running solver task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if solver stopped successfully, False otherwise
        """
        try:
            if task_id not in self.active_solvers:
                logger.warning(f"Task {task_id} not found in active solvers")
                return False
            
            solver_instance = self.active_solvers[task_id]
            
            # Stop solver (simplified for demo)
            await asyncio.sleep(0.05)  # Simulate stopping time
            
            # Update solver status
            solver_instance.status = SolverStatus.IDLE
            solver_instance.current_task = None
            solver_instance.start_time = None
            
            # Remove from active solvers
            del self.active_solvers[task_id]
            
            # Update task status
            task = next((t for t in self.solver_queue if t['task_id'] == task_id), None)
            if task:
                task['status'] = 'stopped'
                task['completed_at'] = datetime.now()
            
            logger.info(f"✅ Solver {solver_instance.solver_name} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop solver for task {task_id}: {e}")
            return False

    async def get_solver_status(self, solver_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a solver.
        
        Args:
            solver_id: Solver identifier
            
        Returns:
            Solver status information or None if not found
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            if solver_id not in self.solver_instances:
                return None
            
            solver_instance = self.solver_instances[solver_id]
            performance = self.solver_performance.get(solver_id, {})
            
            status = {
                'solver_id': solver_id,
                'solver_name': solver_instance.solver_name,
                'solver_type': solver_instance.solver_type.value,
                'version': solver_instance.version,
                'status': solver_instance.status.value,
                'current_task': solver_instance.current_task,
                'start_time': solver_instance.start_time.isoformat() if solver_instance.start_time else None,
                'capabilities': solver_instance.capabilities,
                'resource_usage': solver_instance.resource_usage,
                'performance_metrics': solver_instance.performance_metrics,
                'performance_history': performance
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get solver status for {solver_id}: {e}")
            return None

    async def optimize_solver(
        self,
        solver_id: str,
        optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize a solver for better performance.
        
        Args:
            solver_id: Solver identifier
            optimization_config: Optimization configuration
            
        Returns:
            Optimization results
        """
        try:
            if solver_id not in self.solver_instances:
                raise ValueError(f"Solver {solver_id} not found")
            
            solver_instance = self.solver_instances[solver_id]
            solver_instance.status = SolverStatus.OPTIMIZING
            
            # Perform optimization (simplified for demo)
            optimization_results = await self._perform_solver_optimization(
                solver_id, optimization_config
            )
            
            # Update solver status
            solver_instance.status = SolverStatus.IDLE
            
            # Record optimization
            self.performance_metrics['total_optimizations'] += 1
            
            # Update performance history
            if solver_id in self.solver_performance:
                self.solver_performance[solver_id]['last_optimization'] = datetime.now()
                self.solver_performance[solver_id]['optimization_history'].append(optimization_results)
            
            logger.info(f"✅ Solver {solver_instance.solver_name} optimized successfully")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to optimize solver {solver_id}: {e}")
            if solver_id in self.solver_instances:
                self.solver_instances[solver_id].status = SolverStatus.ERROR
            raise

    async def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get current resource usage information.
        
        Returns:
            Resource usage information
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            resource_usage = {}
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            resource_usage['cpu'] = {
                'current_usage': cpu_percent,
                'limit': self.resource_limits[ResourceType.CPU],
                'available': 100.0 - cpu_percent,
                'status': 'normal' if cpu_percent < self.resource_limits[ResourceType.CPU] else 'warning'
            }
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            resource_usage['memory'] = {
                'current_usage': memory_percent,
                'limit': self.resource_limits[ResourceType.MEMORY],
                'available': 100.0 - memory_percent,
                'total_gb': round(memory.total / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'status': 'normal' if memory_percent < self.resource_limits[ResourceType.MEMORY] else 'warning'
            }
            
            # Storage usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            resource_usage['storage'] = {
                'current_usage': round(disk_percent, 2),
                'limit': self.resource_limits[ResourceType.STORAGE],
                'available': round(100.0 - disk_percent, 2),
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'status': 'normal' if disk_percent < self.resource_limits[ResourceType.STORAGE] else 'warning'
            }
            
            # GPU usage (simplified)
            resource_usage['gpu'] = {
                'current_usage': 0.0,  # Would use nvidia-ml-py in real implementation
                'limit': self.resource_limits[ResourceType.GPU],
                'available': 100.0,
                'status': 'normal'
            }
            
            return resource_usage
            
        except Exception as e:
            logger.error(f"Failed to get resource usage: {e}")
            return {}

    async def select_optimal_solver(
        self,
        requirements: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Select the optimal solver for given requirements.
        
        Args:
            requirements: Solver requirements
            constraints: Additional constraints
            
        Returns:
            Optimal solver ID or None if no suitable solver found
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            suitable_solvers = []
            
            for solver_id, solver_instance in self.solver_instances.items():
                if solver_instance.status != SolverStatus.IDLE:
                    continue
                
                # Check if solver meets requirements
                if await self._solver_meets_requirements(solver_instance, requirements):
                    # Calculate solver score
                    score = await self._calculate_solver_score(solver_instance, requirements, constraints)
                    suitable_solvers.append((solver_id, score))
            
            if not suitable_solvers:
                return None
            
            # Sort by score (highest first) and return the best
            suitable_solvers.sort(key=lambda x: x[1], reverse=True)
            optimal_solver_id = suitable_solvers[0][0]
            
            logger.info(f"✅ Selected optimal solver: {optimal_solver_id}")
            return optimal_solver_id
            
        except Exception as e:
            logger.error(f"Failed to select optimal solver: {e}")
            return None

    async def get_solver_performance_metrics(self, solver_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a solver.
        
        Args:
            solver_id: Solver identifier
            
        Returns:
            Performance metrics
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            if solver_id not in self.solver_instances:
                return {}
            
            solver_instance = self.solver_instances[solver_id]
            performance = self.solver_performance.get(solver_id, {})
            
            metrics = {
                'solver_id': solver_id,
                'solver_name': solver_instance.solver_name,
                'solver_type': solver_instance.solver_type.value,
                'status': solver_instance.status.value,
                'total_tasks': solver_instance.performance_metrics['total_tasks'],
                'successful_tasks': solver_instance.performance_metrics['successful_tasks'],
                'failed_tasks': solver_instance.performance_metrics['failed_tasks'],
                'success_rate': (
                    (solver_instance.performance_metrics['successful_tasks'] / 
                     max(solver_instance.performance_metrics['total_tasks'], 1)) * 100
                ),
                'average_execution_time': solver_instance.performance_metrics['average_execution_time'],
                'last_execution_time': solver_instance.performance_metrics['last_execution_time'],
                'execution_times': performance.get('execution_times', []),
                'resource_usage_history': performance.get('resource_usage_history', []),
                'optimization_history': performance.get('optimization_history', [])
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics for {solver_id}: {e}")
            return {}

    async def _initialize_resource_monitoring(self) -> None:
        """Initialize resource monitoring."""
        try:
            # Initialize resource monitors
            for resource_type in ResourceType:
                self.resource_monitors[resource_type] = {
                    'current_usage': 0.0,
                    'peak_usage': 0.0,
                    'average_usage': 0.0,
                    'usage_history': [],
                    'last_updated': datetime.now()
                }
            
            logger.info("✅ Resource monitoring initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize resource monitoring: {e}")

    async def _discover_solver_modules(self) -> List[str]:
        """Discover solver modules in the system."""
        try:
            discovered_solvers = []
            
            # Discover solvers from the solvers directory
            solvers_dir = "src/modules/physics_modeling/solvers"
            if os.path.exists(solvers_dir):
                for file in os.listdir(solvers_dir):
                    if file.endswith('.py') and not file.startswith('__'):
                        solver_name = file.replace('.py', '')
                        
                        # Determine solver type
                        if 'finite_element' in solver_name.lower():
                            solver_type = SolverType.FINITE_ELEMENT
                        elif 'finite_difference' in solver_name.lower():
                            solver_type = SolverType.FINITE_DIFFERENCE
                        elif 'finite_volume' in solver_name.lower():
                            solver_type = SolverType.FINITE_VOLUME
                        else:
                            solver_type = SolverType.HYBRID
                        
                        # Register solver
                        solver_id = await self.register_solver(
                            solver_type=solver_type,
                            solver_name=solver_name,
                            version="1.0.0",
                            capabilities=[solver_type.value, "physics_modeling"]
                        )
                        discovered_solvers.append(solver_id)
            
            return discovered_solvers
            
        except Exception as e:
            logger.error(f"Failed to discover solver modules: {e}")
            return []

    async def _discover_external_solvers(self) -> List[str]:
        """Discover external solver services."""
        try:
            # In a real implementation, this would discover external solver services
            # For demo purposes, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to discover external solvers: {e}")
            return []

    async def _check_resource_availability(self, task_config: Dict[str, Any]) -> bool:
        """Check if sufficient resources are available for a task."""
        try:
            # Get current resource usage
            resource_usage = await self.get_resource_usage()
            
            # Check CPU availability
            if resource_usage.get('cpu', {}).get('current_usage', 0) > 90:
                return False
            
            # Check memory availability
            if resource_usage.get('memory', {}).get('current_usage', 0) > 90:
                return False
            
            # Check storage availability
            if resource_usage.get('storage', {}).get('current_usage', 0) > 95:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check resource availability: {e}")
            return False

    async def _solver_meets_requirements(
        self,
        solver_instance: SolverInstance,
        requirements: Dict[str, Any]
    ) -> bool:
        """Check if a solver meets the given requirements."""
        try:
            # Check solver type
            if 'solver_type' in requirements:
                if solver_instance.solver_type.value != requirements['solver_type']:
                    return False
            
            # Check capabilities
            if 'capabilities' in requirements:
                required_capabilities = requirements['capabilities']
                if not all(cap in solver_instance.capabilities for cap in required_capabilities):
                    return False
            
            # Check solver status
            if solver_instance.status != SolverStatus.IDLE:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check solver requirements: {e}")
            return False

    async def _calculate_solver_score(
        self,
        solver_instance: SolverInstance,
        requirements: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate a score for a solver based on requirements and constraints."""
        try:
            score = 0.0
            
            # Base score
            score += 50.0
            
            # Performance score
            performance = solver_instance.performance_metrics
            if performance['total_tasks'] > 0:
                success_rate = performance['successful_tasks'] / performance['total_tasks']
                score += success_rate * 20.0
            
            # Execution time score (lower is better)
            if performance['average_execution_time'] > 0:
                time_score = max(0, 20.0 - (performance['average_execution_time'] / 10.0))
                score += time_score
            
            # Capability match score
            if 'capabilities' in requirements:
                required_caps = requirements['capabilities']
                matched_caps = sum(1 for cap in required_caps if cap in solver_instance.capabilities)
                capability_score = (matched_caps / len(required_caps)) * 10.0
                score += capability_score
            
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate solver score: {e}")
            return 0.0

    async def _perform_solver_optimization(
        self,
        solver_id: str,
        optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform solver optimization."""
        try:
            # Simulate optimization process
            await asyncio.sleep(0.2)  # Simulate optimization time
            
            optimization_results = {
                'solver_id': solver_id,
                'optimization_timestamp': datetime.now().isoformat(),
                'optimization_type': optimization_config.get('type', 'general'),
                'parameters_optimized': [
                    'memory_allocation',
                    'algorithm_parameters',
                    'cache_settings',
                    'parallel_processing'
                ],
                'performance_improvement': 15.5,  # Simulated improvement percentage
                'optimization_duration': 0.2,
                'status': 'completed'
            }
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Failed to perform solver optimization: {e}")
            raise

    async def _create_solver_registry_record(self, solver_instance: SolverInstance) -> None:
        """Create a record in the physics modeling registry."""
        try:
            # Create registry record
            registry_record = PhysicsModelingRegistry(
                registry_id=None,  # Will be set by repository
                twin_registry_id=None,  # Not applicable for solvers
                model_name=f"solver_{solver_instance.solver_name}",
                model_type="solver",
                model_version=solver_instance.version,
                model_description=f"Solver: {solver_instance.solver_name}",
                model_status="active",
                model_parameters=json.dumps({
                    'solver_type': solver_instance.solver_type.value,
                    'capabilities': solver_instance.capabilities,
                    'version': solver_instance.version
                }),
                model_metadata={
                    'instance_id': solver_instance.instance_id,
                    'solver_type': solver_instance.solver_type.value,
                    'capabilities': solver_instance.capabilities,
                    'created_at': datetime.now().isoformat()
                },
                compliance_score=80.0,  # Default compliance score
                security_score=75.0,   # Default security score
                quality_score=70.0,    # Default quality score
                performance_score=65.0, # Default performance score
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to database
            await self.registry_repo.create(registry_record)
            
        except Exception as e:
            logger.error(f"Failed to create solver registry record: {e}")

    async def close(self) -> None:
        """Close the solver management service."""
        try:
            # Stop all active solvers
            for task_id in list(self.active_solvers.keys()):
                await self.stop_solver(task_id)
            
            if self.registry_repo:
                await self.registry_repo.close()
            if self.metrics_repo:
                await self.metrics_repo.close()
            
            logger.info("✅ Solver management service closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing solver management service: {e}")





