"""
Use Case Template System

This module provides template-based use case creation and management
for the physics modeling framework.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json

from ..core.dynamic_types import DynamicPhysicsType


class UseCaseTemplate:
    """
    Template system for creating standardized use cases.
    
    This class provides template-based use case creation with
    predefined configurations and parameter sets.
    """
    
    def __init__(self):
        """Initialize the use case template system."""
        self.logger = logging.getLogger(__name__)
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """Load default use case templates."""
        default_templates = {
            'thermal_analysis': {
                'name': 'Thermal Analysis',
                'description': 'Standard thermal analysis template',
                'physics_type_id': 'thermal_heat_transfer',
                'parameters': {
                    'temperature': 298.15,
                    'heat_flux': 1000.0,
                    'material': 'steel',
                    'geometry': 'rectangular'
                },
                'metadata': {
                    'category': 'thermal',
                    'complexity': 'basic',
                    'solver': 'finite_difference'
                }
            },
            'structural_analysis': {
                'name': 'Structural Analysis',
                'description': 'Standard structural analysis template',
                'physics_type_id': 'structural_static',
                'parameters': {
                    'load': 1000.0,
                    'material': 'aluminum',
                    'geometry': 'beam',
                    'boundary_conditions': 'fixed_ends'
                },
                'metadata': {
                    'category': 'structural',
                    'complexity': 'basic',
                    'solver': 'finite_element'
                }
            },
            'fluid_analysis': {
                'name': 'Fluid Analysis',
                'description': 'Standard fluid analysis template',
                'physics_type_id': 'fluid_incompressible',
                'parameters': {
                    'velocity': 10.0,
                    'viscosity': 1.0e-3,
                    'density': 1000.0,
                    'geometry': 'pipe'
                },
                'metadata': {
                    'category': 'fluid',
                    'complexity': 'basic',
                    'solver': 'finite_volume'
                }
            }
        }
        
        for template_id, template_data in default_templates.items():
            self.register_template(template_id, template_data)
    
    def register_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """
        Register a new use case template.
        
        Args:
            template_id: Template identifier
            template_data: Template configuration data
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            required_fields = ['name', 'physics_type_id', 'parameters']
            for field in required_fields:
                if field not in template_data:
                    self.logger.error(f"Template missing required field: {field}")
                    return False
            
            self.templates[template_id] = template_data.copy()
            self.logger.info(f"Registered template: {template_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering template: {str(e)}")
            return False
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template data or None if not found
        """
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates.
        
        Returns:
            List of template information dictionaries
        """
        return [
            {
                'template_id': template_id,
                **template_data
            }
            for template_id, template_data in self.templates.items()
        ]
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get templates by category.
        
        Args:
            category: Template category
            
        Returns:
            List of templates in the specified category
        """
        return [
            {
                'template_id': template_id,
                **template_data
            }
            for template_id, template_data in self.templates.items()
            if template_data.get('metadata', {}).get('category') == category
        ]
    
    def create_use_case_from_template(self, template_id: str, use_case_id: str,
                                     parameter_overrides: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a use case from a template.
        
        Args:
            template_id: Template identifier
            use_case_id: Use case identifier
            parameter_overrides: Parameters to override from template
            
        Returns:
            Use case configuration or None if creation failed
        """
        try:
            template = self.get_template(template_id)
            if not template:
                self.logger.error(f"Template not found: {template_id}")
                return None
            
            # Start with template parameters
            parameters = template['parameters'].copy()
            
            # Apply overrides
            if parameter_overrides:
                parameters.update(parameter_overrides)
            
            use_case = {
                'use_case_id': use_case_id,
                'template_id': template_id,
                'physics_type_id': template['physics_type_id'],
                'parameters': parameters,
                'metadata': template.get('metadata', {}).copy(),
                'created_at': datetime.now().isoformat(),
                'status': 'created'
            }
            
            self.logger.info(f"Created use case from template: {use_case_id}")
            return use_case
            
        except Exception as e:
            self.logger.error(f"Error creating use case from template: {str(e)}")
            return None
    
    def export_template(self, template_id: str) -> Optional[str]:
        """
        Export a template to JSON format.
        
        Args:
            template_id: Template identifier
            
        Returns:
            JSON string representation or None if export failed
        """
        try:
            template = self.get_template(template_id)
            if not template:
                return None
            
            return json.dumps(template, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error exporting template: {str(e)}")
            return None
    
    def import_template(self, template_id: str, template_json: str) -> bool:
        """
        Import a template from JSON format.
        
        Args:
            template_id: Template identifier
            template_json: JSON string representation
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            template_data = json.loads(template_json)
            return self.register_template(template_id, template_data)
            
        except Exception as e:
            self.logger.error(f"Error importing template: {str(e)}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if template_id in self.templates:
            del self.templates[template_id]
            self.logger.info(f"Deleted template: {template_id}")
            return True
        return False 