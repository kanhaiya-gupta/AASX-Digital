"""
Data Preprocessor for Physics Modeling
Handles data cleaning, normalization, and preparation for simulations
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PreprocessingConfig:
    """Configuration for data preprocessing"""
    normalize_data: bool = True
    remove_outliers: bool = True
    outlier_threshold: float = 3.0
    fill_missing: bool = True
    fill_strategy: str = "interpolate"  # "interpolate", "mean", "median", "zero"
    scale_features: bool = True
    scale_method: str = "standard"  # "standard", "minmax", "robust"
    validate_physics_constraints: bool = True
    max_missing_ratio: float = 0.1

class DataPreprocessor:
    """Data preprocessing for physics modeling simulations"""
    
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()
        self.preprocessing_history = []
        self.data_statistics = {}
        self.validation_results = {}
        logger.info("✅ Data Preprocessor initialized")
    
    async def preprocess_data(self, data: Union[np.ndarray, pd.DataFrame, Dict[str, Any]], 
                            data_type: str = "simulation") -> Dict[str, Any]:
        """Main preprocessing pipeline"""
        await asyncio.sleep(0)
        
        start_time = datetime.now()
        logger.info(f"🔄 Starting data preprocessing for {data_type}")
        
        try:
            # Convert to standardized format
            processed_data = await self._standardize_data_format(data)
            
            # Clean data
            cleaned_data = await self._clean_data(processed_data)
            
            # Validate physics constraints
            if self.config.validate_physics_constraints:
                validation_result = await self._validate_physics_constraints(cleaned_data, data_type)
                self.validation_results[data_type] = validation_result
            
            # Normalize if required
            if self.config.normalize_data:
                normalized_data = await self._normalize_data(cleaned_data)
            else:
                normalized_data = cleaned_data
            
            # Scale features if required
            if self.config.scale_features:
                scaled_data = await self._scale_features(normalized_data)
            else:
                scaled_data = normalized_data
            
            # Final validation
            final_validation = await self._final_validation(scaled_data, data_type)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'processed_data': scaled_data,
                'preprocessing_config': self.config.__dict__,
                'processing_time': processing_time,
                'data_statistics': self.data_statistics.get(data_type, {}),
                'validation_results': self.validation_results.get(data_type, {}),
                'final_validation': final_validation,
                'success': True
            }
            
            # Record preprocessing history
            self.preprocessing_history.append({
                'timestamp': datetime.now(),
                'data_type': data_type,
                'config': self.config.__dict__,
                'processing_time': processing_time,
                'success': True
            })
            
            logger.info(f"✅ Data preprocessing completed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Data preprocessing failed: {str(e)}")
            
            self.preprocessing_history.append({
                'timestamp': datetime.now(),
                'data_type': data_type,
                'config': self.config.__dict__,
                'processing_time': processing_time,
                'success': False,
                'error': str(e)
            })
            
            return {
                'success': False,
                'error': str(e),
                'processing_time': processing_time
            }
    
    async def _standardize_data_format(self, data: Union[np.ndarray, pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
        """Convert data to standardized format"""
        await asyncio.sleep(0)
        
        if isinstance(data, np.ndarray):
            return {
                'data': data,
                'format': 'numpy_array',
                'shape': data.shape,
                'dtype': str(data.dtype)
            }
        elif isinstance(data, pd.DataFrame):
            return {
                'data': data.values,
                'columns': data.columns.tolist(),
                'index': data.index.tolist(),
                'format': 'pandas_dataframe',
                'shape': data.shape,
                'dtype': str(data.dtypes)
            }
        elif isinstance(data, dict):
            return {
                'data': data,
                'format': 'dictionary',
                'keys': list(data.keys())
            }
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    async def _clean_data(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the data by handling missing values and outliers"""
        await asyncio.sleep(0)
        
        data = data_dict['data']
        original_shape = data.shape
        
        # Handle missing values
        if self.config.fill_missing:
            data = await self._fill_missing_values(data)
        
        # Remove outliers
        if self.config.remove_outliers:
            data = await self._remove_outliers(data)
        
        # Update data dictionary
        data_dict['data'] = data
        data_dict['cleaned_shape'] = data.shape
        data_dict['cleaning_info'] = {
            'original_shape': original_shape,
            'final_shape': data.shape,
            'missing_values_filled': self.config.fill_missing,
            'outliers_removed': self.config.remove_outliers
        }
        
        return data_dict
    
    async def _fill_missing_values(self, data: np.ndarray) -> np.ndarray:
        """Fill missing values using specified strategy"""
        await asyncio.sleep(0)
        
        if not np.isnan(data).any():
            return data
        
        if self.config.fill_strategy == "interpolate":
            # Linear interpolation along each dimension
            filled_data = data.copy()
            for i in range(data.shape[0]):
                if np.isnan(filled_data[i]).any():
                    valid_mask = ~np.isnan(filled_data[i])
                    if valid_mask.sum() > 1:
                        filled_data[i] = np.interp(
                            np.arange(len(filled_data[i])),
                            np.arange(len(filled_data[i]))[valid_mask],
                            filled_data[i][valid_mask]
                        )
            return filled_data
        
        elif self.config.fill_strategy == "mean":
            return np.where(np.isnan(data), np.nanmean(data), data)
        
        elif self.config.fill_strategy == "median":
            return np.where(np.isnan(data), np.nanmedian(data), data)
        
        elif self.config.fill_strategy == "zero":
            return np.where(np.isnan(data), 0.0, data)
        
        else:
            return data
    
    async def _remove_outliers(self, data: np.ndarray) -> np.ndarray:
        """Remove outliers using statistical methods"""
        await asyncio.sleep(0)
        
        if data.size == 0:
            return data
        
        # Calculate z-scores
        mean = np.nanmean(data)
        std = np.nanstd(data)
        
        if std == 0:
            return data
        
        z_scores = np.abs((data - mean) / std)
        outlier_mask = z_scores > self.config.outlier_threshold
        
        # Replace outliers with mean
        cleaned_data = data.copy()
        cleaned_data[outlier_mask] = mean
        
        return cleaned_data
    
    async def _validate_physics_constraints(self, data_dict: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Validate data against physics constraints"""
        await asyncio.sleep(0)
        
        data = data_dict['data']
        validation_results = {
            'data_type': data_type,
            'constraints_checked': [],
            'violations': [],
            'warnings': [],
            'overall_valid': True
        }
        
        # Check for negative values in physical quantities
        if data_type in ['temperature', 'pressure', 'density', 'mass']:
            negative_mask = data < 0
            if negative_mask.any():
                validation_results['violations'].append({
                    'constraint': 'non_negative_values',
                    'count': negative_mask.sum(),
                    'severity': 'high'
                })
                validation_results['overall_valid'] = False
        
        # Check for infinite values
        infinite_mask = np.isinf(data)
        if infinite_mask.any():
            validation_results['violations'].append({
                'constraint': 'finite_values',
                'count': infinite_mask.sum(),
                'severity': 'critical'
            })
            validation_results['overall_valid'] = False
        
        # Check for NaN values
        nan_mask = np.isnan(data)
        if nan_mask.any():
            validation_results['violations'].append({
                'constraint': 'no_nan_values',
                'count': nan_mask.sum(),
                'severity': 'high'
            })
            validation_results['overall_valid'] = False
        
        # Check data range for specific types
        if data_type == 'temperature' and data.size > 0:
            temp_range = np.nanmax(data) - np.nanmin(data)
            if temp_range > 1000:  # Kelvin
                validation_results['warnings'].append({
                    'constraint': 'temperature_range',
                    'message': f'Large temperature range: {temp_range:.2f}K',
                    'severity': 'medium'
                })
        
        validation_results['constraints_checked'] = [
            'non_negative_values',
            'finite_values', 
            'no_nan_values',
            'data_range'
        ]
        
        return validation_results
    
    async def _normalize_data(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data to standard range"""
        await asyncio.sleep(0)
        
        data = data_dict['data']
        
        if data.size == 0:
            return data_dict
        
        # Calculate statistics
        mean = np.nanmean(data)
        std = np.nanstd(data)
        min_val = np.nanmin(data)
        max_val = np.nanmax(data)
        
        # Store statistics
        data_type = data_dict.get('format', 'unknown')
        self.data_statistics[data_type] = {
            'mean': mean,
            'std': std,
            'min': min_val,
            'max': max_val,
            'range': max_val - min_val
        }
        
        # Normalize if std > 0
        if std > 0:
            normalized_data = (data - mean) / std
            data_dict['data'] = normalized_data
            data_dict['normalization_info'] = {
                'method': 'z_score',
                'mean': mean,
                'std': std
            }
        
        return data_dict
    
    async def _scale_features(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Scale features using specified method"""
        await asyncio.sleep(0)
        
        data = data_dict['data']
        
        if data.size == 0:
            return data_dict
        
        if self.config.scale_method == "minmax":
            min_val = np.nanmin(data)
            max_val = np.nanmax(data)
            if max_val > min_val:
                scaled_data = (data - min_val) / (max_val - min_val)
                data_dict['data'] = scaled_data
                data_dict['scaling_info'] = {
                    'method': 'minmax',
                    'min': min_val,
                    'max': max_val
                }
        
        elif self.config.scale_method == "robust":
            q25 = np.nanpercentile(data, 25)
            q75 = np.nanpercentile(data, 75)
            iqr = q75 - q25
            if iqr > 0:
                scaled_data = (data - q25) / iqr
                data_dict['data'] = scaled_data
                data_dict['scaling_info'] = {
                    'method': 'robust',
                    'q25': q25,
                    'q75': q75,
                    'iqr': iqr
                }
        
        return data_dict
    
    async def _final_validation(self, data_dict: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Final validation after preprocessing"""
        await asyncio.sleep(0)
        
        data = data_dict['data']
        
        final_validation = {
            'data_ready': True,
            'shape': data.shape,
            'dtype': str(data.dtype),
            'has_nan': np.isnan(data).any(),
            'has_inf': np.isinf(data).any(),
            'is_finite': np.isfinite(data).all(),
            'is_normalized': 'normalization_info' in data_dict,
            'is_scaled': 'scaling_info' in data_dict
        }
        
        # Check if data is ready for simulation
        if final_validation['has_nan'] or final_validation['has_inf']:
            final_validation['data_ready'] = False
        
        return final_validation
    
    async def get_preprocessing_summary(self) -> Dict[str, Any]:
        """Get summary of all preprocessing operations"""
        await asyncio.sleep(0)
        
        total_operations = len(self.preprocessing_history)
        successful_operations = sum(1 for op in self.preprocessing_history if op.get('success', False))
        failed_operations = total_operations - successful_operations
        
        avg_processing_time = 0
        if successful_operations > 0:
            processing_times = [op['processing_time'] for op in self.preprocessing_history if op.get('success', False)]
            avg_processing_time = sum(processing_times) / len(processing_times)
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'average_processing_time': avg_processing_time,
            'data_types_processed': list(set(op['data_type'] for op in self.preprocessing_history)),
            'recent_operations': self.preprocessing_history[-5:] if self.preprocessing_history else []
        }
    
    async def reset_statistics(self) -> None:
        """Reset all statistics and history"""
        await asyncio.sleep(0)
        
        self.preprocessing_history.clear()
        self.data_statistics.clear()
        self.validation_results.clear()
        logger.info("🔄 Data Preprocessor statistics reset")
