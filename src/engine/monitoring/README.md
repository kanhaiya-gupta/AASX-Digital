# Monitoring and Observability System

## Overview

The AAS Data Modeling Engine includes a comprehensive monitoring and observability system that provides real-time insights into system performance, health, and operational status. This system is designed to be production-ready with enterprise-grade features for monitoring, alerting, and performance analysis.

## 🏗️ Architecture

The monitoring system is built with a modular architecture consisting of several core components:

```
src/engine/monitoring/
├── __init__.py              # Main module exports
├── monitoring_config.py      # Configuration management
├── metrics_collector.py      # Metrics collection and aggregation
├── health_monitor.py         # Health monitoring and checks
├── performance_profiler.py   # Performance profiling and tracing
├── resource_monitor.py       # System resource monitoring
├── alert_manager.py          # Alerting and notification system
├── monitoring_middleware.py  # Web framework integration
└── README.md                 # This documentation
```

## 🚀 Features

### 1. Metrics Collection
- **Real-time metrics**: CPU, memory, disk, network usage
- **Application metrics**: Database connections, cache performance, API calls
- **Custom metrics**: User-defined metrics with automatic collection
- **Multiple formats**: JSON, CSV, Prometheus export support
- **Historical data**: Configurable retention and cleanup policies

### 2. Health Monitoring
- **Component health checks**: Database, cache, security, messaging systems
- **Dependency tracking**: Hierarchical health status with dependencies
- **Automatic monitoring**: Configurable check intervals and timeouts
- **Health aggregation**: Overall system health status calculation
- **Critical component identification**: Fail-fast detection for critical services

### 3. Performance Profiling
- **Operation tracing**: Detailed timing for all system operations
- **Slow operation detection**: Configurable thresholds with automatic alerting
- **Performance metrics**: P50, P95, P99 percentile calculations
- **Sampling support**: Configurable sampling rates for high-volume operations
- **Decorator support**: Easy integration with existing code

### 4. Resource Monitoring
- **System resources**: CPU, memory, disk, network monitoring
- **Application resources**: Database connections, cache usage, queue lengths
- **Custom collectors**: Extensible resource monitoring framework
- **Threshold management**: Configurable warning and error thresholds
- **Trend analysis**: Resource usage trend detection and reporting

### 5. Alert Management
- **Multi-channel alerts**: Log, email, and custom notification channels
- **Configurable rules**: Flexible alert rule definition and management
- **Alert lifecycle**: Acknowledgment, resolution, and suppression support
- **Cooldown periods**: Prevent alert spam with intelligent throttling
- **Severity levels**: Info, Warning, Error, and Critical alert levels

### 6. Web Framework Integration
- **Flask integration**: Drop-in middleware for Flask applications
- **Django integration**: Django middleware class
- **FastAPI integration**: FastAPI middleware support
- **Request monitoring**: Full request/response lifecycle tracking
- **Performance metrics**: API response time and error rate monitoring

## 📋 Quick Start

### Basic Usage

```python
from engine.monitoring import (
    MonitoringConfig, MetricsCollector, HealthMonitor, 
    PerformanceProfiler, ResourceMonitor, AlertManager
)

# Create configuration
config = MonitoringConfig()

# Initialize components
metrics = MetricsCollector(config)
health = HealthMonitor(config)
profiler = PerformanceProfiler(config)
resources = ResourceMonitor(config)
alerts = AlertManager(config)

# Start monitoring
metrics.start_collection()
health.start_monitoring()
resources.start_monitoring()
```

### Performance Profiling

```python
# Using decorator
@profiler.profile_function("database.query")
def query_database():
    # Database operation
    pass

# Using context manager
with profiler.profile_context("api.request"):
    # API operation
    pass

# Manual profiling
op_id = profiler.start_operation("custom.operation")
# ... do work ...
profiler.end_operation(op_id, success=True)
```

### Custom Metrics

```python
# Add custom metric collector
def collect_custom_metric():
    return {"custom_value": 42}

metrics.add_custom_metric("custom.metric", collect_custom_metric)

# Record values
metrics.record_value("business.metric", 100)
metrics.increment_counter("user.actions")
metrics.set_gauge("active.users", 150)
```

### Health Checks

```python
# Add custom health check
async def custom_health_check():
    # Perform health check
    return {
        "status": "healthy",
        "message": "Custom service is working",
        "details": {"custom_info": "value"}
    }

health.add_health_check(
    "custom_service",
    "Custom service health check",
    custom_health_check,
    critical=True
)
```

### Alert Rules

```python
# Create custom alert rule
from engine.monitoring.alert_manager import AlertRule, AlertSeverity

rule = AlertRule(
    name="high_error_rate",
    description="Error rate exceeds threshold",
    condition="error_rate > 0.1",
    severity=AlertSeverity.ERROR,
    notification_channels=["log", "email"]
)

alerts.add_alert_rule(rule)
```

## 🔧 Configuration

### Environment Variables

```bash
# Enable/disable monitoring
export MONITORING_ENABLED=true

# Set environment
export MONITORING_ENVIRONMENT=production

# Enable debug mode
export MONITORING_DEBUG=true

# Service configuration
export MONITORING_SERVICE_NAME=my-service
export MONITORING_VERSION=1.0.0
```

### Configuration File

```python
# Create custom configuration
config = MonitoringConfig()

# Metrics configuration
config.metrics.collection_interval = 30  # seconds
config.metrics.retention_period = 86400  # 24 hours
config.metrics.max_metrics_history = 5000

# Health monitoring
config.health.check_interval = 15  # seconds
config.health.timeout = 5  # seconds
config.health.max_failures = 3

# Performance profiling
config.performance.slow_query_threshold = 2.0  # seconds
config.performance.sampling_rate = 0.1  # 10%

# Resource monitoring
config.resources.collection_interval = 10  # seconds
config.resources.monitor_cpu = True
config.resources.monitor_memory = True

# Alerting
config.alerts.email_recipients = ["admin@example.com"]
config.alerts.smtp_server = "smtp.example.com"
config.alerts.smtp_port = 587
```

## 🌐 Web Framework Integration

### Flask Integration

```python
from flask import Flask
from engine.monitoring import MonitoringMiddleware

app = Flask(__name__)

# Add monitoring middleware
monitoring = MonitoringMiddleware(config, metrics, profiler, alerts)
app = monitoring.flask_middleware(app)
```

### Django Integration

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware ...
    'engine.monitoring.monitoring_middleware.DjangoMonitoringMiddleware',
]

# Initialize monitoring in your app
from engine.monitoring import MonitoringMiddleware
monitoring = MonitoringMiddleware(config, metrics, profiler, alerts)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from engine.monitoring import MonitoringMiddleware

app = FastAPI()

# Add monitoring middleware
monitoring = MonitoringMiddleware(config, metrics, profiler, alerts)
app = monitoring.fastapi_middleware(app)
```

## 📊 Data Export

### Export Formats

```python
# Export metrics
metrics.export_metrics("json")      # JSON format
metrics.export_metrics("csv")       # CSV format
metrics.export_metrics("prometheus") # Prometheus format

# Export performance data
profiler.export_performance_data("json")

# Export resource data
resources.export_resource_data("json")

# Export alerts
alerts.export_alerts("json")
```

### Export Directory Structure

```
monitoring_exports/
├── metrics_20231201_143022.json
├── performance_20231201_143022.json
├── resources_20231201_143022.json
└── alerts_20231201_143022.json
```

## 🔍 Monitoring Dashboard

### Health Status

```python
# Get overall health
overall_health = health.get_overall_health()
print(f"System Health: {overall_health.value}")

# Get health summary
health_summary = health.get_health_summary()
print(f"Components: {health_summary['components']}")
```

### Performance Metrics

```python
# Get operation summary
perf_summary = profiler.get_operation_summary()
print(f"Total Operations: {perf_summary['total_operations']}")

# Get slow operations
slow_ops = profiler.get_slow_operations(limit=10)
for op in slow_ops:
    print(f"Slow: {op.operation_name} - {op.duration:.3f}s")
```

### Resource Usage

```python
# Get resource summary
resource_summary = resources.get_resource_summary(window_minutes=60)
print(f"CPU Usage: {resource_summary['system_resources']['cpu']['average']:.1f}%")

# Get resource trends
cpu_trend = resources.get_resource_trends("cpu", window_minutes=60)
print(f"CPU Trend: {cpu_trend['trend']}")
```

### Alert Summary

```python
# Get alert summary
alert_summary = alerts.get_alert_summary()
print(f"Active Alerts: {alert_summary['active_alerts']}")

# Get active alerts
active_alerts = alerts.get_active_alerts()
for alert in active_alerts:
    print(f"Alert: {alert.title} - {alert.severity.value}")
```

## 🧪 Testing

### Run Test Suite

```bash
# Run comprehensive monitoring tests
python scripts/test_monitoring_system.py
```

### Test Individual Components

```python
# Test metrics collection
from engine.monitoring import MetricsCollector
metrics = MetricsCollector(config)
metrics.record_value("test.metric", 42)

# Test health monitoring
from engine.monitoring import HealthMonitor
health = HealthMonitor(config)
health_summary = health.get_health_summary()

# Test performance profiling
from engine.monitoring import PerformanceProfiler
profiler = PerformanceProfiler(config)
with profiler.profile_context("test.operation"):
    time.sleep(0.1)
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the `src` directory is in your Python path
2. **Configuration Issues**: Check environment variables and configuration values
3. **Performance Impact**: Adjust sampling rates and collection intervals
4. **Memory Usage**: Configure appropriate retention periods and history limits

### Debug Mode

```python
# Enable debug mode
config.debug_mode = True

# Check component status
print(f"Metrics Collection: {metrics._running}")
print(f"Health Monitoring: {health._running}")
print(f"Resource Monitoring: {resources._running}")
```

### Logging

```python
import logging

# Configure logging for monitoring components
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('engine.monitoring')
logger.setLevel(logging.DEBUG)
```

## 📈 Performance Considerations

### Optimization Tips

1. **Sampling**: Use sampling rates for high-volume operations
2. **Retention**: Configure appropriate data retention periods
3. **Collection Intervals**: Balance monitoring frequency with system impact
4. **Export Scheduling**: Use background tasks for data export
5. **Memory Management**: Monitor memory usage of monitoring components

### Scaling

- **Horizontal Scaling**: Each service instance runs its own monitoring
- **Centralized Collection**: Use external monitoring systems (Prometheus, Grafana)
- **Data Aggregation**: Implement centralized metrics aggregation
- **Alert Consolidation**: Use alert deduplication and correlation

## 🔐 Security

### Access Control

- **Read-only Access**: Monitoring data should be read-only for most users
- **Admin Access**: Configuration changes require administrative privileges
- **Audit Logging**: All monitoring configuration changes are logged
- **Data Privacy**: Ensure sensitive data is not exposed in metrics

### Network Security

- **Internal Access**: Restrict monitoring endpoints to internal networks
- **Authentication**: Implement authentication for monitoring APIs
- **Encryption**: Use HTTPS for monitoring data transmission
- **Firewall Rules**: Configure appropriate firewall rules

## 📚 API Reference

### Core Classes

- `MonitoringConfig`: Configuration management
- `MetricsCollector`: Metrics collection and management
- `HealthMonitor`: Health monitoring and checks
- `PerformanceProfiler`: Performance profiling and tracing
- `ResourceMonitor`: System resource monitoring
- `AlertManager`: Alert management and notification
- `MonitoringMiddleware`: Web framework integration

### Key Methods

- `start_collection()`: Start automatic data collection
- `stop_collection()`: Stop automatic data collection
- `get_summary()`: Get component summary information
- `export_data()`: Export data to various formats
- `reset_data()`: Reset all collected data

## 🤝 Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python scripts/test_monitoring_system.py`
4. Make changes and ensure tests pass
5. Submit pull request

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings
- Write unit tests for new functionality
- Update documentation for API changes

## 📄 License

This monitoring system is part of the AAS Data Modeling Engine and follows the same license terms.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the test suite for usage examples
3. Check existing issues in the repository
4. Create a new issue with detailed information

---

**Note**: This monitoring system is designed for production use but should be thoroughly tested in your specific environment before deployment.




