# Enhanced Twin Management

## Overview

**Phase 2.2.2: Complete Twin Registry Management** introduces comprehensive twin lifecycle management, advanced operations, configuration management, and enhanced monitoring capabilities to the Twin Registry system.

## 🚀 Features

### Core Management
- **Twin Lifecycle**: Create, update, delete twins with full configuration
- **Twin Operations**: Start, stop, restart twins with operation tracking
- **Bulk Operations**: Manage multiple twins simultaneously
- **Configuration Management**: Detailed twin settings and metadata

### Advanced Monitoring
- **Event History**: Complete audit trail of twin activities
- **Health Monitoring**: Comprehensive health scoring and diagnostics
- **Real-time Status**: Live operational status tracking
- **Performance Metrics**: Detailed performance monitoring

### Enhanced UI
- **Advanced Table**: Sortable, filterable twin management interface
- **Search & Filter**: Find twins by name, type, status, owner
- **Bulk Selection**: Select multiple twins for batch operations
- **Configuration Modal**: Rich twin configuration interface
- **Event Viewer**: Timeline of twin events and activities
- **Health Dashboard**: Visual health metrics and recommendations

## 📊 Data Architecture

### Database Schema

#### Twin Configurations
```sql
CREATE TABLE twin_configurations (
    twin_id TEXT PRIMARY KEY,
    twin_name TEXT NOT NULL,
    description TEXT,
    twin_type TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    owner TEXT DEFAULT 'system',
    tags TEXT,  -- JSON array of tags
    settings TEXT,  -- JSON object of settings
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### Twin Events
```sql
CREATE TABLE twin_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_message TEXT NOT NULL,
    severity TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    user TEXT DEFAULT 'system',
    metadata TEXT,  -- JSON object of metadata
    FOREIGN KEY (twin_id) REFERENCES twin_aasx_relationships (twin_id)
);
```

#### Twin Health
```sql
CREATE TABLE twin_health (
    twin_id TEXT PRIMARY KEY,
    overall_health REAL NOT NULL,
    performance_health REAL NOT NULL,
    connectivity_health REAL NOT NULL,
    data_health REAL NOT NULL,
    operational_health REAL NOT NULL,
    last_check TEXT DEFAULT CURRENT_TIMESTAMP,
    issues TEXT,  -- JSON array of issues
    recommendations TEXT,  -- JSON array of recommendations
    FOREIGN KEY (twin_id) REFERENCES twin_aasx_relationships (twin_id)
);
```

#### Twin Operations
```sql
CREATE TABLE twin_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twin_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    result TEXT,
    error_message TEXT,
    user TEXT DEFAULT 'system',
    FOREIGN KEY (twin_id) REFERENCES twin_aasx_relationships (twin_id)
);
```

## 🔧 API Endpoints

### Twin Management

#### Create Twin
```http
POST /twin-registry/api/twins
Content-Type: application/json

{
    "twin_id": "unique-twin-id",
    "twin_name": "Twin Name",
    "description": "Twin description",
    "twin_type": "manufacturing",
    "version": "1.0.0",
    "owner": "user@example.com",
    "tags": ["tag1", "tag2"],
    "settings": {
        "auto_start": true,
        "monitoring_enabled": true
    }
}
```

#### Update Twin
```http
PUT /twin-registry/api/twins/{twin_id}
Content-Type: application/json

{
    "description": "Updated description",
    "version": "1.1.0",
    "tags": ["updated", "tags"],
    "settings": {
        "new_setting": "value"
    }
}
```

#### Delete Twin
```http
DELETE /twin-registry/api/twins/{twin_id}
```

### Twin Operations

#### Start Twin
```http
POST /twin-registry/api/twins/{twin_id}/start
```

#### Stop Twin
```http
POST /twin-registry/api/twins/{twin_id}/stop
```

#### Restart Twin
```http
POST /twin-registry/api/twins/{twin_id}/restart
```

#### Bulk Operations
```http
POST /twin-registry/api/twins/bulk/start
Content-Type: application/json

{
    "twin_ids": ["twin1", "twin2", "twin3"]
}
```

### Twin Information

#### Get Twin Configuration
```http
GET /twin-registry/api/twins/{twin_id}/configuration
```

#### Get Twin Events
```http
GET /twin-registry/api/twins/{twin_id}/events?limit=50
```

#### Get Twin Health
```http
GET /twin-registry/api/twins/{twin_id}/health
```

#### Get All Twins Summary
```http
GET /twin-registry/api/twins/summary
```

#### Search Twins
```http
GET /twin-registry/api/twins/search?query=search&type=manufacturing&status=active&limit=50
```

## 🎯 Usage Guide

### 1. Creating Twins

#### Via API
```python
import requests

twin_data = {
    "twin_id": "motor-001",
    "twin_name": "Production Motor",
    "description": "Main production line motor",
    "twin_type": "manufacturing",
    "version": "1.0.0",
    "owner": "production-team",
    "tags": ["motor", "production", "critical"],
    "settings": {
        "auto_start": True,
        "monitoring_enabled": True,
        "alert_threshold": 85
    }
}

response = requests.post("http://localhost:8000/twin-registry/api/twins", json=twin_data)
```

#### Via Web Interface
1. Navigate to `/twin-registry`
2. Click "Create Twin" button
3. Fill in the configuration form
4. Click "Save Configuration"

### 2. Managing Twin Operations

#### Start a Twin
```python
response = requests.post(f"http://localhost:8000/twin-registry/api/twins/{twin_id}/start")
```

#### Stop a Twin
```python
response = requests.post(f"http://localhost:8000/twin-registry/api/twins/{twin_id}/stop")
```

#### Restart a Twin
```python
response = requests.post(f"http://localhost:8000/twin-registry/api/twins/{twin_id}/restart")
```

### 3. Bulk Operations

#### Start Multiple Twins
```python
twin_ids = ["twin1", "twin2", "twin3"]
response = requests.post(
    "http://localhost:8000/twin-registry/api/twins/bulk/start",
    json={"twin_ids": twin_ids}
)
```

#### Stop Multiple Twins
```python
response = requests.post(
    "http://localhost:8000/twin-registry/api/twins/bulk/stop",
    json={"twin_ids": twin_ids}
)
```

### 4. Monitoring Twins

#### Get Twin Health
```python
response = requests.get(f"http://localhost:8000/twin-registry/api/twins/{twin_id}/health")
health_data = response.json()["data"]

print(f"Overall Health: {health_data['overall_health']}%")
print(f"Performance Health: {health_data['performance_health']}%")
print(f"Connectivity Health: {health_data['connectivity_health']}%")
```

#### Get Twin Events
```python
response = requests.get(f"http://localhost:8000/twin-registry/api/twins/{twin_id}/events?limit=20")
events = response.json()["data"]

for event in events:
    print(f"{event['timestamp']}: {event['event_type']} - {event['event_message']}")
```

### 5. Searching Twins

#### Search by Name
```python
response = requests.get("http://localhost:8000/twin-registry/api/twins/search?query=motor")
```

#### Filter by Type
```python
response = requests.get("http://localhost:8000/twin-registry/api/twins/search?type=manufacturing")
```

#### Filter by Status
```python
response = requests.get("http://localhost:8000/twin-registry/api/twins/search?status=active")
```

## 🎨 Web Interface Features

### Enhanced Twin Table
- **Sortable Columns**: Click column headers to sort
- **Search**: Real-time search across twin names
- **Filters**: Filter by type, status, owner
- **Bulk Selection**: Checkboxes for bulk operations
- **Action Buttons**: Quick access to twin operations

### Configuration Modal
- **Rich Form**: Comprehensive twin configuration
- **Validation**: Real-time form validation
- **JSON Settings**: Advanced settings editor
- **Tags Management**: Easy tag addition/removal

### Event History
- **Timeline View**: Chronological event display
- **Severity Colors**: Visual severity indicators
- **User Tracking**: Track who performed actions
- **Metadata**: Additional event context

### Health Dashboard
- **Progress Bars**: Visual health indicators
- **Color Coding**: Health status colors
- **Issues List**: Active problems and warnings
- **Recommendations**: Suggested improvements

## 🔍 Monitoring & Analytics

### Health Metrics
- **Overall Health**: Composite health score
- **Performance Health**: Performance-related metrics
- **Connectivity Health**: Network and communication health
- **Data Health**: Data quality and availability
- **Operational Health**: Operational status and reliability

### Event Tracking
- **Event Types**: Creation, updates, operations, errors
- **Severity Levels**: Critical, warning, info, debug
- **User Attribution**: Track who performed actions
- **Metadata**: Additional context for events

### Performance Monitoring
- **Real-time Metrics**: Live performance data
- **Historical Trends**: Performance over time
- **Alerting**: Automated alerts for issues
- **Recommendations**: Suggested optimizations

## 🛠️ Configuration Options

### Twin Types
- `manufacturing`: Manufacturing equipment twins
- `energy`: Energy system twins
- `component`: Component-level twins
- `generic`: Generic twins for custom use

### Settings Examples
```json
{
    "auto_start": true,
    "monitoring_enabled": true,
    "alert_threshold": 85,
    "sync_interval": 300,
    "retention_days": 30,
    "backup_enabled": true,
    "log_level": "info"
}
```

### Tags Examples
```json
["critical", "production", "motor", "line-1", "maintenance-due"]
```

## 🚨 Troubleshooting

### Common Issues

#### Twin Creation Fails
- **Check**: Twin ID uniqueness
- **Solution**: Use unique twin IDs
- **Check**: Required fields
- **Solution**: Ensure all required fields are provided

#### Operations Fail
- **Check**: Twin exists and is active
- **Solution**: Verify twin status
- **Check**: Permissions
- **Solution**: Ensure proper user permissions

#### Health Data Missing
- **Check**: Twin registration
- **Solution**: Ensure twin is properly registered
- **Check**: Health monitoring enabled
- **Solution**: Enable health monitoring in settings

### Debug Commands

#### Check Twin Status
```python
response = requests.get(f"http://localhost:8000/twin-registry/api/twins/{twin_id}/configuration")
print(response.json())
```

#### View Twin Events
```python
response = requests.get(f"http://localhost:8000/twin-registry/api/twins/{twin_id}/events")
events = response.json()["data"]
for event in events:
    print(f"{event['timestamp']}: {event['event_type']} - {event['event_message']}")
```

#### Check Database
```python
import sqlite3
conn = sqlite3.connect("data/twin_registry.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM twin_configurations WHERE twin_id = ?", (twin_id,))
print(cursor.fetchone())
conn.close()
```

## 📈 Best Practices

### Twin Naming
- Use descriptive, consistent names
- Include location or line information
- Use version numbers for updates
- Avoid special characters

### Configuration Management
- Use tags for categorization
- Document settings thoroughly
- Version control configurations
- Test configurations before deployment

### Monitoring Setup
- Set appropriate alert thresholds
- Configure health monitoring
- Enable event logging
- Regular health reviews

### Operations Management
- Use bulk operations for efficiency
- Monitor operation results
- Track operation history
- Implement rollback procedures

## 🔄 Integration with Other Components

### AASX Integration
- Twins can be auto-registered from AASX files
- AASX data feeds into twin health metrics
- Twin operations can trigger AASX processing

### Performance Monitoring
- Health metrics integrate with performance data
- Performance alerts trigger twin health updates
- Combined dashboard views available

### Real-time Sync
- Twin status updates in real-time
- WebSocket notifications for operations
- Live health metric updates

## 🎯 Next Steps

### Phase 2.2.3: Advanced Analytics
- Predictive health modeling
- Trend analysis and forecasting
- Advanced reporting and dashboards
- Machine learning integration

### Phase 2.2.4: Registry Administration
- User management and permissions
- Audit logging and compliance
- Backup and recovery
- System administration tools

### Phase 2.2.5: Integration Features
- External system integration
- API rate limiting and security
- Webhook notifications
- Third-party integrations

## 📚 Quick Reference

### API Quick Commands
```bash
# Create twin
curl -X POST http://localhost:8000/twin-registry/api/twins \
  -H "Content-Type: application/json" \
  -d '{"twin_id":"test","twin_name":"Test Twin","twin_type":"generic"}'

# Start twin
curl -X POST http://localhost:8000/twin-registry/api/twins/test/start

# Get health
curl http://localhost:8000/twin-registry/api/twins/test/health

# Search twins
curl "http://localhost:8000/twin-registry/api/twins/search?query=test"
```

### Web Interface URLs
- **Main Dashboard**: `/twin-registry`
- **Enhanced Management**: Available in main dashboard
- **Event History**: Available in main dashboard
- **Health Monitoring**: Available in main dashboard

### Database Tables
- `twin_configurations`: Twin configuration data
- `twin_events`: Event history and audit trail
- `twin_health`: Health metrics and diagnostics
- `twin_operations`: Operation tracking and results
- `twin_aasx_relationships`: AASX integration data

---

**Phase 2.2.2 Enhanced Twin Management** provides a complete, production-ready twin management system with comprehensive lifecycle management, advanced monitoring, and intuitive user interface. 