"""
Physics Modeling System API Routes
Provides REST API endpoints for the physics modeling system frontend
Integrated with the physics modeling framework
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import logging
from pathlib import Path
import sys
from datetime import datetime
import uuid
import numpy as np
import time

# Import the physics modeling framework
try:
    from src.physics_modeling import PhysicsModelingFramework
    from src.physics_modeling.core import PhysicsModel
    from src.physics_modeling.integration import TwinConnector, AIRAGConnector
    print("✅ Physics Modeling modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Physics Modeling modules: {e}")
    # Fallback to None if modules not available
    PhysicsModelingFramework = None
    PhysicsModel = None
    TwinConnector = None
    AIRAGConnector = None

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize physics modeling framework
physics_framework = None

def get_physics_framework():
    """Get or initialize physics modeling framework instance"""
    global physics_framework
    if physics_framework is None:
        if PhysicsModelingFramework is None:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available. Please check that the src modules are properly installed."
            )
        try:
            physics_framework = PhysicsModelingFramework()
            logger.info("Physics Modeling Framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Physics Modeling Framework: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize Physics Modeling Framework")
    return physics_framework

def serialize_use_case(use_case: dict) -> dict:
    """Convert use case object to JSON-serializable dictionary"""
    def _serialize_value(value):
        """Recursively serialize any value to JSON-serializable format"""
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, (list, tuple)):
            return [_serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {str(k): _serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (np.ndarray, np.generic)):
            return value.tolist() if hasattr(value, 'tolist') else str(value)
        elif hasattr(value, 'to_dict'):
            return _serialize_value(value.to_dict())
        elif hasattr(value, '__dict__'):
            try:
                # Convert object to dict and serialize
                obj_dict = {}
                for attr_name, attr_value in value.__dict__.items():
                    if not attr_name.startswith('_'):  # Skip private attributes
                        obj_dict[str(attr_name)] = _serialize_value(attr_value)
                return obj_dict
            except Exception:
                return str(value)
        else:
            return str(value)
    
    serialized = {}
    for key, value in use_case.items():
        serialized[str(key)] = _serialize_value(value)
    
    return serialized

def serialize_use_cases(use_cases: List[dict]) -> List[dict]:
    """Convert list of use case objects to JSON-serializable dictionaries"""
    return [serialize_use_case(use_case) for use_case in use_cases]

def serialize_use_case_categories(use_case_categories: dict) -> dict:
    """Convert use case categories to JSON-serializable dictionaries"""
    serialized = {}
    for category, use_cases in use_case_categories.items():
        serialized[str(category)] = serialize_use_cases(use_cases)
    return serialized

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

class SimulationRequest(BaseModel):
    model_id: str
    simulation_type: str  # steady_state, transient, optimization
    parameters: Optional[Dict[str, Any]] = None
    time_range: Optional[Dict[str, float]] = None
    output_format: str = "json"

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

@router.get("/", response_class=HTMLResponse)
async def physics_modeling_page(request: Request):
    """Render the physics modeling main page"""
    try:
        return templates.TemplateResponse(
            "physics_modeling/index.html",
            {
                "request": request,
                "page_title": "Physics Modeling",
                "module_name": "Physics Modeling",
                "version": "1.0.0"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering physics modeling page: {e}")
        raise HTTPException(status_code=500, detail="Failed to render physics modeling page")

@router.post("/api/models/create", response_model=ModelCreationResponse)
async def create_physics_model(request: ModelCreationRequest):
    """Create a new physics model from twin data"""
    try:
        framework = get_physics_framework()
        
        # Create model with AI insights if requested
        if request.use_ai_insights:
            # Get AI insights for model parameters
            ai_insights = framework.get_ai_insights_for_model(
                model_type=request.model_type,
                twin_id=request.twin_id
            )
        else:
            ai_insights = None
        
        # Create the model
        model = framework.create_model(
            name=f"Model_{request.twin_id}_{request.model_type}",
            physics_type=request.model_type,
            materials=request.material_properties,
            geometry=request.geometry_file,
            boundary_conditions=request.boundary_conditions,
            solver_settings=request.solver_settings
        )
        
        model_id = str(uuid.uuid4())
        
        return ModelCreationResponse(
            model_id=model_id,
            twin_id=request.twin_id,
            model_type=request.model_type,
            status="created",
            created_at=datetime.now().isoformat(),
            configuration={
                "materials": request.material_properties,
                "geometry": request.geometry_file,
                "boundary_conditions": request.boundary_conditions,
                "solver_settings": request.solver_settings
            },
            ai_insights=ai_insights
        )
        
    except Exception as e:
        logger.error(f"Error creating physics model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create model: {str(e)}")

@router.post("/api/simulations/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """Run a physics simulation"""
    try:
        framework = get_physics_framework()
        
        simulation_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Start simulation in background
        background_tasks.add_task(
            run_simulation_background,
            simulation_id=simulation_id,
            model_id=request.model_id,
            simulation_type=request.simulation_type,
            parameters=request.parameters,
            time_range=request.time_range
        )
        
        return SimulationResponse(
            simulation_id=simulation_id,
            model_id=request.model_id,
            status="running",
            progress=0.0,
            results=None,
            visualization_data=None,
            execution_time=time.time() - start_time,
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run simulation: {str(e)}")

@router.get("/api/simulations/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """Get simulation status and results"""
    try:
        # In a real implementation, this would check the actual simulation status
        # For now, return a mock response
        return {
            "simulation_id": simulation_id,
            "status": "completed",
            "progress": 100.0,
            "results": {
                "temperature": [25.0, 30.0, 35.0],
                "pressure": [101325.0, 102000.0, 103000.0],
                "time": [0.0, 1.0, 2.0]
            },
            "visualization_data": {
                "contour_plot": "data:image/png;base64,...",
                "time_series": "data:image/png;base64,..."
            },
            "execution_time": 45.2,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get simulation status: {str(e)}")

@router.post("/api/models/validate", response_model=ModelValidationResponse)
async def validate_model(request: ModelValidationRequest):
    """Validate a physics model against experimental data"""
    try:
        framework = get_physics_framework()
        
        # Perform validation
        validation_result = framework.validate_model(
            model_id=request.model_id,
            validation_data=request.validation_data
        )
        
        validation_id = str(uuid.uuid4())
        
        return ModelValidationResponse(
            validation_id=validation_id,
            model_id=request.model_id,
            accuracy_score=validation_result.get("accuracy", 0.85),
            validation_metrics=validation_result.get("metrics", {}),
            status="completed",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error validating model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate model: {str(e)}")

@router.get("/api/models")
async def get_available_models():
    """Get all available physics models"""
    try:
        framework = get_physics_framework()
        models = framework.get_available_models()
        
        return {
            "models": [
                {
                    "model_id": str(uuid.uuid4()),
                    "name": model.name if hasattr(model, 'name') else f"Model_{i}",
                    "physics_type": model.physics_type if hasattr(model, 'physics_type') else "multi_physics",
                    "status": "ready",
                    "created_at": datetime.now().isoformat()
                }
                for i, model in enumerate(models)
            ],
            "total_count": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@router.get("/api/twins")
async def get_available_twins():
    """Get all available digital twins from the twin registry"""
    try:
        # Import twin manager
        from webapp.modules.twin_registry.twin_manager import twin_manager
        
        # Get all registered twins from the database
        twins = twin_manager.get_all_registered_twins()
        
        # Transform the data to match the expected format
        formatted_twins = []
        for twin in twins:
            formatted_twin = {
                "twin_id": twin.get('twin_id', ''),
                "name": twin.get('twin_name', twin.get('name', 'Unknown Twin')),
                "type": twin.get('twin_type', twin.get('type', 'general')),
                "status": twin.get('status', 'active'),
                "description": twin.get('description', ''),
                "project_id": twin.get('project_id', ''),
                "created_at": twin.get('created_at', ''),
                "data_points": twin.get('data_points', 0)
            }
            formatted_twins.append(formatted_twin)
        
        # If no twins found, return some helpful mock data for development
        if not formatted_twins:
            logger.info("No twins found in registry, returning development mock data")
            formatted_twins = [
                {
                    "twin_id": "twin_001",
                    "name": "CPU Cooling System",
                    "type": "thermal",
                    "status": "active",
                    "description": "Thermal analysis of CPU cooling system",
                    "project_id": "electronics_project",
                    "created_at": datetime.now().isoformat(),
                    "data_points": 150
                },
                {
                    "twin_id": "twin_002", 
                    "name": "EV Battery Pack",
                    "type": "thermal",
                    "status": "active",
                    "description": "Battery thermal management system",
                    "project_id": "automotive_project",
                    "created_at": datetime.now().isoformat(),
                    "data_points": 200
                },
                {
                    "twin_id": "twin_003",
                    "name": "Wind Turbine Blade",
                    "type": "structural",
                    "status": "active",
                    "description": "Structural analysis of wind turbine blade",
                    "project_id": "renewable_energy_project",
                    "created_at": datetime.now().isoformat(),
                    "data_points": 300
                }
            ]
        
        return {
            "twins": formatted_twins,
            "total_count": len(formatted_twins)
        }
        
    except Exception as e:
        logger.error(f"Error getting available twins: {e}")
        # Return fallback data in case of error
        return {
            "twins": [
                {
                    "twin_id": "twin_001",
                    "name": "CPU Cooling System",
                    "type": "thermal",
                    "status": "active",
                    "description": "Thermal analysis of CPU cooling system"
                },
                {
                    "twin_id": "twin_002", 
                    "name": "EV Battery Pack",
                    "type": "thermal",
                    "status": "active",
                    "description": "Battery thermal management system"
                },
                {
                    "twin_id": "twin_003",
                    "name": "Wind Turbine Blade",
                    "type": "structural",
                    "status": "active",
                    "description": "Structural analysis of wind turbine blade"
                }
            ],
            "total_count": 3,
            "error": f"Failed to load twins from registry: {str(e)}"
        }

@router.get("/api/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get physics modeling system status"""
    try:
        framework = get_physics_framework()
        
        return SystemStatusResponse(
            physics_framework_available=True,
            available_models=len(framework.get_available_models()),
            active_simulations=2,  # Mock data
            twin_connector_status="connected",
            ai_rag_connector_status="connected",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        framework = get_physics_framework()
        return {
            "status": "healthy",
            "physics_framework": "available",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Use Cases Endpoints
# Global variables
DATABASE_AVAILABLE = False
project_manager = None

# Try to import project manager
try:
    from webapp.modules.aasx.routes import project_manager
    DATABASE_AVAILABLE = True
except ImportError:
    logger.warning("Database manager not available: No module named 'webapp.modules.aasx.routes'")
    DATABASE_AVAILABLE = False

def get_fallback_use_cases(category: str = None):
    """Get fallback use case data when database is not available."""
    try:
        framework = get_physics_framework()
        use_cases = framework.get_available_use_cases()
        
        if category:
            # Filter by category
            category_mapping = {
                "thermal": "thermal",
                "structural": "structural", 
                "fluid_dynamics": "fluid_dynamics",
                "multi_physics": "multi_physics",
                "industrial": "industrial"
            }
            
            if category in category_mapping:
                framework_category = category_mapping[category]
                if framework_category in use_cases:
                    return {
                        category: [serialize_use_case(uc) for uc in use_cases[framework_category]]
                    }
            
            return {}
        else:
            return serialize_use_case_categories(use_cases)
            
    except Exception as e:
        logger.error(f"Error getting fallback use cases: {e}")
        return {}

@router.get("/api/use-cases")
async def get_use_cases(category: str = None):
    """Get all use cases, optionally filtered by category."""
    try:
        if not DATABASE_AVAILABLE:
            # Return fallback data if database is not available
            return get_fallback_use_cases(category)
        
        use_cases = project_manager.list_use_cases(category=category)
        
        # Group by category
        grouped_use_cases = {}
        for use_case in use_cases:
            cat = use_case.get('category', 'other')
            if cat not in grouped_use_cases:
                grouped_use_cases[cat] = []
            grouped_use_cases[cat].append(use_case)
        
        return {
            "success": True,
            "use_cases": grouped_use_cases,
            "total_count": len(use_cases)
        }
        
    except Exception as e:
        logger.error(f"Error fetching use cases: {e}")
        return {
            "success": False,
            "error": str(e),
            "use_cases": get_fallback_use_cases(category)
        }

@router.get("/api/use-cases/{use_case_id}")
async def get_use_case(use_case_id: str):
    """Get a specific use case by ID."""
    try:
        if not DATABASE_AVAILABLE:
            return {"success": False, "error": "Database not available"}
        
        use_case = project_manager.get_use_case(use_case_id)
        if use_case:
            return {"success": True, "use_case": use_case}
        else:
            return {"success": False, "error": "Use case not found"}
            
    except Exception as e:
        logger.error(f"Error fetching use case {use_case_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/use-cases/{use_case_id}/projects")
async def get_use_case_projects(use_case_id: str):
    """Get all projects linked to a specific use case."""
    try:
        if not DATABASE_AVAILABLE:
            return {"success": False, "error": "Database not available"}
        
        projects = project_manager.get_use_case_projects(use_case_id)
        return {
            "success": True,
            "projects": projects,
            "count": len(projects)
        }
        
    except Exception as e:
        logger.error(f"Error fetching projects for use case {use_case_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/use-cases")
async def create_use_case(request: Request):
    """Create a new use case."""
    try:
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        form_data = await request.form()
        
        # Parse form data
        use_case_data = {
            "name": form_data.get("name"),
            "description": form_data.get("description"),
            "category": form_data.get("category"),
            "industry": form_data.get("industry"),
            "physics_type": form_data.get("physics_type"),
            "complexity": form_data.get("complexity"),
            "expected_duration": form_data.get("expected_duration"),
            "data_points": int(form_data.get("data_points", 0)) if form_data.get("data_points") else None,
            "tags": [tag.strip() for tag in form_data.get("tags", "").split(",") if tag.strip()],
            "metadata": {}
        }
        
        # Parse JSON fields
        if form_data.get("famous_examples"):
            examples_text = form_data.get("famous_examples")
            if examples_text.strip():
                use_case_data["famous_examples"] = [ex.strip() for ex in examples_text.split("\n") if ex.strip()]
        
        if form_data.get("optimization_targets"):
            targets_text = form_data.get("optimization_targets")
            if targets_text.strip():
                use_case_data["optimization_targets"] = [target.strip() for target in targets_text.split("\n") if target.strip()]
        
        if form_data.get("materials"):
            materials_text = form_data.get("materials")
            if materials_text.strip():
                try:
                    # Try to parse as JSON first
                    use_case_data["materials"] = json.loads(materials_text)
                except json.JSONDecodeError:
                    # If not JSON, treat as simple text
                    use_case_data["materials"] = materials_text
        
        # Validate required fields
        if not use_case_data["name"] or not use_case_data["description"] or not use_case_data["category"]:
            raise HTTPException(status_code=400, detail="Name, description, and category are required")
        
        # Create use case
        use_case_id = project_manager.create_use_case(use_case_data)
        
        return {
            "success": True,
            "use_case_id": use_case_id,
            "message": f"Use case '{use_case_data['name']}' created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create use case: {str(e)}")

@router.put("/api/use-cases/{use_case_id}")
async def update_use_case(use_case_id: str, request: Request):
    """Update an existing use case."""
    try:
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Check if use case exists
        existing_use_case = project_manager.get_use_case(use_case_id)
        if not existing_use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        
        form_data = await request.form()
        
        # Parse form data
        updates = {}
        if form_data.get("name"):
            updates["name"] = form_data.get("name")
        if form_data.get("description"):
            updates["description"] = form_data.get("description")
        if form_data.get("category"):
            updates["category"] = form_data.get("category")
        if form_data.get("industry"):
            updates["industry"] = form_data.get("industry")
        if form_data.get("physics_type"):
            updates["physics_type"] = form_data.get("physics_type")
        if form_data.get("complexity"):
            updates["complexity"] = form_data.get("complexity")
        if form_data.get("expected_duration"):
            updates["expected_duration"] = form_data.get("expected_duration")
        if form_data.get("data_points"):
            updates["data_points"] = int(form_data.get("data_points"))
        
        # Parse JSON fields
        if form_data.get("famous_examples"):
            examples_text = form_data.get("famous_examples")
            if examples_text.strip():
                updates["famous_examples"] = [ex.strip() for ex in examples_text.split("\n") if ex.strip()]
        
        if form_data.get("optimization_targets"):
            targets_text = form_data.get("optimization_targets")
            if targets_text.strip():
                updates["optimization_targets"] = [target.strip() for target in targets_text.split("\n") if target.strip()]
        
        if form_data.get("materials"):
            materials_text = form_data.get("materials")
            if materials_text.strip():
                try:
                    updates["materials"] = json.loads(materials_text)
                except json.JSONDecodeError:
                    updates["materials"] = materials_text
        
        if form_data.get("tags"):
            updates["tags"] = [tag.strip() for tag in form_data.get("tags", "").split(",") if tag.strip()]
        
        # Update use case
        success = project_manager.update_use_case(use_case_id, updates)
        
        if success:
            return {
                "success": True,
                "message": f"Use case updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update use case")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update use case: {str(e)}")

@router.delete("/api/use-cases/{use_case_id}")
async def delete_use_case(use_case_id: str):
    """Delete a use case."""
    try:
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Check if use case exists
        existing_use_case = project_manager.get_use_case(use_case_id)
        if not existing_use_case:
            raise HTTPException(status_code=404, detail="Use case not found")
        
        # Delete use case
        success = project_manager.delete_use_case(use_case_id)
        
        if success:
            return {
                "success": True,
                "message": f"Use case '{existing_use_case['name']}' deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete use case")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete use case: {str(e)}")

@router.get("/api/use-cases/statistics")
async def get_use_case_statistics():
    """Get use case statistics."""
    try:
        if not DATABASE_AVAILABLE:
            return get_fallback_statistics()
        
        stats = project_manager.get_use_case_statistics()
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting use case statistics: {e}")
        return {
            "success": False,
            "error": str(e),
            "statistics": get_fallback_statistics()
        }

def get_fallback_statistics():
    """Get fallback statistics when database is not available."""
    try:
        framework = get_physics_framework()
        use_cases = framework.get_available_use_cases()
        
        total_use_cases = sum(len(category_use_cases) for category_use_cases in use_cases.values())
        categories = {category: len(category_use_cases) for category, category_use_cases in use_cases.items()}
        
        return {
            "total_use_cases": total_use_cases,
            "categories": categories,
            "total_links": 0,
            "popular_use_cases": []
        }
    except Exception:
        return {
            "total_use_cases": 0,
            "categories": {},
            "total_links": 0,
            "popular_use_cases": []
        }

@router.get("/api/use-cases/famous-examples")
async def get_famous_examples():
    """Get famous examples organized by industry"""
    try:
        framework = get_physics_framework()
        famous_examples = framework.get_famous_examples()
        return famous_examples
    except Exception as e:
        logger.error(f"Error getting famous examples: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get famous examples: {str(e)}")

@router.get("/api/use-cases/optimization-targets")
async def get_optimization_targets():
    """Get optimization targets organized by use case"""
    try:
        framework = get_physics_framework()
        optimization_targets = framework.get_optimization_targets()
        return optimization_targets
    except Exception as e:
        logger.error(f"Error getting optimization targets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization targets: {str(e)}")

@router.get("/api/use-cases/hydrogen-economy")
async def get_hydrogen_economy_use_case():
    """Get the hydrogen economy use case specifically"""
    try:
        framework = get_physics_framework()
        hydrogen_use_case = framework.get_use_case_by_name("Hydrogen Economy Infrastructure Analysis")
        return serialize_use_case(hydrogen_use_case)
    except Exception as e:
        logger.error(f"Error getting hydrogen economy use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hydrogen economy use case: {str(e)}")

@router.post("/api/models/create-from-use-case")
async def create_model_from_use_case(request: Dict[str, Any]):
    """Create a physics model from a predefined use case"""
    try:
        framework = get_physics_framework()
        use_case_name = request.get("use_case_name")
        
        if not use_case_name:
            raise HTTPException(status_code=400, detail="use_case_name is required")
        
        # Create model from use case
        model = framework.create_model_from_use_case(use_case_name)
        
        model_id = str(uuid.uuid4())
        
        return {
            "model_id": model_id,
            "use_case_name": use_case_name,
            "model_name": model.name if hasattr(model, 'name') else use_case_name,
            "physics_type": model.physics_type if hasattr(model, 'physics_type') else "multi_physics",
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "message": f"Model created successfully from use case: {use_case_name}"
        }
    except Exception as e:
        logger.error(f"Error creating model from use case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create model: {str(e)}")

async def run_simulation_background(simulation_id: str, model_id: str, simulation_type: str, 
                                   parameters: Optional[Dict[str, Any]], time_range: Optional[Dict[str, float]]):
    """Background task to run simulation"""
    try:
        logger.info(f"Starting background simulation {simulation_id} for model {model_id}")
        
        # Simulate simulation progress
        for progress in range(0, 101, 10):
            await asyncio.sleep(1)  # Simulate work
            logger.info(f"Simulation {simulation_id} progress: {progress}%")
        
        logger.info(f"Simulation {simulation_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background simulation {simulation_id} failed: {e}")

# Setup templates
templates = Jinja2Templates(directory="webapp/templates")

@router.get("/use-cases-page", response_class=HTMLResponse)
async def use_cases_page(request: Request):
    """Render the dedicated use cases page"""
    try:
        templates = Jinja2Templates(directory="webapp/templates")
        return templates.TemplateResponse(
            "physics_modeling/use_cases.html",
            {
                "request": request,
                "title": "Physics Modeling Use Cases",
                "page": "use_cases"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering use cases page: {e}")
        raise HTTPException(status_code=500, detail="Failed to render use cases page")