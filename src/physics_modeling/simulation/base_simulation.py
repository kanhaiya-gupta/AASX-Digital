"""
Base simulation class for physics modeling framework.

This module provides the base simulation class that all plugins can extend
to get common preprocessing, postprocessing, and validation capabilities.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseSimulation:
    """
    Common simulation infrastructure for all plugins.
    
    This class provides shared functionality that all physics simulations can use:
    - Data preprocessing
    - Result postprocessing
    - Result validation
    - Common utilities
    """
    
    def __init__(self, model_data: Dict[str, Any], parameters: Dict[str, Any]):
        """
        Initialize the base simulation.
        
        Args:
            model_data: Extracted data from ETL process
            parameters: Simulation parameters
        """
        self.model_data = model_data
        self.parameters = parameters
        self.results: Dict[str, Any] = {}
        self.preprocessed_data: Optional[Dict[str, Any]] = None
        self.postprocessed_results: Optional[Dict[str, Any]] = None
        self.validation_errors: List[str] = []
        self.simulation_start_time = datetime.now()
        self.simulation_end_time: Optional[datetime] = None
        
        logger.debug(f"Base simulation initialized with {len(model_data)} data items and {len(parameters)} parameters")
    
    def preprocess(self) -> Dict[str, Any]:
        """
        Common preprocessing for all simulations.
        
        This method performs standard preprocessing steps that are common
        across all physics simulations.
        
        Returns:
            Preprocessed data
        """
        try:
            logger.debug("Starting preprocessing")
            
            # Initialize preprocessed data
            self.preprocessed_data = {
                'original_data': self.model_data.copy(),
                'original_parameters': self.parameters.copy(),
                'preprocessing_timestamp': datetime.now().isoformat(),
                'data_summary': self._summarize_data(),
                'parameter_summary': self._summarize_parameters()
            }
            
            # Perform common preprocessing steps
            self._validate_data_structure()
            self._normalize_parameters()
            self._extract_common_entities()
            self._prepare_coordinate_systems()
            
            logger.debug("Preprocessing completed successfully")
            return self.preprocessed_data
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            self.validation_errors.append(f"Preprocessing error: {str(e)}")
            return {}
    
    def postprocess(self) -> Dict[str, Any]:
        """
        Common postprocessing for all simulations.
        
        This method performs standard postprocessing steps that are common
        across all physics simulations.
        
        Returns:
            Postprocessed results
        """
        try:
            logger.debug("Starting postprocessing")
            
            # Initialize postprocessed results
            self.postprocessed_results = {
                'original_results': self.results.copy(),
                'postprocessing_timestamp': datetime.now().isoformat(),
                'simulation_duration': self._calculate_duration(),
                'result_summary': self._summarize_results()
            }
            
            # Perform common postprocessing steps
            self._validate_results()
            self._add_metadata()
            self._format_results()
            self._calculate_statistics()
            
            logger.debug("Postprocessing completed successfully")
            return self.postprocessed_results
            
        except Exception as e:
            logger.error(f"Postprocessing failed: {e}")
            self.validation_errors.append(f"Postprocessing error: {str(e)}")
            return {}
    
    def validate_results(self) -> bool:
        """
        Common result validation.
        
        This method performs standard validation checks that are common
        across all physics simulations.
        
        Returns:
            True if validation passed, False otherwise
        """
        try:
            logger.debug("Starting result validation")
            
            # Clear previous validation errors
            self.validation_errors.clear()
            
            # Perform common validation checks
            self._check_result_structure()
            self._check_numerical_validity()
            self._check_physical_constraints()
            self._check_convergence()
            
            is_valid = len(self.validation_errors) == 0
            
            if is_valid:
                logger.debug("Result validation passed")
            else:
                logger.warning(f"Result validation failed with {len(self.validation_errors)} errors")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Result validation failed: {e}")
            self.validation_errors.append(f"Validation error: {str(e)}")
            return False
    
    def get_validation_errors(self) -> List[str]:
        """
        Get validation errors.
        
        Returns:
            List of validation error messages
        """
        return self.validation_errors.copy()
    
    def get_simulation_duration(self) -> Optional[float]:
        """
        Get simulation duration in seconds.
        
        Returns:
            Duration in seconds or None if simulation not completed
        """
        if self.simulation_end_time:
            return (self.simulation_end_time - self.simulation_start_time).total_seconds()
        return None
    
    def mark_completed(self):
        """Mark simulation as completed."""
        self.simulation_end_time = datetime.now()
    
    def _summarize_data(self) -> Dict[str, Any]:
        """Summarize the input data."""
        summary = {
            'total_items': len(self.model_data),
            'data_types': {},
            'key_items': list(self.model_data.keys())[:10]  # First 10 keys
        }
        
        # Count data types
        for key, value in self.model_data.items():
            data_type = type(value).__name__
            summary['data_types'][data_type] = summary['data_types'].get(data_type, 0) + 1
        
        return summary
    
    def _summarize_parameters(self) -> Dict[str, Any]:
        """Summarize the input parameters."""
        summary = {
            'total_parameters': len(self.parameters),
            'parameter_types': {},
            'parameter_names': list(self.parameters.keys())
        }
        
        # Count parameter types
        for key, value in self.parameters.items():
            param_type = type(value).__name__
            summary['parameter_types'][param_type] = summary['parameter_types'].get(param_type, 0) + 1
        
        return summary
    
    def _summarize_results(self) -> Dict[str, Any]:
        """Summarize the simulation results."""
        summary = {
            'total_results': len(self.results),
            'result_types': {},
            'result_names': list(self.results.keys())
        }
        
        # Count result types
        for key, value in self.results.items():
            result_type = type(value).__name__
            summary['result_types'][result_type] = summary['result_types'].get(result_type, 0) + 1
        
        return summary
    
    def _validate_data_structure(self):
        """Validate the structure of input data."""
        if not isinstance(self.model_data, dict):
            self.validation_errors.append("Model data must be a dictionary")
        
        if not isinstance(self.parameters, dict):
            self.validation_errors.append("Parameters must be a dictionary")
    
    def _normalize_parameters(self):
        """Normalize parameter values."""
        # Convert string numbers to actual numbers
        for key, value in self.parameters.items():
            if isinstance(value, str):
                try:
                    # Try to convert to float
                    float_value = float(value)
                    self.parameters[key] = float_value
                except ValueError:
                    # Keep as string if conversion fails
                    pass
    
    def _extract_common_entities(self):
        """Extract common entities from data."""
        # Look for common physics entities
        common_entities = ['geometry', 'materials', 'boundary_conditions', 'mesh']
        
        for entity in common_entities:
            if entity in self.model_data:
                self.preprocessed_data[f'extracted_{entity}'] = self.model_data[entity]
    
    def _prepare_coordinate_systems(self):
        """Prepare coordinate systems for simulation."""
        # Common coordinate system preparation
        if 'geometry' in self.model_data:
            geometry = self.model_data['geometry']
            if isinstance(geometry, dict):
                # Extract coordinate system information
                self.preprocessed_data['coordinate_system'] = {
                    'type': geometry.get('coordinate_system', 'cartesian'),
                    'units': geometry.get('units', 'meters')
                }
    
    def _check_result_structure(self):
        """Check the structure of results."""
        if not isinstance(self.results, dict):
            self.validation_errors.append("Results must be a dictionary")
            return
        
        if len(self.results) == 0:
            self.validation_errors.append("Results cannot be empty")
    
    def _check_numerical_validity(self):
        """Check numerical validity of results."""
        for key, value in self.results.items():
            if isinstance(value, (int, float)):
                # Check for NaN or infinite values
                if str(value).lower() in ['nan', 'inf', '-inf']:
                    self.validation_errors.append(f"Invalid numerical value in result '{key}': {value}")
    
    def _check_physical_constraints(self):
        """Check physical constraints of results."""
        # This is a basic implementation - plugins can override for specific constraints
        pass
    
    def _check_convergence(self):
        """Check convergence of simulation results."""
        # This is a basic implementation - plugins can override for specific convergence criteria
        pass
    
    def _add_metadata(self):
        """Add metadata to results."""
        self.postprocessed_results['metadata'] = {
            'simulation_type': 'physics_modeling',
            'framework_version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'validation_errors': self.validation_errors.copy()
        }
    
    def _format_results(self):
        """Format results for consistency."""
        # Ensure all numerical results have consistent precision
        for key, value in self.results.items():
            if isinstance(value, float):
                self.results[key] = round(value, 6)  # 6 decimal places
    
    def _calculate_statistics(self):
        """Calculate basic statistics for results."""
        numerical_results = {}
        
        for key, value in self.results.items():
            if isinstance(value, (int, float)):
                numerical_results[key] = value
        
        if numerical_results:
            values = list(numerical_results.values())
            self.postprocessed_results['statistics'] = {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': sum(values) / len(values)
            }
    
    def _calculate_duration(self) -> Optional[float]:
        """Calculate simulation duration."""
        if self.simulation_end_time:
            return (self.simulation_end_time - self.simulation_start_time).total_seconds()
        return None 