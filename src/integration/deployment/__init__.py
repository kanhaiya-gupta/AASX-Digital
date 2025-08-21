"""
Deployment Support Package

This module provides comprehensive deployment capabilities for the
AAS Data Modeling Engine integration layer, including containerization,
Kubernetes deployment, and auto-scaling support.

The deployment service handles:
- Docker containerization and image management
- Kubernetes deployment manifests and orchestration
- Auto-scaling policies and resource management
- Environment-specific configuration management
- Deployment monitoring and rollback capabilities
"""

from .containerization import DockerManager
from .kubernetes import KubernetesManager
from .scaling import AutoScalingManager

__version__ = "1.0.0"
__author__ = "AAS Data Modeling Team"

__all__ = [
    "DockerManager",
    "KubernetesManager", 
    "AutoScalingManager"
]
