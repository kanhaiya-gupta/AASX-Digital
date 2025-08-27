# Complete Configuration System

This document describes the complete configuration system for the AAS Engine, including the newly implemented **secrets management** and **application settings** components.

## 🏗️ Architecture Overview

The configuration system consists of three main components:

1. **Configuration Management** - Core configuration loading, validation, and management
2. **Secrets Management** - Secure storage and retrieval of sensitive data
3. **Application Settings** - Environment-specific application configuration

```
src/engine/config/
├── __init__.py              # Package exports
├── config_manager.py        # Configuration orchestration
├── config_loader.py         # Configuration loading from various sources
├── config_validator.py      # Configuration validation
├── config_schema.py         # JSON schemas for validation
├── engine_config.py         # Main configuration classes
├── environment_config.py    # Environment detection and configuration
├── secrets.py              # 🔐 NEW: Secret management system
└── settings.py             # ⚙️ NEW: Application settings system
```

## 🔐 Secrets Management System

### Overview

The secrets management system provides secure storage, retrieval, and management of sensitive configuration data including API keys, passwords, tokens, and other secrets.

### Key Features

- **Encrypted Storage**: All secrets are encrypted using Fernet (symmetric encryption)
- **Environment Variable Support**: Integration with environment variables
- **Metadata Management**: Track creation, updates, expiration, and tags
- **Secret Validation**: Password strength and API key format validation
- **Secret Rotation**: Secure secret rotation capabilities
- **Search and Discovery**: Search secrets by name, description, or tags

### Components

#### SecretManager

The main class for managing encrypted secrets.

```python
from engine.config import SecretManager

# Initialize with custom settings
secret_manager = SecretManager(
    master_key="your-master-key",  # Auto-generated if None
    secrets_file="~/.aas_engine/secrets.enc",
    auto_encrypt=True
)

# Store a secret
secret_manager.set_secret(
    name="api_key",
    value="sk_test_12345",
    description="Stripe API key for payments",
    tags=["payment", "stripe"],
    expires_at="2024-12-31T23:59:59"
)

# Retrieve a secret
api_key = secret_manager.get_secret("api_key", default="")

# List all secrets
secrets = secret_manager.list_secrets()

# Search secrets
results = secret_manager.search_secrets("payment")

# Rotate a secret
secret_manager.rotate_secret("api_key", "sk_test_67890")

# Delete a secret
secret_manager.delete_secret("old_api_key")
```

#### EnvironmentSecretManager

Manages secrets from environment variables with configurable prefixes.

```python
from engine.config import EnvironmentSecretManager

# Initialize with custom prefix
env_manager = EnvironmentSecretManager(prefix="AAS_ENGINE_")

# Get secret from environment variable AAS_ENGINE_DB_PASSWORD
db_password = env_manager.get_secret("db_password")

# Set secret in environment
env_manager.set_secret("api_key", "new_api_key_value")

# List environment secrets
env_secrets = env_manager.list_secrets()

# Refresh from environment
env_manager.refresh()
```

#### SecretValidator

Validates secret strength and compliance.

```python
from engine.config import SecretValidator

# Validate password strength
result = SecretValidator.validate_password_strength(
    password="MySecurePass123!",
    min_length=8,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True
)

if result['valid']:
    print(f"Password score: {result['score']}/100")
    print("Strengths:", result['strengths'])
else:
    print("Issues:", result['issues'])

# Validate API key format
api_result = SecretValidator.validate_api_key_format(
    api_key="sk_test_1234567890abcdef",
    expected_length=32
)
```

#### Global Functions

Convenient global functions for common operations.

```python
from engine.config import get_secret, set_secret

# Get secret using global manager
api_key = get_secret("api_key", default="")

# Set secret using global manager
set_secret("new_secret", "secret_value", description="New secret")
```

## ⚙️ Application Settings System

### Overview

The application settings system provides centralized management of application settings with defaults, overrides, and environment-specific configurations.

### Key Features

- **Environment Detection**: Automatic environment detection from multiple sources
- **Hierarchical Settings**: Nested configuration with dot notation access
- **Environment Overrides**: Automatic environment-specific setting overrides
- **Configuration Persistence**: Save and load configurations in YAML/JSON
- **Validation**: Built-in settings validation with issue reporting
- **Type Safety**: Strongly typed settings with dataclass definitions

### Components

#### ApplicationSettings

The main settings container with all configuration options.

```python
from engine.config import ApplicationSettings

# Create settings with defaults
settings = ApplicationSettings()

# Access nested settings
db_host = settings.database.host
enable_mfa = settings.security.enable_mfa
log_level = settings.logging.level
```

#### SettingsManager

Manages application settings with environment-specific overrides.

```python
from engine.config import SettingsManager, AppEnvironment

# Initialize with custom environment
settings_manager = SettingsManager(
    config_dir="~/.aas_engine/config",
    environment=AppEnvironment.PRODUCTION
)

# Get setting using dot notation
db_host = settings_manager.get_setting("database.host", default="localhost")
api_port = settings_manager.get_setting("api.port", default=8000)

# Set setting using dot notation
settings_manager.set_setting("database.host", "prod-db.example.com")
settings_manager.set_setting("api.port", 9000)

# Save configuration
settings_manager.save_configuration("production_config.yaml")

# Export settings
yaml_config = settings_manager.export_settings("yaml")
json_config = settings_manager.export_settings("json")

# Validate settings
issues = settings_manager.validate_settings()
for category, messages in issues.items():
    print(f"{category}: {messages}")
```

#### Environment Detection

The system automatically detects the current environment:

```python
# Environment variables
export AAS_ENGINE_ENV=production

# Debug mode
export DEBUG=true

# Test mode (automatic when running pytest/unittest)
pytest tests/
```

#### Environment-Specific Overrides

Automatic overrides based on environment:

- **Production**: Enhanced security, file logging, metrics enabled
- **Testing**: Debug mode, test database, minimal monitoring
- **Staging**: Info logging, metrics enabled
- **Development**: Debug mode, console logging

### Global Functions

Convenient global functions for settings management.

```python
from engine.config import (
    get_setting, set_setting, get_settings, get_environment
)

# Get setting using global manager
db_host = get_setting("database.host", default="localhost")

# Set setting using global manager
set_setting("api.port", 9000)

# Get all settings
all_settings = get_settings()

# Get current environment
current_env = get_environment()
```

## 🔗 Integration Examples

### Database Configuration with Secrets

```python
from engine.config import get_secret, set_setting

# Store database credentials securely
set_secret("db_password", "SecureDBPass123!")
set_secret("db_user", "aas_user")

# Configure database settings using secrets
set_setting("database.username", get_secret("db_user"))
set_setting("database.password", get_secret("db_password"))
set_setting("database.host", "prod-db.example.com")
set_setting("database.port", 5432)
```

### Environment-Specific Configuration

```python
from engine.config import SettingsManager, AppEnvironment

# Production settings
prod_manager = SettingsManager(environment=AppEnvironment.PRODUCTION)
prod_manager.set_setting("logging.level", "WARNING")
prod_manager.set_setting("logging.enable_file", True)
prod_manager.set_setting("security.enable_mfa", True)
prod_manager.set_setting("monitoring.enable_metrics", True)

# Save production configuration
prod_manager.save_configuration("config.production.yaml")

# Testing settings
test_manager = SettingsManager(environment=AppEnvironment.TESTING)
test_manager.set_setting("database.database", "aas_engine_test")
test_manager.set_setting("logging.level", "DEBUG")
test_manager.set_setting("cache.enable_memory_cache", True)
```

### API Configuration with Rate Limiting

```python
from engine.config import set_setting

# Configure API settings
set_setting("api.host", "0.0.0.0")
set_setting("api.port", 8000)
set_setting("api.debug", False)
set_setting("api.workers", 4)
set_setting("api.rate_limit_enabled", True)
set_setting("api.rate_limit_requests", 100)
set_setting("api.rate_limit_window", 60)

# Configure CORS
set_setting("api.cors_origins", ["https://app.example.com", "https://api.example.com"])
set_setting("api.cors_allow_credentials", True)
```

## 🧪 Testing

Run the complete configuration system tests:

```bash
cd scripts
python test_config_complete.py
```

This will test:
- Secrets management system
- Application settings system
- Integration between components
- All major functionality

## 📁 Configuration Files

### Example Configuration Structure

```
~/.aas_engine/
├── config/
│   ├── config.yaml              # Main configuration
│   ├── config.production.yaml   # Production overrides
│   ├── config.testing.yaml      # Testing overrides
│   └── user_config.yaml         # User-specific overrides
└── secrets.enc                  # Encrypted secrets file
```

### Example Configuration File

```yaml
name: "AAS Engine"
version: "1.0.0"
environment: "production"
debug: false

database:
  host: "prod-db.example.com"
  port: 5432
  database: "aas_engine_prod"
  username: "aas_user"
  ssl_mode: "require"

security:
  enable_mfa: true
  enable_audit_logging: true
  session_timeout: 1800

logging:
  level: "WARNING"
  enable_file: true
  file_path: "/var/log/aas_engine/app.log"

monitoring:
  enable_metrics: true
  enable_health_checks: true
  metrics_interval: 60
```

## 🚀 Usage Best Practices

### 1. Environment Separation

- Use different configuration files for different environments
- Store sensitive data in secrets, not in configuration files
- Use environment variables for deployment-specific settings

### 2. Security

- Never commit secrets to version control
- Use strong master keys for secret encryption
- Rotate secrets regularly
- Validate secret strength and format

### 3. Configuration Management

- Use dot notation for nested setting access
- Validate settings before use
- Provide sensible defaults
- Document configuration options

### 4. Integration

- Use secrets for sensitive configuration values
- Integrate with existing environment variable systems
- Provide fallback values for missing settings
- Log configuration changes for audit purposes

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Encryption Errors**: Check master key format and permissions
3. **File Permission Errors**: Verify directory permissions for config and secrets
4. **Environment Detection Issues**: Check environment variables and detection logic

### Debug Mode

Enable debug logging to troubleshoot configuration issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validation Issues

Use the validation system to identify configuration problems:

```python
from engine.config import get_global_settings_manager

manager = get_global_settings_manager()
issues = manager.validate_settings()

for category, messages in issues.items():
    print(f"{category}:")
    for message in messages:
        print(f"  - {message}")
```

## 📚 API Reference

For detailed API documentation, see the individual module docstrings and type hints in the source code.

## 🤝 Contributing

When adding new configuration options:

1. Add new fields to appropriate settings dataclasses
2. Update environment-specific overrides if needed
3. Add validation rules in the validation system
4. Update documentation and examples
5. Add comprehensive tests



