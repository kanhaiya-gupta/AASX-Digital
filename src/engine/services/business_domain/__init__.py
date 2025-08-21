"""
Business Domain Services Package
===============================

This package contains business domain services that implement core business logic
for the AAS Data Modeling Engine.

Services:
- OrganizationService: Manages organizational structures and hierarchies
- ProjectService: Manages projects, tasks, and milestones
- FileService: Manages files, documents, and file operations
- WorkflowService: Manages business workflows and process automation

Each service follows the modular architecture pattern and extends BaseService
for consistent behavior and integration.
"""

from .organization_service import (
    OrganizationService,
    OrganizationType,
    OrganizationStatus,
    OrganizationInfo,
    DepartmentInfo
)

from .project_service import (
    ProjectService,
    ProjectStatus,
    ProjectPriority,
    TaskStatus,
    ProjectInfo,
    TaskInfo,
    MilestoneInfo
)

from .file_service import (
    FileService,
    FileType,
    FileStatus,
    FilePermission,
    FileInfo,
    FileVersion,
    FileAccessLog
)

from .workflow_service import (
    WorkflowService,
    WorkflowStatus,
    TaskStatus as WorkflowTaskStatus,
    WorkflowTriggerType,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    WorkflowEvent
)

# Convenience functions for accessing services
_organization_service: OrganizationService = None
_project_service: ProjectService = None
_file_service: FileService = None
_workflow_service: WorkflowService = None

def get_organization_service() -> OrganizationService:
    """Get the global organization service instance."""
    global _organization_service
    if _organization_service is None:
        _organization_service = OrganizationService()
    return _organization_service

def get_project_service() -> ProjectService:
    """Get the global project service instance."""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service

def get_file_service() -> FileService:
    """Get the global file service instance."""
    global _file_service
    if _file_service is None:
        _file_service = FileService()
    return _file_service

def get_workflow_service() -> WorkflowService:
    """Get the global workflow service instance."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService()
    return _workflow_service

def set_organization_service(service: OrganizationService) -> None:
    """Set the global organization service instance."""
    global _organization_service
    _organization_service = service

def set_project_service(service: ProjectService) -> None:
    """Set the global project service instance."""
    global _project_service
    _project_service = service

def set_file_service(service: FileService) -> None:
    """Set the global file service instance."""
    global _file_service
    _file_service = service

def set_workflow_service(service: WorkflowService) -> None:
    """Set the global workflow service instance."""
    global _workflow_service
    _workflow_service = service

async def initialize_business_domain_services() -> None:
    """Initialize all business domain services."""
    try:
        # Initialize organization service
        org_service = get_organization_service()
        await org_service.start()
        
        # Initialize project service
        proj_service = get_project_service()
        await proj_service.start()
        
        # Initialize file service
        file_service = get_file_service()
        await file_service.start()
        
        # Initialize workflow service
        wf_service = get_workflow_service()
        await wf_service.start()
        
        print("🏢 Business Domain Services Initialized")
        print(f"   📊 Organization Service: {org_service.health_status}")
        print(f"   📋 Project Service: {proj_service.health_status}")
        print(f"   📁 File Service: {file_service.health_status}")
        print(f"   🔄 Workflow Service: {wf_service.health_status}")
        
    except Exception as e:
        print(f"❌ Failed to initialize business domain services: {e}")
        raise

async def get_business_domain_services_info() -> dict:
    """Get information about all business domain services."""
    try:
        services_info = {}
        
        # Organization service info
        org_service = get_organization_service()
        if org_service.is_active:
            services_info['organization'] = await org_service.get_service_info()
        
        # Project service info
        proj_service = get_project_service()
        if proj_service.is_active:
            services_info['project'] = await proj_service.get_service_info()
        
        # File service info
        file_service = get_file_service()
        if file_service.is_active:
            services_info['file'] = await file_service.get_service_info()
        
        # Workflow service info
        wf_service = get_workflow_service()
        if wf_service.is_active:
            services_info['workflow'] = await wf_service.get_service_info()
        
        return services_info
        
    except Exception as e:
        return {'error': str(e)}

async def stop_business_domain_services() -> None:
    """Stop all business domain services."""
    try:
        # Stop organization service
        org_service = get_organization_service()
        if org_service.is_active:
            await org_service.stop()
        
        # Stop project service
        proj_service = get_project_service()
        if proj_service.is_active:
            await proj_service.stop()
        
        # Stop file service
        file_service = get_file_service()
        if file_service.is_active:
            await file_service.stop()
        
        # Stop workflow service
        wf_service = get_workflow_service()
        if wf_service.is_active:
            await wf_service.stop()
        
        print("🏢 Business Domain Services Stopped")
        
    except Exception as e:
        print(f"❌ Failed to stop business domain services: {e}")

# Export all public components
__all__ = [
    # Services
    'OrganizationService',
    'ProjectService', 
    'FileService',
    'WorkflowService',
    
    # Data Models
    'OrganizationType',
    'OrganizationStatus',
    'OrganizationInfo',
    'DepartmentInfo',
    'ProjectStatus',
    'ProjectPriority',
    'TaskStatus',
    'ProjectInfo',
    'TaskInfo',
    'MilestoneInfo',
    'FileType',
    'FileStatus',
    'FilePermission',
    'FileInfo',
    'FileVersion',
    'FileAccessLog',
    'WorkflowStatus',
    'WorkflowTaskStatus',
    'WorkflowTriggerType',
    'WorkflowDefinition',
    'WorkflowInstance',
    'WorkflowTask',
    'WorkflowEvent',
    
    # Utility Functions
    'get_organization_service',
    'get_project_service',
    'get_file_service',
    'get_workflow_service',
    'set_organization_service',
    'set_project_service',
    'set_file_service',
    'set_workflow_service',
    'initialize_business_domain_services',
    'get_business_domain_services_info',
    'stop_business_domain_services'
]
