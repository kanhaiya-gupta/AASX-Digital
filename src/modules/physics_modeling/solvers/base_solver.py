"""
Base solver for physics modeling framework.

This module provides the base solver interface that users can extend
to create custom solver plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseSolver(ABC):
    """
    Abstract base class for physics solvers.
    
    All solver plugins must extend this class and implement the required methods.
    This provides a common interface for different solver algorithms.
    """
    
    def __init__(self):
        """Initialize the solver."""
        self.solver_name = self.__class__.__name__
        self.solver_version = "1.0.0"
        self.supported_physics_types = []
        self.solver_parameters = {}
        
        logger.debug(f"Solver {self.solver_name} initialized")
    
    @abstractmethod
    def solve(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a physics problem using this solver.
        
        This is the main method that users implement to perform their
        specific solver calculations.
        
        Args:
            model_data: Model data and parameters
            
        Returns:
            Dictionary containing solver results
        """
        pass
    
    def validate_input(self, model_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate input data for the solver.
        
        Args:
            model_data: Model data to validate
            
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Basic validation - subclasses can override for specific validation
        if not isinstance(model_data, dict):
            errors['model_data'] = "Model data must be a dictionary"
        
        return errors
    
    def get_solver_info(self) -> Dict[str, Any]:
        """
        Get information about the solver.
        
        Returns:
            Solver information dictionary
        """
        return {
            'solver_name': self.solver_name,
            'solver_version': self.solver_version,
            'supported_physics_types': self.supported_physics_types,
            'solver_parameters': self.solver_parameters,
            'class_name': self.__class__.__name__,
            'module_name': self.__class__.__module__
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Set solver parameters.
        
        Args:
            parameters: Solver parameters
            
        Returns:
            True if parameters set successfully, False otherwise
        """
        try:
            self.solver_parameters.update(parameters)
            logger.debug(f"Parameters set for solver {self.solver_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to set parameters for solver {self.solver_name}: {e}")
            return False
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current solver parameters.
        
        Returns:
            Current solver parameters
        """
        return self.solver_parameters.copy()
    
    def supports_physics_type(self, physics_type: str) -> bool:
        """
        Check if solver supports a specific physics type.
        
        Args:
            physics_type: Physics type to check
            
        Returns:
            True if supported, False otherwise
        """
        return physics_type in self.supported_physics_types
    
    def preprocess(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess model data before solving.
        
        Args:
            model_data: Model data to preprocess
            
        Returns:
            Preprocessed model data
        """
        # Default implementation returns data as-is
        # Subclasses can override for specific preprocessing
        return model_data
    
    def postprocess(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess solver results.
        
        Args:
            results: Raw solver results
            
        Returns:
            Postprocessed results
        """
        # Default implementation returns results as-is
        # Subclasses can override for specific postprocessing
        return results 