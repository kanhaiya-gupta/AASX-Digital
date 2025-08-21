"""
Module Orchestrator Service

This service orchestrates complex workflows and interactions between
multiple modules, enabling sophisticated multi-step processes and
automated workflow execution.

The orchestrator coordinates module operations, manages workflow state,
handles errors and rollbacks, and provides a unified interface for
complex multi-module operations.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from collections import defaultdict

from .models import WorkflowStep, WorkflowResult, WorkflowStatus, ModuleInfo


logger = logging.getLogger(__name__)


class WorkflowDefinition:
    """Defines a workflow with steps and dependencies."""
    
    def __init__(self, workflow_id: UUID, name: str, description: str = ""):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps: List[Dict[str, Any]] = []
        self.dependencies: Dict[str, List[str]] = defaultdict(list)
        self.retry_policy: Dict[str, Any] = {}
        self.timeout: Optional[int] = None
        self.created_at = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}
    
    def add_step(self, step_id: str, module_name: str, operation: str, parameters: Dict[str, Any] = None, dependencies: List[str] = None):
        """Add a step to the workflow."""
        step = {
            "step_id": step_id,
            "module_name": module_name,
            "operation": operation,
            "parameters": parameters or {},
            "dependencies": dependencies or [],
            "retry_count": 0,
            "max_retries": 3
        }
        
        self.steps.append(step)
        
        # Update dependencies
        if dependencies:
            for dep in dependencies:
                self.dependencies[step_id].append(dep)
    
    def get_step(self, step_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific step by ID."""
        for step in self.steps:
            if step["step_id"] == step_id:
                return step
        return None
    
    def get_ready_steps(self, completed_steps: List[str]) -> List[str]:
        """Get steps that are ready to execute (dependencies satisfied)."""
        ready_steps = []
        
        for step in self.steps:
            step_id = step["step_id"]
            if step_id in completed_steps:
                continue
            
            dependencies = step.get("dependencies", [])
            if all(dep in completed_steps for dep in dependencies):
                ready_steps.append(step_id)
        
        return ready_steps


class ModuleOrchestratorService:
    """
    Service for orchestrating complex workflows between multiple modules.
    
    This service coordinates module operations, manages workflow state,
    handles errors and rollbacks, and provides a unified interface for
    complex multi-module operations.
    """
    
    def __init__(self, max_concurrent_workflows: int = 20):
        """
        Initialize the module orchestrator service.
        
        Args:
            max_concurrent_workflows: Maximum number of concurrent workflows
        """
        self.max_concurrent_workflows = max_concurrent_workflows
        
        # Workflow management
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_workflows: Dict[UUID, WorkflowResult] = {}
        self.workflow_history: List[WorkflowResult] = []
        
        # Workflow templates
        self.workflow_templates: Dict[str, Dict] = {}
        self._initialize_workflow_templates()
        
        # Performance tracking
        self.workflow_metrics: Dict[str, List[Dict]] = defaultdict(list)
        self.module_usage_stats: Dict[str, Dict] = defaultdict(lambda: {"total_executions": 0, "successful_executions": 0, "failed_executions": 0})
    
    def _initialize_workflow_templates(self):
        """Initialize predefined workflow templates."""
        
        # Carbon Footprint Analysis Workflow
        carbon_footprint_workflow = {
            "name": "Carbon Footprint Analysis",
            "description": "Complete workflow for analyzing carbon footprint from AASX files",
            "steps": [
                {
                    "step_id": "upload_aasx",
                    "module_name": "aasx",
                    "operation": "process_aasx_file",
                    "parameters": {"file_type": "aasx", "validation_level": "strict"},
                    "dependencies": []
                },
                {
                    "step_id": "extract_data",
                    "module_name": "aasx",
                    "operation": "extract_structured_data",
                    "parameters": {"extract_metadata": True, "extract_relationships": True},
                    "dependencies": ["upload_aasx"]
                },
                {
                    "step_id": "ai_analysis",
                    "module_name": "ai_rag",
                    "operation": "analyze_carbon_footprint",
                    "parameters": {"analysis_type": "carbon_footprint", "detail_level": "comprehensive"},
                    "dependencies": ["extract_data"]
                },
                {
                    "step_id": "store_twin",
                    "module_name": "twin_registry",
                    "operation": "create_digital_twin",
                    "parameters": {"twin_type": "carbon_footprint", "metadata": "auto_generated"},
                    "dependencies": ["ai_analysis"]
                },
                {
                    "step_id": "knowledge_graph",
                    "module_name": "kg_neo4j",
                    "operation": "index_analysis_results",
                    "parameters": {"index_type": "carbon_footprint", "relationship_depth": 3},
                    "dependencies": ["store_twin"]
                },
                {
                    "step_id": "generate_report",
                    "module_name": "ai_rag",
                    "operation": "generate_analysis_report",
                    "parameters": {"report_format": "comprehensive", "include_recommendations": True},
                    "dependencies": ["knowledge_graph"]
                }
            ],
            "retry_policy": {"max_retries": 3, "retry_delay": 5},
            "timeout": 1800  # 30 minutes
        }
        
        # Digital Twin Creation Workflow
        twin_creation_workflow = {
            "name": "Digital Twin Creation",
            "description": "Workflow for creating and configuring digital twins",
            "steps": [
                {
                    "step_id": "validate_input",
                    "module_name": "twin_registry",
                    "operation": "validate_twin_configuration",
                    "parameters": {"validation_level": "strict"},
                    "dependencies": []
                },
                {
                    "step_id": "create_twin",
                    "module_name": "twin_registry",
                    "operation": "create_digital_twin",
                    "parameters": {"twin_type": "standard", "auto_configure": True},
                    "dependencies": ["validate_input"]
                },
                {
                    "step_id": "configure_physics",
                    "module_name": "physics_modeling",
                    "operation": "configure_physics_models",
                    "parameters": {"model_type": "standard", "auto_calibration": True},
                    "dependencies": ["create_twin"]
                },
                {
                    "step_id": "setup_monitoring",
                    "module_name": "twin_registry",
                    "operation": "setup_monitoring_configuration",
                    "parameters": {"monitoring_type": "comprehensive", "alerting": True},
                    "dependencies": ["configure_physics"]
                }
            ],
            "retry_policy": {"max_retries": 2, "retry_delay": 3},
            "timeout": 900  # 15 minutes
        }
        
        # AI Model Training Workflow
        ai_training_workflow = {
            "name": "AI Model Training",
            "description": "Workflow for training AI models using federated learning",
            "steps": [
                {
                    "step_id": "prepare_data",
                    "module_name": "ai_rag",
                    "operation": "prepare_training_data",
                    "parameters": {"data_type": "structured", "preprocessing": "standard"},
                    "dependencies": []
                },
                {
                    "step_id": "train_model",
                    "module_name": "federated_learning",
                    "operation": "train_federated_model",
                    "parameters": {"model_type": "neural_network", "federation_rounds": 10},
                    "dependencies": ["prepare_data"]
                },
                {
                    "step_id": "validate_model",
                    "module_name": "ai_rag",
                    "operation": "validate_model_performance",
                    "parameters": {"validation_metrics": "comprehensive", "threshold": 0.85},
                    "dependencies": ["train_model"]
                },
                {
                    "step_id": "deploy_model",
                    "module_name": "ai_rag",
                    "operation": "deploy_trained_model",
                    "parameters": {"deployment_type": "production", "monitoring": True},
                    "dependencies": ["validate_model"]
                }
            ],
            "retry_policy": {"max_retries": 5, "retry_delay": 10},
            "timeout": 3600  # 1 hour
        }
        
        self.workflow_templates = {
            "carbon_footprint_analysis": carbon_footprint_workflow,
            "digital_twin_creation": twin_creation_workflow,
            "ai_model_training": ai_training_workflow
        }
    
    async def create_workflow_from_template(
        self,
        template_name: str,
        workflow_name: str = None,
        parameters: Dict[str, Any] = None
    ) -> Optional[WorkflowDefinition]:
        """
        Create a workflow from a predefined template.
        
        Args:
            template_name: Name of the template to use
            workflow_name: Custom name for the workflow
            parameters: Custom parameters to override template defaults
            
        Returns:
            WorkflowDefinition if successful, None otherwise
        """
        try:
            if template_name not in self.workflow_templates:
                logger.error(f"Workflow template '{template_name}' not found")
                return None
            
            template = self.workflow_templates[template_name]
            
            # Create workflow definition
            workflow_id = uuid4()
            workflow = WorkflowDefinition(
                workflow_id=workflow_id,
                name=workflow_name or template["name"],
                description=template["description"]
            )
            
            # Apply template steps
            for step_data in template["steps"]:
                step_id = step_data["step_id"]
                module_name = step_data["module_name"]
                operation = step_data["operation"]
                step_params = step_data["parameters"].copy()
                dependencies = step_data["dependencies"]
                
                # Override with custom parameters if provided
                if parameters and step_id in parameters:
                    step_params.update(parameters[step_id])
                
                workflow.add_step(step_id, module_name, operation, step_params, dependencies)
            
            # Apply template configuration
            workflow.retry_policy = template.get("retry_policy", {})
            workflow.timeout = template.get("timeout")
            workflow.metadata = {"template": template_name}
            
            # Store workflow definition
            self.workflow_definitions[str(workflow_id)] = workflow
            
            logger.info(f"Created workflow from template '{template_name}': {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Error creating workflow from template '{template_name}': {e}")
            return None
    
    async def execute_workflow(
        self,
        workflow_definition: WorkflowDefinition,
        input_data: Dict[str, Any] = None,
        timeout: int = None
    ) -> WorkflowResult:
        """
        Execute a workflow.
        
        Args:
            workflow_definition: The workflow to execute
            input_data: Input data for the workflow
            timeout: Workflow timeout in seconds
            
        Returns:
            WorkflowResult containing execution results
        """
        try:
            # Check if we can start a new workflow
            if len(self.active_workflows) >= self.max_concurrent_workflows:
                raise RuntimeError(f"Maximum concurrent workflows ({self.max_concurrent_workflows}) reached")
            
            # Create workflow result
            workflow_result = WorkflowResult(
                workflow_id=workflow_definition.workflow_id,
                workflow_name=workflow_definition.name
            )
            
            # Add workflow to active workflows
            self.active_workflows[workflow_definition.workflow_id] = workflow_result
            
            # Execute workflow
            await self._execute_workflow_internal(workflow_definition, workflow_result, input_data, timeout)
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_definition.workflow_id}: {e}")
            
            # Create failed workflow result
            workflow_result = WorkflowResult(
                workflow_id=workflow_definition.workflow_id,
                workflow_name=workflow_definition.name
            )
            workflow_result.fail(str(e))
            
            return workflow_result
    
    async def _execute_workflow_internal(
        self,
        workflow_definition: WorkflowDefinition,
        workflow_result: WorkflowResult,
        input_data: Dict[str, Any],
        timeout: int
    ):
        """Internal workflow execution logic."""
        try:
            logger.info(f"Starting workflow execution: {workflow_definition.name}")
            
            # Set workflow timeout
            workflow_timeout = timeout or workflow_definition.timeout or 3600  # Default 1 hour
            
            # Initialize workflow state
            completed_steps = []
            failed_steps = []
            step_results = {}
            
            # Workflow execution loop
            start_time = datetime.utcnow()
            
            while len(completed_steps) + len(failed_steps) < len(workflow_definition.steps):
                # Check timeout
                if (datetime.utcnow() - start_time).total_seconds() > workflow_timeout:
                    workflow_result.fail(f"Workflow timeout after {workflow_timeout} seconds")
                    return
                
                # Get ready steps
                ready_steps = workflow_definition.get_ready_steps(completed_steps)
                
                if not ready_steps and not failed_steps:
                    # No steps ready and no failures - workflow is stuck
                    workflow_result.fail("Workflow execution stuck - no steps can proceed")
                    return
                
                # Execute ready steps in parallel
                execution_tasks = []
                for step_id in ready_steps:
                    task = asyncio.create_task(
                        self._execute_workflow_step(workflow_definition, step_id, step_results, input_data)
                    )
                    execution_tasks.append((step_id, task))
                
                # Wait for all ready steps to complete
                for step_id, task in execution_tasks:
                    try:
                        step_result = await asyncio.wait_for(task, timeout=workflow_timeout)
                        if step_result["status"] == "completed":
                            completed_steps.append(step_id)
                            step_results[step_id] = step_result
                        else:
                            failed_steps.append(step_id)
                    except asyncio.TimeoutError:
                        logger.error(f"Step {step_id} timed out")
                        failed_steps.append(step_id)
                    except Exception as e:
                        logger.error(f"Step {step_id} failed: {e}")
                        failed_steps.append(step_id)
                
                # Check if we have failures that prevent continuation
                if failed_steps:
                    # Check if any failed steps are dependencies for remaining steps
                    remaining_steps = [step["step_id"] for step in workflow_definition.steps if step["step_id"] not in completed_steps and step["step_id"] not in failed_steps]
                    
                    for step_id in remaining_steps:
                        step = workflow_definition.get_step(step_id)
                        if step and any(dep in failed_steps for dep in step.get("dependencies", [])):
                            # This step depends on a failed step - mark as failed
                            failed_steps.append(step_id)
                    
                    # If all remaining steps are failed, workflow fails
                    if len(completed_steps) + len(failed_steps) == len(workflow_definition.steps):
                        workflow_result.fail(f"Workflow failed - {len(failed_steps)} steps failed")
                        return
            
            # Workflow completed
            if failed_steps:
                workflow_result.fail(f"Workflow completed with {len(failed_steps)} failed steps")
            else:
                workflow_result.complete(step_results)
            
            logger.info(f"Workflow execution completed: {workflow_definition.name}")
            
        except Exception as e:
            logger.error(f"Error in workflow execution: {e}")
            workflow_result.fail(str(e))
        
        finally:
            # Remove from active workflows and add to history
            if workflow_definition.workflow_id in self.active_workflows:
                del self.active_workflows[workflow_definition.workflow_id]
            
            self.workflow_history.append(workflow_result)
            
            # Keep only recent history
            if len(self.workflow_history) > 1000:
                self.workflow_history = self.workflow_history[-1000:]
    
    async def _execute_workflow_step(
        self,
        workflow_definition: WorkflowDefinition,
        step_id: str,
        step_results: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            step = workflow_definition.get_step(step_id)
            if not step:
                return {"status": "failed", "error": f"Step {step_id} not found"}
            
            # Create workflow step object
            workflow_step = WorkflowStep(
                module_name=step["module_name"],
                operation=step["operation"],
                parameters=step["parameters"]
            )
            
            # Add step to workflow result
            workflow_result = self.active_workflows.get(workflow_definition.workflow_id)
            if workflow_result:
                workflow_result.add_step(workflow_step)
            
            # Start step execution
            workflow_step.start()
            
            # Execute step operation (placeholder implementation)
            step_result = await self._execute_module_operation(step, step_results, input_data)
            
            if step_result["success"]:
                workflow_step.complete(step_result["data"])
                result = {"status": "completed", "data": step_result["data"]}
            else:
                workflow_step.fail(step_result["error"])
                result = {"status": "failed", "error": step_result["error"]}
            
            # Update module usage statistics
            self._update_module_usage_stats(step["module_name"], result["status"] == "completed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing workflow step {step_id}: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _execute_module_operation(
        self,
        step: Dict[str, Any],
        step_results: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a module operation for a workflow step."""
        # This is a placeholder implementation
        # In a real system, this would:
        # 1. Connect to the specified module
        # 2. Execute the operation with parameters
        # 3. Handle the response and errors
        
        try:
            module_name = step["module_name"]
            operation = step["operation"]
            parameters = step["parameters"]
            
            logger.debug(f"Executing {operation} on module {module_name}")
            
            # Simulate operation execution
            import random
            import time
            
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.1, 2.0))
            
            # Simulate success/failure
            success = random.random() > 0.1  # 90% success rate
            
            if success:
                # Generate mock result data
                result_data = {
                    "module": module_name,
                    "operation": operation,
                    "parameters": parameters,
                    "step_id": step["step_id"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "execution_time_ms": random.uniform(100, 2000)
                }
                
                # Add step-specific result data
                if operation == "process_aasx_file":
                    result_data["file_processed"] = True
                    result_data["data_extracted"] = True
                elif operation == "analyze_carbon_footprint":
                    result_data["analysis_completed"] = True
                    result_data["carbon_footprint_score"] = random.uniform(0.1, 0.9)
                elif operation == "create_digital_twin":
                    result_data["twin_created"] = True
                    result_data["twin_id"] = str(uuid4())
                
                return {"success": True, "data": result_data}
            else:
                return {"success": False, "error": f"Simulated failure in {operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_module_usage_stats(self, module_name: str, success: bool):
        """Update module usage statistics."""
        if module_name not in self.module_usage_stats:
            self.module_usage_stats[module_name] = {"total_executions": 0, "successful_executions": 0, "failed_executions": 0}
        
        stats = self.module_usage_stats[module_name]
        stats["total_executions"] += 1
        
        if success:
            stats["successful_executions"] += 1
        else:
            stats["failed_executions"] += 1
    
    def get_workflow_templates(self) -> Dict[str, Dict]:
        """Get available workflow templates."""
        return self.workflow_templates.copy()
    
    def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow definition by ID."""
        return self.workflow_definitions.get(workflow_id)
    
    def get_active_workflows(self) -> Dict[UUID, WorkflowResult]:
        """Get all currently active workflows."""
        return self.active_workflows.copy()
    
    def get_workflow_history(self, limit: int = 100) -> List[WorkflowResult]:
        """Get workflow history with optional limit."""
        return self.workflow_history[-limit:] if self.workflow_history else []
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator service status."""
        return {
            "active_workflows": len(self.active_workflows),
            "total_workflows": len(self.workflow_history),
            "max_concurrent_workflows": self.max_concurrent_workflows,
            "available_templates": len(self.workflow_templates),
            "module_usage_stats": dict(self.module_usage_stats)
        }
    
    def get_workflow_metrics(self, limit: int = 100) -> Dict[str, List[Dict]]:
        """Get workflow performance metrics."""
        return {key: metrics[-limit:] if metrics else [] for key, metrics in self.workflow_metrics.items()}
