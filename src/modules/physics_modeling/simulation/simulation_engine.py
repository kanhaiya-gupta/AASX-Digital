"""
Simulation Engine for Physics Modeling
=====================================

Provides comprehensive simulation orchestration for physics modeling,
integrating with the new src/engine infrastructure and twin registry system.

Features:
- Digital twin data retrieval from database
- Plugin-based simulation execution
- Enterprise-grade metrics and monitoring
- Integration with physics modeling registry
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json

# Import the new twin registry system
from ...twin_registry.models.twin_registry import TwinRegistry
from ...twin_registry.repositories.twin_registry_repository import TwinRegistryRepository
from ...twin_registry.core.twin_registry_service import TwinRegistryService

# Import physics modeling components
from ..core.plugin_manager import PluginManager
from ..core.registry import Registry
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..models.physics_modeling_metrics import PhysicsModelingMetrics
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Main simulation engine for physics modeling.
    
    Integrates with:
    - Twin registry system for digital twin data
    - Plugin manager for simulation plugins
    - Physics modeling registry for model management
    - Enterprise metrics for performance tracking
    """

    def __init__(
        self,
        plugin_manager: Optional[PluginManager] = None,
        registry: Optional[Registry] = None,
        registry_repo: Optional[PhysicsModelingRegistryRepository] = None,
        metrics_repo: Optional[PhysicsModelingMetricsRepository] = None,
        twin_registry_repo: Optional[TwinRegistryRepository] = None,
        twin_registry_service: Optional[TwinRegistryService] = None
    ):
        """Initialize the simulation engine with required components."""
        self.plugin_manager = plugin_manager
        self.registry = registry
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        self.twin_registry_repo = twin_registry_repo
        self.twin_registry_service = twin_registry_service
        
        # Initialize repositories if not provided
        if not self.registry_repo:
            from ...physics_modeling.repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
            self.registry_repo = PhysicsModelingRegistryRepository()
        
        if not self.metrics_repo:
            from ...physics_modeling.repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
            self.metrics_repo = PhysicsModelingMetricsRepository()
        
        if not self.twin_registry_repo:
            from ...twin_registry.repositories.twin_registry_repository import TwinRegistryRepository
            self.twin_registry_repo = TwinRegistryRepository()
        
        if not self.twin_registry_service:
            from ...twin_registry.core.twin_registry_service import TwinRegistryService
            self.twin_registry_service = TwinRegistryService(self.twin_registry_repo)
        
        logger.info("Simulation engine initialized with twin registry integration")

    async def initialize(self) -> bool:
        """Initialize the simulation engine and its components."""
        try:
            # Initialize repositories
            await self.registry_repo.initialize()
            await self.metrics_repo.initialize()
            await self.twin_registry_repo.initialize()
            await self.twin_registry_service.initialize()
            
            # Set plugin manager instance
            if self.plugin_manager:
                self.plugin_manager.registry_repo = self.registry_repo
            
            logger.info("✅ Simulation engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize simulation engine: {e}")
            return False

    async def run_simulation_with_plugin(
        self,
        twin_id: str,
        plugin_id: str,
        simulation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a simulation using a specific plugin and digital twin.
        
        Args:
            twin_id: Digital twin ID from the twin registry
            plugin_id: Plugin identifier
            simulation_params: Simulation parameters
            
        Returns:
            Simulation results with metrics
        """
        try:
            # 1. Validate inputs
            if not twin_id or not plugin_id:
                raise ValueError("twin_id and plugin_id are required")
            
            # 2. Get plugin information
            plugin_info = await self.plugin_manager.get_plugin_by_id(plugin_id)
            if not plugin_info:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            # 3. Get digital twin data from database
            twin_data = await self.get_twin_data(twin_id)
            if not twin_data:
                raise ValueError(f"Digital twin {twin_id} not found")
            
            # 4. Run simulation
            simulation_result = await self._execute_simulation_with_plugin(
                plugin_info, twin_data, simulation_params
            )
            
            # 5. Record metrics
            await self._record_simulation_metrics(twin_id, plugin_id, simulation_result)
            
            logger.info(f"✅ Simulation completed for twin {twin_id} with plugin {plugin_id}")
            return simulation_result
            
        except Exception as e:
            logger.error(f"❌ Simulation failed for twin {twin_id} with plugin {plugin_id}: {e}")
            await self._record_simulation_error(twin_id, plugin_id, str(e))
            raise

    async def get_available_twins(self) -> List[Dict[str, Any]]:
        """
        Get available twins from the twin registry database.
        
        Returns:
            List of available digital twins
        """
        try:
            # Query the twin registry database
            twins = await self.twin_registry_repo.get_all()
            
            # Convert to simplified format for selection
            available_twins = []
            for twin in twins:
                available_twins.append({
                    'twin_id': twin.registry_id,
                    'twin_name': twin.twin_name,
                    'twin_category': twin.twin_category,
                    'twin_type': twin.twin_type,
                    'lifecycle_status': twin.lifecycle_status,
                    'description': twin.description
                })
            
            logger.info(f"Found {len(available_twins)} available twins")
            return available_twins
            
        except Exception as e:
            logger.error(f"Failed to get available twins: {e}")
            return []

    async def get_twin_data(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get twin data from the twin registry database.
        
        Args:
            twin_id: Digital twin ID
            
        Returns:
            Twin data dictionary or None if not found
        """
        try:
            # Query the twin registry database
            twin = await self.twin_registry_repo.get_by_id(twin_id)
            if not twin:
                logger.warning(f"Twin {twin_id} not found in registry")
                return None
            
            # Convert twin model to dictionary with all relevant data
            twin_data = {
                'twin_id': twin.registry_id,
                'twin_name': twin.twin_name,
                'twin_category': twin.twin_category,
                'twin_type': twin.twin_type,
                'lifecycle_status': twin.lifecycle_status,
                'description': twin.description,
                'metadata': twin.metadata,
                'configuration': twin.configuration,
                'created_at': twin.created_at,
                'updated_at': twin.updated_at,
                'activated_at': twin.activated_at,
                'last_accessed_at': twin.last_accessed_at,
                'last_modified_at': twin.last_modified_at
            }
            
            # Add any additional twin-specific data from metadata
            if twin.metadata:
                twin_data.update(twin.metadata)
            
            logger.info(f"Retrieved twin data for {twin_id}")
            return twin_data
            
        except Exception as e:
            logger.error(f"Failed to get twin data for {twin_id}: {e}")
            return None

    async def _execute_simulation_with_plugin(
        self,
        plugin_info: Dict[str, Any],
        twin_data: Dict[str, Any],
        simulation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute simulation using the specified plugin and twin data.
        
        Args:
            plugin_info: Plugin information from registry
            twin_data: Digital twin data from database
            simulation_params: Simulation parameters
            
        Returns:
            Simulation results
        """
        try:
            # Get the actual plugin instance
            plugin_instance = await self._get_plugin_instance(plugin_info)
            if not plugin_instance:
                raise ValueError("Failed to get plugin instance")
            
            # Execute simulation steps
            start_time = datetime.now()
            
            # 1. Preprocess twin data
            processed_data = await plugin_instance.preprocess(twin_data, simulation_params)
            
            # 2. Validate inputs
            validation_result = await plugin_instance.validate_input(processed_data, simulation_params)
            if not validation_result.get('valid', False):
                raise ValueError(f"Input validation failed: {validation_result.get('errors', [])}")
            
            # 3. Run simulation
            simulation_result = await plugin_instance.solve(processed_data, simulation_params)
            
            # 4. Postprocess results
            final_result = await plugin_instance.postprocess(simulation_result, twin_data)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Prepare comprehensive result
            result = {
                'simulation_id': f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'twin_id': twin_data['twin_id'],
                'plugin_id': plugin_info.get('plugin_id'),
                'execution_time': execution_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'status': 'completed',
                'results': final_result,
                'metadata': {
                    'twin_category': twin_data.get('twin_category'),
                    'twin_type': twin_data.get('twin_type'),
                    'plugin_version': plugin_info.get('version'),
                    'simulation_params': simulation_params
                }
            }
            
            logger.info(f"✅ Simulation executed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Simulation execution failed: {e}")
            raise

    async def _get_plugin_instance(self, plugin_info: Dict[str, Any]):
        """
        Get the actual plugin instance for execution.
        
        Args:
            plugin_info: Plugin information from registry
            
        Returns:
            Plugin instance or None
        """
        try:
            # This would typically load the actual plugin class/instance
            # For now, we'll return the plugin info as a mock instance
            # In a real implementation, this would instantiate the actual plugin
            return MockPluginInstance(plugin_info)
            
        except Exception as e:
            logger.error(f"Failed to get plugin instance: {e}")
            return None

    async def _record_simulation_metrics(
        self,
        twin_id: str,
        plugin_id: str,
        simulation_result: Dict[str, Any]
    ) -> None:
        """Record simulation metrics for analysis."""
        try:
            # Create metrics record
            metrics = PhysicsModelingMetrics(
                physics_modeling_id=None,  # Will be set by repository
                metric_name="simulation_execution",
                metric_value=simulation_result.get('execution_time', 0.0),
                metric_unit="seconds",
                metric_type="performance",
                metric_category="simulation",
                metric_timestamp=datetime.now(),
                metric_metadata={
                    'twin_id': twin_id,
                    'plugin_id': plugin_id,
                    'simulation_id': simulation_result.get('simulation_id'),
                    'status': simulation_result.get('status'),
                    'twin_category': simulation_result.get('metadata', {}).get('twin_category'),
                    'plugin_version': simulation_result.get('metadata', {}).get('plugin_version')
                }
            )
            
            # Save to database
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Simulation metrics recorded for {twin_id}")
            
        except Exception as e:
            logger.error(f"Failed to record simulation metrics: {e}")

    async def _record_simulation_error(
        self,
        twin_id: str,
        plugin_id: str,
        error_message: str
    ) -> None:
        """Record simulation error for monitoring."""
        try:
            # Create error metrics record
            metrics = PhysicsModelingMetrics(
                physics_modeling_id=None,  # Will be set by repository
                metric_name="simulation_error",
                metric_value=1.0,
                metric_unit="count",
                metric_type="error",
                metric_category="simulation",
                metric_timestamp=datetime.now(),
                metric_metadata={
                    'twin_id': twin_id,
                    'plugin_id': plugin_id,
                    'error_message': error_message,
                    'status': 'failed'
                }
            )
            
            # Save to database
            await self.metrics_repo.create(metrics)
            logger.info(f"✅ Simulation error recorded for {twin_id}")
            
        except Exception as e:
            logger.error(f"Failed to record simulation error: {e}")

    async def close(self) -> None:
        """Close the simulation engine and cleanup resources."""
        try:
            if self.registry_repo:
                await self.registry_repo.close()
            if self.metrics_repo:
                await self.metrics_repo.close()
            if self.twin_registry_repo:
                await self.twin_registry_repo.close()
            if self.twin_registry_service:
                await self.twin_registry_service.close()
            
            logger.info("✅ Simulation engine closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing simulation engine: {e}")


class MockPluginInstance:
    """Mock plugin instance for testing purposes."""
    
    def __init__(self, plugin_info: Dict[str, Any]):
        self.plugin_info = plugin_info
    
    async def preprocess(self, twin_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock preprocessing."""
        await asyncio.sleep(0)  # Pure async
        return {**twin_data, 'preprocessed': True}
    
    async def validate_input(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock input validation."""
        await asyncio.sleep(0)  # Pure async
        return {'valid': True, 'errors': []}
    
    async def solve(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock simulation solving."""
        await asyncio.sleep(0)  # Pure async
        return {'solution': 'mock_solution', 'converged': True}
    
    async def postprocess(self, result: Dict[str, Any], twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock postprocessing."""
        await asyncio.sleep(0)  # Pure async
        return {**result, 'postprocessed': True, 'twin_id': twin_data['twin_id']} 