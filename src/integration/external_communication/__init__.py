"""
External Communication Package

This package provides communication infrastructure for external modules within
the AAS Data Modeling Engine, enabling seamless data flow and event-driven
communication between distributed components.

The external communication layer handles:
- HTTP/GRPC client management for external modules
- Event communication bridge for pub/sub messaging
- Data pipeline orchestration for complex workflows
- External module registry for service discovery
"""

from .module_client import ModuleClient, ModuleClientPool
from .event_bridge import EventBridge, EventMessage, EventType
from .data_pipeline import DataPipeline, PipelineStage, PipelineConfig
from .module_registry import ExternalModuleRegistry, ModuleEndpoint
from .models import (
    CommunicationProtocol,
    PipelineStatus,
    CommunicationMetrics
)

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    "ModuleClient",
    "ModuleClientPool", 
    "EventBridge",
    "EventMessage",
    "EventType",
    "DataPipeline",
    "PipelineStage",
    "PipelineConfig",
    "ExternalModuleRegistry",
    "ModuleEndpoint",
    "CommunicationProtocol",
    "PipelineStatus",
    "CommunicationMetrics"
]
