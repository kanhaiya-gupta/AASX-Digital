"""
Physics Modeling Orchestration Service

This service provides main orchestration for the Physics Modeling module,
integrating existing components with new enterprise features and engine infrastructure.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import asyncio
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..models.physics_ml_registry import PhysicsMLRegistry
from ..models.physics_modeling_metrics import PhysicsModelingMetrics
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
from ..repositories.physics_ml_registry_repository import PhysicsMLRegistryRepository
from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository

logger = logging.getLogger(__name__)


class PhysicsModelingOrchestrationService:
    """
    Main orchestration service for Physics Modeling module
    
    Coordinates between existing components (plugins, simulation, solvers) and
    new enterprise features through the engine infrastructure.
    """
    
    def __init__(self):
        """Initialize the orchestration service"""
        self.registry_repo: Optional[PhysicsModelingRegistryRepository] = None
        self.ml_registry_repo: Optional[PhysicsMLRegistryRepository] = None
        self.metrics_repo: Optional[PhysicsModelingMetricsRepository] = None
        self.initialized = False
    
    async def initialize(self) -> None:
        """Async initialization of the service and repositories"""
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Initialize repositories
            self.registry_repo = PhysicsModelingRegistryRepository()
            self.ml_registry_repo = PhysicsMLRegistryRepository()
            self.metrics_repo = PhysicsModelingMetricsRepository()
            
            await self.registry_repo.initialize()
            await self.ml_registry_repo.initialize()
            await self.metrics_repo.initialize()
            
            self.initialized = True
            logger.info("Physics Modeling Orchestration Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestration service: {e}")
            raise
    
    async def register_physics_model(self, model_data: Dict[str, Any], user_id: str) -> Optional[str]:
        """
        Async register a new physics model
        
        Args:
            model_data: Model data dictionary
            user_id: ID of the user registering the model
            
        Returns:
            Created model ID or None if failed
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Create model instance
            model = PhysicsModelingRegistry(
                model_id=model_data.get('model_id'),
                model_name=model_data.get('model_name'),
                model_type=model_data.get('model_type'),
                physics_domain=model_data.get('physics_domain'),
                model_version=model_data.get('model_version', '1.0.0'),
                description=model_data.get('description'),
                parameters=model_data.get('parameters', {}),
                constraints=model_data.get('constraints', {}),
                mesh_config=model_data.get('mesh_config'),
                solver_config=model_data.get('solver_config'),
                created_by=user_id
            )
            
            # Validate model parameters
            if not await model.validate_model_parameters():
                logger.error(f"Invalid model parameters for model: {model.model_id}")
                return None
            
            # Create model in registry
            model_id = await self.registry_repo.create(model)
            
            if model_id:
                # Create initial metrics
                await self._create_model_metrics(model_id, "registration", user_id)
                logger.info(f"Physics model registered successfully: {model_id}")
                return model_id
            else:
                logger.error(f"Failed to create physics model in registry: {model.model_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to register physics model: {e}")
            return None
    
    async def register_ml_model(self, ml_model_data: Dict[str, Any], user_id: str) -> Optional[str]:
        """
        Async register a new ML model (PINN, etc.)
        
        Args:
            ml_model_data: ML model data dictionary
            user_id: ID of the user registering the ML model
            
        Returns:
            Created ML model ID or None if failed
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Create ML model instance
            ml_model = PhysicsMLRegistry(
                ml_model_id=ml_model_data.get('ml_model_id'),
                model_name=ml_model_data.get('model_name'),
                model_type=ml_model_data.get('model_type'),
                physics_domain=ml_model_data.get('physics_domain'),
                ml_framework=ml_model_data.get('ml_framework'),
                model_version=ml_model_data.get('model_version', '1.0.0'),
                description=ml_model_data.get('description'),
                architecture=ml_model_data.get('architecture', {}),
                hyperparameters=ml_model_data.get('hyperparameters', {}),
                loss_functions=ml_model_data.get('loss_functions', []),
                physics_constraints=ml_model_data.get('physics_constraints', []),
                conservation_laws=ml_model_data.get('conservation_laws', []),
                created_by=user_id
            )
            
            # Validate ML model architecture
            if not await ml_model.validate_ml_architecture():
                logger.error(f"Invalid ML model architecture for model: {ml_model.ml_model_id}")
                return None
            
            # Create ML model in registry
            ml_model_id = await self.ml_registry_repo.create(ml_model)
            
            if ml_model_id:
                # Create initial ML metrics
                await self._create_ml_model_metrics(ml_model_id, "registration", user_id)
                logger.info(f"ML model registered successfully: {ml_model_id}")
                return ml_model_id
            else:
                logger.error(f"Failed to create ML model in registry: {ml_model.ml_model_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to register ML model: {e}")
            return None
    
    async def update_model_status(self, model_id: str, new_status: str, user_id: str) -> bool:
        """
        Async update physics model status
        
        Args:
            model_id: ID of the model to update
            new_status: New status to set
            user_id: ID of the user updating the model
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Update model status
            updates = {
                'status': new_status,
                'updated_by': user_id,
                'updated_at': datetime.utcnow()
            }
            
            success = await self.registry_repo.update(model_id, updates)
            
            if success:
                # Create status change metric
                await self._create_model_metrics(model_id, "status_change", user_id, 
                                              {"old_status": "unknown", "new_status": new_status})
                logger.info(f"Model status updated successfully: {model_id} -> {new_status}")
                return True
            else:
                logger.error(f"Failed to update model status: {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update model status: {e}")
            return False
    
    async def update_ml_model_training_status(self, ml_model_id: str, training_status: str, 
                                           progress: float, user_id: str) -> bool:
        """
        Async update ML model training status
        
        Args:
            ml_model_id: ID of the ML model to update
            training_status: New training status
            progress: Training progress (0-1)
            user_id: ID of the user updating the ML model
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Update ML model training status
            updates = {
                'training_status': training_status,
                'training_progress': progress,
                'updated_by': user_id,
                'updated_at': datetime.utcnow()
            }
            
            success = await self.ml_registry_repo.update(ml_model_id, updates)
            
            if success:
                # Create training status metric
                await self._create_ml_model_metrics(ml_model_id, "training_status_change", user_id,
                                                 {"old_status": "unknown", "new_status": training_status, "progress": progress})
                logger.info(f"ML model training status updated successfully: {ml_model_id} -> {training_status}")
                return True
            else:
                logger.error(f"Failed to update ML model training status: {ml_model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update ML model training status: {e}")
            return False
    
    async def get_model_summary(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Async get comprehensive model summary
        
        Args:
            model_id: ID of the model to get summary for
            
        Returns:
            Model summary dictionary or None if failed
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get model from registry
            model = await self.registry_repo.get_by_id(model_id)
            if not model:
                return None
            
            # Get associated metrics
            metrics = await self.metrics_repo.get_by_model_id(model_id)
            
            # Calculate compliance score
            compliance_score = await model.calculate_compliance_score()
            
            # Prepare summary
            summary = {
                'model_info': model.to_dict(),
                'compliance_score': compliance_score,
                'metrics_count': len(metrics),
                'recent_metrics': [m.to_dict() for m in metrics[:5]],  # Last 5 metrics
                'status': model.status,
                'lifecycle_stage': model.lifecycle_stage
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get model summary: {e}")
            return None
    
    async def get_ml_model_summary(self, ml_model_id: str) -> Optional[Dict[str, Any]]:
        """
        Async get comprehensive ML model summary
        
        Args:
            ml_model_id: ID of the ML model to get summary for
            
        Returns:
            ML model summary dictionary or None if failed
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            # Get ML model from registry
            ml_model = await self.ml_registry_repo.get_by_id(ml_model_id)
            if not ml_model:
                return None
            
            # Get associated metrics
            metrics = await self.metrics_repo.get_by_ml_model_id(ml_model_id)
            
            # Calculate ML compliance score
            ml_compliance_score = await ml_model.calculate_ml_compliance_score()
            
            # Prepare summary
            summary = {
                'ml_model_info': ml_model.to_dict(),
                'ml_compliance_score': ml_compliance_score,
                'metrics_count': len(metrics),
                'recent_metrics': [m.to_dict() for m in metrics[:5]],  # Last 5 metrics
                'training_status': ml_model.training_status,
                'training_progress': ml_model.training_progress,
                'deployment_status': ml_model.deployment_status
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get ML model summary: {e}")
            return None
    
    async def _create_model_metrics(self, model_id: str, metric_type: str, user_id: str, 
                                  additional_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Async create metrics for physics model operations
        
        Args:
            model_id: ID of the physics model
            metric_type: Type of metric to create
            user_id: ID of the user performing the operation
            additional_data: Additional data for the metric
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            metric_data = {
                'metric_id': f"{metric_type}_{model_id}_{datetime.utcnow().timestamp()}",
                'metric_name': f"{metric_type.replace('_', ' ').title()}",
                'metric_type': 'operation',
                'metric_category': 'model_management',
                'metric_value': 1.0,
                'metric_unit': 'operation',
                'model_id': model_id,
                'created_by': user_id,
                'tags': [metric_type, 'model_operation'],
                'metadata': additional_data or {}
            }
            
            metric = PhysicsModelingMetrics(**metric_data)
            await self.metrics_repo.create(metric)
            
        except Exception as e:
            logger.error(f"Failed to create model metrics: {e}")
    
    async def _create_ml_model_metrics(self, ml_model_id: str, metric_type: str, user_id: str,
                                     additional_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Async create metrics for ML model operations
        
        Args:
            ml_model_id: ID of the ML model
            metric_type: Type of metric to create
            user_id: ID of the user performing the operation
            additional_data: Additional data for the metric
        """
        try:
            await asyncio.sleep(0)  # Ensure async context
            
            metric_data = {
                'metric_id': f"{metric_type}_{ml_model_id}_{datetime.utcnow().timestamp()}",
                'metric_name': f"{metric_type.replace('_', ' ').title()}",
                'metric_type': 'operation',
                'metric_category': 'ml_model_management',
                'metric_value': 1.0,
                'metric_unit': 'operation',
                'ml_model_id': ml_model_id,
                'created_by': user_id,
                'tags': [metric_type, 'ml_model_operation'],
                'metadata': additional_data or {}
            }
            
            metric = PhysicsModelingMetrics(**metric_data)
            await self.metrics_repo.create(metric)
            
        except Exception as e:
            logger.error(f"Failed to create ML model metrics: {e}")
    
    async def close(self) -> None:
        """Async cleanup of service and repositories"""
        try:
            if self.registry_repo:
                await self.registry_repo.close()
            if self.ml_registry_repo:
                await self.ml_registry_repo.close()
            if self.metrics_repo:
                await self.metrics_repo.close()
            
            logger.info("Physics Modeling Orchestration Service closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close orchestration service: {e}")
