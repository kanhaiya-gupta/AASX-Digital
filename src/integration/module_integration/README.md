# Module Integration Package

## Overview

The Module Integration Package provides the orchestration layer for the AAS Data Modeling Engine, enabling seamless coordination and workflow management between the engine core and external task modules.

This package acts as the "nervous system" that connects the protected engine core with specialized task modules, enabling complex multi-module workflows while maintaining data governance and system integrity.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Module Integration Layer                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Discovery     │  │   Connector     │  │ Orchestrator│ │
│  │   Service       │  │   Service       │  │   Service   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Health        │  │   Data Sync     │                  │
│  │   Monitor       │  │   Service       │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    Engine Core (Protected)                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Data          │  │   Governance    │  │   Security  │ │
│  │   Services      │  │   Services      │  │   Services  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    Task Modules                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Twin        │  │ AASX       │  │ AI/RAG              │ │
│  │ Registry    │  │ Processing │  │ Analysis            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Knowledge   │  │ Federated  │  │ Physics             │ │
│  │ Graph       │  │ Learning   │  │ Modeling            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Core Services

### 1. Module Discovery Service (`module_discovery.py`)

**Purpose**: Automatically discovers and registers available task modules in the system.

**Key Features**:
- Scans multiple discovery sources (src/modules, webapp/modules, environment variables)
- Validates module availability and capabilities
- Maintains registry of discovered modules
- Supports automatic re-discovery at configurable intervals

**Usage**:
```python
from src.integration.module_integration import ModuleDiscoveryService

# Initialize discovery service
discovery_service = ModuleDiscoveryService(discovery_interval=300)

# Start automatic discovery
await discovery_service.start_discovery()

# Get discovered modules
modules = discovery_service.get_discovered_modules()
```

### 2. Module Connector Service (`module_connector.py`)

**Purpose**: Establishes and manages connections to external modules.

**Key Features**:
- Connection pooling and management
- Health checking and validation
- Retry logic with exponential backoff
- Graceful degradation when modules are unavailable

**Usage**:
```python
from src.integration.module_integration import ModuleConnectorService

# Initialize connector service
connector_service = ModuleConnectorService(max_connections=100)

# Connect to a module
connection = await connector_service.connect_to_module(module_info)

# Execute operations
result = await connector_service.execute_module_operation(
    module_name="ai_rag",
    operation="analyze_text",
    parameters={"text": "sample text"}
)
```

### 3. Module Health Monitor Service (`module_health_monitor.py`)

**Purpose**: Continuously monitors the health and performance of all modules.

**Key Features**:
- Real-time health status tracking
- Performance metrics collection
- Alert generation for unhealthy modules
- Integration with engine monitoring system

**Usage**:
```python
from src.integration.module_integration import ModuleHealthMonitorService

# Initialize health monitor
health_monitor = ModuleHealthMonitorService(monitoring_interval=60)

# Start monitoring
await health_monitor.start_monitoring()

# Get health summary
health_summary = health_monitor.get_health_summary()

# Register alert callbacks
def alert_callback(alert):
    print(f"Alert: {alert['message']}")

health_monitor.register_alert_callback(alert_callback)
```

### 4. Module Data Sync Service (`module_data_sync.py`)

**Purpose**: Handles data synchronization between the engine and external modules.

**Key Features**:
- Bidirectional data flow management
- Data transformation and validation
- Conflict resolution strategies
- Performance tracking and optimization

**Usage**:
```python
from src.integration.module_integration import ModuleDataSyncService

# Initialize data sync service
sync_service = ModuleDataSyncService(sync_interval=300)

# Start data synchronization
await sync_service.start_data_sync()

# Queue sync operations
sync_id = await sync_service.queue_sync_operation(
    operation_type="push",
    source_module="aasx",
    target_module="ai_rag"
)
```

### 5. Module Orchestrator Service (`module_orchestrator.py`)

**Purpose**: Orchestrates complex workflows and interactions between multiple modules.

**Key Features**:
- Pre-built workflow templates
- Dependency management and parallel execution
- Error handling and rollback capabilities
- Workflow monitoring and metrics

**Usage**:
```python
from src.integration.module_integration import ModuleOrchestratorService

# Initialize orchestrator service
orchestrator = ModuleOrchestratorService(max_concurrent_workflows=20)

# Create workflow from template
workflow = await orchestrator.create_workflow_from_template(
    template_name="carbon_footprint_analysis",
    workflow_name="My Carbon Analysis"
)

# Execute workflow
result = await orchestrator.execute_workflow(workflow)
```

## 📋 Data Models

### Core Models

- **`ModuleInfo`**: Information about discovered modules
- **`ModuleHealth`**: Health status and performance metrics
- **`WorkflowStep`**: Individual step in a workflow
- **`WorkflowResult`**: Complete workflow execution result
- **`ModuleConnection`**: Active connection to a module

### Enums

- **`ModuleStatus`**: ONLINE, OFFLINE, DEGRADED, ERROR, UNKNOWN
- **`ModuleType`**: TWIN_REGISTRY, AASX, AI_RAG, KG_NEO4J, etc.
- **`WorkflowStatus`**: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, TIMEOUT

## 🔧 Configuration

### Environment Variables

```bash
# Module discovery settings
MODULE_DISCOVERY_INTERVAL=300
MODULE_HEALTH_CHECK_INTERVAL=60
MODULE_DATA_SYNC_INTERVAL=300

# Connection settings
MAX_CONCURRENT_CONNECTIONS=100
CONNECTION_TIMEOUT=30
MAX_CONCURRENT_WORKFLOWS=20

# External module URLs
MODULE_AI_RAG_URL=http://localhost:8001
MODULE_TWIN_REGISTRY_URL=http://localhost:8002
```

### Service Configuration

```python
# Discovery service
discovery_service = ModuleDiscoveryService(
    discovery_interval=300  # 5 minutes
)

# Health monitor
health_monitor = ModuleHealthMonitorService(
    monitoring_interval=60,    # 1 minute
    alert_threshold=3          # Alert after 3 consecutive failures
)

# Data sync service
sync_service = ModuleDataSyncService(
    sync_interval=300,           # 5 minutes
    max_concurrent_syncs=10     # Max 10 concurrent sync operations
)

# Orchestrator service
orchestrator = ModuleOrchestratorService(
    max_concurrent_workflows=20  # Max 20 concurrent workflows
)
```

## 🎯 Workflow Templates

### Available Templates

1. **Carbon Footprint Analysis**
   - Upload AASX → Extract Data → AI Analysis → Store Twin → Knowledge Graph → Generate Report

2. **Digital Twin Creation**
   - Validate Input → Create Twin → Configure Physics → Setup Monitoring

3. **AI Model Training**
   - Prepare Data → Train Model → Validate Model → Deploy Model

### Custom Workflows

```python
# Create custom workflow
workflow = WorkflowDefinition(
    workflow_id=uuid4(),
    name="Custom Workflow",
    description="My custom workflow"
)

# Add steps
workflow.add_step(
    step_id="step1",
    module_name="aasx",
    operation="process_file",
    parameters={"file_type": "aasx"},
    dependencies=[]
)

workflow.add_step(
    step_id="step2",
    module_name="ai_rag",
    operation="analyze_data",
    parameters={"analysis_type": "custom"},
    dependencies=["step1"]
)

# Execute custom workflow
result = await orchestrator.execute_workflow(workflow)
```

## 🚀 Getting Started

### 1. Installation

```bash
# Install dependencies
pip install -r src/integration/requirements.txt
```

### 2. Basic Usage

```python
import asyncio
from src.integration.module_integration import (
    ModuleDiscoveryService,
    ModuleConnectorService,
    ModuleHealthMonitorService,
    ModuleDataSyncService,
    ModuleOrchestratorService
)

async def main():
    # Initialize all services
    discovery = ModuleDiscoveryService()
    connector = ModuleConnectorService()
    health_monitor = ModuleHealthMonitorService()
    sync_service = ModuleDataSyncService()
    orchestrator = ModuleOrchestratorService()
    
    # Start services
    await discovery.start_discovery()
    await health_monitor.start_monitoring()
    await sync_service.start_data_sync()
    
    # Wait for discovery to complete
    await asyncio.sleep(10)
    
    # Get discovered modules
    modules = discovery.get_discovered_modules()
    print(f"Discovered {len(modules)} modules")
    
    # Execute a workflow
    workflow = await orchestrator.create_workflow_from_template(
        template_name="carbon_footprint_analysis"
    )
    
    result = await orchestrator.execute_workflow(workflow)
    print(f"Workflow completed: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Service Integration

```python
# Integrate with existing webapp
from webapp.core.app_factory import create_app_with_routers
from src.integration.module_integration import ModuleOrchestratorService

app = create_app_with_routers()

# Add orchestrator service to app state
orchestrator = ModuleOrchestratorService()
app.state.orchestrator = orchestrator

# Use in routes
@app.post("/api/workflows/execute")
async def execute_workflow(workflow_request: dict):
    workflow = await orchestrator.create_workflow_from_template(
        workflow_request["template_name"]
    )
    result = await orchestrator.execute_workflow(workflow)
    return {"workflow_id": str(result.workflow_id), "status": result.status}
```

## 🔍 Monitoring and Debugging

### Service Status

```python
# Get service status
discovery_status = discovery_service.get_discovery_status()
health_status = health_monitor.get_monitoring_status()
sync_status = sync_service.get_sync_status()
orchestrator_status = orchestrator.get_orchestrator_status()

print(f"Discovery: {discovery_status}")
print(f"Health Monitor: {health_status}")
print(f"Data Sync: {sync_status}")
print(f"Orchestrator: {orchestrator_status}")
```

### Health Monitoring

```python
# Get module health
all_health = health_monitor.get_all_module_health()
for module_name, health in all_health.items():
    print(f"{module_name}: {health.status.value}")

# Get health summary
summary = health_monitor.get_health_summary()
print(f"Overall health: {summary['overall_health']}")
print(f"Modules with issues: {summary['modules_with_issues']}")
```

### Workflow Monitoring

```python
# Get active workflows
active_workflows = orchestrator.get_active_workflows()
for workflow_id, workflow in active_workflows.items():
    print(f"Workflow {workflow_id}: {workflow.status.value}")

# Get workflow history
history = orchestrator.get_workflow_history(limit=10)
for workflow in history:
    print(f"{workflow.workflow_name}: {workflow.status.value}")
```

## 🧪 Testing

### Unit Tests

```bash
# Run tests
pytest src/integration/module_integration/tests/ -v

# Run with coverage
pytest src/integration/module_integration/tests/ --cov=. --cov-report=html
```

### Integration Tests

```python
# Test workflow execution
async def test_carbon_footprint_workflow():
    orchestrator = ModuleOrchestratorService()
    
    workflow = await orchestrator.create_workflow_from_template(
        template_name="carbon_footprint_analysis"
    )
    
    result = await orchestrator.execute_workflow(workflow)
    assert result.status == WorkflowStatus.COMPLETED
```

## 🔒 Security and Governance

### Data Governance

- All data flows through the engine's governance services
- Data lineage tracking across module boundaries
- Validation and quality checks before data transfer
- Audit logging for all operations

### Access Control

- Module authentication and authorization
- Connection-level security
- Workflow execution permissions
- Data access controls

### Compliance

- GDPR compliance for data handling
- Industry-standard security practices
- Regular security audits
- Compliance reporting

## 📈 Performance and Scalability

### Performance Features

- Asynchronous operation execution
- Connection pooling and reuse
- Parallel workflow step execution
- Intelligent retry mechanisms

### Scalability Features

- Configurable concurrency limits
- Horizontal scaling support
- Load balancing capabilities
- Performance monitoring and optimization

### Monitoring

- Real-time performance metrics
- Resource usage tracking
- Bottleneck identification
- Automatic scaling recommendations

## 🚨 Troubleshooting

### Common Issues

1. **Module Discovery Fails**
   - Check module directory structure
   - Verify module has `__init__.py` or `routes.py`
   - Check discovery service logs

2. **Connection Failures**
   - Verify module is running
   - Check network connectivity
   - Review connection timeout settings

3. **Workflow Execution Stuck**
   - Check step dependencies
   - Review module availability
   - Check workflow timeout settings

4. **Data Sync Issues**
   - Verify data formats
   - Check validation rules
   - Review conflict resolution strategies

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Enable service-specific debug
discovery_service.logger.setLevel(logging.DEBUG)
connector_service.logger.setLevel(logging.DEBUG)
```

## 🔮 Future Enhancements

### Planned Features

- **Advanced Workflow Engine**: Complex workflow patterns and state machines
- **Machine Learning Integration**: AI-powered workflow optimization
- **Real-time Collaboration**: Multi-user workflow editing and execution
- **Advanced Analytics**: Workflow performance insights and recommendations
- **Plugin System**: Extensible workflow templates and operations

### Roadmap

- **Phase 1**: Core integration services (✅ Complete)
- **Phase 2**: Advanced workflow capabilities
- **Phase 3**: AI-powered optimization
- **Phase 4**: Enterprise features and scaling

## 📚 Additional Resources

- [AAS Data Modeling Engine Documentation](../engine/README.md)
- [Workflow Templates Guide](./workflow_templates.md)
- [API Reference](./api_reference.md)
- [Performance Tuning Guide](./performance_tuning.md)
- [Security Best Practices](./security_guide.md)

## 🤝 Contributing

We welcome contributions to the Module Integration Package! Please see our contributing guidelines and code of conduct for more information.

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd aas-data-modeling

# Install development dependencies
pip install -r src/integration/requirements.txt

# Run tests
pytest src/integration/module_integration/tests/

# Format code
black src/integration/module_integration/
```

---

**Module Integration Package** - The orchestration layer for the AAS Data Modeling Engine ecosystem.
