"""
Data Preprocessor
================

Data preprocessing utilities for federated learning.
Handles data cleaning, normalization, and preparation.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class PreprocessingConfig:
    """Configuration for data preprocessing"""
    # Data cleaning
    remove_missing_values: bool = True
    missing_value_strategy: str = "drop"  # drop, fill_mean, fill_median, fill_mode
    outlier_detection: bool = True
    outlier_threshold: float = 3.0  # Standard deviations for outlier detection
    
    # Normalization
    normalize_features: bool = True
    normalization_method: str = "standard"  # standard, minmax, robust
    feature_scaling: bool = True
    
    # Feature engineering
    create_polynomial_features: bool = False
    polynomial_degree: int = 2
    create_interaction_features: bool = False
    
    # Data splitting
    train_test_split: bool = True
    test_size: float = 0.2
    validation_size: float = 0.1
    random_state: int = 42


@dataclass
class PreprocessingMetrics:
    """Metrics for data preprocessing performance"""
    # Data statistics
    original_samples: int = 0
    processed_samples: int = 0
    removed_samples: int = 0
    missing_values_filled: int = 0
    outliers_removed: int = 0
    
    # Feature statistics
    original_features: int = 0
    processed_features: int = 0
    created_features: int = 0
    
    # Performance metrics
    preprocessing_time: float = 0.0
    memory_usage_mb: float = 0.0
    data_quality_score: float = 0.0


class DataPreprocessor:
    """Data preprocessing implementation for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[PreprocessingConfig] = None
    ):
        """Initialize Data Preprocessor"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or PreprocessingConfig()
        
        # Preprocessing state
        self.is_processing = False
        self.current_dataset = None
        self.preprocessing_history: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = PreprocessingMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
    
    async def preprocess_dataset(
        self,
        dataset: Union[np.ndarray, List[List[float]], Dict[str, Any]],
        dataset_name: str = "unknown"
    ) -> Dict[str, Any]:
        """Preprocess a dataset for federated learning"""
        try:
            self.start_time = datetime.now()
            self.is_processing = True
            self.current_dataset = dataset_name
            
            print(f"🔄 Starting data preprocessing for: {dataset_name}")
            
            # Convert dataset to numpy array if needed
            data_array = await self._prepare_data_array(dataset)
            
            # Update metrics
            self.metrics.original_samples = data_array.shape[0]
            self.metrics.original_features = data_array.shape[1]
            
            # Data cleaning
            cleaned_data = await self._clean_data(data_array)
            
            # Feature engineering
            engineered_data = await self._engineer_features(cleaned_data)
            
            # Normalization
            normalized_data = await self._normalize_features(engineered_data)
            
            # Data splitting
            split_data = await self._split_data(normalized_data)
            
            # Update final metrics
            self.metrics.processed_samples = normalized_data.shape[0]
            self.metrics.processed_features = normalized_data.shape[1]
            self.metrics.removed_samples = self.metrics.original_samples - self.metrics.processed_samples
            self.metrics.created_features = self.metrics.processed_features - self.metrics.original_features
            
            # Calculate processing time
            processing_time = (datetime.now() - self.start_time).total_seconds()
            self.metrics.preprocessing_time = processing_time
            
            # Calculate data quality score
            self.metrics.data_quality_score = await self._calculate_data_quality_score(normalized_data)
            
            # Record preprocessing history
            self.preprocessing_history.append({
                'dataset_name': dataset_name,
                'timestamp': datetime.now().isoformat(),
                'metrics': self.metrics.__dict__,
                'config': self.config.__dict__
            })
            
            print(f"✅ Data preprocessing completed in {processing_time:.2f}s")
            
            return {
                'status': 'success',
                'dataset_name': dataset_name,
                'processed_data': split_data,
                'metrics': self.metrics.__dict__,
                'processing_time': processing_time
            }
            
        except Exception as e:
            print(f"❌ Data preprocessing failed: {e}")
            return {'status': 'failed', 'error': str(e)}
        finally:
            self.is_processing = False
    
    async def _prepare_data_array(
        self,
        dataset: Union[np.ndarray, List[List[float]], Dict[str, Any]]
    ) -> np.ndarray:
        """Prepare dataset as numpy array"""
        try:
            if isinstance(dataset, np.ndarray):
                return dataset
            elif isinstance(dataset, list):
                return np.array(dataset)
            elif isinstance(dataset, dict):
                # Handle dictionary format
                if 'data' in dataset:
                    return np.array(dataset['data'])
                elif 'features' in dataset:
                    return np.array(dataset['features'])
                else:
                    # Convert dict values to array
                    return np.array(list(dataset.values()))
            else:
                raise ValueError(f"Unsupported dataset type: {type(dataset)}")
                
        except Exception as e:
            print(f"❌ Data array preparation failed: {e}")
            raise
    
    async def _clean_data(self, data: np.ndarray) -> np.ndarray:
        """Clean the dataset by handling missing values and outliers"""
        try:
            cleaned_data = data.copy()
            
            # Handle missing values
            if self.config.remove_missing_values:
                cleaned_data = await self._handle_missing_values(cleaned_data)
            
            # Remove outliers
            if self.config.outlier_detection:
                cleaned_data = await self._remove_outliers(cleaned_data)
            
            return cleaned_data
            
        except Exception as e:
            print(f"❌ Data cleaning failed: {e}")
            raise
    
    async def _handle_missing_values(self, data: np.ndarray) -> np.ndarray:
        """Handle missing values in the dataset"""
        try:
            if self.config.missing_value_strategy == "drop":
                # Remove rows with any missing values
                mask = ~np.isnan(data).any(axis=1)
                cleaned_data = data[mask]
                self.metrics.removed_samples += (len(data) - len(cleaned_data))
                
            elif self.config.missing_value_strategy == "fill_mean":
                # Fill missing values with column means
                cleaned_data = data.copy()
                for col in range(data.shape[1]):
                    col_data = data[:, col]
                    mean_val = np.nanmean(col_data)
                    cleaned_data[np.isnan(col_data), col] = mean_val
                    self.metrics.missing_values_filled += np.isnan(col_data).sum()
                
            elif self.config.missing_value_strategy == "fill_median":
                # Fill missing values with column medians
                cleaned_data = data.copy()
                for col in range(data.shape[1]):
                    col_data = data[:, col]
                    median_val = np.nanmedian(col_data)
                    cleaned_data[np.isnan(col_data), col] = median_val
                    self.metrics.missing_values_filled += np.isnan(col_data).sum()
                
            elif self.config.missing_value_strategy == "fill_mode":
                # Fill missing values with column modes
                cleaned_data = data.copy()
                for col in range(data.shape[1]):
                    col_data = data[:, col]
                    mode_val = self._calculate_mode(col_data)
                    cleaned_data[np.isnan(col_data), col] = mode_val
                    self.metrics.missing_values_filled += np.isnan(col_data).sum()
            
            return cleaned_data
            
        except Exception as e:
            print(f"❌ Missing value handling failed: {e}")
            return data
    
    async def _remove_outliers(self, data: np.ndarray) -> np.ndarray:
        """Remove outliers using statistical methods"""
        try:
            cleaned_data = data.copy()
            outlier_mask = np.zeros(len(data), dtype=bool)
            
            for col in range(data.shape[1]):
                col_data = data[:, col]
                
                # Calculate z-scores
                mean_val = np.nanmean(col_data)
                std_val = np.nanstd(col_data)
                
                if std_val > 0:
                    z_scores = np.abs((col_data - mean_val) / std_val)
                    col_outliers = z_scores > self.config.outlier_threshold
                    outlier_mask |= col_outliers
            
            # Remove outlier rows
            cleaned_data = data[~outlier_mask]
            self.metrics.outliers_removed += outlier_mask.sum()
            
            return cleaned_data
            
        except Exception as e:
            print(f"❌ Outlier removal failed: {e}")
            return data
    
    async def _engineer_features(self, data: np.ndarray) -> np.ndarray:
        """Engineer new features from existing data"""
        try:
            engineered_data = data.copy()
            
            # Create polynomial features
            if self.config.create_polynomial_features:
                engineered_data = await self._create_polynomial_features(engineered_data)
            
            # Create interaction features
            if self.config.create_interaction_features:
                engineered_data = await self._create_interaction_features(engineered_data)
            
            return engineered_data
            
        except Exception as e:
            print(f"❌ Feature engineering failed: {e}")
            return data
    
    async def _create_polynomial_features(self, data: np.ndarray) -> np.ndarray:
        """Create polynomial features"""
        try:
            if self.config.polynomial_degree < 2:
                return data
            
            n_samples, n_features = data.shape
            poly_features = []
            
            # Original features
            poly_features.append(data)
            
            # Quadratic features
            if self.config.polynomial_degree >= 2:
                for i in range(n_features):
                    for j in range(i, n_features):
                        if i == j:
                            # Square terms
                            poly_features.append(data[:, i:i+1] ** 2)
                        else:
                            # Interaction terms
                            poly_features.append((data[:, i:i+1] * data[:, j:j+1]))
            
            # Cubic features (if degree >= 3)
            if self.config.polynomial_degree >= 3:
                for i in range(n_features):
                    for j in range(i, n_features):
                        for k in range(j, n_features):
                            if i == j == k:
                                # Cube terms
                                poly_features.append(data[:, i:i+1] ** 3)
                            elif i == j:
                                # Square * linear terms
                                poly_features.append((data[:, i:i+1] ** 2) * data[:, k:k+1])
                            elif j == k:
                                # Linear * square terms
                                poly_features.append(data[:, i:i+1] * (data[:, j:j+1] ** 2))
                            else:
                                # Triple interaction terms
                                poly_features.append(data[:, i:i+1] * data[:, j:j+1] * data[:, k:k+1])
            
            return np.hstack(poly_features)
            
        except Exception as e:
            print(f"❌ Polynomial feature creation failed: {e}")
            return data
    
    async def _create_interaction_features(self, data: np.ndarray) -> np.ndarray:
        """Create interaction features between variables"""
        try:
            n_samples, n_features = data.shape
            interaction_features = []
            
            # Create pairwise interactions
            for i in range(n_features):
                for j in range(i + 1, n_features):
                    interaction = data[:, i:i+1] * data[:, j:j+1]
                    interaction_features.append(interaction)
            
            if interaction_features:
                return np.hstack([data] + interaction_features)
            else:
                return data
                
        except Exception as e:
            print(f"❌ Interaction feature creation failed: {e}")
            return data
    
    async def _normalize_features(self, data: np.ndarray) -> np.ndarray:
        """Normalize features using specified method"""
        try:
            if not self.config.normalize_features:
                return data
            
            normalized_data = data.copy()
            
            if self.config.normalization_method == "standard":
                # Standard scaling (z-score normalization)
                for col in range(data.shape[1]):
                    col_data = data[:, col]
                    mean_val = np.nanmean(col_data)
                    std_val = np.nanstd(col_data)
                    if std_val > 0:
                        normalized_data[:, col] = (col_data - mean_val) / std_val
                
            elif self.config.normalization_method == "minmax":
                # Min-max scaling to [0, 1]
                for col in range(data.shape[1]):
                    col_data = data[:, col]
                    min_val = np.nanmin(col_data)
                    max_val = np.nanmax(col_data)
                    if max_val > min_val:
                        normalized_data[:, col] = (col_data - min_val) / (max_val - min_val)
                
            elif self.config.normalization_method == "robust":
                # Robust scaling using median and IQR
                for col in range(data.shape[1]):
                    col_data = data[:, col]
                    median_val = np.nanmedian(col_data)
                    q75 = np.nanpercentile(col_data, 75)
                    q25 = np.nanpercentile(col_data, 25)
                    iqr = q75 - q25
                    if iqr > 0:
                        normalized_data[:, col] = (col_data - median_val) / iqr
            
            return normalized_data
            
        except Exception as e:
            print(f"❌ Feature normalization failed: {e}")
            return data
    
    async def _split_data(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Split data into train, validation, and test sets"""
        try:
            if not self.config.train_test_split:
                return {'data': data}
            
            n_samples = len(data)
            
            # Calculate split indices
            test_size = int(n_samples * self.config.test_size)
            val_size = int(n_samples * self.config.validation_size)
            train_size = n_samples - test_size - val_size
            
            # Set random seed for reproducibility
            np.random.seed(self.config.random_state)
            
            # Shuffle indices
            indices = np.random.permutation(n_samples)
            
            # Split data
            train_indices = indices[:train_size]
            val_indices = indices[train_size:train_size + val_size]
            test_indices = indices[train_size + val_size:]
            
            return {
                'train': data[train_indices],
                'validation': data[val_indices],
                'test': data[test_indices],
                'train_indices': train_indices,
                'val_indices': val_indices,
                'test_indices': test_indices
            }
            
        except Exception as e:
            print(f"❌ Data splitting failed: {e}")
            return {'data': data}
    
    async def _calculate_data_quality_score(self, data: np.ndarray) -> float:
        """Calculate overall data quality score"""
        try:
            if len(data) == 0:
                return 0.0
            
            # Calculate various quality metrics
            completeness = 1.0 - np.isnan(data).sum() / data.size
            consistency = 1.0 - np.isinf(data).sum() / data.size
            
            # Calculate feature variance (higher is better for ML)
            feature_vars = np.var(data, axis=0)
            variance_score = np.mean(feature_vars) / (1.0 + np.mean(feature_vars))
            
            # Calculate correlation score (lower is better to avoid multicollinearity)
            corr_matrix = np.corrcoef(data.T)
            np.fill_diagonal(corr_matrix, 0)
            correlation_score = 1.0 - np.mean(np.abs(corr_matrix))
            
            # Combine scores
            quality_score = (
                0.3 * completeness +
                0.2 * consistency +
                0.3 * variance_score +
                0.2 * correlation_score
            )
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            print(f"⚠️  Data quality score calculation failed: {e}")
            return 0.5
    
    def _calculate_mode(self, data: np.ndarray) -> float:
        """Calculate mode of a numeric array"""
        try:
            # Remove NaN values
            clean_data = data[~np.isnan(data)]
            if len(clean_data) == 0:
                return 0.0
            
            # Find most frequent value
            unique_values, counts = np.unique(clean_data, return_counts=True)
            mode_index = np.argmax(counts)
            return float(unique_values[mode_index])
            
        except Exception as e:
            print(f"⚠️  Mode calculation failed: {e}")
            return 0.0
    
    async def get_preprocessing_report(self) -> Dict[str, Any]:
        """Get comprehensive preprocessing report"""
        try:
            return {
                'preprocessing_metrics': self.metrics.__dict__,
                'preprocessing_history': self.preprocessing_history,
                'current_config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Preprocessing report generation failed: {e}")
            return {'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'DataPreprocessor',
            'is_processing': self.is_processing,
            'current_dataset': self.current_dataset,
            'metrics': self.metrics.__dict__,
            'config': self.config.__dict__
        }
    
    async def reset_preprocessor(self):
        """Reset preprocessor state and metrics"""
        self.is_processing = False
        self.current_dataset = None
        self.preprocessing_history.clear()
        self.metrics = PreprocessingMetrics()
        self.start_time = None
        
        print("🔄 Data Preprocessor reset")
