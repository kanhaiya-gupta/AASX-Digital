"""
Docker Containerization Support

This module provides comprehensive Docker support for the AAS Data Modeling
Engine integration layer, including image building, container management,
and deployment orchestration.
"""

import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


logger = logging.getLogger(__name__)


class ContainerStatus(str, Enum):
    """Container status enumeration."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"


class ImageStatus(str, Enum):
    """Image status enumeration."""
    AVAILABLE = "available"
    BUILDING = "building"
    FAILED = "failed"
    NOT_FOUND = "not_found"


@dataclass
class ContainerConfig:
    """Configuration for a Docker container."""
    
    name: str
    image: str
    ports: Dict[str, str] = field(default_factory=dict)  # host_port: container_port
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)  # host_path: container_path
    networks: List[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"
    memory_limit: str = "512m"
    cpu_limit: str = "0.5"
    health_check: Optional[str] = None
    command: Optional[List[str]] = None
    working_dir: Optional[str] = None
    user: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ImageConfig:
    """Configuration for building a Docker image."""
    
    name: str
    tag: str = "latest"
    dockerfile_path: str = "Dockerfile"
    build_context: str = "."
    build_args: Dict[str, str] = field(default_factory=dict)
    target_stage: Optional[str] = None
    cache_from: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ContainerInfo:
    """Information about a Docker container."""
    
    container_id: str
    name: str
    image: str
    status: ContainerStatus
    ports: Dict[str, str]
    created: str
    state: str
    health: Optional[str] = None
    exit_code: Optional[int] = None
    logs: Optional[str] = None


@dataclass
class ImageInfo:
    """Information about a Docker image."""
    
    image_id: str
    repository: str
    tag: str
    size: str
    created: str
    status: ImageStatus
    layers: List[str] = field(default_factory=list)


class DockerManager:
    """
    Docker container and image management service.
    
    Provides comprehensive Docker operations including:
    - Image building and management
    - Container lifecycle management
    - Health monitoring
    - Resource management
    - Multi-container orchestration
    """
    
    def __init__(self, docker_host: Optional[str] = None):
        """Initialize the Docker manager."""
        self.docker_host = docker_host or os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
        self.containers: Dict[str, ContainerInfo] = {}
        self.images: Dict[str, ImageInfo] = {}
        
        # Verify Docker is available
        if not self._check_docker_available():
            raise RuntimeError("Docker is not available or not running")
        
        logger.info("Docker Manager initialized")
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def build_image(self, config: ImageConfig) -> str:
        """Build a Docker image from the specified configuration."""
        logger.info(f"Building Docker image: {config.name}:{config.tag}")
        
        try:
            # Prepare build command
            build_cmd = [
                "docker", "build",
                "-t", f"{config.name}:{config.tag}",
                "-f", config.dockerfile_path,
                config.build_context
            ]
            
            # Add build arguments
            for key, value in config.build_args.items():
                build_cmd.extend(["--build-arg", f"{key}={value}"])
            
            # Add target stage if specified
            if config.target_stage:
                build_cmd.extend(["--target", config.target_stage])
            
            # Add cache from images
            for cache_image in config.cache_from:
                build_cmd.extend(["--cache-from", cache_image])
            
            # Add labels
            for key, value in config.labels.items():
                build_cmd.extend(["--label", f"{key}={value}"])
            
            # Execute build
            process = await asyncio.create_subprocess_exec(
                *build_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                image_id = stdout.decode().strip().split()[-1]
                logger.info(f"Image built successfully: {image_id}")
                
                # Update image info
                await self._update_image_info(config.name, config.tag)
                
                return image_id
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Image build failed: {error_msg}")
                raise RuntimeError(f"Docker build failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error building Docker image: {str(e)}")
            raise
    
    async def run_container(self, config: ContainerConfig) -> str:
        """Run a Docker container with the specified configuration."""
        logger.info(f"Running container: {config.name}")
        
        try:
            # Prepare run command
            run_cmd = [
                "docker", "run",
                "-d",  # Detached mode
                "--name", config.name,
                "--restart", config.restart_policy,
                "-m", config.memory_limit,
                "--cpus", config.cpu_limit
            ]
            
            # Add ports
            for host_port, container_port in config.ports.items():
                run_cmd.extend(["-p", f"{host_port}:{container_port}"])
            
            # Add environment variables
            for key, value in config.environment.items():
                run_cmd.extend(["-e", f"{key}={value}"])
            
            # Add volumes
            for host_path, container_path in config.volumes.items():
                run_cmd.extend(["-v", f"{host_path}:{container_path}"])
            
            # Add networks
            for network in config.networks:
                run_cmd.extend(["--network", network])
            
            # Add labels
            for key, value in config.labels.items():
                run_cmd.extend(["--label", f"{key}={value}"])
            
            # Add working directory
            if config.working_dir:
                run_cmd.extend(["-w", config.working_dir])
            
            # Add user
            if config.user:
                run_cmd.extend(["-u", config.user])
            
            # Add health check
            if config.health_check:
                run_cmd.extend(["--health-cmd", config.health_check])
            
            # Add command
            if config.command:
                run_cmd.extend(config.command)
            
            # Execute run command
            process = await asyncio.create_subprocess_exec(
                *run_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                container_id = stdout.decode().strip()
                logger.info(f"Container started successfully: {container_id}")
                
                # Update container info
                await self._update_container_info(container_id)
                
                return container_id
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Container start failed: {error_msg}")
                raise RuntimeError(f"Docker run failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error running container: {str(e)}")
            raise
    
    async def stop_container(self, container_name: str) -> bool:
        """Stop a running container."""
        logger.info(f"Stopping container: {container_name}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "stop", container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Container stopped successfully: {container_name}")
                await self._update_container_info(container_name)
                return True
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Container stop failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping container: {str(e)}")
            return False
    
    async def remove_container(self, container_name: str, force: bool = False) -> bool:
        """Remove a container."""
        logger.info(f"Removing container: {container_name}")
        
        try:
            cmd = ["docker", "rm"]
            if force:
                cmd.append("-f")
            cmd.append(container_name)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Container removed successfully: {container_name}")
                if container_name in self.containers:
                    del self.containers[container_name]
                return True
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Container removal failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing container: {str(e)}")
            return False
    
    async def get_container_logs(self, container_name: str, tail: int = 100) -> str:
        """Get logs from a container."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "logs", "--tail", str(tail), container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to get container logs: {error_msg}")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting container logs: {str(e)}")
            return ""
    
    async def get_container_status(self, container_name: str) -> Optional[ContainerStatus]:
        """Get the status of a container."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "inspect", "--format", "{{.State.Status}}", container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                status = stdout.decode().strip()
                return ContainerStatus(status)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting container status: {str(e)}")
            return None
    
    async def list_containers(self, all_containers: bool = False) -> List[ContainerInfo]:
        """List all containers."""
        try:
            cmd = ["docker", "ps"]
            if all_containers:
                cmd.append("-a")
            cmd.extend(["--format", "{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                containers = []
                for line in stdout.decode().strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            container_info = ContainerInfo(
                                container_id=parts[0],
                                name=parts[1],
                                image=parts[2],
                                status=ContainerStatus(parts[3].split()[0]),
                                ports={},
                                created="",
                                state=parts[3]
                            )
                            containers.append(container_info)
                
                return containers
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to list containers: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing containers: {str(e)}")
            return []
    
    async def list_images(self) -> List[ImageInfo]:
        """List all Docker images."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "images", "--format", "{{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                images = []
                for line in stdout.decode().strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            image_info = ImageInfo(
                                image_id=parts[0],
                                repository=parts[1],
                                tag=parts[2],
                                size=parts[3],
                                created=parts[4],
                                status=ImageStatus.AVAILABLE
                            )
                            images.append(image_info)
                
                return images
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Failed to list images: {error_msg}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing images: {str(e)}")
            return []
    
    async def remove_image(self, image_name: str, force: bool = False) -> bool:
        """Remove a Docker image."""
        logger.info(f"Removing image: {image_name}")
        
        try:
            cmd = ["docker", "rmi"]
            if force:
                cmd.append("-f")
            cmd.append(image_name)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Image removed successfully: {image_name}")
                return True
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"Image removal failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing image: {str(e)}")
            return False
    
    async def _update_container_info(self, container_id: str) -> None:
        """Update container information."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "inspect", container_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                container_data = json.loads(stdout.decode())
                if container_data:
                    data = container_data[0]
                    container_info = ContainerInfo(
                        container_id=data.get("Id", ""),
                        name=data.get("Name", "").lstrip("/"),
                        image=data.get("Image", ""),
                        status=ContainerStatus(data.get("State", {}).get("Status", "unknown")),
                        ports=data.get("NetworkSettings", {}).get("Ports", {}),
                        created=data.get("Created", ""),
                        state=data.get("State", {}).get("Status", ""),
                        health=data.get("State", {}).get("Health", {}).get("Status"),
                        exit_code=data.get("State", {}).get("ExitCode")
                    )
                    
                    self.containers[container_info.name] = container_info
                    
        except Exception as e:
            logger.error(f"Error updating container info: {str(e)}")
    
    async def _update_image_info(self, repository: str, tag: str) -> None:
        """Update image information."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "inspect", f"{repository}:{tag}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                image_data = json.loads(stdout.decode())
                if image_data:
                    data = image_data[0]
                    image_info = ImageInfo(
                        image_id=data.get("Id", ""),
                        repository=repository,
                        tag=tag,
                        size=str(data.get("Size", 0)),
                        created=data.get("Created", ""),
                        status=ImageStatus.AVAILABLE,
                        layers=data.get("Layers", [])
                    )
                    
                    self.images[f"{repository}:{tag}"] = image_info
                    
        except Exception as e:
            logger.error(f"Error updating image info: {str(e)}")
    
    async def cleanup_unused_resources(self) -> Dict[str, int]:
        """Clean up unused Docker resources."""
        logger.info("Cleaning up unused Docker resources")
        
        try:
            # Remove stopped containers
            process = await asyncio.create_subprocess_exec(
                "docker", "container", "prune", "-f",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Remove unused images
            process2 = await asyncio.create_subprocess_exec(
                "docker", "image", "prune", "-f",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout2, stderr2 = await process2.communicate()
            
            # Remove unused networks
            process3 = await asyncio.create_subprocess_exec(
                "docker", "network", "prune", "-f",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout3, stderr3 = await process3.communicate()
            
            # Parse results
            containers_removed = 0
            images_removed = 0
            networks_removed = 0
            
            if "Total reclaimed space" in stdout.decode():
                # Parse the output to get counts
                pass
            
            logger.info("Docker cleanup completed")
            
            return {
                "containers_removed": containers_removed,
                "images_removed": images_removed,
                "networks_removed": networks_removed
            }
            
        except Exception as e:
            logger.error(f"Error during Docker cleanup: {str(e)}")
            return {"containers_removed": 0, "images_removed": 0, "networks_removed": 0}
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get Docker system information."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "system", "df",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse the output to get system information
                return {
                    "status": "available",
                    "output": stdout.decode().strip()
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
