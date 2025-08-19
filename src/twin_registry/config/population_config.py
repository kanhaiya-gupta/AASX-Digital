"""
Population Configuration for Twin Registry
Manages configuration settings for the population system
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class PopulationMode(Enum):
    """Population modes"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"


class ValidationLevel(Enum):
    """Validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    CUSTOM = "custom"


@dataclass
class PopulationSettings:
    """Population system settings"""
    mode: PopulationMode = PopulationMode.AUTOMATIC
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    max_concurrent_populations: int = 5
    population_timeout: int = 300  # seconds
    retry_attempts: int = 3
    retry_delay: int = 60  # seconds
    cleanup_failed_after: int = 86400  # 24 hours in seconds
    enable_metrics_collection: bool = True
    enable_event_logging: bool = True
    enable_rollback_on_failure: bool = True


@dataclass
class PhaseSettings:
    """Settings for population phases"""
    phase1_enabled: bool = True
    phase1_timeout: int = 120  # seconds
    phase1_retry_count: int = 2
    
    phase2_enabled: bool = True
    phase2_timeout: int = 300  # seconds
    phase2_retry_count: int = 3
    
    phase_transition_delay: int = 10  # seconds


@dataclass
class TriggerSettings:
    """Settings for population triggers"""
    file_upload_enabled: bool = True
    etl_completion_enabled: bool = True
    scheduled_enabled: bool = False
    manual_enabled: bool = True
    
    # File upload trigger settings
    file_upload_delay: int = 5  # seconds
    file_upload_batch_size: int = 10
    
    # ETL completion trigger settings
    etl_completion_delay: int = 30  # seconds
    etl_completion_batch_size: int = 5
    
    # Scheduled trigger settings
    scheduled_interval: int = 3600  # 1 hour in seconds
    scheduled_batch_size: int = 20


@dataclass
class ValidationSettings:
    """Settings for data validation"""
    required_fields: List[str] = None
    optional_fields: List[str] = None
    field_validation_rules: Dict[str, Any] = None
    quality_thresholds: Dict[str, float] = None
    custom_validators: List[str] = None
    
    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = [
                "twin_name", "registry_type", "workflow_source", "user_id", "org_id"
            ]
        
        if self.optional_fields is None:
            self.optional_fields = [
                "description", "tags", "metadata", "config"
            ]
        
        if self.field_validation_rules is None:
            self.field_validation_rules = {
                "twin_name": {"min_length": 3, "max_length": 100},
                "description": {"max_length": 500},
                "tags": {"max_count": 10, "max_length": 50}
            }
        
        if self.quality_thresholds is None:
            self.quality_thresholds = {
                "completeness": 0.8,
                "accuracy": 0.9,
                "consistency": 0.85,
                "timeliness": 0.95
            }


@dataclass
class IntegrationSettings:
    """Settings for external integrations"""
    etl_pipeline_enabled: bool = True
    file_upload_enabled: bool = True
    ai_rag_enabled: bool = False
    
    # ETL pipeline settings
    etl_polling_interval: int = 30  # seconds
    etl_status_check_timeout: int = 60  # seconds
    
    # File upload settings
    file_upload_watch_directory: Optional[str] = None
    file_upload_file_patterns: List[str] = None
    
    # AI/RAG settings
    ai_rag_api_endpoint: Optional[str] = None
    ai_rag_api_key: Optional[str] = None
    ai_rag_timeout: int = 120  # seconds


class PopulationConfig:
    """Configuration manager for twin registry population"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/twin_registry_population.json")
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize default configuration
        self.settings = PopulationSettings()
        self.phase_settings = PhaseSettings()
        self.trigger_settings = TriggerSettings()
        self.validation_settings = ValidationSettings()
        self.integration_settings = IntegrationSettings()
        
        # Load configuration if exists
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update settings from loaded config
                self._update_from_dict(config_data)
                logger.info(f"Configuration loaded from: {self.config_path}")
            else:
                # Create default configuration file
                self.save_config()
                logger.info(f"Default configuration created at: {self.config_path}")
                
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}. Using defaults.")
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            config_data = self._to_dict()
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update settings from dictionary"""
        try:
            # Update main settings
            if "settings" in config_data:
                settings_data = config_data["settings"]
                for key, value in settings_data.items():
                    if hasattr(self.settings, key):
                        if key == "mode":
                            setattr(self.settings, key, PopulationMode(value))
                        elif key == "validation_level":
                            setattr(self.settings, key, ValidationLevel(value))
                        else:
                            setattr(self.settings, key, value)
            
            # Update phase settings
            if "phase_settings" in config_data:
                phase_data = config_data["phase_settings"]
                for key, value in phase_data.items():
                    if hasattr(self.phase_settings, key):
                        setattr(self.phase_settings, key, value)
            
            # Update trigger settings
            if "trigger_settings" in config_data:
                trigger_data = config_data["trigger_settings"]
                for key, value in trigger_data.items():
                    if hasattr(self.trigger_settings, key):
                        setattr(self.trigger_settings, key, value)
            
            # Update validation settings
            if "validation_settings" in config_data:
                validation_data = config_data["validation_settings"]
                for key, value in validation_data.items():
                    if hasattr(self.validation_settings, key):
                        setattr(self.validation_settings, key, value)
            
            # Update integration settings
            if "integration_settings" in config_data:
                integration_data = config_data["integration_settings"]
                for key, value in integration_data.items():
                    if hasattr(self.integration_settings, key):
                        setattr(self.integration_settings, key, value)
                        
        except Exception as e:
            logger.error(f"Failed to update configuration from dict: {e}")
            raise
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert current configuration to dictionary"""
        return {
            "settings": asdict(self.settings),
            "phase_settings": asdict(self.phase_settings),
            "trigger_settings": asdict(self.trigger_settings),
            "validation_settings": asdict(self.validation_settings),
            "integration_settings": asdict(self.integration_settings)
        }
    
    def get_setting(self, setting_path: str) -> Any:
        """Get a specific setting value using dot notation"""
        try:
            parts = setting_path.split('.')
            current = self
            
            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                else:
                    raise ValueError(f"Setting not found: {setting_path}")
            
            return current
            
        except Exception as e:
            logger.error(f"Failed to get setting {setting_path}: {e}")
            return None
    
    def set_setting(self, setting_path: str, value: Any) -> bool:
        """Set a specific setting value using dot notation"""
        try:
            parts = setting_path.split('.')
            current = self
            
            # Navigate to parent object
            for part in parts[:-1]:
                if hasattr(current, part):
                    current = getattr(current, part)
                else:
                    raise ValueError(f"Setting path not found: {setting_path}")
            
            # Set the value
            setattr(current, parts[-1], value)
            
            # Auto-save configuration
            self.save_config()
            
            logger.info(f"Setting updated: {setting_path} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set setting {setting_path}: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Validate main settings
            if self.settings.max_concurrent_populations <= 0:
                validation_results["errors"].append(
                    "max_concurrent_populations must be positive"
                )
                validation_results["valid"] = False
            
            if self.settings.population_timeout <= 0:
                validation_results["errors"].append(
                    "population_timeout must be positive"
                )
                validation_results["valid"] = False
            
            # Validate phase settings
            if self.phase_settings.phase1_timeout <= 0:
                validation_results["errors"].append(
                    "phase1_timeout must be positive"
                )
                validation_results["valid"] = False
            
            if self.phase_settings.phase2_timeout <= 0:
                validation_results["errors"].append(
                    "phase2_timeout must be positive"
                )
                validation_results["valid"] = False
            
            # Validate trigger settings
            if self.trigger_settings.file_upload_delay < 0:
                validation_results["warnings"].append(
                    "file_upload_delay should be non-negative"
                )
            
            if self.trigger_settings.etl_completion_delay < 0:
                validation_results["warnings"].append(
                    "etl_completion_delay should be non-negative"
                )
            
            # Validate integration settings
            if self.integration_settings.etl_polling_interval <= 0:
                validation_results["errors"].append(
                    "etl_polling_interval must be positive"
                )
                validation_results["valid"] = False
            
            # Add recommendations
            if self.settings.max_concurrent_populations > 10:
                validation_results["recommendations"].append(
                    "Consider reducing max_concurrent_populations for better stability"
                )
            
            if self.settings.population_timeout > 600:
                validation_results["recommendations"].append(
                    "Consider reducing population_timeout for better responsiveness"
                )
            
            if not self.trigger_settings.scheduled_enabled:
                validation_results["recommendations"].append(
                    "Consider enabling scheduled triggers for maintenance tasks"
                )
            
        except Exception as e:
            validation_results["errors"].append(f"Configuration validation failed: {e}")
            validation_results["valid"] = False
        
        return validation_results
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        try:
            # Reinitialize with defaults
            self.settings = PopulationSettings()
            self.phase_settings = PhaseSettings()
            self.trigger_settings = TriggerSettings()
            self.validation_settings = ValidationSettings()
            self.integration_settings = IntegrationSettings()
            
            # Save default configuration
            self.save_config()
            
            logger.info("Configuration reset to defaults")
            
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            raise
    
    def export_config(self, output_path: Path, format: str = "json") -> bool:
        """Export configuration to file"""
        try:
            config_data = self._to_dict()
            
            if format.lower() == "json":
                with open(output_path, 'w') as f:
                    json.dump(config_data, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Configuration exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """Import configuration from file"""
        try:
            if not import_path.exists():
                raise FileNotFoundError(f"Import file not found: {import_path}")
            
            with open(import_path, 'r') as f:
                config_data = json.load(f)
            
            # Update configuration
            self._update_from_dict(config_data)
            
            # Save imported configuration
            self.save_config()
            
            logger.info(f"Configuration imported from: {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            "mode": self.settings.mode.value,
            "validation_level": self.settings.validation_level.value,
            "phases_enabled": {
                "phase1": self.phase_settings.phase1_enabled,
                "phase2": self.phase_settings.phase2_enabled
            },
            "triggers_enabled": {
                "file_upload": self.trigger_settings.file_upload_enabled,
                "etl_completion": self.trigger_settings.etl_completion_enabled,
                "scheduled": self.trigger_settings.scheduled_enabled,
                "manual": self.trigger_settings.manual_enabled
            },
            "integrations_enabled": {
                "etl_pipeline": self.integration_settings.etl_pipeline_enabled,
                "file_upload": self.integration_settings.file_upload_enabled,
                "ai_rag": self.integration_settings.ai_rag_enabled
            },
            "performance_settings": {
                "max_concurrent": self.settings.max_concurrent_populations,
                "timeout": self.settings.population_timeout,
                "retry_attempts": self.settings.retry_attempts
            }
        }
