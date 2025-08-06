"""
Configuration management for physics modeling framework.

This module provides settings, plugin configuration, and solver configuration
management for the framework.
"""

from .settings import Settings
from .plugin_config import PluginConfig
from .solver_config import SolverConfig

__all__ = [
    "Settings",
    "PluginConfig",
    "SolverConfig"
] 