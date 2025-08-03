"""
Twin Operations Service
======================

Service for twin lifecycle operations (start, stop, restart, configure).
Handles twin operational state management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import shared services
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository

logger = logging.getLogger(__name__)

class TwinOperationsService:
    """
    Service for managing twin lifecycle operations.
    Handles start, stop, restart, and configuration operations.
    """
    
    def __init__(self, twin_service: DigitalTwinService):
        """Initialize the twin operations service."""
        self.twin_service = twin_service
        self.twin_repo = twin_service.get_repository()
        
        logger.info("Twin Operations Service initialized")
    
    async def start_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """
        Start a twin operation.
        
        Args:
            twin_id: The twin ID to start
            user: User performing the operation
            
        Returns:
            Operation result
        """
        try:
            logger.info(f"Starting twin: {twin_id} by user: {user}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Check if twin can be started
            current_status = getattr(twin, 'status', 'unknown')
            if current_status == 'active':
                logger.warning(f"Twin {twin_id} is already active")
                return {
                    "success": True,
                    "message": "Twin is already active",
                    "twin_id": twin_id,
                    "status": "active"
                }
            
            # Update twin status to active
            twin.status = "active"
            twin.updated_at = datetime.now().isoformat()
            
            # Save changes
            updated_twin = self.twin_repo.update(twin)
            if not updated_twin:
                raise Exception(f"Failed to update twin status: {twin_id}")
            
            # Log operation
            self._log_operation(twin_id, "start", user, "success")
            
            result = {
                "success": True,
                "message": f"Twin {twin_id} started successfully",
                "twin_id": twin_id,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully started twin: {twin_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start twin {twin_id}: {str(e)}")
            self._log_operation(twin_id, "start", user, "failed", str(e))
            raise Exception(f"Failed to start twin {twin_id}: {str(e)}")
    
    async def stop_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """
        Stop a twin operation.
        
        Args:
            twin_id: The twin ID to stop
            user: User performing the operation
            
        Returns:
            Operation result
        """
        try:
            logger.info(f"Stopping twin: {twin_id} by user: {user}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Check if twin can be stopped
            current_status = getattr(twin, 'status', 'unknown')
            if current_status == 'inactive':
                logger.warning(f"Twin {twin_id} is already inactive")
                return {
                    "success": True,
                    "message": "Twin is already inactive",
                    "twin_id": twin_id,
                    "status": "inactive"
                }
            
            # Update twin status to inactive
            twin.status = "inactive"
            twin.updated_at = datetime.now().isoformat()
            
            # Save changes
            updated_twin = self.twin_repo.update(twin)
            if not updated_twin:
                raise Exception(f"Failed to update twin status: {twin_id}")
            
            # Log operation
            self._log_operation(twin_id, "stop", user, "success")
            
            result = {
                "success": True,
                "message": f"Twin {twin_id} stopped successfully",
                "twin_id": twin_id,
                "status": "inactive",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully stopped twin: {twin_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to stop twin {twin_id}: {str(e)}")
            self._log_operation(twin_id, "stop", user, "failed", str(e))
            raise Exception(f"Failed to stop twin {twin_id}: {str(e)}")
    
    async def restart_twin(self, twin_id: str, user: str = "system") -> Dict[str, Any]:
        """
        Restart a twin operation.
        
        Args:
            twin_id: The twin ID to restart
            user: User performing the operation
            
        Returns:
            Operation result
        """
        try:
            logger.info(f"Restarting twin: {twin_id} by user: {user}")
            
            # Stop the twin first
            stop_result = await self.stop_twin(twin_id, user)
            if not stop_result.get("success"):
                raise Exception(f"Failed to stop twin during restart: {twin_id}")
            
            # Wait a moment for cleanup
            import asyncio
            await asyncio.sleep(1)
            
            # Start the twin
            start_result = await self.start_twin(twin_id, user)
            if not start_result.get("success"):
                raise Exception(f"Failed to start twin during restart: {twin_id}")
            
            # Log operation
            self._log_operation(twin_id, "restart", user, "success")
            
            result = {
                "success": True,
                "message": f"Twin {twin_id} restarted successfully",
                "twin_id": twin_id,
                "status": "active",
                "timestamp": datetime.now().isoformat(),
                "stop_result": stop_result,
                "start_result": start_result
            }
            
            logger.info(f"Successfully restarted twin: {twin_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to restart twin {twin_id}: {str(e)}")
            self._log_operation(twin_id, "restart", user, "failed", str(e))
            raise Exception(f"Failed to restart twin {twin_id}: {str(e)}")
    
    async def configure_twin(self, twin_id: str, config_data: Dict[str, Any], 
                           user: str = "system") -> Dict[str, Any]:
        """
        Configure twin settings.
        
        Args:
            twin_id: The twin ID to configure
            config_data: Configuration data to apply
            user: User performing the operation
            
        Returns:
            Operation result
        """
        try:
            logger.info(f"Configuring twin: {twin_id} by user: {user}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Apply configuration
            updated_fields = []
            for key, value in config_data.items():
                if hasattr(twin, key):
                    old_value = getattr(twin, key)
                    setattr(twin, key, value)
                    updated_fields.append({
                        "field": key,
                        "old_value": old_value,
                        "new_value": value
                    })
            
            # Update timestamp
            twin.updated_at = datetime.now().isoformat()
            
            # Save changes
            updated_twin = self.twin_repo.update(twin)
            if not updated_twin:
                raise Exception(f"Failed to update twin configuration: {twin_id}")
            
            # Log operation
            self._log_operation(twin_id, "configure", user, "success")
            
            result = {
                "success": True,
                "message": f"Twin {twin_id} configured successfully",
                "twin_id": twin_id,
                "updated_fields": updated_fields,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully configured twin: {twin_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to configure twin {twin_id}: {str(e)}")
            self._log_operation(twin_id, "configure", user, "failed", str(e))
            raise Exception(f"Failed to configure twin {twin_id}: {str(e)}")
    
    async def bulk_operations(self, twin_ids: List[str], operation: str, 
                            user: str = "system") -> Dict[str, Any]:
        """
        Perform bulk operations on multiple twins.
        
        Args:
            twin_ids: List of twin IDs to operate on
            operation: Operation to perform ('start', 'stop', 'restart')
            user: User performing the operation
            
        Returns:
            Bulk operation result
        """
        try:
            logger.info(f"Performing bulk {operation} on {len(twin_ids)} twins")
            
            results = {
                "success": True,
                "operation": operation,
                "total_twins": len(twin_ids),
                "successful": 0,
                "failed": 0,
                "results": []
            }
            
            for twin_id in twin_ids:
                try:
                    if operation == "start":
                        result = await self.start_twin(twin_id, user)
                    elif operation == "stop":
                        result = await self.stop_twin(twin_id, user)
                    elif operation == "restart":
                        result = await self.restart_twin(twin_id, user)
                    else:
                        raise Exception(f"Unknown operation: {operation}")
                    
                    results["results"].append({
                        "twin_id": twin_id,
                        "success": True,
                        "result": result
                    })
                    results["successful"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to {operation} twin {twin_id}: {str(e)}")
                    results["results"].append({
                        "twin_id": twin_id,
                        "success": False,
                        "error": str(e)
                    })
                    results["failed"] += 1
            
            # Update overall success status
            if results["failed"] > 0:
                results["success"] = False
                results["message"] = f"Bulk operation completed with {results['failed']} failures"
            else:
                results["message"] = f"Bulk operation completed successfully"
            
            results["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"Bulk {operation} completed: {results['successful']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform bulk {operation}: {str(e)}")
            raise Exception(f"Failed to perform bulk {operation}: {str(e)}")
    
    async def get_twin_operations_history(self, twin_id: str, 
                                        limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get operation history for a twin.
        
        Args:
            twin_id: The twin ID to get history for
            limit: Maximum number of history entries
            
        Returns:
            List of operation history entries
        """
        try:
            logger.info(f"Getting operation history for twin: {twin_id}")
            
            # This would typically query a separate operations log table
            # For now, return a placeholder structure
            history = [
                {
                    "operation": "start",
                    "user": "system",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "details": "Twin started successfully"
                }
            ]
            
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get operation history for twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to get operation history for twin {twin_id}: {str(e)}")
    
    def _log_operation(self, twin_id: str, operation: str, user: str, 
                      status: str, error_message: str = None):
        """
        Log an operation for audit purposes.
        
        Args:
            twin_id: The twin ID
            operation: The operation performed
            user: User performing the operation
            status: Operation status ('success' or 'failed')
            error_message: Error message if failed
        """
        try:
            log_entry = {
                "twin_id": twin_id,
                "operation": operation,
                "user": user,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
            if error_message:
                log_entry["error_message"] = error_message
            
            # In a real implementation, this would be saved to a database
            logger.info(f"Operation logged: {log_entry}")
            
        except Exception as e:
            logger.error(f"Failed to log operation: {str(e)}") 