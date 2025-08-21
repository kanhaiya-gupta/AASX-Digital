"""
Kubernetes Deployment Support

This module provides comprehensive Kubernetes deployment capabilities for the
AAS Data Modeling Engine integration layer, including deployment management,
service orchestration, and cluster operations.
"""

import asyncio
import logging
import os
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


logger = logging.getLogger(__name__)


class DeploymentStatus(str, Enum):
    """Kubernetes deployment status enumeration."""
    AVAILABLE = "Available"
    PROGRESSING = "Progressing"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class PodStatus(str, Enum):
    """Kubernetes pod status enumeration."""
    RUNNING = "Running"
    PENDING = "Pending"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class ServiceType(str, Enum):
    """Kubernetes service type enumeration."""
    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"
    EXTERNAL_NAME = "ExternalName"


@dataclass
class KubernetesConfig:
    """Configuration for Kubernetes deployment."""
    
    namespace: str = "default"
    context: Optional[str] = None
    config_file: Optional[str] = None
    cluster_name: Optional[str] = None
    user_name: Optional[str] = None


@dataclass
class DeploymentConfig:
    """Configuration for a Kubernetes deployment."""
    
    name: str
    image: str
    replicas: int = 1
    namespace: str = "default"
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    ports: List[Dict[str, Any]] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    volume_mounts: List[Dict[str, Any]] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    health_check: Optional[Dict[str, Any]] = None
    strategy: Dict[str, Any] = field(default_factory=lambda: {"type": "RollingUpdate"})
    selector: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceConfig:
    """Configuration for a Kubernetes service."""
    
    name: str
    deployment_name: str
    namespace: str = "default"
    service_type: ServiceType = ServiceType.CLUSTER_IP
    ports: List[Dict[str, Any]] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    selector: Dict[str, str] = field(default_factory=dict)


@dataclass
class IngressConfig:
    """Configuration for a Kubernetes ingress."""
    
    name: str
    namespace: str = "default"
    hosts: List[str] = field(default_factory=list)
    tls: List[Dict[str, Any]] = field(default_factory=list)
    annotations: Dict[str, str] = field(default_factory=dict)
    rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DeploymentInfo:
    """Information about a Kubernetes deployment."""
    
    name: str
    namespace: str
    replicas: int
    available_replicas: int
    updated_replicas: int
    status: DeploymentStatus
    age: str
    labels: Dict[str, str]
    selector: Dict[str, str]


@dataclass
class PodInfo:
    """Information about a Kubernetes pod."""
    
    name: str
    namespace: str
    ready: str
    status: PodStatus
    restarts: int
    age: str
    ip: str
    node: str
    labels: Dict[str, str]


@dataclass
class ServiceInfo:
    """Information about a Kubernetes service."""
    
    name: str
    namespace: str
    type: ServiceType
    cluster_ip: str
    external_ip: Optional[str]
    ports: str
    age: str
    labels: Dict[str, str]
    selector: Dict[str, str]


class KubernetesManager:
    """
    Kubernetes deployment and management service.
    
    Provides comprehensive Kubernetes operations including:
    - Deployment management and scaling
    - Service and ingress configuration
    - Pod monitoring and health checks
    - Resource management and optimization
    - Multi-cluster operations
    """
    
    def __init__(self, config: Optional[KubernetesConfig] = None):
        """Initialize the Kubernetes manager."""
        self.config = config or KubernetesConfig()
        self.deployments: Dict[str, DeploymentInfo] = {}
        self.pods: Dict[str, PodInfo] = {}
        self.services: Dict[str, ServiceInfo] = {}
        
        # Verify kubectl is available
        if not self._check_kubectl_available():
            raise RuntimeError("kubectl is not available or not configured")
        
        # Set kubectl context if specified
        if self.config.context:
            self._set_kubectl_context(self.config.context)
        
        logger.info("Kubernetes Manager initialized")
    
    def _check_kubectl_available(self) -> bool:
        """Check if kubectl is available and configured."""
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _set_kubectl_context(self, context: str) -> bool:
        """Set the kubectl context."""
        try:
            result = subprocess.run(
                ["kubectl", "config", "use-context", context],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def create_namespace(self, name: str, labels: Optional[Dict[str, str]] = None) -> bool:
        """Create a Kubernetes namespace."""
        logger.info(f"Creating namespace: {name}")
        
        try:
            # Create namespace YAML
            namespace_manifest = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": name,
                    "labels": labels or {}
                }
            }
            
            # Apply namespace
            success = await self._apply_manifest(namespace_manifest)
            
            if success:
                logger.info(f"Namespace created successfully: {name}")
                return True
            else:
                logger.error(f"Failed to create namespace: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating namespace: {str(e)}")
            return False
    
    async def create_deployment(self, config: DeploymentConfig) -> bool:
        """Create a Kubernetes deployment."""
        logger.info(f"Creating deployment: {config.name}")
        
        try:
            # Create deployment manifest
            deployment_manifest = self._create_deployment_manifest(config)
            
            # Apply deployment
            success = await self._apply_manifest(deployment_manifest)
            
            if success:
                logger.info(f"Deployment created successfully: {config.name}")
                await self._update_deployment_info(config.name, config.namespace)
                return True
            else:
                logger.error(f"Failed to create deployment: {config.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating deployment: {str(e)}")
            return False
    
    async def create_service(self, config: ServiceConfig) -> bool:
        """Create a Kubernetes service."""
        logger.info(f"Creating service: {config.name}")
        
        try:
            # Create service manifest
            service_manifest = self._create_service_manifest(config)
            
            # Apply service
            success = await self._apply_manifest(service_manifest)
            
            if success:
                logger.info(f"Service created successfully: {config.name}")
                await self._update_service_info(config.name, config.namespace)
                return True
            else:
                logger.error(f"Failed to create service: {config.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating service: {str(e)}")
            return False
    
    async def create_ingress(self, config: IngressConfig) -> bool:
        """Create a Kubernetes ingress."""
        logger.info(f"Creating ingress: {config.name}")
        
        try:
            # Create ingress manifest
            ingress_manifest = self._create_ingress_manifest(config)
            
            # Apply ingress
            success = await self._apply_manifest(ingress_manifest)
            
            if success:
                logger.info(f"Ingress created successfully: {config.name}")
                return True
            else:
                logger.error(f"Failed to create ingress: {config.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating ingress: {str(e)}")
            return False
    
    async def scale_deployment(self, name: str, namespace: str, replicas: int) -> bool:
        """Scale a Kubernetes deployment."""
        logger.info(f"Scaling deployment {name} to {replicas} replicas")
        
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "scale", "deployment", name, f"--replicas={replicas}", "-n", namespace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Deployment scaled successfully: {name}")
                await self._update_deployment_info(name, namespace)
                return True
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Deployment scaling failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error scaling deployment: {str(e)}")
            return False
    
    async def delete_deployment(self, name: str, namespace: str) -> bool:
        """Delete a Kubernetes deployment."""
        logger.info(f"Deleting deployment: {name}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "delete", "deployment", name, "-n", namespace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Deployment deleted successfully: {name}")
                if name in self.deployments:
                    del self.deployments[name]
                return True
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Deployment deletion failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting deployment: {str(e)}")
            return False
    
    async def get_deployment_status(self, name: str, namespace: str) -> Optional[DeploymentStatus]:
        """Get the status of a deployment."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "get", "deployment", name, "-n", namespace, "-o", "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                deployment_data = json.loads(stdout.decode())
                status = deployment_data.get("status", {}).get("conditions", [])
                
                for condition in status:
                    if condition.get("type") == "Available":
                        if condition.get("status") == "True":
                            return DeploymentStatus.AVAILABLE
                        else:
                            return DeploymentStatus.FAILED
                
                return DeploymentStatus.PROGRESSING
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting deployment status: {str(e)}")
            return None
    
    async def list_deployments(self, namespace: str = "default") -> List[DeploymentInfo]:
        """List all deployments in a namespace."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "get", "deployments", "-n", namespace, "-o", "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                deployments_data = json.loads(stdout.decode())
                deployments = []
                
                for item in deployments_data.get("items", []):
                    metadata = item.get("metadata", {})
                    spec = item.get("spec", {})
                    status = item.get("status", {})
                    
                    deployment_info = DeploymentInfo(
                        name=metadata.get("name", ""),
                        namespace=metadata.get("namespace", ""),
                        replicas=spec.get("replicas", 0),
                        available_replicas=status.get("availableReplicas", 0),
                        updated_replicas=status.get("updatedReplicas", 0),
                        status=DeploymentStatus(status.get("conditions", [{}])[0].get("type", "Unknown")),
                        age=metadata.get("creationTimestamp", ""),
                        labels=metadata.get("labels", {}),
                        selector=spec.get("selector", {})
                    )
                    
                    deployments.append(deployment_info)
                
                return deployments
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to list deployments: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing deployments: {str(e)}")
            return []
    
    async def list_pods(self, namespace: str = "default", label_selector: Optional[str] = None) -> List[PodInfo]:
        """List all pods in a namespace."""
        try:
            cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
            if label_selector:
                cmd.extend(["-l", label_selector])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                pods_data = json.loads(stdout.decode())
                pods = []
                
                for item in pods_data.get("items", []):
                    metadata = item.get("metadata", {})
                    status = item.get("status", {})
                    
                    pod_info = PodInfo(
                        name=metadata.get("name", ""),
                        namespace=metadata.get("namespace", ""),
                        ready=f"{status.get('ready', 0)}/{len(status.get('containerStatuses', []))}",
                        status=PodStatus(status.get("phase", "Unknown")),
                        restarts=sum(container.get("restartCount", 0) for container in status.get("containerStatuses", [])),
                        age=metadata.get("creationTimestamp", ""),
                        ip=status.get("podIP", ""),
                        node=status.get("hostIP", ""),
                        labels=metadata.get("labels", {})
                    )
                    
                    pods.append(pod_info)
                
                return pods
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to list pods: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing pods: {str(e)}")
            return []
    
    async def list_services(self, namespace: str = "default") -> List[ServiceInfo]:
        """List all services in a namespace."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "get", "services", "-n", namespace, "-o", "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                services_data = json.loads(stdout.decode())
                services = []
                
                for item in services_data.get("items", []):
                    metadata = item.get("metadata", {})
                    spec = item.get("spec", {})
                    status = item.get("status", {})
                    
                    service_info = ServiceInfo(
                        name=metadata.get("name", ""),
                        namespace=metadata.get("namespace", ""),
                        type=ServiceType(spec.get("type", "ClusterIP")),
                        cluster_ip=spec.get("clusterIP", ""),
                        external_ip=spec.get("externalIPs", [None])[0] if spec.get("externalIPs") else None,
                        ports=",".join([f"{port.get('port')}:{port.get('targetPort', '')}" for port in spec.get("ports", [])]),
                        age=metadata.get("creationTimestamp", ""),
                        labels=metadata.get("labels", {}),
                        selector=spec.get("selector", {})
                    )
                    
                    services.append(service_info)
                
                return services
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to list services: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing services: {str(e)}")
            return []
    
    async def get_pod_logs(self, pod_name: str, namespace: str, tail: int = 100) -> str:
        """Get logs from a pod."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "logs", pod_name, "-n", namespace, "--tail", str(tail),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to get pod logs: {error_msg}")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting pod logs: {str(e)}")
            return ""
    
    async def describe_resource(self, resource_type: str, name: str, namespace: str = "default") -> str:
        """Describe a Kubernetes resource."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "describe", resource_type, name, "-n", namespace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to describe resource: {error_msg}")
                return ""
                
        except Exception as e:
            logger.error(f"Error describing resource: {str(e)}")
            return ""
    
    def _create_deployment_manifest(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Create a deployment manifest from configuration."""
        containers = [{
            "name": config.name,
            "image": config.image,
            "ports": config.ports,
            "env": [{"name": k, "value": v} for k, v in config.environment.items()],
            "volumeMounts": config.volume_mounts,
            "resources": config.resources
        }]
        
        if config.health_check:
            containers[0]["livenessProbe"] = config.health_check
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
                "labels": config.labels,
                "annotations": config.annotations
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": config.selector or {"app": config.name}
                },
                "template": {
                    "metadata": {
                        "labels": config.selector or {"app": config.name}
                    },
                    "spec": {
                        "containers": containers,
                        "volumes": config.volumes
                    }
                },
                "strategy": config.strategy
            }
        }
    
    def _create_service_manifest(self, config: ServiceConfig) -> Dict[str, Any]:
        """Create a service manifest from configuration."""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
                "labels": config.labels,
                "annotations": config.annotations
            },
            "spec": {
                "type": config.service_type.value,
                "selector": config.selector or {"app": config.deployment_name},
                "ports": config.ports
            }
        }
    
    def _create_ingress_manifest(self, config: IngressConfig) -> Dict[str, Any]:
        """Create an ingress manifest from configuration."""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": config.name,
                "namespace": config.namespace,
                "annotations": config.annotations
            },
            "spec": {
                "rules": config.rules,
                "tls": config.tls
            }
        }
    
    async def _apply_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Apply a Kubernetes manifest."""
        try:
            # Create temporary YAML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                temp_file = f.name
            
            try:
                # Apply the manifest
                process = await asyncio.create_subprocess_exec(
                    "kubectl", "apply", "-f", temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    return True
                else:
                    error_msg = stderr.decode().strip()
                    logger.error(f"Manifest application failed: {error_msg}")
                    return False
                    
            finally:
                # Clean up temporary file
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Error applying manifest: {str(e)}")
            return False
    
    async def _update_deployment_info(self, name: str, namespace: str) -> None:
        """Update deployment information."""
        try:
            deployments = await self.list_deployments(namespace)
            for deployment in deployments:
                if deployment.name == name:
                    self.deployments[name] = deployment
                    break
        except Exception as e:
            logger.error(f"Error updating deployment info: {str(e)}")
    
    async def _update_service_info(self, name: str, namespace: str) -> None:
        """Update service information."""
        try:
            services = await self.list_services(namespace)
            for service in services:
                if service.name == name:
                    self.services[name] = service
                    break
        except Exception as e:
            logger.error(f"Error updating service info: {str(e)}")
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get Kubernetes cluster information."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "cluster-info",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "status": "available",
                    "info": stdout.decode().strip()
                }
            else:
                return {
                    "status": "error",
                    "error": stderr.decode().strip()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_node_info(self) -> List[Dict[str, Any]]:
        """Get Kubernetes node information."""
        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl", "get", "nodes", "-o", "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                nodes_data = json.loads(stdout.decode())
                nodes = []
                
                for item in nodes_data.get("items", []):
                    metadata = item.get("metadata", {})
                    status = item.get("status", {})
                    
                    node_info = {
                        "name": metadata.get("name", ""),
                        "status": status.get("conditions", [{}])[0].get("type", "Unknown"),
                        "capacity": status.get("capacity", {}),
                        "allocatable": status.get("allocatable", {}),
                        "labels": metadata.get("labels", {})
                    }
                    
                    nodes.append(node_info)
                
                return nodes
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to get node info: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting node info: {str(e)}")
            return []
