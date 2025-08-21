"""
Digital Twin Connector for Physics Modeling

This module provides integration between physics modeling and the digital twin
registry, enabling physics models to be created from digital twin data.
"""

import logging
from typing import Dict, Any, Optional, List
import json
import os

logger = logging.getLogger(__name__)

class TwinConnector:
    """
    Connector for integrating physics modeling with digital twin registry
    """
    
    def __init__(self, twin_registry=None):
        """
        Initialize twin connector
        
        Args:
            twin_registry: Digital twin registry instance
        """
        self.twin_registry = twin_registry
        logger.info("Initialized TwinConnector for physics modeling")
    
    def get_twin_data(self, twin_id: str) -> Dict[str, Any]:
        """
        Get digital twin data for physics modeling
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            Dict containing twin data
        """
        try:
            if self.twin_registry:
                # Use actual twin registry if available
                twin_data = self.twin_registry.get_twin(twin_id)
            else:
                # Fallback to file-based approach
                twin_data = self._load_twin_from_file(twin_id)
            
            logger.info(f"Retrieved twin data for {twin_id}")
            return twin_data
            
        except Exception as e:
            logger.error(f"Failed to get twin data for {twin_id}: {str(e)}")
            return {}
    
    def _load_twin_from_file(self, twin_id: str) -> Dict[str, Any]:
        """
        Load twin data from file system (fallback method)
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            Dict containing twin data
        """
        # Look for twin data in common locations
        possible_paths = [
            f"output/projects/{twin_id}/twin_data.json",
            f"data/projects/{twin_id}/twin_data.json",
            f"aas-processor/output/structured_data_minimal/{twin_id}/twin_data.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        twin_data = json.load(f)
                    logger.info(f"Loaded twin data from {path}")
                    return twin_data
                except Exception as e:
                    logger.warning(f"Failed to load twin data from {path}: {str(e)}")
        
        # Return default structure if no file found
        logger.warning(f"No twin data file found for {twin_id}, using default structure")
        return self._create_default_twin_structure(twin_id)
    
    def _create_default_twin_structure(self, twin_id: str) -> Dict[str, Any]:
        """
        Create default twin structure for physics modeling
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            Default twin data structure
        """
        return {
            'twin_id': twin_id,
            'metadata': {
                'ai_insights': {
                    'raw_data_files': [],
                    'processed_content': {},
                    'quality_metrics': {}
                }
            },
            'properties': {},
            'submodels': [],
            'relationships': []
        }
    
    def get_raw_data_files(self, twin_id: str) -> List[Dict[str, Any]]:
        """
        Get raw data files associated with a digital twin
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            List of raw data file information
        """
        twin_data = self.get_twin_data(twin_id)
        raw_files = twin_data.get('metadata', {}).get('ai_insights', {}).get('raw_data_files', [])
        
        logger.info(f"Found {len(raw_files)} raw data files for twin {twin_id}")
        return raw_files
    
    def get_asset_properties(self, twin_id: str) -> Dict[str, Any]:
        """
        Get asset properties from digital twin
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            Asset properties dictionary
        """
        twin_data = self.get_twin_data(twin_id)
        properties = twin_data.get('properties', {})
        
        logger.info(f"Retrieved {len(properties)} properties for twin {twin_id}")
        return properties
    
    def get_submodels(self, twin_id: str) -> List[Dict[str, Any]]:
        """
        Get submodels from digital twin
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            List of submodels
        """
        twin_data = self.get_twin_data(twin_id)
        submodels = twin_data.get('submodels', [])
        
        logger.info(f"Retrieved {len(submodels)} submodels for twin {twin_id}")
        return submodels
    
    def get_relationships(self, twin_id: str) -> List[Dict[str, Any]]:
        """
        Get relationships from digital twin
        
        Args:
            twin_id: Digital twin identifier
            
        Returns:
            List of relationships
        """
        twin_data = self.get_twin_data(twin_id)
        relationships = twin_data.get('relationships', [])
        
        logger.info(f"Retrieved {len(relationships)} relationships for twin {twin_id}")
        return relationships
    
    def update_twin_physics_results(self, twin_id: str, physics_results: Dict[str, Any]):
        """
        Update digital twin with physics simulation results
        
        Args:
            twin_id: Digital twin identifier
            physics_results: Physics simulation results
        """
        try:
            if self.twin_registry:
                # Update actual twin registry
                self.twin_registry.update_twin_physics_results(twin_id, physics_results)
            else:
                # Save to file system
                self._save_physics_results_to_file(twin_id, physics_results)
            
            logger.info(f"Updated twin {twin_id} with physics results")
            
        except Exception as e:
            logger.error(f"Failed to update twin {twin_id} with physics results: {str(e)}")
    
    def _save_physics_results_to_file(self, twin_id: str, physics_results: Dict[str, Any]):
        """
        Save physics results to file system
        
        Args:
            twin_id: Digital twin identifier
            physics_results: Physics simulation results
        """
        # Create output directory
        output_dir = f"output/physics_results/{twin_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save results
        output_file = f"{output_dir}/physics_results.json"
        with open(output_file, 'w') as f:
            json.dump(physics_results, f, indent=2)
        
        logger.info(f"Saved physics results to {output_file}")
    
    def get_physics_model_config(self, twin_id: str, model_type: str) -> Dict[str, Any]:
        """
        Get physics model configuration from digital twin
        
        Args:
            twin_id: Digital twin identifier
            model_type: Type of physics model
            
        Returns:
            Physics model configuration
        """
        twin_data = self.get_twin_data(twin_id)
        
        # Extract relevant data for physics modeling
        config = {
            'twin_id': twin_id,
            'model_type': model_type,
            'asset_properties': twin_data.get('properties', {}),
            'raw_data_files': twin_data.get('metadata', {}).get('ai_insights', {}).get('raw_data_files', []),
            'submodels': twin_data.get('submodels', []),
            'relationships': twin_data.get('relationships', [])
        }
        
        # Add model-specific configuration
        if model_type == "thermal":
            config.update(self._get_thermal_model_config(twin_data))
        elif model_type == "structural":
            config.update(self._get_structural_model_config(twin_data))
        elif model_type == "fluid":
            config.update(self._get_fluid_model_config(twin_data))
        
        logger.info(f"Generated physics model config for {twin_id} ({model_type})")
        return config
    
    def _get_thermal_model_config(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get thermal model specific configuration"""
        return {
            'thermal_properties': {
                'thermal_conductivity': twin_data.get('properties', {}).get('thermal_conductivity', 50.0),
                'heat_capacity': twin_data.get('properties', {}).get('heat_capacity', 500.0),
                'density': twin_data.get('properties', {}).get('density', 7850.0)
            },
            'boundary_conditions': {
                'temperature': twin_data.get('properties', {}).get('operating_temperature', 25.0),
                'heat_flux': twin_data.get('properties', {}).get('heat_flux', 0.0)
            }
        }
    
    def _get_structural_model_config(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get structural model specific configuration"""
        return {
            'mechanical_properties': {
                'youngs_modulus': twin_data.get('properties', {}).get('youngs_modulus', 200e9),
                'poissons_ratio': twin_data.get('properties', {}).get('poissons_ratio', 0.3),
                'density': twin_data.get('properties', {}).get('density', 7850.0)
            },
            'boundary_conditions': {
                'loads': twin_data.get('properties', {}).get('applied_loads', {}),
                'constraints': twin_data.get('properties', {}).get('constraints', {})
            }
        }
    
    def _get_fluid_model_config(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fluid model specific configuration"""
        return {
            'fluid_properties': {
                'viscosity': twin_data.get('properties', {}).get('viscosity', 1e-3),
                'density': twin_data.get('properties', {}).get('density', 1000.0),
                'thermal_expansion': twin_data.get('properties', {}).get('thermal_expansion', 2.1e-4)
            },
            'boundary_conditions': {
                'inlet_velocity': twin_data.get('properties', {}).get('inlet_velocity', 1.0),
                'outlet_pressure': twin_data.get('properties', {}).get('outlet_pressure', 101325.0)
            }
        }
    
    def list_available_twins(self) -> List[str]:
        """
        List available digital twins
        
        Returns:
            List of twin identifiers
        """
        if self.twin_registry:
            return self.twin_registry.list_twins()
        else:
            return self._list_twins_from_filesystem()
    
    def _list_twins_from_filesystem(self) -> List[str]:
        """List twins from file system"""
        twin_ids = []
        
        # Check common twin data locations
        possible_dirs = [
            "output/projects",
            "data/projects", 
            "aas-processor/output/structured_data_minimal"
        ]
        
        for base_dir in possible_dirs:
            if os.path.exists(base_dir):
                for item in os.listdir(base_dir):
                    item_path = os.path.join(base_dir, item)
                    if os.path.isdir(item_path):
                        twin_ids.append(item)
        
        logger.info(f"Found {len(twin_ids)} twins in filesystem")
        return list(set(twin_ids))  # Remove duplicates