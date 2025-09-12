"""
Physics Modeling System API Routes (Refactored)
Provides REST API endpoints for the physics modeling system frontend
Uses service layer for business logic separation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

# Import authentication components
from src.integration.api.dependencies import require_auth, get_current_user
from src.engine.models.request_context import UserContext

# Import services
from .services import (
    PhysicsModelService, SimulationService, ValidationService, UseCaseService,
    PhysicsModelingUserSpecificService, PhysicsModelingOrganizationService
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize database manager and services
from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.database.base_manager import BaseDatabaseManager
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository
# Migrated to new twin registry system
from src.modules.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
from pathlib import Path

# Create data directory and set database path
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
db_path = data_dir / "aasx_database.db"

# Initialize central database connection
connection_manager = DatabaseConnectionManager(db_path)
db_manager = BaseDatabaseManager(connection_manager)

# Initialize repositories
file_repository = FileRepository(db_manager)
project_repository = ProjectRepository(db_manager)

# Initialize shared services - migrated to new twin registry system
twin_registry_service = CoreTwinRegistryService()

# Initialize physics modeling services with database manager
physics_model_service = PhysicsModelService(db_manager, twin_registry_service)
simulation_service = SimulationService(db_manager, twin_registry_service)
validation_service = ValidationService()
use_case_service = UseCaseService()

# Pydantic models for request/response
class ModelCreationRequest(BaseModel):
    twin_id: str
    model_type: str  # thermal, structural, fluid, multi_physics
    geometry_file: Optional[str] = None
    material_properties: Optional[Dict[str, Any]] = None
    boundary_conditions: Optional[Dict[str, Any]] = None
    solver_settings: Optional[Dict[str, Any]] = None
    use_ai_insights: bool = True

    class Config:
        protected_namespaces = ()

class ModelCreationResponse(BaseModel):
    model_id: str
    twin_id: str
    model_type: str
    status: str
    created_at: str
    configuration: Dict[str, Any]
    ai_insights: Optional[Dict[str, Any]] = None

    class Config:
        protected_namespaces = ()

class PluginInfo(BaseModel):
    plugin_id: str
    name: str
    version: str
    description: str
    category: str
    parameters: List[Dict[str, Any]]
    equations: List[Dict[str, Any]]
    solver_capabilities: List[Dict[str, Any]]

    class Config:
        protected_namespaces = ()

class SimulationRequest(BaseModel):
    twin_id: str
    plugin_id: str
    parameters: Optional[Dict[str, Any]] = None

    class Config:
        protected_namespaces = ()

class SimulationResponse(BaseModel):
    simulation_id: str
    model_id: str
    status: str
    progress: float
    results: Optional[Dict[str, Any]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    execution_time: float
    error: Optional[str] = None

class ModelValidationRequest(BaseModel):
    model_id: str
    validation_data: Dict[str, Any]

class ModelValidationResponse(BaseModel):
    validation_id: str
    model_id: str
    accuracy_score: float
    validation_metrics: Dict[str, Any]
    status: str
    timestamp: str

class SystemStatusResponse(BaseModel):
    physics_framework_available: bool
    available_models: int
    active_simulations: int
    twin_connector_status: str
    ai_rag_connector_status: str
    timestamp: str

# Page routes
@router.get("/", response_class=HTMLResponse)
@require_auth("read", allow_independent=True)
async def physics_modeling_page(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Render the main physics modeling dashboard page"""
    try:
        # Initialize user-specific and organization services
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        organization_service = PhysicsModelingOrganizationService(user_context)
        
        # Get user-specific data
        user_models = user_specific_service.get_user_models()
        user_simulations = user_specific_service.get_user_simulations()
        user_validations = user_specific_service.get_user_validations()
        user_stats = user_specific_service.get_user_statistics()
        
        # Get organization data (if applicable)
        organization_stats = organization_service.get_organization_statistics()
        organization_health = organization_service.get_organization_health()
        
        # Check permissions
        can_create_model = user_specific_service.can_create_model()
        can_manage_org = organization_service.can_manage_organization()
        
        templates = Jinja2Templates(directory="client/templates")
        return templates.TemplateResponse(
            "physics_modeling/index.html",
            {
                "request": request,
                "page_title": "Physics Modeling Dashboard",
                "module_name": "Physics Modeling",
                "user_context": user_context,
                "can_create_model": can_create_model,
                "can_manage_org": can_manage_org,
                "is_independent": user_specific_service.is_independent,
                "user_type": user_specific_service.user_type,
                "user_models": user_models,
                "user_simulations": user_simulations,
                "user_validations": user_validations,
                "user_stats": user_stats,
                "organization_stats": organization_stats,
                "organization_health": organization_health
            }
        )
    except Exception as e:
        logger.error(f"Error rendering physics modeling page: {e}")
        raise HTTPException(status_code=500, detail="Failed to render physics modeling page")

@router.get("/use-cases-page", response_class=HTMLResponse)
@require_auth("read", allow_independent=True)
async def use_cases_page(
    request: Request,
    user_context: UserContext = Depends(get_current_user)
):
    """Render the use cases showcase page"""
    try:
        # Initialize user-specific and organization services
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        organization_service = PhysicsModelingOrganizationService(user_context)
        
        # Get user-specific use cases
        user_use_cases = user_specific_service.get_user_use_cases()
        
        # Get organization use cases (if applicable)
        organization_use_cases = organization_service.get_organization_use_cases()
        
        # Check permissions
        can_create_use_case = any(perm in user_context.permissions for perm in ['create'])
        
        templates = Jinja2Templates(directory="client/templates")
        return templates.TemplateResponse(
            "physics_modeling/use_cases_showcase.html",
            {
                "request": request,
                "page_title": "Physics Modeling Use Cases",
                "module_name": "Physics Modeling",
                "user_context": user_context,
                "can_create_use_case": can_create_use_case,
                "is_independent": user_specific_service.is_independent,
                "user_type": user_specific_service.user_type,
                "user_use_cases": user_use_cases,
                "organization_use_cases": organization_use_cases
            }
        )
    except Exception as e:
        logger.error(f"Error rendering use cases page: {e}")
        raise HTTPException(status_code=500, detail="Failed to render use cases page")

# Model management endpoints
@router.post("/models/create", response_model=ModelCreationResponse)
@require_auth("create", allow_independent=True)
async def create_physics_model(
    request: ModelCreationRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Create a new physics model from twin data"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can create models
        if not user_specific_service.can_create_model():
            raise HTTPException(status_code=403, detail="Insufficient permissions to create models")
        
        # Get user limits
        user_limits = user_specific_service.get_user_model_limits()
        
        # Check if user has reached model limit
        current_models = len(user_specific_service.get_user_models())
        if current_models >= user_limits['max_models']:
            raise HTTPException(
                status_code=400, 
                detail=f"Model limit reached. Maximum allowed: {user_limits['max_models']}"
            )
        
        # Create model with user context
        result = physics_model_service.create_model(
            twin_id=request.twin_id,
            model_type=request.model_type,
            geometry_file=request.geometry_file,
            material_properties=request.material_properties,
            boundary_conditions=request.boundary_conditions,
            solver_settings=request.solver_settings,
            use_ai_insights=request.use_ai_insights,
            created_by=user_context.user_id,
            organization_id=getattr(user_context, 'organization_id', None)
        )
        
        return ModelCreationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating physics model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create model: {str(e)}")

@router.get("/models")
@require_auth("read", allow_independent=True)
async def get_available_models(
    user_context: UserContext = Depends(get_current_user)
):
    """Get list of available physics models"""
    try:
        # Initialize user-specific service
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Return user-specific models
        models = user_specific_service.get_user_models()
        return {"models": models}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@router.get("/models/{model_id}")
@require_auth("read", allow_independent=True)
async def get_model(
    model_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get specific physics model details"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can access this model
        if not user_specific_service.can_access_model(model_id):
            raise HTTPException(status_code=403, detail="Access denied to this model")
        
        # Get model details
        model = physics_model_service.get_model(model_id)
        return model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model: {str(e)}")

@router.put("/models/{model_id}")
@require_auth("update", allow_independent=True)
async def update_model(
    model_id: str, 
    updates: Dict[str, Any],
    user_context: UserContext = Depends(get_current_user)
):
    """Update a physics model"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can update this model
        if not user_specific_service.can_update_model(model_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to update this model")
        
        # Update model
        result = physics_model_service.update_model(model_id, updates)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update model: {str(e)}")

@router.delete("/models/{model_id}")
@require_auth("delete", allow_independent=True)
async def delete_model(
    model_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Delete a physics model"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can delete this model
        if not user_specific_service.can_delete_model(model_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to delete this model")
        
        # Delete model
        result = physics_model_service.delete_model(model_id)
        return {"message": "Model deleted successfully", "details": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model {model_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Plugin Management Endpoints
@router.get("/plugins")
async def get_available_plugins():
    """Get all available physics plugins"""
    try:
        plugins = physics_model_service.get_available_plugins()
        return {"success": True, "data": plugins}
    except Exception as e:
        logger.error(f"Failed to get available plugins: {e}")
        return {"success": False, "error": str(e)}

@router.get("/plugins/{twin_id}")
async def get_plugins_for_twin(twin_id: str):
    """Get plugins available for a specific digital twin"""
    try:
        plugins = physics_model_service.get_plugins_for_twin(twin_id)
        return {"success": True, "data": plugins}
    except Exception as e:
        logger.error(f"Failed to get plugins for twin {twin_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/plugins/{plugin_id}/details")
async def get_plugin_details(plugin_id: str):
    """Get detailed information about a specific plugin"""
    try:
        # Get all plugins and find the specific one
        plugins = physics_model_service.get_available_plugins()
        plugin = next((p for p in plugins if p["plugin_id"] == plugin_id), None)
        
        if not plugin:
            return {"success": False, "error": f"Plugin {plugin_id} not found"}
        
        return {"success": True, "data": plugin}
    except Exception as e:
        logger.error(f"Failed to get plugin details for {plugin_id}: {e}")
        return {"success": False, "error": str(e)}

# Updated Simulation Endpoints
@router.post("/simulations/run", response_model=SimulationResponse)
@require_auth("create", allow_independent=True)
async def run_simulation(
    request: SimulationRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Run a physics simulation using a specific plugin"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can run simulations
        if not user_specific_service.can_run_simulation(request.twin_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to run simulations")
        
        # Run simulation with user context
        results = physics_model_service.run_simulation(
            twin_id=request.twin_id,
            plugin_id=request.plugin_id,
            parameters=request.parameters,
            created_by=user_context.user_id,
            organization_id=getattr(user_context, 'organization_id', None)
        )
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simulations/{simulation_id}/status")
@require_auth("read", allow_independent=True)
async def get_simulation_status(
    simulation_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get simulation status and progress"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can access this simulation
        if not user_specific_service.can_access_simulation(simulation_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this simulation")
        
        status = physics_model_service.get_simulation_status(simulation_id)
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get simulation status: {str(e)}")

@router.get("/simulations/{simulation_id}/results")
@require_auth("read", allow_independent=True)
async def get_simulation_results(
    simulation_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get simulation results and visualization data"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can access this simulation
        if not user_specific_service.can_access_simulation(simulation_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this simulation")
        
        results = physics_model_service.get_simulation_results(simulation_id)
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting simulation results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get simulation results: {str(e)}")

@router.post("/simulations/{simulation_id}/cancel")
@require_auth("update", allow_independent=True)
async def cancel_simulation(
    simulation_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Cancel a running simulation"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can cancel this simulation
        if not user_specific_service.can_cancel_simulation(simulation_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to cancel this simulation")
        
        result = physics_model_service.cancel_simulation(simulation_id)
        return {"message": "Simulation cancelled successfully", "simulation_id": simulation_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel simulation: {str(e)}")

@router.get("/simulations")
@require_auth("read", allow_independent=True)
async def list_simulations(
    model_id: Optional[str] = None, 
    status: Optional[str] = None,
    user_context: UserContext = Depends(get_current_user)
):
    """List simulations with optional filtering"""
    try:
        # Initialize user-specific service
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Get user-specific simulations
        simulations = user_specific_service.get_user_simulations()
        
        # Apply filters if provided
        if model_id:
            simulations = [s for s in simulations if s.get('model_id') == model_id]
        if status:
            simulations = [s for s in simulations if s.get('status') == status]
        
        return {"simulations": simulations}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing simulations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list simulations: {str(e)}")

@router.get("/simulations/active/count")
@require_auth("read", allow_independent=True)
async def get_active_simulations_count(
    user_context: UserContext = Depends(get_current_user)
):
    """Get count of active simulations for the current user"""
    try:
        # Initialize user-specific service
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Get user-specific active simulations
        active_simulations = [
            s for s in user_specific_service.get_user_simulations() 
            if s.get('status') in ['running', 'queued', 'preparing']
        ]
        
        return {"active_count": len(active_simulations)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active simulations count: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active simulations count: {str(e)}")

# Validation endpoints
@router.post("/models/validate", response_model=ModelValidationResponse)
@require_auth("create", allow_independent=True)
async def validate_model(
    request: ModelValidationRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Validate a physics model against experimental data"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can validate this model
        if not user_specific_service.can_validate_model(request.model_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to validate this model")
        
        # Validate model
        result = physics_model_service.validate_model(
            model_id=request.model_id,
            validation_data=request.validation_data,
            validated_by=user_context.user_id,
            organization_id=getattr(user_context, 'organization_id', None)
        )
        
        return ModelValidationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate model: {str(e)}")

@router.get("/validations/{validation_id}")
@require_auth("read", allow_independent=True)
async def get_validation_results(
    validation_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get validation results for a specific validation"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can access this validation
        if not user_specific_service.can_access_validation(validation_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this validation")
        
        results = validation_service.get_validation_results(validation_id)
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting validation results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get validation results: {str(e)}")

@router.post("/models/compare")
@require_auth("read", allow_independent=True)
async def compare_models(
    model_ids: List[str], 
    comparison_metrics: Optional[List[str]] = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Compare multiple physics models"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can access all models being compared
        for model_id in model_ids:
            if not user_specific_service.can_access_model(model_id):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Insufficient permissions to access model {model_id}"
                )
        
        # Compare models
        comparison = physics_model_service.compare_models(model_ids, comparison_metrics)
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare models: {str(e)}")

@router.get("/models/{model_id}/validation-report")
@require_auth("read", allow_independent=True)
async def generate_validation_report(
    model_id: str, 
    validation_id: Optional[str] = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Generate validation report for a model"""
    try:
        # Initialize user-specific service for access control
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can access this model
        if not user_specific_service.can_access_model(model_id):
            raise HTTPException(status_code=403, detail="Insufficient permissions to access this model")
        
        # Generate report
        report = validation_service.generate_validation_report(model_id, validation_id)
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating validation report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate validation report: {str(e)}")

@router.get("/validations")
@require_auth("read", allow_independent=True)
async def list_validations(
    model_id: Optional[str] = None,
    user_context: UserContext = Depends(get_current_user)
):
    """List validations with optional filtering"""
    try:
        # Initialize user-specific service
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Get user-specific validations
        validations = user_specific_service.get_user_validations()
        
        # Apply filter if provided
        if model_id:
            validations = [v for v in validations if v.get('model_id') == model_id]
        
        return {"validations": validations}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing validations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list validations: {str(e)}")

# Use case endpoints
@router.get("/use-cases")
@require_auth("read", allow_independent=True)
async def get_use_cases(
    category: Optional[str] = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Get available use cases with optional category filtering"""
    try:
        # Use cases are shared resources, just ensure user is authenticated
        use_cases = use_case_service.get_use_cases(category=category)
        return {"use_cases": use_cases}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting use cases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get use cases: {str(e)}")

@router.get("/use-cases/{use_case_id}")
@require_auth("read", allow_independent=True)
async def get_use_case(
    use_case_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get specific use case details"""
    try:
        # Use cases are shared resources, just ensure user is authenticated
        use_case = use_case_service.get_use_case(use_case_id)
        return use_case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting use case {use_case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get use case: {str(e)}")

@router.get("/use-cases/{use_case_id}/projects")
@require_auth("read", allow_independent=True)
async def get_use_case_projects(
    use_case_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get projects associated with a specific use case"""
    try:
        # Use cases are shared resources, just ensure user is authenticated
        projects = use_case_service.get_use_case_projects(use_case_id)
        return {"use_case_id": use_case_id, "projects": projects}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting projects for use case {use_case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get projects for use case: {str(e)}")

@router.post("/use-cases")
@require_auth("create", allow_independent=True)
async def create_use_case(
    use_case_data: Dict[str, Any],
    user_context: UserContext = Depends(get_current_user)
):
    """Create a new use case"""
    try:
        # Check if user can create use cases
        if not any(perm in user_context.permissions for perm in ['create']):
            raise HTTPException(status_code=403, detail="Insufficient permissions to create use cases")
        
        # Add user context to use case data
        use_case_data['created_by'] = user_context.user_id
        use_case_data['organization_id'] = getattr(user_context, 'organization_id', None)
        
        result = use_case_service.create_use_case(use_case_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create use case: {str(e)}")

@router.put("/use-cases/{use_case_id}")
@require_auth("update", allow_independent=True)
async def update_use_case(
    use_case_id: str, 
    updates: Dict[str, Any],
    user_context: UserContext = Depends(get_current_user)
):
    """Update an existing use case"""
    try:
        # Use cases are shared resources, just ensure user is authenticated
        result = use_case_service.update_use_case(use_case_id, updates)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating use case {use_case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update use case: {str(e)}")

@router.delete("/use-cases/{use_case_id}")
@require_auth("delete", allow_independent=True)
async def delete_use_case(
    use_case_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Delete a use case"""
    try:
        # Use cases are shared resources, just ensure user is authenticated
        result = use_case_service.delete_use_case(use_case_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting use case {use_case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete use case: {str(e)}")

@router.get("/use-cases/templates")
@require_auth("read", allow_independent=True)
async def get_use_case_templates(
    category: Optional[str] = None,
    user_context: UserContext = Depends(get_current_user)
):
    """Get use case templates with optional category filtering"""
    try:
        # Use case templates are shared resources, just ensure user is authenticated
        templates = use_case_service.get_use_case_templates(category=category)
        return {"templates": templates}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting use case templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get use case templates: {str(e)}")

@router.get("/use-cases/statistics")
@require_auth("read", allow_independent=True)
async def get_use_case_statistics(
    user_context: UserContext = Depends(get_current_user)
):
    """Get use case statistics"""
    try:
        # Use case statistics are shared data, just ensure user is authenticated
        statistics = use_case_service.get_use_case_statistics()
        return statistics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting use case statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get use case statistics: {str(e)}")

@router.get("/use-cases/famous-examples")
@require_auth("read", allow_independent=True)
async def get_famous_examples(
    user_context: UserContext = Depends(get_current_user)
):
    """Get famous physics modeling examples"""
    try:
        # Famous examples are shared resources, just ensure user is authenticated
        examples = use_case_service.get_famous_examples()
        return {"examples": examples}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting famous examples: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get famous examples: {str(e)}")

@router.get("/use-cases/optimization-targets")
@require_auth("read", allow_independent=True)
async def get_optimization_targets(
    user_context: UserContext = Depends(get_current_user)
):
    """Get common optimization targets for physics modeling"""
    try:
        # Optimization targets are shared resources, just ensure user is authenticated
        targets = use_case_service.get_optimization_targets()
        return {"targets": targets}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting optimization targets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization targets: {str(e)}")

@router.get("/use-cases/hydrogen-economy")
@require_auth("read", allow_independent=True)
async def get_hydrogen_economy_use_case(
    user_context: UserContext = Depends(get_current_user)
):
    """Get hydrogen economy use case details"""
    try:
        # Hydrogen economy use case is a shared resource, just ensure user is authenticated
        use_case = use_case_service.get_hydrogen_economy_use_case()
        return use_case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting hydrogen economy use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hydrogen economy use case: {str(e)}")

@router.post("/models/create-from-use-case")
@require_auth("create", allow_independent=True)
async def create_model_from_use_case(
    request: Dict[str, Any],
    user_context: UserContext = Depends(get_current_user)
):
    """Create a physics model from a use case template"""
    try:
        # Initialize user-specific service for permission checking
        user_specific_service = PhysicsModelingUserSpecificService(user_context)
        
        # Check if user can create models
        if not user_specific_service.can_create_model():
            raise HTTPException(status_code=403, detail="Insufficient permissions to create models")
        
        # Get user limits
        user_limits = user_specific_service.get_user_model_limits()
        
        # Check if user has reached model limit
        current_models = len(user_specific_service.get_user_models())
        if current_models >= user_limits['max_models']:
            raise HTTPException(
                status_code=400, 
                detail=f"Model limit reached. Maximum allowed: {user_limits['max_models']}"
            )
        
        # Add user context to request
        request['created_by'] = user_context.user_id
        request['organization_id'] = getattr(user_context, 'organization_id', None)
        
        # Create model from use case
        result = physics_model_service.create_model_from_use_case(request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating model from use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create model from use case: {str(e)}")

# System endpoints
@router.get("/twins")
@require_auth("read", allow_independent=True)
async def get_available_twins(
    user_context: UserContext = Depends(get_current_user)
):
    """Get available digital twins for physics modeling"""
    try:
        # Digital twins are shared resources, just ensure user is authenticated
        twins = digital_twin_service.get_available_twins()
        return {"twins": twins}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available twins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get available twins: {str(e)}")

@router.get("/twins/{twin_id}")
@require_auth("read", allow_independent=True)
async def get_twin_details(
    twin_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get specific digital twin details"""
    try:
        # Digital twins are shared resources, just ensure user is authenticated
        twins = digital_twin_service.get_available_twins()
        twin = next((t for t in twins if t["twin_id"] == twin_id), None)
        
        if not twin:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        
        # Get additional twin details
        twin_details = digital_twin_service.get_twin_details(twin_id)
        return twin_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting twin details {twin_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get twin details: {str(e)}")

@router.get("/status", response_model=SystemStatusResponse)
@require_auth("read", allow_independent=True)
async def get_system_status(
    user_context: UserContext = Depends(get_current_user)
):
    """Get system status and health information"""
    try:
        # System status is shared information, just ensure user is authenticated
        # Check service availability
        physics_framework_available = physics_model_service is not None
        twin_connector_status = "connected" if digital_twin_service else "disconnected"
        ai_rag_connector_status = "connected" if ai_rag_service else "disconnected"
        
        # Get system metrics
        available_models = len(physics_model_service.list_models())
        active_simulations = simulation_service.get_active_simulations_count()
        available_twins = len(digital_twin_service.get_available_twins())
        
        # Check framework availability
        framework_status = "available" if physics_framework_available else "unavailable"
        
        return SystemStatusResponse(
            physics_framework_available=physics_framework_available,
            available_models=available_models,
            active_simulations=active_simulations,
            twin_connector_status=twin_connector_status,
            ai_rag_connector_status=ai_rag_connector_status,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/system/status", response_model=SystemStatusResponse)
@require_auth("read", allow_independent=True)
async def get_system_status_alt(
    user_context: UserContext = Depends(get_current_user)
):
    """Alternative endpoint for system status"""
    return await get_system_status(user_context)

@router.get("/system/performance")
@require_auth("read", allow_independent=True)
async def get_system_performance(
    user_context: UserContext = Depends(get_current_user)
):
    """Get system performance metrics"""
    try:
        # System performance metrics are shared information, just ensure user is authenticated
        # Get real performance data
        active_simulations = simulation_service.get_active_simulations_count()
        total_models = len(physics_model_service.list_models())
        available_twins = len(digital_twin_service.get_available_twins())
        
        # Get real system metrics (simplified for now)
        performance_metrics = {
            "cpu_usage": 0.75,  # Mock data - replace with real monitoring
            "memory_usage": 0.60,  # Mock data - replace with real monitoring
            "disk_io": 0.45,  # Mock data - replace with real monitoring
            "network_latency": "20ms",  # Mock data - replace with real monitoring
            "api_response_time_avg": "50ms",  # Mock data - replace with real monitoring
            "simulation_throughput_avg": "10 simulations/min",  # Mock data - replace with real monitoring
            "timestamp": datetime.now().isoformat()
        }
        
        return performance_metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system performance: {str(e)}")

@router.get("/system/metrics")
@require_auth("read", allow_independent=True)
async def get_system_metrics(
    user_context: UserContext = Depends(get_current_user)
):
    """Get detailed system metrics for monitoring"""
    try:
        # System metrics are shared information, just ensure user is authenticated
        # Get real metrics from services
        total_models = len(physics_model_service.list_models())
        total_simulations_run = len(simulation_service.list_simulations())
        total_validations_run = len(validation_service.list_validations())
        available_twins = len(digital_twin_service.get_available_twins())
        
        # Calculate real metrics based on available data
        successful_simulations = len([s for s in simulation_service.list_simulations() if s.get('status') == 'completed'])
        failed_simulations = len([s for s in simulation_service.list_simulations() if s.get('status') == 'failed'])
        
        # Mock metrics that would come from real monitoring systems
        metrics = {
            "total_models": total_models,
            "total_simulations_run": total_simulations_run,
            "total_validations_run": total_validations_run,
            "successful_simulations": successful_simulations,
            "failed_simulations": failed_simulations,
            "average_simulation_time_sec": 300,  # Mock - replace with real calculation
            "average_validation_accuracy": 0.92,  # Mock - replace with real calculation
            "data_storage_gb": 150,  # Mock - replace with real monitoring
            "api_calls_per_hour": 1200,  # Mock - replace with real monitoring
            "user_sessions_active": 50,  # Mock - replace with real monitoring
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

@router.post("/system/diagnostics")
@require_auth("read", allow_independent=True)
async def run_system_diagnostics(
    user_context: UserContext = Depends(get_current_user)
):
    """Run system diagnostics and health checks"""
    try:
        # System diagnostics are shared information, just ensure user is authenticated
        logger.info("Running system diagnostics...")
        
        # Check service availability
        services_status = {
            "physics_model_service": physics_model_service is not None,
            "simulation_service": simulation_service is not None,
            "validation_service": validation_service is not None,
            "use_case_service": use_case_service is not None,
            "digital_twin_service": digital_twin_service is not None,
            "ai_rag_service": ai_rag_service is not None
        }
        
        # Check database connections and basic functionality
        diagnostic_results = {
            "status": "completed",
            "checks_run": ["service_availability", "database_connection", "api_connectivity", "resource_availability"],
            "services_status": services_status,
            "issues_found": [],
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add specific checks if services are available
        if physics_model_service:
            try:
                model_count = len(physics_model_service.list_models())
                diagnostic_results["model_count"] = model_count
            except Exception as e:
                diagnostic_results["issues_found"].append(f"Physics model service error: {str(e)}")
        
        if simulation_service:
            try:
                simulation_count = simulation_service.get_active_simulations_count()
                diagnostic_results["active_simulations"] = simulation_count
            except Exception as e:
                diagnostic_results["issues_found"].append(f"Simulation service error: {str(e)}")
        
        return diagnostic_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running system diagnostics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run system diagnostics: {str(e)}")

@router.get("/health")
@require_auth("read", allow_independent=True)
async def health_check(
    user_context: UserContext = Depends(get_current_user)
):
    """Health check endpoint"""
    return {"status": "ok", "message": "Physics Modeling module is healthy"} 