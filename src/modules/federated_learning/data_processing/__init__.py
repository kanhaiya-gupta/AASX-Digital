"""
Federated Learning Data Processing
================================

Data processing components for federated learning.
"""

from .feature_extractor import FeatureExtractor
from .training_data_preparer import TrainingDataPreparer
from .data_validator import DataValidator

# New modern components
from .data_preprocessor import DataPreprocessor, PreprocessingConfig, PreprocessingMetrics
from .validation_processor import ValidationProcessor, ValidationConfig, ValidationMetrics, ValidationRule
from .quality_assessor import DataQualityAssessor, QualityAssessmentConfig, QualityAssessmentMetrics, QualityMetric
from .privacy_processor import PrivacyProcessor, PrivacyConfig, PrivacyMetrics

__all__ = [
    # Existing components
    'FeatureExtractor',
    'TrainingDataPreparer',
    'DataValidator',
    
    # New modern components
    'DataPreprocessor',
    'PreprocessingConfig', 
    'PreprocessingMetrics',
    'ValidationProcessor',
    'ValidationConfig',
    'ValidationMetrics',
    'ValidationRule',
    'DataQualityAssessor',
    'QualityAssessmentConfig',
    'QualityAssessmentMetrics',
    'QualityMetric',
    'PrivacyProcessor',
    'PrivacyConfig',
    'PrivacyMetrics'
] 