"""
Model factory for physics modeling framework.

This module handles the creation of physics models from digital twins and plugins.
It integrates with the existing digital twin repository to access extracted data.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .dynamic_types import PhysicsPlugin, DynamicPhysicsType
from src.shared.models.digital_twin import DigitalTwin

logger = logging.getLogger(__name__)


class PhysicsModel:
    """
    Represents a physics model instance.
    
    This class encapsulates a physics model created from a digital twin
    and a specific physics plugin.
    """
    
    def __init__(self, model_id: str, twin_id: str, physics_type: str, 
                 plugin: PhysicsPlugin, parameters: Dict[str, Any], 
                 extracted_data: Dict[str, Any]):
        """
        Initialize a physics model.
        
        Args:
            model_id: Unique model identifier
            twin_id: Digital twin ID
            physics_type: Physics type identifier
            plugin: Physics plugin instance
            parameters: Model parameters
            extracted_data: Data extracted from ETL process
        """
        self.model_id = model_id
        self.twin_id = twin_id
        self.physics_type = physics_type
        self.plugin = plugin
        self.parameters = parameters
        self.extracted_data = extracted_data
        self.created_at = None
        self.status = "created"
        self.results = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'model_id': self.model_id,
            'twin_id': self.twin_id,
            'physics_type': self.physics_type,
            'parameters': self.parameters,
            'created_at': self.created_at,
            'status': self.status,
            'results': self.results
        }


class ModelFactory:
    """
    Factory for creating physics models from digital twins and plugins.
    
    This class handles:
    - Loading extracted data from digital twins
    - Creating model instances with plugins
    - Validating model parameters
    - Managing model lifecycle
    """
    
    def __init__(self, digital_twin_repository, plugin_manager, file_repository=None):
        """
        Initialize the model factory.
        
        Args:
            digital_twin_repository: Repository for digital twins
            plugin_manager: Plugin manager instance
            file_repository: Repository for files (for tracing)
        """
        self.digital_twin_repo = digital_twin_repository
        self.plugin_manager = plugin_manager
        self.file_repo = file_repository
        self.models: Dict[str, PhysicsModel] = {}
        
        logger.info("Model factory initialized")
    
    def create_model_from_twin(self, twin_id: str, physics_type: str, 
                              parameters: Dict[str, Any]) -> Optional[PhysicsModel]:
        """
        Create a physics model from a digital twin.
        
        Args:
            twin_id: Digital twin ID
            physics_type: Physics type identifier
            parameters: Model parameters
            
        Returns:
            Physics model instance or None if creation failed
        """
        try:
            # Get digital twin
            twin = self.digital_twin_repo.get_by_id(twin_id)
            if not twin:
                logger.error(f"Digital twin not found: {twin_id}")
                return None
            
            # Get plugin
            plugin = self.plugin_manager.get_plugin(physics_type)
            if not plugin:
                logger.error(f"Physics plugin not found: {physics_type}")
                return None
            
            # Load extracted data
            extracted_data = self._load_extracted_data(twin)
            if extracted_data is None:
                logger.error(f"Failed to load extracted data for twin: {twin_id}")
                return None
            
            # Get trace information (use case, project, file context)
            trace_info = self._get_trace_info(twin_id)
            if trace_info:
                # Enhance extracted data with trace information
                extracted_data['trace_info'] = {
                    'use_case_name': trace_info.get('use_case_name'),
                    'use_case_category': trace_info.get('use_case_category'),
                    'project_name': trace_info.get('project_name'),
                    'file_name': trace_info.get('filename'),
                    'original_filename': trace_info.get('original_filename')
                }
                logger.info(f"Added trace info for twin {twin_id}: {trace_info.get('use_case_name')} -> {trace_info.get('project_name')} -> {trace_info.get('filename')}")
            else:
                logger.warning(f"Could not get trace info for twin: {twin_id}")
            
            # Validate parameters
            validation_errors = plugin.validate_input(parameters)
            if validation_errors:
                logger.error(f"Parameter validation failed: {validation_errors}")
                return None
            
            # Create model ID
            model_id = f"{twin_id}_{physics_type}_{len(self.models)}"
            
            # Create model instance
            model = PhysicsModel(
                model_id=model_id,
                twin_id=twin_id,
                physics_type=physics_type,
                plugin=plugin,
                parameters=parameters,
                extracted_data=extracted_data
            )
            
            # Store model
            self.models[model_id] = model
            
            logger.info(f"Successfully created model: {model_id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            return None
    
    def get_model(self, model_id: str) -> Optional[PhysicsModel]:
        """
        Get a model by ID.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model instance or None if not found
        """
        return self.models.get(model_id)
    
    def get_models_by_twin(self, twin_id: str) -> Dict[str, PhysicsModel]:
        """
        Get all models for a digital twin.
        
        Args:
            twin_id: Digital twin ID
            
        Returns:
            Dictionary of model_id -> model instance
        """
        return {
            model_id: model 
            for model_id, model in self.models.items()
            if model.twin_id == twin_id
        }
    
    def get_models_by_physics_type(self, physics_type: str) -> Dict[str, PhysicsModel]:
        """
        Get all models for a physics type.
        
        Args:
            physics_type: Physics type identifier
            
        Returns:
            Dictionary of model_id -> model instance
        """
        return {
            model_id: model 
            for model_id, model in self.models.items()
            if model.physics_type == physics_type
        }
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model.
        
        Args:
            model_id: Model ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if model_id in self.models:
                del self.models[model_id]
                logger.info(f"Successfully deleted model: {model_id}")
                return True
            else:
                logger.warning(f"Model not found for deletion: {model_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete model {model_id}: {e}")
            return False
    
    def update_model_parameters(self, model_id: str, parameters: Dict[str, Any]) -> bool:
        """
        Update model parameters.
        
        Args:
            model_id: Model ID
            parameters: New parameters
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            model = self.get_model(model_id)
            if not model:
                logger.error(f"Model not found: {model_id}")
                return False
            
            # Validate new parameters
            validation_errors = model.plugin.validate_input(parameters)
            if validation_errors:
                logger.error(f"Parameter validation failed: {validation_errors}")
                return False
            
            # Update parameters
            model.parameters = parameters
            logger.info(f"Successfully updated parameters for model: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update model parameters: {e}")
            return False
    
    def _get_trace_info(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace information for a twin (file_id).
        
        Args:
            twin_id: Digital twin ID (equals file_id)
            
        Returns:
            Trace information dictionary or None if not found
        """
        try:
            if not self.file_repo:
                logger.warning("File repository not available for tracing")
                return None
            
            trace_info = self.file_repo.get_file_trace_info(twin_id)
            if trace_info:
                logger.debug(f"Retrieved trace info for twin {twin_id}: {trace_info.get('use_case_name')} -> {trace_info.get('project_name')}")
                return trace_info
            else:
                logger.warning(f"No trace info found for twin: {twin_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get trace info for twin {twin_id}: {e}")
            return None
    
    def _load_extracted_data(self, twin: DigitalTwin) -> Optional[Dict[str, Any]]:
        """
        Load extracted data from digital twin.
        
        Args:
            twin: Digital twin instance
            
        Returns:
            Extracted data dictionary or None if loading failed
        """
        try:
            if not twin.extracted_data_path:
                logger.warning(f"No extracted data path for twin: {twin.twin_id}")
                return {}
            
            # Check if path exists
            data_path = Path(twin.extracted_data_path)
            if not data_path.exists():
                logger.warning(f"Extracted data path does not exist: {twin.extracted_data_path}")
                return {}
            
            # Load data based on file type
            if data_path.suffix.lower() == '.json':
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif data_path.suffix.lower() in ['.yaml', '.yml']:
                import yaml
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            else:
                # Try to load as JSON first, then as text
                try:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = {'raw_content': f.read()}
            
            logger.info(f"Successfully loaded extracted data for twin: {twin.twin_id}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load extracted data for twin {twin.twin_id}: {e}")
            return None
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a model.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model information dictionary or None if not found
        """
        model = self.get_model(model_id)
        if not model:
            return None
        
        return {
            'model_id': model.model_id,
            'twin_id': model.twin_id,
            'physics_type': model.physics_type,
            'parameters': model.parameters,
            'created_at': model.created_at,
            'status': model.status,
            'plugin_info': model.plugin.get_metadata(),
            'extracted_data_keys': list(model.extracted_data.keys()) if model.extracted_data else []
        }
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """
        List all models with basic information.
        
        Returns:
            Dictionary of model_id -> model info
        """
        return {
            model_id: {
                'twin_id': model.twin_id,
                'physics_type': model.physics_type,
                'status': model.status,
                'created_at': model.created_at
            }
            for model_id, model in self.models.items()
        } 