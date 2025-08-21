"""
Twin Registry Population Module

This module handles automatic population of the twin registry based on:
- File uploads (Phase 1: Basic registry entry)
- ETL pipeline completion (Phase 2: Enhanced registry data)
- AI/RAG processing completion
- Other system events

The module provides a modular, event-driven approach to twin registry management
with zero disruption to existing ETL workflows.
"""

from .twin_registry_populator import TwinRegistryPopulator
from .phase1_upload_populator import Phase1UploadPopulator
from .phase2_etl_populator import Phase2ETLPopulator
from .population_coordinator import PopulationCoordinator
from .population_triggers import PopulationTriggers
from .population_validator import PopulationValidator

__all__ = [
    'TwinRegistryPopulator',
    'Phase1UploadPopulator', 
    'Phase2ETLPopulator',
    'PopulationCoordinator',
    'PopulationTriggers',
    'PopulationValidator'
]

__version__ = "1.0.0"
__description__ = "Twin Registry Population Module - Automatic registry population from ETL events"
