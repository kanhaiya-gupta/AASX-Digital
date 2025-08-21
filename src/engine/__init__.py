"""
AAS Data Modeling Engine
========================

A comprehensive engine for Asset Administration Shell (AAS) data modeling,
including messaging, caching, and data management capabilities.
"""

from . import messaging
from . import caching
from . import security
from . import monitoring
from . import utils
from . import config

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    'messaging',
    'caching',
    'security',
    'monitoring',
    'utils',
    'config'
] 