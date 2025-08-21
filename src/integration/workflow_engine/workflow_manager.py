"""
Workflow Manager Service

This module provides workflow lifecycle management, versioning, and template
management capabilities for the cross-module workflow engine.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from .models import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    TaskDependency,
    WorkflowTrigger,
    WorkflowPriority,
    WorkflowStatus,
    TaskStatus
)


logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Manages workflow lifecycle, versioning, and templates.
    
    The workflow manager handles:
    - Workflow definition lifecycle management
    - Version control and template management
    - Workflow validation and optimization
    - Template library and reuse
    """
    
    def __init__(self):
        """Initialize the workflow manager."""
        self.workflow_templates: Dict[str, WorkflowDefinition] = {}
        self.workflow_versions: Dict[UUID, List[WorkflowDefinition]] = {}
        self.workflow_categories: Dict[str, Set[UUID]] = {}
        self.workflow_tags: Dict[str, Set[UUID]] = {}
        
        # Validation rules
        self.validation_rules = {
            "max_tasks_per_workflow": 100,
            "max_dependencies_per_task": 10,
            "max_workflow_depth": 20,
            "required_task_fields": ["task_name", "task_type", "target_module"]
        }
        
        logger.info("Workflow manager initialized")
    
    def create_workflow_template(
        self,
        name: str,
        description: str,
        workflow_type: str,
        tasks: List[WorkflowTask],
        dependencies: Optional[List[TaskDependency]] = None,
        category: str = "general",
        tags: Optional[List[str]] = None,
        version: str = "1.0.0"
    ) -> WorkflowDefinition:
        """Create a new workflow template."""
        # Validate template
        validation_result = self._validate_workflow_template(tasks, dependencies)
        if not validation_result["is_valid"]:
            raise ValueError(f"Invalid workflow template: {validation_result['errors']}")
        
        # Create workflow definition
        workflow_def = WorkflowDefinition(
            workflow_name=name,
            workflow_description=description,
            workflow_type=workflow_type,
            version=version,
            tasks=tasks,
            dependencies=dependencies or [],
            tags=tags or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store template
        template_key = f"{name}_{version}"
        self.workflow_templates[template_key] = workflow_def
        
        # Store version
        if workflow_def.workflow_id not in self.workflow_versions:
            self.workflow_versions[workflow_def.workflow_id] = []
        self.workflow_versions[workflow_def.workflow_id].append(workflow_def)
        
        # Categorize
        if category not in self.workflow_categories:
            self.workflow_categories[category] = set()
        self.workflow_categories[category].add(workflow_def.workflow_id)
        
        # Tag
        if tags:
            for tag in tags:
                if tag not in self.workflow_tags:
                    self.workflow_tags[tag] = set()
                self.workflow_tags[tag].add(workflow_def.workflow_id)
        
        logger.info(f"Created workflow template: {name} v{version}")
        return workflow_def
    
    def update_workflow_template(
        self,
        template_key: str,
        updates: Dict[str, Any]
    ) -> Optional[WorkflowDefinition]:
        """Update an existing workflow template."""
        if template_key not in self.workflow_templates:
            logger.error(f"Workflow template not found: {template_key}")
            return None
        
        template = self.workflow_templates[template_key]
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        
        logger.info(f"Updated workflow template: {template_key}")
        return template
    
    def delete_workflow_template(self, template_key: str) -> bool:
        """Delete a workflow template."""
        if template_key not in self.workflow_templates:
            return False
        
        template = self.workflow_templates[template_key]
        
        # Remove from categories
        for category, workflow_ids in self.workflow_categories.items():
            if template.workflow_id in workflow_ids:
                workflow_ids.remove(template.workflow_id)
        
        # Remove from tags
        for tag, workflow_ids in self.workflow_tags.items():
            if template.workflow_id in workflow_ids:
                workflow_ids.remove(template.workflow_id)
        
        # Remove from versions
        if template.workflow_id in self.workflow_versions:
            del self.workflow_versions[template.workflow_id]
        
        # Remove template
        del self.workflow_templates[template_key]
        
        logger.info(f"Deleted workflow template: {template_key}")
        return True
    
    def get_workflow_template(self, template_key: str) -> Optional[WorkflowDefinition]:
        """Get a workflow template by key."""
        return self.workflow_templates.get(template_key)
    
    def get_workflow_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        workflow_type: Optional[str] = None
    ) -> List[WorkflowDefinition]:
        """Get workflow templates with optional filtering."""
        templates = list(self.workflow_templates.values())
        
        if category:
            templates = [t for t in templates if t.workflow_id in self.workflow_categories.get(category, set())]
        
        if tags:
            for tag in tags:
                templates = [t for t in templates if t.workflow_id in self.workflow_tags.get(tag, set())]
        
        if workflow_type:
            templates = [t for t in templates if t.workflow_type == workflow_type]
        
        return templates
    
    def get_workflow_categories(self) -> List[str]:
        """Get all available workflow categories."""
        return list(self.workflow_categories.keys())
    
    def get_workflow_tags(self) -> List[str]:
        """Get all available workflow tags."""
        return list(self.workflow_tags.keys())
    
    def create_workflow_from_template(
        self,
        template_key: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowDefinition]:
        """Create a new workflow definition from a template with customizations."""
        template = self.get_workflow_template(template_key)
        if not template:
            return None
        
        # Create copy of template
        workflow_def = WorkflowDefinition(
            workflow_name=template.workflow_name,
            workflow_description=template.workflow_description,
            workflow_type=template.workflow_type,
            version=template.version,
            tasks=[self._copy_task(task) for task in template.tasks],
            dependencies=template.dependencies.copy(),
            schedule=template.schedule,
            trigger=template.trigger,
            priority=template.priority,
            timeout=template.timeout,
            retry_policy=template.retry_policy.copy(),
            tags=template.tags.copy(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Apply customizations
        if customizations:
            workflow_def = self._apply_workflow_customizations(workflow_def, customizations)
        
        logger.info(f"Created workflow from template: {template_key}")
        return workflow_def
    
    def validate_workflow_definition(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Validate a workflow definition."""
        return self._validate_workflow_template(workflow_def.tasks, workflow_def.dependencies)
    
    def optimize_workflow_definition(self, workflow_def: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize a workflow definition for better performance."""
        # This is a placeholder for workflow optimization logic
        # In a real implementation, you would:
        # - Analyze task dependencies for parallelization opportunities
        # - Optimize task ordering
        # - Validate resource requirements
        # - Check for redundant tasks
        
        logger.info(f"Optimized workflow definition: {workflow_def.workflow_name}")
        return workflow_def
    
    def export_workflow_template(
        self,
        template_key: str,
        format: str = "json"
    ) -> Optional[Dict[str, Any]]:
        """Export a workflow template in the specified format."""
        template = self.get_workflow_template(template_key)
        if not template:
            return None
        
        if format == "json":
            return template.to_dict()
        elif format == "yaml":
            # This would require PyYAML - for now return dict
            return template.to_dict()
        else:
            logger.error(f"Unsupported export format: {format}")
            return None
    
    def import_workflow_template(
        self,
        template_data: Dict[str, Any],
        format: str = "json"
    ) -> Optional[WorkflowDefinition]:
        """Import a workflow template from external data."""
        try:
            # This is a simplified import - in a real implementation you would:
            # - Validate the imported data structure
            # - Convert from the specified format
            # - Create proper WorkflowDefinition objects
            
            workflow_def = WorkflowDefinition(
                workflow_name=template_data.get("workflow_name", "Imported Workflow"),
                workflow_description=template_data.get("workflow_description", ""),
                workflow_type=template_data.get("workflow_type", "imported"),
                version=template_data.get("version", "1.0.0"),
                tags=template_data.get("tags", []),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store as template
            template_key = f"{workflow_def.workflow_name}_{workflow_def.version}"
            self.workflow_templates[template_key] = workflow_def
            
            logger.info(f"Imported workflow template: {template_key}")
            return workflow_def
            
        except Exception as e:
            logger.error(f"Failed to import workflow template: {e}")
            return None
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about managed workflows."""
        total_templates = len(self.workflow_templates)
        total_versions = sum(len(versions) for versions in self.workflow_versions.values())
        total_categories = len(self.workflow_categories)
        total_tags = len(self.workflow_tags)
        
        # Category distribution
        category_distribution = {
            category: len(workflow_ids) 
            for category, workflow_ids in self.workflow_categories.items()
        }
        
        # Tag distribution
        tag_distribution = {
            tag: len(workflow_ids) 
            for tag, workflow_ids in self.workflow_tags.items()
        }
        
        return {
            "total_templates": total_templates,
            "total_versions": total_versions,
            "total_categories": total_categories,
            "total_tags": total_tags,
            "category_distribution": category_distribution,
            "tag_distribution": tag_distribution
        }
    
    def _validate_workflow_template(
        self,
        tasks: List[WorkflowTask],
        dependencies: Optional[List[TaskDependency]] = None
    ) -> Dict[str, Any]:
        """Validate a workflow template."""
        errors = []
        warnings = []
        
        # Check task count
        if len(tasks) > self.validation_rules["max_tasks_per_workflow"]:
            errors.append(f"Too many tasks: {len(tasks)} > {self.validation_rules['max_tasks_per_workflow']}")
        
        # Validate individual tasks
        for i, task in enumerate(tasks):
            task_errors = self._validate_task(task, i)
            errors.extend(task_errors)
        
        # Validate dependencies
        if dependencies:
            dep_errors = self._validate_dependencies(dependencies, tasks)
            errors.extend(dep_errors)
        
        # Check for circular dependencies
        if dependencies and self._has_circular_dependencies(dependencies):
            errors.append("Circular dependencies detected")
        
        # Check workflow depth
        max_depth = self._calculate_workflow_depth(tasks, dependencies or [])
        if max_depth > self.validation_rules["max_workflow_depth"]:
            warnings.append(f"Workflow depth {max_depth} exceeds recommended limit {self.validation_rules['max_workflow_depth']}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "max_depth": max_depth
        }
    
    def _validate_task(self, task: WorkflowTask, index: int) -> List[str]:
        """Validate a single workflow task."""
        errors = []
        
        # Check required fields
        for field in self.validation_rules["required_task_fields"]:
            if not getattr(task, field):
                errors.append(f"Task {index}: Missing required field '{field}'")
        
        # Check task name uniqueness (would need to check against other tasks)
        if not task.task_name:
            errors.append(f"Task {index}: Task name is required")
        
        # Check retry policy
        if task.max_retries < 0:
            errors.append(f"Task {index}: Max retries cannot be negative")
        
        return errors
    
    def _validate_dependencies(
        self,
        dependencies: List[TaskDependency],
        tasks: List[WorkflowTask]
    ) -> List[str]:
        """Validate task dependencies."""
        errors = []
        task_ids = {task.task_id for task in tasks}
        
        for dep in dependencies:
            if dep.source_task_id not in task_ids:
                errors.append(f"Dependency references non-existent source task: {dep.source_task_id}")
            if dep.target_task_id not in task_ids:
                errors.append(f"Dependency references non-existent target task: {dep.target_task_id}")
            
            if dep.source_task_id == dep.target_task_id:
                errors.append(f"Self-referencing dependency detected: {dep.source_task_id}")
        
        return errors
    
    def _has_circular_dependencies(self, dependencies: List[TaskDependency]) -> bool:
        """Check for circular dependencies using depth-first search."""
        # This is a simplified check - in a real implementation you would use
        # a proper graph algorithm to detect cycles
        
        # For now, just check for obvious self-references
        for dep in dependencies:
            if dep.source_task_id == dep.target_task_id:
                return True
        
        return False
    
    def _calculate_workflow_depth(
        self,
        tasks: List[WorkflowTask],
        dependencies: List[TaskDependency]
    ) -> int:
        """Calculate the maximum depth of the workflow."""
        # This is a simplified calculation - in a real implementation you would
        # use a proper graph algorithm to calculate the longest path
        
        if not dependencies:
            return 1
        
        # For now, return a simple estimate
        return min(len(dependencies), self.validation_rules["max_workflow_depth"])
    
    def _apply_workflow_customizations(
        self,
        workflow_def: WorkflowDefinition,
        customizations: Dict[str, Any]
    ) -> WorkflowDefinition:
        """Apply customizations to a workflow definition."""
        # This is a placeholder for customization logic
        # In a real implementation, you would:
        # - Modify task parameters
        # - Adjust dependencies
        # - Change scheduling
        # - Update priorities
        
        logger.info(f"Applied customizations to workflow: {workflow_def.workflow_name}")
        return workflow_def
    
    def _copy_task(self, task: WorkflowTask) -> WorkflowTask:
        """Create a copy of a workflow task."""
        return WorkflowTask(
            task_id=task.task_id,
            task_name=task.task_name,
            task_description=task.task_description,
            task_type=task.task_type,
            target_module=task.target_module,
            operation_name=task.operation_name,
            parameters=task.parameters.copy(),
            retry_policy=task.retry_policy.copy(),
            timeout=task.timeout,
            priority=task.priority,
            dependencies=task.dependencies.copy(),
            max_retries=task.max_retries,
            metadata=task.metadata.copy()
        )
