"""
Dynamic Use Case Engine

This module provides dynamic use case management capabilities for the
physics modeling framework, including use case creation, execution,
and lifecycle management.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from ..core.dynamic_types import DynamicPhysicsType
from ..core.model_factory import DynamicModelFactory


class DynamicUseCaseEngine:
    """
    Engine for managing and executing dynamic use cases.
    
    This class provides capabilities for creating, configuring, and
    executing physics modeling use cases in a dynamic manner.
    """
    
    def __init__(self, model_factory: Optional[DynamicModelFactory] = None):
        """
        Initialize the dynamic use case engine.
        
        Args:
            model_factory: Model factory instance (optional)
        """
        self.model_factory = model_factory or DynamicModelFactory()
        self.logger = logging.getLogger(__name__)
        self.use_cases: Dict[str, Dict[str, Any]] = {}
        
    def create_use_case(self, use_case_id: str, physics_type_id: str, 
                       parameters: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new use case.
        
        Args:
            use_case_id: Unique identifier for the use case
            physics_type_id: Physics type identifier
            parameters: Use case parameters
            metadata: Additional metadata
            
        Returns:
            True if creation was successful, False otherwise
        """
        try:
            # Validate physics type exists
            if not self.model_factory.get_available_physics_types():
                self.logger.error(f"Physics type not found: {physics_type_id}")
                return False
                
            use_case = {
                'use_case_id': use_case_id,
                'physics_type_id': physics_type_id,
                'parameters': parameters,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'status': 'created'
            }
            
            self.use_cases[use_case_id] = use_case
            self.logger.info(f"Created use case: {use_case_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating use case: {str(e)}")
            return False
    
    def execute_use_case(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """
        Execute a use case.
        
        Args:
            use_case_id: Use case identifier
            
        Returns:
            Execution results or None if execution failed
        """
        try:
            if use_case_id not in self.use_cases:
                self.logger.error(f"Use case not found: {use_case_id}")
                return None
                
            use_case = self.use_cases[use_case_id]
            physics_type_id = use_case['physics_type_id']
            parameters = use_case['parameters']
            
            # Create and execute model
            model = self.model_factory.create_model(physics_type_id, parameters)
            if not model:
                self.logger.error(f"Failed to create model for use case: {use_case_id}")
                return None
                
            results = model.solve()
            
            # Update use case status
            use_case['status'] = 'completed'
            use_case['results'] = results
            use_case['completed_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Executed use case: {use_case_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error executing use case {use_case_id}: {str(e)}")
            return None
    
    def get_use_case(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get use case information.
        
        Args:
            use_case_id: Use case identifier
            
        Returns:
            Use case information or None if not found
        """
        return self.use_cases.get(use_case_id)
    
    def list_use_cases(self) -> List[Dict[str, Any]]:
        """
        List all use cases.
        
        Returns:
            List of use case information dictionaries
        """
        return list(self.use_cases.values())
    
    def delete_use_case(self, use_case_id: str) -> bool:
        """
        Delete a use case.
        
        Args:
            use_case_id: Use case identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if use_case_id in self.use_cases:
            del self.use_cases[use_case_id]
            self.logger.info(f"Deleted use case: {use_case_id}")
            return True
        return False 