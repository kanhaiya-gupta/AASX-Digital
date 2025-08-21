# Cross-Module Governance Layer

## Overview

The Cross-Module Governance layer ensures data integrity, compliance, and quality across all external modules within the AAS Data Modeling Engine. This layer provides comprehensive governance capabilities that work seamlessly with the existing engine while maintaining the separation of concerns.

## 🎯 Purpose

The governance layer serves as the **guardian** of data integrity across module boundaries, ensuring:

- **Data Lineage Tracking**: Complete visibility into how data flows between modules
- **Compliance Monitoring**: Automated enforcement of governance policies and business rules
- **Quality Assurance**: Continuous monitoring of data quality metrics
- **Policy Enforcement**: Automated validation and enforcement of governance policies

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Cross-Module Governance                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Data Lineage    │  │ Compliance      │  │ Quality     │ │
│  │ Service         │  │ Service         │  │ Monitor     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Policy Enforcer Service                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Cross-Module Lineage Service (`cross_module_lineage.py`)

**Purpose**: Tracks data flow and transformations across module boundaries.

**Key Features**:
- Automatic lineage discovery and tracking
- Data transformation history
- Compliance status tracking
- Lineage querying and visualization
- Export capabilities for audit purposes

**Usage Example**:
```python
from integration.cross_module_governance import CrossModuleLineageService

# Create lineage service
lineage_service = CrossModuleLineageService()

# Start tracking
await lineage_service.start_lineage_tracking()

# Create data lineage
lineage = lineage_service.create_lineage(
    source_module="twin_registry",
    target_module="ai_rag",
    source_data_id="twin_001",
    target_data_id="analysis_001",
    lineage_type=LineageType.DATA_FLOW,
    transformation_details={"operation": "enrichment", "fields_added": 5}
)

# Get lineage path between modules
path = lineage_service.get_data_flow_path("twin_registry", "kg_neo4j")
```

### 2. Module Compliance Service (`module_compliance.py`)

**Purpose**: Ensures all modules comply with governance policies and business rules.

**Key Features**:
- Compliance rule management
- Policy violation detection
- Compliance scoring and reporting
- Automated compliance checks
- Violation tracking and resolution

**Usage Example**:
```python
from integration.cross_module_governance import ModuleComplianceService, ComplianceRule, PolicySeverity

# Create compliance service
compliance_service = ModuleComplianceService()

# Add compliance rule
rule = ComplianceRule(
    rule_name="Data Privacy Check",
    rule_type="data_privacy",
    applicable_modules=["ai_rag", "kg_neo4j"],
    rule_conditions={"data_classification": "confidential"},
    severity=PolicySeverity.HIGH
)
compliance_service.add_compliance_rule(rule)

# Check module compliance
result = compliance_service.check_module_compliance(
    module_name="ai_rag",
    data_id="data_001",
    data_context={"data_classification": "public", "user_id": "user_123"}
)
```

### 3. Data Quality Monitor Service (`data_quality_monitor.py`)

**Purpose**: Monitors data quality across all modules and provides quality metrics.

**Key Features**:
- Quality metrics collection
- Threshold management and alerts
- Trend analysis and reporting
- Quality improvement recommendations
- Automated quality monitoring

**Usage Example**:
```python
from integration.cross_module_governance import DataQualityMonitorService

# Create quality monitor
quality_monitor = DataQualityMonitorService()

# Start monitoring
await quality_monitor.start_quality_monitoring()

# Record quality metric
metric = quality_monitor.record_quality_metric(
    metric_name="completeness",
    metric_value=0.95,
    module_name="twin_registry",
    data_id="twin_001",
    metric_description="Data completeness percentage"
)

# Get quality recommendations
recommendations = quality_monitor.get_quality_recommendations("twin_registry")
```

### 4. Governance Policy Enforcer Service (`governance_policy_enforcer.py`)

**Purpose**: Enforces governance policies and handles policy violations.

**Key Features**:
- Policy validation and enforcement
- Violation detection and handling
- Automated enforcement actions
- Policy compliance reporting
- Violation resolution tracking

**Usage Example**:
```python
from integration.cross_module_governance import GovernancePolicyEnforcerService, GovernancePolicy

# Create policy enforcer
enforcer = GovernancePolicyEnforcerService()

# Start enforcement
await enforcer.start_policy_enforcement()

# Add governance policy
policy = GovernancePolicy(
    policy_name="Data Access Control",
    policy_type="access_control",
    applicable_modules=["twin_registry", "ai_rag"],
    enforcement_level="strict"
)
enforcer.add_policy(policy)

# Validate operation
result = enforcer.validate_operation(
    module_name="ai_rag",
    operation_type="data_read",
    data_context={"user_role": "analyst", "data_sensitivity": "high"}
)
```

## 📊 Data Models

### Core Enums

- **`ComplianceStatus`**: `compliant`, `non_compliant`, `pending`, `error`, `unknown`
- **`QualityStatus`**: `excellent`, `good`, `acceptable`, `poor`, `critical`, `unknown`
- **`PolicySeverity`**: `low`, `medium`, `high`, `critical`
- **`LineageType`**: `data_flow`, `transformation`, `derivation`, `aggregation`, `filtering`, `enrichment`

### Core Data Classes

- **`DataLineage`**: Tracks data flow between modules
- **`ComplianceRule`**: Defines compliance requirements
- **`QualityMetric`**: Represents data quality measurements
- **`GovernancePolicy`**: Defines governance policies
- **`PolicyViolation`**: Records policy violations

## 🚀 Getting Started

### 1. Import the Services

```python
from integration.cross_module_governance import (
    CrossModuleLineageService,
    ModuleComplianceService,
    DataQualityMonitorService,
    GovernancePolicyEnforcerService
)
```

### 2. Initialize Services

```python
# Initialize all governance services
lineage_service = CrossModuleLineageService()
compliance_service = ModuleComplianceService()
quality_monitor = DataQualityMonitorService()
policy_enforcer = GovernancePolicyEnforcerService()
```

### 3. Start Monitoring

```python
# Start all services
await lineage_service.start_lineage_tracking()
await compliance_service.start_compliance_monitoring()
await quality_monitor.start_quality_monitoring()
await policy_enforcer.start_policy_enforcement()
```

### 4. Configure Governance Rules

```python
# Add compliance rules
compliance_rule = ComplianceRule(
    rule_name="Data Validation",
    rule_type="data_quality",
    applicable_modules=["twin_registry"],
    rule_conditions={"min_quality_score": 0.8},
    severity=PolicySeverity.MEDIUM
)
compliance_service.add_compliance_rule(compliance_rule)

# Set quality thresholds
quality_monitor.set_quality_thresholds("accuracy", {
    "excellent": 0.98,
    "good": 0.90,
    "acceptable": 0.80,
    "poor": 0.60,
    "critical": 0.40
})
```

## 🔍 Monitoring and Reporting

### Lineage Reports

```python
# Get lineage summary
summary = lineage_service.get_lineage_summary()

# Export lineage data
export_data = lineage_service.export_lineage_data("json")

# Get data flow path
path = lineage_service.get_data_flow_path("module_a", "module_b")
```

### Compliance Reports

```python
# Get compliance summary
summary = compliance_service.get_compliance_summary()

# Get module compliance status
status = compliance_service.get_module_compliance_status("twin_registry")

# Export compliance report
report = compliance_service.export_compliance_report("json")
```

### Quality Reports

```python
# Get quality summary
summary = quality_monitor.get_quality_summary()

# Get quality trends
trends = quality_monitor.get_quality_trend("accuracy", "twin_registry", days=30)

# Get quality recommendations
recommendations = quality_monitor.get_quality_recommendations("twin_registry")
```

### Enforcement Reports

```python
# Get enforcement summary
summary = policy_enforcer.get_enforcement_summary()

# Get policy violations
violations = policy_enforcer.get_policy_violations(
    module_name="ai_rag",
    severity=PolicySeverity.HIGH,
    resolved_only=False
)

# Export enforcement report
report = policy_enforcer.export_enforcement_report("json")
```

## 🛡️ Security and Compliance

### Data Privacy

- All governance data is stored securely
- Access controls for governance operations
- Audit trails for all governance actions

### Compliance Standards

- Supports industry-standard compliance frameworks
- Configurable compliance rules and policies
- Automated compliance monitoring and reporting

### Audit and Logging

- Comprehensive logging of all governance activities
- Audit trails for policy violations and resolutions
- Export capabilities for compliance audits

## 🔧 Configuration

### Quality Thresholds

```python
# Configure quality thresholds for specific metrics
quality_monitor.set_quality_thresholds("completeness", {
    "excellent": 0.95,
    "good": 0.85,
    "acceptable": 0.70,
    "poor": 0.50,
    "critical": 0.30
})
```

### Monitoring Intervals

```python
# Services automatically adjust monitoring intervals based on load
# Default intervals:
# - Lineage tracking: 30 seconds
# - Compliance monitoring: 60 seconds
# - Quality monitoring: 60 seconds
# - Policy enforcement: 30 seconds
```

## 🚨 Error Handling

### Graceful Degradation

- Services continue operating even if individual components fail
- Automatic retry mechanisms for failed operations
- Comprehensive error logging and reporting

### Recovery Mechanisms

- Automatic cleanup of old data
- Violation resolution workflows
- Policy violation escalation procedures

## 📈 Performance Considerations

### Scalability

- Efficient indexing for fast queries
- Background processing for monitoring tasks
- Configurable cleanup intervals

### Resource Management

- Automatic cleanup of old metrics and violations
- Memory-efficient data structures
- Configurable retention policies

## 🔄 Integration with Other Layers

### Module Integration Layer

- Automatically discovers modules for governance
- Integrates with module health monitoring
- Provides governance status to module orchestrator

### External Communication Layer

- Uses event bridge for governance notifications
- Integrates with data pipelines for quality monitoring
- Leverages module registry for compliance checks

## 🧪 Testing

### Unit Tests

```bash
# Run governance layer tests
python -m pytest tests/integration/cross_module_governance/
```

### Integration Tests

```bash
# Run full integration tests
python scripts/test_cross_module_governance.py
```

## 📚 API Reference

For detailed API documentation, see the individual service files:

- [`cross_module_lineage.py`](cross_module_lineage.py)
- [`module_compliance.py`](module_compliance.py)
- [`data_quality_monitor.py`](data_quality_monitor.py)
- [`governance_policy_enforcer.py`](governance_policy_enforcer.py)

## 🤝 Contributing

When contributing to the governance layer:

1. **Maintain Separation**: Don't modify the protected engine layer
2. **Follow Patterns**: Use the established async service patterns
3. **Add Tests**: Include comprehensive tests for new features
4. **Update Documentation**: Keep this README and service docs current

## 📄 License

This governance layer is part of the AAS Data Modeling Engine and follows the same licensing terms.

---

**Note**: The Cross-Module Governance layer is designed to work seamlessly with the existing engine while providing enterprise-grade governance capabilities. It maintains the architectural principle of engine protection while enabling comprehensive cross-module governance.
