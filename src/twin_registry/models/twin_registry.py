"""
Twin Registry Model

Manages registry metadata and configuration for twin registry services.
"""

from src.shared.models.base_model import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class TwinRegistryMetadata(BaseModel):
    """Model for twin registry metadata and configuration"""
    
    registry_id: str
    twin_id: str
    registry_name: str
    registry_type: str  # aasx, custom, external, etc.
    registry_config: Optional[Dict[str, Any]] = None
    registry_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    version: str = "1.0.0"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def create_metadata(
        cls,
        twin_id: str,
        registry_name: str,
        registry_type: str = "aasx",
        registry_config: Optional[Dict[str, Any]] = None,
        registry_metadata: Optional[Dict[str, Any]] = None
    ) -> "TwinRegistryMetadata":
        """Create new registry metadata"""
        now = datetime.utcnow()
        return cls(
            registry_id=str(uuid.uuid4()),
            twin_id=twin_id,
            registry_name=registry_name,
            registry_type=registry_type,
            registry_config=registry_config or {},
            registry_metadata=registry_metadata or {},
            created_at=now,
            updated_at=now,
            is_active=True
        )
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update registry configuration"""
        if self.registry_config is None:
            self.registry_config = {}
        self.registry_config.update(new_config)
        self.updated_at = datetime.utcnow()
    
    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """Update registry metadata"""
        if self.registry_metadata is None:
            self.registry_metadata = {}
        self.registry_metadata.update(new_metadata)
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the registry entry"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the registry entry"""
        self.is_active = True
        self.updated_at = datetime.utcnow()


class TwinRegistryQuery(BaseModel):
    """Query model for filtering registry metadata"""
    
    twin_id: Optional[str] = None
    registry_type: Optional[str] = None
    registry_name: Optional[str] = None
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwinRegistrySummary(BaseModel):
    """Summary model for registry statistics"""
    
    total_registries: int
    active_registries: int
    registries_by_type: Dict[str, int]
    registries_by_name: Dict[str, int]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwinRegistryConfig(BaseModel):
    """Model for registry configuration"""
    
    auto_sync_enabled: bool = False
    sync_interval_minutes: int = 30
    health_check_enabled: bool = True
    health_check_interval_minutes: int = 5
    max_instances_per_twin: int = 10
    retention_days: int = 90
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 