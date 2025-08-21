# Deployment Support Layer

## Overview

The Deployment Support Layer provides comprehensive deployment capabilities for the AAS Data Modeling Engine integration layer, including containerization, Kubernetes deployment, and auto-scaling support.

## 🚀 Features

### **Docker Containerization**
- **Image Management**: Build, manage, and optimize Docker images
- **Container Lifecycle**: Run, stop, remove, and monitor containers
- **Resource Management**: CPU and memory limits, health checks
- **Multi-container Orchestration**: Manage complex container deployments

### **Kubernetes Deployment**
- **Deployment Management**: Create, scale, and manage K8s deployments
- **Service Configuration**: Load balancers, ingress controllers
- **Namespace Management**: Multi-tenant deployment support
- **Cluster Operations**: Node monitoring, resource management

### **Auto-Scaling**
- **Multi-Metric Policies**: CPU, memory, custom metrics
- **Intelligent Scaling**: Trend analysis and predictive scaling
- **Performance Optimization**: Automatic policy optimization
- **Scaling Analytics**: Historical analysis and performance metrics

## 📁 Structure

```
src/integration/deployment/
├── __init__.py              # Package initialization
├── containerization.py      # Docker container management
├── kubernetes.py            # Kubernetes deployment
├── scaling.py               # Auto-scaling policies
└── README.md               # This documentation
```

## 🔧 Installation & Dependencies

### **Required Tools**
- **Docker**: For containerization support
- **kubectl**: For Kubernetes operations
- **PyYAML**: For Kubernetes manifest generation

### **System Requirements**
- Python 3.8+
- Docker daemon running
- Kubernetes cluster access
- Sufficient system resources

## 📖 Usage Examples

### **Docker Containerization**

#### **Basic Container Management**
```python
from integration.deployment import DockerManager
from integration.deployment.containerization import ContainerConfig, ImageConfig

# Initialize Docker manager
docker_manager = DockerManager()

# Build an image
image_config = ImageConfig(
    name="aas-integration",
    tag="latest",
    dockerfile_path="Dockerfile",
    build_context="."
)

image_id = await docker_manager.build_image(image_config)

# Run a container
container_config = ContainerConfig(
    name="aas-integration-container",
    image="aas-integration:latest",
    ports={"8080": "8000"},
    environment={"ENV": "production"},
    memory_limit="1g",
    cpu_limit="1.0"
)

container_id = await docker_manager.run_container(container_config)

# Monitor container status
status = await docker_manager.get_container_status("aas-integration-container")
logs = await docker_manager.get_container_logs("aas-integration-container")
```

#### **Advanced Container Operations**
```python
# List all containers
containers = await docker_manager.list_containers(all_containers=True)

# Get system information
system_info = await docker_manager.get_system_info()

# Clean up unused resources
cleanup_result = await docker_manager.cleanup_unused_resources()

# Stop and remove containers
await docker_manager.stop_container("container-name")
await docker_manager.remove_container("container-name", force=True)
```

### **Kubernetes Deployment**

#### **Basic Deployment**
```python
from integration.deployment import KubernetesManager
from integration.deployment.kubernetes import (
    KubernetesConfig, DeploymentConfig, ServiceConfig
)

# Initialize Kubernetes manager
k8s_config = KubernetesConfig(
    namespace="aas-integration",
    context="production-cluster"
)
k8s_manager = KubernetesManager(k8s_config)

# Create namespace
await k8s_manager.create_namespace("aas-integration", {
    "environment": "production",
    "team": "data-engineering"
})

# Create deployment
deployment_config = DeploymentConfig(
    name="aas-integration-api",
    image="aas-integration:latest",
    replicas=3,
    namespace="aas-integration",
    ports=[{"containerPort": 8000, "protocol": "TCP"}],
    environment={
        "DATABASE_URL": "postgresql://localhost:5432/aas",
        "REDIS_URL": "redis://localhost:6379"
    },
    resources={
        "requests": {"cpu": "100m", "memory": "128Mi"},
        "limits": {"cpu": "500m", "memory": "512Mi"}
    }
)

await k8s_manager.create_deployment(deployment_config)

# Create service
service_config = ServiceConfig(
    name="aas-integration-service",
    deployment_name="aas-integration-api",
    namespace="aas-integration",
    service_type=ServiceType.LOAD_BALANCER,
    ports=[{"port": 80, "targetPort": 8000, "protocol": "TCP"}]
)

await k8s_manager.create_service(service_config)
```

#### **Advanced Kubernetes Operations**
```python
# Scale deployment
await k8s_manager.scale_deployment("aas-integration-api", "aas-integration", 5)

# Monitor deployment status
status = await k8s_manager.get_deployment_status("aas-integration-api", "aas-integration")

# List resources
deployments = await k8s_manager.list_deployments("aas-integration")
pods = await k8s_manager.list_pods("aas-integration")
services = await k8s_manager.list_services("aas-integration")

# Get pod logs
logs = await k8s_manager.get_pod_logs("pod-name", "aas-integration")

# Describe resources
description = await k8s_manager.describe_resource("deployment", "aas-integration-api", "aas-integration")

# Get cluster information
cluster_info = await k8s_manager.get_cluster_info()
node_info = await k8s_manager.get_node_info()
```

### **Auto-Scaling**

#### **Basic Auto-Scaling Setup**
```python
from integration.deployment import AutoScalingManager
from integration.deployment.scaling import (
    ScalingPolicy, ScalingThreshold, ResourceType
)

# Initialize auto-scaling manager
scaling_manager = AutoScalingManager()

# Create custom scaling policy
custom_policy = ScalingPolicy(
    name="production_scaling",
    policy_type=ScalingPolicy.HYBRID,
    thresholds=[
        ScalingThreshold(
            resource_type=ResourceType.CPU,
            upper_threshold=75.0,
            lower_threshold=25.0,
            cooldown_period=300
        ),
        ScalingThreshold(
            resource_type=ResourceType.MEMORY,
            upper_threshold=80.0,
            lower_threshold=30.0,
            cooldown_period=300
        )
    ],
    min_replicas=2,
    max_replicas=20,
    target_replicas=5,
    scale_up_factor=1.5,
    scale_down_factor=0.7
)

scaling_manager.add_scaling_policy(custom_policy)

# Add metric collectors
async def cpu_metric_collector():
    # Implement CPU metrics collection
    return {
        "current_usage": 65.0,
        "current_percentage": 65.0
    }

async def memory_metric_collector():
    # Implement memory metrics collection
    return {
        "current_usage": 2.5,  # GB
        "current_percentage": 70.0
    }

scaling_manager.add_metric_collector(ResourceType.CPU, cpu_metric_collector)
scaling_manager.add_metric_collector(ResourceType.MEMORY, memory_metric_collector)

# Add scaling callback
async def scaling_callback(decision):
    # Implement actual scaling logic
    if decision.action == ScalingAction.SCALE_UP:
        # Scale up deployment
        return True
    elif decision.action == ScalingAction.SCALE_DOWN:
        # Scale down deployment
        return True
    return False

scaling_manager.add_scaling_callback("production_scaling", scaling_callback)
```

#### **Advanced Auto-Scaling Operations**
```python
# Evaluate scaling policy
decision = await scaling_manager.evaluate_scaling_policy("production_scaling", 3)

# Auto-scale all policies
decisions = await scaling_manager.auto_scale_all_policies(3)

# Get scaling analytics
analytics = scaling_manager.get_scaling_analytics()

# Get resource metrics summary
cpu_summary = scaling_manager.get_resource_metrics_summary(ResourceType.CPU, hours=24)
memory_summary = scaling_manager.get_resource_metrics_summary(ResourceType.MEMORY, hours=24)

# Optimize scaling policies
optimizations = await scaling_manager.optimize_scaling_policies()

# Get scaling history
history = scaling_manager.get_scaling_history(
    action=ScalingAction.SCALE_UP,
    start_time=datetime.now() - timedelta(hours=24)
)

# Start continuous monitoring
monitoring_task = asyncio.create_task(
    scaling_manager.start_monitoring(interval_seconds=60)
)

# Stop monitoring
monitoring_task.cancel()
```

## 🏗️ Architecture

### **Component Relationships**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docker        │    │  Kubernetes     │    │   Auto-Scaling  │
│   Manager       │    │   Manager       │    │    Manager      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Container      │    │   Deployment    │    │   Scaling       │
│  Operations     │    │   Operations    │    │   Policies      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Flow**
1. **Metric Collection**: Resource usage metrics are collected
2. **Policy Evaluation**: Scaling policies evaluate current metrics
3. **Decision Making**: Scaling decisions are made based on thresholds
4. **Action Execution**: Scaling actions are executed via callbacks
5. **Monitoring**: Continuous monitoring tracks performance and adjusts

## ⚙️ Configuration

### **Environment Variables**
```bash
# Docker configuration
DOCKER_HOST=unix:///var/run/docker.sock
DOCKER_TLS_VERIFY=1
DOCKER_CERT_PATH=/path/to/certs

# Kubernetes configuration
KUBECONFIG=/path/to/kubeconfig
KUBE_CONTEXT=production-cluster
KUBE_NAMESPACE=aas-integration

# Auto-scaling configuration
SCALING_INTERVAL=60
SCALING_ENABLED=true
SCALING_LOG_LEVEL=INFO
```

### **Configuration Files**
```yaml
# deployment-config.yaml
docker:
  host: "unix:///var/run/docker.sock"
  timeout: 30
  cleanup_interval: 3600

kubernetes:
  namespace: "aas-integration"
  context: "production-cluster"
  default_replicas: 3
  resource_limits:
    cpu: "500m"
    memory: "512Mi"

scaling:
  enabled: true
  interval_seconds: 60
  policies:
    cpu_scaling:
      enabled: true
      upper_threshold: 80.0
      lower_threshold: 20.0
      cooldown_period: 300
    memory_scaling:
      enabled: true
      upper_threshold: 85.0
      lower_threshold: 30.0
      cooldown_period: 300
```

## 🔍 Monitoring & Observability

### **Metrics Collection**
- **Resource Usage**: CPU, memory, storage, network
- **Scaling Actions**: Frequency, success rate, duration
- **Performance**: Response times, throughput, error rates
- **Health**: Container/pod status, availability

### **Logging**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Deployment layer logs
logger = logging.getLogger('integration.deployment')
```

### **Health Checks**
```python
# Docker health check
health_status = await docker_manager.get_system_info()

# Kubernetes health check
cluster_status = await k8s_manager.get_cluster_info()

# Auto-scaling health check
scaling_analytics = scaling_manager.get_scaling_analytics()
```

## 🚨 Error Handling

### **Common Issues & Solutions**

#### **Docker Issues**
```python
try:
    await docker_manager.build_image(image_config)
except RuntimeError as e:
    if "Docker is not available" in str(e):
        logger.error("Docker daemon not running")
    elif "build failed" in str(e):
        logger.error("Image build failed - check Dockerfile")
    else:
        logger.error(f"Unexpected Docker error: {e}")
```

#### **Kubernetes Issues**
```python
try:
    await k8s_manager.create_deployment(deployment_config)
except Exception as e:
    if "kubectl is not available" in str(e):
        logger.error("kubectl not configured")
    elif "manifest application failed" in str(e):
        logger.error("Kubernetes manifest invalid")
    else:
        logger.error(f"Unexpected Kubernetes error: {e}")
```

#### **Auto-Scaling Issues**
```python
try:
    decision = await scaling_manager.evaluate_scaling_policy("policy_name", 3)
except Exception as e:
    logger.error(f"Scaling policy evaluation failed: {e}")
    # Fall back to default scaling behavior
```

## 🧪 Testing

### **Unit Tests**
```python
# Test Docker manager
async def test_docker_manager():
    manager = DockerManager()
    assert manager._check_docker_available() == True

# Test Kubernetes manager
async def test_k8s_manager():
    manager = KubernetesManager()
    assert manager._check_kubectl_available() == True

# Test Auto-scaling manager
async def test_scaling_manager():
    manager = AutoScalingManager()
    policies = manager.list_scaling_policies()
    assert len(policies) >= 3  # Default policies
```

### **Integration Tests**
```python
# Test end-to-end deployment
async def test_deployment_workflow():
    # Build image
    docker_manager = DockerManager()
    image_id = await docker_manager.build_image(image_config)
    
    # Deploy to Kubernetes
    k8s_manager = KubernetesManager()
    await k8s_manager.create_deployment(deployment_config)
    
    # Verify deployment
    status = await k8s_manager.get_deployment_status("test-deployment", "default")
    assert status == DeploymentStatus.AVAILABLE
```

## 📊 Performance & Optimization

### **Best Practices**
1. **Resource Limits**: Set appropriate CPU and memory limits
2. **Scaling Policies**: Use conservative thresholds to avoid thrashing
3. **Monitoring**: Implement comprehensive health checks
4. **Cleanup**: Regular cleanup of unused resources
5. **Caching**: Cache frequently accessed deployment information

### **Performance Tuning**
```python
# Optimize scaling policies
optimizations = await scaling_manager.optimize_scaling_policies()

# Adjust thresholds based on performance data
for policy_name, policy_optimizations in optimizations.items():
    for issue, optimization in policy_optimizations.items():
        if "high_frequency" in issue:
            # Increase cooldown periods
            policy = scaling_manager.get_scaling_policy(policy_name)
            policy.scale_up_cooldown = optimization["suggested_changes"]["scale_up_cooldown"]
```

## 🔒 Security Considerations

### **Docker Security**
- Use non-root users in containers
- Implement resource limits
- Scan images for vulnerabilities
- Use minimal base images

### **Kubernetes Security**
- Implement RBAC policies
- Use network policies
- Enable pod security policies
- Implement secrets management

### **Auto-Scaling Security**
- Validate scaling callbacks
- Implement rate limiting
- Monitor scaling actions
- Audit scaling decisions

## 🚀 Deployment Examples

### **Complete Integration Service Deployment**
```python
async def deploy_integration_service():
    # 1. Build Docker image
    docker_manager = DockerManager()
    image_config = ImageConfig(
        name="aas-integration-service",
        tag="latest",
        dockerfile_path="Dockerfile.integration"
    )
    await docker_manager.build_image(image_config)
    
    # 2. Deploy to Kubernetes
    k8s_manager = KubernetesManager()
    
    # Create namespace
    await k8s_manager.create_namespace("aas-integration")
    
    # Create deployment
    deployment_config = DeploymentConfig(
        name="aas-integration-api",
        image="aas-integration-service:latest",
        replicas=3,
        namespace="aas-integration"
    )
    await k8s_manager.create_deployment(deployment_config)
    
    # Create service
    service_config = ServiceConfig(
        name="aas-integration-service",
        deployment_name="aas-integration-api",
        namespace="aas-integration"
    )
    await k8s_manager.create_service(service_config)
    
    # 3. Configure auto-scaling
    scaling_manager = AutoScalingManager()
    
    # Add scaling callback
    async def scale_integration_service(decision):
        if decision.action == ScalingAction.SCALE_UP:
            return await k8s_manager.scale_deployment(
                "aas-integration-api",
                "aas-integration",
                decision.target_replicas
            )
        return True
    
    scaling_manager.add_scaling_callback("integration_scaling", scale_integration_service)
    
    # Start monitoring
    monitoring_task = asyncio.create_task(
        scaling_manager.start_monitoring(interval_seconds=60)
    )
    
    return monitoring_task
```

## 📚 Additional Resources

### **Documentation**
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AAS Data Modeling Engine Documentation](../README.md)

### **Examples**
- [Docker Examples](examples/docker/)
- [Kubernetes Examples](examples/kubernetes/)
- [Auto-scaling Examples](examples/scaling/)

### **Troubleshooting**
- [Common Issues](troubleshooting.md)
- [Performance Tuning](performance.md)
- [Security Guidelines](security.md)

---

## 🤝 Contributing

Contributions to the Deployment Support Layer are welcome! Please see the main project contribution guidelines for details.

## 📄 License

This project is licensed under the MIT License - see the main project license file for details.
