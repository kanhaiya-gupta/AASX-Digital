"""
Compliance Monitoring Service
=============================

Service for real-time compliance tracking and monitoring in federated learning.
Uses pure async patterns for optimal performance.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService
from ..models.federated_learning_registry import FederatedLearningRegistry
from ..models.federated_learning_metrics import FederatedLearningMetrics
from ..repositories.federated_learning_registry_repository import FederatedLearningRegistryRepository
from ..repositories.federated_learning_metrics_repository import FederatedLearningMetricsRepository


class ComplianceMonitoringService:
    """Service for compliance monitoring and tracking in federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService
    ):
        """Initialize service with dependencies"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Initialize repositories
        self.registry_repo = FederatedLearningRegistryRepository(connection_manager)
        self.metrics_repo = FederatedLearningMetricsRepository(connection_manager)
    
    async def monitor_compliance_status(
        self,
        registry_id: str
    ) -> Dict[str, Any]:
        """Monitor real-time compliance status (async)"""
        try:
            # Get federation details
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return {'error': 'Federation not found'}
            
            # Get latest metrics
            metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            
            # Check compliance requirements
            compliance_checks = await self._perform_compliance_checks(registry, metrics)
            
            # Calculate compliance score
            compliance_score = await self._calculate_compliance_score(compliance_checks)
            
            # Determine overall status
            overall_status = self._determine_compliance_status(compliance_score)
            
            # Generate compliance report
            compliance_report = {
                'registry_id': registry_id,
                'federation_name': registry.federation_name,
                'monitoring_date': datetime.now().isoformat(),
                'overall_status': overall_status,
                'compliance_score': compliance_score,
                'compliance_checks': compliance_checks,
                'framework': registry.compliance_framework,
                'risk_level': registry.risk_level,
                'last_audit': registry.last_audit_date.isoformat() if registry.last_audit_date else None,
                'next_audit': registry.next_audit_date.isoformat() if registry.next_audit_date else None
            }
            
            return compliance_report
            
        except Exception as e:
            print(f"❌ Failed to monitor compliance status: {e}")
            return {'error': str(e)}
    
    async def _perform_compliance_checks(
        self,
        registry: FederatedLearningRegistry,
        metrics: Optional[FederatedLearningMetrics]
    ) -> Dict[str, Dict[str, Any]]:
        """Perform comprehensive compliance checks"""
        checks = {}
        
        try:
            # Security compliance checks
            checks['security'] = await self._check_security_compliance(registry)
            
            # Privacy compliance checks
            checks['privacy'] = await self._check_privacy_compliance(registry, metrics)
            
            # Performance compliance checks
            checks['performance'] = await self._check_performance_compliance(metrics)
            
            # Data governance checks
            checks['data_governance'] = await self._check_data_governance(registry)
            
            # Audit compliance checks
            checks['audit'] = await self._check_audit_compliance(registry)
            
        except Exception as e:
            print(f"⚠️  Failed to perform compliance checks: {e}")
        
        return checks
    
    async def _check_security_compliance(self, registry: FederatedLearningRegistry) -> Dict[str, Any]:
        """Check security compliance requirements"""
        security_checks = {
            'encryption': {
                'status': 'compliant' if registry.encryption_enabled else 'non_compliant',
                'details': f"Encryption: {'Enabled' if registry.encryption_enabled else 'Disabled'}",
                'score': 100.0 if registry.encryption_enabled else 0.0
            },
            'access_control': {
                'status': 'compliant' if registry.access_control_level in ['advanced', 'enterprise'] else 'non_compliant',
                'details': f"Access Control Level: {registry.access_control_level}",
                'score': 100.0 if registry.access_control_level in ['advanced', 'enterprise'] else 50.0
            },
            'security_score': {
                'status': 'compliant' if (registry.security_score or 0) >= 80.0 else 'non_compliant',
                'details': f"Security Score: {registry.security_score or 0}",
                'score': min((registry.security_score or 0), 100.0)
            }
        }
        
        return security_checks
    
    async def _check_privacy_compliance(
        self,
        registry: FederatedLearningRegistry,
        metrics: Optional[FederatedLearningMetrics]
    ) -> Dict[str, Any]:
        """Check privacy compliance requirements"""
        privacy_checks = {
            'data_protection': {
                'status': 'compliant' if (registry.data_protection_score or 0) >= 80.0 else 'non_compliant',
                'details': f"Data Protection Score: {registry.data_protection_score or 0}",
                'score': min((registry.data_protection_score or 0), 100.0)
            },
            'privacy_preservation': {
                'status': 'compliant' if metrics and (metrics.privacy_preservation_score or 0) >= 80.0 else 'non_compliant',
                'details': f"Privacy Preservation Score: {metrics.privacy_preservation_score if metrics else 'N/A'}",
                'score': min((metrics.privacy_preservation_score or 0) if metrics else 0, 100.0)
            },
            'incident_response': {
                'status': 'compliant' if (registry.incident_response_time or 0) <= 24 else 'non_compliant',
                'details': f"Incident Response Time: {registry.incident_response_time or 'N/A'} hours",
                'score': max(100.0 - (registry.incident_response_time or 0), 0.0)
            }
        }
        
        return privacy_checks
    
    async def _check_performance_compliance(
        self,
        metrics: Optional[FederatedLearningMetrics]
    ) -> Dict[str, Any]:
        """Check performance compliance requirements"""
        if not metrics:
            return {
                'health_score': {'status': 'unknown', 'details': 'No metrics available', 'score': 0.0},
                'uptime': {'status': 'unknown', 'details': 'No metrics available', 'score': 0.0},
                'error_rate': {'status': 'unknown', 'details': 'No metrics available', 'score': 0.0}
            }
        
        performance_checks = {
            'health_score': {
                'status': 'compliant' if metrics.health_score >= 80.0 else 'non_compliant',
                'details': f"Health Score: {metrics.health_score}",
                'score': min(metrics.health_score, 100.0)
            },
            'uptime': {
                'status': 'compliant' if metrics.uptime_percentage >= 99.0 else 'non_compliant',
                'details': f"Uptime: {metrics.uptime_percentage}%",
                'score': min(metrics.uptime_percentage, 100.0)
            },
            'error_rate': {
                'status': 'compliant' if metrics.error_rate <= 1.0 else 'non_compliant',
                'details': f"Error Rate: {metrics.error_rate}%",
                'score': max(100.0 - (metrics.error_rate * 10), 0.0)
            }
        }
        
        return performance_checks
    
    async def _check_data_governance(self, registry: FederatedLearningRegistry) -> Dict[str, Any]:
        """Check data governance compliance"""
        governance_checks = {
            'compliance_framework': {
                'status': 'compliant' if registry.compliance_framework else 'non_compliant',
                'details': f"Framework: {registry.compliance_framework or 'Not specified'}",
                'score': 100.0 if registry.compliance_framework else 0.0
            },
            'risk_assessment': {
                'status': 'compliant' if registry.risk_level else 'non_compliant',
                'details': f"Risk Level: {registry.risk_level or 'Not assessed'}",
                'score': 100.0 if registry.risk_level else 0.0
            },
            'audit_schedule': {
                'status': 'compliant' if registry.next_audit_date else 'non_compliant',
                'details': f"Next Audit: {registry.next_audit_date or 'Not scheduled'}",
                'score': 100.0 if registry.next_audit_date else 0.0
            }
        }
        
        return governance_checks
    
    async def _check_audit_compliance(self, registry: FederatedLearningRegistry) -> Dict[str, Any]:
        """Check audit compliance requirements"""
        current_date = datetime.now()
        
        audit_checks = {
            'last_audit': {
                'status': 'compliant' if registry.last_audit_date else 'non_compliant',
                'details': f"Last Audit: {registry.last_audit_date or 'Never'}",
                'score': 100.0 if registry.last_audit_date else 0.0
            },
            'audit_frequency': {
                'status': 'unknown',
                'details': 'Audit frequency not specified',
                'score': 0.0
            }
        }
        
        # Check if audit is overdue
        if registry.last_audit_date and registry.next_audit_date:
            if current_date > registry.next_audit_date:
                audit_checks['audit_frequency'] = {
                    'status': 'non_compliant',
                    'details': f"Audit overdue since {registry.next_audit_date}",
                    'score': 0.0
                }
            else:
                days_until_audit = (registry.next_audit_date - current_date).days
                if days_until_audit <= 30:
                    audit_checks['audit_frequency'] = {
                        'status': 'warning',
                        'details': f"Audit due in {days_until_audit} days",
                        'score': 70.0
                    }
                else:
                    audit_checks['audit_frequency'] = {
                        'status': 'compliant',
                        'details': f"Audit due in {days_until_audit} days",
                        'score': 100.0
                    }
        
        return audit_checks
    
    async def _calculate_compliance_score(self, compliance_checks: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall compliance score"""
        try:
            total_score = 0.0
            total_weight = 0.0
            
            # Define weights for different compliance areas
            weights = {
                'security': 0.3,
                'privacy': 0.25,
                'performance': 0.2,
                'data_governance': 0.15,
                'audit': 0.1
            }
            
            for area, checks in compliance_checks.items():
                if area in weights:
                    area_score = 0.0
                    check_count = 0
                    
                    for check_name, check_details in checks.items():
                        if isinstance(check_details, dict) and 'score' in check_details:
                            area_score += check_details['score']
                            check_count += 1
                    
                    if check_count > 0:
                        area_avg_score = area_score / check_count
                        total_score += area_avg_score * weights[area]
                        total_weight += weights[area]
            
            if total_weight > 0:
                return round(total_score / total_weight, 2)
            else:
                return 0.0
                
        except Exception as e:
            print(f"⚠️  Failed to calculate compliance score: {e}")
            return 0.0
    
    def _determine_compliance_status(self, compliance_score: float) -> str:
        """Determine overall compliance status based on score"""
        if compliance_score >= 90.0:
            return 'excellent'
        elif compliance_score >= 80.0:
            return 'compliant'
        elif compliance_score >= 70.0:
            return 'mostly_compliant'
        elif compliance_score >= 60.0:
            return 'partially_compliant'
        else:
            return 'non_compliant'
    
    async def get_compliance_alerts(
        self,
        registry_id: str,
        severity: str = "all"
    ) -> List[Dict[str, Any]]:
        """Get compliance alerts for a federation (async)"""
        try:
            # Get compliance status
            compliance_status = await self.monitor_compliance_status(registry_id)
            if 'error' in compliance_status:
                return []
            
            alerts = []
            
            # Check for critical compliance issues
            for area, checks in compliance_status.get('compliance_checks', {}).items():
                for check_name, check_details in checks.items():
                    if check_details.get('status') == 'non_compliant':
                        alert = {
                            'registry_id': registry_id,
                            'alert_type': 'compliance_violation',
                            'severity': 'high',
                            'area': area,
                            'check': check_name,
                            'details': check_details.get('details', ''),
                            'timestamp': datetime.now().isoformat()
                        }
                        alerts.append(alert)
                    
                    elif check_details.get('status') == 'warning':
                        alert = {
                            'registry_id': registry_id,
                            'alert_type': 'compliance_warning',
                            'severity': 'medium',
                            'area': area,
                            'check': check_name,
                            'details': check_details.get('details', ''),
                            'timestamp': datetime.now().isoformat()
                        }
                        alerts.append(alert)
            
            # Filter by severity if specified
            if severity != "all":
                alerts = [alert for alert in alerts if alert['severity'] == severity]
            
            return alerts
            
        except Exception as e:
            print(f"❌ Failed to get compliance alerts: {e}")
            return []
    
    async def get_enterprise_compliance_summary(self) -> Dict[str, Any]:
        """Get enterprise-wide compliance summary (async)"""
        try:
            # Get all federations
            all_registries = await self.registry_repo.get_all(limit=1000)
            
            compliance_summary = {
                'total_federations': len(all_registries),
                'compliance_statuses': {
                    'excellent': 0,
                    'compliant': 0,
                    'mostly_compliant': 0,
                    'partially_compliant': 0,
                    'non_compliant': 0
                },
                'framework_distribution': {},
                'risk_level_distribution': {},
                'avg_compliance_score': 0.0
            }
            
            total_score = 0.0
            valid_scores = 0
            
            for registry in all_registries:
                # Get compliance status for each federation
                compliance_status = await self.monitor_compliance_status(registry.registry_id)
                
                if 'error' not in compliance_status:
                    status = compliance_status.get('overall_status', 'unknown')
                    if status in compliance_summary['compliance_statuses']:
                        compliance_summary['compliance_statuses'][status] += 1
                    
                    score = compliance_status.get('compliance_score', 0.0)
                    if score > 0:
                        total_score += score
                        valid_scores += 1
                    
                    # Track framework distribution
                    framework = registry.compliance_framework
                    if framework:
                        if framework not in compliance_summary['framework_distribution']:
                            compliance_summary['framework_distribution'][framework] = 0
                        compliance_summary['framework_distribution'][framework] += 1
                    
                    # Track risk level distribution
                    risk_level = registry.risk_level
                    if risk_level:
                        if risk_level not in compliance_summary['risk_level_distribution']:
                            compliance_summary['risk_level_distribution'][risk_level] = 0
                        compliance_summary['risk_level_distribution'][risk_level] += 1
            
            # Calculate average compliance score
            if valid_scores > 0:
                compliance_summary['avg_compliance_score'] = round(total_score / valid_scores, 2)
            
            compliance_summary['summary_date'] = datetime.now().isoformat()
            
            return compliance_summary
            
        except Exception as e:
            print(f"❌ Failed to get enterprise compliance summary: {e}")
            return {'error': str(e)}
    
    async def schedule_compliance_audit(
        self,
        registry_id: str,
        audit_date: datetime,
        auditor: str,
        audit_scope: str
    ) -> bool:
        """Schedule a compliance audit (async)"""
        try:
            # Update registry with audit information
            update_data = {
                'next_audit_date': audit_date,
                'audit_details': {
                    'auditor': auditor,
                    'scope': audit_scope,
                    'scheduled_date': audit_date.isoformat(),
                    'status': 'scheduled'
                }
            }
            
            success = await self.registry_repo.update(registry_id, update_data)
            if not success:
                raise Exception("Failed to schedule compliance audit")
            
            print(f"✅ Compliance audit scheduled for {registry_id} on {audit_date}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to schedule compliance audit: {e}")
            return False
    
    async def record_audit_result(
        self,
        registry_id: str,
        audit_date: datetime,
        audit_result: str,
        findings: List[str],
        recommendations: List[str],
        auditor: str
    ) -> bool:
        """Record audit results (async)"""
        try:
            # Update registry with audit results
            update_data = {
                'last_audit_date': audit_date,
                'compliance_status': audit_result,
                'audit_details': {
                    'auditor': auditor,
                    'audit_date': audit_date.isoformat(),
                    'result': audit_result,
                    'findings': findings,
                    'recommendations': recommendations,
                    'status': 'completed'
                }
            }
            
            success = await self.registry_repo.update(registry_id, update_data)
            if not success:
                raise Exception("Failed to record audit results")
            
            print(f"✅ Audit results recorded for {registry_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to record audit results: {e}")
            return False
