"""
Project Service - Business Domain Service
========================================

Manages projects, their lifecycle, tasks, resources, and project-related operations.
This service provides comprehensive project management capabilities.

Features:
- Project creation and lifecycle management
- Task and milestone management
- Resource allocation and tracking
- Project status and progress monitoring
- Project templates and workflows
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..base import BaseService
from ...models.base_model import BaseModel
from ...repositories.base_repository import BaseRepository
from ...models.enums import EventType, SystemCategory, SecurityLevel

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Project status values."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProjectPriority(Enum):
    """Project priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task status values."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass
class ProjectInfo:
    """Project information structure."""
    project_id: str
    name: str
    description: str
    status: ProjectStatus
    priority: ProjectPriority
    org_id: str
    owner_id: str
    dept_id: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[float]
    actual_cost: Optional[float]
    progress_percentage: float
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class TaskInfo:
    """Task information structure."""
    task_id: str
    project_id: str
    name: str
    description: str
    status: TaskStatus
    priority: ProjectPriority
    assignee_id: Optional[str]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    due_date: Optional[datetime]
    completed_date: Optional[datetime]
    dependencies: List[str]
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class MilestoneInfo:
    """Milestone information structure."""
    milestone_id: str
    project_id: str
    name: str
    description: str
    due_date: datetime
    completed_date: Optional[datetime]
    is_critical: bool
    dependencies: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ProjectService(BaseService[BaseModel, BaseRepository]):
    """
    Business domain service for project management.
    
    Provides:
    - Project CRUD operations
    - Task and milestone management
    - Project lifecycle management
    - Resource allocation and tracking
    - Progress monitoring and reporting
    """

    def __init__(self, repository: Optional[BaseRepository] = None):
        super().__init__(repository, "ProjectService")
        
        # Project storage
        self._projects: Dict[str, ProjectInfo] = {}
        self._tasks: Dict[str, TaskInfo] = {}
        self._milestones: Dict[str, MilestoneInfo] = {}
        
        # Project relationships
        self._project_tasks: Dict[str, Set[str]] = {}  # project -> tasks
        self._project_milestones: Dict[str, Set[str]] = {}  # project -> milestones
        self._task_dependencies: Dict[str, Set[str]] = {}  # task -> dependencies
        
        # Validation rules
        self._validation_rules = {
            'max_project_duration_days': 365 * 5,  # 5 years
            'max_tasks_per_project': 1000,
            'max_milestones_per_project': 100,
            'min_progress_percentage': 0.0,
            'max_progress_percentage': 100.0
        }
        
        logger.info("Project service initialized")

    async def _initialize_service_resources(self) -> None:
        """Initialize project service resources."""
        # Load existing projects from repository
        await self._load_projects()
        
        # Build relationship indexes
        await self._build_relationship_indexes()
        
        logger.info("Project service resources initialized")

    async def _cleanup_service_resources(self) -> None:
        """Cleanup project service resources."""
        # Save projects to repository
        await self._save_projects()
        
        # Clear in-memory data
        self._projects.clear()
        self._tasks.clear()
        self._milestones.clear()
        self._project_tasks.clear()
        self._project_milestones.clear()
        self._task_dependencies.clear()
        
        logger.info("Project service resources cleaned up")

    async def get_service_info(self) -> Dict[str, Any]:
        """Get project service information."""
        return {
            'service_name': self.service_name,
            'total_projects': len(self._projects),
            'total_tasks': len(self._tasks),
            'total_milestones': len(self._milestones),
            'project_statuses': [s.value for s in ProjectStatus],
            'task_statuses': [s.value for s in TaskStatus],
            'health_status': self.health_status,
            'uptime': str(self.get_uptime()),
            'last_health_check': self.last_health_check.isoformat()
        }

    # Project Management

    async def create_project(self, name: str, description: str, org_id: str, owner_id: str,
                           status: ProjectStatus = ProjectStatus.PLANNING,
                           priority: ProjectPriority = ProjectPriority.MEDIUM,
                           start_date: datetime = None, end_date: datetime = None,
                           budget: float = None, dept_id: str = None, **kwargs) -> Optional[str]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            org_id: Organization ID
            owner_id: Project owner ID
            status: Project status
            priority: Project priority
            start_date: Project start date
            end_date: Project end date
            budget: Project budget
            **kwargs: Additional project properties
            
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            # Validate project data
            if not await self._validate_project_data(name, org_id, start_date, end_date):
                return None
            
            # Generate project ID
            project_id = f"proj_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create project info
            project_info = ProjectInfo(
                project_id=project_id,
                name=name,
                description=description,
                status=status,
                priority=priority,
                org_id=org_id,
                owner_id=owner_id,
                dept_id=dept_id,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                actual_cost=0.0,
                progress_percentage=0.0,
                tags=kwargs.get('tags', []),
                metadata=kwargs.get('metadata', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store project
            self._projects[project_id] = project_info
            
            # Initialize project collections
            self._project_tasks[project_id] = set()
            self._project_milestones[project_id] = set()
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_CREATED,
                SystemCategory.APPLICATION,
                f"Project created: {name}",
                {'project_id': project_id, 'org_id': org_id, 'owner_id': owner_id},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Project created: {project_id} ({name})")
            return project_id
            
        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}")
            return None

    async def get_project(self, project_id: str) -> Optional[ProjectInfo]:
        """Get project by ID."""
        try:
            return self._projects.get(project_id)
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            return None

    async def update_project(self, project_id: str, **kwargs) -> bool:
        """Update project information."""
        try:
            if project_id not in self._projects:
                logger.warning(f"Project {project_id} not found")
                return False
            
            project_info = self._projects[project_id]
            
            # Update allowed fields
            allowed_fields = {
                'name', 'description', 'status', 'priority', 'start_date', 'end_date',
                'budget', 'actual_cost', 'progress_percentage', 'tags', 'metadata'
            }
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(project_info, field):
                    setattr(project_info, field, value)
            
            project_info.updated_at = datetime.now()
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_UPDATED,
                SystemCategory.APPLICATION,
                f"Project updated: {project_id}",
                {'project_id': project_id, 'updated_fields': list(kwargs.keys())},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Project updated: {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            return False

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        try:
            if project_id not in self._projects:
                logger.warning(f"Project {project_id} not found")
                return False
            
            # Check if project has tasks
            if project_id in self._project_tasks and self._project_tasks[project_id]:
                logger.warning(f"Cannot delete project {project_id} with tasks")
                return False
            
            # Check if project has milestones
            if project_id in self._project_milestones and self._project_milestones[project_id]:
                logger.warning(f"Cannot delete project {project_id} with milestones")
                return False
            
            # Delete project
            del self._projects[project_id]
            
            # Clean up collections
            if project_id in self._project_tasks:
                del self._project_tasks[project_id]
            if project_id in self._project_milestones:
                del self._project_milestones[project_id]
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_DELETED,
                SystemCategory.APPLICATION,
                f"Project deleted: {project_id}",
                {'project_id': project_id},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Project deleted: {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            return False

    # Task Management

    async def create_task(self, project_id: str, name: str, description: str,
                         status: TaskStatus = TaskStatus.TODO,
                         priority: ProjectPriority = ProjectPriority.MEDIUM,
                         assignee_id: str = None, estimated_hours: float = None,
                         due_date: datetime = None, dependencies: List[str] = None,
                         **kwargs) -> Optional[str]:
        """
        Create a new task.
        
        Args:
            project_id: Parent project ID
            name: Task name
            description: Task description
            status: Task status
            priority: Task priority
            assignee_id: Assigned user ID
            estimated_hours: Estimated hours to complete
            due_date: Task due date
            dependencies: List of dependent task IDs
            **kwargs: Additional task properties
            
        Returns:
            Task ID if successful, None otherwise
        """
        try:
            # Validate task data
            if not await self._validate_task_data(project_id, name, dependencies):
                return None
            
            # Generate task ID
            task_id = f"task_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create task info
            task_info = TaskInfo(
                task_id=task_id,
                project_id=project_id,
                name=name,
                description=description,
                status=status,
                priority=priority,
                assignee_id=assignee_id,
                estimated_hours=estimated_hours,
                actual_hours=0.0,
                due_date=due_date,
                completed_date=None,
                dependencies=dependencies or [],
                tags=kwargs.get('tags', []),
                metadata=kwargs.get('metadata', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store task
            self._tasks[task_id] = task_info
            
            # Add to project tasks
            if project_id not in self._project_tasks:
                self._project_tasks[project_id] = set()
            self._project_tasks[project_id].add(task_id)
            
            # Update task dependencies
            self._task_dependencies[task_id] = set(dependencies or [])
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_CREATED,
                SystemCategory.APPLICATION,
                f"Task created: {name}",
                {'task_id': task_id, 'project_id': project_id, 'assignee_id': assignee_id},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Task created: {task_id} ({name})")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create task {name}: {e}")
            return None

    async def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task by ID."""
        try:
            return self._tasks.get(task_id)
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None

    async def get_project_tasks(self, project_id: str) -> List[TaskInfo]:
        """Get all tasks for a project."""
        try:
            if project_id not in self._project_tasks:
                return []
            
            return [self._tasks[task_id] for task_id in self._project_tasks[project_id] 
                   if task_id in self._tasks]
        except Exception as e:
            logger.error(f"Failed to get tasks for project {project_id}: {e}")
            return []

    async def update_task_status(self, task_id: str, status: TaskStatus, 
                                actual_hours: float = None) -> bool:
        """Update task status and progress."""
        try:
            if task_id not in self._tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task_info = self._tasks[task_id]
            old_status = task_info.status
            task_info.status = status
            task_info.updated_at = datetime.now()
            
            # Update actual hours if provided
            if actual_hours is not None:
                task_info.actual_hours = actual_hours
            
            # Set completion date if task is done
            if status == TaskStatus.DONE and task_info.completed_date is None:
                task_info.completed_date = datetime.now()
            
            # Update project progress
            await self._update_project_progress(task_info.project_id)
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_UPDATED,
                SystemCategory.APPLICATION,
                f"Task status updated: {task_id}",
                {'task_id': task_id, 'old_status': old_status.value, 'new_status': status.value},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Task status updated: {task_id} -> {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task status {task_id}: {e}")
            return False

    # Milestone Management

    async def create_milestone(self, project_id: str, name: str, description: str,
                             due_date: datetime, is_critical: bool = False,
                             dependencies: List[str] = None, **kwargs) -> Optional[str]:
        """
        Create a new milestone.
        
        Args:
            project_id: Parent project ID
            name: Milestone name
            description: Milestone description
            due_date: Milestone due date
            is_critical: Whether this is a critical milestone
            dependencies: List of dependent milestone IDs
            **kwargs: Additional milestone properties
            
        Returns:
            Milestone ID if successful, None otherwise
        """
        try:
            # Validate milestone data
            if not await self._validate_milestone_data(project_id, name, due_date):
                return None
            
            # Generate milestone ID
            milestone_id = f"milestone_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create milestone info
            milestone_info = MilestoneInfo(
                milestone_id=milestone_id,
                project_id=project_id,
                name=name,
                description=description,
                due_date=due_date,
                completed_date=None,
                is_critical=is_critical,
                dependencies=dependencies or [],
                metadata=kwargs.get('metadata', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store milestone
            self._milestones[milestone_id] = milestone_info
            
            # Add to project milestones
            if project_id not in self._project_milestones:
                self._project_milestones[project_id] = set()
            self._project_milestones[project_id].add(milestone_id)
            
            # Log audit event
            await self.log_audit_event(
                EventType.PROJECT_CREATED,
                SystemCategory.APPLICATION,
                f"Milestone created: {name}",
                {'milestone_id': milestone_id, 'project_id': project_id, 'due_date': due_date.isoformat()},
                SecurityLevel.INTERNAL
            )
            
            logger.info(f"Milestone created: {milestone_id} ({name})")
            return milestone_id
            
        except Exception as e:
            logger.error(f"Failed to create milestone {name}: {e}")
            return None

    async def get_milestone(self, milestone_id: str) -> Optional[MilestoneInfo]:
        """Get milestone by ID."""
        try:
            return self._milestones.get(milestone_id)
        except Exception as e:
            logger.error(f"Failed to get milestone {milestone_id}: {e}")
            return None

    async def get_project_milestones(self, project_id: str) -> List[MilestoneInfo]:
        """Get all milestones for a project."""
        try:
            if project_id not in self._project_milestones:
                return []
            
            return [self._milestones[milestone_id] for milestone_id in self._project_milestones[project_id] 
                   if milestone_id in self._milestones]
        except Exception as e:
            logger.error(f"Failed to get milestones for project {project_id}: {e}")
            return []

    # Progress Tracking

    async def _update_project_progress(self, project_id: str) -> None:
        """Update project progress based on task completion."""
        try:
            if project_id not in self._project_tasks:
                return
            
            project_tasks = [self._tasks[task_id] for task_id in self._project_tasks[project_id] 
                           if task_id in self._tasks]
            
            if not project_tasks:
                return
            
            # Calculate progress based on completed tasks
            completed_tasks = [t for t in project_tasks if t.status == TaskStatus.DONE]
            progress_percentage = (len(completed_tasks) / len(project_tasks)) * 100
            
            # Update project progress
            if project_id in self._projects:
                self._projects[project_id].progress_percentage = min(progress_percentage, 100.0)
                self._projects[project_id].updated_at = datetime.now()
                
                logger.debug(f"Project {project_id} progress updated to {progress_percentage:.1f}%")
                
        except Exception as e:
            logger.error(f"Failed to update project progress for {project_id}: {e}")

    # Validation Methods

    async def _validate_project_data(self, name: str, org_id: str,
                                   start_date: datetime = None, end_date: datetime = None) -> bool:
        """Validate project data before creation."""
        try:
            # Check name uniqueness within organization
            for project in self._projects.values():
                if project.org_id == org_id and project.name.lower() == name.lower():
                    logger.warning(f"Project name '{name}' already exists in organization {org_id}")
                    return False
            
            # Check date validity
            if start_date and end_date and start_date >= end_date:
                logger.warning("Project start date must be before end date")
                return False
            
            # Check project duration
            if start_date and end_date:
                duration = (end_date - start_date).days
                if duration > self._validation_rules['max_project_duration_days']:
                    logger.warning(f"Project duration {duration} days exceeds maximum allowed")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Project validation error: {e}")
            return False

    async def _validate_task_data(self, project_id: str, name: str,
                                dependencies: List[str] = None) -> bool:
        """Validate task data before creation."""
        try:
            # Check project exists
            if project_id not in self._projects:
                logger.warning(f"Project {project_id} not found")
                return False
            
            # Check name uniqueness within project
            project_tasks = [self._tasks[task_id] for task_id in self._project_tasks.get(project_id, set())
                           if task_id in self._tasks]
            for task in project_tasks:
                if task.name.lower() == name.lower():
                    logger.warning(f"Task name '{name}' already exists in project {project_id}")
                    return False
            
            # Check dependencies exist and belong to same project
            if dependencies:
                for dep_id in dependencies:
                    if dep_id not in self._tasks:
                        logger.warning(f"Dependency task {dep_id} not found")
                        return False
                    
                    dep_task = self._tasks[dep_id]
                    if dep_task.project_id != project_id:
                        logger.warning(f"Dependency task {dep_id} does not belong to project {project_id}")
                        return False
            
            # Check task limit per project
            if len(project_tasks) >= self._validation_rules['max_tasks_per_project']:
                logger.warning(f"Maximum tasks per project exceeded for {project_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Task validation error: {e}")
            return False

    async def _validate_milestone_data(self, project_id: str, name: str,
                                     due_date: datetime) -> bool:
        """Validate milestone data before creation."""
        try:
            # Check project exists
            if project_id not in self._projects:
                logger.warning(f"Project {project_id} not found")
                return False
            
            # Check name uniqueness within project
            project_milestones = [self._milestones[milestone_id] for milestone_id in self._project_milestones.get(project_id, set())
                                if milestone_id in self._milestones]
            for milestone in project_milestones:
                if milestone.name.lower() == name.lower():
                    logger.warning(f"Milestone name '{name}' already exists in project {project_id}")
                    return False
            
            # Check due date is in the future
            if due_date <= datetime.now():
                logger.warning("Milestone due date must be in the future")
                return False
            
            # Check milestone limit per project
            if len(project_milestones) >= self._validation_rules['max_milestones_per_project']:
                logger.warning(f"Maximum milestones per project exceeded for {project_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Milestone validation error: {e}")
            return False

    # Data Loading and Saving

    async def _load_projects(self) -> None:
        """Load projects from repository."""
        try:
            # This would typically load from a database or file
            logger.info("Loading projects from repository")
            
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")

    async def _save_projects(self) -> None:
        """Save projects to repository."""
        try:
            # This would typically save to a database or file
            logger.info("Saving projects to repository")
            
        except Exception as e:
            logger.error(f"Failed to save projects: {e}")

    async def _build_relationship_indexes(self) -> None:
        """Build relationship indexes from loaded data."""
        try:
            # Build project-task relationships
            for task_id, task_info in self._tasks.items():
                project_id = task_info.project_id
                if project_id not in self._project_tasks:
                    self._project_tasks[project_id] = set()
                self._project_tasks[project_id].add(task_id)
            
            # Build project-milestone relationships
            for milestone_id, milestone_info in self._milestones.items():
                project_id = milestone_info.project_id
                if project_id not in self._project_milestones:
                    self._project_milestones[project_id] = set()
                self._project_milestones[project_id].add(milestone_id)
            
            # Build task dependencies
            for task_id, task_info in self._tasks.items():
                self._task_dependencies[task_id] = set(task_info.dependencies)
            
            logger.info("Relationship indexes built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build relationship indexes: {e}")

    # Business Intelligence

    async def get_project_statistics(self) -> Dict[str, Any]:
        """Get comprehensive project statistics."""
        try:
            stats = {
                'total_projects': len(self._projects),
                'total_tasks': len(self._tasks),
                'total_milestones': len(self._milestones),
                'project_status_distribution': {},
                'task_status_distribution': {},
                'priority_distribution': {},
                'progress_distribution': {},
                'overdue_items': {}
            }
            
            # Count by project status
            for project in self._projects.values():
                status = project.status.value
                stats['project_status_distribution'][status] = stats['project_status_distribution'].get(status, 0) + 1
            
            # Count by task status
            for task in self._tasks.values():
                status = task.status.value
                stats['task_status_distribution'][status] = stats['task_status_distribution'].get(status, 0) + 1
            
            # Count by priority
            for project in self._projects.values():
                priority = project.priority.value
                stats['priority_distribution'][priority] = stats['priority_distribution'].get(priority, 0) + 1
            
            # Progress distribution
            progress_ranges = [(0, 25), (25, 50), (50, 75), (75, 100)]
            for project in self._projects.values():
                for start, end in progress_ranges:
                    if start <= project.progress_percentage < end:
                        range_key = f"{start}-{end}%"
                        stats['progress_distribution'][range_key] = stats['progress_distribution'].get(range_key, 0) + 1
                        break
            
            # Overdue items
            now = datetime.now()
            overdue_tasks = [t for t in self._tasks.values() 
                           if t.due_date and t.due_date < now and t.status != TaskStatus.DONE]
            overdue_milestones = [m for m in self._milestones.values() 
                                if m.due_date < now and m.completed_date is None]
            
            stats['overdue_items'] = {
                'tasks': len(overdue_tasks),
                'milestones': len(overdue_milestones)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get project statistics: {e}")
            return {'error': str(e)}
