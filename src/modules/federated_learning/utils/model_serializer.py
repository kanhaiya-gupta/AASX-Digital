"""
Model Serializer
===============

Utility for model serialization and deserialization.
"""

from typing import Dict, Any, Optional
import logging
import json
import pickle
import base64
import gzip

logger = logging.getLogger(__name__)

class ModelSerializer:
    """Utility for model serialization and deserialization"""
    
    def __init__(self):
        self.logger = logger
    
    def serialize_model(self, model: Dict[str, Any], format: str = "json") -> str:
        """Serialize model to string"""
        try:
            if format == "json":
                return self._serialize_to_json(model)
            elif format == "pickle":
                return self._serialize_to_pickle(model)
            elif format == "compressed":
                return self._serialize_compressed(model)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error serializing model: {str(e)}")
            raise
    
    def deserialize_model(self, serialized_model: str, format: str = "json") -> Dict[str, Any]:
        """Deserialize model from string"""
        try:
            if format == "json":
                return self._deserialize_from_json(serialized_model)
            elif format == "pickle":
                return self._deserialize_from_pickle(serialized_model)
            elif format == "compressed":
                return self._deserialize_compressed(serialized_model)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error deserializing model: {str(e)}")
            raise
    
    def _serialize_to_json(self, model: Dict[str, Any]) -> str:
        """Serialize model to JSON string"""
        try:
            return json.dumps(model, default=self._json_serializer)
        except Exception as e:
            self.logger.error(f"Error serializing to JSON: {str(e)}")
            raise
    
    def _deserialize_from_json(self, serialized_model: str) -> Dict[str, Any]:
        """Deserialize model from JSON string"""
        try:
            return json.loads(serialized_model)
        except Exception as e:
            self.logger.error(f"Error deserializing from JSON: {str(e)}")
            raise
    
    def _serialize_to_pickle(self, model: Dict[str, Any]) -> str:
        """Serialize model to pickle string"""
        try:
            pickled = pickle.dumps(model)
            return base64.b64encode(pickled).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error serializing to pickle: {str(e)}")
            raise
    
    def _deserialize_from_pickle(self, serialized_model: str) -> Dict[str, Any]:
        """Deserialize model from pickle string"""
        try:
            pickled = base64.b64decode(serialized_model.encode('utf-8'))
            return pickle.loads(pickled)
        except Exception as e:
            self.logger.error(f"Error deserializing from pickle: {str(e)}")
            raise
    
    def _serialize_compressed(self, model: Dict[str, Any]) -> str:
        """Serialize model with compression"""
        try:
            json_str = json.dumps(model, default=self._json_serializer)
            compressed = gzip.compress(json_str.encode('utf-8'))
            return base64.b64encode(compressed).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error serializing compressed: {str(e)}")
            raise
    
    def _deserialize_compressed(self, serialized_model: str) -> Dict[str, Any]:
        """Deserialize compressed model"""
        try:
            compressed = base64.b64decode(serialized_model.encode('utf-8'))
            json_str = gzip.decompress(compressed).decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error deserializing compressed: {str(e)}")
            raise
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-serializable objects"""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        else:
            return str(obj)
    
    def get_serialization_info(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about model serialization"""
        try:
            info = {}
            
            # JSON serialization info
            json_str = self._serialize_to_json(model)
            info['json_size'] = len(json_str)
            info['json_compression_ratio'] = 1.0
            
            # Pickle serialization info
            pickle_str = self._serialize_to_pickle(model)
            info['pickle_size'] = len(pickle_str)
            
            # Compressed serialization info
            compressed_str = self._serialize_compressed(model)
            info['compressed_size'] = len(compressed_str)
            info['compression_ratio'] = len(json_str) / len(compressed_str) if len(compressed_str) > 0 else 1.0
            
            # Model structure info
            info['model_keys'] = list(model.keys())
            info['parameter_count'] = self._count_parameters(model)
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting serialization info: {str(e)}")
            return {}
    
    def _count_parameters(self, model: Dict[str, Any]) -> int:
        """Count parameters in model"""
        try:
            count = 0
            
            for key, value in model.items():
                if isinstance(value, dict):
                    count += self._count_parameters(value)
                elif isinstance(value, list):
                    count += len(value)
                elif isinstance(value, (int, float)):
                    count += 1
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error counting parameters: {str(e)}")
            return 0
    
    def validate_serialization(self, model: Dict[str, Any]) -> bool:
        """Validate that model can be serialized and deserialized correctly"""
        try:
            # Test JSON serialization
            json_str = self._serialize_to_json(model)
            json_model = self._deserialize_from_json(json_str)
            
            # Test pickle serialization
            pickle_str = self._serialize_to_pickle(model)
            pickle_model = self._deserialize_from_pickle(pickle_str)
            
            # Test compressed serialization
            compressed_str = self._serialize_compressed(model)
            compressed_model = self._deserialize_compressed(compressed_str)
            
            # Compare models
            if not self._compare_models(model, json_model):
                self.logger.warning("JSON serialization validation failed")
                return False
            
            if not self._compare_models(model, pickle_model):
                self.logger.warning("Pickle serialization validation failed")
                return False
            
            if not self._compare_models(model, compressed_model):
                self.logger.warning("Compressed serialization validation failed")
                return False
            
            self.logger.info("Serialization validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating serialization: {str(e)}")
            return False
    
    def _compare_models(self, model1: Dict[str, Any], model2: Dict[str, Any]) -> bool:
        """Compare two models for equality"""
        try:
            return json.dumps(model1, sort_keys=True) == json.dumps(model2, sort_keys=True)
        except Exception as e:
            self.logger.error(f"Error comparing models: {str(e)}")
            return False 