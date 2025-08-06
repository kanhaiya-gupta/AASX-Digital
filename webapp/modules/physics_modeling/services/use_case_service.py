"""
Use Case Service

Handles business logic for physics modeling use cases, templates, and examples.
"""

import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from pathlib import Path

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


class UseCaseService:
    """Service for managing physics modeling use cases"""
    
    def __init__(self):
        self.physics_framework = None
        self.db_path = Path('data/aasx_database.db')
        self.use_cases = {}
        self._initialize_framework()
        self._load_use_cases_from_database()
    
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
    
    def _load_use_cases_from_database(self):
        """Load use cases from the database"""
        try:
            if not self.db_path.exists():
                logger.error(f"Database not found at {self.db_path}")
                raise HTTPException(
                    status_code=500,
                    detail="Use cases database not available"
                )

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get use cases with project counts
            cursor.execute("""
                SELECT uc.use_case_id, uc.name, uc.description, uc.category, uc.metadata,
                       COUNT(p.project_id) as project_count
                FROM use_cases uc
                LEFT JOIN project_use_case_links puc ON uc.use_case_id = puc.use_case_id
                LEFT JOIN projects p ON puc.project_id = p.project_id
                WHERE uc.is_active = 1
                GROUP BY uc.use_case_id, uc.name, uc.description, uc.category, uc.metadata
                ORDER BY uc.name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            self.use_cases = {}
            for row in rows:
                use_case_id, name, description, category, metadata_json, project_count = row
                
                # Parse metadata
                metadata = {}
                if metadata_json:
                    try:
                        metadata = json.loads(metadata_json)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in metadata for use case {use_case_id}")
                
                # Extract examples from metadata
                examples = metadata.get('famous_examples', [])
                
                # Map database category to physics model type
                model_type_mapping = {
                    'thermal': 'thermal',
                    'structural': 'structural', 
                    'fluid_dynamics': 'fluid',
                    'multi_physics': 'multi_physics',
                    'industrial': 'industrial'
                }
                
                self.use_cases[use_case_id] = {
                    "id": use_case_id,
                    "name": name,
                    "category": category,
                    "description": description,
                    "model_type": model_type_mapping.get(category, category),
                    "examples": examples,
                    "project_count": project_count,
                    "metadata": metadata,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            
            logger.info(f"Loaded {len(self.use_cases)} use cases from database")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error loading use cases from database: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load use cases from database: {str(e)}"
            )
    
    def get_use_cases(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available use cases with optional category filtering
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of use cases
        """
        use_cases = []
        
        for use_case in self.use_cases.values():
            if category and use_case["category"] != category:
                continue
            
            use_cases.append({
                "id": use_case["id"],
                "name": use_case["name"],
                "category": use_case["category"],
                "description": use_case["description"],
                "model_type": use_case["model_type"],
                "examples": use_case["examples"],
                "project_count": use_case.get("project_count", 0),
                "created_at": use_case["created_at"],
                "updated_at": use_case["updated_at"]
            })
        
        return use_cases
    
    def get_use_case(self, use_case_id: str) -> Dict[str, Any]:
        """
        Get a specific use case by ID
        
        Args:
            use_case_id: ID of the use case
            
        Returns:
            Use case details
        """
        if use_case_id not in self.use_cases:
            raise HTTPException(
                status_code=404,
                detail=f"Use case {use_case_id} not found"
            )
        
        return self.use_cases[use_case_id]
    
    def get_use_case_projects(self, use_case_id: str) -> List[Dict[str, Any]]:
        """
        Get projects associated with a specific use case
        
        Args:
            use_case_id: ID of the use case
            
        Returns:
            List of associated projects
        """
        if use_case_id not in self.use_cases:
            raise HTTPException(
                status_code=404,
                detail=f"Use case {use_case_id} not found"
            )
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get projects linked to this use case
            cursor.execute("""
                SELECT p.project_id, p.name, p.description, p.access_level, p.created_at, p.updated_at
                FROM projects p
                INNER JOIN project_use_case_links puc ON p.project_id = puc.project_id
                WHERE puc.use_case_id = ?
                ORDER BY p.name
            """, (use_case_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            projects = []
            for row in rows:
                project_id, name, description, access_level, created_at, updated_at = row
                projects.append({
                    "project_id": project_id,
                    "name": name,
                    "description": description,
                    "access_level": access_level,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            
            logger.info(f"Found {len(projects)} projects for use case {use_case_id}")
            return projects
            
        except Exception as e:
            logger.error(f"Error getting projects for use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get projects for use case: {str(e)}"
            )
    
    def get_use_case_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get use case templates for model creation
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of use case templates
        """
        templates = []
        
        for use_case in self.use_cases.values():
            if category and use_case["category"] != category:
                continue
            
            template = {
                "id": use_case["id"],
                "name": use_case["name"],
                "category": use_case["category"],
                "model_type": use_case["model_type"],
                "template": {
                    "parameters": use_case.get("parameters", {}),
                    "boundary_conditions": use_case.get("boundary_conditions", {}),
                    "solver_settings": use_case.get("solver_settings", {})
                }
            }
            templates.append(template)
        
        return templates
    
    def get_use_case_statistics(self) -> Dict[str, Any]:
        """
        Get use case statistics
        
        Returns:
            Use case statistics
        """
        total_use_cases = len(self.use_cases)
        
        # Count by category
        category_counts = {}
        for use_case in self.use_cases.values():
            category = use_case["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by model type
        model_type_counts = {}
        for use_case in self.use_cases.values():
            model_type = use_case["model_type"]
            model_type_counts[model_type] = model_type_counts.get(model_type, 0) + 1
        
        return {
            "total_use_cases": total_use_cases,
            "category_distribution": category_counts,
            "model_type_distribution": model_type_counts,
            "categories": list(category_counts.keys()),
            "model_types": list(model_type_counts.keys())
        }
    
    def get_famous_examples(self) -> List[Dict[str, Any]]:
        """
        Get famous physics modeling examples from database metadata
        
        Returns:
            List of famous examples
        """
        examples = []
        
        for use_case in self.use_cases.values():
            metadata = use_case.get("metadata", {})
            famous_examples = metadata.get("famous_examples", [])
            
            for example in famous_examples:
                examples.append({
                    "id": f"{use_case['id']}_{example.lower().replace(' ', '_')}",
                    "name": example,
                    "description": f"Example from {use_case['name']}",
                    "category": use_case["category"],
                    "use_case_id": use_case["id"]
                })
        
        return examples
    
    def get_optimization_targets(self) -> List[Dict[str, Any]]:
        """
        Get common optimization targets for physics modeling
        
        Returns:
            List of optimization targets
        """
        return [
            {
                "id": "thermal_efficiency",
                "name": "Thermal Efficiency",
                "category": "thermal",
                "description": "Maximize heat transfer efficiency",
                "metrics": ["COP", "thermal_resistance", "heat_transfer_coefficient"],
                "optimization_methods": ["parameter_sweep", "genetic_algorithm", "gradient_descent"]
            },
            {
                "id": "structural_weight",
                "name": "Structural Weight Optimization",
                "category": "structural",
                "description": "Minimize weight while maintaining strength",
                "metrics": ["weight", "stress", "deflection", "safety_factor"],
                "optimization_methods": ["topology_optimization", "shape_optimization", "size_optimization"]
            },
            {
                "id": "flow_efficiency",
                "name": "Flow Efficiency",
                "category": "fluid",
                "description": "Minimize pressure drop and maximize flow rate",
                "metrics": ["pressure_drop", "flow_rate", "turbulence_intensity", "drag_coefficient"],
                "optimization_methods": ["shape_optimization", "parameter_optimization", "multi_objective"]
            },
            {
                "id": "energy_consumption",
                "name": "Energy Consumption",
                "category": "multi_physics",
                "description": "Minimize energy consumption in coupled systems",
                "metrics": ["power_consumption", "efficiency", "heat_loss", "mechanical_loss"],
                "optimization_methods": ["system_optimization", "control_optimization", "design_optimization"]
            }
        ]
    
    def get_hydrogen_economy_use_case(self) -> Dict[str, Any]:
        """
        Get hydrogen economy use case template
        
        Returns:
            Hydrogen economy use case details
        """
        return {
            "id": "hydrogen_economy",
            "name": "Hydrogen Economy Infrastructure",
            "category": "multi_physics",
            "description": "Multi-physics analysis of hydrogen production, storage, and distribution systems",
            "model_type": "multi_physics",
            "parameters": {
                "electrolyzer_efficiency": 0.75,
                "compression_ratio": 700.0,
                "storage_pressure": 70e6,
                "thermal_conductivity": 0.5,
                "hydrogen_diffusivity": 1e-8
            },
            "boundary_conditions": {
                "renewable_power_input": 100e6,  # 100 MW
                "ambient_temperature": 298.15,
                "storage_temperature": 293.15,
                "pipeline_pressure": 10e6
            },
            "solver_settings": {
                "solver_type": "coupled",
                "coupling_method": "staggered",
                "time_step": 3600,  # 1 hour
                "simulation_duration": 8760  # 1 year
            },
            "subsystems": [
                {
                    "name": "Electrolysis",
                    "physics": ["electrochemical", "thermal"],
                    "optimization_target": "efficiency"
                },
                {
                    "name": "Compression",
                    "physics": ["fluid", "thermal", "structural"],
                    "optimization_target": "energy_consumption"
                },
                {
                    "name": "Storage",
                    "physics": ["fluid", "thermal", "structural"],
                    "optimization_target": "safety"
                },
                {
                    "name": "Distribution",
                    "physics": ["fluid", "thermal"],
                    "optimization_target": "pressure_loss"
                }
            ],
            "examples": [
                "Green hydrogen production plant design",
                "Hydrogen storage tank optimization",
                "Pipeline network analysis",
                "Fueling station design"
            ],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def create_model_from_use_case(self, use_case_id: str, twin_id: str, 
                                 custom_parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a physics model from a use case template
        
        Args:
            use_case_id: ID of the use case template
            twin_id: ID of the digital twin
            custom_parameters: Optional custom parameters to override template
            
        Returns:
            Created model details
        """
        if use_case_id not in self.use_cases:
            raise HTTPException(
                status_code=404,
                detail=f"Use case {use_case_id} not found"
            )
        
        try:
            use_case = self.use_cases[use_case_id]
            
            # Merge template parameters with custom parameters
            parameters = use_case.get("parameters", {}).copy()
            if custom_parameters:
                parameters.update(custom_parameters)
            
            # Create model using physics model service
            from .physics_model_service import PhysicsModelService
            model_service = PhysicsModelService()
            
            model_response = model_service.create_model(
                twin_id=twin_id,
                model_type=use_case["model_type"],
                material_properties=parameters,
                boundary_conditions=use_case.get("boundary_conditions", {}),
                solver_settings=use_case.get("solver_settings", {}),
                use_ai_insights=True
            )
            
            # Add use case reference
            model_response["use_case_id"] = use_case_id
            model_response["use_case_name"] = use_case["name"]
            
            logger.info(f"Created model {model_response['model_id']} from use case {use_case_id}")
            
            return model_response
            
        except Exception as e:
            logger.error(f"Failed to create model from use case {use_case_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create model from use case: {str(e)}"
            ) 