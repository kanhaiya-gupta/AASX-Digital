"""
Alert Manager Service

Provides comprehensive alert management and notification system for the AASX-ETL platform
with user-based access control and configurable alert rules.
"""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    severity: AlertSeverity
    conditions: Dict[str, Any]
    actions: List[str]
    enabled: bool = True
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Alert:
    """Alert instance"""
    alert_id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    status: AlertStatus
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None

@dataclass
class Notification:
    """Notification instance"""
    notification_id: str
    alert_id: str
    user_id: str
    type: str  # 'email', 'webhook', 'sms', 'in_app'
    content: str
    org_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered: bool = False
    delivery_error: Optional[str] = None

class AlertManager:
    """Comprehensive alert management service with user-based access control"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notifications: Dict[str, List[Notification]] = {}
        self.alert_handlers: Dict[str, Callable] = {}
        
        # Default alert rules
        self._initialize_default_rules()
        
        # Alert cleanup thread
        self.cleanup_thread = None
        self.stop_cleanup = threading.Event()
        self.start_cleanup_thread()
    
    def create_alert_rule(self, name: str, description: str, severity: AlertSeverity,
                         conditions: Dict[str, Any], actions: List[str], 
                         user_id: str, org_id: Optional[str] = None) -> Optional[str]:
        """Create a new alert rule for user"""
        try:
            rule_id = str(uuid.uuid4())
            now = datetime.now()
            
            rule = AlertRule(
                rule_id=rule_id,
                name=name,
                description=description,
                severity=severity,
                conditions=conditions,
                actions=actions,
                user_id=user_id,
                org_id=org_id,
                created_at=now,
                updated_at=now
            )
            
            self.alert_rules[rule_id] = rule
            logger.info(f"✅ Created alert rule '{name}' for user {user_id}")
            
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create alert rule for user {user_id}: {e}")
            return None
    
    def update_alert_rule(self, rule_id: str, updates: Dict[str, Any], 
                         user_id: str, org_id: Optional[str] = None) -> bool:
        """Update an existing alert rule"""
        try:
            if rule_id not in self.alert_rules:
                logger.warning(f"⚠️ Alert rule {rule_id} not found")
                return False
            
            rule = self.alert_rules[rule_id]
            
            # Check if user can modify this rule
            if not self._user_can_modify_rule(rule, user_id, org_id):
                logger.warning(f"⚠️ User {user_id} cannot modify rule {rule_id}")
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(rule, key) and key not in ['rule_id', 'created_at']:
                    setattr(rule, key, value)
            
            rule.updated_at = datetime.now()
            logger.info(f"✅ Updated alert rule {rule_id} for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update alert rule {rule_id}: {e}")
            return False
    
    def delete_alert_rule(self, rule_id: str, user_id: str, org_id: Optional[str] = None) -> bool:
        """Delete an alert rule"""
        try:
            if rule_id not in self.alert_rules:
                return False
            
            rule = self.alert_rules[rule_id]
            
            # Check if user can delete this rule
            if not self._user_can_modify_rule(rule, user_id, org_id):
                logger.warning(f"⚠️ User {user_id} cannot delete rule {rule_id}")
                return False
            
            del self.alert_rules[rule_id]
            logger.info(f"✅ Deleted alert rule {rule_id} for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete alert rule {rule_id}: {e}")
            return False
    
    def get_alert_rules_for_user(self, user_id: str, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get alert rules accessible to user"""
        try:
            user_rules = []
            
            for rule in self.alert_rules.values():
                if self._user_can_access_rule(rule, user_id, org_id):
                    user_rules.append(asdict(rule))
            
            return user_rules
            
        except Exception as e:
            logger.error(f"❌ Failed to get alert rules for user {user_id}: {e}")
            return []
    
    def create_alert(self, rule_id: str, message: str, details: Dict[str, Any],
                    user_id: str, org_id: Optional[str] = None) -> Optional[str]:
        """Create a new alert based on rule"""
        try:
            if rule_id not in self.alert_rules:
                logger.warning(f"⚠️ Alert rule {rule_id} not found")
                return None
            
            rule = self.alert_rules[rule_id]
            
            # Check if user can access this rule
            if not self._user_can_access_rule(rule, user_id, org_id):
                logger.warning(f"⚠️ User {user_id} cannot access rule {rule_id}")
                return None
            
            alert_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Calculate expiration (default: 24 hours)
            expires_at = now + timedelta(hours=24)
            
            alert = Alert(
                alert_id=alert_id,
                rule_id=rule_id,
                severity=rule.severity,
                message=message,
                details=details,
                status=AlertStatus.ACTIVE,
                created_at=now,
                expires_at=expires_at,
                user_id=user_id,
                org_id=org_id
            )
            
            self.alerts[alert_id] = alert
            
            # Create notifications
            self._create_notifications(alert, rule)
            
            # Execute actions
            self._execute_alert_actions(alert, rule)
            
            logger.info(f"🚨 Created alert {alert_id} for user {user_id}")
            return alert_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create alert for user {user_id}: {e}")
            return None
    
    def get_alerts_for_user(self, user_id: str, org_id: Optional[str] = None,
                           status: Optional[AlertStatus] = None,
                           severity: Optional[AlertSeverity] = None,
                           hours: int = 24) -> List[Dict[str, Any]]:
        """Get alerts for specific user with filtering"""
        try:
            user_alerts = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for alert in self.alerts.values():
                # Check if user can access this alert
                if not self._user_can_access_alert(alert, user_id, org_id):
                    continue
                
                # Apply filters
                if status and alert.status != status:
                    continue
                if severity and alert.severity != severity:
                    continue
                if alert.created_at < cutoff_time:
                    continue
                
                user_alerts.append(asdict(alert))
            
            # Sort by creation time (newest first)
            user_alerts.sort(key=lambda x: x['created_at'], reverse=True)
            
            return user_alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to get alerts for user {user_id}: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str, user_id: str, org_id: Optional[str] = None) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            
            # Check if user can acknowledge this alert
            if not self._user_can_access_alert(alert, user_id, org_id):
                logger.warning(f"⚠️ User {user_id} cannot acknowledge alert {alert_id}")
                return False
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = user_id
            
            logger.info(f"✅ Alert {alert_id} acknowledged by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, user_id: str, org_id: Optional[str] = None) -> bool:
        """Resolve an alert"""
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            
            # Check if user can resolve this alert
            if not self._user_can_access_alert(alert, user_id, org_id):
                logger.warning(f"⚠️ User {user_id} cannot resolve alert {alert_id}")
                return False
            
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.resolved_by = user_id
            
            logger.info(f"✅ Alert {alert_id} resolved by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to resolve alert {alert_id}: {e}")
            return False
    
    def get_notifications_for_user(self, user_id: str, org_id: Optional[str] = None,
                                  delivered: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get notifications for specific user"""
        try:
            user_notifications = []
            
            for notification_list in self.notifications.values():
                for notification in notification_list:
                    if notification.user_id == user_id:
                        if org_id is None or notification.org_id == org_id:
                            if delivered is None or notification.delivered == delivered:
                                user_notifications.append(asdict(notification))
            
            # Sort by creation time (newest first)
            user_notifications.sort(key=lambda x: x['sent_at'] or x['notification_id'], reverse=True)
            
            return user_notifications
            
        except Exception as e:
            logger.error(f"❌ Failed to get notifications for user {user_id}: {e}")
            return []
    
    def mark_notification_delivered(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as delivered"""
        try:
            for notification_list in self.notifications.values():
                for notification in notification_list:
                    if (notification.notification_id == notification_id and 
                        notification.user_id == user_id):
                        notification.delivered = True
                        notification.sent_at = datetime.now()
                        logger.info(f"✅ Notification {notification_id} marked as delivered")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to mark notification {notification_id} as delivered: {e}")
            return False
    
    def register_alert_handler(self, alert_type: str, handler: Callable) -> bool:
        """Register a custom alert handler"""
        try:
            self.alert_handlers[alert_type] = handler
            logger.info(f"✅ Registered alert handler for type: {alert_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register alert handler for {alert_type}: {e}")
            return False
    
    def get_alert_summary_for_user(self, user_id: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """Get alert summary statistics for user"""
        try:
            alerts = self.get_alerts_for_user(user_id, org_id, hours=24)
            
            # Count by status
            status_counts = {'active': 0, 'acknowledged': 0, 'resolved': 0, 'expired': 0}
            severity_counts = {'info': 0, 'warning': 0, 'critical': 0, 'emergency': 0}
            
            for alert in alerts:
                status = alert['status']
                if isinstance(status, AlertStatus):
                    status = status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                
                severity = alert['severity']
                if isinstance(severity, AlertSeverity):
                    severity = severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            return {
                'user_id': user_id,
                'org_id': org_id,
                'total_alerts': len(alerts),
                'status_counts': status_counts,
                'severity_counts': severity_counts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get alert summary for user {user_id}: {e}")
            return {}
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        try:
            # System health rules
            system_health_rule = AlertRule(
                rule_id="system_health_default",
                name="System Health Monitoring",
                description="Default system health monitoring rule",
                severity=AlertSeverity.WARNING,
                conditions={
                    'cpu_threshold': 80.0,
                    'memory_threshold': 85.0,
                    'disk_threshold': 90.0
                },
                actions=['create_alert', 'send_notification'],
                user_id=None,  # Available to all users
                org_id=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.alert_rules[system_health_rule.rule_id] = system_health_rule
            
            # Service health rules
            service_health_rule = AlertRule(
                rule_id="service_health_default",
                name="Service Health Monitoring",
                description="Default service health monitoring rule",
                severity=AlertSeverity.CRITICAL,
                conditions={
                    'response_time_threshold': 5.0,
                    'error_rate_threshold': 0.1
                },
                actions=['create_alert', 'send_notification', 'escalate'],
                user_id=None,  # Available to all users
                org_id=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.alert_rules[service_health_rule.rule_id] = service_health_rule
            
            logger.info("✅ Initialized default alert rules")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize default alert rules: {e}")
    
    def _create_notifications(self, alert: Alert, rule: AlertRule):
        """Create notifications for alert"""
        try:
            if 'send_notification' not in rule.actions:
                return
            
            alert_id = alert.alert_id
            if alert_id not in self.notifications:
                self.notifications[alert_id] = []
            
            # Create in-app notification
            in_app_notification = Notification(
                notification_id=str(uuid.uuid4()),
                alert_id=alert_id,
                user_id=alert.user_id,
                org_id=alert.org_id,
                type='in_app',
                content=f"Alert: {alert.message}",
                sent_at=datetime.now(),
                delivered=True
            )
            
            self.notifications[alert_id].append(in_app_notification)
            
            # Create email notification (placeholder)
            email_notification = Notification(
                notification_id=str(uuid.uuid4()),
                alert_id=alert_id,
                user_id=alert.user_id,
                org_id=alert.org_id,
                type='email',
                content=f"Alert: {alert.message}",
                sent_at=None,
                delivered=False
            )
            
            self.notifications[alert_id].append(email_notification)
            
            logger.info(f"✅ Created notifications for alert {alert_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create notifications for alert {alert.alert_id}: {e}")
    
    def _execute_alert_actions(self, alert: Alert, rule: AlertRule):
        """Execute alert actions"""
        try:
            for action in rule.actions:
                if action == 'create_alert':
                    # Already done
                    pass
                elif action == 'send_notification':
                    # Already done
                    pass
                elif action == 'escalate':
                    self._escalate_alert(alert)
                elif action in self.alert_handlers:
                    # Execute custom handler
                    try:
                        self.alert_handlers[action](alert, rule)
                    except Exception as e:
                        logger.error(f"❌ Custom alert handler {action} failed: {e}")
                else:
                    logger.warning(f"⚠️ Unknown alert action: {action}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to execute alert actions: {e}")
    
    def _escalate_alert(self, alert: Alert):
        """Escalate alert (placeholder for future implementation)"""
        try:
            logger.info(f"🚨 Escalating alert {alert.alert_id} with severity {alert.severity}")
            # Future: Implement escalation logic (e.g., notify managers, create tickets)
        except Exception as e:
            logger.error(f"❌ Failed to escalate alert {alert.alert_id}: {e}")
    
    def _user_can_access_rule(self, rule: AlertRule, user_id: str, org_id: Optional[str] = None) -> bool:
        """Check if user can access alert rule"""
        try:
            # Rules without user_id are available to all users
            if rule.user_id is None:
                return True
            
            # User can access their own rules
            if rule.user_id == user_id:
                return True
            
            # User can access organization rules
            if org_id and rule.org_id == org_id:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check rule access for user {user_id}: {e}")
            return False
    
    def _user_can_modify_rule(self, rule: AlertRule, user_id: str, org_id: Optional[str] = None) -> bool:
        """Check if user can modify alert rule"""
        try:
            # Users can only modify their own rules
            if rule.user_id == user_id:
                return True
            
            # Organization admins can modify org rules
            if org_id and rule.org_id == org_id:
                # Future: Add role-based permission check
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check rule modification for user {user_id}: {e}")
            return False
    
    def _user_can_access_alert(self, alert: Alert, user_id: str, org_id: Optional[str] = None) -> bool:
        """Check if user can access alert"""
        try:
            # User can access their own alerts
            if alert.user_id == user_id:
                return True
            
            # User can access organization alerts
            if org_id and alert.org_id == org_id:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check alert access for user {user_id}: {e}")
            return False
    
    def start_cleanup_thread(self):
        """Start cleanup thread for expired alerts"""
        try:
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            logger.info("✅ Started alert cleanup thread")
        except Exception as e:
            logger.error(f"❌ Failed to start cleanup thread: {e}")
    
    def _cleanup_loop(self):
        """Cleanup loop for expired alerts"""
        try:
            while not self.stop_cleanup.is_set():
                self._cleanup_expired_alerts()
                self.stop_cleanup.wait(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"❌ Cleanup loop failed: {e}")
    
    def _cleanup_expired_alerts(self):
        """Clean up expired alerts"""
        try:
            now = datetime.now()
            expired_alerts = []
            
            for alert_id, alert in self.alerts.items():
                if alert.expires_at and alert.expires_at < now:
                    expired_alerts.append(alert_id)
            
            for alert_id in expired_alerts:
                alert = self.alerts[alert_id]
                alert.status = AlertStatus.EXPIRED
                logger.info(f"🕐 Alert {alert_id} expired")
            
            # Remove very old alerts (older than 30 days)
            cutoff_time = now - timedelta(days=30)
            old_alerts = [
                alert_id for alert_id, alert in self.alerts.items()
                if alert.created_at < cutoff_time
            ]
            
            for alert_id in old_alerts:
                del self.alerts[alert_id]
                if alert_id in self.notifications:
                    del self.notifications[alert_id]
            
            if expired_alerts or old_alerts:
                logger.info(f"🧹 Cleaned up {len(expired_alerts)} expired and {len(old_alerts)} old alerts")
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired alerts: {e}")
    
    def stop_cleanup_thread(self):
        """Stop cleanup thread"""
        try:
            self.stop_cleanup.set()
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5.0)
            logger.info("🛑 Stopped alert cleanup thread")
        except Exception as e:
            logger.error(f"❌ Failed to stop cleanup thread: {e}")
