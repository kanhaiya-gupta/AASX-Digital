"""
Audit Logging Service
====================

Handles comprehensive audit logging for security events and user activities.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)

class AuditService:
    """Service for handling audit logging and security event tracking"""
    
    def __init__(self, auth_db):
        """Initialize audit service with database connection"""
        self.auth_db = auth_db
        
        # Audit event types
        self.event_types = {
            # Authentication events
            'login_success': 'User successfully logged in',
            'login_failed': 'User failed to log in',
            'logout': 'User logged out',
            'password_reset_requested': 'Password reset requested',
            'password_reset_completed': 'Password reset completed',
            'password_changed': 'Password changed',
            
            # MFA events
            'mfa_enabled': 'MFA enabled for user',
            'mfa_disabled': 'MFA disabled for user',
            'mfa_verification_success': 'MFA verification successful',
            'mfa_verification_failed': 'MFA verification failed',
            'mfa_backup_code_used': 'MFA backup code used',
            
            # Security events
            'account_locked': 'Account locked due to failed attempts',
            'account_unlocked': 'Account unlocked',
            'rate_limit_exceeded': 'Rate limit exceeded',
            'suspicious_activity': 'Suspicious activity detected',
            'security_alert': 'Security alert triggered',
            
            # User management events
            'user_created': 'User account created',
            'user_updated': 'User account updated',
            'user_deleted': 'User account deleted',
            'user_activated': 'User account activated',
            'user_deactivated': 'User account deactivated',
            
            # Session events
            'session_created': 'New session created',
            'session_revoked': 'Session revoked',
            'session_expired': 'Session expired',
            
            # Social login events
            'social_account_linked': 'Social account linked',
            'social_account_unlinked': 'Social account unlinked',
            'social_login_success': 'Social login successful',
            'social_login_failed': 'Social login failed',
            
            # Admin events
            'admin_action': 'Admin action performed',
            'permission_granted': 'Permission granted',
            'permission_revoked': 'Permission revoked',
            'role_changed': 'User role changed',
            
            # Data access events
            'data_access': 'Data accessed',
            'data_export': 'Data exported',
            'data_import': 'Data imported',
            'data_modified': 'Data modified',
            'data_deleted': 'Data deleted',
            'data_exported': 'Data exported',
            
            # Compliance events
            'gdpr_request': 'GDPR data request',
            'gdpr_deletion': 'GDPR data deletion',
            'compliance_audit': 'Compliance audit performed',
            'data_retention': 'Data retention policy applied',
            
            # System events
            'system_backup': 'System backup performed',
            'system_restore': 'System restore performed',
            'configuration_change': 'System configuration changed',
            'maintenance_mode': 'Maintenance mode toggled'
        }
        
        # Compliance configuration
        self.compliance_config = {
            'gdpr_enabled': True,
            'data_retention_days': 90,
            'audit_retention_days': 365,
            'sensitive_data_fields': ['password', 'ssn', 'credit_card', 'phone'],
            'encryption_required': True
        }
        
        # Log retention configuration
        self.retention_config = {
            'audit_logs_days': 365,
            'security_events_days': 730,
            'user_activity_days': 90,
            'system_events_days': 180
        }
    
    def log_event(self, user_id: str, event_type: str, ip_address: str = None, 
                  user_agent: str = None, details: dict = None, 
                  resource_type: str = None, resource_id: str = None) -> bool:
        """
        Log an audit event
        
        Args:
            user_id: ID of the user performing the action
            event_type: Type of event (from self.event_types)
            ip_address: IP address of the client
            user_agent: User agent string
            details: Additional event details
            resource_type: Type of resource affected
            resource_id: ID of resource affected
        """
        try:
            # Validate event type
            if event_type not in self.event_types:
                logger.warning(f"Unknown event type: {event_type}")
            
            # Prepare event details
            event_details = {
                'event_type': event_type,
                'description': self.event_types.get(event_type, 'Unknown event'),
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': self._sanitize_details(details or {}),
                'resource_type': resource_type,
                'resource_id': resource_id,
                'severity': self._get_event_severity(event_type),
                'compliance_relevant': self._is_compliance_relevant(event_type)
            }
            
            # Log to database
            success = self.auth_db.log_user_activity(
                user_id=user_id,
                activity_type=event_type,
                resource_type=resource_type or 'audit',
                details=event_details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if success:
                logger.info(f"Audit event logged: {event_type} by user {user_id}")
            else:
                logger.error(f"Failed to log audit event: {event_type} by user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return False
    
    def log_security_event(self, user_id: str, event_type: str, ip_address: str = None,
                          user_agent: str = None, details: dict = None) -> bool:
        """
        Log a security-specific event
        
        Args:
            user_id: ID of the user involved
            event_type: Type of security event
            ip_address: IP address of the client
            user_agent: User agent string
            details: Additional event details
        """
        try:
            # Add security-specific metadata
            security_details = details or {}
            security_details['security_event'] = True
            security_details['timestamp'] = datetime.utcnow().isoformat()
            
            return self.log_event(
                user_id=user_id,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                details=security_details,
                resource_type='security'
            )
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            return False
    
    def log_authentication_event(self, user_id: str, event_type: str, 
                                ip_address: str = None, user_agent: str = None,
                                details: dict = None) -> bool:
        """
        Log an authentication-related event
        
        Args:
            user_id: ID of the user
            event_type: Type of authentication event
            ip_address: IP address of the client
            user_agent: User agent string
            details: Additional event details
        """
        try:
            # Add authentication-specific metadata
            auth_details = details or {}
            auth_details['authentication_event'] = True
            auth_details['timestamp'] = datetime.utcnow().isoformat()
            
            return self.log_event(
                user_id=user_id,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                details=auth_details,
                resource_type='authentication'
            )
            
        except Exception as e:
            logger.error(f"Error logging authentication event: {e}")
            return False
    
    def log_admin_event(self, admin_user_id: str, event_type: str, 
                        target_user_id: str = None, ip_address: str = None,
                        user_agent: str = None, details: dict = None) -> bool:
        """
        Log an admin action
        
        Args:
            admin_user_id: ID of the admin user
            event_type: Type of admin event
            target_user_id: ID of the target user (if applicable)
            ip_address: IP address of the client
            user_agent: User agent string
            details: Additional event details
        """
        try:
            # Add admin-specific metadata
            admin_details = details or {}
            admin_details['admin_event'] = True
            admin_details['target_user_id'] = target_user_id
            admin_details['timestamp'] = datetime.utcnow().isoformat()
            
            return self.log_event(
                user_id=admin_user_id,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                details=admin_details,
                resource_type='admin'
            )
            
        except Exception as e:
            logger.error(f"Error logging admin event: {e}")
            return False
    
    def log_data_access(self, user_id: str, data_type: str, action: str,
                        resource_id: str = None, ip_address: str = None,
                        user_agent: str = None, details: dict = None) -> bool:
        """
        Log data access events for compliance
        
        Args:
            user_id: ID of the user accessing data
            data_type: Type of data being accessed
            action: Action performed (view, export, modify, delete)
            resource_id: ID of the resource being accessed
            ip_address: IP address of the client
            user_agent: User agent string
            details: Additional event details
        """
        try:
            # Add data access-specific metadata
            access_details = details or {}
            access_details['data_access'] = True
            access_details['data_type'] = data_type
            access_details['action'] = action
            access_details['timestamp'] = datetime.utcnow().isoformat()
            
            return self.log_event(
                user_id=user_id,
                event_type=f'data_{action}',
                ip_address=ip_address,
                user_agent=user_agent,
                details=access_details,
                resource_type=data_type,
                resource_id=resource_id
            )
            
        except Exception as e:
            logger.error(f"Error logging data access event: {e}")
            return False
    
    def get_audit_logs(self, user_id: str = None, event_type: str = None,
                       start_date: datetime = None, end_date: datetime = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit logs with optional filtering
        
        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of logs to return
        """
        try:
            # Build query parameters
            query_params = {}
            if user_id:
                query_params['user_id'] = user_id
            if event_type:
                query_params['activity_type'] = event_type
            if start_date:
                query_params['start_date'] = start_date.isoformat()
            if end_date:
                query_params['end_date'] = end_date.isoformat()
            
            # Get logs from database
            logs = self.auth_db.get_user_activity_logs(
                user_id=user_id,
                activity_type=event_type,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # Process logs for compliance
            processed_logs = []
            for log in logs:
                processed_log = self._process_log_for_compliance(log)
                processed_logs.append(processed_log)
            
            return processed_logs
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    def get_security_events(self, user_id: str = None, start_date: datetime = None,
                           end_date: datetime = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get security-specific events
        
        Args:
            user_id: Filter by user ID
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of events to return
        """
        try:
            # Get security events from audit logs
            security_events = self.get_audit_logs(
                user_id=user_id,
                event_type='security',
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            # Filter for security-specific events
            filtered_events = []
            for event in security_events:
                if self._is_security_event(event.get('event_type', '')):
                    filtered_events.append(event)
            
            return filtered_events
            
        except Exception as e:
            logger.error(f"Error getting security events: {e}")
            return []
    
    def get_compliance_report(self, start_date: datetime = None, 
                             end_date: datetime = None) -> Dict[str, Any]:
        """
        Generate compliance report for GDPR and other regulations
        
        Args:
            start_date: Start date for report
            end_date: End date for report
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get compliance-relevant events
            compliance_events = self.get_audit_logs(
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            
            # Filter for compliance-relevant events
            compliance_relevant = [
                event for event in compliance_events
                if event.get('compliance_relevant', False)
            ]
            
            # Generate report
            report = {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'total_events': len(compliance_events),
                'compliance_events': len(compliance_relevant),
                'gdpr_requests': len([e for e in compliance_relevant if 'gdpr' in e.get('event_type', '')]),
                'data_access_events': len([e for e in compliance_relevant if 'data_access' in e.get('event_type', '')]),
                'security_events': len([e for e in compliance_relevant if self._is_security_event(e.get('event_type', ''))]),
                'user_activity_summary': self._generate_activity_summary(compliance_events),
                'compliance_status': self._assess_compliance_status(compliance_relevant)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {}
    
    def cleanup_old_logs(self, days_to_keep: int = None) -> bool:
        """
        Clean up old audit logs based on retention policy
        
        Args:
            days_to_keep: Number of days to keep logs (uses default if None)
        """
        try:
            if not days_to_keep:
                days_to_keep = self.retention_config['audit_logs_days']
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Clean up old logs from database
            success = self.auth_db.cleanup_old_activity_logs(cutoff_date)
            
            if success:
                logger.info(f"Cleaned up audit logs older than {days_to_keep} days")
            else:
                logger.error("Failed to cleanup old audit logs")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return False
    
    def _sanitize_details(self, details: dict) -> dict:
        """Sanitize sensitive information from details"""
        try:
            sanitized = details.copy()
            
            # Remove sensitive fields
            for field in self.compliance_config['sensitive_data_fields']:
                if field in sanitized:
                    sanitized[field] = '[REDACTED]'
            
            # Hash sensitive information if needed
            if self.compliance_config['encryption_required']:
                for key, value in sanitized.items():
                    if isinstance(value, str) and any(sensitive in key.lower() for sensitive in self.compliance_config['sensitive_data_fields']):
                        sanitized[key] = hashlib.sha256(value.encode()).hexdigest()[:8] + '***'
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing details: {e}")
            return details
    
    def _get_event_severity(self, event_type: str) -> str:
        """Get severity level for an event type"""
        try:
            # Define severity levels
            high_severity = {
                'login_failed', 'account_locked', 'suspicious_activity',
                'security_alert', 'data_deleted', 'gdpr_deletion'
            }
            
            medium_severity = {
                'password_changed', 'mfa_verification_failed', 'rate_limit_exceeded',
                'data_modified', 'admin_action', 'permission_revoked'
            }
            
            if event_type in high_severity:
                return 'high'
            elif event_type in medium_severity:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error getting event severity: {e}")
            return 'low'
    
    def _is_compliance_relevant(self, event_type: str) -> bool:
        """Check if event is relevant for compliance reporting"""
        try:
            compliance_events = {
                'gdpr_request', 'gdpr_deletion', 'data_access', 'data_export',
                'data_import', 'data_modified', 'data_deleted', 'compliance_audit',
                'data_retention', 'user_created', 'user_deleted', 'permission_granted',
                'permission_revoked', 'role_changed'
            }
            
            return event_type in compliance_events
            
        except Exception as e:
            logger.error(f"Error checking compliance relevance: {e}")
            return False
    
    def _is_security_event(self, event_type: str) -> bool:
        """Check if event is a security event"""
        try:
            security_events = {
                'login_failed', 'account_locked', 'suspicious_activity',
                'security_alert', 'rate_limit_exceeded', 'mfa_verification_failed',
                'password_changed', 'session_revoked'
            }
            
            return event_type in security_events
            
        except Exception as e:
            logger.error(f"Error checking security event: {e}")
            return False
    
    def _process_log_for_compliance(self, log: dict) -> dict:
        """Process log entry for compliance requirements"""
        try:
            processed = log.copy()
            
            # Add compliance metadata
            processed['compliance_relevant'] = self._is_compliance_relevant(log.get('activity_type', ''))
            processed['severity'] = self._get_event_severity(log.get('activity_type', ''))
            
            # Sanitize sensitive data
            if 'details' in processed and isinstance(processed['details'], dict):
                processed['details'] = self._sanitize_details(processed['details'])
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing log for compliance: {e}")
            return log
    
    def _generate_activity_summary(self, events: List[dict]) -> dict:
        """Generate activity summary for compliance report"""
        try:
            summary = {
                'total_events': len(events),
                'unique_users': len(set(event.get('user_id') for event in events if event.get('user_id'))),
                'event_types': {},
                'daily_activity': {}
            }
            
            # Count event types
            for event in events:
                event_type = event.get('activity_type', 'unknown')
                summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
            
            # Daily activity
            for event in events:
                timestamp = event.get('timestamp', '')
                if timestamp:
                    try:
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date().isoformat()
                        summary['daily_activity'][date] = summary['daily_activity'].get(date, 0) + 1
                    except:
                        pass
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating activity summary: {e}")
            return {}
    
    def _assess_compliance_status(self, events: List[dict]) -> dict:
        """Assess compliance status based on events"""
        try:
            status = {
                'gdpr_compliant': True,
                'data_protection_adequate': True,
                'audit_trail_complete': True,
                'issues': []
            }
            
            # Check for GDPR compliance issues
            gdpr_events = [e for e in events if 'gdpr' in e.get('activity_type', '')]
            if not gdpr_events:
                status['issues'].append('No GDPR-related events found')
            
            # Check for data access logging
            data_access_events = [e for e in events if 'data_access' in e.get('activity_type', '')]
            if not data_access_events:
                status['issues'].append('No data access logging found')
                status['data_protection_adequate'] = False
            
            # Check for security events
            security_events = [e for e in events if self._is_security_event(e.get('activity_type', ''))]
            if not security_events:
                status['issues'].append('No security events found')
            
            return status
            
        except Exception as e:
            logger.error(f"Error assessing compliance status: {e}")
            return {'gdpr_compliant': False, 'data_protection_adequate': False, 'audit_trail_complete': False, 'issues': [str(e)]} 