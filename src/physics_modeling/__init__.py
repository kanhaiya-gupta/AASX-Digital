"""
Physics Modeling Framework

A comprehensive framework for physics-based modeling and simulation,
integrating with digital twins and AI/RAG systems for enhanced insights.

This package provides:
- Core physics modeling components (materials, geometry, boundary conditions)
- Integration with digital twins and AI/RAG systems
- Real-world use cases and examples
- Multi-physics simulation capabilities
"""

from .core import PhysicsModel, Material, Geometry, BoundaryConditions
from .integration import TwinConnector, AIRAGConnector, RealTimeConnector
from .use_cases import (
    ThermalAnalysisUseCases,
    StructuralAnalysisUseCases,
    FluidDynamicsUseCases,
    MultiPhysicsUseCases,
    IndustrialUseCases
)

class PhysicsModelingFramework:
    """
    Main integration class for physics modeling framework
    
    This class provides a unified interface for creating, managing, and
    analyzing physics-based models with integration to digital twins
    and AI/RAG systems.
    """
    
    def __init__(self):
        """Initialize the physics modeling framework"""
        self.core_components = {
            'physics_model': PhysicsModel,
            'material': Material,
            'geometry': Geometry,
            'boundary_conditions': BoundaryConditions
        }
        
        self.integration_components = {
            'twin_connector': TwinConnector,
            'ai_rag_connector': AIRAGConnector,
            'realtime_connector': RealTimeConnector
        }
        
        self.use_cases = {
            'thermal': ThermalAnalysisUseCases,
            'structural': StructuralAnalysisUseCases,
            'fluid_dynamics': FluidDynamicsUseCases,
            'multi_physics': MultiPhysicsUseCases,
            'industrial': IndustrialUseCases
        }
    
    def get_available_use_cases(self) -> dict:
        """Get all available use cases organized by category"""
        use_case_categories = {}
        
        for category, use_case_class in self.use_cases.items():
            use_case_categories[category] = use_case_class.get_all_use_cases()
        
        return use_case_categories
    
    def get_use_case_by_name(self, name: str) -> dict:
        """Get a specific use case by name across all categories"""
        for category, use_case_class in self.use_cases.items():
            try:
                return use_case_class.get_use_case_by_name(name)
            except ValueError:
                continue
        raise ValueError(f"Use case '{name}' not found in any category")
    
    def get_use_cases_by_industry(self, industry: str) -> list:
        """Get all use cases for a specific industry"""
        matching_use_cases = []
        
        for category, use_case_class in self.use_cases.items():
            use_cases = use_case_class.get_all_use_cases()
            for use_case in use_cases:
                if use_case.get('industry', '').lower() == industry.lower():
                    matching_use_cases.append(use_case)
        
        return matching_use_cases
    
    def get_use_cases_by_physics_type(self, physics_type: str) -> list:
        """Get all use cases for a specific physics type"""
        matching_use_cases = []
        
        for category, use_case_class in self.use_cases.items():
            use_cases = use_case_class.get_all_use_cases()
            for use_case in use_cases:
                if use_case.get('physics_focus', '').lower().find(physics_type.lower()) != -1:
                    matching_use_cases.append(use_case)
        
        return matching_use_cases
    
    def create_model_from_use_case(self, use_case_name: str) -> PhysicsModel:
        """Create a physics model from a predefined use case"""
        use_case = self.get_use_case_by_name(use_case_name)
        
        # Create physics model with use case data
        model = PhysicsModel(
            name=use_case['name'],
            physics_type=use_case.get('physics_focus', 'multi_physics'),
            description=use_case['description']
        )
        
        # Add materials from use case
        for material_name, material_data in use_case.get('materials', {}).items():
            model.add_material(material_name, material_data)
        
        # Add geometry from use case
        for geometry_name, geometry_data in use_case.get('geometry', {}).items():
            model.add_geometry(geometry_name, geometry_data)
        
        # Add boundary conditions from use case
        if 'boundary_conditions' in use_case:
            model.set_boundary_conditions(use_case['boundary_conditions'])
        
        return model
    
    def get_famous_examples(self) -> dict:
        """Get famous examples organized by industry"""
        famous_examples = {}
        
        for category, use_case_class in self.use_cases.items():
            use_cases = use_case_class.get_all_use_cases()
            for use_case in use_cases:
                industry = use_case.get('industry', 'Other')
                if industry not in famous_examples:
                    famous_examples[industry] = []
                
                examples = use_case.get('famous_examples', [])
                famous_examples[industry].extend(examples)
        
        # Remove duplicates
        for industry in famous_examples:
            famous_examples[industry] = list(set(famous_examples[industry]))
        
        return famous_examples
    
    def get_optimization_targets(self) -> dict:
        """Get optimization targets organized by category"""
        optimization_targets = {}
        
        for category, use_case_class in self.use_cases.items():
            use_cases = use_case_class.get_all_use_cases()
            for use_case in use_cases:
                targets = use_case.get('optimization_targets', [])
                if targets:
                    optimization_targets[use_case['name']] = targets
        
        return optimization_targets

# Version information
__version__ = "1.0.0"
__author__ = "Physics Modeling Team"
__description__ = "Comprehensive physics-based modeling framework with real-world use cases"

# Export main classes and functions
__all__ = [
    'PhysicsModelingFramework',
    'PhysicsModel',
    'Material',
    'Geometry', 
    'BoundaryConditions',
    'TwinConnector',
    'AIRAGConnector',
    'RealTimeConnector',
    'ThermalAnalysisUseCases',
    'StructuralAnalysisUseCases',
    'FluidDynamicsUseCases',
    'MultiPhysicsUseCases',
    'IndustrialUseCases'
]