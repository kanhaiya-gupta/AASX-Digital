# Engine Configuration System

The Engine Configuration System provides centralized configuration management for all components of the AAS Data Modeling Engine. It supports multiple configuration sources, validation, and environment-specific settings.

## Overview

The configuration system consists of several key components:

- **Configuration Classes**: Define the structure and default values for all engine components
- **Configuration Loader**: Handles loading configurations from various sources
- **Configuration Validator**: Validates configuration values and ensures requirements are met
- **Configuration Manager**: Provides a unified interface for configuration operations
- **Configuration Schema**: JSON schemas for validation and documentation

## Features

- **Multi-source Configuration**: Support for files (JSON, YAML, TOML), environment variables, and databases
- **Environment-specific Settings**: Different configurations for development, testing, staging, production, and demo
- **Validation**: Comprehensive validation of configuration values with detailed error reporting
- **Hot Reloading**: Ability to reload configurations without restarting the engine
- **Configuration History**: Track configuration changes with rollback capability
- **Schema Support**: JSON schema validation and documentation
- **Async Support**: Asynchronous configuration operations for non-blocking I/O

## Quick Start

### Basic Usage

```python
from engine.config import ConfigManager, load_config

# Create a configuration manager
config_manager = ConfigManager()

# Load configuration for development environment
config = config_manager.load_config("development")

# Access configuration values
db_enabled = config.database.enabled
db_host = config.database.settings.host
cache_ttl = config.caching.settings.default_ttl

# Use global configuration manager
config = load_config("production")
```

### Environment Variables

The system automatically reads configuration from environment variables:

```bash
export ENVIRONMENT=production
export DB_TYPE=postgresql
export DB_HOST=db.example.com
export DB_PORT=5432
export DB_NAME=aas_prod
export DB_USER=aas_user
export DB_PASSWORD=secure_password
export JWT_SECRET=your-super-secret-jwt-key-here
export LOG_LEVEL=INFO
```

### Configuration Files

Create configuration files in JSON, YAML, or TOML format:

```json
{
  "version": "1.0.0",
  "name": "AAS Data Modeling Engine",
  "environment": {
    "name": "production",
    "debug": false,
    "verbose": false
  },
  "database": {
    "enabled": true,
    "settings": {
      "type": "postgresql",
      "host": "db.example.com",
      "port": 5432,
      "name": "aas_prod",
      "username": "aas_user",
      "password": "secure_password"
    }
  },
  "caching": {
    "enabled": true,
    "settings": {
      "type": "redis",
      "host": "redis.example.com",
      "port": 6379,
      "default_ttl": 3600
    }
  }
}
```

## Configuration Components

### Environment Configuration

Controls environment-specific settings and feature flags:

```python
from engine.config import EnvironmentConfig

env_config = EnvironmentConfig.from_environment("production")
print(f"Environment: {env_config.environment}")
print(f"Debug mode: {env_config.debug}")
print(f"Feature flags: {env_config.features}")
```

### Database Configuration

Database connection and pool settings:

```python
from engine.config import DatabaseConfig, DatabaseSettings

db_settings = DatabaseSettings(
    type="postgresql",
    host="localhost",
    port=5432,
    name="aas_engine",
    username="aas_user",
    password="password",
    pool_size=20,
    max_overflow=30
)

db_config = DatabaseConfig(
    enabled=True,
    settings=db_settings,
    auto_migrate=True,
    backup_enabled=True
)
```

### Caching Configuration

Multi-level caching with various backends:

```python
from engine.config import CachingConfig, CacheSettings

cache_settings = CacheSettings(
    type="redis",
    host="localhost",
    port=6379,
    max_size=10000,
    default_ttl=3600
)

cache_config = CachingConfig(
    enabled=True,
    settings=cache_settings,
    multi_level=True,
    eviction_policy="lru"
)
```

### Security Configuration

Authentication, authorization, and encryption settings:

```python
from engine.config import SecurityConfig, SecuritySettings

security_settings = SecuritySettings(
    auth_enabled=True,
    jwt_secret="your-super-secret-key-here",
    jwt_algorithm="HS256",
    jwt_expiration=3600,
    password_min_length=12,
    encryption_enabled=True
)

security_config = SecurityConfig(
    enabled=True,
    settings=security_settings,
    audit_logging=True,
    mfa_enabled=True
)
```

### Monitoring Configuration

Metrics, health checks, and alerting:

```python
from engine.config import MonitoringConfig, MonitoringSettings

monitoring_settings = MonitoringSettings(
    metrics_enabled=True,
    metrics_interval=60,
    health_enabled=True,
    health_interval=30,
    profiling_enabled=True,
    profiling_sampling_rate=0.1
)

monitoring_config = MonitoringConfig(
    enabled=True,
    settings=monitoring_settings,
    error_tracking=True,
    dashboard_enabled=True
)
```

## Advanced Usage

### Custom Configuration Loading

```python
from engine.config import ConfigLocation, ConfigSource

# Load from specific file
location = ConfigLocation(
    source=ConfigSource.FILE,
    path="config/custom.json",
    format="json"
)
config = config_manager.loader.load_engine_config(location)

# Load from environment only
location = ConfigLocation(source=ConfigSource.ENVIRONMENT)
config = config_manager.loader.load_engine_config(location)
```

### Configuration Validation

```python
from engine.config import ConfigValidator, ValidationLevel

validator = ConfigValidator(ValidationLevel.STRICT)
result = validator.validate_config(config)

if not result.is_valid:
    print(f"Validation failed with {len(result.errors)} errors:")
    for error in result.errors:
        print(f"  {error.path}: {error.message}")
else:
    print("Configuration is valid!")
    if result.warnings:
        print(f"Warnings: {len(result.warnings)}")
```

### Configuration Updates

```python
# Update specific settings
updates = {
    "database.settings.pool_size": 25,
    "caching.settings.default_ttl": 7200,
    "monitoring.settings.metrics_interval": 30
}

success = config_manager.update_config(updates)
if success:
    print("Configuration updated successfully!")
```

### Configuration Export

```python
# Export to JSON (sensitive data redacted)
json_config = config_manager.export_config("json", include_sensitive=False)
print(json_config)

# Export to YAML with sensitive data
yaml_config = config_manager.export_config("yaml", include_sensitive=True)
print(yaml_config)
```

### Configuration History and Rollback

```python
# View configuration history
history = config_manager.get_config_history()
print(f"Configuration history: {len(history)} versions")

# Rollback to previous configuration
if config_manager.rollback_config(-1):
    print("Configuration rolled back successfully!")
```

## Async Configuration Operations

For non-blocking I/O operations:

```python
from engine.config import AsyncConfigManager
import asyncio

async def load_config_async():
    async_manager = AsyncConfigManager()
    
    # Load configuration asynchronously
    config = await async_manager.load_config_async("production")
    
    # Validate asynchronously
    validation = await async_manager.validate_config_async(config)
    
    # Save asynchronously
    await async_manager.save_config_async(config, "config/backup.json")
    
    return config

# Run async configuration loading
config = asyncio.run(load_config_async())
```

## Configuration Schema

The system provides JSON schemas for validation and documentation:

```python
from engine.config import ConfigSchema

# Get complete engine schema
engine_schema = ConfigSchema.get_engine_config_schema()

# Get component-specific schemas
db_schema = ConfigSchema.get_database_schema()
monitoring_schema = ConfigSchema.get_monitoring_schema()

# Get schema for specific component
component_schema = ConfigSchema.get_schema_by_component("security")
```

## Best Practices

### 1. Environment Separation

- Use different configuration files for each environment
- Override sensitive values with environment variables
- Keep production configurations secure

### 2. Validation

- Always validate configurations before use
- Use appropriate validation levels (strict for production)
- Handle validation errors gracefully

### 3. Security

- Never commit sensitive configuration to version control
- Use environment variables for secrets
- Regularly rotate sensitive keys

### 4. Monitoring

- Enable configuration change monitoring
- Log configuration updates
- Track configuration validation results

### 5. Performance

- Use async operations for I/O-bound tasks
- Cache validated configurations
- Minimize configuration reloads

## File Structure

```
src/engine/config/
├── __init__.py              # Package exports
├── environment_config.py     # Environment configuration
├── engine_config.py         # Main engine configuration classes
├── config_loader.py         # Configuration loading from various sources
├── config_validator.py      # Configuration validation
├── config_schema.py         # JSON schemas for validation
├── config_manager.py        # Centralized configuration management
└── README.md               # This documentation
```

## Dependencies

The configuration system requires the following Python packages:

- `pyyaml` - For YAML configuration files
- `toml` - For TOML configuration files
- `jsonschema` - For JSON schema validation (optional)

## Examples

See the `examples/` directory for complete configuration examples:

- `examples/dev_config.json` - Development environment configuration
- `examples/prod_config.yaml` - Production environment configuration
- `examples/custom_config.toml` - Custom configuration example

## Troubleshooting

### Common Issues

1. **Configuration not found**: Check file paths and environment variables
2. **Validation errors**: Review configuration values against schemas
3. **Permission errors**: Ensure proper file and directory permissions
4. **Import errors**: Verify all dependencies are installed

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export LOG_LEVEL=DEBUG
```

### Support

For issues and questions:

1. Check the validation results for specific error messages
2. Review the configuration schema for required fields
3. Verify environment variable names and values
4. Check file permissions and paths

## Contributing

When adding new configuration options:

1. Update the appropriate configuration class
2. Add validation rules in `ConfigValidator`
3. Update the JSON schema in `ConfigSchema`
4. Add tests for the new configuration
5. Update this documentation

## License

This configuration system is part of the AAS Data Modeling Engine and follows the same license terms.
