"""
Configuration Manager

Centralized configuration management for the AAS Data Modeling Engine.
Provides a unified interface for loading, validating, and managing configurations.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime, timezone

from .engine_config import EngineConfig
from .environment_config import EnvironmentConfig, ConfigEnvironment
from .config_loader import ConfigLoader, ConfigLocation, ConfigSource
from .config_validator import ConfigValidator, ValidationLevel, ValidationResult
from .config_schema import ConfigSchema


class ConfigManager:
    """Centralized configuration manager for the engine."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize configuration manager."""
        self.base_path = base_path or Path.cwd()
        self.loader = ConfigLoader(self.base_path)
        self.validator = ConfigValidator()
        self.current_config: Optional[EngineConfig] = None
        self.config_history: List[EngineConfig] = []
        self.max_history_size = 10
        
        # Default configuration locations
        self.default_locations = {
            ConfigEnvironment.DEVELOPMENT: [
                ConfigLocation(source=ConfigSource.FILE, path="config/dev.json"),
                ConfigLocation(source=ConfigSource.ENVIRONMENT),
                ConfigLocation(source=ConfigSource.DEFAULT)
            ],
            ConfigEnvironment.TESTING: [
                ConfigLocation(source=ConfigSource.FILE, path="config/test.json"),
                ConfigLocation(source=ConfigSource.ENVIRONMENT),
                ConfigLocation(source=ConfigSource.DEFAULT)
            ],
            ConfigEnvironment.STAGING: [
                ConfigLocation(source=ConfigSource.FILE, path="config/staging.json"),
                ConfigLocation(source=ConfigSource.ENVIRONMENT),
                ConfigLocation(source=ConfigSource.DEFAULT)
            ],
            ConfigEnvironment.PRODUCTION: [
                ConfigLocation(source=ConfigSource.FILE, path="config/prod.json"),
                ConfigLocation(source=ConfigSource.ENVIRONMENT),
                ConfigLocation(source=ConfigSource.DEFAULT)
            ],
            ConfigEnvironment.DEMO: [
                ConfigLocation(source=ConfigSource.FILE, path="config/demo.json"),
                ConfigLocation(source=ConfigSource.ENVIRONMENT),
                ConfigLocation(source=ConfigSource.DEFAULT)
            ]
        }
    
    def load_config(self, environment: Optional[Union[str, ConfigEnvironment]] = None,
                   locations: Optional[List[ConfigLocation]] = None,
                   validate: bool = True) -> EngineConfig:
        """Load configuration for the specified environment."""
        # Determine environment
        if environment is None:
            env_name = os.getenv("ENVIRONMENT", "development")
            environment = ConfigEnvironment(env_name)
        elif isinstance(environment, str):
            environment = ConfigEnvironment(environment)
        
        # Use default locations if none specified
        if locations is None:
            locations = self.default_locations.get(environment, [ConfigLocation(source=ConfigSource.DEFAULT)])
        
        # Try to load from each location
        config = None
        last_error = None
        
        for location in locations:
            try:
                config = self.loader.load_engine_config(location)
                break
            except Exception as e:
                last_error = e
                continue
        
        if config is None:
            if last_error:
                raise RuntimeError(f"Failed to load configuration from all sources: {last_error}")
            else:
                raise RuntimeError("No configuration sources available")
        
        # Validate configuration if requested
        if validate:
            validation_result = self.validator.validate_config(config)
            if not validation_result.is_valid:
                print(f"Configuration validation warnings: {len(validation_result.warnings)}")
                for warning in validation_result.warnings:
                    print(f"  Warning: {warning.path} - {warning.message}")
                
                if validation_result.has_errors():
                    print(f"Configuration validation errors: {len(validation_result.errors)}")
                    for error in validation_result.errors:
                        print(f"  Error: {error.path} - {error.message}")
                    raise RuntimeError("Configuration validation failed")
        
        # Store configuration
        self._store_config(config)
        
        return config
    
    def load_config_from_file(self, file_path: Union[str, Path], validate: bool = True) -> EngineConfig:
        """Load configuration from a specific file."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        location = ConfigLocation(
            source=ConfigSource.FILE,
            path=str(file_path),
            format=file_path.suffix.lstrip(".")
        )
        
        config = self.loader.load_engine_config(location)
        
        if validate:
            validation_result = self.validator.validate_config(config)
            if not validation_result.is_valid:
                if validation_result.has_errors():
                    raise RuntimeError("Configuration validation failed")
        
        self._store_config(config)
        return config
    
    def load_config_from_environment(self, validate: bool = True) -> EngineConfig:
        """Load configuration from environment variables."""
        location = ConfigLocation(source=ConfigSource.ENVIRONMENT)
        config = self.loader.load_engine_config(location)
        
        if validate:
            validation_result = self.validator.validate_config(config)
            if not validation_result.is_valid:
                if validation_result.has_errors():
                    raise RuntimeError("Configuration validation failed")
        
        self._store_config(config)
        return config
    
    def save_config(self, config: Optional[EngineConfig] = None,
                   file_path: Optional[Union[str, Path]] = None,
                   format: str = "json") -> bool:
        """Save configuration to file."""
        if config is None:
            config = self.current_config
        
        if config is None:
            raise RuntimeError("No configuration to save")
        
        if file_path is None:
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.base_path / "config" / f"engine_config_{timestamp}.{format}"
        
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        location = ConfigLocation(
            source=ConfigSource.FILE,
            path=str(file_path),
            format=format
        )
        
        return self.loader.save_config(config, location)
    
    def validate_config(self, config: Optional[EngineConfig] = None) -> ValidationResult:
        """Validate configuration."""
        if config is None:
            config = self.current_config
        
        if config is None:
            raise RuntimeError("No configuration to validate")
        
        return self.validator.validate_config(config)
    
    def get_config(self) -> Optional[EngineConfig]:
        """Get current configuration."""
        return self.current_config
    
    def get_component_config(self, component: str) -> Any:
        """Get configuration for a specific component."""
        if self.current_config is None:
            raise RuntimeError("No configuration loaded")
        
        return self.current_config.get_component_config(component)
    
    def is_component_enabled(self, component: str) -> bool:
        """Check if a component is enabled."""
        if self.current_config is None:
            return False
        
        return self.current_config.is_component_enabled(component)
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """Get a configuration setting using dot notation."""
        if self.current_config is None:
            return default
        
        return self.current_config.get_setting(path, default)
    
    def set_setting(self, path: str, value: Any) -> bool:
        """Set a configuration setting using dot notation."""
        if self.current_config is None:
            return False
        
        return self.current_config.set_setting(path, value)
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values."""
        if self.current_config is None:
            return False
        
        success = True
        for path, value in updates.items():
            if not self.current_config.set_setting(path, value):
                success = False
        
        if success:
            self._store_config(self.current_config)
        
        return success
    
    def reload_config(self, environment: Optional[Union[str, ConfigEnvironment]] = None) -> EngineConfig:
        """Reload configuration."""
        # Clear current configuration
        self.current_config = None
        
        # Reload
        return self.load_config(environment)
    
    def get_config_history(self) -> List[EngineConfig]:
        """Get configuration history."""
        return self.config_history.copy()
    
    def rollback_config(self, index: int = -1) -> bool:
        """Rollback to a previous configuration."""
        if not self.config_history or index >= len(self.config_history):
            return False
        
        config = self.config_history[index]
        self._store_config(config)
        return True
    
    def export_config(self, format: str = "json", include_sensitive: bool = False) -> str:
        """Export configuration to string."""
        if self.current_config is None:
            raise RuntimeError("No configuration to export")
        
        config_data = self.current_config.to_dict()
        
        if not include_sensitive:
            # Remove sensitive information
            self._remove_sensitive_data(config_data)
        
        if format.lower() == "json":
            import json
            return json.dumps(config_data, indent=2, default=str)
        elif format.lower() == "yaml":
            import yaml
            return yaml.dump(config_data, default_flow_style=False, default_style=None)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_schema(self, component: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration schema."""
        if component is None:
            return ConfigSchema.get_engine_config_schema()
        else:
            return ConfigSchema.get_schema_by_component(component) or {}
    
    def create_default_config(self, environment: Union[str, ConfigEnvironment] = "development") -> EngineConfig:
        """Create a default configuration for the specified environment."""
        if isinstance(environment, str):
            environment = ConfigEnvironment(environment)
        
        # Create environment config
        env_config = EnvironmentConfig.from_environment(environment.name)
        
        # Create engine config with environment
        config = EngineConfig(environment=env_config)
        
        # Store configuration
        self._store_config(config)
        
        return config
    
    def _store_config(self, config: EngineConfig) -> None:
        """Store configuration in history and set as current."""
        # Add to history
        self.config_history.append(config)
        
        # Limit history size
        if len(self.config_history) > self.max_history_size:
            self.config_history.pop(0)
        
        # Set as current
        self.current_config = config
    
    def _remove_sensitive_data(self, config_data: Dict[str, Any]) -> None:
        """Remove sensitive information from configuration data."""
        sensitive_keys = [
            "jwt_secret", "password", "secret_key", "api_key",
            "ssl_key", "ssl_cert", "smtp_password"
        ]
        
        def _clean_dict(data: Any) -> None:
            if isinstance(data, dict):
                for key in list(data.keys()):
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        data[key] = "***REDACTED***"
                    else:
                        _clean_dict(data[key])
            elif isinstance(data, list):
                for item in data:
                    _clean_dict(item)
        
        _clean_dict(config_data)


class AsyncConfigManager(ConfigManager):
    """Asynchronous configuration manager."""
    
    async def load_config_async(self, environment: Optional[Union[str, ConfigEnvironment]] = None,
                               locations: Optional[List[ConfigLocation]] = None,
                               validate: bool = True) -> EngineConfig:
        """Load configuration asynchronously."""
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.load_config, environment, locations, validate
        )
    
    async def load_config_from_file_async(self, file_path: Union[str, Path], 
                                        validate: bool = True) -> EngineConfig:
        """Load configuration from file asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.load_config_from_file, file_path, validate
        )
    
    async def load_config_from_environment_async(self, validate: bool = True) -> EngineConfig:
        """Load configuration from environment asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.load_config_from_environment, validate
        )
    
    async def save_config_async(self, config: Optional[EngineConfig] = None,
                               file_path: Optional[Union[str, Path]] = None,
                               format: str = "json") -> bool:
        """Save configuration asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.save_config, config, file_path, format
        )
    
    async def validate_config_async(self, config: Optional[EngineConfig] = None) -> ValidationResult:
        """Validate configuration asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.validate_config, config
        )
    
    async def reload_config_async(self, environment: Optional[Union[str, ConfigEnvironment]] = None) -> EngineConfig:
        """Reload configuration asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.reload_config, environment
        )
    
    async def update_config_async(self, updates: Dict[str, Any]) -> bool:
        """Update configuration asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.update_config, updates
        )
    
    async def export_config_async(self, format: str = "json", include_sensitive: bool = False) -> str:
        """Export configuration asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.export_config, format, include_sensitive
        )
    
    async def create_default_config_async(self, environment: Union[str, ConfigEnvironment] = "development") -> EngineConfig:
        """Create default configuration asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.create_default_config, environment
        )


# Global configuration manager instance
_global_config_manager: Optional[ConfigManager] = None


def get_global_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


def set_global_config_manager(manager: ConfigManager) -> None:
    """Set the global configuration manager instance."""
    global _global_config_manager
    _global_config_manager = manager


def get_config() -> Optional[EngineConfig]:
    """Get the current configuration from the global manager."""
    return get_global_config_manager().get_config()


def load_config(environment: Optional[Union[str, ConfigEnvironment]] = None) -> EngineConfig:
    """Load configuration using the global manager."""
    return get_global_config_manager().load_config(environment)
