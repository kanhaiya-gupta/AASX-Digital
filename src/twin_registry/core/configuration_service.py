"""
Configuration Service for Twin Registry
Provides business logic for configuration management
"""

import logging
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from pathlib import Path

from ..config.system_config import (
    SystemConfiguration, ConfigurationManager, ConfigEnvironment, 
    ConfigSecurityLevel, default_config
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConfigurationUpdateRequest(BaseModel):
    """Request model for configuration updates"""
    updates: Dict[str, Any]
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    environment: Optional[str] = None


class ConfigurationValidationResult(BaseModel):
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    timestamp: str
    config_id: str


class ConfigurationHistoryEntry(BaseModel):
    """Configuration history entry"""
    config_id: str
    version: str
    environment: str
    created_at: str
    created_by: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    change_summary: Optional[str] = None


class ConfigurationService:
    """Service for managing Twin Registry configuration"""
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.config_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = 0
        
        # Initialize with default configuration
        self._ensure_default_config()
    
    def _ensure_default_config(self) -> None:
        """Ensure default configuration exists"""
        try:
            if not self.config_manager.config.config_id:
                self.config_manager.config = default_config
                self.config_manager.save_configuration()
                logger.info("Default configuration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize default configuration: {e}")
    
    def get_configuration(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get current configuration"""
        try:
            if use_cache and self._is_cache_valid():
                return self.config_cache
            
            config = self.config_manager.get_configuration()
            config_dict = config.to_dict()
            
            # Update cache
            self.config_cache = config_dict
            self.last_cache_update = datetime.now().timestamp()
            
            return config_dict
        except Exception as e:
            logger.error(f"Failed to get configuration: {e}")
            return default_config.to_dict()
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        current_time = datetime.now().timestamp()
        return (current_time - self.last_cache_update) < self.cache_ttl
    
    def get_configuration_section(self, section: str) -> Dict[str, Any]:
        """Get specific configuration section"""
        try:
            config = self.config_manager.get_configuration()
            if hasattr(config, section):
                section_config = getattr(config, section)
                return section_config.__dict__
            else:
                logger.warning(f"Configuration section '{section}' not found")
                return {}
        except Exception as e:
            logger.error(f"Failed to get configuration section '{section}': {e}")
            return {}
    
    def update_configuration(self, updates: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Update configuration with new values"""
        try:
            # Validate updates
            validation_result = self._validate_updates(updates)
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "errors": validation_result["errors"],
                    "message": "Configuration validation failed"
                }
            
            # Apply updates
            success = self.config_manager.update_configuration(updates)
            if not success:
                return {
                    "success": False,
                    "message": "Failed to update configuration"
                }
            
            # Update metadata
            if user_id:
                self.config_manager.config.updated_by = user_id
                self.config_manager.config.updated_at = datetime.now(timezone.utc)
            
            # Save configuration
            if self.config_manager.save_configuration():
                # Clear cache
                self.config_cache = {}
                self.last_cache_update = 0
                
                return {
                    "success": True,
                    "message": "Configuration updated successfully",
                    "config_id": self.config_manager.config.config_id,
                    "timestamp": self.config_manager.config.updated_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save configuration"
                }
                
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return {
                "success": False,
                "message": f"Configuration update failed: {str(e)}"
            }
    
    def _validate_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration updates"""
        errors = []
        warnings = []
        
        try:
            # Create a temporary configuration for validation
            temp_config = SystemConfiguration.from_dict(self.config_manager.config.to_dict())
            
            # Apply updates to temporary config
            for key, value in updates.items():
                if hasattr(temp_config, key):
                    setattr(temp_config, key, value)
                else:
                    # Try to update nested settings
                    if not temp_config.set_setting(key, value):
                        errors.append(f"Invalid configuration path: {key}")
            
            # Validate the temporary configuration
            if not temp_config.is_valid():
                errors.extend(temp_config.validate())
            
            # Check for warnings
            if temp_config.registry.max_twins > 100000:
                warnings.append("max_twins is very high, consider reducing for performance")
            if temp_config.monitoring.monitoring_interval_seconds < 10:
                warnings.append("monitoring_interval_seconds is very low, may impact performance")
            if temp_config.security.password_min_length < 12:
                warnings.append("password_min_length is below recommended security standards")
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return {
                "is_valid": False,
                "errors": errors,
                "warnings": warnings
            }
    
    def reset_configuration(self, reset_type: str = "defaults", user_id: Optional[str] = None) -> Dict[str, Any]:
        """Reset configuration to defaults or previous version"""
        try:
            success = self.config_manager.reset_configuration(reset_type)
            if not success:
                return {
                    "success": False,
                    "message": f"Failed to reset configuration to {reset_type}"
                }
            
            # Update metadata
            if user_id:
                self.config_manager.config.updated_by = user_id
                self.config_manager.config.updated_at = datetime.now(timezone.utc)
            
            # Save configuration
            if self.config_manager.save_configuration():
                # Clear cache
                self.config_cache = {}
                self.last_cache_update = 0
                
                return {
                    "success": True,
                    "message": f"Configuration reset to {reset_type} successfully",
                    "config_id": self.config_manager.config.config_id,
                    "timestamp": self.config_manager.config.updated_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save reset configuration"
                }
                
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return {
                "success": False,
                "message": f"Configuration reset failed: {str(e)}"
            }
    
    def export_configuration(self, format: str = "json") -> Dict[str, Any]:
        """Export configuration in specified format"""
        try:
            config_data = self.config_manager.export_configuration(format)
            if not config_data:
                return {
                    "success": False,
                    "message": "Failed to export configuration"
                }
            
            return {
                "success": True,
                "format": format,
                "data": config_data,
                "config_id": self.config_manager.config.config_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return {
                "success": False,
                "message": f"Configuration export failed: {str(e)}"
            }
    
    def import_configuration(self, config_data: str, format: str = "json", user_id: Optional[str] = None) -> Dict[str, Any]:
        """Import configuration from string"""
        try:
            success = self.config_manager.import_configuration(config_data, format)
            if not success:
                return {
                    "success": False,
                    "message": "Failed to import configuration"
                }
            
            # Update metadata
            if user_id:
                self.config_manager.config.updated_by = user_id
                self.config_manager.config.updated_at = datetime.now(timezone.utc)
            
            # Save configuration
            if self.config_manager.save_configuration():
                # Clear cache
                self.config_cache = {}
                self.last_cache_update = 0
                
                return {
                    "success": True,
                    "message": "Configuration imported successfully",
                    "config_id": self.config_manager.config.config_id,
                    "timestamp": self.config_manager.config.updated_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save imported configuration"
                }
                
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return {
                "success": False,
                "message": f"Configuration import failed: {str(e)}"
            }
    
    def validate_configuration(self) -> ConfigurationValidationResult:
        """Validate current configuration"""
        try:
            validation_result = self.config_manager.validate_configuration()
            
            return ConfigurationValidationResult(
                is_valid=validation_result["is_valid"],
                errors=validation_result["errors"],
                warnings=validation_result["warnings"],
                timestamp=validation_result["timestamp"],
                config_id=self.config_manager.config.config_id
            )
            
        except Exception as e:
            logger.error(f"Failed to validate configuration: {e}")
            return ConfigurationValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                timestamp=datetime.now(timezone.utc).isoformat(),
                config_id="unknown"
            )
    
    def get_configuration_history(self) -> List[ConfigurationHistoryEntry]:
        """Get configuration history"""
        try:
            history = self.config_manager.get_configuration_history()
            history_entries = []
            
            for config_dict in history:
                entry = ConfigurationHistoryEntry(
                    config_id=config_dict.get("config_id", "unknown"),
                    version=config_dict.get("version", "1.0.0"),
                    environment=config_dict.get("environment", "development"),
                    created_at=config_dict.get("created_at", ""),
                    created_by=config_dict.get("created_by"),
                    description=config_dict.get("description"),
                    tags=config_dict.get("tags", []),
                    change_summary=self._generate_change_summary(config_dict)
                )
                history_entries.append(entry)
            
            return history_entries
            
        except Exception as e:
            logger.error(f"Failed to get configuration history: {e}")
            return []
    
    def _generate_change_summary(self, config_dict: Dict[str, Any]) -> Optional[str]:
        """Generate a summary of changes for a configuration version"""
        try:
            # This is a simplified change summary
            # In a real implementation, you'd compare with previous version
            registry = config_dict.get("registry", {})
            monitoring = config_dict.get("monitoring", {})
            
            changes = []
            if registry.get("max_twins") != 10000:
                changes.append(f"Max twins: {registry.get('max_twins')}")
            if monitoring.get("monitoring_interval_seconds") != 30:
                changes.append(f"Monitoring interval: {monitoring.get('monitoring_interval_seconds')}s")
            
            if changes:
                return f"Updated: {', '.join(changes)}"
            else:
                return "No significant changes"
                
        except Exception:
            return None
    
    def rollback_to_version(self, config_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Rollback to specific configuration version"""
        try:
            success = self.config_manager.rollback_to_version(config_id)
            if not success:
                return {
                    "success": False,
                    "message": f"Failed to rollback to configuration version {config_id}"
                }
            
            # Update metadata
            if user_id:
                self.config_manager.config.updated_by = user_id
                self.config_manager.config.updated_at = datetime.now(timezone.utc)
            
            # Save configuration
            if self.config_manager.save_configuration():
                # Clear cache
                self.config_cache = {}
                self.last_cache_update = 0
                
                return {
                    "success": True,
                    "message": f"Configuration rolled back to version {config_id} successfully",
                    "config_id": self.config_manager.config.config_id,
                    "timestamp": self.config_manager.config.updated_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save rolled back configuration"
                }
                
        except Exception as e:
            logger.error(f"Failed to rollback configuration: {e}")
            return {
                "success": False,
                "message": f"Configuration rollback failed: {str(e)}"
            }
    
    def apply_environment_overrides(self, environment: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Apply environment-specific configuration overrides"""
        try:
            # Convert string to enum
            try:
                env_enum = ConfigEnvironment(environment)
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid environment: {environment}"
                }
            
            # Apply overrides
            self.config_manager.apply_environment_overrides(env_enum)
            
            # Update metadata
            if user_id:
                self.config_manager.config.updated_by = user_id
                self.config_manager.config.updated_at = datetime.now(timezone.utc)
            
            # Save configuration
            if self.config_manager.save_configuration():
                # Clear cache
                self.config_cache = {}
                self.last_cache_update = 0
                
                return {
                    "success": True,
                    "message": f"Environment overrides applied for {environment} successfully",
                    "config_id": self.config_manager.config.config_id,
                    "timestamp": self.config_manager.config.updated_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save environment overrides"
                }
                
        except Exception as e:
            logger.error(f"Failed to apply environment overrides: {e}")
            return {
                "success": False,
                "message": f"Environment overrides failed: {str(e)}"
            }
    
    def get_setting(self, path: str) -> Any:
        """Get specific configuration setting using dot notation"""
        try:
            return self.config_manager.config.get_setting(path)
        except Exception as e:
            logger.error(f"Failed to get setting '{path}': {e}")
            return None
    
    def set_setting(self, path: str, value: Any, user_id: Optional[str] = None) -> bool:
        """Set specific configuration setting using dot notation"""
        try:
            success = self.config_manager.config.set_setting(path, value)
            if success and user_id:
                self.config_manager.config.updated_by = user_id
                self.config_manager.config.updated_at = datetime.now(timezone.utc)
                self.config_manager.save_configuration()
                
                # Clear cache
                self.config_cache = {}
                self.last_cache_update = 0
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to set setting '{path}': {e}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary for dashboard"""
        try:
            config = self.config_manager.get_configuration()
            
            return {
                "config_id": config.config_id,
                "version": config.version,
                "environment": config.environment.value,
                "security_level": config.security_level.value,
                "last_updated": config.updated_at.isoformat(),
                "updated_by": config.updated_by,
                "is_valid": config.is_valid(),
                "sections": {
                    "registry": {
                        "max_twins": config.registry.max_twins,
                        "enable_relationships": config.registry.enable_relationships,
                        "enable_monitoring": config.registry.enable_performance_monitoring
                    },
                    "monitoring": {
                        "enabled": config.monitoring.enable_monitoring,
                        "interval": config.monitoring.monitoring_interval_seconds,
                        "real_time": config.monitoring.enable_real_time_monitoring
                    },
                    "security": {
                        "auth_enabled": config.security.enable_authentication,
                        "two_factor": config.security.enable_two_factor_auth,
                        "encryption": config.security.enable_data_encryption
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get configuration summary: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def refresh_cache(self) -> None:
        """Refresh configuration cache"""
        self.config_cache = {}
        self.last_cache_update = 0
        logger.info("Configuration cache refreshed")


# Global configuration service instance
configuration_service = ConfigurationService()
