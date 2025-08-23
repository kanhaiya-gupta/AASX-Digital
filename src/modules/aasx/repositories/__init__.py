"""
AASX Data Access Layer Package

This package contains repositories for AASX processing operations.
Repositories use the engine ConnectionManager for database access.
"""

from .aasx_processing_repository import AasxProcessingRepository
from .aasx_processing_metrics_repository import AasxProcessingMetricsRepository

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    'AasxProcessingRepository',
    'AasxProcessingMetricsRepository'
]
