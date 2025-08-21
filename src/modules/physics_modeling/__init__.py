"""
Physics Modeling Framework - Main Entry Point

A minimal, static framework that provides plugin templates for users to create 
custom physics types and solvers. Integrates with existing shared database infrastructure.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicPhysicsModelingFramework:
    """
    Main entry point for physics modeling framework.
    
    This framework provides:
    - Plugin management and discovery
    - Model creation from digital twins
    - Common simulation infrastructure
    - Integration with existing shared database
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the physics modeling framework.
        
        Args:
            db_path: Optional path to database. If None, uses default from environment.
        """
        try:
            # Use existing shared database infrastructure
            from src.shared.database.connection_manager import DatabaseConnectionManager
            from src.shared.database.base_manager import BaseDatabaseManager
            
            # Get database path from environment if not provided
            if db_path is None:
                db_path = os.getenv('DATABASE_PATH', 'data/aasx_database.db')
            
            # Convert to Path object
            db_path = Path(db_path)
            
            # Initialize database connection
            connection_manager = DatabaseConnectionManager(db_path)
            self.db_manager = BaseDatabaseManager(connection_manager)
            
            # Use existing repositories
            from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
            from src.shared.repositories.file_repository import FileRepository
            from src.shared.repositories.project_repository import ProjectRepository
            from src.shared.repositories.use_case_repository import UseCaseRepository
            
            self.digital_twin_repo = DigitalTwinRepository(self.db_manager)
            self.file_repo = FileRepository(self.db_manager)
            self.project_repo = ProjectRepository(self.db_manager)
            self.use_case_repo = UseCaseRepository(self.db_manager)
            
            # Initialize core components
            from .core.plugin_manager import PluginManager
            from .core.model_factory import ModelFactory
            from .core.registry import Registry
            from .simulation.simulation_engine import SimulationEngine
            
            self.plugin_manager = PluginManager(self.use_case_repo)
            self.model_factory = ModelFactory(self.digital_twin_repo, self.plugin_manager, self.file_repo)
            self.registry = Registry()
            self.simulation_engine = SimulationEngine(
                self.digital_twin_repo, 
                self.plugin_manager,
                self.file_repo
            )
            
            # Discover and register plugins for existing use cases
            self.plugin_manager.discover_and_register_plugins()
            
            logger.info("Physics Modeling Framework initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Physics Modeling Framework: {e}")
            raise
    
    def get_available_plugins(self, twin_id: str = None) -> Dict[str, Any]:
        """
        Get available physics plugins, optionally filtered by digital twin.
        
        Args:
            twin_id: Optional digital twin ID to filter plugins by use case/project
            
        Returns:
            Dictionary of plugin_id -> plugin_info
        """
        if twin_id:
            # Get plugins specific to this twin's use case/project
            plugins = self.plugin_manager.get_plugins_for_twin(twin_id)
            return {plugin['plugin_id']: plugin for plugin in plugins}
        else:
            # Get all plugins
            return self.plugin_manager.get_all_plugins_info()
    
    def get_twin_trace_info(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace information for a digital twin (use case, project, file).
        
        Args:
            twin_id: Digital twin ID (which equals file_id)
            
        Returns:
            Trace information or None if not found
        """
        try:
            trace_info = self.file_repo.get_file_trace_info(twin_id)
            return trace_info
        except Exception as e:
            logger.error(f"Failed to get trace info for twin {twin_id}: {e}")
            return None
    
    def get_plugins_for_use_case(self, use_case_name: str) -> List[Dict[str, Any]]:
        """
        Get plugins available for a specific use case.
        
        Args:
            use_case_name: Name of the use case
            
        Returns:
            List of plugin information
        """
        try:
            plugins = self.plugin_manager.get_plugins_for_use_case(use_case_name)
            return plugins
        except Exception as e:
            logger.error(f"Failed to get plugins for use case {use_case_name}: {e}")
            return []
    
    def create_model(self, twin_id: str, physics_type: str, 
                    parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a physics model from digital twin.
        
        Args:
            twin_id: Digital twin ID
            physics_type: Type of physics plugin to use
            parameters: Model parameters
            
        Returns:
            Model information or None if creation failed
        """
        try:
            model = self.model_factory.create_model_from_twin(
                twin_id, physics_type, parameters
            )
            return model
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            return None
    
    def run_simulation(self, twin_id: str, plugin_id: str, 
                      parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run a physics simulation using a specific plugin.
        
        Args:
            twin_id: Digital twin ID
            plugin_id: Plugin ID to use for simulation
            parameters: Simulation parameters
            
        Returns:
            Simulation results or None if simulation failed
        """
        try:
            # Get plugin by ID
            plugin_info = self.plugin_manager.get_plugin_by_id(plugin_id)
            if not plugin_info:
                logger.error(f"Plugin {plugin_id} not found")
                return None
            
            # Run simulation using the plugin
            results = self.simulation_engine.run_simulation_with_plugin(
                twin_id, plugin_id, parameters
            )
            return results
        except Exception as e:
            logger.error(f"Failed to run simulation: {e}")
            return None
    
    def get_simulation_history(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation history for a digital twin.
        
        Args:
            twin_id: Digital twin ID
            
        Returns:
            Simulation history or None if not found
        """
        try:
            twin = self.digital_twin_repo.get_by_id(twin_id)
            if twin and twin.simulation_history:
                return twin.simulation_history
            return None
        except Exception as e:
            logger.error(f"Failed to get simulation history: {e}")
            return None


# Create a singleton instance
_physics_framework = None


def get_physics_framework(db_path: Optional[str] = None) -> DynamicPhysicsModelingFramework:
    """
    Get the singleton instance of the physics modeling framework.
    
    Args:
        db_path: Optional database path
        
    Returns:
        Physics modeling framework instance
    """
    global _physics_framework
    if _physics_framework is None:
        _physics_framework = DynamicPhysicsModelingFramework(db_path)
    return _physics_framework


# Export main class
__all__ = ['DynamicPhysicsModelingFramework', 'get_physics_framework'] 