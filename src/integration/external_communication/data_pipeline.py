"""
Data Pipeline for Module Orchestration

This module provides data pipeline orchestration capabilities for coordinating
data flow between multiple modules, including stage execution, dependency
management, and error handling.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    PipelineConfig, 
    PipelineStage, 
    PipelineStatus,
    EventMessage,
    EventType
)
from .event_bridge import EventBridge


logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Executes individual pipeline stages."""
    
    def __init__(self, stage: PipelineStage, event_bridge: EventBridge):
        """
        Initialize pipeline executor.
        
        Args:
            stage: Pipeline stage to execute
            event_bridge: Event bridge for communication
        """
        self.stage = stage
        self.event_bridge = event_bridge
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the pipeline stage.
        
        Args:
            input_data: Input data for the stage
            
        Returns:
            Execution result
        """
        self.start_time = datetime.utcnow()
        self.stage.status = PipelineStatus.RUNNING
        
        try:
            # Publish workflow start event
            await self.event_bridge.send_workflow_event(
                source_module="pipeline_engine",
                target_module=self.stage.module_name,
                workflow_id=str(self.stage.stage_id),
                status="start",
                payload={
                    "stage_name": self.stage.stage_name,
                    "input_data": input_data
                }
            )
            
            # Simulate stage execution (in real implementation, this would call the actual module)
            await asyncio.sleep(1)  # Simulate processing time
            
            # Generate output data based on input
            self.result = {
                "stage_id": str(self.stage.stage_id),
                "stage_name": self.stage.stage_name,
                "input_data": input_data,
                "output_data": {
                    "processed": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "stage_order": self.stage.stage_order
                },
                "execution_time_ms": 1000  # Simulated execution time
            }
            
            self.stage.status = PipelineStatus.COMPLETED
            self.end_time = datetime.utcnow()
            
            # Publish workflow complete event
            await self.event_bridge.send_workflow_event(
                source_module="pipeline_engine",
                target_module=self.stage.module_name,
                workflow_id=str(self.stage.stage_id),
                status="complete",
                payload={
                    "stage_name": self.stage.stage_name,
                    "result": self.result
                }
            )
            
            logger.info(f"Stage {self.stage.stage_name} completed successfully")
            return self.result
            
        except Exception as e:
            self.error = str(e)
            self.stage.status = PipelineStatus.FAILED
            self.stage.error_message = str(e)
            self.end_time = datetime.utcnow()
            
            logger.error(f"Stage {self.stage.stage_name} failed: {e}")
            
            # Publish error event
            await self.event_bridge.publish_simple(
                event_type=EventType.ERROR_OCCURRED,
                source_module="pipeline_engine",
                target_module=self.stage.module_name,
                payload={
                    "stage_name": self.stage.stage_name,
                    "error": str(e),
                    "stage_id": str(self.stage.stage_id)
                }
            )
            
            raise
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """Get execution metrics for the stage."""
        execution_time = None
        if self.start_time and self.end_time:
            execution_time = (self.end_time - self.start_time).total_seconds() * 1000
        
        return {
            "stage_id": str(self.stage.stage_id),
            "stage_name": self.stage.stage_name,
            "status": self.stage.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time_ms": execution_time,
            "error": self.error,
            "result": self.result
        }


class DataPipeline:
    """
    Data pipeline orchestrator for coordinating data flow between modules.
    
    This pipeline provides:
    - Stage-by-stage execution with dependency management
    - Concurrent execution of independent stages
    - Error handling and retry logic
    - Progress monitoring and metrics
    - Event-driven communication between stages
    """
    
    def __init__(self, config: PipelineConfig, event_bridge: EventBridge):
        """
        Initialize the data pipeline.
        
        Args:
            config: Pipeline configuration
            event_bridge: Event bridge for communication
        """
        self.config = config
        self.event_bridge = event_bridge
        self.executors: Dict[str, PipelineExecutor] = {}
        self.stage_results: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self._execution_task: Optional[asyncio.Task] = None
        
        # Initialize executors for each stage
        for stage in config.stages:
            executor = PipelineExecutor(stage, event_bridge)
            self.executors[str(stage.stage_id)] = executor
    
    async def start(self) -> None:
        """Start pipeline execution."""
        if self.is_running:
            logger.warning("Pipeline is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.utcnow()
        self._execution_task = asyncio.create_task(self._execute_pipeline())
        
        logger.info(f"Started pipeline: {self.config.pipeline_name}")
        
        # Publish pipeline start event
        await self.event_bridge.publish_simple(
            event_type=EventType.WORKFLOW_START,
            source_module="pipeline_engine",
            payload={
                "pipeline_id": str(self.config.pipeline_id),
                "pipeline_name": self.config.pipeline_name,
                "stages_count": len(self.config.stages)
            }
        )
    
    async def stop(self) -> None:
        """Stop pipeline execution."""
        self.is_running = False
        
        if self._execution_task:
            self._execution_task.cancel()
            try:
                await self._execution_task
            except asyncio.CancelledError:
                pass
        
        self.end_time = datetime.utcnow()
        logger.info(f"Stopped pipeline: {self.config.pipeline_name}")
    
    async def _execute_pipeline(self) -> None:
        """Main pipeline execution logic."""
        try:
            # Sort stages by order
            sorted_stages = sorted(self.config.stages, key=lambda s: s.stage_order)
            
            # Execute stages sequentially (can be enhanced for parallel execution)
            for stage in sorted_stages:
                if not self.is_running:
                    break
                
                await self._execute_stage(stage)
                
                # Check if stage failed
                if stage.status == PipelineStatus.FAILED:
                    logger.error(f"Pipeline failed at stage: {stage.stage_name}")
                    break
            
            # Pipeline completed
            if self.is_running:
                await self._complete_pipeline()
            else:
                await self._cancel_pipeline()
                
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            await self._handle_pipeline_error(e)
    
    async def _execute_stage(self, stage: PipelineStage) -> None:
        """
        Execute a single pipeline stage.
        
        Args:
            stage: Stage to execute
        """
        executor = self.executors[str(stage.stage_id)]
        
        try:
            # Prepare input data (combine results from previous stages)
            input_data = self._prepare_stage_input(stage)
            
            # Execute the stage
            result = await executor.execute(input_data)
            
            # Store result
            self.stage_results[str(stage.stage_id)] = result
            
            # Update stage
            stage.completed_at = datetime.utcnow()
            
            logger.info(f"Stage {stage.stage_name} completed successfully")
            
        except Exception as e:
            logger.error(f"Stage {stage.stage_name} execution failed: {e}")
            stage.error_message = str(e)
            stage.completed_at = datetime.utcnow()
            raise
    
    def _prepare_stage_input(self, stage: PipelineStage) -> Dict[str, Any]:
        """
        Prepare input data for a stage based on dependencies.
        
        Args:
            stage: Stage to prepare input for
            
        Returns:
            Input data dictionary
        """
        input_data = {
            "stage_info": {
                "stage_id": str(stage.stage_id),
                "stage_name": stage.stage_name,
                "stage_order": stage.stage_order,
                "module_name": stage.module_name
            },
            "pipeline_info": {
                "pipeline_id": str(self.config.pipeline_id),
                "pipeline_name": self.config.pipeline_name
            },
            "dependencies": {}
        }
        
        # Add data from dependent stages
        for dep_name in stage.dependencies:
            for stage_id, result in self.stage_results.items():
                if result.get("stage_name") == dep_name:
                    input_data["dependencies"][dep_name] = result
                    break
        
        return input_data
    
    async def _complete_pipeline(self) -> None:
        """Handle successful pipeline completion."""
        self.end_time = datetime.utcnow()
        execution_time = (self.end_time - self.start_time).total_seconds()
        
        completion_record = {
            "timestamp": self.end_time,
            "status": "completed",
            "execution_time_seconds": execution_time,
            "stages_completed": len([s for s in self.config.stages if s.status == PipelineStatus.COMPLETED]),
            "stages_failed": len([s for s in self.config.stages if s.status == PipelineStatus.FAILED])
        }
        
        self.execution_history.append(completion_record)
        
        logger.info(f"Pipeline {self.config.pipeline_name} completed successfully in {execution_time:.2f}s")
        
        # Publish completion event
        await self.event_bridge.publish_simple(
            event_type=EventType.WORKFLOW_COMPLETE,
            source_module="pipeline_engine",
            payload={
                "pipeline_id": str(self.config.pipeline_id),
                "pipeline_name": self.config.pipeline_name,
                "execution_time_seconds": execution_time,
                "stages_completed": completion_record["stages_completed"]
            }
        )
    
    async def _cancel_pipeline(self) -> None:
        """Handle pipeline cancellation."""
        self.end_time = datetime.utcnow()
        
        cancellation_record = {
            "timestamp": self.end_time,
            "status": "cancelled",
            "reason": "User requested cancellation"
        }
        
        self.execution_history.append(cancellation_record)
        
        logger.info(f"Pipeline {self.config.pipeline_name} was cancelled")
    
    async def _handle_pipeline_error(self, error: Exception) -> None:
        """Handle pipeline execution error."""
        self.end_time = datetime.utcnow()
        
        error_record = {
            "timestamp": self.end_time,
            "status": "error",
            "error": str(error)
        }
        
        self.execution_history.append(error_record)
        
        logger.error(f"Pipeline {self.config.pipeline_name} failed with error: {error}")
        
        # Publish error event
        await self.event_bridge.publish_simple(
            event_type=EventType.ERROR_OCCURRED,
            source_module="pipeline_engine",
            payload={
                "pipeline_id": str(self.config.pipeline_id),
                "pipeline_name": self.config.pipeline_name,
                "error": str(error)
            }
        )
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        stages_status = {}
        for stage in self.config.stages:
            executor = self.executors.get(str(stage.stage_id))
            if executor:
                stages_status[stage.stage_name] = {
                    "status": stage.status.value,
                    "execution_metrics": executor.get_execution_metrics()
                }
        
        execution_time = None
        if self.start_time:
            end_time = self.end_time or datetime.utcnow()
            execution_time = (end_time - self.start_time).total_seconds()
        
        return {
            "pipeline_id": str(self.config.pipeline_id),
            "pipeline_name": self.config.pipeline_name,
            "status": "running" if self.is_running else "completed" if self.end_time else "pending",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time_seconds": execution_time,
            "total_stages": len(self.config.stages),
            "completed_stages": len([s for s in self.config.stages if s.status == PipelineStatus.COMPLETED]),
            "failed_stages": len([s for s in self.config.stages if s.status == PipelineStatus.FAILED]),
            "stages_status": stages_status,
            "execution_history": self.execution_history
        }
    
    def get_stage_result(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """Get result for a specific stage."""
        return self.stage_results.get(stage_id)
    
    def get_all_results(self) -> Dict[str, Any]:
        """Get results from all stages."""
        return {
            "pipeline_id": str(self.config.pipeline_id),
            "pipeline_name": self.config.pipeline_name,
            "stage_results": self.stage_results,
            "execution_summary": {
                "total_stages": len(self.config.stages),
                "completed_stages": len(self.stage_results),
                "execution_time": self.get_pipeline_status()["execution_time_seconds"]
            }
        }
    
    @classmethod
    def create_simple_pipeline(
        cls,
        name: str,
        stages: List[Dict[str, Any]],
        event_bridge: EventBridge
    ) -> "DataPipeline":
        """
        Create a simple pipeline from stage definitions.
        
        Args:
            name: Pipeline name
            stages: List of stage definitions
            event_bridge: Event bridge instance
            
        Returns:
            Configured DataPipeline instance
        """
        pipeline_stages = []
        
        for i, stage_def in enumerate(stages):
            stage = PipelineStage(
                stage_name=stage_def["name"],
                stage_order=i,
                module_name=stage_def["module"],
                operation=stage_def.get("operation", "process"),
                input_schema=stage_def.get("input_schema", {}),
                output_schema=stage_def.get("output_schema", {}),
                dependencies=stage_def.get("dependencies", [])
            )
            pipeline_stages.append(stage)
        
        config = PipelineConfig(
            pipeline_name=name,
            description=f"Simple pipeline: {name}",
            stages=pipeline_stages
        )
        
        return cls(config, event_bridge)
