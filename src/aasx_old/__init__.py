"""
AASX Backend Processing Package

This package contains the core AASX processing logic including:
- ETL pipeline for AASX data processing
- AASX file loading and parsing
- Data transformation and validation
- .NET bridge for AASX package exploration
"""

from .aasx_loader import AASXLoader
from .aasx_processor import AASXProcessor
from .aasx_transformer import AASXTransformer, TransformationConfig
from .aasx_etl_pipeline import AASXETLPipeline
from .dotnet_bridge import DotNetAasBridge

__all__ = [
    'AASXLoader',
    'AASXProcessor', 
    'AASXTransformer',
    'TransformationConfig',
    'AASXETLPipeline',
    'DotNetAasBridge'
]

__version__ = '1.0.0' 