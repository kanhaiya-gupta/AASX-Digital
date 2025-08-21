"""
Twin Sync Model

Defines the data model for twin synchronization operations.
Handles sync history, configurations, and status tracking.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class TwinSyncConfiguration:
    """Configuration for twin synchronization operations."""
    
    sync_type: str  # 'full', 'incremental', 'metadata'
    sync_interval: int = 3600  # seconds
    retry_attempts: int = 3
    timeout: int = 30  # seconds
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TwinSyncHistory:
    """History record for twin synchronization operations."""
    
    id: str
    twin_id: str
    sync_type: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    sync_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TwinSyncStatus:
    """Current sync status for a twin."""
    
    twin_id: str
    last_sync_timestamp: Optional[str] = None
    last_sync_status: str = "unknown"  # 'unknown', 'success', 'failed', 'pending'
    last_sync_type: Optional[str] = None
    next_sync_timestamp: Optional[str] = None
    sync_configuration: TwinSyncConfiguration = field(default_factory=lambda: TwinSyncConfiguration("full"))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TwinSyncOperation:
    """Represents a sync operation."""
    
    id: str
    twin_id: str
    operation_type: str  # 'sync', 'validate', 'cleanup'
    status: str  # 'pending', 'running', 'completed', 'failed'
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict) 