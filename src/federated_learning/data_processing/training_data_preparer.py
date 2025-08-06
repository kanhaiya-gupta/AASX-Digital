"""
Training Data Preparer
=====================

Prepare training data for federated learning.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)

class TrainingDataPreparer:
    """Prepare training data for federated learning"""
    
    def __init__(self):
        self.logger = logger
    
    def prepare_training_data(self, raw_data: Dict[str, Any], features: List[float]) -> Dict[str, Any]:
        """Prepare training data from raw data and extracted features"""
        try:
            self.logger.info("Preparing training data")
            
            # Normalize features
            normalized_features = self._normalize_features(features)
            
            # Create training samples
            training_samples = self._create_training_samples(raw_data, normalized_features)
            
            # Split into train/validation sets
            train_data, val_data = self._split_data(training_samples)
            
            # Create training data structure
            training_data = {
                'features': normalized_features,
                'training_samples': train_data,
                'validation_samples': val_data,
                'feature_names': self._generate_feature_names(len(features)),
                'data_metadata': self._extract_data_metadata(raw_data)
            }
            
            self.logger.info(f"Prepared training data with {len(train_data)} training samples and {len(val_data)} validation samples")
            
            return training_data
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {str(e)}")
            return {}
    
    def _normalize_features(self, features: List[float]) -> List[float]:
        """Normalize features to [0, 1] range"""
        try:
            if not features:
                return []
            
            features_array = np.array(features)
            
            # Handle constant features
            if np.std(features_array) == 0:
                return [0.5] * len(features)
            
            # Min-max normalization
            min_val = np.min(features_array)
            max_val = np.max(features_array)
            
            if max_val == min_val:
                return [0.5] * len(features)
            
            normalized = (features_array - min_val) / (max_val - min_val)
            
            return normalized.tolist()
            
        except Exception as e:
            self.logger.error(f"Error normalizing features: {str(e)}")
            return features
    
    def _create_training_samples(self, raw_data: Dict[str, Any], features: List[float]) -> List[Dict[str, Any]]:
        """Create training samples from raw data and features"""
        try:
            samples = []
            
            # Create a single sample for now (can be extended for multiple samples)
            sample = {
                'features': features,
                'target': self._extract_target(raw_data),
                'metadata': {
                    'data_type': self._determine_data_type(raw_data),
                    'feature_count': len(features),
                    'sample_id': self._generate_sample_id()
                }
            }
            
            samples.append(sample)
            
            return samples
            
        except Exception as e:
            self.logger.error(f"Error creating training samples: {str(e)}")
            return []
    
    def _extract_target(self, raw_data: Dict[str, Any]) -> float:
        """Extract target value from raw data"""
        try:
            # This is a simplified target extraction
            # In a real implementation, this would extract the actual target variable
            
            # For now, use a synthetic target based on data complexity
            target = 0.5  # Default target
            
            if 'json' in raw_data:
                json_data = raw_data['json']
                if isinstance(json_data, dict):
                    # Use number of keys as a simple complexity measure
                    target = min(1.0, len(json_data) / 100.0)
            
            return target
            
        except Exception as e:
            self.logger.error(f"Error extracting target: {str(e)}")
            return 0.5
    
    def _determine_data_type(self, raw_data: Dict[str, Any]) -> str:
        """Determine the type of data"""
        if 'json' in raw_data:
            return 'json'
        elif 'graph' in raw_data:
            return 'graph'
        elif 'rdf' in raw_data:
            return 'rdf'
        else:
            return 'unknown'
    
    def _generate_sample_id(self) -> str:
        """Generate a unique sample ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _split_data(self, samples: List[Dict[str, Any]], train_ratio: float = 0.8) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Split data into training and validation sets"""
        try:
            if not samples:
                return [], []
            
            # Shuffle samples
            shuffled_samples = samples.copy()
            np.random.shuffle(shuffled_samples)
            
            # Calculate split point
            split_idx = int(len(shuffled_samples) * train_ratio)
            
            train_data = shuffled_samples[:split_idx]
            val_data = shuffled_samples[split_idx:]
            
            return train_data, val_data
            
        except Exception as e:
            self.logger.error(f"Error splitting data: {str(e)}")
            return samples, []
    
    def _generate_feature_names(self, feature_count: int) -> List[str]:
        """Generate feature names"""
        return [f'feature_{i}' for i in range(feature_count)]
    
    def _extract_data_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from raw data"""
        metadata = {
            'data_sources': list(raw_data.keys()),
            'total_size': self._calculate_data_size(raw_data),
            'data_types': {}
        }
        
        for key, value in raw_data.items():
            if isinstance(value, dict):
                metadata['data_types'][key] = 'dict'
            elif isinstance(value, list):
                metadata['data_types'][key] = 'list'
            elif isinstance(value, str):
                metadata['data_types'][key] = 'string'
            else:
                metadata['data_types'][key] = type(value).__name__
        
        return metadata
    
    def _calculate_data_size(self, raw_data: Dict[str, Any]) -> int:
        """Calculate approximate data size"""
        try:
            import json
            return len(json.dumps(raw_data))
        except:
            return 0 