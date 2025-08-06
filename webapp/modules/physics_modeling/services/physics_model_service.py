"""
Physics Model Service

Handles business logic for physics model creation, management, and operations.
Integrated with the shared DigitalTwin database architecture.
"""

import logging
import uuid
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

# Import shared database components
try:
    from src.shared.database.base_manager import BaseDatabaseManager
    from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
    from src.shared.models.digital_twin import DigitalTwin
    from src.shared.services.digital_twin_service import DigitalTwinService
except ImportError as e:
    logging.error(f"Shared database components not available: {e}")
    raise

# Import the physics modeling framework
try:
    from src.physics_modeling import DynamicPhysicsModelingFramework
    from src.physics_modeling.core.dynamic_types import PhysicsPlugin
    from src.physics_modeling.core.plugin_manager import PluginManager
    from src.physics_modeling.core.model_factory import ModelFactory
    from src.physics_modeling.simulation.simulation_engine import SimulationEngine
except ImportError as e:
    logging.warning(f"Physics Modeling modules not available: {e}")
    DynamicPhysicsModelingFramework = None
    PhysicsPlugin = None
    PluginManager = None
    ModelFactory = None
    SimulationEngine = None

logger = logging.getLogger(__name__)


class PhysicsModelService:
    """Service for managing physics models using DigitalTwin data"""
    
    def __init__(self, db_manager: BaseDatabaseManager = None, digital_twin_service: DigitalTwinService = None):
        self.db_manager = db_manager
        self.digital_twin_repository = DigitalTwinRepository(db_manager) if db_manager else None
        self.digital_twin_service = digital_twin_service
        self.physics_framework = None
        self._initialize_framework()
    
    def _initialize_framework(self):
        """Initialize the physics modeling framework"""
        if DynamicPhysicsModelingFramework is None:
            logger.error("Physics Modeling Framework not available")
            return
            
        try:
            self.physics_framework = DynamicPhysicsModelingFramework()
            logger.info("Physics Modeling Framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Physics Modeling Framework: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize Physics Modeling Framework"
            )
    
    def create_model(self, twin_id: str, model_type: str, geometry_file: Optional[str] = None,
                    material_properties: Optional[Dict[str, Any]] = None,
                    boundary_conditions: Optional[Dict[str, Any]] = None,
                    solver_settings: Optional[Dict[str, Any]] = None,
                    use_ai_insights: bool = True) -> Dict[str, Any]:
        """
        Create a new physics model
        
        Args:
            twin_id: ID of the digital twin
            model_type: Type of physics model (thermal, structural, fluid, multi_physics)
            geometry_file: Path to geometry file
            material_properties: Material properties configuration
            boundary_conditions: Boundary conditions configuration
            solver_settings: Solver configuration
            use_ai_insights: Whether to use AI insights for optimization
            
        Returns:
            Model creation response with model details
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        try:
            # Generate unique model ID
            model_id = str(uuid.uuid4())
            
            # Create model configuration
            model_config = {
                "model_id": model_id,
                "twin_id": twin_id,
                "model_type": model_type,
                "geometry_file": geometry_file,
                "material_properties": material_properties or {},
                "boundary_conditions": boundary_conditions or {},
                "solver_settings": solver_settings or {},
                "created_at": datetime.utcnow().isoformat(),
                "status": "created"
            }
            
            # Get AI insights if requested
            ai_insights = None
            if use_ai_insights and PluginManager:
                try:
                    plugin_manager = PluginManager()
                    ai_insights = plugin_manager.get_modeling_insights(
                        model_type=model_type,
                        material_properties=material_properties,
                        boundary_conditions=boundary_conditions
                    )
                    logger.info(f"AI insights generated for model {model_id}")
                except Exception as e:
                    logger.warning(f"Failed to get AI insights: {e}")
            
            # Create the physics model using the framework
            physics_model = self.physics_framework.create_model(
                model_id=model_id,
                twin_id=twin_id,
                model_type=model_type,
                geometry_file=geometry_file,
                material_properties=material_properties,
                boundary_conditions=boundary_conditions,
                solver_settings=solver_settings
            )
            
            # Store model in twin registry if available
            if PluginManager:
                try:
                    plugin_manager = PluginManager()
                    plugin_manager.store_physics_model(twin_id, model_id, model_config)
                    logger.info(f"Model {model_id} stored in twin registry")
                except Exception as e:
                    logger.warning(f"Failed to store model in twin registry: {e}")
            
            return {
                "model_id": model_id,
                "twin_id": twin_id,
                "model_type": model_type,
                "status": "created",
                "created_at": model_config["created_at"],
                "configuration": model_config,
                "ai_insights": ai_insights
            }
            
        except Exception as e:
            logger.error(f"Failed to create physics model: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create physics model: {str(e)}"
            )
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get a specific physics model by ID
        
        Args:
            model_id: ID of the physics model
            
        Returns:
            Model details
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=404,
                detail=f"Physics model {model_id} not found (framework not available)"
            )
        
        try:
            model = self.physics_framework.get_model(model_id)
            if not model:
                raise HTTPException(
                    status_code=404,
                    detail=f"Physics model {model_id} not found"
                )
            
            return {
                "model_id": model_id,
                "twin_id": model.twin_id,
                "model_type": model.model_type,
                "status": model.status,
                "created_at": model.created_at.isoformat() if model.created_at else None,
                "configuration": model.configuration,
                "validation_status": getattr(model, 'validation_status', 'unknown')
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get physics model {model_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get physics model: {str(e)}"
            )
    
    def list_models(self, twin_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available physics models
        
        Args:
            twin_id: Optional twin ID to filter models
            
        Returns:
            List of model summaries
        """
        if not self.physics_framework:
            # Return empty list when framework is not available
            logger.warning("Physics Modeling framework not available, returning empty model list")
            return []
        
        try:
            # For now, return empty list since the framework doesn't have a list_models method
            # This can be enhanced later when model persistence is implemented
            logger.info("Model listing not yet implemented in framework, returning empty list")
            return []
            
        except Exception as e:
            logger.error(f"Failed to list physics models: {e}")
            # Return empty list on error instead of raising exception
            return []
    
    def update_model(self, model_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a physics model
        
        Args:
            model_id: ID of the physics model
            updates: Dictionary of updates to apply
            
        Returns:
            Updated model details
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        try:
            # Get current model
            model = self.physics_framework.get_model(model_id)
            if not model:
                raise HTTPException(
                    status_code=404,
                    detail=f"Physics model {model_id} not found"
                )
            
            # Apply updates
            updated_model = self.physics_framework.update_model(model_id, updates)
            
            return {
                "model_id": model_id,
                "twin_id": updated_model.twin_id,
                "model_type": updated_model.model_type,
                "status": updated_model.status,
                "updated_at": datetime.utcnow().isoformat(),
                "configuration": updated_model.configuration
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update physics model {model_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update physics model: {str(e)}"
            )
    
    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """
        Delete a physics model
        
        Args:
            model_id: ID of the physics model
            
        Returns:
            Deletion confirmation
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        try:
            # Check if model exists
            model = self.physics_framework.get_model(model_id)
            if not model:
                raise HTTPException(
                    status_code=404,
                    detail=f"Physics model {model_id} not found"
                )
            
            # Delete the model
            self.physics_framework.delete_model(model_id)
            
            # Remove from twin registry if available
            if PluginManager:
                try:
                    plugin_manager = PluginManager()
                    plugin_manager.remove_physics_model(model.twin_id, model_id)
                    logger.info(f"Model {model_id} removed from twin registry")
                except Exception as e:
                    logger.warning(f"Failed to remove model from twin registry: {e}")
            
            return {
                "model_id": model_id,
                "status": "deleted",
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete physics model {model_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete physics model: {str(e)}"
            )
    
    def get_available_twins(self) -> List[Dict[str, Any]]:
        """
        Get available digital twins for physics modeling from shared database
        
        Returns:
            List of available twins with extracted data
        """
        if not self.digital_twin_repository:
            logger.error("Digital Twin Repository not available")
            return []
        
        try:
            # Get active digital twins from shared database
            active_twins = self.digital_twin_repository.get_active_twins()
            
            twin_list = []
            for twin in active_twins:
                # Only include twins that have extracted data
                if twin.extracted_data_path and os.path.exists(twin.extracted_data_path):
                    twin_info = {
                        "twin_id": twin.twin_id,
                        "name": twin.twin_name,
                        "status": twin.status,
                        "health_status": twin.health_status,
                        "extracted_data_path": twin.extracted_data_path,
                        "physics_context": twin.physics_context or {},
                        "simulation_status": twin.simulation_status,
                        "last_simulation_run": twin.last_simulation_run,
                        "model_version": twin.model_version,
                        "description": f"Digital twin for {twin.twin_name} with extracted data available"
                    }
                    twin_list.append(twin_info)
            
            logger.info(f"Found {len(twin_list)} digital twins with extracted data for physics modeling")
            return twin_list
            
        except Exception as e:
            logger.error(f"Failed to get available twins from database: {e}")
            return []
    
    def load_extracted_data(self, twin_id: str) -> Dict[str, Any]:
        """
        Load extracted data from DigitalTwin for physics simulation
        
        Args:
            twin_id: ID of the digital twin
            
        Returns:
            Extracted data for physics simulation
        """
        if not self.digital_twin_repository:
            raise HTTPException(
                status_code=503,
                detail="Digital Twin Repository not available"
            )
        
        try:
            # Get the digital twin
            twin = self.digital_twin_repository.get_by_id(twin_id)
            if not twin:
                raise HTTPException(
                    status_code=404,
                    detail=f"Digital twin {twin_id} not found"
                )
            
            # Check if extracted data path exists
            if not twin.extracted_data_path:
                raise HTTPException(
                    status_code=400,
                    detail=f"Digital twin {twin_id} has no extracted data"
                )
            
            if not os.path.exists(twin.extracted_data_path):
                raise HTTPException(
                    status_code=400,
                    detail=f"Extracted data path does not exist: {twin.extracted_data_path}"
                )
            
            # Load extracted data from file
            try:
                with open(twin.extracted_data_path, 'r') as f:
                    extracted_data = json.load(f)
                
                logger.info(f"Loaded extracted data from {twin.extracted_data_path}")
                return extracted_data
                
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid JSON in extracted data: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load extracted data: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to load extracted data for twin {twin_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load extracted data: {str(e)}"
            )

    def get_available_plugins(self) -> List[Dict[str, Any]]:
        """
        Get all available physics plugins from the framework
        
        Returns:
            List of available plugins with their details
        """
        if not self.physics_framework:
            logger.warning("Physics Modeling framework not available")
            return []
        
        try:
            plugins = self.physics_framework.get_available_plugins()
            plugin_list = []
            
            for plugin_id, plugin_info in plugins.items():
                plugin_list.append({
                    "plugin_id": plugin_id,
                    "name": plugin_info.get("name", "Unknown"),
                    "version": plugin_info.get("version", "1.0.0"),
                    "description": plugin_info.get("description", ""),
                    "category": plugin_info.get("category", "unknown"),
                    "parameters": plugin_info.get("parameters", []),
                    "equations": plugin_info.get("equations", []),
                    "solver_capabilities": plugin_info.get("solver_capabilities", [])
                })
            
            logger.info(f"Found {len(plugin_list)} available plugins")
            return plugin_list
            
        except Exception as e:
            logger.error(f"Failed to get available plugins: {e}")
            return []
    
    def get_plugins_for_twin(self, twin_id: str) -> List[Dict[str, Any]]:
        """
        Get plugins available for a specific digital twin
        
        Args:
            twin_id: ID of the digital twin
            
        Returns:
            List of plugins available for the twin
        """
        if not self.physics_framework:
            logger.warning("Physics Modeling framework not available")
            return []
        
        try:
            # Get trace info for the twin
            trace_info = self.physics_framework.get_twin_trace_info(twin_id)
            if not trace_info:
                logger.warning(f"Could not trace twin {twin_id}")
                return []
            
            # Get plugins for the use case
            plugins = self.physics_framework.get_plugins_for_use_case(trace_info['use_case_name'])
            
            plugin_list = []
            for plugin_info in plugins:
                plugin_list.append({
                    "plugin_id": plugin_info.get("plugin_id"),
                    "name": plugin_info.get("name", "Unknown"),
                    "version": plugin_info.get("version", "1.0.0"),
                    "description": plugin_info.get("description", ""),
                    "category": plugin_info.get("category", "unknown"),
                    "parameters": plugin_info.get("parameters", []),
                    "equations": plugin_info.get("equations", []),
                    "solver_capabilities": plugin_info.get("solver_capabilities", []),
                    "use_case_name": trace_info['use_case_name'],
                    "project_name": trace_info['project_name']
                })
            
            logger.info(f"Found {len(plugin_list)} plugins for twin {twin_id}")
            return plugin_list
            
        except Exception as e:
            logger.error(f"Failed to get plugins for twin {twin_id}: {e}")
            return []
    
    def run_simulation(self, twin_id: str, plugin_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a physics simulation using a specific plugin
        
        Args:
            twin_id: ID of the digital twin
            plugin_id: ID of the plugin to use
            parameters: Simulation parameters
            
        Returns:
            Simulation results
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        try:
            # Run simulation using the framework
            results = self.physics_framework.run_simulation(
                twin_id=twin_id,
                plugin_id=plugin_id,
                parameters=parameters or {}
            )
            
            return {
                "simulation_id": str(uuid.uuid4()),
                "twin_id": twin_id,
                "plugin_id": plugin_id,
                "status": "completed",
                "results": results,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to run simulation for twin {twin_id} with plugin {plugin_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to run simulation: {str(e)}"
            )

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get all available physics models
        
        Returns:
            List of available models
        """
        return self.list_models()

    def is_framework_available(self) -> bool:
        """
        Check if the physics framework is available
        
        Returns:
            True if framework is available, False otherwise
        """
        return self.physics_framework is not None 