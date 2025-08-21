"""
Cross-Domain Audit Service

Coordinates audit operations across all business domains, authentication, and data governance services.
Provides comprehensive audit trail and logging for the entire AAS Data Modeling Engine.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from ...repositories.business_domain_repository import BusinessDomainRepository
from ...repositories.auth_repository import AuthRepository
from ...repositories.data_governance_repository import DataGovernanceRepository
from ...models.business_domain import Organization, Project, File
from ...models.auth import User
from ...models.data_governance import DataLineage, DataQualityMetrics, ChangeRequest, DataVersion, GovernancePolicy
from ..base.base_service import BaseService

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """Represents an audit event across all domains."""
    event_id: str
    timestamp: str
    user_id: str
    user_name: str
    domain: str  # business_domain, auth, data_governance
    service: str
    operation: str
    entity_type: str
    entity_id: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    risk_level: str = "low"
    compliance_status: str = "compliant"


@dataclass
class AuditTrail:
    """Represents a complete audit trail for an entity."""
    entity_id: str
    entity_type: str
    domain: str
    events: List[AuditEvent]
    total_events: int = 0
    first_event: Optional[str] = None
    last_event: Optional[str] = None
    risk_assessment: str = "low"
    compliance_score: float = 100.0


@dataclass
class ComplianceReport:
    """Represents a compliance report across all domains."""
    report_id: str
    generated_at: str
    scope: str  # organization, project, user, system
    scope_id: str
    period_start: str
    period_end: str
    total_events: int
    compliant_events: int
    non_compliant_events: int
    compliance_rate: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    risk_level: str


class AuditService(BaseService):
    """
    Cross-domain audit service that coordinates audit operations across all services.
    
    Provides comprehensive audit trail, compliance monitoring, and risk assessment
    for business domain, authentication, and data governance operations.
    """
    
    def __init__(self, 
                 business_repo: BusinessDomainRepository,
                 auth_repo: AuthRepository,
                 governance_repo: DataGovernanceRepository):
        super().__init__("AuditService")
        
        # Repository dependencies for cross-domain operations
        self.business_repo = business_repo
        self.auth_repo = auth_repo
        self.governance_repo = governance_repo
        
        # In-memory audit cache for performance
        self._audit_cache = {}
        self._compliance_cache = {}
        self._risk_cache = {}
        
        # Audit configuration
        self.audit_retention_days = 365
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9
        }
        
        # Performance metrics
        self.events_logged = 0
        self.audit_queries = 0
        self.compliance_checks = 0
        self.risk_assessments = 0
        
        # Initialize service resources
        asyncio.create_task(self._initialize_service_resources())
    
    async def _initialize_service_resources(self) -> None:
        """Initialize service resources and load initial data."""
        try:
            logger.info("Initializing Audit Service resources...")
            
            # Load existing audit data into cache
            await self._load_audit_cache()
            
            # Initialize audit monitoring
            await self._initialize_audit_monitoring()
            
            logger.info("Audit Service resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Audit Service resources: {e}")
            self.handle_error("_initialize_service_resources", e)
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            'service_name': self.service_name,
            'service_type': 'integration.audit',
            'status': 'active' if self.is_active else 'inactive',
            'uptime': str(datetime.now() - self.start_time),
            'cache_size': len(self._audit_cache),
            'events_logged': self.events_logged,
            'audit_queries': self.audit_queries,
            'compliance_checks': self.compliance_checks,
            'risk_assessments': self.risk_assessments
        }
    
    async def _cleanup_service_resources(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Clear caches
            self._audit_cache.clear()
            self._compliance_cache.clear()
            self._risk_cache.clear()
            
            logger.info(f"{self.service_name}: Cleaned up service resources")
            
        except Exception as e:
            logger.error(f"{self.service_name}: Error during cleanup: {e}")
            self.handle_error("cleanup", e)
    
    async def log_event(self, event_data: Dict[str, Any]) -> AuditEvent:
        """Log an audit event across any domain."""
        try:
            self._log_operation("log_event", f"domain: {event_data.get('domain')}, operation: {event_data.get('operation')}")
            
            # Validate required fields
            required_fields = ['user_id', 'domain', 'service', 'operation', 'entity_type', 'entity_id']
            for field in required_fields:
                if not event_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate event ID
            event_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(event_data)}"
            
            # Get user information
            user = await self.auth_repo.get_user_by_id(event_data['user_id'])
            user_name = user.name if user else "Unknown User"
            
            # Create audit event
            audit_event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.now().isoformat(),
                user_id=event_data['user_id'],
                user_name=user_name,
                domain=event_data['domain'],
                service=event_data['service'],
                operation=event_data['operation'],
                entity_type=event_data['entity_type'],
                entity_id=event_data['entity_id'],
                details=event_data.get('details', {}),
                ip_address=event_data.get('ip_address'),
                user_agent=event_data.get('user_agent'),
                session_id=event_data.get('session_id'),
                risk_level=self._assess_event_risk(event_data),
                compliance_status=self._assess_compliance_status(event_data)
            )
            
            # Store audit event
            await self._store_audit_event(audit_event)
            
            # Update cache
            self._update_audit_cache(audit_event)
            
            # Update metrics
            self.events_logged += 1
            
            logger.info(f"Audit event logged successfully: {event_id}")
            return audit_event
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            self.handle_error("log_event", e)
            raise
    
    async def get_audit_trail(self, entity_id: str, entity_type: str, domain: str, limit: int = 100) -> AuditTrail:
        """Get complete audit trail for an entity across all domains."""
        try:
            self._log_operation("get_audit_trail", f"entity_id: {entity_id}, domain: {domain}")
            
            # Check cache first
            cache_key = f"audit_trail:{domain}:{entity_type}:{entity_id}"
            if cache_key in self._audit_cache:
                return self._audit_cache[cache_key]
            
            # Get audit events from repository
            events = await self._get_audit_events(entity_id, entity_type, domain, limit)
            
            # Create audit trail
            audit_trail = AuditTrail(
                entity_id=entity_id,
                entity_type=entity_type,
                domain=domain,
                events=events,
                total_events=len(events),
                first_event=events[0].timestamp if events else None,
                last_event=events[-1].timestamp if events else None,
                risk_assessment=self._assess_trail_risk(events),
                compliance_score=self._calculate_compliance_score(events)
            )
            
            # Update cache
            self._audit_cache[cache_key] = audit_trail
            
            # Update metrics
            self.audit_queries += 1
            
            return audit_trail
            
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            self.handle_error("get_audit_trail", e)
            return AuditTrail(entity_id=entity_id, entity_type=entity_type, domain=domain, events=[])
    
    async def get_compliance_report(self, scope: str, scope_id: str, period_days: int = 30) -> ComplianceReport:
        """Get compliance report for a specific scope across all domains."""
        try:
            self._log_operation("get_compliance_report", f"scope: {scope}, scope_id: {scope_id}")
            
            # Check cache first
            cache_key = f"compliance:{scope}:{scope_id}:{period_days}"
            if cache_key in self._compliance_cache:
                return self._compliance_cache[cache_key]
            
            # Calculate period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get audit events for the period
            events = await self._get_audit_events_for_period(scope, scope_id, start_date, end_date)
            
            # Analyze compliance
            total_events = len(events)
            compliant_events = sum(1 for e in events if e.compliance_status == "compliant")
            non_compliant_events = total_events - compliant_events
            compliance_rate = (compliant_events / total_events * 100) if total_events > 0 else 100.0
            
            # Identify violations
            violations = []
            for event in events:
                if event.compliance_status != "compliant":
                    violations.append({
                        'event_id': event.event_id,
                        'timestamp': event.timestamp,
                        'user_id': event.user_id,
                        'operation': event.operation,
                        'details': event.details,
                        'risk_level': event.risk_level
                    })
            
            # Generate recommendations
            recommendations = self._generate_compliance_recommendations(events, compliance_rate)
            
            # Assess overall risk
            risk_level = self._assess_trail_risk(events)
            
            # Create compliance report
            report = ComplianceReport(
                report_id=f"compliance_{scope}_{scope_id}_{datetime.now().strftime('%Y%m%d')}",
                generated_at=datetime.now().isoformat(),
                scope=scope,
                scope_id=scope_id,
                period_start=start_date.isoformat(),
                period_end=end_date.isoformat(),
                total_events=total_events,
                compliant_events=compliant_events,
                non_compliant_events=non_compliant_events,
                compliance_rate=compliance_rate,
                violations=violations,
                recommendations=recommendations,
                risk_level=risk_level
            )
            
            # Update cache
            self._compliance_cache[cache_key] = report
            
            # Update metrics
            self.compliance_checks += 1
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to get compliance report: {e}")
            self.handle_error("get_compliance_report", e)
            return ComplianceReport(
                report_id="", generated_at="", scope="", scope_id="", 
                period_start="", period_end="", total_events=0, compliant_events=0,
                non_compliant_events=0, compliance_rate=0.0, violations=[],
                recommendations=[], risk_level="unknown"
            )
    
    async def assess_risk(self, entity_id: str, entity_type: str, domain: str) -> Dict[str, Any]:
        """Assess risk for an entity across all domains."""
        try:
            self._log_operation("assess_risk", f"entity_id: {entity_id}, domain: {domain}")
            
            # Check cache first
            cache_key = f"risk:{domain}:{entity_type}:{entity_id}"
            if cache_key in self._risk_cache:
                return self._risk_cache[cache_key]
            
            # Get audit trail
            audit_trail = await self.get_audit_trail(entity_id, entity_type, domain)
            
            # Analyze risk factors
            risk_factors = self._analyze_risk_factors(audit_trail)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(risk_factors)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Create risk assessment
            risk_assessment = {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'domain': domain,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'assessment_date': datetime.now().isoformat(),
                'recommendations': self._generate_risk_recommendations(risk_factors, risk_level)
            }
            
            # Update cache
            self._risk_cache[cache_key] = risk_assessment
            
            # Update metrics
            self.risk_assessments += 1
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Failed to assess risk: {e}")
            self.handle_error("assess_risk", e)
            return {}
    
    # Private helper methods
    
    async def _load_audit_cache(self):
        """Load existing audit data into cache."""
        try:
            # For now, start with empty cache
            # In a real implementation, this would load from persistent storage
            logger.info("Audit cache initialized")
            
        except Exception as e:
            logger.warning(f"Failed to load audit cache: {e}")
    
    async def _initialize_audit_monitoring(self):
        """Initialize audit monitoring."""
        try:
            # Set up periodic audit monitoring
            asyncio.create_task(self._periodic_audit_monitoring())
            logger.info("Audit monitoring initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize audit monitoring: {e}")
    
    async def _store_audit_event(self, event: AuditEvent):
        """Store audit event in persistent storage."""
        try:
            # For now, just log the event
            # In a real implementation, this would store in database
            logger.debug(f"Storing audit event: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Failed to store audit event: {e}")
    
    async def _get_audit_events(self, entity_id: str, entity_type: str, domain: str, limit: int) -> List[AuditEvent]:
        """Get audit events for an entity."""
        try:
            # For now, return empty list
            # In a real implementation, this would query the audit database
            return []
            
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
    
    async def _get_audit_events_for_period(self, scope: str, scope_id: str, start_date: datetime, end_date: datetime) -> List[AuditEvent]:
        """Get audit events for a specific period and scope."""
        try:
            # For now, return empty list
            # In a real implementation, this would query the audit database
            return []
            
        except Exception as e:
            logger.error(f"Failed to get audit events for period: {e}")
            return []
    
    def _update_audit_cache(self, event: AuditEvent):
        """Update the audit cache with new data."""
        # Store event in cache
        cache_key = f"event:{event.event_id}"
        self._audit_cache[cache_key] = event
        
        # Maintain cache size
        if len(self._audit_cache) > 10000:
            # Remove oldest entries
            oldest_keys = sorted(self._audit_cache.keys(), key=lambda k: self._audit_cache[k].timestamp if hasattr(self._audit_cache[k], 'timestamp') else '0')[:1000]
            for key in oldest_keys:
                del self._audit_cache[key]
    
    def _assess_event_risk(self, event_data: Dict[str, Any]) -> str:
        """Assess risk level for an individual event."""
        # Simple risk assessment based on operation type
        high_risk_operations = ['delete', 'modify', 'admin', 'privileged']
        medium_risk_operations = ['create', 'update', 'export']
        
        operation = event_data.get('operation', '').lower()
        
        if any(op in operation for op in high_risk_operations):
            return "high"
        elif any(op in operation for op in medium_risk_operations):
            return "medium"
        else:
            return "low"
    
    def _assess_compliance_status(self, event_data: Dict[str, Any]) -> str:
        """Assess compliance status for an individual event."""
        # Simple compliance assessment
        # In a real implementation, this would check against compliance policies
        
        # Check if user has required permissions
        if event_data.get('user_id') and event_data.get('entity_id'):
            return "compliant"  # Assume compliant for now
        else:
            return "non_compliant"
    
    def _assess_trail_risk(self, events: List[AuditEvent]) -> str:
        """Assess overall risk for an audit trail."""
        if not events:
            return "low"
        
        # Count high-risk events
        high_risk_count = sum(1 for e in events if e.risk_level == "high")
        total_events = len(events)
        
        if high_risk_count / total_events > 0.3:
            return "high"
        elif high_risk_count / total_events > 0.1:
            return "medium"
        else:
            return "low"
    
    def _calculate_compliance_score(self, events: List[AuditEvent]) -> float:
        """Calculate compliance score for an audit trail."""
        if not events:
            return 100.0
        
        compliant_count = sum(1 for e in events if e.compliance_status == "compliant")
        total_events = len(events)
        
        return (compliant_count / total_events) * 100.0
    
    def _generate_compliance_recommendations(self, events: List[AuditEvent], compliance_rate: float) -> List[str]:
        """Generate compliance recommendations based on events."""
        recommendations = []
        
        if compliance_rate < 90:
            recommendations.append("Implement stricter access controls")
            recommendations.append("Review user permissions and roles")
        
        if compliance_rate < 80:
            recommendations.append("Conduct compliance training for users")
            recommendations.append("Implement automated compliance monitoring")
        
        # Add specific recommendations based on violations
        violations = [e for e in events if e.compliance_status != "compliant"]
        if violations:
            recommendations.append(f"Investigate {len(violations)} compliance violations")
        
        return recommendations
    
    def _analyze_risk_factors(self, audit_trail: AuditTrail) -> Dict[str, Any]:
        """Analyze risk factors from audit trail."""
        if not audit_trail.events:
            return {}
        
        events = audit_trail.events
        
        # Analyze various risk factors
        risk_factors = {
            'high_risk_operations': sum(1 for e in events if e.risk_level == "high"),
            'privileged_users': len(set(e.user_id for e in events if e.risk_level == "high")),
            'recent_activity': len([e for e in events if datetime.fromisoformat(e.timestamp) > datetime.now() - timedelta(days=7)]),
            'compliance_violations': sum(1 for e in events if e.compliance_status != "compliant"),
            'unique_operations': len(set(e.operation for e in events))
        }
        
        return risk_factors
    
    def _calculate_risk_score(self, risk_factors: Dict[str, Any]) -> float:
        """Calculate numerical risk score from risk factors."""
        score = 0.0
        
        # Weight different risk factors
        weights = {
            'high_risk_operations': 0.3,
            'privileged_users': 0.2,
            'recent_activity': 0.1,
            'compliance_violations': 0.3,
            'unique_operations': 0.1
        }
        
        for factor, value in risk_factors.items():
            if factor in weights:
                # Normalize value to 0-1 range and apply weight
                normalized_value = min(value / 10.0, 1.0)  # Assume max 10 for normalization
                score += normalized_value * weights[factor]
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from numerical score."""
        if risk_score >= self.risk_thresholds['high']:
            return "high"
        elif risk_score >= self.risk_thresholds['medium']:
            return "medium"
        else:
            return "low"
    
    def _generate_risk_recommendations(self, risk_factors: Dict[str, Any], risk_level: str) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if risk_factors.get('high_risk_operations', 0) > 5:
            recommendations.append("Review and restrict high-risk operations")
        
        if risk_factors.get('privileged_users', 0) > 3:
            recommendations.append("Reduce number of privileged users")
        
        if risk_factors.get('compliance_violations', 0) > 0:
            recommendations.append("Address compliance violations immediately")
        
        if risk_level == "high":
            recommendations.append("Conduct immediate security review")
            recommendations.append("Implement additional monitoring")
        
        return recommendations
    
    async def _periodic_audit_monitoring(self):
        """Periodic audit monitoring."""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                # Perform periodic audit tasks
                # This would typically include compliance checks, risk assessments, etc.
                logger.info("Completed periodic audit monitoring")
                
            except Exception as e:
                logger.error(f"Periodic audit monitoring failed: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry
