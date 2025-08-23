"""
Local Trainer
============

Handle local model training for each twin.
"""

from typing import Dict, Any, List, Optional
import logging
import json
from pathlib import Path

from src.engine.services.core_system import RegistryService, MetricsService
from src.engine.database.connection_manager import ConnectionManager
from ..data_processing.feature_extractor import FeatureExtractor
from ..data_processing.training_data_preparer import TrainingDataPreparer

logger = logging.getLogger(__name__)

class LocalTrainer:
    """Local model training for individual twins"""
    
    def __init__(self, connection_manager: ConnectionManager, registry_service: RegistryService, metrics_service: MetricsService):
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.feature_extractor = FeatureExtractor()
        self.data_preparer = TrainingDataPreparer()
    
    async def load_twin_data(self, twin_id: str) -> Dict[str, Any]:
        """Load twin-specific training data"""
        try:
            logger.info(f"Loading training data for twin {twin_id}")
            
            # Get twin information from database using ConnectionManager
            twin_query = "SELECT * FROM twin_registry WHERE twin_id = ?"
            twin = await self.connection_manager.fetch_one(twin_query, (twin_id,))
            
            if not twin:
                raise ValueError(f"Twin {twin_id} not found")
            
            # Load AASX data from extracted_data_path
            if not twin.get('extracted_data_path'):
                raise ValueError(f"Twin {twin_id} has no extracted data path")
            
            data_path = Path(twin['extracted_data_path'])
            if not data_path.exists():
                raise ValueError(f"Extracted data path does not exist: {data_path}")
            
            # Load different data formats
            training_data = {}
            
            # Load JSON data
            json_file = data_path / f"{twin['name']}.json"
            if json_file.exists():
                with open(json_file, 'r') as f:
                    training_data['json'] = json.load(f)
            
            # Load Graph data
            graph_file = data_path / f"{twin['name']}_graph.json"
            if graph_file.exists():
                with open(graph_file, 'r') as f:
                    training_data['graph'] = json.load(f)
            
            # Load RDF data
            rdf_file = data_path / f"{twin['name']}.ttl"
            if rdf_file.exists():
                with open(rdf_file, 'r') as f:
                    training_data['rdf'] = f.read()
            
            # Extract features from loaded data
            features = self.feature_extractor.extract_features(training_data)
            
            # Prepare training data
            prepared_data = self.data_preparer.prepare_training_data(training_data, features)
            
            logger.info(f"Successfully loaded training data for twin {twin_id}")
            
            return {
                'twin_id': twin_id,
                'twin_name': twin['name'],
                'raw_data': training_data,
                'features': features,
                'prepared_data': prepared_data,
                'physics_context': twin.get('physics_context')
            }
            
        except Exception as e:
            logger.error(f"Error loading twin data for {twin_id}: {str(e)}")
            raise
    
    async def train_local_model(self, global_model: Dict[str, Any], twin_id: str) -> Dict[str, Any]:
        """Train local model and return updates"""
        try:
            logger.info(f"Training local model for twin {twin_id}")
            
            # Load twin data
            twin_data = await self.load_twin_data(twin_id)
            
            # Initialize local model (use global model as starting point)
            local_model = global_model.copy() if global_model else self._initialize_model()
            
            # Extract features for training
            features = twin_data['features']
            prepared_data = twin_data['prepared_data']
            
            # Perform local training (simplified for now)
            # In a real implementation, this would use actual ML libraries
            local_update = self._perform_local_training(local_model, features, prepared_data)
            
            # Add metadata
            local_update['twin_id'] = twin_id
            local_update['training_timestamp'] = self._get_current_timestamp()
            local_update['data_size'] = len(features)
            
            logger.info(f"Local training completed for twin {twin_id}")
            
            return local_update
            
        except Exception as e:
            logger.error(f"Error in local training for twin {twin_id}: {str(e)}")
            raise
    
    def apply_privacy_mechanisms(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential privacy and secure aggregation"""
        try:
            logger.info("Applying privacy mechanisms to updates")
            
            # Apply differential privacy (simplified implementation)
            private_updates = self._apply_differential_privacy(updates)
            
            # Apply secure aggregation preparation
            secure_updates = self._prepare_secure_aggregation(private_updates)
            
            logger.info("Privacy mechanisms applied successfully")
            
            return secure_updates
            
        except Exception as e:
            logger.error(f"Error applying privacy mechanisms: {str(e)}")
            raise
    
    def validate_updates(self, updates: Dict[str, Any]) -> bool:
        """Validate update quality and security"""
        try:
            logger.info("Validating updates")
            
            # Check if updates contain required fields
            required_fields = ['twin_id', 'model_parameters', 'training_timestamp']
            for field in required_fields:
                if field not in updates:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate model parameters
            if not self._validate_model_parameters(updates.get('model_parameters', {})):
                logger.error("Invalid model parameters")
                return False
            
            # Check for anomalies in updates
            if self._detect_anomalies(updates):
                logger.warning("Anomalies detected in updates")
                return False
            
            logger.info("Updates validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating updates: {str(e)}")
            return False
    
    def _initialize_model(self) -> Dict[str, Any]:
        """Initialize a new model"""
        return {
            'model_type': 'federated_model',
            'parameters': {},
            'version': '1.0.0',
            'initialized_at': self._get_current_timestamp()
        }
    
    def _perform_local_training(self, model: Dict[str, Any], features: List[float], data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform actual local training (placeholder implementation)"""
        # This is a simplified implementation
        # In a real system, this would use actual ML libraries like TensorFlow/PyTorch
        
        # Simulate training by updating model parameters
        updated_parameters = model.get('parameters', {}).copy()
        
        # Simple parameter update simulation
        for i, feature in enumerate(features[:10]):  # Limit to first 10 features
            param_key = f'param_{i}'
            updated_parameters[param_key] = feature * 0.1  # Simple update rule
        
        return {
            'model_parameters': updated_parameters,
            'training_metrics': {
                'loss': 0.5,  # Simulated loss
                'accuracy': 0.85,  # Simulated accuracy
                'epochs': 5
            },
            'model_type': model.get('model_type', 'federated_model'),
            'version': model.get('version', '1.0.0')
        }
    
    def _apply_differential_privacy(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential privacy to updates"""
        # Simplified differential privacy implementation
        import random
        
        private_updates = updates.copy()
        parameters = private_updates.get('model_parameters', {})
        
        # Add noise to parameters
        noise_scale = 0.01
        for key, value in parameters.items():
            if isinstance(value, (int, float)):
                noise = random.gauss(0, noise_scale)
                parameters[key] = value + noise
        
        private_updates['privacy_applied'] = True
        private_updates['noise_scale'] = noise_scale
        
        return private_updates
    
    def _prepare_secure_aggregation(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare updates for secure aggregation"""
        # Simplified secure aggregation preparation
        secure_updates = updates.copy()
        
        # Add encryption metadata (placeholder)
        secure_updates['encryption'] = {
            'method': 'homomorphic_encryption',
            'key_id': 'placeholder_key',
            'encrypted': False  # Would be True in real implementation
        }
        
        return secure_updates
    
    def _validate_model_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate model parameters"""
        if not isinstance(parameters, dict):
            return False
        
        # Check for reasonable parameter values
        for key, value in parameters.items():
            if isinstance(value, (int, float)):
                if abs(value) > 1000:  # Reasonable range check
                    return False
        
        return True
    
    def _detect_anomalies(self, updates: Dict[str, Any]) -> bool:
        """Detect anomalies in updates"""
        # Simplified anomaly detection
        parameters = updates.get('model_parameters', {})
        
        # Check for extreme values
        for key, value in parameters.items():
            if isinstance(value, (int, float)):
                if abs(value) > 100:  # Threshold for anomaly
                    return True
        
        return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.now().isoformat() 