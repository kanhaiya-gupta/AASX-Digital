"""
Plugin manager for physics modeling framework.

This module handles the discovery, loading, and management of physics plugins.
It integrates with the existing use_cases table for plugin registration.
"""

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from .dynamic_types import PhysicsPlugin, DynamicPhysicsType
from src.shared.models.use_case import UseCase

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugin discovery, loading, and lifecycle.
    
    This class handles:
    - Discovering plugins in the plugins directory
    - Loading and instantiating plugins
    - Registering plugins in the existing use_cases table
    - Providing access to available plugins
    """
    
    def __init__(self, use_case_repository):
        """
        Initialize the plugin manager.
        
        Args:
            use_case_repository: Repository for use cases (existing database)
        """
        self.use_case_repo = use_case_repository
        self.plugins: Dict[str, PhysicsPlugin] = {}
        self.plugin_info: Dict[str, Dict[str, Any]] = {}
        self.plugins_dir = Path(__file__).parent.parent / "plugins"
        
        logger.info(f"Plugin manager initialized with plugins directory: {self.plugins_dir}")
    
    def discover_and_register_plugins(self, use_case_name: str = None, project_name: str = None) -> List[str]:
        """
        Discover and register plugins globally (available to all use cases).
        
        Args:
            use_case_name: Name of existing use case (optional, for backward compatibility)
            project_name: Name of project (optional, for backward compatibility)
            
        Returns:
            List of discovered plugin IDs
        """
        try:
            discovered_plugins = self.discover_plugins()
            registered_plugins = []
            loaded_plugin_ids = set()  # Track loaded plugin IDs to avoid duplicates
            
            for plugin_path in discovered_plugins:
                try:
                    plugin = self.load_plugin(plugin_path)
                    if plugin:
                        physics_type = plugin.get_physics_type()
                        plugin_id = self._generate_plugin_id(physics_type.name)
                        
                        # Skip if we've already loaded this plugin
                        if plugin_id in loaded_plugin_ids:
                            logger.info(f"Skipping duplicate plugin {plugin_id} from {plugin_path}")
                            continue
                        
                        loaded_plugin_ids.add(plugin_id)
                        
                        # Register plugin globally (available to all use cases)
                        if self.register_plugin_globally(plugin):
                            registered_plugins.append(plugin_id)
                            logger.info(f"Successfully registered plugin globally: {plugin_id}")
                        else:
                            logger.warning(f"Failed to register plugin {plugin_id} globally")
                            
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_path}: {e}")
            
            logger.info(f"Discovered and registered {len(registered_plugins)} plugins globally")
            return registered_plugins
            
        except Exception as e:
            logger.error(f"Error during plugin discovery: {e}")
            return []
    
    def get_plugins_for_twin(self, twin_id: str) -> List[Dict[str, Any]]:
        """
        Get available plugins for a specific digital twin by tracing from twin_id.
        
        Args:
            twin_id: Digital twin ID (same as file_id)
            
        Returns:
            List of available plugins for this twin's use case/project
        """
        try:
            # Import here to avoid circular imports
            from src.shared.repositories.file_repository import FileRepository
            from src.shared.database.base_manager import BaseDatabaseManager
            from src.shared.database.connection_manager import DatabaseConnectionManager
            
            # Get file repository to trace twin_id
            db_path = Path("data/aasx_database.db")
            connection_manager = DatabaseConnectionManager(db_path)
            db_manager = BaseDatabaseManager(connection_manager)
            file_repo = FileRepository(db_manager)
            
            # Trace from twin_id to get use case and project
            trace_info = file_repo.get_file_trace_info(twin_id)
            if not trace_info:
                logger.warning(f"Could not trace twin_id {twin_id} to use case/project")
                return []
            
            use_case_name = trace_info.get("use_case_name")
            project_name = trace_info.get("project_name")
            
            if not use_case_name:
                logger.warning(f"No use case found for twin_id {twin_id}")
                return []
            
            # Get plugins registered for this use case
            return self.get_plugins_for_use_case(use_case_name)
            
        except Exception as e:
            logger.error(f"Failed to get plugins for twin {twin_id}: {e}")
            return []
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugin files.
        
        Returns:
            List of plugin file paths
        """
        plugin_files = []
        
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory does not exist: {self.plugins_dir}")
            return plugin_files
        
        # Walk through plugins directory
        for category_dir in self.plugins_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('_'):
                # Skip templates directory - those are just templates, not actual plugins
                if category_dir.name == "templates":
                    logger.info("Skipping templates directory - templates are not loaded as plugins")
                    continue
                    
                for plugin_file in category_dir.glob("*.py"):
                    if not plugin_file.name.startswith('_') and plugin_file.name != "__init__.py":
                        plugin_files.append(str(plugin_file))
        
        logger.info(f"Discovered {len(plugin_files)} plugin files")
        return plugin_files
    
    def load_plugin(self, plugin_path: str) -> Optional[PhysicsPlugin]:
        """
        Load a plugin from a file path.
        
        Args:
            plugin_path: Path to the plugin file
            
        Returns:
            Plugin instance or None if loading failed
        """
        try:
            # Convert file path to module path
            plugin_file = Path(plugin_path)
            # Calculate relative path from src directory
            src_root = self.plugins_dir.parent.parent  # src directory
            relative_path = plugin_file.relative_to(src_root)
            module_path = str(relative_path).replace(os.sep, '.').replace('.py', '')
            
            # Add src to sys.path if not already there
            if str(src_root) not in sys.path:
                sys.path.insert(0, str(src_root))
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Find PhysicsPlugin subclasses
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PhysicsPlugin) and 
                    obj != PhysicsPlugin):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                logger.warning(f"No PhysicsPlugin classes found in {plugin_path}")
                return None
            
            if len(plugin_classes) > 1:
                logger.warning(f"Multiple PhysicsPlugin classes found in {plugin_path}, using first one")
            
            # Instantiate the plugin
            plugin_class = plugin_classes[0]
            plugin = plugin_class()
            
            # Validate the plugin
            if not self._validate_plugin(plugin):
                logger.error(f"Plugin validation failed for {plugin_path}")
                return None
            
            logger.info(f"Successfully loaded plugin: {plugin.get_physics_type().type_id}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return None
    
    def _generate_plugin_id(self, plugin_name: str) -> str:
        """Generate deterministic plugin ID from plugin name only."""
        import hashlib
        return hashlib.md5(plugin_name.encode()).hexdigest()[:16]
    
    def register_plugin_globally(self, plugin: PhysicsPlugin) -> bool:
        """
        Register a plugin globally (available to all use cases).
        
        Args:
            plugin: Plugin instance to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            physics_type = plugin.get_physics_type()
            
            # Generate deterministic plugin ID from plugin name only
            plugin_id = self._generate_plugin_id(physics_type.name)
            
            # Check if plugin already exists globally
            if plugin_id in self.plugin_info:
                logger.info(f"Plugin {plugin_id} already registered globally")
                return True
            
            # Add to global plugins and info
            self.plugins[plugin_id] = plugin
            self.plugin_info[plugin_id] = self._get_plugin_info(plugin)
            
            logger.info(f"Successfully registered plugin globally: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin globally: {e}")
            return False
    
    def get_plugin(self, plugin_id: str) -> Optional[PhysicsPlugin]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> Dict[str, PhysicsPlugin]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of plugin_id -> plugin instance
        """
        return self.plugins.copy()
    
    def get_all_plugins_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all plugins.
        
        Returns:
            Dictionary of plugin_id -> plugin info
        """
        return self.plugin_info.copy()
    
    def get_plugins_by_category(self, category: str) -> Dict[str, PhysicsPlugin]:
        """
        Get plugins by category.
        
        Args:
            category: Plugin category (e.g., 'thermal', 'structural')
            
        Returns:
            Dictionary of plugin_id -> plugin instance for the category
        """
        return {
            plugin_id: plugin 
            for plugin_id, plugin in self.plugins.items()
            if plugin.get_physics_type().category == category
        }
    
    def get_plugins_by_base_type(self, base_physics_type: str) -> Dict[str, PhysicsPlugin]:
        """
        Get all plugin variants for a base physics type.
        
        Args:
            base_physics_type: Base physics type name (e.g., 'Thermal Analysis')
            
        Returns:
            Dictionary of plugin_id -> plugin instance for the base type
        """
        return {
            plugin_id: plugin 
            for plugin_id, plugin in self.plugins.items()
            if plugin.get_physics_type().name == base_physics_type
        }
    
    def get_plugins_for_use_case(self, use_case_name: str) -> List[Dict[str, Any]]:
        """
        Get all plugins available for a specific use case.
        Since plugins are registered globally, all plugins are available to all use cases.
        
        Args:
            use_case_name: Name of the use case
            
        Returns:
            List of plugin information for the use case
        """
        plugins = []
        
        # Since plugins are registered globally, return all available plugins
        for plugin_id, plugin_info in self.plugin_info.items():
            plugins.append({
                'plugin_id': plugin_id,
                'use_case_name': use_case_name,
                'name': plugin_info.get('name'),
                'project': 'global',  # All plugins are globally available
                'version': plugin_info.get('version'),
                'category': plugin_info.get('category'),
                'description': f"Global plugin available for {use_case_name} - {plugin_info.get('name')}"
            })
        
        return plugins
    
    def get_plugin_by_id(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin information by plugin ID from global registry.
        
        Args:
            plugin_id: The plugin ID to search for
            
        Returns:
            Plugin information or None if not found
        """
        if plugin_id in self.plugin_info:
            plugin_info = self.plugin_info[plugin_id]
            return {
                'plugin_id': plugin_id,
                'use_case_name': 'global',  # Available to all use cases
                'name': plugin_info.get('name'),
                'project': 'global',
                'version': plugin_info.get('version'),
                'category': plugin_info.get('category'),
                'description': plugin_info.get('description'),
                'parameters': plugin_info.get('parameters', []),
                'equations': plugin_info.get('equations', []),
                'solver_capabilities': plugin_info.get('solver_capabilities', [])
            }
        return None
    
    def get_plugin_instance(self, plugin_id: str) -> Optional[PhysicsPlugin]:
        """
        Get the actual plugin instance by plugin ID.
        
        Args:
            plugin_id: The plugin ID to search for
            
        Returns:
            Plugin instance or None if not found
        """
        if plugin_id in self.plugins:
            return self.plugins[plugin_id]
        return None
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a specific plugin.
        
        Args:
            plugin_id: Plugin ID to reload
            
        Returns:
            True if reload successful, False otherwise
        """
        try:
            # Remove existing plugin
            if plugin_id in self.plugins:
                del self.plugins[plugin_id]
                del self.plugin_info[plugin_id]
            
            # Find and reload the plugin
            plugin_files = self.discover_plugins()
            for plugin_path in plugin_files:
                plugin = self.load_plugin(plugin_path)
                if plugin and plugin.get_physics_type().type_id == plugin_id:
                    self.plugins[plugin_id] = plugin
                    self.plugin_info[plugin_id] = self._get_plugin_info(plugin)
                    logger.info(f"Successfully reloaded plugin: {plugin_id}")
                    return True
            
            logger.warning(f"Plugin {plugin_id} not found for reload")
            return False
            
        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_id}: {e}")
            return False
    
    def _validate_plugin(self, plugin: PhysicsPlugin) -> bool:
        """
        Validate a plugin instance.
        
        Args:
            plugin: Plugin to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if plugin implements required methods
            if not hasattr(plugin, 'get_physics_type') or not callable(plugin.get_physics_type):
                logger.error("Plugin must implement get_physics_type() method")
                return False
            
            if not hasattr(plugin, 'solve') or not callable(plugin.solve):
                logger.error("Plugin must implement solve() method")
                return False
            
            # Get physics type and validate it
            physics_type = plugin.get_physics_type()
            if not isinstance(physics_type, DynamicPhysicsType):
                logger.error("get_physics_type() must return a DynamicPhysicsType")
                return False
            
            # Validate required fields
            if not physics_type.type_id or not physics_type.name or not physics_type.category:
                logger.error("Physics type must have type_id, name, and category")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Plugin validation error: {e}")
            return False
    
    def _get_plugin_info(self, plugin: PhysicsPlugin) -> Dict[str, Any]:
        """
        Get information about a plugin.
        
        Args:
            plugin: Plugin instance
            
        Returns:
            Plugin information dictionary
        """
        try:
            physics_type = plugin.get_physics_type()
            return {
                'plugin_id': physics_type.type_id,
                'name': physics_type.name,
                'category': physics_type.category,
                'description': physics_type.description,
                'version': physics_type.version,
                'class_name': plugin.__class__.__name__,
                'module_name': plugin.__class__.__module__,
                'parameters': [param.__dict__ for param in physics_type.parameters],
                'equations': [eq.__dict__ for eq in physics_type.equations],
                'solver_capabilities': [cap.__dict__ for cap in physics_type.solver_capabilities],
                'dependencies': physics_type.dependencies,
                'metadata': physics_type.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get plugin info: {e}")
            return {}
    
    def _serialize_parameter(self, param) -> Dict[str, Any]:
        """Convert PhysicsParameter to JSON-serializable dict."""
        return {
            'name': param.name,
            'parameter_type': param.parameter_type.value,  # Convert enum to string
            'description': param.description,
            'default_value': param.default_value,
            'unit': param.unit,
            'unit_system': param.unit_system.value,  # Convert enum to string
            'min_value': param.min_value,
            'max_value': param.max_value,
            'required': param.required,
            'metadata': param.metadata
        }
    
    def _serialize_equation(self, eq) -> Dict[str, Any]:
        """Convert PhysicsEquation to JSON-serializable dict."""
        return {
            'name': eq.name,
            'equation': eq.equation,
            'description': eq.description,
            'variables': eq.variables,
            'units': eq.units
        }
    
    def _serialize_capability(self, cap) -> Dict[str, Any]:
        """Convert SolverCapability to JSON-serializable dict."""
        return {
            'name': cap.name,
            'description': cap.description,
            'problem_types': cap.problem_types,
            'supported_physics': cap.supported_physics,
            'accuracy_level': cap.accuracy_level,
            'performance_rating': cap.performance_rating
        } 