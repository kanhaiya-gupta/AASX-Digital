# Cross-Module Workflow Engine

## Overview

The Cross-Module Workflow Engine provides comprehensive workflow orchestration and management capabilities for coordinating complex business processes across multiple external modules within the AAS Data Modeling Engine. This layer enables enterprise-grade workflow automation while maintaining the separation of concerns and engine protection principles.

## 🎯 Purpose

The workflow engine serves as the **orchestrator** of complex business processes, providing:

- **Workflow Definition & Management**: Create, version, and manage workflow templates
- **Task Orchestration**: Coordinate task execution across multiple modules
- **Resource Management**: Efficient allocation and monitoring of module resources
- **Performance Monitoring**: Real-time monitoring and optimization of workflow execution
- **Cross-Module Coordination**: Seamless integration between different processing modules

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 Cross-Module Workflow Engine                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Workflow        │  │ Task            │  │ Workflow        │ │
│  │ Engine          │  │ Orchestrator    │  │ Monitor         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Workflow Manager                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Workflow Engine (`workflow_engine.py`)

**Purpose**: Core orchestration engine that manages workflow execution and lifecycle.

**Key Features**:
- Workflow definition and instance management
- Task execution and dependency resolution
- Cross-module coordination
- Workflow lifecycle management (start, pause, resume, cancel)
- Background execution loop with error handling

**Usage Example**:
```python
from integration.workflow_engine import WorkflowEngine

# Create workflow engine
engine = WorkflowEngine()

# Start the engine
await engine.start_engine()

# Register workflow definition
engine.register_workflow_definition(workflow_def)

# Create and start workflow instance
instance = await engine.create_workflow_instance(workflow_def.workflow_id)
success = await engine.start_workflow(instance.instance_id)

# Stop the engine
await engine.stop_engine()
```

### 2. Workflow Manager (`workflow_manager.py`)

**Purpose**: Manages workflow templates, versioning, and lifecycle.

**Key Features**:
- Template creation and management
- Version control and validation
- Workflow optimization and validation
- Template library and reuse
- Import/export capabilities

**Usage Example**:
```python
from integration.workflow_engine import WorkflowManager, WorkflowTask, TaskDependency

# Create workflow manager
manager = WorkflowManager()

# Create workflow template
tasks = [
    WorkflowTask(
        task_name="Data Extraction",
        task_type="module_operation",
        target_module="twin_registry",
        operation_name="extract_data"
    ),
    WorkflowTask(
        task_name="Data Processing",
        task_type="module_operation",
        target_module="ai_rag",
        operation_name="process_data"
    )
]

template = manager.create_workflow_template(
    name="Data Pipeline",
    description="Extract and process data workflow",
    workflow_type="data_pipeline",
    tasks=tasks,
    category="data_processing",
    tags=["extraction", "processing"]
)

# Create workflow from template
workflow_def = manager.create_workflow_from_template(
    f"{template.workflow_name}_{template.version}"
)
```

### 3. Task Orchestrator (`task_orchestrator.py`)

**Purpose**: Orchestrates task execution, scheduling, and resource management.

**Key Features**:
- Task scheduling and prioritization
- Resource allocation and management
- Parallel execution coordination
- Task dependency resolution
- Performance optimization

**Usage Example**:
```python
from integration.workflow_engine import TaskOrchestrator, WorkflowPriority

# Create task orchestrator
orchestrator = TaskOrchestrator(max_concurrent_tasks=10)

# Start orchestrator
await orchestrator.start_orchestrator()

# Submit tasks for execution
for task in workflow_tasks:
    await orchestrator.submit_task(task, priority=WorkflowPriority.HIGH)

# Get orchestrator status
status = orchestrator.get_orchestrator_status()
print(f"Running tasks: {status['running_tasks']}")
print(f"Queued tasks: {status['queued_tasks']}")

# Stop orchestrator
await orchestrator.stop_orchestrator()
```

### 4. Workflow Monitor (`workflow_monitor.py`)

**Purpose**: Provides real-time monitoring, alerting, and performance analytics.

**Key Features**:
- Real-time workflow monitoring
- Performance analytics and metrics
- Alerting and notifications
- Health checks and diagnostics
- Performance optimization recommendations

**Usage Example**:
```python
from integration.workflow_engine import WorkflowMonitor

# Create workflow monitor
monitor = WorkflowMonitor()

# Start monitoring
await monitor.start_monitoring()

# Register workflow for monitoring
monitor.register_workflow_for_monitoring(workflow_instance)

# Set performance thresholds
monitor.set_performance_thresholds("execution_time", {
    "warning": 300.0,  # 5 minutes
    "critical": 1800.0  # 30 minutes
})

# Get workflow health summary
health = monitor.get_workflow_health_summary()
print(f"Overall health: {health['status']}")
print(f"Health percentage: {health['health_percentage']:.1f}%")

# Get performance recommendations
recommendations = monitor.get_performance_recommendations(workflow_id)
for rec in recommendations:
    print(f"Recommendation: {rec}")

# Stop monitoring
await monitor.stop_monitoring()
```

## 📊 Data Models

### Core Enums

- **`TaskStatus`**: `pending`, `running`, `completed`, `failed`, `cancelled`, `skipped`, `retrying`
- **`WorkflowStatus`**: `draft`, `active`, `running`, `completed`, `failed`, `cancelled`, `paused`, `suspended`
- **`WorkflowTrigger`**: `manual`, `scheduled`, `event_driven`, `dependency_driven`, `api_call`
- **`WorkflowPriority`**: `low`, `normal`, `high`, `critical`

### Core Data Classes

- **`WorkflowDefinition`**: Template for workflow execution
- **`WorkflowInstance`**: Running instance of a workflow
- **`WorkflowTask`**: Individual task within a workflow
- **`TaskDependency`**: Dependencies between tasks
- **`WorkflowSchedule`**: Scheduling information for workflows
- **`WorkflowMetrics`**: Performance metrics and statistics

## 🚀 Getting Started

### 1. Import the Services

```python
from integration.workflow_engine import (
    WorkflowEngine,
    WorkflowManager,
    TaskOrchestrator,
    WorkflowMonitor,
    WorkflowDefinition,
    WorkflowTask,
    WorkflowPriority
)
```

### 2. Initialize Services

```python
# Initialize workflow engine
engine = WorkflowEngine()
manager = WorkflowManager()
orchestrator = TaskOrchestrator()
monitor = WorkflowMonitor()

# Start services
await engine.start_engine()
await orchestrator.start_orchestrator()
await monitor.start_monitoring()
```

### 3. Create and Execute Workflows

```python
# Create workflow definition
tasks = [
    WorkflowTask(
        task_name="Step 1",
        task_type="module_operation",
        target_module="module_a",
        operation_name="operation_1"
    ),
    WorkflowTask(
        task_name="Step 2",
        task_type="module_operation",
        target_module="module_b",
        operation_name="operation_2"
    )
]

workflow_def = manager.create_workflow_template(
    name="Sample Workflow",
    description="A sample workflow for demonstration",
    workflow_type="sample",
    tasks=tasks
)

# Register with engine
engine.register_workflow_definition(workflow_def)

# Create and start instance
instance = await engine.create_workflow_instance(workflow_def.workflow_id)
success = await engine.start_workflow(instance.instance_id)

# Register for monitoring
monitor.register_workflow_for_monitoring(instance)
```

### 4. Monitor and Manage

```python
# Get workflow status
status = engine.get_workflow_instance(instance.instance_id)
print(f"Workflow status: {status.status}")
print(f"Progress: {status.progress:.1f}%")

# Get orchestrator status
orch_status = orchestrator.get_orchestrator_status()
print(f"Running tasks: {orch_status['running_tasks']}")

# Get monitoring metrics
metrics = monitor.get_workflow_metrics(instance.instance_id)
print(f"Total executions: {metrics.total_executions}")
print(f"Success rate: {metrics.success_rate:.1%}")
```

## 🔍 Monitoring and Analytics

### Performance Metrics

```python
# Get global metrics
global_metrics = monitor.get_global_metrics()
print(f"Total workflows: {global_metrics['total_workflows_monitored']}")
print(f"Overall success rate: {global_metrics['overall_success_rate']:.1%}")

# Get workflow-specific metrics
workflow_metrics = monitor.get_workflow_metrics(instance.instance_id)
print(f"Average execution time: {workflow_metrics.average_execution_time:.1f}s")
print(f"Min execution time: {workflow_metrics.min_execution_time:.1f}s")
print(f"Max execution time: {workflow_metrics.max_execution_time:.1f}s")
```

### Health Monitoring

```python
# Get workflow health summary
health = monitor.get_workflow_health_summary()
print(f"Overall health: {health['status']}")
print(f"Healthy workflows: {health['healthy_workflows']}")
print(f"Warning workflows: {health['warning_workflows']}")
print(f"Critical workflows: {health['critical_workflows']}")

# Get performance alerts
alerts = monitor.get_performance_alerts(severity="critical")
for alert in alerts:
    print(f"Critical alert: {alert['message']}")
```

### Performance Recommendations

```python
# Get optimization recommendations
recommendations = monitor.get_performance_recommendations(instance.instance_id)
for rec in recommendations:
    print(f"Recommendation: {rec}")
```

## 🛡️ Error Handling and Recovery

### Task Retry Logic

```python
# Configure retry policy for tasks
task = WorkflowTask(
    task_name="Resilient Task",
    max_retries=3,
    retry_policy={
        "backoff_factor": 2,
        "max_delay": 300
    }
)
```

### Workflow Recovery

```python
# Pause and resume workflows
await engine.pause_workflow(instance.instance_id)
await engine.resume_workflow(instance.instance_id)

# Cancel workflows
await engine.cancel_workflow(instance.instance_id)
```

## 🔧 Configuration

### Performance Thresholds

```python
# Set custom performance thresholds
monitor.set_performance_thresholds("execution_time", {
    "warning": 600.0,   # 10 minutes
    "critical": 3600.0  # 1 hour
})

monitor.set_performance_thresholds("success_rate", {
    "warning": 0.90,    # 90%
    "critical": 0.75    # 75%
})
```

### Resource Limits

```python
# Configure task orchestrator limits
orchestrator = TaskOrchestrator(max_concurrent_tasks=20)

# Register module connectors with resource limits
orchestrator.register_module_connector("module_a", connector_a)
orchestrator.register_module_connector("module_b", connector_b)
```

## 🔄 Integration with Other Layers

### Module Integration Layer

- Automatically discovers available modules for workflow execution
- Integrates with module health monitoring for resource allocation
- Provides workflow status to module orchestrator

### External Communication Layer

- Uses event bridge for workflow notifications and alerts
- Integrates with data pipelines for workflow coordination
- Leverages module registry for service discovery

### Cross-Module Governance Layer

- Tracks workflow execution for compliance monitoring
- Provides governance policies for workflow validation
- Ensures data quality across workflow boundaries

## 🧪 Testing

### Unit Tests

```bash
# Run workflow engine tests
python -m pytest tests/integration/workflow_engine/
```

### Integration Tests

```bash
# Run full workflow engine tests
python scripts/test_workflow_engine.py
```

## 📚 API Reference

For detailed API documentation, see the individual service files:

- [`workflow_engine.py`](workflow_engine.py)
- [`workflow_manager.py`](workflow_manager.py)
- [`task_orchestrator.py`](task_orchestrator.py)
- [`workflow_monitor.py`](workflow_monitor.py)
- [`models.py`](models.py)

## 🤝 Contributing

When contributing to the workflow engine:

1. **Maintain Separation**: Don't modify the protected engine layer
2. **Follow Patterns**: Use the established async service patterns
3. **Add Tests**: Include comprehensive tests for new features
4. **Update Documentation**: Keep this README and service docs current
5. **Performance**: Consider the impact on workflow execution performance

## 📄 License

This workflow engine is part of the AAS Data Modeling Engine and follows the same licensing terms.

---

**Note**: The Cross-Module Workflow Engine is designed to work seamlessly with the existing engine while providing enterprise-grade workflow orchestration capabilities. It maintains the architectural principle of engine protection while enabling comprehensive cross-module workflow management and coordination.


