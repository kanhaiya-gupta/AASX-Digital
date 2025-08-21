"""
Module Data Sync Service

This service handles data synchronization between the AAS Data Modeling Engine
and external task modules, ensuring data consistency, integrity, and
governance across the entire ecosystem.

The data sync service manages data flow, transformation, validation,
and conflict resolution between modules and the engine.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from collections import defaultdict

from .models import ModuleInfo, ModuleStatus


logger = logging.getLogger(__name__)


class DataSyncOperation:
    """Represents a data synchronization operation."""
    
    def __init__(self, operation_id: UUID, operation_type: str, source_module: str, target_module: str):
        self.operation_id = operation_id
        self.operation_type = operation_type  # push, pull, sync, transform
        self.source_module = source_module
        self.target_module = target_module
        self.status = "pending"  # pending, running, completed, failed
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.data_size = 0
        self.error_message = None
        self.metadata = {}


class ModuleDataSyncService:
    """
    Service for synchronizing data between the engine and external modules.
    
    This service handles data flow, transformation, validation, and
    conflict resolution to ensure data consistency across the ecosystem.
    """
    
    def __init__(self, sync_interval: int = 300, max_concurrent_syncs: int = 10):
        """
        Initialize the module data sync service.
        
        Args:
            sync_interval: Interval in seconds between sync cycles
            max_concurrent_syncs: Maximum number of concurrent sync operations
        """
        self.sync_interval = sync_interval
        self.max_concurrent_syncs = max_concurrent_syncs
        self.is_syncing = False
        self.last_sync_cycle = None
        
        # Sync tracking
        self.active_syncs: Dict[UUID, DataSyncOperation] = {}
        self.sync_history: List[DataSyncOperation] = []
        self.sync_queue: List[DataSyncOperation] = []
        
        # Data mapping and transformation
        self.data_mappings: Dict[str, Dict] = {}
        self.transformation_rules: Dict[str, Dict] = {}
        self.validation_rules: Dict[str, Dict] = {}
        
        # Conflict resolution
        self.conflict_resolution_strategies: Dict[str, str] = {
            "last_write_wins": "Use the most recent data",
            "source_wins": "Always use source module data",
            "target_wins": "Always use target module data",
            "manual_resolution": "Require manual intervention"
        }
        
        # Performance tracking
        self.sync_metrics: Dict[str, List[Dict]] = defaultdict(list)
        self.data_flow_graph: Dict[str, List[str]] = defaultdict(list)
    
    async def start_data_sync(self) -> None:
        """Start the continuous data synchronization process."""
        if self.is_syncing:
            logger.warning("Data sync service is already running")
            return
        
        self.is_syncing = True
        logger.info("Starting module data sync service")
        
        # Run sync as a background task
        self._sync_task = asyncio.create_task(self._sync_loop())
    
    async def _sync_loop(self) -> None:
        """Background task for continuous data sync."""
        try:
            while self.is_syncing:
                await self.perform_sync_cycle()
                await asyncio.sleep(self.sync_interval)
        except Exception as e:
            logger.error(f"Error in data sync service: {e}")
            self.is_syncing = False
            raise
    
    async def stop_data_sync(self) -> None:
        """Stop the continuous data synchronization process."""
        self.is_syncing = False
        
        # Cancel the background task if it exists
        if hasattr(self, '_sync_task') and self._sync_task:
            try:
                self._sync_task.cancel()
                await self._sync_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling
            except Exception as e:
                logger.warning(f"Error cancelling sync task: {e}")
        
        logger.info("Stopped module data sync service")
    
    async def perform_sync_cycle(self) -> None:
        """Perform a complete data synchronization cycle."""
        logger.debug("Starting data sync cycle")
        start_time = datetime.utcnow()
        
        try:
            # Process sync queue
            await self._process_sync_queue()
            
            # Perform scheduled syncs
            await self._perform_scheduled_syncs()
            
            # Update sync cycle timestamp
            self.last_sync_cycle = start_time
            
            logger.debug("Data sync cycle completed")
            
        except Exception as e:
            logger.error(f"Error during data sync cycle: {e}")
    
    async def _process_sync_queue(self) -> None:
        """Process the sync queue."""
        if not self.sync_queue:
            return
        
        # Process up to max_concurrent_syncs operations
        available_slots = self.max_concurrent_syncs - len(self.active_syncs)
        if available_slots <= 0:
            logger.debug("No available sync slots, waiting for completion")
            return
        
        # Get operations to process
        operations_to_process = self.sync_queue[:available_slots]
        self.sync_queue = self.sync_queue[available_slots:]
        
        # Start sync operations
        for operation in operations_to_process:
            await self._start_sync_operation(operation)
    
    async def _perform_scheduled_syncs(self) -> None:
        """Perform scheduled synchronization operations."""
        # This would check for modules that need regular syncing
        # For now, this is a placeholder
        pass
    
    async def _start_sync_operation(self, operation: DataSyncOperation) -> None:
        """Start a sync operation."""
        try:
            operation.status = "running"
            operation.started_at = datetime.utcnow()
            self.active_syncs[operation.operation_id] = operation
            
            # Execute the sync operation
            await self._execute_sync_operation(operation)
            
        except Exception as e:
            logger.error(f"Error starting sync operation {operation.operation_id}: {e}")
            operation.status = "failed"
            operation.error_message = str(e)
            operation.completed_at = datetime.utcnow()
    
    async def _execute_sync_operation(self, operation: DataSyncOperation) -> None:
        """Execute a sync operation."""
        try:
            logger.debug(f"Executing sync operation: {operation.operation_type} from {operation.source_module} to {operation.target_module}")
            
            # Perform the sync based on operation type
            if operation.operation_type == "push":
                result = await self._push_data(operation.source_module, operation.target_module)
            elif operation.operation_type == "pull":
                result = await self._pull_data(operation.source_module, operation.target_module)
            elif operation.operation_type == "sync":
                result = await self._sync_data(operation.source_module, operation.target_module)
            elif operation.operation_type == "transform":
                result = await self._transform_data(operation.source_module, operation.target_module)
            else:
                raise ValueError(f"Unknown sync operation type: {operation.operation_type}")
            
            # Update operation status
            operation.status = "completed"
            operation.completed_at = datetime.utcnow()
            operation.data_size = result.get("data_size", 0)
            operation.metadata = result.get("metadata", {})
            
            # Record metrics
            self._record_sync_metrics(operation)
            
            logger.info(f"Sync operation completed: {operation.operation_id}")
            
        except Exception as e:
            logger.error(f"Error executing sync operation {operation.operation_id}: {e}")
            operation.status = "failed"
            operation.error_message = str(e)
            operation.completed_at = datetime.utcnow()
        
        finally:
            # Remove from active syncs and add to history
            if operation.operation_id in self.active_syncs:
                del self.active_syncs[operation.operation_id]
            
            self.sync_history.append(operation)
            
            # Keep only recent history
            if len(self.sync_history) > 1000:
                self.sync_history = self.sync_history[-1000:]
    
    async def _push_data(self, source_module: str, target_module: str) -> Dict[str, Any]:
        """Push data from source module to target module."""
        try:
            logger.debug(f"Pushing data from {source_module} to {target_module}")
            
            # Get data from source module
            source_data = await self._get_module_data(source_module)
            if not source_data:
                return {"data_size": 0, "metadata": {"error": "No data available from source"}}
            
            # Transform data if needed
            transformed_data = await self._transform_data_for_target(source_data, source_module, target_module)
            
            # Validate data before sending
            validation_result = await self._validate_data(transformed_data, target_module)
            if not validation_result["is_valid"]:
                return {
                    "data_size": 0,
                    "metadata": {"error": "Data validation failed", "validation_errors": validation_result["errors"]}
                }
            
            # Send data to target module
            send_result = await self._send_data_to_module(transformed_data, target_module)
            
            # Update data flow graph
            self.data_flow_graph[source_module].append(target_module)
            
            return {
                "data_size": len(json.dumps(transformed_data)),
                "metadata": {
                    "source_module": source_module,
                    "target_module": target_module,
                    "data_type": type(transformed_data).__name__,
                    "validation_passed": True,
                    "send_success": send_result["success"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error pushing data from {source_module} to {target_module}: {e}")
            return {"data_size": 0, "metadata": {"error": str(e)}}
    
    async def _pull_data(self, source_module: str, target_module: str) -> Dict[str, Any]:
        """Pull data from source module to target module."""
        # Similar to push but initiated by target module
        return await self._push_data(source_module, target_module)
    
    async def _sync_data(self, source_module: str, target_module: str) -> Dict[str, Any]:
        """Synchronize data between two modules bidirectionally."""
        try:
            logger.debug(f"Synchronizing data between {source_module} and {target_module}")
            
            # Get data from both modules
            source_data = await self._get_module_data(source_module)
            target_data = await self._get_module_data(target_module)
            
            # Compare data and resolve conflicts
            sync_result = await self._resolve_data_conflicts(source_data, target_data, source_module, target_module)
            
            # Apply resolved data to both modules
            if sync_result["has_changes"]:
                await self._apply_sync_changes(sync_result["resolved_data"], source_module, target_module)
            
            return {
                "data_size": sync_result.get("data_size", 0),
                "metadata": {
                    "source_module": source_module,
                    "target_module": target_module,
                    "conflicts_resolved": sync_result["conflicts_resolved"],
                    "changes_applied": sync_result["has_changes"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error synchronizing data between {source_module} and {target_module}: {e}")
            return {"data_size": 0, "metadata": {"error": str(e)}}
    
    async def _transform_data(self, source_module: str, target_module: str) -> Dict[str, Any]:
        """Transform data from source format to target format."""
        try:
            logger.debug(f"Transforming data from {source_module} to {target_module}")
            
            # Get source data
            source_data = await self._get_module_data(source_module)
            if not source_data:
                return {"data_size": 0, "metadata": {"error": "No data available from source"}}
            
            # Apply transformation rules
            transformed_data = await self._apply_transformation_rules(source_data, source_module, target_module)
            
            return {
                "data_size": len(json.dumps(transformed_data)),
                "metadata": {
                    "source_module": source_module,
                    "target_module": target_module,
                    "transformation_applied": True,
                    "original_format": type(source_data).__name__,
                    "transformed_format": type(transformed_data).__name__
                }
            }
            
        except Exception as e:
            logger.error(f"Error transforming data from {source_module} to {target_module}: {e}")
            return {"data_size": 0, "metadata": {"error": str(e)}}
    
    async def _get_module_data(self, module_name: str) -> Optional[Any]:
        """Get data from a specific module."""
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Connect to the module
        # 2. Request data based on sync configuration
        # 3. Handle authentication and authorization
        # 4. Return the data
        
        logger.debug(f"Getting data from module: {module_name}")
        
        # Return mock data for demonstration
        return {
            "module": module_name,
            "data": f"Sample data from {module_name}",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    async def _transform_data_for_target(self, data: Any, source_module: str, target_module: str) -> Any:
        """Transform data for a specific target module."""
        # This is a placeholder implementation
        # In a real system, this would apply transformation rules
        
        # For now, return data as-is
        return data
    
    async def _validate_data(self, data: Any, target_module: str) -> Dict[str, Any]:
        """Validate data before sending to target module."""
        # This is a placeholder implementation
        # In a real system, this would apply validation rules
        
        return {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
    
    async def _send_data_to_module(self, data: Any, target_module: str) -> Dict[str, Any]:
        """Send data to a target module."""
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Connect to the target module
        # 2. Send the data
        # 3. Handle the response
        
        logger.debug(f"Sending data to module: {target_module}")
        
        # Simulate successful send
        return {
            "success": True,
            "message": f"Data sent to {target_module}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _resolve_data_conflicts(self, source_data: Any, target_data: Any, source_module: str, target_module: str) -> Dict[str, Any]:
        """Resolve conflicts between source and target data."""
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Compare data structures
        # 2. Identify conflicts
        # 3. Apply conflict resolution strategy
        # 4. Return resolved data
        
        logger.debug(f"Resolving conflicts between {source_module} and {target_module}")
        
        # For now, assume no conflicts
        return {
            "has_changes": False,
            "conflicts_resolved": 0,
            "resolved_data": source_data,
            "data_size": len(json.dumps(source_data))
        }
    
    async def _apply_sync_changes(self, resolved_data: Any, source_module: str, target_module: str) -> None:
        """Apply resolved sync changes to both modules."""
        # This is a placeholder implementation
        logger.debug(f"Applying sync changes to {source_module} and {target_module}")
    
    async def _apply_transformation_rules(self, data: Any, source_module: str, target_module: str) -> Any:
        """Apply transformation rules to data."""
        # This is a placeholder implementation
        # In a real system, this would apply configured transformation rules
        
        return data
    
    def _record_sync_metrics(self, operation: DataSyncOperation) -> None:
        """Record metrics for a sync operation."""
        metrics = {
            "timestamp": operation.completed_at,
            "operation_type": operation.operation_type,
            "source_module": operation.source_module,
            "target_module": operation.target_module,
            "status": operation.status,
            "data_size": operation.data_size,
            "duration_ms": (operation.completed_at - operation.started_at).total_seconds() * 1000 if operation.started_at else 0
        }
        
        self.sync_metrics[f"{operation.source_module}_{operation.target_module}"].append(metrics)
        
        # Keep only recent metrics
        if len(self.sync_metrics[f"{operation.source_module}_{operation.target_module}"]) > 1000:
            self.sync_metrics[f"{operation.source_module}_{operation.target_module}"] = \
                self.sync_metrics[f"{operation.source_module}_{operation.target_module}"][-1000:]
    
    async def queue_sync_operation(
        self,
        operation_type: str,
        source_module: str,
        target_module: str,
        priority: int = 0
    ) -> UUID:
        """Queue a sync operation for execution."""
        operation = DataSyncOperation(
            operation_id=uuid4(),
            operation_type=operation_type,
            source_module=source_module,
            target_module=target_module
        )
        
        # Add priority to metadata
        operation.metadata["priority"] = priority
        
        # Add to queue (simple FIFO for now, could be enhanced with priority queue)
        self.sync_queue.append(operation)
        
        logger.info(f"Queued sync operation: {operation.operation_id} ({operation_type} from {source_module} to {target_module})")
        
        return operation.operation_id
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync service status."""
        return {
            "is_syncing": self.is_syncing,
            "last_sync_cycle": self.last_sync_cycle,
            "sync_interval": self.sync_interval,
            "active_syncs": len(self.active_syncs),
            "queued_syncs": len(self.sync_queue),
            "total_syncs": len(self.sync_history),
            "max_concurrent_syncs": self.max_concurrent_syncs
        }
    
    def get_sync_history(self, limit: int = 100) -> List[DataSyncOperation]:
        """Get sync history with optional limit."""
        return self.sync_history[-limit:] if self.sync_history else []
    
    def get_sync_metrics(self, source_module: str = None, target_module: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get sync metrics for specific modules or overall."""
        if source_module and target_module:
            key = f"{source_module}_{target_module}"
            metrics = self.sync_metrics.get(key, [])
            return {key: metrics[-limit:] if metrics else []}
        else:
            return {key: metrics[-limit:] if metrics else [] for key, metrics in self.sync_metrics.items()}
    
    def get_data_flow_graph(self) -> Dict[str, List[str]]:
        """Get the data flow graph showing module connections."""
        return dict(self.data_flow_graph)
