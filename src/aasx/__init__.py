"""
AASX Backend Processing Package

This package contains the core AASX processing logic including:
- ETL pipeline for AASX data processing using external .NET processor
- AASX file extraction and generation orchestration
- Data transformation and validation
"""

# New modular backend imports
from .aasx_extraction import extract_aasx, batch_extract
from .aasx_generator import generate_aasx, batch_generate

__all__ = [
    'extract_aasx',
    'batch_extract', 
    'generate_aasx',
    'batch_generate'
]

__version__ = '1.0.0' 