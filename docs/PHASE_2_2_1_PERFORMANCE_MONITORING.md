# Phase 2.2.1: Performance Monitoring System

## 🎯 **Overview**

The Performance Monitoring System provides real-time monitoring, analytics, and alerting for digital twins in the AASX Digital Twin Analytics Framework. This system tracks CPU usage, memory consumption, response times, throughput, error rates, and overall health scores for each digital twin.

## 🚀 **Features**

### **Real-Time Performance Metrics**
- **CPU Usage**: Tracks processing power consumption per twin
- **Memory Usage**: Monitors RAM utilization per twin
- **Response Time**: Measures query and sync response times
- **Throughput**: Tracks data points processed per second
- **Error Rate**: Monitors error frequency and types
- **Uptime**: Tracks continuous operation time
- **Health Score**: Overall performance rating (0-100%)

### **Performance Alerts**
- **Automatic Threshold Monitoring**: Alerts when metrics exceed limits
- **Multi-Severity Levels**: Warning, Critical alerts
- **Real-Time Notifications**: Immediate alert generation
- **Alert Resolution**: Mark alerts as resolved

### **Performance Dashboard**
- **Summary Statistics**: Overview of all twins
- **Health Distribution**: Visual representation of twin health
- **Resource Usage Charts**: CPU and memory trends
- **Real-Time Updates**: Live data refresh every 30 seconds

### **Historical Analytics**
- **Performance History**: 24-hour metric tracking
- **Trend Analysis**: Performance pattern identification
- **Data Export**: Historical data for analysis

## 🏗️ **Architecture**

### **Backend Components**

#### **Performance Monitor (`performance_monitor.py`)**
```python
class PerformanceMonitor:
    - Real-time metric collection
    - Alert generation and management
    - Historical data storage
    - Health score calculation
```

#### **Database Schema**
```sql
-- Performance metrics history
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY,
    twin_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    timestamp TEXT NOT NULL,
    unit TEXT NOT NULL
);

-- Performance alerts
CREATE TABLE performance_alerts (
    id INTEGER PRIMARY KEY,
    twin_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    metric_value REAL NOT NULL,
    threshold_value REAL NOT NULL,
    message TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT DEFAULT 'active'
);

-- Performance snapshots
CREATE TABLE performance_snapshots (
    id INTEGER PRIMARY KEY,
    twin_id TEXT NOT NULL,
    twin_name TEXT NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage REAL NOT NULL,
    response_time REAL NOT NULL,
    throughput REAL NOT NULL,
    error_rate REAL NOT NULL,
    health_score REAL NOT NULL,
    status TEXT NOT NULL
);
```

### **Frontend Components**

#### **Performance Monitoring JavaScript (`twin_registry_performance.js`)**
```javascript
class TwinRegistryPerformance:
    - Real-time UI updates
    - Chart generation and management
    - Alert display and management
    - Performance card creation
```

#### **UI Components**
- **Performance Cards**: Individual twin performance display
- **Alerts Panel**: Active alert management
- **Dashboard**: Summary statistics and charts
- **Details Modal**: Detailed twin performance view

## 📊 **API Endpoints**

### **Performance Data**
```http
GET /twin-registry/api/performance/twins
GET /twin-registry/api/performance/twins/{twin_id}
GET /twin-registry/api/performance/dashboard
```

### **Performance History**
```http
GET /twin-registry/api/performance/twins/{twin_id}/history?metric_type=cpu_usage&hours=24
```

### **Alerts Management**
```http
GET /twin-registry/api/performance/alerts
POST /twin-registry/api/performance/alerts/{alert_id}/resolve
```

## 🎨 **User Interface**

### **Performance Monitoring Panel**
- **Real-time twin cards** with health scores and resource usage
- **Progress bars** for CPU and memory usage
- **Status indicators** with color-coded health levels
- **View Details** buttons for detailed analysis

### **Alerts Panel**
- **Active alerts** with severity levels
- **Alert messages** with detailed descriptions
- **Resolve buttons** for alert management
- **Alert count** badge in header

### **Performance Dashboard**
- **Summary cards**: Total, Healthy, Warning, Critical twins
- **Resource usage chart**: CPU vs Memory comparison
- **Health distribution chart**: Pie chart of twin health
- **Real-time updates**: Automatic refresh every 30 seconds

### **Twin Details Modal**
- **Current metrics** table with all performance data
- **Performance history** chart for trend analysis
- **Detailed statistics** for comprehensive analysis

## 🔧 **Configuration**

### **Alert Thresholds**
```python
alert_thresholds = {
    "cpu_usage": 80.0,      # Alert if CPU > 80%
    "memory_usage": 85.0,   # Alert if memory > 85%
    "response_time": 5.0,   # Alert if response time > 5 seconds
    "error_rate": 5.0,      # Alert if error rate > 5%
}
```

### **Health Score Calculation**
```python
health_score = (
    cpu_score * 0.25 +      # CPU weight: 25%
    memory_score * 0.25 +   # Memory weight: 25%
    response_score * 0.3 +  # Response time weight: 30%
    error_score * 0.2       # Error rate weight: 20%
)
```

### **Monitoring Intervals**
- **Metric Collection**: Every 30 seconds
- **UI Updates**: Every 30 seconds
- **Alert Checks**: Every 30 seconds
- **Snapshot Storage**: Every 30 seconds

## 📈 **Metrics and Calculations**

### **CPU Usage**
- **Calculation**: Based on data processing activity and twin complexity
- **Range**: 5% - 100%
- **Alert Threshold**: > 80%

### **Memory Usage**
- **Calculation**: Based on twin complexity and data volume
- **Range**: 10% - 100%
- **Alert Threshold**: > 85%

### **Response Time**
- **Calculation**: Based on data volume and processing complexity
- **Range**: 0.1s - 10s
- **Alert Threshold**: > 5 seconds

### **Throughput**
- **Calculation**: Data points processed per second
- **Range**: 10 - 1000+ points/sec
- **Unit**: points/second

### **Error Rate**
- **Calculation**: Percentage of failed operations
- **Range**: 0% - 10%
- **Alert Threshold**: > 5%

### **Health Score**
- **Calculation**: Weighted average of all metrics
- **Range**: 0% - 100%
- **Categories**:
  - **Excellent** (90-100%): Optimal performance
  - **Good** (75-89%): Normal performance
  - **Fair** (60-74%): Performance issues
  - **Poor** (0-59%): Critical issues

## 🚨 **Alert System**

### **Alert Types**
1. **High CPU Usage**: CPU consumption exceeds threshold
2. **High Memory Usage**: Memory consumption exceeds threshold
3. **Slow Response Time**: Response time exceeds threshold
4. **High Error Rate**: Error rate exceeds threshold

### **Alert Severity**
- **Warning**: Performance degradation detected
- **Critical**: Severe performance issues

### **Alert Management**
- **Automatic Generation**: Based on threshold violations
- **Manual Resolution**: Mark alerts as resolved
- **Alert History**: Track all alerts and resolutions

## 📊 **Charts and Visualizations**

### **Resource Usage Chart**
- **Type**: Bar chart
- **Data**: CPU vs Memory usage by twin
- **Colors**: Blue (CPU), Red (Memory)
- **Y-axis**: 0-100% usage

### **Health Distribution Chart**
- **Type**: Pie chart
- **Data**: Distribution of twin health scores
- **Colors**: Green (Healthy), Yellow (Warning), Red (Critical)

### **Performance History Chart**
- **Type**: Line chart
- **Data**: Metric values over time
- **Time Range**: Configurable (default: 24 hours)
- **Metrics**: CPU, Memory, Response Time, Error Rate

## 🔄 **Real-Time Updates**

### **WebSocket Integration**
- **Performance Data**: Real-time metric updates
- **Alert Notifications**: Immediate alert delivery
- **Status Changes**: Live status updates

### **Auto-Refresh**
- **Dashboard**: Automatic refresh every 30 seconds
- **Charts**: Real-time chart updates
- **Alerts**: Live alert count updates

## 🧪 **Testing**

### **Test Script**
```bash
python test_performance_monitoring.py
```

### **Test Coverage**
1. **API Endpoints**: All performance endpoints
2. **Data Retrieval**: Twin performance data
3. **Dashboard**: Summary statistics
4. **Alerts**: Alert generation and management
5. **History**: Performance history retrieval

### **Expected Results**
- ✅ Performance data for all twins
- ✅ Dashboard with summary statistics
- ✅ Active alerts (if any)
- ✅ Individual twin performance details
- ✅ Performance history data

## 🚀 **Usage Guide**

### **Starting Performance Monitoring**
1. Navigate to `/twin-registry`
2. Look for "Twin Performance Monitoring" section
3. Click "Start Monitoring" to begin real-time updates
4. View performance cards for each twin

### **Viewing Performance Details**
1. Click "View Details" on any twin card
2. Review current metrics in the modal
3. Analyze performance history chart
4. Close modal when finished

### **Managing Alerts**
1. Check "Performance Alerts" section
2. Review alert messages and severity
3. Click "X" to resolve alerts
4. Monitor alert count in header

### **Dashboard Analysis**
1. View summary statistics in dashboard
2. Analyze resource usage chart
3. Review health distribution
4. Monitor real-time updates

## 🔮 **Future Enhancements**

### **Phase 2.2.2: Advanced Analytics**
- **Predictive Analytics**: Performance forecasting
- **Anomaly Detection**: AI-powered issue detection
- **Performance Optimization**: Automated recommendations
- **Custom Dashboards**: User-defined views

### **Phase 2.2.3: Integration Features**
- **External Monitoring**: Integration with external tools
- **Notification System**: Email/SMS alerts
- **Performance Reports**: Automated report generation
- **API Integration**: Third-party system integration

## 📚 **Technical Details**

### **Dependencies**
- **Backend**: `psutil`, `sqlite3`, `threading`, `asyncio`
- **Frontend**: `Chart.js`, `Bootstrap 5`, `jQuery`
- **Database**: SQLite with performance tables

### **Performance Considerations**
- **Memory Usage**: Efficient data storage and retrieval
- **CPU Usage**: Optimized metric collection
- **Database**: Indexed queries for fast retrieval
- **UI**: Responsive design for all devices

### **Security**
- **Data Validation**: Input sanitization
- **Access Control**: Role-based permissions
- **Error Handling**: Graceful error management
- **Logging**: Comprehensive audit trail

## 🎉 **Conclusion**

The Performance Monitoring System provides comprehensive real-time monitoring capabilities for digital twins, enabling proactive issue detection, performance optimization, and data-driven decision making. This system forms the foundation for advanced analytics and predictive maintenance in future phases.

---

**Phase 2.2.1 Status**: ✅ **COMPLETED**  
**Next Phase**: 2.2.2 Advanced Analytics  
**Last Updated**: January 2025 