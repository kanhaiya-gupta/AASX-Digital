# External Communication Package

## 🌐 Overview

The External Communication Package provides the communication infrastructure for external modules within the AAS Data Modeling Engine, enabling seamless data flow and event-driven communication between distributed components.

This package serves as the **communication backbone** that connects your protected engine core with external task modules, providing enterprise-grade orchestration capabilities without modifying your existing codebase.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                External Communication Layer                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Module        │  │   Event         │  │   Data      │ │
│  │   Client        │  │   Bridge        │  │   Pipeline  │ │
│  │                 │  │                 │  │             │ │
│  │ • HTTP/GRPC     │  │ • Pub/Sub       │  │ • Stage     │ │
│  │ • Connection    │  │ • Event Routing │  │   Execution │ │
│  │   Pooling       │  │ • Delivery      │  │ • Dependency│ │
│  │ • Auth & Retry  │  │   Guarantees    │  │   Management│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐                                        │
│  │   External      │                                        │
│  │   Module        │                                        │
│  │   Registry      │                                        │
│  │                 │                                        │
│  │ • Endpoint      │                                        │
│  │   Management    │                                        │
│  │ • Health        │                                        │
│  │   Monitoring    │                                        │
│  │ • Load          │                                        │
│  │   Balancing     │                                        │
│  └─────────────────┘                                        │
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
│                    External Task Modules                    │
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

## 🚀 Core Components

### 1. **Module Client** (`module_client.py`)
**Purpose**: HTTP/GRPC client for communicating with external modules

**Features**:
- **Connection Management**: Automatic connection establishment and cleanup
- **Connection Pooling**: Efficient resource management with `ModuleClientPool`
- **Authentication**: Bearer token support for secure communication
- **Retry Logic**: Automatic retry with configurable attempts
- **Performance Monitoring**: Response time tracking and metrics
- **Error Handling**: Comprehensive error handling and fallback strategies

**Key Classes**:
- `ModuleClient`: Individual client for a module endpoint
- `ModuleClientPool`: Pool of clients for load balancing and failover

### 2. **Event Bridge** (`event_bridge.py`)
**Purpose**: Event-driven communication system for inter-module messaging

**Features**:
- **Pub/Sub Messaging**: Publish and subscribe to events
- **Event Routing**: Route events to specific modules or broadcast
- **Event Filtering**: Filter events by type and source
- **Delivery Guarantees**: Reliable event delivery with retry logic
- **Event Persistence**: Event history and replay capabilities
- **Performance Monitoring**: Event processing metrics and monitoring

**Key Classes**:
- `EventBridge`: Main event communication system
- `EventHandler`: Processes individual events
- `EventMessage`: Event data structure

### 3. **Data Pipeline** (`data_pipeline.py`)
**Purpose**: Orchestrate data flow between multiple modules

**Features**:
- **Stage Execution**: Execute pipeline stages sequentially or in parallel
- **Dependency Management**: Handle stage dependencies and execution order
- **Error Handling**: Comprehensive error handling and recovery
- **Progress Monitoring**: Real-time pipeline status and metrics
- **Event Integration**: Integrate with Event Bridge for workflow events

**Key Classes**:
- `DataPipeline`: Main pipeline orchestrator
- `PipelineExecutor`: Executes individual pipeline stages
- `PipelineConfig`: Pipeline configuration and setup

### 4. **External Module Registry** (`module_registry.py`)
**Purpose**: Manage external module endpoints and connections

**Features**:
- **Endpoint Registration**: Register and manage module endpoints
- **Health Monitoring**: Continuous health checks and status tracking
- **Connection Management**: Manage connection pools and load balancing
- **Service Discovery**: Discover and catalog available modules
- **Performance Analytics**: Comprehensive metrics and analytics

**Key Classes**:
- `ExternalModuleRegistry`: Main registry for managing endpoints
- `ModuleEndpoint`: Endpoint configuration and metadata

## 📊 Data Models

### Core Enums
- `EventType`: Types of events (DATA_UPDATE, MODULE_HEALTH, WORKFLOW_START, etc.)
- `PipelineStatus`: Pipeline stage status (PENDING, RUNNING, COMPLETED, FAILED, etc.)
- `CommunicationProtocol`: Supported protocols (HTTP, HTTPS, GRPC, WEBSOCKET, MQTT)

### Core Data Classes
- `EventMessage`: Event communication structure
- `ModuleEndpoint`: Module endpoint configuration
- `PipelineStage`: Individual pipeline stage definition
- `PipelineConfig`: Complete pipeline configuration
- `CommunicationMetrics`: Performance and health metrics

## 🔧 Usage Examples

### Basic Module Communication

```python
from src.integration.external_communication import (
    ModuleClient, ModuleEndpoint, CommunicationProtocol
)

# Create module endpoint
endpoint = ModuleEndpoint(
    module_name="ai_rag",
    base_url="http://localhost:8001",
    protocol=CommunicationProtocol.HTTP,
    timeout_seconds=30
)

# Create client and communicate
async with ModuleClient(endpoint) as client:
    # Health check
    health = await client.health_check()
    print(f"Module health: {health['status']}")
    
    # Send data
    response = await client.post_data("/api/process", {"text": "Hello AI!"})
    print(f"Response: {response['data']}")
```

### Event-Driven Communication

```python
from src.integration.external_communication import (
    EventBridge, EventType
)

# Create event bridge
event_bridge = EventBridge()
await event_bridge.start()

# Subscribe to events
def handle_data_update(event):
    print(f"Data updated: {event.payload}")

subscription_id = event_bridge.subscribe(
    topic="data_update",
    callback=handle_data_update,
    event_types=[EventType.DATA_UPDATE]
)

# Publish events
await event_bridge.publish_simple(
    event_type=EventType.DATA_UPDATE,
    source_module="engine",
    payload={"data_id": "123", "operation": "create"}
)
```

### Data Pipeline Orchestration

```python
from src.integration.external_communication import (
    DataPipeline, EventBridge
)

# Create event bridge
event_bridge = EventBridge()
await event_bridge.start()

# Define pipeline stages
stages = [
    {
        "name": "data_extraction",
        "module": "aasx",
        "operation": "extract",
        "dependencies": []
    },
    {
        "name": "ai_analysis",
        "module": "ai_rag",
        "operation": "analyze",
        "dependencies": ["data_extraction"]
    },
    {
        "name": "knowledge_graph_update",
        "module": "kg_neo4j",
        "operation": "update",
        "dependencies": ["ai_analysis"]
    }
]

# Create and run pipeline
pipeline = DataPipeline.create_simple_pipeline(
    name="data_processing_pipeline",
    stages=stages,
    event_bridge=event_bridge
)

await pipeline.start()

# Monitor pipeline status
status = pipeline.get_pipeline_status()
print(f"Pipeline status: {status['status']}")
```

### Module Registry Management

```python
from src.integration.external_communication import (
    ExternalModuleRegistry, ModuleEndpoint, CommunicationProtocol
)

# Create registry
registry = ExternalModuleRegistry()
await registry.start_monitoring()

# Register modules
endpoint = ModuleEndpoint(
    module_name="twin_registry",
    base_url="http://localhost:8002",
    protocol=CommunicationProtocol.HTTP
)

endpoint_id = registry.register_endpoint(endpoint)

# Test connection
connection_test = await registry.test_endpoint_connection(endpoint_id)
print(f"Connection test: {connection_test['success']}")

# Get registry summary
summary = registry.get_registry_summary()
print(f"Total endpoints: {summary['total_endpoints']}")
```

## 🔌 Integration Points

### With Module Integration Layer
- **Discovery Service**: Uses registry for module discovery
- **Connector Service**: Uses client pool for connections
- **Health Monitor**: Uses registry health monitoring
- **Data Sync**: Uses event bridge for sync events

### With Engine Core
- **Event Publishing**: Engine services can publish events
- **Data Pipelines**: Engine can orchestrate cross-module workflows
- **Health Monitoring**: Engine can monitor external module health

### With External Modules
- **HTTP/GRPC Communication**: Direct API communication
- **Event Subscription**: Modules can subscribe to relevant events
- **Health Reporting**: Modules report health status
- **Data Exchange**: Bidirectional data flow

## 📈 Performance Features

### Connection Pooling
- **Efficient Resource Management**: Reuse connections across requests
- **Load Balancing**: Distribute load across multiple clients
- **Failover Support**: Automatic failover to healthy endpoints

### Event Processing
- **Asynchronous Processing**: Non-blocking event handling
- **Queue Management**: Configurable event queue sizes
- **Batch Processing**: Process multiple events efficiently

### Health Monitoring
- **Continuous Monitoring**: Background health checks
- **Performance Metrics**: Response time and success rate tracking
- **Automatic Recovery**: Detect and recover from failures

## 🛡️ Security Features

### Authentication
- **Bearer Token Support**: Secure API communication
- **Configurable Auth**: Per-endpoint authentication settings
- **Token Management**: Secure token storage and rotation

### Communication Security
- **HTTPS Support**: Encrypted communication
- **Protocol Validation**: Validate communication protocols
- **Access Control**: Control access to endpoints

## 📊 Monitoring and Metrics

### Performance Metrics
- **Response Times**: Track API response performance
- **Success Rates**: Monitor communication success rates
- **Error Rates**: Track and analyze failures
- **Throughput**: Measure communication volume

### Health Metrics
- **Endpoint Health**: Monitor module availability
- **Connection Status**: Track connection pool health
- **Event Processing**: Monitor event bridge performance

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r src/integration/requirements.txt
```

### 2. Basic Setup
```python
from src.integration.external_communication import (
    EventBridge, ExternalModuleRegistry
)

# Initialize services
event_bridge = EventBridge()
registry = ExternalModuleRegistry()

# Start services
await event_bridge.start()
await registry.start_monitoring()
```

### 3. Register External Modules
```python
from src.integration.external_communication import ModuleEndpoint

# Register your external modules
endpoint = ModuleEndpoint(
    module_name="your_module",
    base_url="http://your-module-url",
    protocol=CommunicationProtocol.HTTP
)

endpoint_id = registry.register_endpoint(endpoint)
```

### 4. Start Communication
```python
# Publish events
await event_bridge.publish_simple(
    event_type=EventType.DATA_UPDATE,
    source_module="engine",
    payload={"message": "Hello from engine!"}
)

# Create data pipelines
pipeline = DataPipeline.create_simple_pipeline(
    name="your_pipeline",
    stages=[...],
    event_bridge=event_bridge
)

await pipeline.start()
```

## 🔍 Testing

Run the comprehensive test suite to verify all components:

```bash
# Run all tests
python scripts/test_external_communication.py

# Run specific component tests
python scripts/test_external_communication.py --component module_client
python scripts/test_external_communication.py --component event_bridge
python scripts/test_external_communication.py --component data_pipeline
python scripts/test_external_communication.py --component module_registry
```

## 📚 API Reference

### Module Client
- `ModuleClient.connect()`: Establish connection
- `ModuleClient.health_check()`: Check module health
- `ModuleClient.send_request()`: Send HTTP request
- `ModuleClient.send_event()`: Send event message

### Event Bridge
- `EventBridge.start()`: Start event processing
- `EventBridge.subscribe()`: Subscribe to events
- `EventBridge.publish()`: Publish events
- `EventBridge.get_metrics()`: Get performance metrics

### Data Pipeline
- `DataPipeline.start()`: Start pipeline execution
- `DataPipeline.get_pipeline_status()`: Get execution status
- `DataPipeline.get_all_results()`: Get execution results

### Module Registry
- `ExternalModuleRegistry.register_endpoint()`: Register module
- `ExternalModuleRegistry.start_monitoring()`: Start health monitoring
- `ExternalModuleRegistry.get_registry_summary()`: Get registry overview

## 🎯 Use Cases

### 1. **Real-time Data Synchronization**
- Modules publish data updates via events
- Other modules subscribe and react to changes
- Maintain data consistency across the system

### 2. **Workflow Orchestration**
- Define multi-stage data processing pipelines
- Coordinate execution across multiple modules
- Handle dependencies and error recovery

### 3. **Health Monitoring**
- Continuous monitoring of external modules
- Automatic failover and recovery
- Performance analytics and alerting

### 4. **Event-Driven Architecture**
- Loose coupling between modules
- Asynchronous communication
- Scalable event processing

## 🔧 Configuration

### Environment Variables
```bash
# Module communication settings
EXTERNAL_COMM_MAX_ENDPOINTS=100
EXTERNAL_COMM_HEALTH_CHECK_INTERVAL=60
EXTERNAL_COMM_MAX_QUEUE_SIZE=10000

# Connection settings
EXTERNAL_COMM_TIMEOUT_SECONDS=30
EXTERNAL_COMM_RETRY_ATTEMPTS=3
EXTERNAL_COMM_MAX_CLIENTS=10
```

### Configuration Files
```yaml
# config/external_communication.yaml
module_registry:
  max_endpoints: 100
  health_check_interval: 60
  
event_bridge:
  max_queue_size: 10000
  max_history_size: 1000
  
data_pipeline:
  max_concurrent_stages: 3
  default_timeout: 300
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check endpoint URLs and network connectivity
   - Verify authentication tokens
   - Check firewall and security settings

2. **Event Processing Issues**
   - Verify event bridge is running
   - Check event queue size limits
   - Monitor event handler performance

3. **Pipeline Execution Failures**
   - Check stage dependencies
   - Verify module availability
   - Review error logs and recovery logic

### Debug Mode
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Component-specific debugging
logging.getLogger('src.integration.external_communication').setLevel(logging.DEBUG)
```

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies
3. Run tests to verify setup
4. Make changes and run tests
5. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This package is part of the AAS Data Modeling Engine and follows the same licensing terms.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Run the test suite to verify functionality
4. Create an issue with detailed error information

---

**🎉 The External Communication Package provides the foundation for enterprise-grade module orchestration and communication!**
