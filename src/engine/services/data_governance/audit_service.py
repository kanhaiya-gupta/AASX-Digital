"""
Audit Manager Service

Enterprise-grade audit logging and compliance tracking service.
Provides comprehensive audit trail for all operations across the system.

Features:
- Cross-domain audit logging
- Compliance framework support
- Audit trail persistence
- Real-time audit monitoring
- Compliance reporting
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...monitoring.monitoring_config import MonitoringConfig


class AuditLevel(Enum):
    """Audit levels for different types of operations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class AuditCategory(Enum):
    """Audit categories for classification"""
    USER_ACTION = "user_action"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_EVENT = "security_event"
    DATA_ACCESS = "data_access"
    BUSINESS_OPERATION = "business_operation"
    COMPLIANCE_CHECK = "compliance_check"
    PERFORMANCE_METRIC = "performance_metric"


@dataclass
class AuditEvent:
    """Audit event data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    level: AuditLevel = AuditLevel.INFO
    category: AuditCategory = AuditCategory.SYSTEM_OPERATION
    operation: str = ""
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    dept_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    compliance_framework: Optional[str] = None
    risk_level: Optional[str] = None


class AuditManager:
    """
    Enterprise audit manager for comprehensive audit logging and compliance tracking.
    
    Provides:
    - Cross-domain audit logging
    - Compliance framework support
    - Real-time audit monitoring
    - Audit trail persistence
    - Compliance reporting
    """
    
    def __init__(self, config: MonitoringConfig):
        """
        Initialize the audit manager.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.audit_events: List[AuditEvent] = []
        self.max_events = config.audit.max_events if hasattr(config, 'audit') else 10000
        self.retention_days = config.audit.retention_days if hasattr(config, 'audit') else 90
        
        self.logger.info("AuditManager initialized with enterprise-grade audit capabilities")
    
    async def log_operation(
        self,
        operation: str,
        target_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO,
        category: AuditCategory = AuditCategory.BUSINESS_OPERATION
    ) -> str:
        """
        Log an audit event for an operation.
        
        Args:
            operation: Operation being performed
            target_id: Target entity ID
            user_context: User context information
            metadata: Additional metadata
            level: Audit level
            category: Audit category
            
        Returns:
            Audit event ID
        """
        try:
            # Extract user context information
            user_id = user_context.get('user_id') if user_context else None
            org_id = user_context.get('org_id') if user_context else None
            dept_id = user_context.get('dept_id') if user_context else None
            
            # Create audit event
            audit_event = AuditEvent(
                level=level,
                category=category,
                operation=operation,
                target_id=target_id,
                target_type=metadata.get('target_type') if metadata else None,
                user_id=user_id,
                org_id=org_id,
                dept_id=dept_id,
                metadata=metadata or {},
                compliance_framework=metadata.get('compliance_framework') if metadata else None,
                risk_level=metadata.get('risk_level') if metadata else None
            )
            
            # Store audit event
            await self._store_audit_event(audit_event)
            
            # Log to logger for immediate visibility
            self.logger.info(
                f"Audit: {operation} | User: {user_id} | Target: {target_id} | "
                f"Level: {level.value} | Category: {category.value}"
            )
            
            return audit_event.id
            
        except Exception as e:
            self.logger.error(f"Error logging audit event: {e}")
            return ""
    
    async def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a security-related audit event.
        
        Args:
            event_type: Type of security event
            user_id: User ID involved
            ip_address: IP address
            metadata: Additional security metadata
            
        Returns:
            Audit event ID
        """
        return await self.log_operation(
            operation=event_type,
            user_context={'user_id': user_id} if user_id else None,
            metadata={
                'ip_address': ip_address,
                'security_event': True,
                **(metadata or {})
            },
            level=AuditLevel.SECURITY,
            category=AuditCategory.SECURITY_EVENT
        )
    
    async def log_compliance_check(
        self,
        compliance_framework: str,
        check_type: str,
        result: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a compliance check audit event.
        
        Args:
            compliance_framework: Compliance framework name
            check_type: Type of compliance check
            result: Check result
            metadata: Additional compliance metadata
            
        Returns:
            Audit event ID
        """
        return await self.log_operation(
            operation=f"compliance_check_{check_type}",
            metadata={
                'compliance_framework': compliance_framework,
                'check_type': check_type,
                'result': result,
                'compliance_event': True,
                **(metadata or {})
            },
            level=AuditLevel.INFO,
            category=AuditCategory.COMPLIANCE_CHECK
        )
    
    async def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[AuditLevel] = None,
        category: Optional[AuditCategory] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Retrieve audit trail with filtering options.
        
        Args:
            user_id: Filter by user ID
            org_id: Filter by organization ID
            dept_id: Filter by department ID
            start_date: Filter from date
            end_date: Filter to date
            level: Filter by audit level
            category: Filter by audit category
            limit: Maximum number of events to return
            
        Returns:
            List of audit events
        """
        try:
            filtered_events = []
            
            for event in self.audit_events:
                # Apply filters
                if user_id and event.user_id != user_id:
                    continue
                if org_id and event.org_id != org_id:
                    continue
                if dept_id and event.dept_id != dept_id:
                    continue
                if start_date and event.timestamp < start_date:
                    continue
                if end_date and event.timestamp > end_date:
                    continue
                if level and event.level != level:
                    continue
                if category and event.category != category:
                    continue
                
                filtered_events.append(event)
                
                if len(filtered_events) >= limit:
                    break
            
            return filtered_events
            
        except Exception as e:
            self.logger.error(f"Error retrieving audit trail: {e}")
            return []
    
    async def generate_compliance_report(
        self,
        compliance_framework: str,
        org_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report for a specific framework.
        
        Args:
            compliance_framework: Compliance framework name
            org_id: Organization ID to filter
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Compliance report data
        """
        try:
            # Get relevant audit events
            events = await self.get_audit_trail(
                org_id=org_id,
                start_date=start_date,
                end_date=end_date,
                category=AuditCategory.COMPLIANCE_CHECK
            )
            
            # Filter by compliance framework
            framework_events = [
                e for e in events 
                if e.metadata.get('compliance_framework') == compliance_framework
            ]
            
            # Generate report
            report = {
                'compliance_framework': compliance_framework,
                'report_period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'total_checks': len(framework_events),
                'passed_checks': len([e for e in framework_events if e.metadata.get('result') == 'passed']),
                'failed_checks': len([e for e in framework_events if e.metadata.get('result') == 'failed']),
                'compliance_score': 0.0,
                'risk_assessment': 'low',
                'recommendations': []
            }
            
            # Calculate compliance score
            if report['total_checks'] > 0:
                report['compliance_score'] = (report['passed_checks'] / report['total_checks']) * 100
            
            # Determine risk level
            if report['compliance_score'] >= 90:
                report['risk_assessment'] = 'low'
            elif report['compliance_score'] >= 70:
                report['risk_assessment'] = 'medium'
            else:
                report['risk_assessment'] = 'high'
            
            # Add recommendations
            if report['compliance_score'] < 90:
                report['recommendations'].append("Increase compliance monitoring frequency")
            if report['failed_checks'] > 0:
                report['recommendations'].append("Review and address failed compliance checks")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {e}")
            return {'error': str(e)}
    
    async def _store_audit_event(self, event: AuditEvent) -> None:
        """
        Store an audit event in memory (for now).
        In production, this would persist to database.
        
        Args:
            event: Audit event to store
        """
        try:
            # Add to memory storage
            self.audit_events.append(event)
            
            # Enforce storage limits
            if len(self.audit_events) > self.max_events:
                # Remove oldest events
                self.audit_events = self.audit_events[-self.max_events:]
            
            # TODO: In production, persist to database
            # await self._persist_to_database(event)
            
        except Exception as e:
            self.logger.error(f"Error storing audit event: {e}")
    
    async def cleanup_old_events(self) -> int:
        """
        Clean up old audit events based on retention policy.
        
        Returns:
            Number of events cleaned up
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            original_count = len(self.audit_events)
            
            # Remove old events
            self.audit_events = [
                e for e in self.audit_events 
                if e.timestamp > cutoff_date
            ]
            
            cleaned_count = original_count - len(self.audit_events)
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old audit events")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old audit events: {e}")
            return 0
