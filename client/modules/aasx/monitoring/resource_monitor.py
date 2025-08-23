"""
Resource Monitor Service

Provides real-time resource monitoring (CPU, memory, disk) for the AASX-ETL platform
with user-based access control and performance tracking.
"""

import psutil
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading

logger = logging.getLogger(__name__)

@dataclass
class ResourceSnapshot:
    """Resource usage snapshot"""
    timestamp: datetime
    cpu_percent: float
    cpu_freq: Optional[float]
    memory_percent: float
    memory_used: int
    memory_available: int
    disk_percent: float
    disk_used: int
    disk_free: int
    network_sent: int
    network_recv: int
    user_id: Optional[str] = None
    org_id: Optional[str] = None

@dataclass
class ResourceAlert:
    """Resource usage alert"""
    alert_id: str
    timestamp: datetime
    alert_type: str  # 'cpu', 'memory', 'disk', 'network'
    severity: str    # 'warning', 'critical'
    message: str
    current_value: float
    threshold: float
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    acknowledged: bool = False

class ResourceMonitor:
    """Real-time resource monitoring service with user-based access control"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitoring_interval = 5.0  # seconds
        self.resource_history: Dict[str, List[ResourceSnapshot]] = {}
        self.max_history_size = 1000
        self.alerts: Dict[str, List[ResourceAlert]] = {}
        
        # Default thresholds (can be customized per user)
        self.default_thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'network_warning': 100 * 1024 * 1024,  # 100MB
            'network_critical': 500 * 1024 * 1024   # 500MB
        }
        
        # User-specific thresholds
        self.user_thresholds = {}
        
        # Monitoring thread
        self.monitor_thread = None
        self.stop_event = threading.Event()
    
    def start_monitoring(self, user_id: str, org_id: Optional[str] = None) -> bool:
        """Start resource monitoring for specific user"""
        try:
            if self.is_monitoring:
                logger.info(f"🔄 Resource monitoring already running for user: {user_id}")
                return True
            
            self.is_monitoring = True
            self.stop_event.clear()
            
            # Initialize user monitoring
            self._initialize_user_monitoring(user_id, org_id)
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(user_id, org_id),
                daemon=True
            )
            self.monitor_thread.start()
            
            logger.info(f"🚀 Resource monitoring started for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start resource monitoring for user {user_id}: {e}")
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop resource monitoring"""
        try:
            if not self.is_monitoring:
                return True
            
            self.is_monitoring = False
            self.stop_event.set()
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5.0)
            
            logger.info("🛑 Resource monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop resource monitoring: {e}")
            return False
    
    def get_current_resources(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current resource usage for user"""
        try:
            # Check if user has access
            if not self._user_can_access_resources(user_id, org_id):
                logger.warning(f"⚠️ User {user_id} cannot access resource monitoring")
                return self._get_access_denied_response(user_id, org_id)
            
            # Get current resource snapshot
            snapshot = self._take_resource_snapshot(user_id, org_id)
            
            # Check for alerts
            alerts = self._check_resource_alerts(snapshot, user_id, org_id)
            
            return {
                'user_id': user_id,
                'org_id': org_id,
                'timestamp': snapshot.timestamp.isoformat(),
                'resources': asdict(snapshot),
                'alerts': [asdict(alert) for alert in alerts],
                'thresholds': self._get_user_thresholds(user_id, org_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get current resources for user {user_id}: {e}")
            return self._get_error_response(user_id, org_id)
    
    def get_resource_history(self, user_id: str, org_id: Optional[str] = None, 
                           hours: int = 24) -> List[Dict[str, Any]]:
        """Get resource usage history for user"""
        try:
            if not self._user_can_access_resources(user_id, org_id):
                return []
            
            user_key = self._get_user_key(user_id, org_id)
            if user_key not in self.resource_history:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_snapshots = [
                snapshot for snapshot in self.resource_history[user_key]
                if snapshot.timestamp > cutoff_time
            ]
            
            return [asdict(snapshot) for snapshot in recent_snapshots]
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource history for user {user_id}: {e}")
            return []
    
    def get_resource_trends(self, user_id: str, org_id: Optional[str] = None, 
                           hours: int = 24) -> Dict[str, Any]:
        """Get resource usage trends for user"""
        try:
            if not self._user_can_access_resources(user_id, org_id):
                return self._get_access_denied_response(user_id, org_id)
            
            history = self.get_resource_history(user_id, org_id, hours)
            if not history:
                return self._get_empty_trends(user_id, org_id)
            
            # Calculate trends
            trends = self._calculate_resource_trends(history)
            
            return {
                'user_id': user_id,
                'org_id': org_id,
                'period_hours': hours,
                'trends': trends,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource trends for user {user_id}: {e}")
            return self._get_error_response(user_id, org_id)
    
    def set_user_thresholds(self, user_id: str, thresholds: Dict[str, float], 
                           org_id: Optional[str] = None) -> bool:
        """Set custom thresholds for specific user"""
        try:
            user_key = self._get_user_key(user_id, org_id)
            
            # Validate thresholds
            for key, value in thresholds.items():
                if not self._is_valid_threshold(key, value):
                    raise ValueError(f"Invalid threshold: {key} = {value}")
            
            # Update user thresholds
            if user_key not in self.user_thresholds:
                self.user_thresholds[user_key] = {}
            
            self.user_thresholds[user_key].update(thresholds)
            
            logger.info(f"✅ Updated resource thresholds for user {user_id}: {thresholds}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set thresholds for user {user_id}: {e}")
            return False
    
    def get_user_thresholds(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, float]:
        """Get current thresholds for user"""
        try:
            user_key = self._get_user_key(user_id, org_id)
            
            if user_key in self.user_thresholds:
                # Merge default with user-specific thresholds
                thresholds = self.default_thresholds.copy()
                thresholds.update(self.user_thresholds[user_key])
                return thresholds
            
            return self.default_thresholds.copy()
            
        except Exception as e:
            logger.error(f"❌ Failed to get thresholds for user {user_id}: {e}")
            return self.default_thresholds.copy()
    
    def get_alerts_for_user(self, user_id: str, org_id: Optional[str] = None, 
                           acknowledged: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get alerts for specific user"""
        try:
            if not self._user_can_access_resources(user_id, org_id):
                return []
            
            user_key = self._get_user_key(user_id, org_id)
            if user_key not in self.alerts:
                return []
            
            user_alerts = self.alerts[user_key]
            
            # Filter by acknowledgment status if specified
            if acknowledged is not None:
                user_alerts = [alert for alert in user_alerts if alert.acknowledged == acknowledged]
            
            return [asdict(alert) for alert in user_alerts]
            
        except Exception as e:
            logger.error(f"❌ Failed to get alerts for user {user_id}: {e}")
            return []
    
    def acknowledge_alert(self, user_id: str, alert_id: str, org_id: Optional[str] = None) -> bool:
        """Acknowledge an alert for user"""
        try:
            if not self._user_can_access_resources(user_id, org_id):
                return False
            
            user_key = self._get_user_key(user_id, org_id)
            if user_key not in self.alerts:
                return False
            
            # Find and acknowledge alert
            for alert in self.alerts[user_key]:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    logger.info(f"✅ Alert {alert_id} acknowledged by user {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to acknowledge alert {alert_id} for user {user_id}: {e}")
            return False
    
    def _monitoring_loop(self, user_id: str, org_id: Optional[str] = None):
        """Main monitoring loop"""
        try:
            while self.is_monitoring and not self.stop_event.is_set():
                # Take resource snapshot
                snapshot = self._take_resource_snapshot(user_id, org_id)
                
                # Store in history
                self._store_resource_snapshot(snapshot)
                
                # Check for alerts
                alerts = self._check_resource_alerts(snapshot, user_id, org_id)
                
                # Wait for next interval
                self.stop_event.wait(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"❌ Resource monitoring loop failed for user {user_id}: {e}")
            self.is_monitoring = False
    
    def _take_resource_snapshot(self, user_id: str, org_id: Optional[str] = None) -> ResourceSnapshot:
        """Take current resource usage snapshot"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_freq_mhz = cpu_freq.current if cpu_freq else None
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            return ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                cpu_freq=cpu_freq_mhz,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_available=memory.available,
                disk_percent=disk.percent,
                disk_used=disk.used,
                disk_free=disk.free,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                user_id=user_id,
                org_id=org_id
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to take resource snapshot: {e}")
            return self._get_error_snapshot(user_id, org_id)
    
    def _check_resource_alerts(self, snapshot: ResourceSnapshot, user_id: str, 
                              org_id: Optional[str] = None) -> List[ResourceAlert]:
        """Check for resource usage alerts"""
        try:
            alerts = []
            thresholds = self._get_user_thresholds(user_id, org_id)
            
            # CPU alerts
            if snapshot.cpu_percent >= thresholds['cpu_critical']:
                alerts.append(self._create_alert('cpu', 'critical', snapshot.cpu_percent, 
                                              thresholds['cpu_critical'], user_id, org_id))
            elif snapshot.cpu_percent >= thresholds['cpu_warning']:
                alerts.append(self._create_alert('cpu', 'warning', snapshot.cpu_percent, 
                                              thresholds['cpu_warning'], user_id, org_id))
            
            # Memory alerts
            if snapshot.memory_percent >= thresholds['memory_critical']:
                alerts.append(self._create_alert('memory', 'critical', snapshot.memory_percent, 
                                              thresholds['memory_critical'], user_id, org_id))
            elif snapshot.memory_percent >= thresholds['memory_warning']:
                alerts.append(self._create_alert('memory', 'warning', snapshot.memory_percent, 
                                              thresholds['memory_warning'], user_id, org_id))
            
            # Disk alerts
            if snapshot.disk_percent >= thresholds['disk_critical']:
                alerts.append(self._create_alert('disk', 'critical', snapshot.disk_percent, 
                                              thresholds['disk_critical'], user_id, org_id))
            elif snapshot.disk_percent >= thresholds['disk_warning']:
                alerts.append(self._create_alert('disk', 'warning', snapshot.disk_percent, 
                                              thresholds['disk_warning'], user_id, org_id))
            
            # Store alerts
            for alert in alerts:
                self._store_alert(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to check resource alerts: {e}")
            return []
    
    def _create_alert(self, alert_type: str, severity: str, current_value: float, 
                     threshold: float, user_id: str, org_id: Optional[str] = None) -> ResourceAlert:
        """Create a new resource alert"""
        alert_id = f"{alert_type}_{severity}_{int(time.time())}"
        
        messages = {
            'cpu': f"CPU usage is {current_value:.1f}% (threshold: {threshold:.1f}%)",
            'memory': f"Memory usage is {current_value:.1f}% (threshold: {threshold:.1f}%)",
            'disk': f"Disk usage is {current_value:.1f}% (threshold: {threshold:.1f}%)"
        }
        
        return ResourceAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            message=messages.get(alert_type, f"{alert_type} threshold exceeded"),
            current_value=current_value,
            threshold=threshold,
            user_id=user_id,
            org_id=org_id
        )
    
    def _calculate_resource_trends(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate resource usage trends"""
        try:
            if not history:
                return {}
            
            # Calculate averages
            avg_cpu = sum(h['cpu_percent'] for h in history) / len(history)
            avg_memory = sum(h['memory_percent'] for h in history) / len(history)
            avg_disk = sum(h['disk_percent'] for h in history) / len(history)
            
            # Calculate trends (simple comparison of first and last 25% of data)
            quarter_size = max(1, len(history) // 4)
            if quarter_size > 0:
                recent_avg = sum(h['cpu_percent'] for h in history[:quarter_size]) / quarter_size
                older_avg = sum(h['cpu_percent'] for h in history[-quarter_size:]) / quarter_size
                cpu_trend = 'increasing' if recent_avg > older_avg * 1.1 else 'decreasing' if recent_avg < older_avg * 0.9 else 'stable'
            else:
                cpu_trend = 'stable'
            
            return {
                'averages': {
                    'cpu': round(avg_cpu, 2),
                    'memory': round(avg_memory, 2),
                    'disk': round(avg_disk, 2)
                },
                'trends': {
                    'cpu': cpu_trend
                },
                'data_points': len(history)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate resource trends: {e}")
            return {}
    
    def _initialize_user_monitoring(self, user_id: str, org_id: Optional[str] = None):
        """Initialize monitoring for specific user"""
        try:
            user_key = self._get_user_key(user_id, org_id)
            
            # Initialize history storage
            if user_key not in self.resource_history:
                self.resource_history[user_key] = []
            
            # Initialize alerts storage
            if user_key not in self.alerts:
                self.alerts[user_key] = []
            
            logger.info(f"✅ Initialized resource monitoring for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize user monitoring for user {user_id}: {e}")
    
    def _store_resource_snapshot(self, snapshot: ResourceSnapshot):
        """Store resource snapshot in history"""
        try:
            user_key = self._get_user_key(snapshot.user_id, snapshot.org_id)
            
            if user_key in self.resource_history:
                self.resource_history[user_key].append(snapshot)
                
                # Maintain history size limit
                if len(self.resource_history[user_key]) > self.max_history_size:
                    self.resource_history[user_key].pop(0)
                    
        except Exception as e:
            logger.error(f"❌ Failed to store resource snapshot: {e}")
    
    def _store_alert(self, alert: ResourceAlert):
        """Store alert in user's alert list"""
        try:
            user_key = self._get_user_key(alert.user_id, alert.org_id)
            
            if user_key in self.alerts:
                self.alerts[user_key].append(alert)
                
                # Keep only recent alerts (last 100)
                if len(self.alerts[user_key]) > 100:
                    self.alerts[user_key] = self.alerts[user_key][-100:]
                    
        except Exception as e:
            logger.error(f"❌ Failed to store alert: {e}")
    
    def _user_can_access_resources(self, user_id: str, org_id: Optional[str] = None) -> bool:
        """Check if user can access resource monitoring"""
        # For now, all authenticated users can access resource monitoring
        # This can be enhanced with role-based permissions later
        return True
    
    def _get_user_key(self, user_id: str, org_id: Optional[str] = None) -> str:
        """Get unique key for user"""
        if org_id:
            return f"{user_id}_{org_id}"
        return user_id
    
    def _is_valid_threshold(self, key: str, value: float) -> bool:
        """Validate threshold value"""
        if not isinstance(value, (int, float)) or value < 0:
            return False
        
        # CPU and memory percentages should be 0-100
        if key in ['cpu_warning', 'cpu_critical', 'memory_warning', 'memory_critical', 'disk_warning', 'disk_critical']:
            return 0 <= value <= 100
        
        # Network thresholds should be positive
        if key in ['network_warning', 'network_critical']:
            return value > 0
        
        return True
    
    def _get_error_snapshot(self, user_id: str, org_id: Optional[str] = None) -> ResourceSnapshot:
        """Return error snapshot when monitoring fails"""
        return ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=0.0,
            cpu_freq=None,
            memory_percent=0.0,
            memory_used=0,
            memory_available=0,
            disk_percent=0.0,
            disk_used=0,
            disk_free=0,
            network_sent=0,
            network_recv=0,
            user_id=user_id,
            org_id=org_id
        )
    
    def _get_access_denied_response(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Return access denied response"""
        return {
            'user_id': user_id,
            'org_id': org_id,
            'error': 'Access denied to resource monitoring',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_error_response(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Return error response"""
        return {
            'user_id': user_id,
            'org_id': org_id,
            'error': 'Failed to retrieve resource information',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_empty_trends(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Return empty trends response"""
        return {
            'user_id': user_id,
            'org_id': org_id,
            'period_hours': 0,
            'trends': {},
            'timestamp': datetime.now().isoformat()
        }
