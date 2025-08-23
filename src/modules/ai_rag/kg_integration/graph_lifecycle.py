"""
AI RAG Graph Lifecycle Manager
==============================

Service for managing the complete lifecycle of graphs from creation to retirement.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

from ..graph_models.graph_structure import GraphStructure
from ..graph_models.graph_metadata import GraphMetadata
from .graph_transfer_service import GraphTransferService
from .graph_sync_manager import GraphSyncManager

logger = logging.getLogger(__name__)


class GraphLifecycleStage(Enum):
    """Graph lifecycle stages."""
    CREATED = "created"
    PROCESSING = "processing"
    VALIDATED = "validated"
    PUBLISHED = "published"
    ACTIVE = "active"
    ARCHIVED = "archived"
    RETIRED = "retired"
    ERROR = "error"


class GraphLifecycleEvent(Enum):
    """Graph lifecycle events."""
    GRAPH_CREATED = "graph_created"
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    PUBLISHED = "published"
    ACTIVATED = "activated"
    ARCHIVED = "archived"
    RETIRED = "retired"
    ERROR_OCCURRED = "error_occurred"
    LIFECYCLE_CHANGED = "lifecycle_changed"


class GraphLifecycleManager:
    """
    Graph Lifecycle Manager for AI RAG and KG Neo4j Integration
    
    Manages the complete lifecycle of graphs from creation to retirement,
    including stage transitions, event handling, and lifecycle policies.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the graph lifecycle manager.
        
        Args:
            config: Configuration dictionary for graph lifecycle management
        """
        self.config = config or self._get_default_config()
        self.lifecycle_stats = {
            "graphs_managed": 0,
            "stage_transitions": 0,
            "events_processed": 0,
            "lifecycle_completions": 0,
            "errors_handled": 0
        }
        
        # Initialize services
        self.transfer_service = GraphTransferService(self.config.get("transfer_config", {}))
        self.sync_manager = GraphSyncManager(self.config.get("sync_config", {}))
        
        # Track lifecycle state
        self.lifecycle_state = {}
        self.lifecycle_policies = self._initialize_lifecycle_policies()
        self.event_handlers = self._initialize_event_handlers()
        
        # Lifecycle workflow definitions
        self.lifecycle_workflows = self._initialize_lifecycle_workflows()
        
        logger.info("✅ GraphLifecycleManager initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for graph lifecycle management."""
        return {
            "enable_auto_lifecycle": True,
            "enable_lifecycle_validation": True,
            "enable_lifecycle_events": True,
            "enable_lifecycle_policies": True,
            "default_lifecycle_workflow": "standard",
            "lifecycle_timeout": 3600,  # 1 hour
            "max_lifecycle_retries": 3,
            "enable_lifecycle_monitoring": True,
            "lifecycle_monitoring_interval": 300,  # 5 minutes
            "enable_lifecycle_cleanup": True,
            "lifecycle_cleanup_interval": 86400,  # 24 hours
            "enable_lifecycle_metrics": True,
            "lifecycle_stage_timeout": {
                "processing": 1800,  # 30 minutes
                "validation": 900,   # 15 minutes
                "publishing": 600    # 10 minutes
            },
            "transfer_config": {
                "kg_neo4j_api_url": "http://localhost:7474",
                "transfer_timeout": 300,
                "max_retries": 3
            },
            "sync_config": {
                "sync_interval_minutes": 15,
                "enable_auto_sync": True,
                "conflict_resolution_strategy": "ai_rag_wins"
            }
        }
    
    async def start_lifecycle_manager(self) -> None:
        """Start the graph lifecycle manager."""
        try:
            logger.info("🚀 Starting Graph Lifecycle Manager")
            
            # Initialize lifecycle state
            await self._initialize_lifecycle_state()
            
            # Start lifecycle monitoring if enabled
            if self.config["enable_lifecycle_monitoring"]:
                asyncio.create_task(self._lifecycle_monitoring_loop())
            
            # Start lifecycle cleanup if enabled
            if self.config["enable_lifecycle_cleanup"]:
                asyncio.create_task(self._lifecycle_cleanup_loop())
            
            # Start sync manager
            await self.sync_manager.start_sync_manager()
            
            logger.info("✅ Graph Lifecycle Manager started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Graph Lifecycle Manager: {e}")
            raise
    
    async def stop_lifecycle_manager(self) -> None:
        """Stop the graph lifecycle manager."""
        try:
            logger.info("🛑 Stopping Graph Lifecycle Manager")
            
            # Stop sync manager
            await self.sync_manager.stop_sync_manager()
            
            # Stop background tasks
            # In a real implementation, this would properly cancel tasks
            
            logger.info("✅ Graph Lifecycle Manager stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop Graph Lifecycle Manager: {e}")
    
    async def create_graph_lifecycle(
        self,
        graph_id: str,
        graph_structure: GraphStructure,
        graph_metadata: GraphMetadata,
        workflow_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new graph lifecycle.
        
        Args:
            graph_id: ID of the graph
            graph_structure: Graph structure
            graph_metadata: Graph metadata
            workflow_name: Optional workflow name override
            
        Returns:
            Dict: Lifecycle creation results
        """
        start_time = datetime.now()
        lifecycle_id = f"lifecycle_{graph_id}_{int(start_time.timestamp())}"
        
        logger.info(f"🎯 Creating graph lifecycle: {lifecycle_id} for graph: {graph_id}")
        
        try:
            # Determine workflow
            workflow_name = workflow_name or self.config["default_lifecycle_workflow"]
            workflow = self.lifecycle_workflows.get(workflow_name)
            
            if not workflow:
                return {
                    "lifecycle_id": lifecycle_id,
                    "graph_id": graph_id,
                    "status": "failed",
                    "error": f"Unknown workflow: {workflow_name}",
                    "creation_time_ms": 0
                }
            
            # Initialize lifecycle state
            lifecycle_state = {
                "lifecycle_id": lifecycle_id,
                "graph_id": graph_id,
                "workflow_name": workflow_name,
                "current_stage": GraphLifecycleStage.CREATED,
                "stage_history": [],
                "events": [],
                "start_time": start_time,
                "status": "active",
                "workflow": workflow
            }
            
            # Add initial stage
            await self._add_lifecycle_stage(lifecycle_state, GraphLifecycleStage.CREATED, "Lifecycle created")
            
            # Store lifecycle state
            self.lifecycle_state[lifecycle_id] = lifecycle_state
            
            # Process lifecycle event
            await self._process_lifecycle_event(
                lifecycle_id,
                GraphLifecycleEvent.GRAPH_CREATED,
                {"graph_structure": graph_structure.dict(), "graph_metadata": graph_metadata.dict()}
            )
            
            # Start workflow execution
            workflow_task = asyncio.create_task(
                self._execute_lifecycle_workflow(lifecycle_id, workflow)
            )
            
            # Calculate creation time
            end_time = datetime.now()
            creation_time = (end_time - start_time).total_seconds() * 1000
            
            # Update lifecycle statistics
            self._update_lifecycle_stats("graphs_managed", 1)
            
            logger.info(f"✅ Graph lifecycle created: {lifecycle_id} in {creation_time:.0f}ms")
            
            return {
                "lifecycle_id": lifecycle_id,
                "graph_id": graph_id,
                "workflow_name": workflow_name,
                "status": "created",
                "current_stage": GraphLifecycleStage.CREATED.value,
                "creation_time_ms": creation_time,
                "workflow_task": workflow_task
            }
            
        except Exception as e:
            logger.error(f"❌ Graph lifecycle creation failed: {lifecycle_id} - {e}")
            
            return {
                "lifecycle_id": lifecycle_id,
                "graph_id": graph_id,
                "status": "failed",
                "error": str(e),
                "creation_time_ms": 0
            }
    
    async def get_lifecycle_status(self, lifecycle_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific lifecycle."""
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                return None
            
            return {
                "lifecycle_id": lifecycle_id,
                "graph_id": lifecycle["graph_id"],
                "workflow_name": lifecycle["workflow_name"],
                "current_stage": lifecycle["current_stage"].value,
                "status": lifecycle["status"],
                "start_time": lifecycle["start_time"],
                "stage_history": lifecycle["stage_history"],
                "events": lifecycle["events"][-10:],  # Last 10 events
                "workflow_progress": self._calculate_workflow_progress(lifecycle)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get lifecycle status: {e}")
            return None
    
    async def transition_lifecycle_stage(
        self,
        lifecycle_id: str,
        new_stage: GraphLifecycleStage,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manually transition a lifecycle to a new stage.
        
        Args:
            lifecycle_id: ID of the lifecycle
            new_stage: New stage to transition to
            reason: Reason for transition
            metadata: Additional metadata
            
        Returns:
            Dict: Transition results
        """
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                return {
                    "lifecycle_id": lifecycle_id,
                    "status": "failed",
                    "error": "Lifecycle not found"
                }
            
            current_stage = lifecycle["current_stage"]
            
            # Validate transition
            if not self._is_valid_transition(current_stage, new_stage):
                return {
                    "lifecycle_id": lifecycle_id,
                    "status": "failed",
                    "error": f"Invalid transition from {current_stage.value} to {new_stage.value}"
                }
            
            # Perform transition
            await self._add_lifecycle_stage(lifecycle, new_stage, reason, metadata)
            
            # Update current stage
            lifecycle["current_stage"] = new_stage
            
            # Process lifecycle event
            await self._process_lifecycle_event(
                lifecycle_id,
                GraphLifecycleEvent.LIFECYCLE_CHANGED,
                {
                    "from_stage": current_stage.value,
                    "to_stage": new_stage.value,
                    "reason": reason,
                    "metadata": metadata or {}
                }
            )
            
            # Update lifecycle statistics
            self._update_lifecycle_stats("stage_transitions", 1)
            
            logger.info(f"🔄 Lifecycle stage transitioned: {lifecycle_id} {current_stage.value} -> {new_stage.value}")
            
            return {
                "lifecycle_id": lifecycle_id,
                "status": "success",
                "from_stage": current_stage.value,
                "to_stage": new_stage.value,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"❌ Lifecycle stage transition failed: {e}")
            return {
                "lifecycle_id": lifecycle_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def pause_lifecycle(self, lifecycle_id: str, reason: str = "") -> Dict[str, Any]:
        """Pause a lifecycle."""
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                return {
                    "lifecycle_id": lifecycle_id,
                    "status": "failed",
                    "error": "Lifecycle not found"
                }
            
            lifecycle["status"] = "paused"
            lifecycle["pause_reason"] = reason
            lifecycle["pause_time"] = datetime.now()
            
            # Process lifecycle event
            await self._process_lifecycle_event(
                lifecycle_id,
                GraphLifecycleEvent.LIFECYCLE_CHANGED,
                {"action": "paused", "reason": reason}
            )
            
            logger.info(f"⏸️ Lifecycle paused: {lifecycle_id} - {reason}")
            
            return {
                "lifecycle_id": lifecycle_id,
                "status": "success",
                "action": "paused",
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to pause lifecycle: {e}")
            return {
                "lifecycle_id": lifecycle_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def resume_lifecycle(self, lifecycle_id: str) -> Dict[str, Any]:
        """Resume a paused lifecycle."""
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                return {
                    "lifecycle_id": lifecycle_id,
                    "status": "failed",
                    "error": "Lifecycle not found"
                }
            
            if lifecycle["status"] != "paused":
                return {
                    "lifecycle_id": lifecycle_id,
                    "status": "failed",
                    "error": "Lifecycle is not paused"
                }
            
            lifecycle["status"] = "active"
            lifecycle["resume_time"] = datetime.now()
            
            # Process lifecycle event
            await self._process_lifecycle_event(
                lifecycle_id,
                GraphLifecycleEvent.LIFECYCLE_CHANGED,
                {"action": "resumed"}
            )
            
            # Restart workflow execution
            workflow = lifecycle["workflow"]
            workflow_task = asyncio.create_task(
                self._execute_lifecycle_workflow(lifecycle_id, workflow)
            )
            
            logger.info(f"▶️ Lifecycle resumed: {lifecycle_id}")
            
            return {
                "lifecycle_id": lifecycle_id,
                "status": "success",
                "action": "resumed",
                "workflow_task": workflow_task
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to resume lifecycle: {e}")
            return {
                "lifecycle_id": lifecycle_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def cancel_lifecycle(self, lifecycle_id: str, reason: str = "") -> Dict[str, Any]:
        """Cancel a lifecycle."""
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                return {
                    "lifecycle_id": lifecycle_id,
                    "status": "failed",
                    "error": "Lifecycle not found"
                }
            
            lifecycle["status"] = "cancelled"
            lifecycle["cancel_reason"] = reason
            lifecycle["cancel_time"] = datetime.now()
            
            # Process lifecycle event
            await self._process_lifecycle_event(
                lifecycle_id,
                GraphLifecycleEvent.LIFECYCLE_CHANGED,
                {"action": "cancelled", "reason": reason}
            )
            
            logger.info(f"❌ Lifecycle cancelled: {lifecycle_id} - {reason}")
            
            return {
                "lifecycle_id": lifecycle_id,
                "status": "success",
                "action": "cancelled",
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel lifecycle: {e}")
            return {
                "lifecycle_id": lifecycle_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_lifecycle_workflow(
        self,
        lifecycle_id: str,
        workflow: Dict[str, Any]
    ) -> None:
        """Execute a lifecycle workflow."""
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                logger.error(f"❌ Lifecycle not found: {lifecycle_id}")
                return
            
            logger.info(f"🔄 Executing workflow for lifecycle: {lifecycle_id}")
            
            # Execute workflow stages
            for stage_config in workflow["stages"]:
                try:
                    # Check if lifecycle is still active
                    if lifecycle["status"] not in ["active", "processing"]:
                        logger.info(f"⏸️ Lifecycle {lifecycle_id} is no longer active, stopping workflow")
                        break
                    
                    stage_name = stage_config["name"]
                    stage_handler = stage_config["handler"]
                    stage_timeout = stage_config.get("timeout", 300)
                    
                    logger.info(f"🎯 Executing workflow stage: {stage_name}")
                    
                    # Execute stage
                    stage_result = await asyncio.wait_for(
                        self._execute_workflow_stage(lifecycle_id, stage_handler, stage_config),
                        timeout=stage_timeout
                    )
                    
                    if not stage_result["success"]:
                        logger.error(f"❌ Workflow stage failed: {stage_name} - {stage_result['error']}")
                        
                        # Handle stage failure
                        await self._handle_stage_failure(lifecycle_id, stage_name, stage_result)
                        break
                    
                    logger.info(f"✅ Workflow stage completed: {stage_name}")
                    
                except asyncio.TimeoutError:
                    logger.error(f"⏰ Workflow stage timeout: {stage_name}")
                    await self._handle_stage_timeout(lifecycle_id, stage_name)
                    break
                
                except Exception as e:
                    logger.error(f"❌ Workflow stage error: {stage_name} - {e}")
                    await self._handle_stage_error(lifecycle_id, stage_name, str(e))
                    break
            
            # Workflow completed
            logger.info(f"✅ Workflow execution completed for lifecycle: {lifecycle_id}")
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {lifecycle_id} - {e}")
            await self._handle_workflow_error(lifecycle_id, str(e))
    
    async def _execute_workflow_stage(
        self,
        lifecycle_id: str,
        stage_handler: str,
        stage_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific workflow stage."""
        try:
            if stage_handler == "process_graph":
                return await self._process_graph_stage(lifecycle_id, stage_config)
            
            elif stage_handler == "validate_graph":
                return await self._validate_graph_stage(lifecycle_id, stage_config)
            
            elif stage_handler == "publish_graph":
                return await self._publish_graph_stage(lifecycle_id, stage_config)
            
            elif stage_handler == "activate_graph":
                return await self._activate_graph_stage(lifecycle_id, stage_config)
            
            elif stage_handler == "sync_to_kg_neo4j":
                return await self._sync_to_kg_neo4j_stage(lifecycle_id, stage_config)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown stage handler: {stage_handler}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_graph_stage(
        self,
        lifecycle_id: str,
        stage_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute graph processing stage."""
        try:
            # Transition to processing stage
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.PROCESSING,
                "Graph processing started"
            )
            
            # Simulate processing
            await asyncio.sleep(2)
            
            # Transition to completed stage
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.VALIDATED,
                "Graph processing completed"
            )
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_graph_stage(
        self,
        lifecycle_id: str,
        stage_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute graph validation stage."""
        try:
            # Transition to validation stage
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.VALIDATED,
                "Graph validation started"
            )
            
            # Simulate validation
            await asyncio.sleep(1)
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _publish_graph_stage(
        self,
        lifecycle_id: str,
        stage_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute graph publishing stage."""
        try:
            # Transition to published stage
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.PUBLISHED,
                "Graph published"
            )
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _activate_graph_stage(
        self,
        lifecycle_id: str,
        stage_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute graph activation stage."""
        try:
            # Transition to active stage
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.ACTIVE,
                "Graph activated"
            )
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _sync_to_kg_neo4j_stage(
        self,
        lifecycle_id: str,
        stage_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute KG Neo4j synchronization stage."""
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                return {"success": False, "error": "Lifecycle not found"}
            
            # Perform synchronization
            sync_result = await self.sync_manager.sync_graph(lifecycle["graph_id"])
            
            if sync_result["status"] == "success":
                return {"success": True, "sync_result": sync_result}
            else:
                return {"success": False, "error": f"Sync failed: {sync_result.get('error', 'Unknown error')}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _add_lifecycle_stage(
        self,
        lifecycle: Dict[str, Any],
        stage: GraphLifecycleStage,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a new stage to lifecycle history."""
        stage_entry = {
            "stage": stage.value,
            "timestamp": datetime.now(),
            "reason": reason,
            "metadata": metadata or {}
        }
        
        lifecycle["stage_history"].append(stage_entry)
    
    async def _process_lifecycle_event(
        self,
        lifecycle_id: str,
        event_type: GraphLifecycleEvent,
        event_data: Dict[str, Any]
    ) -> None:
        """Process a lifecycle event."""
        try:
            lifecycle = self.lifecycle_state.get(lifecycle_id)
            if not lifecycle:
                return
            
            event = {
                "event_type": event_type.value,
                "timestamp": datetime.now(),
                "data": event_data
            }
            
            lifecycle["events"].append(event)
            
            # Update lifecycle statistics
            self._update_lifecycle_stats("events_processed", 1)
            
            # Execute event handlers if enabled
            if self.config["enable_lifecycle_events"]:
                await self._execute_event_handlers(event_type, event_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to process lifecycle event: {e}")
    
    async def _execute_event_handlers(
        self,
        event_type: GraphLifecycleEvent,
        event_data: Dict[str, Any]
    ) -> None:
        """Execute event handlers for a lifecycle event."""
        try:
            handlers = self.event_handlers.get(event_type, [])
            
            for handler in handlers:
                try:
                    await handler(event_type, event_data)
                except Exception as e:
                    logger.error(f"❌ Event handler failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to execute event handlers: {e}")
    
    async def _handle_stage_failure(
        self,
        lifecycle_id: str,
        stage_name: str,
        stage_result: Dict[str, Any]
    ) -> None:
        """Handle workflow stage failure."""
        try:
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.ERROR,
                f"Stage {stage_name} failed: {stage_result['error']}"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to handle stage failure: {e}")
    
    async def _handle_stage_timeout(
        self,
        lifecycle_id: str,
        stage_name: str
    ) -> None:
        """Handle workflow stage timeout."""
        try:
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.ERROR,
                f"Stage {stage_name} timed out"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to handle stage timeout: {e}")
    
    async def _handle_stage_error(
        self,
        lifecycle_id: str,
        stage_name: str,
        error: str
    ) -> None:
        """Handle workflow stage error."""
        try:
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.ERROR,
                f"Stage {stage_name} error: {error}"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to handle stage error: {e}")
    
    async def _handle_workflow_error(
        self,
        lifecycle_id: str,
        error: str
    ) -> None:
        """Handle workflow execution error."""
        try:
            await self.transition_lifecycle_stage(
                lifecycle_id,
                GraphLifecycleStage.ERROR,
                f"Workflow error: {error}"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to handle workflow error: {e}")
    
    def _is_valid_transition(
        self,
        from_stage: GraphLifecycleStage,
        to_stage: GraphLifecycleStage
    ) -> bool:
        """Check if a stage transition is valid."""
        # Define valid transitions
        valid_transitions = {
            GraphLifecycleStage.CREATED: [GraphLifecycleStage.PROCESSING, GraphLifecycleStage.ERROR],
            GraphLifecycleStage.PROCESSING: [GraphLifecycleStage.VALIDATED, GraphLifecycleStage.ERROR],
            GraphLifecycleStage.VALIDATED: [GraphLifecycleStage.PUBLISHED, GraphLifecycleStage.ERROR],
            GraphLifecycleStage.PUBLISHED: [GraphLifecycleStage.ACTIVE, GraphLifecycleStage.ERROR],
            GraphLifecycleStage.ACTIVE: [GraphLifecycleStage.ARCHIVED, GraphLifecycleStage.ERROR],
            GraphLifecycleStage.ARCHIVED: [GraphLifecycleStage.RETIRED, GraphLifecycleStage.ACTIVE, GraphLifecycleStage.ERROR],
            GraphLifecycleStage.RETIRED: [GraphLifecycleStage.ERROR],
            GraphLifecycleStage.ERROR: [GraphLifecycleStage.CREATED, GraphLifecycleStage.RETIRED]
        }
        
        return to_stage in valid_transitions.get(from_stage, [])
    
    def _calculate_workflow_progress(self, lifecycle: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate workflow progress."""
        try:
            workflow = lifecycle["workflow"]
            total_stages = len(workflow["stages"])
            
            # Find current stage index
            current_stage = lifecycle["current_stage"]
            current_stage_index = -1
            
            for i, stage in enumerate(workflow["stages"]):
                if stage["name"] == current_stage.value:
                    current_stage_index = i
                    break
            
            if current_stage_index == -1:
                return {"progress_percent": 0, "current_stage_index": -1, "total_stages": total_stages}
            
            progress_percent = ((current_stage_index + 1) / total_stages) * 100
            
            return {
                "progress_percent": round(progress_percent, 2),
                "current_stage_index": current_stage_index,
                "total_stages": total_stages,
                "stages_completed": current_stage_index + 1,
                "stages_remaining": total_stages - (current_stage_index + 1)
            }
            
        except Exception:
            return {"progress_percent": 0, "current_stage_index": -1, "total_stages": 0}
    
    async def _lifecycle_monitoring_loop(self) -> None:
        """Lifecycle monitoring loop."""
        while True:
            try:
                await self._perform_lifecycle_monitoring()
                await asyncio.sleep(self.config["lifecycle_monitoring_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Lifecycle monitoring failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _lifecycle_cleanup_loop(self) -> None:
        """Lifecycle cleanup loop."""
        while True:
            try:
                await self._perform_lifecycle_cleanup()
                await asyncio.sleep(self.config["lifecycle_cleanup_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Lifecycle cleanup failed: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _perform_lifecycle_monitoring(self) -> None:
        """Perform lifecycle monitoring."""
        try:
            active_lifecycles = [l for l in self.lifecycle_state.values() if l["status"] == "active"]
            
            for lifecycle in active_lifecycles:
                # Check for stuck lifecycles
                if self._is_lifecycle_stuck(lifecycle):
                    logger.warning(f"⚠️ Lifecycle appears stuck: {lifecycle['lifecycle_id']}")
                    
                    # Attempt recovery
                    await self._attempt_lifecycle_recovery(lifecycle["lifecycle_id"])
            
            logger.info(f"🏥 Lifecycle monitoring completed: {len(active_lifecycles)} active lifecycles")
            
        except Exception as e:
            logger.error(f"❌ Lifecycle monitoring failed: {e}")
    
    async def _perform_lifecycle_cleanup(self) -> None:
        """Perform lifecycle cleanup."""
        try:
            # Clean up completed lifecycles older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            lifecycles_to_remove = []
            for lifecycle_id, lifecycle in self.lifecycle_state.items():
                if (lifecycle["status"] in ["completed", "cancelled", "error"] and
                    lifecycle["start_time"] < cutoff_date):
                    lifecycles_to_remove.append(lifecycle_id)
            
            for lifecycle_id in lifecycles_to_remove:
                del self.lifecycle_state[lifecycle_id]
            
            if lifecycles_to_remove:
                logger.info(f"🧹 Lifecycle cleanup completed: {len(lifecycles_to_remove)} lifecycles removed")
            
        except Exception as e:
            logger.error(f"❌ Lifecycle cleanup failed: {e}")
    
    def _is_lifecycle_stuck(self, lifecycle: Dict[str, Any]) -> bool:
        """Check if a lifecycle is stuck."""
        try:
            current_stage = lifecycle["current_stage"]
            stage_timeout = self.config["lifecycle_stage_timeout"].get(current_stage.value, 1800)
            
            # Check if current stage has been active too long
            if lifecycle["stage_history"]:
                last_stage_time = lifecycle["stage_history"][-1]["timestamp"]
                time_in_stage = (datetime.now() - last_stage_time).total_seconds()
                
                return time_in_stage > stage_timeout
            
            return False
            
        except Exception:
            return False
    
    async def _attempt_lifecycle_recovery(self, lifecycle_id: str) -> None:
        """Attempt to recover a stuck lifecycle."""
        try:
            logger.info(f"🔄 Attempting lifecycle recovery: {lifecycle_id}")
            
            # For now, just log the recovery attempt
            # In a real implementation, this would implement recovery logic
            
        except Exception as e:
            logger.error(f"❌ Lifecycle recovery failed: {e}")
    
    async def _initialize_lifecycle_state(self) -> None:
        """Initialize lifecycle state."""
        try:
            # In a real implementation, this would load lifecycle state from database
            self.lifecycle_state = {}
            logger.info("🔄 Lifecycle state initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize lifecycle state: {e}")
    
    def _initialize_lifecycle_policies(self) -> Dict[str, Any]:
        """Initialize lifecycle policies."""
        return {
            "auto_retry_failed_stages": True,
            "max_retry_attempts": 3,
            "retry_delay_seconds": 60,
            "enable_stage_timeouts": True,
            "enable_automatic_cleanup": True,
            "cleanup_retention_days": 30
        }
    
    def _initialize_event_handlers(self) -> Dict[GraphLifecycleEvent, List]:
        """Initialize event handlers."""
        return {
            GraphLifecycleEvent.GRAPH_CREATED: [],
            GraphLifecycleEvent.PROCESSING_STARTED: [],
            GraphLifecycleEvent.PROCESSING_COMPLETED: [],
            GraphLifecycleEvent.VALIDATION_STARTED: [],
            GraphLifecycleEvent.VALIDATION_COMPLETED: [],
            GraphLifecycleEvent.PUBLISHED: [],
            GraphLifecycleEvent.ACTIVATED: [],
            GraphLifecycleEvent.ARCHIVED: [],
            GraphLifecycleEvent.RETIRED: [],
            GraphLifecycleEvent.ERROR_OCCURRED: [],
            GraphLifecycleEvent.LIFECYCLE_CHANGED: []
        }
    
    def _initialize_lifecycle_workflows(self) -> Dict[str, Any]:
        """Initialize lifecycle workflows."""
        return {
            "standard": {
                "name": "Standard Graph Lifecycle",
                "description": "Standard workflow for graph processing and publication",
                "stages": [
                    {"name": "created", "handler": "process_graph", "timeout": 1800},
                    {"name": "processing", "handler": "validate_graph", "timeout": 900},
                    {"name": "validated", "handler": "publish_graph", "timeout": 600},
                    {"name": "published", "handler": "activate_graph", "timeout": 300},
                    {"name": "active", "handler": "sync_to_kg_neo4j", "timeout": 600}
                ]
            },
            "quick": {
                "name": "Quick Graph Lifecycle",
                "description": "Fast workflow for simple graphs",
                "stages": [
                    {"name": "created", "handler": "process_graph", "timeout": 900},
                    {"name": "processing", "handler": "sync_to_kg_neo4j", "timeout": 600}
                ]
            }
        }
    
    def _update_lifecycle_stats(self, stat_name: str, increment: int = 1) -> None:
        """Update lifecycle statistics."""
        if stat_name in self.lifecycle_stats:
            self.lifecycle_stats[stat_name] += increment
    
    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """Get lifecycle statistics."""
        return self.lifecycle_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset lifecycle statistics."""
        self.lifecycle_stats = {
            "graphs_managed": 0,
            "stage_transitions": 0,
            "events_processed": 0,
            "lifecycle_completions": 0,
            "errors_handled": 0
        }
        logger.info("🔄 Lifecycle statistics reset")
    
    def get_available_workflows(self) -> Dict[str, Any]:
        """Get available lifecycle workflows."""
        return {name: workflow["description"] for name, workflow in self.lifecycle_workflows.items()}
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update lifecycle configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Lifecycle configuration updated")

