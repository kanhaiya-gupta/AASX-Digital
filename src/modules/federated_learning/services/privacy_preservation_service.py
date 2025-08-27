"""
Privacy Preservation Service
============================

Service for managing privacy and security in federated learning.
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


class PrivacyPreservationService:
    """Service for privacy and security management in federated learning"""
    
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
    
    async def assess_privacy_risk(
        self,
        registry_id: str,
        data_sensitivity_level: str = "medium"
    ) -> Dict[str, Any]:
        """Assess privacy risk for a federation (async)"""
        try:
            # Get federation details
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return {'error': 'Federation not found'}
            
            # Calculate risk score based on various factors
            risk_factors = {
                'data_sensitivity': self._get_sensitivity_score(data_sensitivity_level),
                'encryption_strength': self._get_encryption_score(registry.encryption_strength),
                'access_control': self._get_access_control_score(registry.access_control_level),
                'compliance_framework': self._get_compliance_score(registry.compliance_framework),
                'security_score': registry.security_score or 0.0
            }
            
            # Calculate weighted risk score
            weights = {
                'data_sensitivity': 0.3,
                'encryption_strength': 0.25,
                'access_control': 0.2,
                'compliance_framework': 0.15,
                'security_score': 0.1
            }
            
            total_risk_score = sum(
                risk_factors[factor] * weights[factor] 
                for factor in risk_factors
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(total_risk_score)
            
            # Generate recommendations
            recommendations = await self._generate_privacy_recommendations(
                risk_factors, total_risk_score, risk_level
            )
            
            return {
                'registry_id': registry_id,
                'risk_assessment': {
                    'total_score': round(total_risk_score, 2),
                    'risk_level': risk_level,
                    'risk_factors': risk_factors
                },
                'recommendations': recommendations,
                'assessment_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to assess privacy risk: {e}")
            return {'error': str(e)}
    
    def _get_sensitivity_score(self, sensitivity_level: str) -> float:
        """Get sensitivity score based on data level"""
        sensitivity_scores = {
            'low': 20.0,
            'medium': 50.0,
            'high': 80.0,
            'critical': 100.0
        }
        return sensitivity_scores.get(sensitivity_level.lower(), 50.0)
    
    def _get_encryption_score(self, encryption_strength: Optional[str]) -> float:
        """Get encryption strength score"""
        if not encryption_strength:
            return 0.0
        
        encryption_scores = {
            'weak': 20.0,
            'basic': 40.0,
            'strong': 70.0,
            'military': 100.0
        }
        return encryption_scores.get(encryption_strength.lower(), 40.0)
    
    def _get_access_control_score(self, access_level: str) -> float:
        """Get access control score"""
        access_scores = {
            'basic': 30.0,
            'standard': 60.0,
            'advanced': 85.0,
            'enterprise': 100.0
        }
        return access_scores.get(access_level.lower(), 30.0)
    
    def _get_compliance_score(self, framework: Optional[str]) -> float:
        """Get compliance framework score"""
        if not framework:
            return 0.0
        
        compliance_scores = {
            'gdpr': 90.0,
            'hipaa': 85.0,
            'sox': 80.0,
            'iso27001': 95.0,
            'nist': 88.0
        }
        return compliance_scores.get(framework.lower(), 70.0)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score"""
        if risk_score <= 30.0:
            return 'low'
        elif risk_score <= 60.0:
            return 'medium'
        elif risk_score <= 80.0:
            return 'high'
        else:
            return 'critical'
    
    async def _generate_privacy_recommendations(
        self,
        risk_factors: Dict[str, float],
        total_score: float,
        risk_level: str
    ) -> List[str]:
        """Generate privacy recommendations based on risk assessment"""
        recommendations = []
        
        # Data sensitivity recommendations
        if risk_factors['data_sensitivity'] > 70.0:
            recommendations.append("Implement data anonymization techniques")
            recommendations.append("Use differential privacy for sensitive data")
        
        # Encryption recommendations
        if risk_factors['encryption_strength'] < 70.0:
            recommendations.append("Upgrade to stronger encryption (AES-256 or higher)")
            recommendations.append("Implement end-to-end encryption for data transmission")
        
        # Access control recommendations
        if risk_factors['access_control'] < 70.0:
            recommendations.append("Implement multi-factor authentication")
            recommendations.append("Use role-based access control (RBAC)")
            recommendations.append("Implement least privilege principle")
        
        # Compliance recommendations
        if risk_factors['compliance_framework'] < 70.0:
            recommendations.append("Adopt industry-standard compliance framework")
            recommendations.append("Implement regular compliance audits")
            recommendations.append("Establish data governance policies")
        
        # General recommendations based on risk level
        if risk_level in ['high', 'critical']:
            recommendations.append("Conduct regular security assessments")
            recommendations.append("Implement continuous monitoring and alerting")
            recommendations.append("Establish incident response procedures")
        
        return recommendations
    
    async def update_privacy_settings(
        self,
        registry_id: str,
        privacy_updates: Dict[str, Any]
    ) -> bool:
        """Update privacy and security settings (async)"""
        try:
            # Validate updates
            allowed_updates = {
                'encryption_enabled', 'encryption_strength', 'security_level',
                'access_control_level', 'compliance_framework', 'risk_level'
            }
            
            filtered_updates = {
                k: v for k, v in privacy_updates.items() 
                if k in allowed_updates
            }
            
            if not filtered_updates:
                raise Exception("No valid privacy updates provided")
            
            # Update registry
            success = await self.registry_repo.update(registry_id, filtered_updates)
            if not success:
                raise Exception("Failed to update privacy settings")
            
            # Update security score if encryption or access control changed
            if any(key in filtered_updates for key in ['encryption_strength', 'access_control_level']):
                await self._recalculate_security_score(registry_id)
            
            print(f"✅ Privacy settings updated for federation {registry_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update privacy settings: {e}")
            return False
    
    async def _recalculate_security_score(self, registry_id: str) -> None:
        """Recalculate security score based on current settings"""
        try:
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return
            
            # Calculate new security score
            encryption_score = self._get_encryption_score(registry.encryption_strength)
            access_score = self._get_access_control_score(registry.access_control_level)
            compliance_score = self._get_compliance_score(registry.compliance_framework)
            
            # Weighted average
            new_security_score = (
                encryption_score * 0.4 +
                access_score * 0.35 +
                compliance_score * 0.25
            )
            
            # Update security score
            await self.registry_repo.update(registry_id, {
                'security_score': new_security_score,
                'last_security_scan': datetime.now()
            })
            
        except Exception as e:
            print(f"⚠️  Failed to recalculate security score: {e}")
    
    async def get_privacy_compliance_report(
        self,
        registry_id: str
    ) -> Dict[str, Any]:
        """Generate privacy compliance report (async)"""
        try:
            # Get federation details
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return {'error': 'Federation not found'}
            
            # Get latest metrics
            metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            
            # Assess current privacy risk
            risk_assessment = await self.assess_privacy_risk(registry_id)
            
            # Check compliance status
            compliance_status = await self._check_compliance_status(registry)
            
            # Generate report
            report = {
                'registry_id': registry_id,
                'federation_name': registry.federation_name,
                'report_date': datetime.now().isoformat(),
                'privacy_status': {
                    'encryption_enabled': registry.encryption_enabled,
                    'encryption_strength': registry.encryption_strength,
                    'security_level': registry.security_level,
                    'access_control_level': registry.access_control_level
                },
                'compliance_status': compliance_status,
                'risk_assessment': risk_assessment.get('risk_assessment', {}),
                'recommendations': risk_assessment.get('recommendations', []),
                'metrics': {
                    'privacy_preservation_score': metrics.privacy_preservation_score if metrics else None,
                    'data_protection_score': registry.data_protection_score,
                    'incident_response_time': registry.incident_response_time
                }
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Failed to generate privacy compliance report: {e}")
            return {'error': str(e)}
    
    async def _check_compliance_status(self, registry: FederatedLearningRegistry) -> Dict[str, Any]:
        """Check compliance status for a federation"""
        compliance_status = {
            'overall_status': 'unknown',
            'framework': registry.compliance_framework,
            'status': registry.compliance_status,
            'last_audit': registry.last_audit_date.isoformat() if registry.last_audit_date else None,
            'next_audit': registry.next_audit_date.isoformat() if registry.next_audit_date else None,
            'details': {}
        }
        
        # Check security compliance
        if registry.security_score is not None:
            if registry.security_score >= 80.0:
                compliance_status['details']['security'] = 'compliant'
            else:
                compliance_status['details']['security'] = 'non_compliant'
        
        # Check encryption compliance
        if registry.encryption_enabled:
            compliance_status['details']['encryption'] = 'enabled'
        else:
            compliance_status['details']['encryption'] = 'disabled'
        
        # Determine overall status
        if registry.compliance_status:
            compliance_status['overall_status'] = registry.compliance_status
        else:
            # Auto-determine based on factors
            if (registry.encryption_enabled and 
                registry.security_score and 
                registry.security_score >= 70.0):
                compliance_status['overall_status'] = 'compliant'
            else:
                compliance_status['overall_status'] = 'non_compliant'
        
        return compliance_status
    
    async def monitor_privacy_events(
        self,
        registry_id: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Monitor privacy-related events (async)"""
        try:
            # Get metrics within time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            metrics_list = await self.metrics_repo.get_by_time_range(
                registry_id, start_time, end_time
            )
            
            privacy_events = []
            for metrics in metrics_list:
                # Check for privacy-related anomalies
                if metrics.error_rate > 5.0:
                    privacy_events.append({
                        'timestamp': metrics.created_at.isoformat(),
                        'event_type': 'high_error_rate',
                        'severity': 'warning',
                        'description': f"High error rate detected: {metrics.error_rate}%"
                    })
                
                if metrics.health_score < 70.0:
                    privacy_events.append({
                        'timestamp': metrics.created_at.isoformat(),
                        'event_type': 'low_health_score',
                        'severity': 'medium',
                        'description': f"Low health score: {metrics.health_score}"
                    })
            
            return privacy_events
            
        except Exception as e:
            print(f"❌ Failed to monitor privacy events: {e}")
            return []
    
    async def get_privacy_metrics_summary(self) -> Dict[str, Any]:
        """Get privacy metrics summary across all federations"""
        try:
            # Get enterprise metrics summary
            enterprise_summary = await self.metrics_repo.get_enterprise_metrics_summary()
            
            # Get compliance summary
            compliance_summary = await self.registry_repo.get_compliance_summary()
            
            return {
                'privacy_preservation': {
                    'avg_score': enterprise_summary.get('avg_privacy_preservation', 0.0),
                    'total_federations': enterprise_summary.get('total_metrics', 0)
                },
                'compliance': {
                    'compliant_count': compliance_summary.get('compliant_count', 0),
                    'non_compliant_count': compliance_summary.get('non_compliant_count', 0),
                    'pending_count': compliance_summary.get('pending_count', 0)
                },
                'security': {
                    'avg_security_score': compliance_summary.get('avg_security_score', 0.0)
                }
            }
            
        except Exception as e:
            print(f"❌ Failed to get privacy metrics summary: {e}")
            return {}


