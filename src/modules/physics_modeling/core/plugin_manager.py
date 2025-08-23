"""
Plugin manager for physics modeling framework.

This module handles the discovery, loading, and management of physics plugins.
It integrates with the new src/engine infrastructure and PhysicsModelingRegistry.
"""

import os
import sys
import importlib
import inspect
import logging
import asyncio
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from datetime import datetime

from .dynamic_types import PhysicsPlugin, DynamicPhysicsType
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugin discovery, loading, and lifecycle with modern engine integration.
    
    This class handles:
    - Discovering plugins in the plugins directory
    - Loading and instantiating plugins
    - Registering plugins in the new PhysicsModelingRegistry
    - Providing access to available plugins with enterprise features
    """
    
    def __init__(self, registry_repository: Optional[PhysicsModelingRegistryRepository] = None):
        """
        Initialize the plugin manager with modern engine integration.
        
        Args:
            registry_repository: Repository for physics modeling registry (optional, will create if not provided)
        """
        self.registry_repo = registry_repository or PhysicsModelingRegistryRepository()
        self.plugins: Dict[str, PhysicsPlugin] = {}
        self.plugin_info: Dict[str, Dict[str, Any]] = {}
        self.plugins_dir = Path(__file__).parent.parent / "plugins"
        
        logger.info(f"✅ Modern Plugin Manager initialized with plugins directory: {self.plugins_dir}")
    
    async def initialize(self) -> bool:
        """Initialize the plugin manager asynchronously."""
        try:
            await asyncio.sleep(0)  # Ensure async context
            logger.info("Initializing Plugin Manager with engine infrastructure")
            
            # Initialize the registry repository
            await self.registry_repo.initialize()
            
            # Discover and register available plugins
            await self.discover_and_register_plugins()
            
            logger.info("✅ Plugin Manager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Plugin Manager: {e}")
            return False
    
    async def discover_and_register_plugins(self, use_case_name: str = None, project_name: str = None) -> List[str]:
        """
        Discover and register plugins globally with modern engine integration.
        
        Args:
            use_case_name: Name of existing use case (optional, for backward compatibility)
            project_name: Name of project (optional, for backward compatibility)
            
        Returns:
            List of discovered plugin IDs
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            discovered_plugins = await self.discover_plugins()
            registered_plugins = []
            loaded_plugin_ids = set()  # Track loaded plugin IDs to avoid duplicates
            
            for plugin_path in discovered_plugins:
                try:
                    plugin = await self.load_plugin(plugin_path)
                    if plugin:
                        physics_type = plugin.get_physics_type()
                        plugin_id = self._generate_plugin_id(physics_type.name)
                        
                        # Skip if we've already loaded this plugin
                        if plugin_id in loaded_plugin_ids:
                            logger.info(f"Skipping duplicate plugin {plugin_id} from {plugin_path}")
                            continue
                        
                        loaded_plugin_ids.add(plugin_id)
                        
                        # Register plugin globally with new engine infrastructure
                        if await self.register_plugin_globally(plugin):
                            registered_plugins.append(plugin_id)
                            logger.info(f"Successfully registered plugin globally: {plugin_id}")
                        else:
                            logger.warning(f"Failed to register plugin {plugin_id} globally")
                            
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_path}: {e}")
            
            logger.info(f"✅ Discovered and registered {len(registered_plugins)} plugins globally")
            return registered_plugins
            
        except Exception as e:
            logger.error(f"Error during plugin discovery: {e}")
            return []
    
    async def get_plugins_for_twin(self, twin_id: str) -> List[Dict[str, Any]]:
        """
        Get available plugins for a specific digital twin with modern engine integration.
        
        Args:
            twin_id: Digital twin ID (same as file_id)
            
        Returns:
            List of available plugins with enterprise features
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get plugins from the new registry
            available_plugins = await self.registry_repo.get_by_twin_id(twin_id)
            
            # Enhance with plugin information
            enhanced_plugins = []
            for plugin_record in available_plugins:
                plugin_info = {
                    'plugin_id': plugin_record.registry_id,
                    'name': plugin_record.model_name,
                    'physics_type': plugin_record.physics_type,
                    'version': plugin_record.model_version,
                    'status': plugin_record.status,
                    'compliance_score': plugin_record.compliance_score,
                    'security_score': plugin_record.security_score,
                    'performance_score': plugin_record.performance_score,
                    'created_at': plugin_record.created_at,
                    'updated_at': plugin_record.updated_at
                }
                enhanced_plugins.append(plugin_info)
            
            logger.info(f"✅ Retrieved {len(enhanced_plugins)} plugins for twin {twin_id}")
            return enhanced_plugins
            
        except Exception as e:
            logger.error(f"Failed to get plugins for twin {twin_id}: {e}")
            return []
    
    async def discover_plugins(self) -> List[Path]:
        """
        Discover available plugins in the plugins directory.
        
        Returns:
            List of plugin file paths
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            discovered_plugins = []
            
            if not self.plugins_dir.exists():
                logger.warning(f"Plugins directory does not exist: {self.plugins_dir}")
                return discovered_plugins
            
            # Search for Python files in plugins subdirectories
            for plugin_type_dir in self.plugins_dir.iterdir():
                if plugin_type_dir.is_dir() and not plugin_type_dir.name.startswith('_'):
                    for plugin_file in plugin_type_dir.glob("*.py"):
                        if not plugin_file.name.startswith('_') and plugin_file.name != "__init__.py":
                            discovered_plugins.append(plugin_file)
            
            logger.info(f"✅ Discovered {len(discovered_plugins)} plugin files")
            return discovered_plugins
            
        except Exception as e:
            logger.error(f"Failed to discover plugins: {e}")
            return []
    
    async def load_plugin(self, plugin_path: Path) -> Optional[PhysicsPlugin]:
        """
        Load a plugin from a file path.
        
        Args:
            plugin_path: Path to the plugin file
            
        Returns:
            Loaded plugin instance or None if loading failed
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Import the plugin module
            module_name = f"src.modules.physics_modeling.plugins.{plugin_path.parent.name}.{plugin_path.stem}"
            
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                logger.error(f"Failed to import plugin module {module_name}: {e}")
                return None
            
            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PhysicsPlugin) and 
                    obj != PhysicsPlugin):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                logger.warning(f"No plugin classes found in {plugin_path}")
                return None
            
            # Return the first plugin class found
            plugin_class = plugin_classes[0]
            logger.info(f"✅ Successfully loaded plugin: {plugin_class.__name__}")
            return plugin_class()
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")
            return None
    
    async def register_plugin_globally(self, plugin: PhysicsPlugin) -> bool:
        """
        Register a plugin globally in the new PhysicsModelingRegistry.
        
        Args:
            plugin: Plugin instance to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            physics_type = plugin.get_physics_type()
            
            # Create plugin record for the new registry
            plugin_record = PhysicsModelingRegistry(
                model_name=physics_type.name,
                physics_type=physics_type.name,
                model_version=physics_type.version,
                description=physics_type.description,
                model_parameters=physics_type.parameters,
                status="active",
                compliance_score=100.0,  # Default compliance score
                security_score=100.0,   # Default security score
                performance_score=100.0, # Default performance score
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to the new registry
            saved_record = await self.registry_repo.create(plugin_record)
            
            if saved_record:
                # Store plugin instance locally
                plugin_id = self._generate_plugin_id(physics_type.name)
                self.plugins[plugin_id] = plugin
                self.plugin_info[plugin_id] = {
                    'name': physics_type.name,
                    'version': physics_type.version,
                    'description': physics_type.description,
                    'parameters': physics_type.parameters,
                    'registry_id': saved_record.registry_id
                }
                
                logger.info(f"✅ Successfully registered plugin {plugin_id} in new registry")
                return True
            else:
                logger.error(f"Failed to save plugin {physics_type.name} to registry")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register plugin globally: {e}")
            return False
    
    def _generate_plugin_id(self, plugin_name: str) -> str:
        """
        Generate a unique plugin ID.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Unique plugin ID
        """
        # Generate a simple ID based on plugin name
        return f"plugin_{plugin_name.lower().replace(' ', '_')}"
    
    async def get_plugin_by_id(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin information by ID.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin information dictionary or None if not found
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            if plugin_id in self.plugin_info:
                return self.plugin_info[plugin_id]
            
            # Try to find in registry
            plugin_record = await self.registry_repo.get_by_id(plugin_id)
            if plugin_record:
                return {
                    'plugin_id': plugin_record.registry_id,
                    'name': plugin_record.model_name,
                    'physics_type': plugin_record.physics_type,
                    'version': plugin_record.model_version,
                    'status': plugin_record.status,
                    'compliance_score': plugin_record.compliance_score,
                    'security_score': plugin_record.security_score,
                    'performance_score': plugin_record.performance_score
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get plugin by ID {plugin_id}: {e}")
            return None
    
    async def get_all_plugins(self) -> List[Dict[str, Any]]:
        """
        Get all registered plugins with enterprise features.
        
        Returns:
            List of all plugin information
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get all plugins from registry
            all_plugins = await self.registry_repo.get_all()
            
            # Enhance with local plugin information
            enhanced_plugins = []
            for plugin_record in all_plugins:
                plugin_info = {
                    'plugin_id': plugin_record.registry_id,
                    'name': plugin_record.model_name,
                    'physics_type': plugin_record.physics_type,
                    'version': plugin_record.model_version,
                    'status': plugin_record.status,
                    'compliance_score': plugin_record.compliance_score,
                    'security_score': plugin_record.security_score,
                    'performance_score': plugin_record.performance_score,
                    'created_at': plugin_record.created_at,
                    'updated_at': plugin_record.updated_at
                }
                enhanced_plugins.append(plugin_info)
            
            return enhanced_plugins
            
        except Exception as e:
            logger.error(f"Failed to get all plugins: {e}")
            return []
    
    async def update_plugin_status(self, plugin_id: str, status: str) -> bool:
        """
        Update plugin status in the registry.
        
        Args:
            plugin_id: Plugin ID
            status: New status
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            plugin_record = await self.registry_repo.get_by_id(plugin_id)
            if not plugin_record:
                logger.error(f"Plugin {plugin_id} not found in registry")
                return False
            
            # Update status
            plugin_record.status = status
            plugin_record.updated_at = datetime.utcnow()
            
            # Save updated record
            updated_record = await self.registry_repo.update(plugin_record)
            
            if updated_record:
                logger.info(f"✅ Successfully updated plugin {plugin_id} status to {status}")
                return True
            else:
                logger.error(f"Failed to update plugin {plugin_id} status")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update plugin status: {e}")
            return False
    
    async def close(self):
        """Close the plugin manager and cleanup resources."""
        try:
            await asyncio.sleep(0)  # Ensure async context
            logger.info("Closing Plugin Manager")
            
            # Close registry repository
            if hasattr(self.registry_repo, 'close'):
                await self.registry_repo.close()
            
            # Clear local plugin storage
            self.plugins.clear()
            self.plugin_info.clear()
            
            logger.info("✅ Plugin Manager closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing Plugin Manager: {e}") 