"""
Environment Configuration

Defines configuration environments and environment-specific settings
for the AAS Data Modeling Engine.
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


class ConfigEnvironment(str, Enum):
    """Configuration environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEMO = "demo"


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration settings."""
    
    # Environment identification
    environment: ConfigEnvironment = ConfigEnvironment.DEVELOPMENT
    name: str = "development"
    description: str = "Development environment configuration"
    
    # Environment flags
    debug: bool = True
    verbose: bool = True
    test_mode: bool = False
    
    # Paths and directories
    base_path: Path = field(default_factory=lambda: Path.cwd())
    config_path: Path = field(default_factory=lambda: Path.cwd() / "config")
    data_path: Path = field(default_factory=lambda: Path.cwd() / "data")
    log_path: Path = field(default_factory=lambda: Path.cwd() / "logs")
    temp_path: Path = field(default_factory=lambda: Path.cwd() / "temp")
    cache_path: Path = field(default_factory=lambda: Path.cwd() / "cache")
    
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "hot_reload": True,
        "auto_migration": True,
        "debug_endpoints": True,
        "profiling": True,
        "caching": True,
        "monitoring": True,
        "security": True,
        "audit_logging": True
    })
    
    def __post_init__(self):
        """Post-initialization setup."""
        if isinstance(self.base_path, str):
            self.base_path = Path(self.base_path)
        if isinstance(self.config_path, str):
            self.config_path = Path(self.config_path)
        if isinstance(self.data_path, str):
            self.data_path = Path(self.data_path)
        if isinstance(self.log_path, str):
            self.log_path = Path(self.log_path)
        if isinstance(self.temp_path, str):
            self.temp_path = Path(self.temp_path)
        if isinstance(self.cache_path, str):
            self.cache_path = Path(self.cache_path)
    
    @classmethod
    def from_environment(cls, env_name: Optional[str] = None) -> "EnvironmentConfig":
        """Create environment config from environment variables."""
        if env_name is None:
            env_name = os.getenv("ENVIRONMENT", "development")
        
        # Map environment names to ConfigEnvironment
        env_mapping = {
            "dev": ConfigEnvironment.DEVELOPMENT,
            "development": ConfigEnvironment.DEVELOPMENT,
            "test": ConfigEnvironment.TESTING,
            "testing": ConfigEnvironment.TESTING,
            "staging": ConfigEnvironment.STAGING,
            "prod": ConfigEnvironment.PRODUCTION,
            "production": ConfigEnvironment.PRODUCTION,
            "demo": ConfigEnvironment.DEMO
        }
        
        environment = env_mapping.get(env_name.lower(), ConfigEnvironment.DEVELOPMENT)
        
        # Set environment-specific defaults
        if environment == ConfigEnvironment.DEVELOPMENT:
            return cls(
                environment=environment,
                name=env_name,
                description="Development environment configuration",
                debug=True,
                verbose=True,
                test_mode=False
            )
        elif environment == ConfigEnvironment.TESTING:
            return cls(
                environment=environment,
                name=env_name,
                description="Testing environment configuration",
                debug=True,
                verbose=False,
                test_mode=True
            )
        elif environment == ConfigEnvironment.STAGING:
            return cls(
                environment=environment,
                name=env_name,
                description="Staging environment configuration",
                debug=False,
                verbose=True,
                test_mode=False
            )
        elif environment == ConfigEnvironment.PRODUCTION:
            return cls(
                environment=environment,
                name=env_name,
                description="Production environment configuration",
                debug=False,
                verbose=False,
                test_mode=False
            )
        else:  # DEMO
            return cls(
                environment=environment,
                name=env_name,
                description="Demo environment configuration",
                debug=True,
                verbose=True,
                test_mode=False
            )
    
    def get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable value."""
        return self.env_vars.get(key, os.getenv(key, default))
    
    def set_env_var(self, key: str, value: str) -> None:
        """Set environment variable value."""
        self.env_vars[key] = value
        os.environ[key] = value
    
    def is_development(self) -> bool:
        """Check if this is a development environment."""
        return self.environment == ConfigEnvironment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if this is a testing environment."""
        return self.environment == ConfigEnvironment.TESTING
    
    def is_staging(self) -> bool:
        """Check if this is a staging environment."""
        return self.environment == ConfigEnvironment.STAGING
    
    def is_production(self) -> bool:
        """Check if this is a production environment."""
        return self.environment == ConfigEnvironment.PRODUCTION
    
    def is_demo(self) -> bool:
        """Check if this is a demo environment."""
        return self.environment == ConfigEnvironment.DEMO
    
    def get_feature_flag(self, feature: str) -> bool:
        """Get feature flag value."""
        return self.features.get(feature, False)
    
    def set_feature_flag(self, feature: str, enabled: bool) -> None:
        """Set feature flag value."""
        self.features[feature] = enabled
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for path in [self.config_path, self.data_path, self.log_path, self.temp_path, self.cache_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "environment": self.environment.value,
            "name": self.name,
            "description": self.description,
            "debug": self.debug,
            "verbose": self.verbose,
            "test_mode": self.test_mode,
            "base_path": str(self.base_path),
            "config_path": str(self.config_path),
            "data_path": str(self.data_path),
            "log_path": str(self.log_path),
            "temp_path": str(self.temp_path),
            "cache_path": str(self.cache_path),
            "env_vars": self.env_vars,
            "features": self.features
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"EnvironmentConfig(environment={self.environment.value}, name='{self.name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"EnvironmentConfig(environment={self.environment}, name='{self.name}', debug={self.debug})"
