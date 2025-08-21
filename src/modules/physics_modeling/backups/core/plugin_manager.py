"""
Plugin Management System

This module provides functionality for discovering, loading, and managing
physics plugins in a dynamic manner. Plugins can be added, removed, and
updated without restarting the framework.
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import logging
from abc import ABC, abstractmethod

from .dynamic_types import DynamicPhysicsType


class PhysicsPlugin(ABC):
    """
    Abstract base class for physics plugins.
    
    All physics plugins must inherit from this class and implement
    the required methods.
    """
    
    @abstractmethod
    def get_physics_type(self) -> DynamicPhysicsType:
        """Return the physics type definition for this plugin."""
        pass
    
    @abstractmethod
    def validate_input(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate input parameters for the physics type.
        
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    def solve(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve the physics problem with given parameters.
        
        Args:
            parameters: Input parameters for the physics simulation
            
        Returns:
            Dictionary containing simulation results
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return {
            'name': self.__class__.__name__,
            'version': getattr(self, 'version', '1.0.0'),
            'author': getattr(self, 'author', 'Unknown'),
            'description': getattr(self, 'description', ''),
            'category': getattr(self, 'category', 'unknown')
        }


class PhysicsPluginManager:
    """
    Manages the discovery, loading, and lifecycle of physics plugins.
    
    This class provides a centralized way to manage plugins, including
    automatic discovery, loading, validation, and cleanup.
    """
    
    def __init__(self, plugin_directories: Optional[List[str]] = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_directories: List of directories to search for plugins
        """
        self.plugin_directories = plugin_directories or [
            os.path.join(os.path.dirname(__file__), '..', 'plugins')
        ]
        self.loaded_plugins: Dict[str, PhysicsPlugin] = {}
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugin directories.
        
        Returns:
            List of plugin file paths
        """
        plugin_files = []
        
        for directory in self.plugin_directories:
            if not os.path.exists(directory):
                self.logger.warning(f"Plugin directory does not exist: {directory}")
                continue
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        plugin_path = os.path.join(root, file)
                        plugin_files.append(plugin_path)
        
        return plugin_files
    
    def load_plugin(self, plugin_path: str) -> Optional[PhysicsPlugin]:
        """
        Load a plugin from a file path.
        
        Args:
            plugin_path: Path to the plugin file
            
        Returns:
            Loaded plugin instance or None if loading failed
        """
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(
                f"physics_plugin_{os.path.basename(plugin_path)}", 
                plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            plugin_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, PhysicsPlugin) and 
                    attr != PhysicsPlugin):
                    plugin_classes.append(attr)
            
            if not plugin_classes:
                self.logger.warning(f"No plugin classes found in {plugin_path}")
                return None
            
            # Load the first plugin class found
            plugin_class = plugin_classes[0]
            plugin_instance = plugin_class()
            
            # Validate the plugin
            physics_type = plugin_instance.get_physics_type()
            if not isinstance(physics_type, DynamicPhysicsType):
                raise ValueError(f"Plugin {plugin_path} must return a DynamicPhysicsType")
            
            # Register the plugin
            plugin_id = physics_type.type_id
            self.loaded_plugins[plugin_id] = plugin_instance
            self.plugin_metadata[plugin_id] = plugin_instance.get_metadata()
            
            self.logger.info(f"Successfully loaded plugin: {plugin_id}")
            return plugin_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_path}: {str(e)}")
            return None
    
    def load_all_plugins(self) -> Dict[str, PhysicsPlugin]:
        """
        Load all discovered plugins.
        
        Returns:
            Dictionary of loaded plugins
        """
        plugin_files = self.discover_plugins()
        
        for plugin_path in plugin_files:
            self.load_plugin(plugin_path)
        
        return self.loaded_plugins
    
    def get_plugin(self, plugin_id: str) -> Optional[PhysicsPlugin]:
        """
        Get a loaded plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin instance or None if not found
        """
        return self.loaded_plugins.get(plugin_id)
    
    def get_all_plugins(self) -> Dict[str, PhysicsPlugin]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of all loaded plugins
        """
        return self.loaded_plugins.copy()
    
    def get_plugins_by_category(self, category: str) -> Dict[str, PhysicsPlugin]:
        """
        Get plugins by category.
        
        Args:
            category: Plugin category (e.g., 'thermal', 'structural')
            
        Returns:
            Dictionary of plugins in the specified category
        """
        return {
            plugin_id: plugin
            for plugin_id, plugin in self.loaded_plugins.items()
            if plugin.get_metadata().get('category') == category
        }
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if plugin was unloaded, False otherwise
        """
        if plugin_id in self.loaded_plugins:
            del self.loaded_plugins[plugin_id]
            if plugin_id in self.plugin_metadata:
                del self.plugin_metadata[plugin_id]
            self.logger.info(f"Unloaded plugin: {plugin_id}")
            return True
        return False
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if plugin was reloaded, False otherwise
        """
        if plugin_id in self.loaded_plugins:
            # Store metadata for reloading
            metadata = self.plugin_metadata.get(plugin_id, {})
            
            # Unload the plugin
            self.unload_plugin(plugin_id)
            
            # Try to reload it
            # Note: This is a simplified reload - in practice, you might need
            # to track the original file path and reload from there
            self.logger.warning(f"Plugin reload not fully implemented for {plugin_id}")
            return False
        
        return False
    
    def validate_plugin(self, plugin: PhysicsPlugin) -> Dict[str, str]:
        """
        Validate a plugin instance.
        
        Args:
            plugin: Plugin instance to validate
            
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Check if it's a valid plugin class
        if not isinstance(plugin, PhysicsPlugin):
            errors['type'] = "Plugin must inherit from PhysicsPlugin"
            return errors
        
        # Check if it has required methods
        required_methods = ['get_physics_type', 'validate_input', 'solve']
        for method in required_methods:
            if not hasattr(plugin, method):
                errors[method] = f"Plugin must implement {method} method"
        
        # Validate physics type
        try:
            physics_type = plugin.get_physics_type()
            if not isinstance(physics_type, DynamicPhysicsType):
                errors['physics_type'] = "get_physics_type() must return a DynamicPhysicsType"
        except Exception as e:
            errors['physics_type'] = f"Error getting physics type: {str(e)}"
        
        return errors
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin information dictionary or None if not found
        """
        if plugin_id not in self.loaded_plugins:
            return None
        
        plugin = self.loaded_plugins[plugin_id]
        metadata = self.plugin_metadata.get(plugin_id, {})
        physics_type = plugin.get_physics_type()
        
        return {
            'plugin_id': plugin_id,
            'metadata': metadata,
            'physics_type': physics_type.to_dict(),
            'validation_errors': self.validate_plugin(plugin)
        }
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all loaded plugins with basic information.
        
        Returns:
            List of plugin information dictionaries
        """
        plugins_info = []
        
        for plugin_id, plugin in self.loaded_plugins.items():
            metadata = self.plugin_metadata.get(plugin_id, {})
            physics_type = plugin.get_physics_type()
            
            plugins_info.append({
                'plugin_id': plugin_id,
                'name': metadata.get('name', 'Unknown'),
                'version': metadata.get('version', '1.0.0'),
                'category': metadata.get('category', 'unknown'),
                'physics_type_name': physics_type.name,
                'physics_type_category': physics_type.category,
                'description': metadata.get('description', '')
            })
        
        return plugins_info 