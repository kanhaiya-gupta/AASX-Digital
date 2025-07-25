"""
Enhanced Twin Management Module
Phase 2.2.2: Complete Twin Registry Management
Handles twin lifecycle, operations, configuration, and advanced monitoring
Uses centralized DatabaseProjectManager for all database operations.
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Import centralized database manager
try:
    import sys
    from pathlib import Path
    # Add the project root to the path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from src.shared.database_manager import DatabaseProjectManager
    DATABASE_AVAILABLE = True
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"Warning: Centralized database manager not available: {e}")

logger = logging.getLogger(__name__)

class TwinStatus(Enum):
    """Enumeration of possible digital twin operational statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TwinOperation(Enum):
    """Enumeration of supported digital twin operations."""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    UPDATE = "update"
    DELETE = "delete"
    CONFIGURE = "configure"

@dataclass
class TwinConfiguration:
    """Configuration settings for a digital twin."""
    twin_id: str
    twin_name: str
    description: str
    twin_type: str
    version: str
    owner: str
    tags: List[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class TwinEvent:
    """Event log entry for a digital twin."""
    twin_id: str
    event_type: str
    event_message: str
    severity: str
    timestamp: datetime
    user: str
    metadata: Dict[str, Any]

@dataclass
class TwinHealth:
    """Comprehensive health data for a digital twin."""
    twin_id: str
    overall_health: float
    performance_health: float
    connectivity_health: float
    data_health: float
    operational_health: float
    last_check: datetime
    issues: List[str]
    recommendations: List[str]

class TwinManager:
    """
    Enhanced twin management system for digital twins.
    Handles registration, configuration, health, events, and lifecycle operations.
    All listing/filtering of twins for display, analytics, and monitoring should use this class.
    Uses centralized DatabaseProjectManager for all database operations.
    """
    
    def __init__(self):
        """
        Initialize the TwinManager using centralized database manager.
        """
        # Setup paths for AASX operations
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.projects_dir = self.data_dir / "projects"
        self.output_dir = self.project_root / "output" / "projects"
        
        # Use centralized database manager
        if DATABASE_AVAILABLE:
            self.db_manager = DatabaseProjectManager(self.projects_dir, self.output_dir)
            logger.info("✅ Using centralized database manager for twin management")
        else:
            self.db_manager = None
            logger.error("❌ Centralized database manager not available")
        
        self.active_twins: Dict[str, Dict[str, Any]] = {}
        self.twin_operations: Dict[str, asyncio.Task] = {}
        self._load_active_twins()
    
    def _load_active_twins(self):
        """Load active twins from centralized database manager"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return
        
        try:
            # Get all registered twins from centralized database
            twins = self.db_manager.get_all_registered_twins()
            
            # Load active twins into memory
            for twin in twins:
                if twin.get('status') == 'active':
                    self.active_twins[twin['twin_id']] = {
                        "twin_id": twin['twin_id'],
                        "twin_name": twin['twin_name'],
                    "status": TwinStatus.ACTIVE.value,
                        "operational_status": "stopped",
                    "last_operation": None
                }
            
            logger.info(f"Loaded {len(self.active_twins)} active twins")
            
        except Exception as e:
            logger.error(f"Error loading active twins: {e}")
    
    # ==================== AASX-SPECIFIC STATIC METHODS ====================
    # These methods contain AASX-specific logic that cannot be handled by the centralized manager
    
    @staticmethod
    def calculate_data_points_from_aasx_output(aasx_filename: str, project_id: str, output_dir: Path) -> int:
        """
        Calculate data points from AASX output files.
        This is AASX-specific logic that cannot be handled by the centralized manager.
        """
        try:
            # Check for AASX-specific output files
            file_stem = Path(aasx_filename).stem
            project_output_dir = output_dir / project_id / file_stem
            
            if not project_output_dir.exists():
                return 0
            
            # Count AASX-specific data files
            data_files = 0
            for file_path in project_output_dir.rglob("*.json"):
                if file_path.name in ["aas_data.json", "submodels.json", "assets.json"]:
                    data_files += 1
            
            return data_files
            
        except Exception as e:
            logger.error(f"Error calculating data points for {aasx_filename}: {e}")
            return 0

    @staticmethod
    def validate_aasx_output_structure(aasx_filename: str, project_id: str, output_dir: Path) -> Dict[str, Any]:
        """
        Validate AASX output structure.
        This is AASX-specific validation that cannot be handled by the centralized manager.
        """
        try:
            file_stem = Path(aasx_filename).stem
            project_output_dir = output_dir / project_id / file_stem
            
            validation_result = {
                'valid': False,
                'missing_files': [],
                'required_files': ['aas_data.json', 'submodels.json'],
                'found_files': []
            }
            
            if not project_output_dir.exists():
                validation_result['missing_files'] = validation_result['required_files']
                return validation_result
            
            # Check for required AASX files
            for required_file in validation_result['required_files']:
                file_path = project_output_dir / required_file
                if file_path.exists():
                    validation_result['found_files'].append(required_file)
                else:
                    validation_result['missing_files'].append(required_file)
            
            validation_result['valid'] = len(validation_result['missing_files']) == 0
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating AASX output for {aasx_filename}: {e}")
            return {'valid': False, 'error': str(e)}

    @staticmethod
    def extract_aasx_metadata(aasx_filename: str, project_id: str, output_dir: Path) -> Dict[str, Any]:
        """
        Extract AASX-specific metadata from output files.
        This is AASX-specific logic that cannot be handled by the centralized manager.
        """
        try:
            file_stem = Path(aasx_filename).stem
            project_output_dir = output_dir / project_id / file_stem
            aas_data_file = project_output_dir / "aas_data.json"
            
            if not aas_data_file.exists():
                return {}
            
            with open(aas_data_file, 'r', encoding='utf-8') as f:
                aas_data = json.load(f)
            
            # Extract AASX-specific metadata
            metadata = {
                'aas_id': aas_data.get('id', ''),
                'aas_type': aas_data.get('type', ''),
                'submodel_count': len(aas_data.get('submodels', [])),
                'asset_count': len(aas_data.get('assets', [])),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting AASX metadata for {aasx_filename}: {e}")
            return {}

    # ==================== INSTANCE METHODS ====================

    async def create_twin(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create twin using centralized database manager"""
        if not self.db_manager:
            return {"success": False, "error": "Database manager not available"}
        
        # Extract project_id and file_id from twin_data
        project_id = twin_data.get('project_id')
        file_id = twin_data.get('file_id')
        
        if not project_id or not file_id:
            return {'success': False, 'error': 'project_id and file_id required'}
        
        # Use centralized database manager to register twin
        result = self.db_manager.register_digital_twin(project_id, file_id, twin_data)
        
        if result.get('success'):
            # Add to active twins if registration successful
            twin_id = result.get('twin_id')
            if twin_id:
                self.active_twins[twin_id] = {
                    "twin_id": twin_id,
                    "twin_name": result.get('twin_name', ''),
                    "status": TwinStatus.ACTIVE.value,
                    "operational_status": "stopped",
                    "last_operation": None
                }
        
        return result

    async def update_twin(self, twin_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update twin using centralized database manager"""
        if not self.db_manager:
            return {"success": False, "error": "Database manager not available"}
        
        # Update configuration using centralized database manager
        result = self.db_manager.update_twin_configuration(twin_id, update_data)
        
        if result.get('success'):
            # Update active twins if update successful
            if twin_id in self.active_twins:
                self.active_twins[twin_id].update({
                    "twin_name": update_data.get('twin_name', self.active_twins[twin_id]['twin_name'])
                })
        
        return result
    
    async def delete_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Delete twin using centralized database manager"""
        if not self.db_manager:
            return {"success": False, "error": "Database manager not available"}
        
        try:
            # Log deletion event
            self.db_manager.log_twin_event(twin_id, 'twin_deleted', f'Twin {twin_id} deleted by {user}', 'warning', user)
            
            # Remove from active twins
            if twin_id in self.active_twins:
                del self.active_twins[twin_id]
            
            # Note: Actual twin deletion would require additional database operations
            # For now, we'll just mark it as inactive
            return {"success": True, "message": f"Twin {twin_id} marked for deletion"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Start twin operation using centralized database manager"""
        return await self._perform_twin_operation(twin_id, TwinOperation.START, user)
    
    async def stop_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Stop twin operation using centralized database manager"""
        return await self._perform_twin_operation(twin_id, TwinOperation.STOP, user)
    
    async def restart_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """Restart twin operation using centralized database manager"""
        return await self._perform_twin_operation(twin_id, TwinOperation.RESTART, user)
    
    async def _perform_twin_operation(self, twin_id: str, operation: TwinOperation, user: str) -> Dict[str, Any]:
        """Perform a twin operation using centralized database manager"""
        if not self.db_manager:
            return {"success": False, "error": "Database manager not available"}
        
        try:
            # Check if twin exists in active twins or database
            if twin_id not in self.active_twins:
                # Check database using centralized manager
                twin_info = self.db_manager.get_twin_by_aasx(twin_id)  # This might need adjustment
                if not twin_info:
                    return {"success": False, "error": "Twin not found or not active"}
                
                # Add to active twins
                self.active_twins[twin_id] = {
                    "twin_id": twin_id,
                    "twin_name": twin_info.get('twin_name', twin_id),
                    "status": TwinStatus.ACTIVE.value,
                    "operational_status": "stopped",
                    "last_operation": None
                }
            
            # Log operation event using centralized database manager
            event_message = f"Twin {operation.value} operation initiated by {user}"
            self.db_manager.log_twin_event(twin_id, f"twin_{operation.value}", event_message, "info", user)
            
            # Simulate operation (in real implementation, this would be actual twin operations)
            await asyncio.sleep(1)  # Simulate operation time
            
            # Update active twin status
            self.active_twins[twin_id]["operational_status"] = operation.value
            self.active_twins[twin_id]["last_operation"] = datetime.now().isoformat()
            
            # Log operation completion
            completion_message = f"Twin {operation.value} operation completed successfully"
            self.db_manager.log_twin_event(twin_id, f"twin_{operation.value}_completed", completion_message, "info", user)
            
            return {
                "success": True,
                "twin_id": twin_id,
                "operation": operation.value,
                "message": f"Twin {operation.value} operation completed"
            }
            
        except Exception as e:
            # Log error event
            if self.db_manager:
                self.db_manager.log_twin_event(twin_id, f"twin_{operation.value}_error", str(e), "error", user)
            return {"success": False, "error": str(e)}
    
    async def get_twin_configuration(self, twin_id: str) -> Optional[TwinConfiguration]:
        """Get twin configuration using centralized database manager"""
        if not self.db_manager:
            return None
        
        try:
            config_data = self.db_manager.get_twin_configuration(twin_id)
            if config_data:
                return TwinConfiguration(
                    twin_id=config_data['twin_id'],
                    twin_name=config_data['twin_name'],
                    description=config_data.get('description', ''),
                    twin_type=config_data['twin_type'],
                    version=config_data.get('version', '1.0.0'),
                    owner=config_data.get('owner', 'system'),
                    tags=config_data.get('tags', []),
                    settings=config_data.get('settings', {}),
                    created_at=datetime.fromisoformat(config_data['created_at']),
                    updated_at=datetime.fromisoformat(config_data['updated_at'])
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting twin configuration: {e}")
            return None
    
    async def get_twin_events(self, twin_id: str, limit: int = 50) -> List[TwinEvent]:
        """Get twin events using centralized database manager"""
        if not self.db_manager:
            return []
        
        try:
            events_data = self.db_manager.get_twin_events(twin_id, limit)
            events = []
            
            for event_data in events_data:
                events.append(TwinEvent(
                    twin_id=event_data['twin_id'],
                    event_type=event_data['event_type'],
                    event_message=event_data['event_message'],
                    severity=event_data['severity'],
                    timestamp=datetime.fromisoformat(event_data['timestamp']),
                    user=event_data['user'],
                    metadata=event_data.get('metadata', {})
                ))
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting twin events: {e}")
            return []
    
    async def get_twin_health(self, twin_id: str) -> Optional[TwinHealth]:
        """Get twin health using centralized database manager"""
        if not self.db_manager:
            return None
        
        try:
            health_data = self.db_manager.get_twin_health(twin_id)
            if health_data:
                return TwinHealth(
                    twin_id=health_data['twin_id'],
                    overall_health=health_data['overall_health'],
                    performance_health=health_data['performance_health'],
                    connectivity_health=health_data['connectivity_health'],
                    data_health=health_data['data_health'],
                    operational_health=health_data['operational_health'],
                    last_check=datetime.fromisoformat(health_data['last_check']),
                    issues=health_data.get('issues', []),
                    recommendations=health_data.get('recommendations', [])
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting twin health: {e}")
            return None
    
    async def get_all_twins_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all twins using centralized database manager"""
        if not self.db_manager:
            return []
        
        try:
            twins = self.db_manager.get_all_registered_twins()
            summary = []
            
            for twin in twins:
                # Get health information
                health = await self.get_twin_health(twin['twin_id'])
                
                summary.append({
                    'twin_id': twin['twin_id'],
                    'twin_name': twin['twin_name'],
                    'twin_type': twin['twin_type'],
                    'status': twin['status'],
                    'project_id': twin['project_id'],
                    'aasx_filename': twin['aasx_filename'],
                    'created_at': twin['created_at'],
                    'last_sync': twin.get('last_sync'),
                    'data_points': twin.get('data_points', 0),
                    'health': {
                        'overall_health': health.overall_health if health else 0,
                        'operational_health': health.operational_health if health else 0
                    } if health else {'overall_health': 0, 'operational_health': 0},
                    'is_active': twin['twin_id'] in self.active_twins
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting twins summary: {e}")
            return []

    def get_all_registered_twins(self) -> List[Dict[str, Any]]:
        """Get all registered twins using centralized database manager"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return []
        
        return self.db_manager.get_all_registered_twins()

    def get_twin_statistics(self) -> Dict[str, Any]:
        """Get twin statistics using centralized database manager"""
        if not self.db_manager:
            return {
                'total_twins': 0,
                'active_twins': 0,
                'orphaned_twins': 0,
                'error': 'Database manager not available'
            }
        
        return self.db_manager.get_twin_statistics()

    def reset_orphaned_twins(self) -> Dict[str, Any]:
        """Reset orphaned twins using centralized database manager"""
        if not self.db_manager:
            return {'success': False, 'error': 'Database manager not available'}
        
        return self.db_manager.reset_orphaned_twins()

    # ==================== ADDITIONAL DELEGATED METHODS ====================
    # These methods delegate to the centralized database manager for AASX operations
    
    def get_twin_by_aasx(self, aasx_filename: str) -> Optional[Dict[str, Any]]:
        """Get twin information by AASX filename - delegated to centralized manager"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return None
        return self.db_manager.get_twin_by_aasx(aasx_filename)

    def get_sync_status(self, twin_id: str) -> Dict[str, Any]:
        """Get sync status for a twin - delegated to centralized manager"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return {'error': 'Database manager not available'}
        return self.db_manager.get_sync_status(twin_id)

    def discover_processed_aasx_files(self) -> List[Dict[str, Any]]:
        """Discover AASX files that have been processed - delegated to centralized manager"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return []
        return self.db_manager.discover_processed_aasx_files()

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects - delegated to centralized manager"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return []
        return self.db_manager.list_projects()

    def get_orphaned_twins(self) -> List[Dict[str, Any]]:
        """Get orphaned twins - delegated to centralized manager with AASX-specific filtering"""
        if not self.db_manager:
            logger.error("Database manager not available")
            return []
        
        try:
            # Get all twins and filter for orphaned ones
            all_twins = self.db_manager.get_all_registered_twins()
            orphaned_twins = []
            
            for twin in all_twins:
                if twin.get('status') == 'orphaned':
                    # Add project name for display
                    project_metadata = self.db_manager.get_project_metadata(twin.get('project_id', ''))
                    twin['project_name'] = project_metadata.get('name', twin.get('project_id', ''))
                    orphaned_twins.append(twin)
            
            return orphaned_twins
            
        except Exception as e:
            logger.error(f"Error getting orphaned twins: {e}")
            return []



# Create a singleton instance for import
twin_manager = TwinManager() 