"""
Data Quality Assessor
=====================

Data quality assessment utilities for federated learning.
Handles comprehensive quality metrics, scoring, and reporting.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class QualityMetric:
    """Individual quality metric configuration"""
    name: str
    metric_type: str  # completeness, accuracy, consistency, timeliness, validity
    weight: float = 1.0
    threshold: float = 0.8
    description: str = ""


@dataclass
class QualityAssessmentConfig:
    """Configuration for data quality assessment"""
    # Assessment modes
    comprehensive_assessment: bool = True
    include_statistical_analysis: bool = True
    include_outlier_detection: bool = True
    
    # Quality metrics
    quality_metrics: List[QualityMetric] = None
    custom_metrics: List[QualityMetric] = None
    
    # Statistical settings
    confidence_level: float = 0.95
    outlier_detection_method: str = "iqr"  # iqr, zscore, isolation_forest
    
    # Output settings
    detailed_reports: bool = True
    quality_score_breakdown: bool = True
    recommendations_enabled: bool = True


@dataclass
class QualityAssessmentMetrics:
    """Metrics for quality assessment performance"""
    # Quality scores
    overall_quality_score: float = 0.0
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    timeliness_score: float = 0.0
    validity_score: float = 0.0
    
    # Statistical metrics
    total_records: int = 0
    valid_records: int = 0
    missing_values: int = 0
    duplicate_records: int = 0
    outlier_records: int = 0
    
    # Performance metrics
    assessment_time: float = 0.0
    memory_usage_mb: float = 0.0
    processing_efficiency: float = 0.0


class DataQualityAssessor:
    """Data quality assessment implementation for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[QualityAssessmentConfig] = None
    ):
        """Initialize Data Quality Assessor"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or QualityAssessmentConfig()
        
        # Initialize default quality metrics if not provided
        if self.config.quality_metrics is None:
            self.config.quality_metrics = self._get_default_quality_metrics()
        
        # Assessment state
        self.is_assessing = False
        self.current_dataset = None
        self.assessment_history: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = QualityAssessmentMetrics()
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
    
    async def assess_data_quality(
        self,
        dataset: Union[np.ndarray, List[Dict[str, Any]], Dict[str, Any]],
        dataset_name: str = "unknown"
    ) -> Dict[str, Any]:
        """Assess data quality of a dataset"""
        try:
            self.start_time = datetime.now()
            self.is_assessing = True
            self.current_dataset = dataset_name
            
            print(f"🔍 Starting data quality assessment for: {dataset_name}")
            
            # Prepare dataset for assessment
            data_array = await self._prepare_data_array(dataset)
            
            # Update basic metrics
            self.metrics.total_records = data_array.shape[0]
            
            # Perform comprehensive quality assessment
            quality_results = await self._perform_quality_assessment(data_array)
            
            # Calculate overall quality score
            overall_score = await self._calculate_overall_quality_score(quality_results)
            self.metrics.overall_quality_score = overall_score
            
            # Generate recommendations
            recommendations = await self._generate_quality_recommendations(quality_results)
            
            # Calculate assessment time
            assessment_time = (datetime.now() - self.start_time).total_seconds()
            self.metrics.assessment_time = assessment_time
            
            # Record assessment history
            self.assessment_history.append({
                'dataset_name': dataset_name,
                'timestamp': datetime.now().isoformat(),
                'quality_results': quality_results,
                'overall_score': overall_score,
                'recommendations': recommendations,
                'metrics': self.metrics.__dict__,
                'config': self.config.__dict__
            })
            
            print(f"✅ Data quality assessment completed in {assessment_time:.2f}s")
            
            return {
                'status': 'success',
                'dataset_name': dataset_name,
                'quality_results': quality_results,
                'overall_quality_score': overall_score,
                'recommendations': recommendations,
                'metrics': self.metrics.__dict__,
                'assessment_time': assessment_time
            }
            
        except Exception as e:
            print(f"❌ Data quality assessment failed: {e}")
            return {'status': 'failed', 'error': str(e)}
        finally:
            self.is_assessing = False
    
    async def _prepare_data_array(
        self,
        dataset: Union[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]
    ) -> np.ndarray:
        """Prepare dataset as numpy array for assessment"""
        try:
            if isinstance(dataset, np.ndarray):
                return dataset
            elif isinstance(dataset, list):
                if dataset and isinstance(dataset[0], dict):
                    # Convert list of dicts to array
                    return np.array([list(record.values()) for record in dataset])
                else:
                    return np.array(dataset)
            elif isinstance(dataset, dict):
                # Convert dict to array
                return np.array(list(dataset.values()))
            else:
                raise ValueError(f"Unsupported dataset type: {type(dataset)}")
                
        except Exception as e:
            print(f"❌ Data array preparation failed: {e}")
            raise
    
    async def _perform_quality_assessment(self, data: np.ndarray) -> Dict[str, Any]:
        """Perform comprehensive quality assessment"""
        try:
            quality_results = {}
            
            # Assess completeness
            if any(metric.metric_type == 'completeness' for metric in self.config.quality_metrics):
                completeness_result = await self._assess_completeness(data)
                quality_results['completeness'] = completeness_result
                self.metrics.completeness_score = completeness_result['score']
            
            # Assess accuracy
            if any(metric.metric_type == 'accuracy' for metric in self.config.quality_metrics):
                accuracy_result = await self._assess_accuracy(data)
                quality_results['accuracy'] = accuracy_result
                self.metrics.accuracy_score = accuracy_result['score']
            
            # Assess consistency
            if any(metric.metric_type == 'consistency' for metric in self.config.quality_metrics):
                consistency_result = await self._assess_consistency(data)
                quality_results['consistency'] = consistency_result
                self.metrics.consistency_score = consistency_result['score']
            
            # Assess timeliness
            if any(metric.metric_type == 'timeliness' for metric in self.config.quality_metrics):
                timeliness_result = await self._assess_timeliness(data)
                quality_results['timeliness'] = timeliness_result
                self.metrics.timeliness_score = timeliness_result['score']
            
            # Assess validity
            if any(metric.metric_type == 'validity' for metric in self.config.quality_metrics):
                validity_result = await self._assess_validity(data)
                quality_results['validity'] = validity_result
                self.metrics.validity_score = validity_result['score']
            
            # Statistical analysis
            if self.config.include_statistical_analysis:
                statistical_result = await self._perform_statistical_analysis(data)
                quality_results['statistical'] = statistical_result
            
            # Outlier detection
            if self.config.include_outlier_detection:
                outlier_result = await self._detect_outliers(data)
                quality_results['outliers'] = outlier_result
                self.metrics.outlier_records = outlier_result['outlier_count']
            
            return quality_results
            
        except Exception as e:
            print(f"❌ Quality assessment failed: {e}")
            raise
    
    async def _assess_completeness(self, data: np.ndarray) -> Dict[str, Any]:
        """Assess data completeness"""
        try:
            # Calculate missing values
            missing_mask = np.isnan(data)
            missing_count = np.sum(missing_mask)
            total_elements = data.size
            
            # Calculate completeness score
            completeness_score = 1.0 - (missing_count / total_elements)
            
            # Update metrics
            self.metrics.missing_values = missing_count
            
            return {
                'score': completeness_score,
                'missing_count': int(missing_count),
                'total_elements': int(total_elements),
                'missing_percentage': float(missing_count / total_elements * 100),
                'completeness_percentage': float(completeness_score * 100)
            }
            
        except Exception as e:
            print(f"❌ Completeness assessment failed: {e}")
            return {'score': 0.0, 'error': str(e)}
    
    async def _assess_accuracy(self, data: np.ndarray) -> Dict[str, Any]:
        """Assess data accuracy"""
        try:
            # For numerical data, assess accuracy based on statistical properties
            if data.dtype.kind in 'fc':  # float or complex
                # Check for infinite values
                infinite_mask = np.isinf(data)
                infinite_count = np.sum(infinite_mask)
                
                # Check for extreme values (beyond 6 standard deviations)
                mean_val = np.nanmean(data)
                std_val = np.nanstd(data)
                extreme_mask = np.abs(data - mean_val) > 6 * std_val
                extreme_count = np.sum(extreme_mask)
                
                # Calculate accuracy score
                total_elements = data.size
                accuracy_score = 1.0 - ((infinite_count + extreme_count) / total_elements)
                
                return {
                    'score': accuracy_score,
                    'infinite_count': int(infinite_count),
                    'extreme_count': int(extreme_count),
                    'total_elements': int(total_elements),
                    'mean': float(mean_val),
                    'std': float(std_val)
                }
            else:
                # For non-numerical data, assume high accuracy
                return {'score': 0.9, 'note': 'Non-numerical data - accuracy assumed'}
                
        except Exception as e:
            print(f"❌ Accuracy assessment failed: {e}")
            return {'score': 0.0, 'error': str(e)}
    
    async def _assess_consistency(self, data: np.ndarray) -> Dict[str, Any]:
        """Assess data consistency"""
        try:
            # Check for duplicate rows
            unique_rows, counts = np.unique(data, axis=0, return_counts=True)
            duplicate_count = np.sum(counts > 1)
            
            # Check for data type consistency
            type_consistency = True
            for col in range(data.shape[1]):
                col_data = data[:, col]
                if not np.issubdtype(col_data.dtype, np.number):
                    # Check if all values in column have same type
                    types = [type(val) for val in col_data]
                    if len(set(types)) > 1:
                        type_consistency = False
                        break
            
            # Calculate consistency score
            total_rows = data.shape[0]
            consistency_score = 1.0 - (duplicate_count / total_rows)
            
            # Update metrics
            self.metrics.duplicate_records = duplicate_count
            
            return {
                'score': consistency_score,
                'duplicate_count': int(duplicate_count),
                'total_rows': int(total_rows),
                'type_consistency': type_consistency,
                'duplicate_percentage': float(duplicate_count / total_rows * 100)
            }
            
        except Exception as e:
            print(f"❌ Consistency assessment failed: {e}")
            return {'score': 0.0, 'error': str(e)}
    
    async def _assess_timeliness(self, data: np.ndarray) -> Dict[str, Any]:
        """Assess data timeliness"""
        try:
            # For timeliness, we need temporal data
            # This is a simplified assessment - in practice, you'd check actual timestamps
            
            # Assume high timeliness for now
            timeliness_score = 0.9
            
            return {
                'score': timeliness_score,
                'note': 'Timeliness assessment requires temporal data - using default score',
                'assessment_method': 'default'
            }
            
        except Exception as e:
            print(f"❌ Timeliness assessment failed: {e}")
            return {'score': 0.0, 'error': str(e)}
    
    async def _assess_validity(self, data: np.ndarray) -> Dict[str, Any]:
        """Assess data validity"""
        try:
            # Check for valid data types and ranges
            valid_count = 0
            total_elements = data.size
            
            for element in data.flat:
                if np.isfinite(element):  # Check if value is finite
                    valid_count += 1
            
            # Calculate validity score
            validity_score = valid_count / total_elements
            
            # Update metrics
            self.metrics.valid_records = valid_count
            
            return {
                'score': validity_score,
                'valid_count': int(valid_count),
                'total_elements': int(total_elements),
                'valid_percentage': float(validity_score * 100)
            }
            
        except Exception as e:
            print(f"❌ Validity assessment failed: {e}")
            return {'score': 0.0, 'error': str(e)}
    
    async def _perform_statistical_analysis(self, data: np.ndarray) -> Dict[str, Any]:
        """Perform statistical analysis of the data"""
        try:
            statistical_results = {}
            
            # Basic statistics for each column
            for col in range(data.shape[1]):
                col_data = data[:, col]
                
                if np.issubdtype(col_data.dtype, np.number):
                    # Numerical column statistics
                    clean_data = col_data[np.isfinite(col_data)]
                    if len(clean_data) > 0:
                        statistical_results[f'column_{col}'] = {
                            'mean': float(np.mean(clean_data)),
                            'median': float(np.median(clean_data)),
                            'std': float(np.std(clean_data)),
                            'min': float(np.min(clean_data)),
                            'max': float(np.max(clean_data)),
                            'q25': float(np.percentile(clean_data, 25)),
                            'q75': float(np.percentile(clean_data, 75)),
                            'skewness': float(self._calculate_skewness(clean_data)),
                            'kurtosis': float(self._calculate_kurtosis(clean_data))
                        }
            
            # Overall dataset statistics
            statistical_results['overall'] = {
                'shape': data.shape,
                'dtype': str(data.dtype),
                'memory_usage_mb': float(data.nbytes / (1024 * 1024))
            }
            
            return statistical_results
            
        except Exception as e:
            print(f"❌ Statistical analysis failed: {e}")
            return {'error': str(e)}
    
    async def _detect_outliers(self, data: np.ndarray) -> Dict[str, Any]:
        """Detect outliers in the data"""
        try:
            outlier_results = {}
            
            if self.config.outlier_detection_method == "iqr":
                outlier_results = await self._detect_outliers_iqr(data)
            elif self.config.outlier_detection_method == "zscore":
                outlier_results = await self._detect_outliers_zscore(data)
            elif self.config.outlier_detection_method == "isolation_forest":
                outlier_results = await self._detect_outliers_isolation_forest(data)
            else:
                outlier_results = await self._detect_outliers_iqr(data)  # Default
            
            return outlier_results
            
        except Exception as e:
            print(f"❌ Outlier detection failed: {e}")
            return {'error': str(e)}
    
    async def _detect_outliers_iqr(self, data: np.ndarray) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        try:
            outlier_count = 0
            outlier_indices = []
            
            for col in range(data.shape[1]):
                col_data = data[:, col]
                
                if np.issubdtype(col_data.dtype, np.number):
                    # Calculate Q1, Q3, and IQR
                    q1 = np.percentile(col_data, 25)
                    q3 = np.percentile(col_data, 75)
                    iqr = q3 - q1
                    
                    # Define outlier bounds
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    # Find outliers
                    col_outliers = (col_data < lower_bound) | (col_data > upper_bound)
                    outlier_count += np.sum(col_outliers)
                    outlier_indices.extend(np.where(col_outliers)[0].tolist())
            
            return {
                'method': 'iqr',
                'outlier_count': int(outlier_count),
                'outlier_indices': list(set(outlier_indices)),  # Remove duplicates
                'outlier_percentage': float(outlier_count / data.size * 100)
            }
            
        except Exception as e:
            print(f"❌ IQR outlier detection failed: {e}")
            return {'error': str(e)}
    
    async def _detect_outliers_zscore(self, data: np.ndarray) -> Dict[str, Any]:
        """Detect outliers using Z-score method"""
        try:
            outlier_count = 0
            outlier_indices = []
            threshold = 3.0  # Standard deviations
            
            for col in range(data.shape[1]):
                col_data = data[:, col]
                
                if np.issubdtype(col_data.dtype, np.number):
                    # Calculate z-scores
                    mean_val = np.nanmean(col_data)
                    std_val = np.nanstd(col_data)
                    
                    if std_val > 0:
                        z_scores = np.abs((col_data - mean_val) / std_val)
                        col_outliers = z_scores > threshold
                        outlier_count += np.sum(col_outliers)
                        outlier_indices.extend(np.where(col_outliers)[0].tolist())
            
            return {
                'method': 'zscore',
                'outlier_count': int(outlier_count),
                'outlier_indices': list(set(outlier_indices)),
                'outlier_percentage': float(outlier_count / data.size * 100),
                'threshold': threshold
            }
            
        except Exception as e:
            print(f"❌ Z-score outlier detection failed: {e}")
            return {'error': str(e)}
    
    async def _detect_outliers_isolation_forest(self, data: np.ndarray) -> Dict[str, Any]:
        """Detect outliers using Isolation Forest (simplified)"""
        try:
            # Simplified isolation forest implementation
            # In practice, you'd use sklearn.ensemble.IsolationForest
            
            outlier_count = 0
            outlier_indices = []
            
            # Simple distance-based outlier detection as fallback
            for col in range(data.shape[1]):
                col_data = data[:, col]
                
                if np.issubdtype(col_data.dtype, np.number):
                    # Use median absolute deviation (MAD) for robust outlier detection
                    median_val = np.nanmedian(col_data)
                    mad = np.nanmedian(np.abs(col_data - median_val))
                    
                    if mad > 0:
                        # Values beyond 3 MAD are considered outliers
                        col_outliers = np.abs(col_data - median_val) > 3 * mad
                        outlier_count += np.sum(col_outliers)
                        outlier_indices.extend(np.where(col_outliers)[0].tolist())
            
            return {
                'method': 'isolation_forest_simplified',
                'outlier_count': int(outlier_count),
                'outlier_indices': list(set(outlier_indices)),
                'outlier_percentage': float(outlier_count / data.size * 100),
                'note': 'Using simplified MAD-based detection'
            }
            
        except Exception as e:
            print(f"❌ Isolation Forest outlier detection failed: {e}")
            return {'error': str(e)}
    
    async def _calculate_overall_quality_score(self, quality_results: Dict[str, Any]) -> float:
        """Calculate overall quality score from individual assessments"""
        try:
            scores = []
            weights = []
            
            # Collect scores and weights from quality metrics
            for metric in self.config.quality_metrics:
                if metric.metric_type in quality_results:
                    result = quality_results[metric.metric_type]
                    if 'score' in result:
                        scores.append(result['score'])
                        weights.append(metric.weight)
            
            # Calculate weighted average
            if scores and weights:
                total_weight = sum(weights)
                if total_weight > 0:
                    weighted_score = sum(score * weight for score, weight in zip(scores, weights)) / total_weight
                    return max(0.0, min(1.0, weighted_score))
            
            # Fallback: simple average
            if scores:
                return max(0.0, min(1.0, np.mean(scores)))
            
            return 0.0
            
        except Exception as e:
            print(f"⚠️  Overall quality score calculation failed: {e}")
            return 0.0
    
    async def _generate_quality_recommendations(self, quality_results: Dict[str, Any]) -> List[str]:
        """Generate quality improvement recommendations"""
        try:
            recommendations = []
            
            if not self.config.recommendations_enabled:
                return recommendations
            
            # Completeness recommendations
            if 'completeness' in quality_results:
                completeness_score = quality_results['completeness']['score']
                if completeness_score < 0.9:
                    recommendations.append(f"Improve data completeness (current: {completeness_score:.2%})")
            
            # Accuracy recommendations
            if 'accuracy' in quality_results:
                accuracy_score = quality_results['accuracy']['score']
                if accuracy_score < 0.9:
                    recommendations.append(f"Improve data accuracy (current: {accuracy_score:.2%})")
            
            # Consistency recommendations
            if 'consistency' in quality_results:
                consistency_score = quality_results['consistency']['score']
                if consistency_score < 0.9:
                    recommendations.append(f"Improve data consistency (current: {consistency_score:.2%})")
            
            # Outlier recommendations
            if 'outliers' in quality_results:
                outlier_percentage = quality_results['outliers'].get('outlier_percentage', 0)
                if outlier_percentage > 5.0:
                    recommendations.append(f"Investigate high outlier rate ({outlier_percentage:.1f}%)")
            
            # General recommendations
            if not recommendations:
                recommendations.append("Data quality is good - maintain current standards")
            
            return recommendations
            
        except Exception as e:
            print(f"⚠️  Recommendation generation failed: {e}")
            return ["Unable to generate recommendations due to error"]
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data"""
        try:
            if len(data) < 3:
                return 0.0
            
            mean_val = np.mean(data)
            std_val = np.std(data)
            
            if std_val == 0:
                return 0.0
            
            skewness = np.mean(((data - mean_val) / std_val) ** 3)
            return float(skewness)
            
        except Exception:
            return 0.0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data"""
        try:
            if len(data) < 4:
                return 0.0
            
            mean_val = np.mean(data)
            std_val = np.std(data)
            
            if std_val == 0:
                return 0.0
            
            kurtosis = np.mean(((data - mean_val) / std_val) ** 4) - 3
            return float(kurtosis)
            
        except Exception:
            return 0.0
    
    def _get_default_quality_metrics(self) -> List[QualityMetric]:
        """Get default quality metrics"""
        return [
            QualityMetric(
                name="completeness",
                metric_type="completeness",
                weight=0.25,
                threshold=0.9,
                description="Percentage of non-missing values"
            ),
            QualityMetric(
                name="accuracy",
                metric_type="accuracy",
                weight=0.25,
                threshold=0.9,
                description="Data accuracy and precision"
            ),
            QualityMetric(
                name="consistency",
                metric_type="consistency",
                weight=0.2,
                threshold=0.9,
                description="Data consistency and uniformity"
            ),
            QualityMetric(
                name="timeliness",
                metric_type="timeliness",
                weight=0.15,
                threshold=0.8,
                description="Data freshness and relevance"
            ),
            QualityMetric(
                name="validity",
                metric_type="validity",
                weight=0.15,
                threshold=0.9,
                description="Data validity and format compliance"
            )
        ]
    
    async def get_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive quality assessment report"""
        try:
            return {
                'quality_metrics': self.metrics.__dict__,
                'assessment_history': self.assessment_history,
                'current_config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Quality report generation failed: {e}")
            return {'error': str(e)}
    
    async def get_algorithm_statistics(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return {
            'algorithm_name': 'DataQualityAssessor',
            'is_assessing': self.is_assessing,
            'current_dataset': self.current_dataset,
            'metrics': self.metrics.__dict__,
            'config': self.config.__dict__
        }
    
    async def reset_assessor(self):
        """Reset assessor state and metrics"""
        self.is_assessing = False
        self.current_dataset = None
        self.assessment_history.clear()
        self.metrics = QualityAssessmentMetrics()
        self.start_time = None
        
        print("🔄 Data Quality Assessor reset")
