"""
Twin Registry Integration for Physics Modeling
Integration with the existing twin registry system for simulation data
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import twin registry components
try:
    from src.modules.twin_registry.models.twin_registry import TwinRegistry
    from src.modules.twin_registry.repositories.twin_registry_repository import TwinRegistryRepository
    from src.modules.twin_registry.services.twin_registry_service import TwinRegistryService
    TWIN_REGISTRY_AVAILABLE = True
except ImportError:
    logger.warning("Twin registry components not available - using mock implementation")
    TWIN_REGISTRY_AVAILABLE = False

@dataclass
class TwinData:
    """Twin data for physics modeling"""
    twin_id: str
    twin_name: str
    twin_type: str
    physical_properties: Dict[str, Any]
    geometry_data: Dict[str, Any]
    material_properties: Dict[str, Any]
    boundary_conditions: Dict[str, Any]
    simulation_parameters: Dict[str, Any]
    last_updated: datetime
    metadata: Dict[str, Any]

@dataclass
class TwinQuery:
    """Query parameters for twin data"""
    twin_type: Optional[str] = None
    physical_property_filters: Optional[Dict[str, Any]] = None
    geometry_filters: Optional[Dict[str, Any]] = None
    material_filters: Optional[Dict[str, Any]] = None
    active_only: bool = True
    limit: Optional[int] = None

@dataclass
class TwinUpdateRequest:
    """Request to update twin data"""
    twin_id: str
    updates: Dict[str, Any]
    update_reason: str
    user_id: Optional[str] = None

class TwinRegistryIntegration:
    """Integration with the twin registry system"""

    def __init__(self):
        self.twin_service = None
        self.twin_repository = None
        self.integration_history = []
        
        if TWIN_REGISTRY_AVAILABLE:
            try:
                # Initialize twin registry components
                self.twin_service = TwinRegistryService()
                self.twin_repository = TwinRegistryRepository()
                logger.info("✅ Twin Registry Integration initialized with real components")
            except Exception as e:
                logger.warning(f"Failed to initialize twin registry components: {str(e)}")
                self._setup_mock_components()
        else:
            self._setup_mock_components()
        
        logger.info("✅ Twin Registry Integration initialized")

    def _setup_mock_components(self):
        """Setup mock components when twin registry is not available"""
        logger.info("Setting up mock twin registry components")
        
        # Mock twin data for testing
        self.mock_twins = {
            "twin_001": TwinData(
                twin_id="twin_001",
                twin_name="Structural Beam",
                twin_type="structural",
                physical_properties={
                    "length": 10.0,
                    "width": 0.2,
                    "height": 0.3,
                    "mass": 150.0
                },
                geometry_data={
                    "type": "beam",
                    "dimensions": [10.0, 0.2, 0.3],
                    "mesh_resolution": "medium",
                    "element_type": "hexahedron"
                },
                material_properties={
                    "material": "steel",
                    "youngs_modulus": 200e9,
                    "poissons_ratio": 0.3,
                    "density": 7850.0,
                    "yield_strength": 250e6
                },
                boundary_conditions={
                    "fixed_end": "left",
                    "load_type": "distributed",
                    "load_magnitude": 1000.0
                },
                simulation_parameters={
                    "solver_type": "finite_element",
                    "analysis_type": "static",
                    "convergence_tolerance": 1e-6,
                    "max_iterations": 1000
                },
                last_updated=datetime.now(),
                metadata={
                    "created_by": "system",
                    "version": "1.0",
                    "tags": ["structural", "beam", "static_analysis"]
                }
            ),
            "twin_002": TwinData(
                twin_id="twin_002",
                twin_name="Thermal Plate",
                twin_type="thermal",
                physical_properties={
                    "length": 5.0,
                    "width": 5.0,
                    "thickness": 0.05,
                    "mass": 10.0
                },
                geometry_data={
                    "type": "plate",
                    "dimensions": [5.0, 5.0, 0.05],
                    "mesh_resolution": "fine",
                    "element_type": "quadrilateral"
                },
                material_properties={
                    "material": "aluminum",
                    "thermal_conductivity": 237.0,
                    "specific_heat": 900.0,
                    "density": 2700.0,
                    "thermal_expansion": 23.1e-6
                },
                boundary_conditions={
                    "temperature_bc": "mixed",
                    "hot_side_temp": 373.15,
                    "cold_side_temp": 293.15,
                    "insulated_edges": ["top", "bottom"]
                },
                simulation_parameters={
                    "solver_type": "finite_difference",
                    "analysis_type": "steady_state",
                    "convergence_tolerance": 1e-4,
                    "max_iterations": 500
                },
                last_updated=datetime.now(),
                metadata={
                    "created_by": "system",
                    "version": "1.0",
                    "tags": ["thermal", "plate", "steady_state"]
                }
            ),
            "twin_003": TwinData(
                twin_id="twin_003",
                twin_name="Fluid Channel",
                twin_type="fluid",
                physical_properties={
                    "length": 20.0,
                    "diameter": 0.1,
                    "volume": 0.157,
                    "mass": 0.0
                },
                geometry_data={
                    "type": "channel",
                    "dimensions": [20.0, 0.1],
                    "mesh_resolution": "very_fine",
                    "element_type": "tetrahedron"
                },
                material_properties={
                    "fluid": "water",
                    "density": 998.0,
                    "viscosity": 1.002e-3,
                    "thermal_conductivity": 0.6,
                    "specific_heat": 4186.0
                },
                boundary_conditions={
                    "inlet_velocity": 2.0,
                    "outlet_pressure": 101325.0,
                    "wall_condition": "no_slip",
                    "temperature_bc": "isothermal"
                },
                simulation_parameters={
                    "solver_type": "finite_volume",
                    "analysis_type": "transient",
                    "convergence_tolerance": 1e-5,
                    "max_iterations": 2000,
                    "time_step": 0.001
                },
                last_updated=datetime.now(),
                metadata={
                    "created_by": "system",
                    "version": "1.0",
                    "tags": ["fluid", "channel", "transient", "cfd"]
                }
            )
        }

    async def get_available_twins(self, query: Optional[TwinQuery] = None) -> List[TwinData]:
        """Get available twins based on query parameters"""
        await asyncio.sleep(0)
        
        try:
            if self.twin_service and self.twin_repository:
                # Use real twin registry
                twins = await self._get_twins_from_registry(query)
            else:
                # Use mock data
                twins = await self._get_twins_from_mock(query)
            
            self.integration_history.append({
                'operation': 'get_available_twins',
                'query': query.__dict__ if query else None,
                'result_count': len(twins),
                'timestamp': datetime.now()
            })
            
            return twins
            
        except Exception as e:
            logger.error(f"Failed to get available twins: {str(e)}")
            raise

    async def _get_twins_from_registry(self, query: Optional[TwinQuery]) -> List[TwinData]:
        """Get twins from real twin registry"""
        try:
            # Get all twins from registry
            all_twins = await self.twin_service.get_all_twins()
            
            # Apply filters if query provided
            if query:
                filtered_twins = []
                for twin in all_twins:
                    if self._apply_twin_filters(twin, query):
                        filtered_twins.append(twin)
                
                # Apply limit
                if query.limit:
                    filtered_twins = filtered_twins[:query.limit]
                
                return filtered_twins
            else:
                return all_twins
                
        except Exception as e:
            logger.error(f"Failed to get twins from registry: {str(e)}")
            raise

    async def _get_twins_from_mock(self, query: Optional[TwinQuery]) -> List[TwinData]:
        """Get twins from mock data"""
        try:
            all_twins = list(self.mock_twins.values())
            
            # Apply filters if query provided
            if query:
                filtered_twins = []
                for twin in all_twins:
                    if self._apply_twin_filters(twin, query):
                        filtered_twins.append(twin)
                
                # Apply limit
                if query.limit:
                    filtered_twins = filtered_twins[:query.limit]
                
                return filtered_twins
            else:
                return all_twins
                
        except Exception as e:
            logger.error(f"Failed to get twins from mock: {str(e)}")
            raise

    def _apply_twin_filters(self, twin: TwinData, query: TwinQuery) -> bool:
        """Apply query filters to twin data"""
        try:
            # Filter by twin type
            if query.twin_type and twin.twin_type != query.twin_type:
                return False
            
            # Filter by physical properties
            if query.physical_property_filters:
                for prop, value in query.physical_property_filters.items():
                    if prop in twin.physical_properties:
                        if isinstance(value, (list, tuple)):
                            if len(value) == 2:  # Range filter
                                min_val, max_val = value
                                if not (min_val <= twin.physical_properties[prop] <= max_val):
                                    return False
                            else:  # List of allowed values
                                if twin.physical_properties[prop] not in value:
                                    return False
                        else:  # Exact match
                            if twin.physical_properties[prop] != value:
                                return False
            
            # Filter by geometry
            if query.geometry_filters:
                for geom, value in query.geometry_filters.items():
                    if geom in twin.geometry_data:
                        if twin.geometry_data[geom] != value:
                            return False
            
            # Filter by material properties
            if query.material_filters:
                for mat, value in query.material_filters.items():
                    if mat in twin.material_properties:
                        if isinstance(value, (list, tuple)):
                            if len(value) == 2:  # Range filter
                                min_val, max_val = value
                                if not (min_val <= twin.material_properties[mat] <= max_val):
                                    return False
                            else:  # List of allowed values
                                if twin.material_properties[mat] not in value:
                                    return False
                        else:  # Exact match
                            if twin.material_properties[mat] != value:
                                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply twin filters: {str(e)}")
            return False

    async def get_twin_by_id(self, twin_id: str) -> Optional[TwinData]:
        """Get specific twin by ID"""
        await asyncio.sleep(0)
        
        try:
            if self.twin_service and self.twin_repository:
                # Use real twin registry
                twin = await self.twin_service.get_twin_by_id(twin_id)
            else:
                # Use mock data
                twin = self.mock_twins.get(twin_id)
            
            if twin:
                self.integration_history.append({
                    'operation': 'get_twin_by_id',
                    'twin_id': twin_id,
                    'found': True,
                    'timestamp': datetime.now()
                })
            else:
                self.integration_history.append({
                    'operation': 'get_twin_by_id',
                    'twin_id': twin_id,
                    'found': False,
                    'timestamp': datetime.now()
                })
            
            return twin
            
        except Exception as e:
            logger.error(f"Failed to get twin by ID {twin_id}: {str(e)}")
            raise

    async def get_twins_by_type(self, twin_type: str) -> List[TwinData]:
        """Get all twins of a specific type"""
        await asyncio.sleep(0)
        
        try:
            query = TwinQuery(twin_type=twin_type)
            twins = await self.get_available_twins(query)
            
            self.integration_history.append({
                'operation': 'get_twins_by_type',
                'twin_type': twin_type,
                'result_count': len(twins),
                'timestamp': datetime.now()
            })
            
            return twins
            
        except Exception as e:
            logger.error(f"Failed to get twins by type {twin_type}: {str(e)}")
            raise

    async def search_twins(self, search_criteria: Dict[str, Any]) -> List[TwinData]:
        """Search twins using flexible criteria"""
        await asyncio.sleep(0)
        
        try:
            # Convert search criteria to query
            query = TwinQuery()
            
            if 'twin_type' in search_criteria:
                query.twin_type = search_criteria['twin_type']
            
            if 'physical_properties' in search_criteria:
                query.physical_property_filters = search_criteria['physical_properties']
            
            if 'geometry' in search_criteria:
                query.geometry_filters = search_criteria['geometry']
            
            if 'materials' in search_criteria:
                query.material_filters = search_criteria['materials']
            
            if 'limit' in search_criteria:
                query.limit = search_criteria['limit']
            
            twins = await self.get_available_twins(query)
            
            self.integration_history.append({
                'operation': 'search_twins',
                'search_criteria': search_criteria,
                'result_count': len(twins),
                'timestamp': datetime.now()
            })
            
            return twins
            
        except Exception as e:
            logger.error(f"Failed to search twins: {str(e)}")
            raise

    async def get_twin_simulation_data(self, twin_id: str, 
                                     simulation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get simulation-specific data for a twin"""
        await asyncio.sleep(0)
        
        try:
            twin = await self.get_twin_by_id(twin_id)
            if not twin:
                raise ValueError(f"Twin not found: {twin_id}")
            
            # Extract simulation-relevant data
            simulation_data = {
                'twin_id': twin.twin_id,
                'twin_name': twin.twin_name,
                'twin_type': twin.twin_type,
                'geometry': twin.geometry_data,
                'materials': twin.material_properties,
                'boundary_conditions': twin.boundary_conditions,
                'simulation_parameters': twin.simulation_parameters,
                'physical_constraints': self._extract_physical_constraints(twin),
                'mesh_requirements': self._extract_mesh_requirements(twin),
                'solver_recommendations': self._get_solver_recommendations(twin),
                'validation_criteria': self._get_validation_criteria(twin)
            }
            
            # Filter by simulation type if specified
            if simulation_type:
                simulation_data = self._filter_by_simulation_type(simulation_data, simulation_type)
            
            self.integration_history.append({
                'operation': 'get_twin_simulation_data',
                'twin_id': twin_id,
                'simulation_type': simulation_type,
                'data_keys': list(simulation_data.keys()),
                'timestamp': datetime.now()
            })
            
            return simulation_data
            
        except Exception as e:
            logger.error(f"Failed to get twin simulation data: {str(e)}")
            raise

    def _extract_physical_constraints(self, twin: TwinData) -> Dict[str, Any]:
        """Extract physical constraints from twin data"""
        constraints = {}
        
        try:
            # Extract constraints based on twin type
            if twin.twin_type == "structural":
                constraints.update({
                    'max_displacement': twin.physical_properties.get('length', 10.0) * 0.01,  # 1% of length
                    'max_stress': twin.material_properties.get('yield_strength', 250e6) * 0.8,  # 80% of yield
                    'stability_factor': 1.5,
                    'natural_frequency_range': [0.1, 100.0]  # Hz
                })
            elif twin.twin_type == "thermal":
                constraints.update({
                    'max_temperature': 1273.15,  # 1000°C
                    'min_temperature': 77.15,    # -196°C
                    'max_thermal_gradient': 1000.0,  # K/m
                    'thermal_stability': True
                })
            elif twin.twin_type == "fluid":
                constraints.update({
                    'max_velocity': 100.0,  # m/s
                    'max_pressure': 1e7,    # 100 bar
                    'max_temperature': 1273.15,  # 1000°C
                    'flow_stability': True
                })
            
            # Common constraints
            constraints.update({
                'geometry_consistency': True,
                'material_compatibility': True,
                'boundary_condition_validity': True
            })
            
        except Exception as e:
            logger.error(f"Failed to extract physical constraints: {str(e)}")
        
        return constraints

    def _extract_mesh_requirements(self, twin: TwinData) -> Dict[str, Any]:
        """Extract mesh requirements from twin data"""
        requirements = {}
        
        try:
            geometry = twin.geometry_data
            
            if geometry.get('type') == 'beam':
                requirements.update({
                    'min_elements_per_length': 10,
                    'aspect_ratio_limit': 5.0,
                    'mesh_type': 'structured',
                    'refinement_regions': ['ends', 'load_points']
                })
            elif geometry.get('type') == 'plate':
                requirements.update({
                    'min_elements_per_side': 20,
                    'aspect_ratio_limit': 3.0,
                    'mesh_type': 'structured',
                    'refinement_regions': ['corners', 'holes']
                })
            elif geometry.get('type') == 'channel':
                requirements.update({
                    'min_elements_per_diameter': 30,
                    'aspect_ratio_limit': 10.0,
                    'mesh_type': 'unstructured',
                    'refinement_regions': ['inlet', 'outlet', 'walls']
                })
            
            # Common requirements
            requirements.update({
                'quality_threshold': 0.3,
                'smoothing_iterations': 5,
                'adaptive_refinement': True
            })
            
        except Exception as e:
            logger.error(f"Failed to extract mesh requirements: {str(e)}")
        
        return requirements

    def _get_solver_recommendations(self, twin: TwinData) -> Dict[str, Any]:
        """Get solver recommendations for the twin"""
        recommendations = {}
        
        try:
            if twin.twin_type == "structural":
                recommendations.update({
                    'primary_solver': 'finite_element',
                    'alternative_solvers': ['finite_difference', 'analytical'],
                    'solver_parameters': {
                        'convergence_tolerance': 1e-6,
                        'max_iterations': 1000,
                        'preconditioner': 'ilu'
                    }
                })
            elif twin.twin_type == "thermal":
                recommendations.update({
                    'primary_solver': 'finite_difference',
                    'alternative_solvers': ['finite_element', 'finite_volume'],
                    'solver_parameters': {
                        'convergence_tolerance': 1e-4,
                        'max_iterations': 500,
                        'time_integration': 'implicit'
                    }
                })
            elif twin.twin_type == "fluid":
                recommendations.update({
                    'primary_solver': 'finite_volume',
                    'alternative_solvers': ['finite_element', 'lattice_boltzmann'],
                    'solver_parameters': {
                        'convergence_tolerance': 1e-5,
                        'max_iterations': 2000,
                        'turbulence_model': 'k_epsilon'
                    }
                })
            
        except Exception as e:
            logger.error(f"Failed to get solver recommendations: {str(e)}")
        
        return recommendations

    def _get_validation_criteria(self, twin: TwinData) -> Dict[str, Any]:
        """Get validation criteria for the twin"""
        criteria = {}
        
        try:
            if twin.twin_type == "structural":
                criteria.update({
                    'displacement_validation': {
                        'max_allowed': twin.physical_properties.get('length', 10.0) * 0.01,
                        'tolerance': 1e-6
                    },
                    'stress_validation': {
                        'max_allowed': twin.material_properties.get('yield_strength', 250e6) * 0.8,
                        'tolerance': 1e6
                    },
                    'frequency_validation': {
                        'min_allowed': 0.1,
                        'max_allowed': 100.0,
                        'tolerance': 0.1
                    }
                })
            elif twin.twin_type == "thermal":
                criteria.update({
                    'temperature_validation': {
                        'min_allowed': 77.15,
                        'max_allowed': 1273.15,
                        'tolerance': 1.0
                    },
                    'heat_flux_validation': {
                        'max_allowed': 1e6,
                        'tolerance': 1e3
                    }
                })
            elif twin.twin_type == "fluid":
                criteria.update({
                    'velocity_validation': {
                        'max_allowed': 100.0,
                        'tolerance': 0.1
                    },
                    'pressure_validation': {
                        'min_allowed': 1e3,
                        'max_allowed': 1e7,
                        'tolerance': 1e2
                    }
                })
            
        except Exception as e:
            logger.error(f"Failed to get validation criteria: {str(e)}")
        
        return criteria

    def _filter_by_simulation_type(self, simulation_data: Dict[str, Any], 
                                 simulation_type: str) -> Dict[str, Any]:
        """Filter simulation data by simulation type"""
        filtered_data = simulation_data.copy()
        
        try:
            if simulation_type == "static":
                # Keep only static analysis relevant data
                if 'simulation_parameters' in filtered_data:
                    filtered_data['simulation_parameters'] = {
                        k: v for k, v in filtered_data['simulation_parameters'].items()
                        if k in ['solver_type', 'analysis_type', 'convergence_tolerance', 'max_iterations']
                    }
            elif simulation_type == "transient":
                # Keep only transient analysis relevant data
                if 'simulation_parameters' in filtered_data:
                    filtered_data['simulation_parameters'] = {
                        k: v for k, v in filtered_data['simulation_parameters'].items()
                        if k in ['solver_type', 'analysis_type', 'convergence_tolerance', 'max_iterations', 'time_step']
                    }
            elif simulation_type == "frequency":
                # Keep only frequency analysis relevant data
                if 'simulation_parameters' in filtered_data:
                    filtered_data['simulation_parameters'] = {
                        k: v for k, v in filtered_data['simulation_parameters'].items()
                        if k in ['solver_type', 'analysis_type', 'convergence_tolerance', 'max_iterations']
                    }
            
        except Exception as e:
            logger.error(f"Failed to filter by simulation type: {str(e)}")
        
        return filtered_data

    async def update_twin_simulation_results(self, twin_id: str, 
                                           simulation_results: Dict[str, Any]) -> bool:
        """Update twin with simulation results"""
        await asyncio.sleep(0)
        
        try:
            if self.twin_service and self.twin_repository:
                # Use real twin registry
                success = await self._update_twin_in_registry(twin_id, simulation_results)
            else:
                # Use mock data
                success = await self._update_twin_in_mock(twin_id, simulation_results)
            
            self.integration_history.append({
                'operation': 'update_twin_simulation_results',
                'twin_id': twin_id,
                'success': success,
                'result_keys': list(simulation_results.keys()),
                'timestamp': datetime.now()
            })
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update twin simulation results: {str(e)}")
            raise

    async def _update_twin_in_registry(self, twin_id: str, 
                                     simulation_results: Dict[str, Any]) -> bool:
        """Update twin in real registry"""
        try:
            # This would integrate with the actual twin registry update mechanism
            # For now, return success
            return True
        except Exception as e:
            logger.error(f"Failed to update twin in registry: {str(e)}")
            return False

    async def _update_twin_in_mock(self, twin_id: str, 
                                 simulation_results: Dict[str, Any]) -> bool:
        """Update twin in mock data"""
        try:
            if twin_id in self.mock_twins:
                twin = self.mock_twins[twin_id]
                
                # Update simulation parameters with results
                if 'simulation_results' not in twin.metadata:
                    twin.metadata['simulation_results'] = {}
                
                twin.metadata['simulation_results'].update(simulation_results)
                twin.last_updated = datetime.now()
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to update twin in mock: {str(e)}")
            return False

    async def get_integration_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get integration operation history"""
        await asyncio.sleep(0)
        
        if limit is None:
            return self.integration_history
        else:
            return self.integration_history[-limit:]

    async def clear_integration_history(self) -> None:
        """Clear integration history"""
        await asyncio.sleep(0)
        self.integration_history.clear()
        logger.info("Integration history cleared")

    async def get_twin_statistics(self) -> Dict[str, Any]:
        """Get statistics about available twins"""
        await asyncio.sleep(0)
        
        try:
            all_twins = await self.get_available_twins()
            
            statistics = {
                'total_twins': len(all_twins),
                'twin_types': {},
                'materials': {},
                'geometry_types': {},
                'simulation_types': {},
                'last_updated': None
            }
            
            for twin in all_twins:
                # Count by twin type
                statistics['twin_types'][twin.twin_type] = statistics['twin_types'].get(twin.twin_type, 0) + 1
                
                # Count by material
                material = twin.material_properties.get('material', 'unknown')
                statistics['materials'][material] = statistics['materials'].get(material, 0) + 1
                
                # Count by geometry type
                geom_type = twin.geometry_data.get('type', 'unknown')
                statistics['geometry_types'][geom_type] = statistics['geometry_types'].get(geom_type, 0) + 1
                
                # Count by simulation type
                sim_type = twin.simulation_parameters.get('analysis_type', 'unknown')
                statistics['simulation_types'][sim_type] = statistics['simulation_types'].get(sim_type, 0) + 1
                
                # Track last update
                if statistics['last_updated'] is None or twin.last_updated > statistics['last_updated']:
                    statistics['last_updated'] = twin.last_updated
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get twin statistics: {str(e)}")
            raise
