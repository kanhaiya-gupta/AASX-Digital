"""
Configuration Loader

Handles loading configurations from various sources including
files, environment variables, databases, and remote services.
"""

import os
import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import asdict, dataclass
from enum import Enum

from .engine_config import EngineConfig
from .environment_config import EnvironmentConfig


class ConfigSource(str, Enum):
    """Configuration source types."""
    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    REMOTE = "remote"
    DEFAULT = "default"


@dataclass
class ConfigLocation:
    """Configuration location information."""
    source: ConfigSource
    path: Optional[str] = None
    url: Optional[str] = None
    database: Optional[str] = None
    table: Optional[str] = None
    key: Optional[str] = None
    format: Optional[str] = None  # json, yaml, toml, env
    encoding: str = "utf-8"


class ConfigLoader:
    """Configuration loader for various sources."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize configuration loader."""
        self.base_path = base_path or Path.cwd()
        self.config_cache: Dict[str, Any] = {}
        self.loaded_sources: List[ConfigLocation] = []
    
    def load_config(self, location: ConfigLocation) -> Dict[str, Any]:
        """Load configuration from a specific location."""
        try:
            if location.source == ConfigSource.ENVIRONMENT:
                config = self._load_from_environment()
            elif location.source == ConfigSource.FILE:
                config = self._load_from_file(location)
            elif location.source == ConfigSource.DATABASE:
                config = self._load_from_database(location)
            elif location.source == ConfigSource.REMOTE:
                config = self._load_from_remote(location)
            elif location.source == ConfigSource.DEFAULT:
                config = self._load_default_config()
            else:
                raise ValueError(f"Unsupported configuration source: {location.source}")
            
            # Cache the configuration
            cache_key = f"{location.source}_{location.path or location.url or 'default'}"
            self.config_cache[cache_key] = config
            self.loaded_sources.append(location)
            
            return config
            
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {location.source}: {e}")
    
    def load_engine_config(self, location: ConfigLocation) -> EngineConfig:
        """Load and create EngineConfig from configuration data."""
        config_data = self.load_config(location)
        
        # Create environment config
        env_data = config_data.get("environment", {})
        environment = EnvironmentConfig.from_environment(env_data.get("name"))
        
        # Update environment with loaded data
        for key, value in env_data.items():
            if hasattr(environment, key):
                setattr(environment, key, value)
        
        # Create engine config
        engine_config = EngineConfig(environment=environment)
        
        # Update component configurations
        self._update_component_config(engine_config.database, config_data.get("database", {}))
        self._update_component_config(engine_config.messaging, config_data.get("messaging", {}))
        self._update_component_config(engine_config.caching, config_data.get("caching", {}))
        self._update_component_config(engine_config.security, config_data.get("security", {}))
        self._update_component_config(engine_config.monitoring, config_data.get("monitoring", {}))
        self._update_component_config(engine_config.utils, config_data.get("utils", {}))
        self._update_component_config(engine_config.logging, config_data.get("logging", {}))
        self._update_component_config(engine_config.performance, config_data.get("performance", {}))
        
        # Update custom settings
        engine_config.custom_settings = config_data.get("custom_settings", {})
        
        # Update metadata
        engine_config.config_id = config_data.get("config_id", engine_config.config_id)
        engine_config.version = config_data.get("version", engine_config.version)
        engine_config.name = config_data.get("name", engine_config.name)
        engine_config.description = config_data.get("description", engine_config.description)
        
        return engine_config
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # Database configuration
        config["database"] = {
            "enabled": os.getenv("DB_ENABLED", "true").lower() == "true",
            "settings": {
                "type": os.getenv("DB_TYPE", "sqlite"),
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "name": os.getenv("DB_NAME", "aas_engine"),
                "username": os.getenv("DB_USER", "aas_user"),
                "password": os.getenv("DB_PASSWORD", ""),
                "url": os.getenv("DB_URL"),
                "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20"))
            }
        }
        
        # Cache configuration
        config["caching"] = {
            "enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
            "settings": {
                "type": os.getenv("CACHE_TYPE", "memory"),
                "host": os.getenv("CACHE_HOST", "localhost"),
                "port": int(os.getenv("CACHE_PORT", "6379")),
                "db": int(os.getenv("CACHE_DB", "0")),
                "password": os.getenv("CACHE_PASSWORD"),
                "max_size": int(os.getenv("CACHE_MAX_SIZE", "1000")),
                "default_ttl": int(os.getenv("CACHE_DEFAULT_TTL", "3600"))
            }
        }
        
        # Security configuration
        config["security"] = {
            "enabled": os.getenv("SECURITY_ENABLED", "true").lower() == "true",
            "settings": {
                "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key-change-in-production"),
                "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
                "jwt_expiration": int(os.getenv("JWT_EXPIRATION", "3600")),
                "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
            }
        }
        
        # Monitoring configuration
        config["monitoring"] = {
            "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            "settings": {
                "metrics_enabled": os.getenv("METRICS_ENABLED", "true").lower() == "true",
                "health_enabled": os.getenv("HEALTH_ENABLED", "true").lower() == "true",
                "profiling_enabled": os.getenv("PROFILING_ENABLED", "true").lower() == "true"
            }
        }
        
        # Logging configuration
        config["logging"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": os.getenv("LOG_FORMAT", "json"),
            "output": os.getenv("LOG_OUTPUT", "file")
        }
        
        return config
    
    def _load_from_file(self, location: ConfigLocation) -> Dict[str, Any]:
        """Load configuration from file."""
        if not location.path:
            raise ValueError("File path is required for file-based configuration")
        
        file_path = Path(location.path)
        if not file_path.is_absolute():
            file_path = self.base_path / file_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Determine format from file extension or specified format
        if location.format:
            file_format = location.format.lower()
        else:
            file_format = file_path.suffix.lower().lstrip(".")
        
        try:
            with open(file_path, 'r', encoding=location.encoding) as f:
                if file_format in ["json", "js"]:
                    return json.load(f)
                elif file_format in ["yaml", "yml"]:
                    return yaml.safe_load(f)
                elif file_format in ["toml"]:
                    return toml.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse configuration file {file_path}: {e}")
    
    def _load_from_database(self, location: ConfigLocation) -> Dict[str, Any]:
        """Load configuration from database."""
        # This would require database connection setup
        # For now, return empty config
        raise NotImplementedError("Database configuration loading not yet implemented")
    
    def _load_from_remote(self, location: ConfigLocation) -> Dict[str, Any]:
        """Load configuration from remote service."""
        # This would require HTTP client setup
        # For now, return empty config
        raise NotImplementedError("Remote configuration loading not yet implemented")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        # Create a default EngineConfig and convert to dict
        default_config = EngineConfig()
        return default_config.to_dict()
    
    def _update_component_config(self, component: Any, config_data: Dict[str, Any]) -> None:
        """Update component configuration with loaded data."""
        if not config_data:
            return
        
        # Update component attributes
        for key, value in config_data.items():
            if hasattr(component, key):
                if key == "settings" and hasattr(component, "settings"):
                    # Update settings object
                    settings = getattr(component, "settings")
                    if hasattr(settings, "__dict__"):
                        for setting_key, setting_value in value.items():
                            if hasattr(settings, setting_key):
                                setattr(settings, setting_key, setting_value)
                else:
                    # Update component attribute directly
                    setattr(component, key, value)
    
    def save_config(self, config: EngineConfig, location: ConfigLocation) -> bool:
        """Save configuration to a specific location."""
        try:
            if location.source == ConfigSource.FILE:
                return self._save_to_file(config, location)
            elif location.source == ConfigSource.DATABASE:
                return self._save_to_database(config, location)
            elif location.source == ConfigSource.REMOTE:
                return self._save_to_remote(config, location)
            else:
                raise ValueError(f"Cannot save to source type: {location.source}")
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration to {location.source}: {e}")
    
    def _save_to_file(self, config: EngineConfig, location: ConfigLocation) -> bool:
        """Save configuration to file."""
        if not location.path:
            raise ValueError("File path is required for file-based configuration")
        
        file_path = Path(location.path)
        if not file_path.is_absolute():
            file_path = self.base_path / file_path
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format from file extension or specified format
        if location.format:
            file_format = location.format.lower()
        else:
            file_format = file_path.suffix.lower().lstrip(".")
        
        config_data = config.to_dict()
        
        try:
            with open(file_path, 'w', encoding=location.encoding) as f:
                if file_format in ["json", "js"]:
                    json.dump(config_data, f, indent=2, default=str)
                elif file_format in ["yaml", "yml"]:
                    yaml.dump(config_data, f, default_flow_style=False, default_style=None)
                elif file_format in ["toml"]:
                    toml.dump(config_data, f)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration file {file_path}: {e}")
    
    def _save_to_database(self, config: EngineConfig, location: ConfigLocation) -> bool:
        """Save configuration to database."""
        raise NotImplementedError("Database configuration saving not yet implemented")
    
    def _save_to_remote(self, config: EngineConfig, location: ConfigLocation) -> bool:
        """Save configuration to remote service."""
        raise NotImplementedError("Remote configuration saving not yet implemented")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached configurations."""
        return {
            "cache_size": len(self.config_cache),
            "cached_keys": list(self.config_cache.keys()),
            "loaded_sources": [source.source.value for source in self.loaded_sources]
        }
    
    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self.config_cache.clear()
        self.loaded_sources.clear()
    
    def reload_config(self, location: ConfigLocation) -> Dict[str, Any]:
        """Reload configuration from a specific location."""
        # Clear cache for this location
        cache_key = f"{location.source}_{location.path or location.url or 'default'}"
        if cache_key in self.config_cache:
            del self.config_cache[cache_key]
        
        # Remove from loaded sources
        self.loaded_sources = [s for s in self.loaded_sources if not (
            s.source == location.source and 
            s.path == location.path and 
            s.url == location.url
        )]
        
        # Reload
        return self.load_config(location)



