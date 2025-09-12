"""
Simulation Management Service for Physics Modeling
=================================================

Provides comprehensive simulation management capabilities for physics modeling,
integrating with existing simulation components and the new engine infrastructure.

Features:
- Simulation lifecycle management
- Simulation scheduling and queuing
- Performance monitoring and optimization
- Integration with twin registry and plugins
- Enterprise-grade simulation analytics
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import json

# Import physics modeling components
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..models.physics_modeling_metrics import PhysicsModelingMetrics
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
from ..core.plugin_manager import PluginManager
from ..simulation.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)


class SimulationStatus(Enum):
    """Simulation status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SimulationPriority(Enum):
    """Simulation priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class SimulationType(Enum):
    """Simulation type enumeration."""
    STRUCTURAL = "structural"
    THERMAL = "thermal"
    FLUID_DYNAMICS = "fluid_dynamics"
    MULTI_PHYSICS = "multi_physics"
    ML_PHYSICS = "ml_physics"
    OPTIMIZATION = "optimization"


class SimulationRequest:
    """Simulation request data structure."""
    
    def __init__(
        self,
        request_id: str,
        twin_id: str,
        plugin_id: str,
        simulation_type: SimulationType,
        parameters: Dict[str, Any],
        priority: SimulationPriority = SimulationPriority.NORMAL,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None
    ):
        self.request_id = request_id
        self.twin_id = twin_id
        self.plugin_id = plugin_id
        self.simulation_type = simulation_type
        self.parameters = parameters
        self.priority = priority
        self.user_id = user_id
        self.org_id = org_id
        self.created_at = datetime.now()
        self.status = SimulationStatus.PENDING
        self.estimated_duration = None
        self.actual_duration = None
        self.results = None
        self.error_message = None


class SimulationManagementService:
    """
    Comprehensive simulation management service for physics modeling.
    
    Provides:
    - Simulation lifecycle management
    - Queue management and scheduling
    - Performance monitoring and optimization
    - Integration with twin registry and plugins
    - Enterprise-grade simulation analytics
    """

    def __init__(
        self,
        registry_repo: Optional[PhysicsModelingRegistryRepository] = None,
        metrics_repo: Optional[PhysicsModelingMetricsRepository] = None,
        plugin_manager: Optional[PluginManager] = None,
        simulation_engine: Optional[SimulationEngine] = None
    ):
        """Initialize the simulation management service."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        self.plugin_manager = plugin_manager
        self.simulation_engine = simulation_engine
        
        # Initialize repositories if not provided
        if not self.registry_repo:
            from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
            self.registry_repo = PhysicsModelingRegistryRepository()
        
        if not self.metrics_repo:
            from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
            self.metrics_repo = PhysicsModelingMetricsRepository()
        
        # Simulation queue and management
        self.simulation_queue: List[SimulationRequest] = []
        self.active_simulations: Dict[str, SimulationRequest] = {}
        self.completed_simulations: Dict[str, SimulationRequest] = {}
        self.failed_simulations: Dict[str, SimulationRequest] = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_simulations': 0,
            'successful_simulations': 0,
            'failed_simulations': 0,
            'average_execution_time': 0.0,
            'queue_length': 0,
            'active_simulations': 0
        }
        
        logger.info("Simulation management service initialized")

    async def initialize(self) -> bool:
        """Initialize the simulation management service."""
        try:
            # Initialize repositories
            await self.registry_repo.initialize()
            await self.metrics_repo.initialize()
            
            # Initialize simulation engine if provided
            if self.simulation_engine:
                await self.simulation_engine.initialize()
            
            logger.info("✅ Simulation management service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize simulation management service: {e}")
            return False

    async def submit_simulation(
        self,
        twin_id: str,
        plugin_id: str,
        simulation_type: SimulationType,
        parameters: Dict[str, Any],
        priority: SimulationPriority = SimulationPriority.NORMAL,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> str:
        """
        Submit a new simulation request.
        
        Args:
            twin_id: Digital twin ID
            plugin_id: Plugin ID to use
            simulation_type: Type of simulation
            parameters: Simulation parameters
            priority: Simulation priority
            user_id: User ID (optional)
            org_id: Organization ID (optional)
            
        Returns:
            Simulation request ID
        """
        try:
            # Generate unique request ID
            request_id = f"sim_req_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Create simulation request
            request = SimulationRequest(
                request_id=request_id,
                twin_id=twin_id,
                plugin_id=plugin_id,
                simulation_type=simulation_type,
                parameters=parameters,
                priority=priority,
                user_id=user_id,
                org_id=org_id
            )
            
            # Add to queue
            self.simulation_queue.append(request)
            self.simulation_queue.sort(key=lambda x: x.priority.value, reverse=True)
            
            # Update performance metrics
            self.performance_metrics['queue_length'] = len(self.simulation_queue)
            self.performance_metrics['total_simulations'] += 1
            
            # Create registry record
            await self._create_simulation_registry_record(request)
            
            logger.info(f"✅ Simulation request {request_id} submitted successfully")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to submit simulation request: {e}")
            raise

    async def start_simulation(self, request_id: str) -> bool:
        """
        Start a simulation from the queue.
        
        Args:
            request_id: Simulation request ID
            
        Returns:
            True if simulation started successfully, False otherwise
        """
        try:
            # Find request in queue
            request = next((req for req in self.simulation_queue if req.request_id == request_id), None)
            if not request:
                logger.warning(f"Simulation request {request_id} not found in queue")
                return False
            
            # Remove from queue
            self.simulation_queue.remove(request)
            
            # Update status
            request.status = SimulationStatus.RUNNING
            request.estimated_duration = await self._estimate_simulation_duration(request)
            
            # Add to active simulations
            self.active_simulations[request_id] = request
            
            # Update performance metrics
            self.performance_metrics['queue_length'] = len(self.simulation_queue)
            self.performance_metrics['active_simulations'] = len(self.active_simulations)
            
            # Start actual simulation
            await self._execute_simulation(request)
            
            logger.info(f"✅ Simulation {request_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start simulation {request_id}: {e}")
            return False

    async def cancel_simulation(self, request_id: str) -> bool:
        """
        Cancel a running or queued simulation.
        
        Args:
            request_id: Simulation request ID
            
        Returns:
            True if simulation cancelled successfully, False otherwise
        """
        try:
            # Check active simulations
            if request_id in self.active_simulations:
                request = self.active_simulations[request_id]
                request.status = SimulationStatus.CANCELLED
                del self.active_simulations[request_id]
                
                # Add to completed simulations
                self.completed_simulations[request_id] = request
                
                # Update performance metrics
                self.performance_metrics['active_simulations'] = len(self.active_simulations)
                
                logger.info(f"✅ Simulation {request_id} cancelled successfully")
                return True
            
            # Check queue
            request = next((req for req in self.simulation_queue if req.request_id == request_id), None)
            if request:
                request.status = SimulationStatus.CANCELLED
                self.simulation_queue.remove(request)
                
                # Add to completed simulations
                self.completed_simulations[request_id] = request
                
                # Update performance metrics
                self.performance_metrics['queue_length'] = len(self.simulation_queue)
                
                logger.info(f"✅ Queued simulation {request_id} cancelled successfully")
                return True
            
            logger.warning(f"Simulation request {request_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel simulation {request_id}: {e}")
            return False

    async def get_simulation_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a simulation request.
        
        Args:
            request_id: Simulation request ID
            
        Returns:
            Simulation status information or None if not found
        """
        try:
            # Check active simulations
            if request_id in self.active_simulations:
                request = self.active_simulations[request_id]
                return self._format_simulation_status(request)
            
            # Check queue
            request = next((req for req in self.simulation_queue if req.request_id == request_id), None)
            if request:
                return self._format_simulation_status(request)
            
            # Check completed simulations
            if request_id in self.completed_simulations:
                request = self.completed_simulations[request_id]
                return self._format_simulation_status(request)
            
            # Check failed simulations
            if request_id in self.failed_simulations:
                request = self.failed_simulations[request_id]
                return self._format_simulation_status(request)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get simulation status for {request_id}: {e}")
            return None

    async def get_queue_status(self) -> Dict[str, Any]:
        """
        Get the current status of the simulation queue.
        
        Returns:
            Queue status information
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            queue_info = {
                'queue_length': len(self.simulation_queue),
                'active_simulations': len(self.active_simulations),
                'completed_simulations': len(self.completed_simulations),
                'failed_simulations': len(self.failed_simulations),
                'total_simulations': self.performance_metrics['total_simulations'],
                'successful_simulations': self.performance_metrics['successful_simulations'],
                'failed_simulations': self.performance_metrics['failed_simulations'],
                'average_execution_time': self.performance_metrics['average_execution_time']
            }
            
            # Add queue details
            if self.simulation_queue:
                queue_info['queued_simulations'] = [
                    {
                        'request_id': req.request_id,
                        'twin_id': req.twin_id,
                        'plugin_id': req.plugin_id,
                        'simulation_type': req.simulation_type.value,
                        'priority': req.priority.value,
                        'created_at': req.created_at.isoformat()
                    }
                    for req in self.simulation_queue[:10]  # Show first 10
                ]
            
            return queue_info
            
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {}

    async def get_performance_analytics(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        Get performance analytics for simulations.
        
        Args:
            time_range: Time range for analytics (24h, 7d, 30d, all)
            
        Returns:
            Performance analytics data
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Calculate time filter
            now = datetime.now()
            if time_range == "24h":
                start_time = now - timedelta(hours=24)
            elif time_range == "7d":
                start_time = now - timedelta(days=7)
            elif time_range == "30d":
                start_time = now - timedelta(days=30)
            else:
                start_time = datetime.min
            
            # Get metrics from database
            metrics = await self.metrics_repo.get_by_time_range(start_time, now)
            
            # Calculate analytics
            analytics = {
                'time_range': time_range,
                'total_simulations': len(metrics),
                'success_rate': 0.0,
                'average_execution_time': 0.0,
                'simulation_types': {},
                'performance_trends': {},
                'error_analysis': {}
            }
            
            if metrics:
                # Calculate success rate
                successful = len([m for m in metrics if m.metric_type != "error"])
                analytics['success_rate'] = (successful / len(metrics)) * 100
                
                # Calculate average execution time
                execution_times = [m.metric_value for m in metrics if m.metric_name == "simulation_execution"]
                if execution_times:
                    analytics['average_execution_time'] = sum(execution_times) / len(execution_times)
                
                # Analyze simulation types
                for metric in metrics:
                    sim_type = metric.metric_metadata.get('simulation_type', 'unknown')
                    if sim_type not in analytics['simulation_types']:
                        analytics['simulation_types'][sim_type] = 0
                    analytics['simulation_types'][sim_type] += 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {}

    async def _create_simulation_registry_record(self, request: SimulationRequest) -> None:
        """Create a record in the physics modeling registry."""
        try:
            # Create registry record
            registry_record = PhysicsModelingRegistry(
                registry_id=None,  # Will be set by repository
                twin_registry_id=request.twin_id,
                model_name=f"simulation_{request.simulation_type.value}",
                model_type=request.simulation_type.value,
                model_version="1.0.0",
                model_description=f"Simulation request {request.request_id}",
                model_status="pending",
                model_parameters=json.dumps(request.parameters),
                model_metadata={
                    'request_id': request.request_id,
                    'plugin_id': request.plugin_id,
                    'priority': request.priority.value,
                    'user_id': request.user_id,
                    'org_id': request.org_id,
                    'created_at': request.created_at.isoformat()
                },
                compliance_score=85.0,  # Default compliance score
                security_score=90.0,   # Default security score
                quality_score=80.0,    # Default quality score
                performance_score=75.0, # Default performance score
                created_at=request.created_at,
                updated_at=request.created_at
            )
            
            # Save to database
            await self.registry_repo.create(registry_record)
            
        except Exception as e:
            logger.error(f"Failed to create simulation registry record: {e}")

    async def _estimate_simulation_duration(self, request: SimulationRequest) -> float:
        """Estimate simulation duration based on type and parameters."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Base duration estimates (in seconds)
            base_durations = {
                SimulationType.STRUCTURAL: 300,      # 5 minutes
                SimulationType.THERMAL: 240,         # 4 minutes
                SimulationType.FLUID_DYNAMICS: 600,  # 10 minutes
                SimulationType.MULTI_PHYSICS: 900,   # 15 minutes
                SimulationType.ML_PHYSICS: 180,      # 3 minutes
                SimulationType.OPTIMIZATION: 1200    # 20 minutes
            }
            
            base_duration = base_durations.get(request.simulation_type, 300)
            
            # Adjust based on parameters complexity
            complexity_factor = 1.0
            if 'mesh_size' in request.parameters:
                mesh_size = request.parameters['mesh_size']
                if mesh_size > 1000000:  # 1M elements
                    complexity_factor *= 2.0
                elif mesh_size > 100000:  # 100K elements
                    complexity_factor *= 1.5
            
            if 'time_steps' in request.parameters:
                time_steps = request.parameters['time_steps']
                if time_steps > 1000:
                    complexity_factor *= 1.3
            
            estimated_duration = base_duration * complexity_factor
            
            return estimated_duration
            
        except Exception as e:
            logger.error(f"Failed to estimate simulation duration: {e}")
            return 300.0  # Default 5 minutes

    async def _execute_simulation(self, request: SimulationRequest) -> None:
        """Execute the actual simulation."""
        try:
            if not self.simulation_engine:
                logger.error("Simulation engine not available")
                request.status = SimulationStatus.FAILED
                request.error_message = "Simulation engine not available"
                return
            
            # Execute simulation
            start_time = datetime.now()
            results = await self.simulation_engine.run_simulation_with_plugin(
                twin_id=request.twin_id,
                plugin_id=request.plugin_id,
                simulation_params=request.parameters
            )
            end_time = datetime.now()
            
            # Update request with results
            request.actual_duration = (end_time - start_time).total_seconds()
            request.results = results
            request.status = SimulationStatus.COMPLETED
            
            # Move to completed simulations
            del self.active_simulations[request.request_id]
            self.completed_simulations[request.request_id] = request
            
            # Update performance metrics
            self.performance_metrics['active_simulations'] = len(self.active_simulations)
            self.performance_metrics['successful_simulations'] += 1
            
            # Update average execution time
            total_time = self.performance_metrics['average_execution_time'] * (self.performance_metrics['successful_simulations'] - 1)
            total_time += request.actual_duration
            self.performance_metrics['average_execution_time'] = total_time / self.performance_metrics['successful_simulations']
            
            logger.info(f"✅ Simulation {request.request_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Simulation {request.request_id} failed: {e}")
            request.status = SimulationStatus.FAILED
            request.error_message = str(e)
            
            # Move to failed simulations
            if request.request_id in self.active_simulations:
                del self.active_simulations[request.request_id]
            self.failed_simulations[request.request_id] = request
            
            # Update performance metrics
            self.performance_metrics['active_simulations'] = len(self.active_simulations)
            self.performance_metrics['failed_simulations'] += 1

    def _format_simulation_status(self, request: SimulationRequest) -> Dict[str, Any]:
        """Format simulation status for response."""
        return {
            'request_id': request.request_id,
            'twin_id': request.twin_id,
            'plugin_id': request.plugin_id,
            'simulation_type': request.simulation_type.value,
            'priority': request.priority.value,
            'status': request.status.value,
            'created_at': request.created_at.isoformat(),
            'estimated_duration': request.estimated_duration,
            'actual_duration': request.actual_duration,
            'user_id': request.user_id,
            'org_id': request.org_id,
            'error_message': request.error_message
        }

    async def close(self) -> None:
        """Close the simulation management service."""
        try:
            if self.registry_repo:
                await self.registry_repo.close()
            if self.metrics_repo:
                await self.metrics_repo.close()
            if self.simulation_engine:
                await self.simulation_engine.close()
            
            logger.info("✅ Simulation management service closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing simulation management service: {e}")





