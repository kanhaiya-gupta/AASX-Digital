# Twin Registry Implementation

A comprehensive, world-class digital twin registry system for AASX data processing and management.

## 🏗️ Architecture Overview

The Twin Registry is designed as a centralized coordination hub that manages digital twin lifecycle, relationships, instances, and synchronization without duplicating data from other modules. It uses a modern JSON-field-based database schema and event-driven architecture for loose coupling.

### Core Design Principles

- **Reference Hub**: Links to other modules via IDs, doesn't duplicate their data
- **Two-Phase Population**: Basic registration on file upload, enhanced data after ETL completion
- **Event-Driven**: Uses event bus for loose coupling between components
- **Modular Design**: Separate concerns into distinct, testable modules
- **JSON Flexibility**: Stores complex data structures as JSON for extensibility

## 📊 Database Schema

### Main Table: `twin_registry` (53 fields)

```sql
CREATE TABLE twin_registry (
    registry_id TEXT PRIMARY KEY,
    twin_name TEXT NOT NULL,
    registry_type TEXT NOT NULL CHECK (registry_type IN ('extraction', 'generation', 'hybrid')),
    workflow_source TEXT NOT NULL,
    aasx_integration_id TEXT,
    user_id TEXT,
    org_id TEXT,
    project_id TEXT,
    use_case_id TEXT,
    file_id TEXT,
    file_path TEXT,
    file_type TEXT,
    file_size_bytes INTEGER,
    file_hash TEXT,
    file_upload_timestamp TEXT,
    processing_status TEXT DEFAULT 'pending',
    processing_start_time TEXT,
    processing_end_time TEXT,
    processing_duration_ms REAL,
    output_directory TEXT,
    output_formats TEXT, -- JSON array
    extracted_data_summary TEXT, -- JSON object
    quality_score REAL DEFAULT 0.0,
    validation_status TEXT DEFAULT 'pending',
    validation_errors TEXT, -- JSON array
    lifecycle_status TEXT DEFAULT 'created',
    lifecycle_phase TEXT DEFAULT 'initialization',
    lifecycle_events TEXT, -- JSON array
    relationships TEXT, -- JSON array
    instances TEXT, -- JSON array
    sync_status TEXT, -- JSON object
    security_level TEXT DEFAULT 'standard',
    access_control TEXT, -- JSON object
    data_privacy_level TEXT DEFAULT 'private',
    compliance_status TEXT DEFAULT 'pending',
    audit_trail TEXT, -- JSON array
    tags TEXT, -- JSON array
    metadata TEXT, -- JSON object
    configuration TEXT, -- JSON object
    performance_metrics TEXT, -- JSON object
    health_status TEXT DEFAULT 'unknown',
    health_score REAL DEFAULT 0.0,
    last_health_check TEXT,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    version TEXT DEFAULT '1.0.0',
    model_version TEXT DEFAULT '1.0.0',
    description TEXT,
    notes TEXT
);
```

### Metrics Table: `twin_registry_metrics` (19 fields)

```sql
CREATE TABLE twin_registry_metrics (
    metric_id TEXT PRIMARY KEY,
    registry_id TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    health_score REAL DEFAULT 0.0,
    response_time_ms REAL DEFAULT 0.0,
    throughput_ops_per_sec REAL DEFAULT 0.0,
    error_rate REAL DEFAULT 0.0,
    availability_percent REAL DEFAULT 100.0,
    resource_usage TEXT, -- JSON object
    performance_indicators TEXT, -- JSON object
    quality_metrics TEXT, -- JSON object
    compliance_metrics TEXT, -- JSON object
    security_metrics TEXT, -- JSON object
    business_metrics TEXT, -- JSON object
    custom_metrics TEXT, -- JSON object
    alerts TEXT, -- JSON array
    recommendations TEXT, -- JSON array
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registry_id) REFERENCES twin_registry(registry_id)
);
```

## 🏛️ Module Structure

```
src/twin_registry/
├── __init__.py                    # Main module initialization
├── models/                        # Data models and schemas
│   ├── __init__.py
│   ├── twin_registry.py          # Main TwinRegistry model (53 fields)
│   ├── twin_registry_metrics.py  # Metrics model (19 fields)
│   ├── twin_lifecycle.py         # Lifecycle events and status
│   ├── twin_relationship.py      # Relationship definitions
│   ├── twin_instance.py          # Instance definitions
│   └── twin_sync.py              # Synchronization models
├── repositories/                  # Data access layer
│   ├── __init__.py
│   ├── twin_registry_repository.py      # Main registry CRUD
│   ├── twin_registry_metrics_repository.py # Metrics CRUD
│   ├── twin_lifecycle_repository.py     # Lifecycle management
│   ├── twin_relationship_repository.py  # Relationship management
│   ├── twin_instance_repository.py      # Instance management
│   └── twin_sync_repository.py          # Sync management
├── core/                          # Business logic services
│   ├── __init__.py
│   ├── twin_registry_service.py  # Main registry service
│   ├── twin_lifecycle_service.py # Lifecycle management
│   ├── twin_relationship_service.py # Relationship management
│   ├── twin_instance_service.py  # Instance management
│   └── twin_sync_service.py      # Sync management
├── populator/                     # Population logic
│   ├── __init__.py
│   ├── twin_registry_populator.py # Main population orchestrator
│   ├── phase1_upload_populator.py # File upload → Basic registry
│   ├── phase2_etl_populator.py   # ETL → Enhanced registry
│   ├── population_coordinator.py  # Phase coordination
│   ├── population_triggers.py    # Event triggers
│   └── population_validator.py   # Data validation
├── events/                        # Event system
│   ├── __init__.py
│   ├── event_bus.py              # Event bus implementation
│   ├── event_handlers.py         # ETL event handlers
│   ├── event_types.py            # Event definitions
│   └── event_logger.py           # Event logging
├── config/                        # Configuration
│   ├── __init__.py
│   ├── population_config.py      # Config management
│   ├── validation_rules.py       # Validation rules
│   └── population_templates.py   # Population templates
├── integration/                   # External integrations
│   ├── __init__.py
│   ├── etl_integration.py        # ETL pipeline hooks
│   ├── file_upload_integration.py # File upload hooks
│   └── ai_rag_integration.py     # AI/RAG integration
└── utils/                         # Utilities
    ├── population_helpers.py     # Helper functions
    ├── quality_calculator.py     # Quality scoring
    └── metadata_extractor.py     # Metadata extraction
```

## 🔄 Two-Phase Population System

### Phase 1: File Upload Population
- **Trigger**: File upload completion
- **Data**: Basic file information, user context, project details
- **Purpose**: Immediate twin registration for tracking

### Phase 2: ETL Completion Population
- **Trigger**: ETL pipeline completion
- **Data**: Enhanced processing results, output files, quality metrics
- **Purpose**: Complete twin information for operational use

## 🚀 Key Features

### 1. **Automatic Population**
- Triggers automatically on file upload and ETL completion
- No manual intervention required
- Configurable population rules and validation

### 2. **Comprehensive Tracking**
- 53 fields covering all aspects of digital twin lifecycle
- Quality scoring and validation status
- Performance metrics and health monitoring

### 3. **Flexible Data Storage**
- JSON fields for complex, extensible data structures
- No schema changes needed for new data types
- Efficient querying and indexing

### 4. **Event-Driven Architecture**
- Loose coupling between components
- Asynchronous processing for better performance
- Extensible event system

### 5. **Integration Ready**
- Built-in ETL pipeline integration
- File upload system integration
- AI/RAG system integration points

## 🔌 Integration Points

### ETL Pipeline Integration
```python
# Automatically triggered after ETL completion
from webapp.modules.aasx.etl_twin_registry_integration import get_etl_integration

integration = get_etl_integration()
# Population happens automatically
```

### File Upload Integration
```python
# Automatically triggered after file upload
from webapp.modules.aasx.file_upload_twin_registry_integration import get_file_upload_integration

integration = get_file_upload_integration()
# Population happens automatically
```

### Manual Population
```python
# Manual population trigger
from src.twin_registry.populator import TwinRegistryPopulator

populator = TwinRegistryPopulator()
populator.populate_from_file_upload(file_data)
populator.populate_from_etl(etl_data)
```

## 📋 API Endpoints

### File Upload Routes
- `POST /files/upload` - Upload file with automatic twin registry population
- `POST /files/upload-from-url` - Upload from URL with automatic population
- `POST /files/{file_id}/populate-twin-registry` - Manual population trigger
- `POST /files/populate-all-twin-registries` - Bulk population (admin)

### Status and Health
- `GET /twin-registry/integration-status` - Integration status
- `GET /twin-registry/health` - System health check

## 🧪 Testing

### Test Scripts
- `scripts/test_functional_fixes.py` - Phase 1.5 compatibility tests
- `scripts/test_phase2_services.py` - Service layer tests
- `scripts/test_upload_twin_registry_integration.py` - Integration tests

### Running Tests
```bash
# Test the new twin registry system
python scripts/test_functional_fixes.py

# Test service layer
python scripts/test_phase2_services.py

# Test integration
python scripts/test_upload_twin_registry_integration.py
```

## 🔧 Configuration

### Population Configuration
```yaml
# config/population_config.yaml
population:
  phase1:
    enabled: true
    validation_rules: ["file_required", "user_required"]
    quality_threshold: 0.7
  
  phase2:
    enabled: true
    validation_rules: ["etl_required", "output_required"]
    quality_threshold: 0.8
  
  validation:
    strict_mode: false
    auto_correct: true
```

### Validation Rules
```yaml
# config/validation_rules.yaml
rules:
  file_upload:
    - name: "file_required"
      condition: "file_id is not None"
      severity: "error"
    
    - name: "user_required"
      condition: "user_id is not None"
      severity: "warning"
  
  etl_completion:
    - name: "etl_required"
      condition: "etl_result is not None"
      severity: "error"
```

## 📈 Quality Scoring

### Health Score Calculation
- **Base Score**: 50 points
- **Time Bonus**: Up to 25 points for fast processing
- **Quality Bonus**: Up to 25 points for high-quality data
- **Total**: Capped at 100 points

### Quality Metrics
- Data completeness
- Validation status
- Processing performance
- Error rates
- Compliance status

## 🔒 Security & Privacy

### Access Control
- User-based permissions
- Organization-level isolation
- Role-based access control (RBAC)

### Data Privacy
- Configurable privacy levels
- Audit trail logging
- Compliance status tracking

## 🚦 Status Management

### Processing Status
- `pending` - Initial state
- `processing` - Currently being processed
- `completed` - Successfully completed
- `failed` - Processing failed
- `cancelled` - Manually cancelled

### Lifecycle Status
- `created` - Initial creation
- `active` - Operational
- `inactive` - Temporarily disabled
- `archived` - Long-term storage
- `deleted` - Marked for deletion

## 🔄 Migration & Updates

### Database Migration
```bash
# Run Phase 1 migration
python scripts/migrate_twin_registry_phase1_simple.py

# Verify migration
python scripts/test_twin_registry_phase1.py
```

### Schema Updates
- Automatic JSON field validation
- Backward compatibility maintained
- No breaking changes to existing data

## 📚 Usage Examples

### Creating a Twin Registry Entry
```python
from src.twin_registry.models.twin_registry import TwinRegistry

# Create new registry
registry = TwinRegistry.create_registry(
    twin_name="My Digital Twin",
    registry_type="extraction",
    workflow_source="aasx_file",
    user_id="user123",
    org_id="org456",
    project_id="proj789"
)
```

### Querying Twin Registry
```python
from src.twin_registry.core.twin_registry_service import TwinRegistryService

service = TwinRegistryService()
registries = service.query_registries(
    registry_type="extraction",
    user_id="user123"
)
```

### Updating Lifecycle
```python
from src.twin_registry.core.twin_lifecycle_service import TwinLifecycleService

service = TwinLifecycleService()
service.start_twin("registry_id_123")
service.create_event("registry_id_123", "processing_started", "ETL pipeline started")
```

## 🎯 Future Enhancements

### Planned Features
- **Real-time Monitoring**: Live dashboard for twin registry status
- **Advanced Analytics**: Machine learning-based quality prediction
- **API Gateway**: RESTful API for external integrations
- **Webhook System**: External system notifications
- **Batch Processing**: Bulk operations for large datasets

### Integration Roadmap
- **Physics Modeling**: Integration with simulation systems
- **Federated Learning**: Distributed learning coordination
- **AI/RAG Enhancement**: Advanced AI integration
- **Blockchain**: Immutable audit trail
- **IoT Integration**: Real-time sensor data

## 🤝 Contributing

### Development Guidelines
1. Follow the existing module structure
2. Use the event-driven architecture
3. Maintain backward compatibility
4. Add comprehensive tests
5. Update documentation

### Code Quality
- Type hints required
- Comprehensive error handling
- Logging for debugging
- Performance optimization
- Security best practices

## 📄 License

This project follows the same license as the main AAS Data Modeling project.

## 🆘 Support

### Troubleshooting
1. Check integration status: `GET /twin-registry/integration-status`
2. Verify database schema: Run migration scripts
3. Check logs for error details
4. Validate configuration files

### Common Issues
- **Import Errors**: Ensure `src/` is in Python path
- **Database Errors**: Run migration scripts
- **Integration Failures**: Check startup integration hooks
- **Population Failures**: Verify validation rules

---

**Last Updated**: August 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅
