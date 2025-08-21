"""
Alert Manager

Comprehensive alerting and notification system for the AAS Data Modeling Engine.
Provides configurable alerts, multiple notification channels, and alert aggregation.
"""

import time
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

from .monitoring_config import MonitoringConfig


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Individual alert definition"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    suppression_until: Optional[datetime] = None


@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    description: str
    condition: str
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5
    suppression_hours: int = 24
    notification_channels: List[str] = field(default_factory=lambda: ["log"])
    custom_actions: List[str] = field(default_factory=list)


class AlertManager:
    """Comprehensive alerting and notification system"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Alert storage
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alert_history: List[Alert] = []
        
        # Notification channels
        self.notification_channels: Dict[str, Callable] = {}
        self.custom_actions: Dict[str, Callable] = {}
        
        # Alert state
        self._last_alert_time: Dict[str, float] = {}
        self._suppressed_alerts: Dict[str, datetime] = {}
        
        # Initialize default alert rules
        self._init_default_alert_rules()
        
        # Initialize notification channels
        self._init_notification_channels()
        
        # Start alert processing if enabled
        if self.config.alerts.enabled:
            self.start_alert_processing()
    
    def _init_default_alert_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                description="CPU usage exceeds threshold",
                condition="cpu_usage > 80",
                severity=AlertSeverity.WARNING,
                cooldown_minutes=5,
                notification_channels=["log", "email"]
            ),
            AlertRule(
                name="high_memory_usage",
                description="Memory usage exceeds threshold",
                condition="memory_usage > 85",
                severity=AlertSeverity.WARNING,
                cooldown_minutes=5,
                notification_channels=["log", "email"]
            ),
            AlertRule(
                name="high_disk_usage",
                description="Disk usage exceeds threshold",
                condition="disk_usage > 90",
                severity=AlertSeverity.ERROR,
                cooldown_minutes=10,
                notification_channels=["log", "email"]
            ),
            AlertRule(
                name="database_connection_failure",
                description="Database connection pool failure",
                condition="db_connections_failed > 0",
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=1,
                notification_channels=["log", "email"]
            ),
            AlertRule(
                name="cache_performance_degradation",
                description="Cache hit rate below threshold",
                condition="cache_hit_rate < 0.5",
                severity=AlertSeverity.WARNING,
                cooldown_minutes=15,
                notification_channels=["log"]
            ),
            AlertRule(
                name="slow_operation_detected",
                description="Operation response time exceeds threshold",
                condition="operation_duration > 5.0",
                severity=AlertSeverity.WARNING,
                cooldown_minutes=5,
                notification_channels=["log"]
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def _init_notification_channels(self):
        """Initialize notification channels"""
        # Log channel
        self.add_notification_channel("log", self._log_notification)
        
        # Email channel
        if self.config.alerts.smtp_server:
            self.add_notification_channel("email", self._email_notification)
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.name] = rule
        self.logger.debug(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, name: str):
        """Remove an alert rule"""
        if name in self.alert_rules:
            del self.alert_rules[name]
            self.logger.debug(f"Removed alert rule: {name}")
    
    def add_notification_channel(self, name: str, channel_func: Callable[[Alert, AlertRule], None]):
        """Add a notification channel"""
        self.notification_channels[name] = channel_func
        self.logger.debug(f"Added notification channel: {name}")
    
    def add_custom_action(self, name: str, action_func: Callable[[Alert, AlertRule], None]):
        """Add a custom action for alerts"""
        self.custom_actions[name] = action_func
        self.logger.debug(f"Added custom action: {name}")
    
    def create_alert(self, title: str, message: str, severity: AlertSeverity, source: str,
                    metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> Alert:
        """Create a new alert"""
        alert_id = f"{source}_{int(time.time() * 1000000)}"
        
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            severity=severity,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {},
            tags=tags or []
        )
        
        # Store alert
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Check alert rules and trigger notifications
        self._process_alert_rules(alert)
        
        # Cleanup old alerts if needed
        self._cleanup_old_alerts()
        
        self.logger.info(f"Created alert: {title} ({severity.value}) from {source}")
        return alert
    
    def _process_alert_rules(self, alert: Alert):
        """Process alert rules and trigger notifications"""
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule matches this alert
            if self._rule_matches_alert(rule, alert):
                # Check cooldown
                if not self._is_in_cooldown(rule_name):
                    # Check suppression
                    if not self._is_suppressed(rule_name):
                        # Trigger notifications
                        self._trigger_notifications(alert, rule)
                        
                        # Update last alert time
                        self._last_alert_time[rule_name] = time.time()
                        
                        # Apply suppression if configured
                        if rule.suppression_hours > 0:
                            self._suppress_rule(rule_name, rule.suppression_hours)
    
    def _rule_matches_alert(self, rule: AlertRule, alert: Alert) -> bool:
        """Check if an alert rule matches an alert"""
        # Simple rule matching - in production, you might want more sophisticated logic
        if rule.condition == "cpu_usage > 80":
            return (alert.source == "system_resources" and 
                   alert.metadata.get("metric") == "cpu_usage" and
                   alert.metadata.get("value", 0) > 80)
        
        elif rule.condition == "memory_usage > 85":
            return (alert.source == "system_resources" and 
                   alert.metadata.get("metric") == "memory_usage" and
                   alert.metadata.get("value", 0) > 85)
        
        elif rule.condition == "disk_usage > 90":
            return (alert.source == "system_resources" and 
                   alert.metadata.get("metric") == "disk_usage" and
                   alert.metadata.get("value", 0) > 90)
        
        elif rule.condition == "db_connections_failed > 0":
            return (alert.source == "database" and 
                   alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL])
        
        elif rule.condition == "cache_hit_rate < 0.5":
            return (alert.source == "cache" and 
                   alert.metadata.get("metric") == "hit_rate" and
                   alert.metadata.get("value", 1.0) < 0.5)
        
        elif rule.condition == "operation_duration > 5.0":
            return (alert.source == "performance" and 
                   alert.metadata.get("metric") == "duration" and
                   alert.metadata.get("value", 0) > 5.0)
        
        # Default: match by source and severity
        return (alert.source == rule.name.split('_')[0] or 
                alert.severity == rule.severity)
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if a rule is in cooldown period"""
        if rule_name not in self._last_alert_time:
            return False
        
        rule = self.alert_rules.get(rule_name)
        if not rule:
            return False
        
        cooldown_seconds = rule.cooldown_minutes * 60
        return (time.time() - self._last_alert_time[rule_name]) < cooldown_seconds
    
    def _is_suppressed(self, rule_name: str) -> bool:
        """Check if a rule is currently suppressed"""
        if rule_name not in self._suppressed_alerts:
            return False
        
        suppression_until = self._suppressed_alerts[rule_name]
        return datetime.now() < suppression_until
    
    def _suppress_rule(self, rule_name: str, hours: int):
        """Suppress a rule for the specified number of hours"""
        suppression_until = datetime.now() + timedelta(hours=hours)
        self._suppressed_alerts[rule_name] = suppression_until
        self.logger.info(f"Suppressed rule {rule_name} until {suppression_until}")
    
    def _trigger_notifications(self, alert: Alert, rule: AlertRule):
        """Trigger notifications for an alert"""
        # Send to configured channels
        for channel_name in rule.notification_channels:
            if channel_name in self.notification_channels:
                try:
                    self.notification_channels[channel_name](alert, rule)
                except Exception as e:
                    self.logger.error(f"Error sending notification to {channel_name}: {e}")
        
        # Execute custom actions
        for action_name in rule.custom_actions:
            if action_name in self.custom_actions:
                try:
                    self.custom_actions[action_name](alert, rule)
                except Exception as e:
                    self.logger.error(f"Error executing custom action {action_name}: {e}")
    
    def _log_notification(self, alert: Alert, rule: AlertRule):
        """Log notification channel"""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        self.logger.log(log_level, 
                       f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.message}")
    
    def _email_notification(self, alert: Alert, rule: AlertRule):
        """Email notification channel"""
        if not self.config.alerts.smtp_server:
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.alerts.smtp_username or "noreply@aas-engine.com"
            msg['To'] = ", ".join(self.config.alerts.email_recipients)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Create email body
            body = f"""
Alert Details:
--------------
Title: {alert.title}
Message: {alert.message}
Severity: {alert.severity.value}
Source: {alert.source}
Timestamp: {alert.timestamp}
Rule: {rule.name}

Alert ID: {alert.id}
Status: {alert.status.value}

This is an automated alert from the AAS Data Modeling Engine monitoring system.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config.alerts.smtp_server, self.config.alerts.smtp_port) as server:
                if self.config.alerts.smtp_username and self.config.alerts.smtp_password:
                    server.starttls()
                    server.login(self.config.alerts.smtp_username, self.config.alerts.smtp_password)
                
                server.send_message(msg)
            
            self.logger.info(f"Sent email alert to {len(self.config.alerts.email_recipients)} recipients")
            
        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            
            self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
    
    def resolve_alert(self, alert_id: str, resolved_by: str):
        """Resolve an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.now()
            
            self.logger.info(f"Alert {alert_id} resolved by {resolved_by}")
    
    def suppress_alert(self, alert_id: str, suppress_until: datetime):
        """Suppress an alert until a specific time"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            alert.suppression_until = suppress_until
            
            self.logger.info(f"Alert {alert_id} suppressed until {suppress_until}")
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None, 
                         source: Optional[str] = None) -> List[Alert]:
        """Get active alerts with optional filtering"""
        active_alerts = [alert for alert in self.alerts.values() 
                        if alert.status == AlertStatus.ACTIVE]
        
        if severity:
            active_alerts = [alert for alert in active_alerts if alert.severity == severity]
        
        if source:
            active_alerts = [alert for alert in active_alerts if alert.source == source]
        
        return active_alerts
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of all alerts"""
        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE])
        acknowledged_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACKNOWLEDGED])
        resolved_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.RESOLVED])
        suppressed_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.SUPPRESSED])
        
        # Count by severity
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([a for a in self.alerts.values() if a.severity == severity])
        
        # Count by source
        source_counts = {}
        for alert in self.alerts.values():
            source_counts[alert.source] = source_counts.get(alert.source, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "resolved_alerts": resolved_alerts,
            "suppressed_alerts": suppressed_alerts,
            "severity_breakdown": severity_counts,
            "source_breakdown": source_counts,
            "alert_rules": len(self.alert_rules),
            "notification_channels": list(self.notification_channels.keys())
        }
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for the specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
    
    def _cleanup_old_alerts(self):
        """Clean up old alerts from memory"""
        # Keep only the last 1000 alerts in memory
        if len(self.alerts) > 1000:
            # Remove oldest alerts
            sorted_alerts = sorted(self.alerts.values(), key=lambda x: x.timestamp)
            alerts_to_remove = len(sorted_alerts) - 1000
            
            for i in range(alerts_to_remove):
                alert = sorted_alerts[i]
                del self.alerts[alert.id]
    
    def start_alert_processing(self):
        """Start alert processing"""
        self.logger.info("Alert processing started")
    
    def stop_alert_processing(self):
        """Stop alert processing"""
        self.logger.info("Alert processing stopped")
    
    def export_alerts(self, format: str = "json", filepath: Optional[Path] = None) -> Path:
        """Export alerts to file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alerts_{timestamp}.{format}"
            filepath = self.config.export.export_directory / filename
        
        if format == "json":
            self._export_json(filepath)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        self.logger.info(f"Exported alerts to {filepath}")
        return filepath
    
    def _export_json(self, filepath: Path):
        """Export alerts to JSON format"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "alert_summary": self.get_alert_summary(),
            "active_alerts": [],
            "alert_history": [],
            "alert_rules": {}
        }
        
        # Export active alerts
        for alert in self.alerts.values():
            export_data["active_alerts"].append({
                "id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity.value,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "status": alert.status.value,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_by": alert.resolved_by,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "metadata": alert.metadata,
                "tags": alert.tags,
                "suppression_until": alert.suppression_until.isoformat() if alert.suppression_until else None
            })
        
        # Export alert history (last 100)
        for alert in self.alert_history[-100:]:
            export_data["alert_history"].append({
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity.value,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "status": alert.status.value
            })
        
        # Export alert rules
        for rule_name, rule in self.alert_rules.items():
            export_data["alert_rules"][rule_name] = {
                "description": rule.description,
                "condition": rule.condition,
                "severity": rule.severity.value,
                "enabled": rule.enabled,
                "cooldown_minutes": rule.cooldown_minutes,
                "suppression_hours": rule.suppression_hours,
                "notification_channels": rule.notification_channels,
                "custom_actions": rule.custom_actions
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def reset_alerts(self):
        """Reset all alerts"""
        self.alerts.clear()
        self.alert_history.clear()
        self._last_alert_time.clear()
        self._suppressed_alerts.clear()
        self.logger.info("All alerts reset")
    
    def test_notification_channels(self):
        """Test all notification channels"""
        test_alert = Alert(
            id="test_alert",
            title="Test Alert",
            message="This is a test alert to verify notification channels",
            severity=AlertSeverity.INFO,
            source="test",
            timestamp=datetime.now()
        )
        
        test_rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition="test",
            severity=AlertSeverity.INFO,
            notification_channels=list(self.notification_channels.keys())
        )
        
        self.logger.info("Testing notification channels...")
        self._trigger_notifications(test_alert, test_rule)
        self.logger.info("Notification channel test completed")
