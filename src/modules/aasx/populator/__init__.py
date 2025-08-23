"""
AASX Populator Package

This package contains data population utilities for AASX processing operations.
"""

from .data_generator import (
    AASXDataGenerator,
    TestDataPopulator,
    create_data_generator,
    create_test_data_populator
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    # Data generation
    'AASXDataGenerator',
    'TestDataPopulator',
    'create_data_generator',
    'create_test_data_populator'
]
