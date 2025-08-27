"""
Compliance Utilities
===================

Regulatory compliance and auditing utility functions for federated learning.
Handles compliance checking, audit trails, and regulatory reporting.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class ComplianceConfig:
    """Configuration for compliance utilities"""
    # Compliance frameworks
    gdpr_compliance_enabled: bool = True
    ccpa_compliance_enabled: bool = True
    hipaa_compliance_enabled: bool = True
    sox_compliance_enabled: bool = True
    
    # Audit settings
    audit_logging_enabled: bool = True
    audit_retention_days: int = 2555  # 7 years
    audit_encryption_enabled: bool = True
    
    # Compliance thresholds
    min_compliance_score: float = 0.8
    max_violation_count: int = 5
    compliance_check_interval: int = 3600  # seconds
    
    # Reporting settings
    auto_reporting_enabled: bool = True
    report_frequency: str = "monthly"  # daily, weekly, monthly, quarterly
    report_encryption_enabled: bool = True


@dataclass
class ComplianceMetrics:
    """Metrics for compliance operations"""
    # Compliance scores
    overall_compliance_score: float = 0.0
    gdpr_compliance_score: float = 0.0
    ccpa_compliance_score: float = 0.0
    hipaa_compliance_score: float = 0.0
    sox_compliance_score: float = 0.0
    
    # Violation tracking
    total_violations: int = 0
    critical_violations: int = 0
    warning_violations: int = 0
    last_violation_date: Optional[datetime] = None
    
    # Audit metrics
    audit_entries_count: int = 0
    audit_encryption_enabled: bool = True
    audit_retention_compliance: bool = True
    
    # Reporting metrics
    reports_generated: int = 0
    last_report_date: Optional[datetime] = None
    next_report_date: Optional[datetime] = None


class ComplianceUtils:
    """Compliance utility functions for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[ComplianceConfig] = None
    ):
        """Initialize Compliance Utils"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or ComplianceConfig()
        
        # Compliance state
        self.compliance_active = False
        self.audit_trail: List[Dict[str, Any]] = []
        self.violation_history: List[Dict[str, Any]] = []
        
        # Metrics tracking
        self.metrics = ComplianceMetrics()
        
        # Compliance state
        self.compliance_check_task = None
        self.last_compliance_check = None
        
    async def start_compliance_monitoring(self) -> Dict[str, Any]:
        """Start compliance monitoring and checking"""
        try:
            if self.compliance_active:
                return {'status': 'already_active', 'message': 'Compliance monitoring already active'}
            
            print("📋 Starting compliance monitoring...")
            
            # Initialize compliance monitoring
            await self._initialize_compliance_monitoring()
            
            # Start compliance checking task
            self.compliance_check_task = asyncio.create_task(self._compliance_checking_loop())
            self.compliance_active = True
            
            # Perform initial compliance check
            await self._perform_compliance_check()
            
            return {
                'status': 'success',
                'message': 'Compliance monitoring started',
                'config': self.config.__dict__
            }
            
        except Exception as e:
            print(f"❌ Compliance monitoring start failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _initialize_compliance_monitoring(self):
        """Initialize compliance monitoring"""
        try:
            # Reset metrics
            self.metrics = ComplianceMetrics()
            
            # Clear audit trail and violations
            self.audit_trail.clear()
            self.violation_history.clear()
            
            # Set next report date
            self._calculate_next_report_date()
            
            print("🔧 Compliance monitoring initialized")
            
        except Exception as e:
            print(f"❌ Compliance monitoring initialization failed: {e}")
            raise
    
    async def _compliance_checking_loop(self):
        """Continuous compliance checking loop"""
        try:
            while self.compliance_active:
                # Wait for next compliance check
                await asyncio.sleep(self.config.compliance_check_interval)
                
                # Perform compliance check
                await self._perform_compliance_check()
                
        except Exception as e:
            print(f"❌ Compliance checking loop failed: {e}")
    
    async def _perform_compliance_check(self) -> Dict[str, Any]:
        """Perform comprehensive compliance check"""
        try:
            print("🔍 Performing compliance check...")
            
            compliance_results = {
                'timestamp': datetime.now().isoformat(),
                'overall_score': 0.0,
                'framework_results': {},
                'violations': [],
                'recommendations': []
            }
            
            # GDPR compliance check
            if self.config.gdpr_compliance_enabled:
                gdpr_results = await self._check_gdpr_compliance()
                compliance_results['framework_results']['gdpr'] = gdpr_results
                self.metrics.gdpr_compliance_score = gdpr_results['score']
            
            # CCPA compliance check
            if self.config.ccpa_compliance_enabled:
                ccpa_results = await self._check_ccpa_compliance()
                compliance_results['framework_results']['ccpa'] = ccpa_results
                self.metrics.ccpa_compliance_score = ccpa_results['score']
            
            # HIPAA compliance check
            if self.config.hipaa_compliance_enabled:
                hipaa_results = await self._check_hipaa_compliance()
                compliance_results['framework_results']['hipaa'] = hipaa_results
                self.metrics.hipaa_compliance_score = hipaa_results['score']
            
            # SOX compliance check
            if self.config.sox_compliance_enabled:
                sox_results = await self._check_sox_compliance()
                compliance_results['framework_results']['sox'] = sox_results
                self.metrics.sox_compliance_score = sox_results['score']
            
            # Calculate overall compliance score
            framework_scores = [
                self.metrics.gdpr_compliance_score,
                self.metrics.ccpa_compliance_score,
                self.metrics.hipaa_compliance_score,
                self.metrics.sox_compliance_score
            ]
            overall_score = np.mean([score for score in framework_scores if score > 0])
            
            compliance_results['overall_score'] = overall_score
            self.metrics.overall_compliance_score = overall_score
            
            # Check for violations
            violations = await self._identify_compliance_violations(compliance_results)
            compliance_results['violations'] = violations
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(compliance_results)
            compliance_results['recommendations'] = recommendations
            
            # Update metrics
            await self._update_compliance_metrics(compliance_results)
            
            # Log compliance check
            await self._log_compliance_check(compliance_results)
            
            # Update last check time
            self.last_compliance_check = datetime.now()
            
            print(f"✅ Compliance check completed: {overall_score:.2%} overall score")
            
            return compliance_results
            
        except Exception as e:
            print(f"❌ Compliance check failed: {e}")
            return {'error': str(e)}
    
    async def _check_gdpr_compliance(self) -> Dict[str, Any]:
        """Check GDPR compliance"""
        try:
            gdpr_results = {
                'score': 0.0,
                'requirements': {},
                'status': 'unknown'
            }
            
            # GDPR requirements checklist
            requirements = {
                'data_minimization': True,
                'purpose_limitation': True,
                'storage_limitation': True,
                'accuracy': True,
                'integrity_confidentiality': True,
                'accountability': True,
                'lawful_basis': True,
                'consent_management': True,
                'data_subject_rights': True,
                'data_breach_notification': True
            }
            
            # Simulate compliance checking
            # In practice, this would check actual system configurations and data handling
            for requirement, status in requirements.items():
                # Simulate some non-compliance
                if requirement in ['consent_management', 'data_breach_notification']:
                    requirements[requirement] = np.random.choice([True, False], p=[0.8, 0.2])
                else:
                    requirements[requirement] = np.random.choice([True, False], p=[0.9, 0.1])
            
            # Calculate compliance score
            passed_requirements = sum(requirements.values())
            total_requirements = len(requirements)
            compliance_score = passed_requirements / total_requirements
            
            gdpr_results['score'] = compliance_score
            gdpr_results['requirements'] = requirements
            gdpr_results['status'] = 'compliant' if compliance_score >= self.config.min_compliance_score else 'non_compliant'
            
            return gdpr_results
            
        except Exception as e:
            print(f"❌ GDPR compliance check failed: {e}")
            return {'score': 0.0, 'requirements': {}, 'status': 'error'}
    
    async def _check_ccpa_compliance(self) -> Dict[str, Any]:
        """Check CCPA compliance"""
        try:
            ccpa_results = {
                'score': 0.0,
                'requirements': {},
                'status': 'unknown'
            }
            
            # CCPA requirements checklist
            requirements = {
                'notice_at_collection': True,
                'privacy_policy': True,
                'opt_out_rights': True,
                'data_disclosure': True,
                'data_portability': True,
                'deletion_rights': True,
                'non_discrimination': True,
                'service_provider_agreements': True
            }
            
            # Simulate compliance checking
            for requirement, status in requirements.items():
                # Simulate some non-compliance
                if requirement in ['opt_out_rights', 'deletion_rights']:
                    requirements[requirement] = np.random.choice([True, False], p=[0.7, 0.3])
                else:
                    requirements[requirement] = np.random.choice([True, False], p=[0.85, 0.15])
            
            # Calculate compliance score
            passed_requirements = sum(requirements.values())
            total_requirements = len(requirements)
            compliance_score = passed_requirements / total_requirements
            
            ccpa_results['score'] = compliance_score
            ccpa_results['requirements'] = requirements
            ccpa_results['status'] = 'compliant' if compliance_score >= self.config.min_compliance_score else 'non_compliant'
            
            return ccpa_results
            
        except Exception as e:
            print(f"❌ CCPA compliance check failed: {e}")
            return {'score': 0.0, 'requirements': {}, 'status': 'error'}
    
    async def _check_hipaa_compliance(self) -> Dict[str, Any]:
        """Check HIPAA compliance"""
        try:
            hipaa_results = {
                'score': 0.0,
                'requirements': {},
                'status': 'unknown'
            }
            
            # HIPAA requirements checklist
            requirements = {
                'privacy_rule': True,
                'security_rule': True,
                'breach_notification': True,
                'administrative_safeguards': True,
                'physical_safeguards': True,
                'technical_safeguards': True,
                'business_associate_agreements': True,
                'training_programs': True
            }
            
            # Simulate compliance checking
            for requirement, status in requirements.items():
                # Simulate some non-compliance
                if requirement in ['security_rule', 'technical_safeguards']:
                    requirements[requirement] = np.random.choice([True, False], p=[0.75, 0.25])
                else:
                    requirements[requirement] = np.random.choice([True, False], p=[0.9, 0.1])
            
            # Calculate compliance score
            passed_requirements = sum(requirements.values())
            total_requirements = len(requirements)
            compliance_score = passed_requirements / total_requirements
            
            hipaa_results['score'] = compliance_score
            hipaa_results['requirements'] = requirements
            hipaa_results['status'] = 'compliant' if compliance_score >= self.config.min_compliance_score else 'non_compliant'
            
            return hipaa_results
            
        except Exception as e:
            print(f"❌ HIPAA compliance check failed: {e}")
            return {'score': 0.0, 'requirements': {}, 'status': 'error'}
    
    async def _check_sox_compliance(self) -> Dict[str, Any]:
        """Check SOX compliance"""
        try:
            sox_results = {
                'score': 0.0,
                'requirements': {},
                'status': 'unknown'
            }
            
            # SOX requirements checklist
            requirements = {
                'internal_controls': True,
                'financial_reporting': True,
                'audit_committee': True,
                'whistleblower_protection': True,
                'executive_certification': True,
                'disclosure_controls': True,
                'code_of_ethics': True,
                'risk_assessment': True
            }
            
            # Simulate compliance checking
            for requirement, status in requirements.items():
                # Simulate some non-compliance
                if requirement in ['internal_controls', 'risk_assessment']:
                    requirements[requirement] = np.random.choice([True, False], p=[0.8, 0.2])
                else:
                    requirements[requirement] = np.random.choice([True, False], p=[0.9, 0.1])
            
            # Calculate compliance score
            passed_requirements = sum(requirements.values())
            total_requirements = len(requirements)
            compliance_score = passed_requirements / total_requirements
            
            sox_results['score'] = compliance_score
            sox_results['requirements'] = requirements
            sox_results['status'] = 'compliant' if compliance_score >= self.config.min_compliance_score else 'non_compliant'
            
            return sox_results
            
        except Exception as e:
            print(f"❌ SOX compliance check failed: {e}")
            return {'score': 0.0, 'requirements': {}, 'status': 'error'}
    
    async def _identify_compliance_violations(self, compliance_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify compliance violations"""
        try:
            violations = []
            
            for framework, results in compliance_results['framework_results'].items():
                if results['status'] == 'non_compliant':
                    # Identify specific violations
                    failed_requirements = [
                        req for req, status in results['requirements'].items()
                        if not status
                    ]
                    
                    for requirement in failed_requirements:
                        violation = {
                            'framework': framework.upper(),
                            'requirement': requirement,
                            'severity': 'critical' if framework in ['hipaa', 'gdpr'] else 'warning',
                            'description': f"Failed to meet {framework.upper()} requirement: {requirement}",
                            'timestamp': datetime.now().isoformat(),
                            'compliance_score': results['score']
                        }
                        violations.append(violation)
            
            # Update violation metrics
            self.metrics.total_violations = len(violations)
            self.metrics.critical_violations = len([v for v in violations if v['severity'] == 'critical'])
            self.metrics.warning_violations = len([v for v in violations if v['severity'] == 'warning'])
            
            if violations:
                self.metrics.last_violation_date = datetime.now()
            
            return violations
            
        except Exception as e:
            print(f"❌ Violation identification failed: {e}")
            return []
    
    async def _generate_compliance_recommendations(self, compliance_results: Dict[str, Any]) -> List[str]:
        """Generate compliance improvement recommendations"""
        try:
            recommendations = []
            
            # Overall compliance recommendations
            if compliance_results['overall_score'] < self.config.min_compliance_score:
                recommendations.append("Overall compliance score is below threshold. Review all framework requirements.")
            
            # Framework-specific recommendations
            for framework, results in compliance_results['framework_results'].items():
                if results['status'] == 'non_compliant':
                    failed_count = sum(1 for req, status in results['requirements'].items() if not status)
                    recommendations.append(f"Address {failed_count} failed {framework.upper()} requirements to achieve compliance.")
            
            # Specific recommendations based on violations
            if compliance_results['violations']:
                critical_violations = [v for v in compliance_results['violations'] if v['severity'] == 'critical']
                if critical_violations:
                    recommendations.append("Prioritize resolution of critical compliance violations.")
                
                recommendations.append("Implement regular compliance training and monitoring programs.")
                recommendations.append("Establish clear compliance policies and procedures.")
                recommendations.append("Conduct regular compliance audits and assessments.")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Recommendation generation failed: {e}")
            return ["Unable to generate recommendations due to error"]
    
    async def _update_compliance_metrics(self, compliance_results: Dict[str, Any]):
        """Update compliance metrics based on results"""
        try:
            # Update violation counts
            self.metrics.total_violations = len(compliance_results.get('violations', []))
            
            # Check if violations exceed threshold
            if self.metrics.total_violations > self.config.max_violation_count:
                print(f"⚠️  Violation count {self.metrics.total_violations} exceeds threshold {self.config.max_violation_count}")
            
        except Exception as e:
            print(f"⚠️  Metrics update failed: {e}")
    
    async def _log_compliance_check(self, compliance_results: Dict[str, Any]):
        """Log compliance check results"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'compliance_score': compliance_results['overall_score'],
                'violations_count': len(compliance_results['violations']),
                'frameworks_checked': list(compliance_results['framework_results'].keys()),
                'status': 'compliant' if compliance_results['overall_score'] >= self.config.min_compliance_score else 'non_compliant'
            }
            
            self.audit_trail.append(log_entry)
            self.metrics.audit_entries_count += 1
            
        except Exception as e:
            print(f"⚠️  Compliance check logging failed: {e}")
    
    def _calculate_next_report_date(self):
        """Calculate next compliance report date"""
        try:
            current_date = datetime.now()
            
            if self.config.report_frequency == "daily":
                next_date = current_date + timedelta(days=1)
            elif self.config.report_frequency == "weekly":
                next_date = current_date + timedelta(weeks=1)
            elif self.config.report_frequency == "monthly":
                next_date = current_date + timedelta(days=30)
            elif self.config.report_frequency == "quarterly":
                next_date = current_date + timedelta(days=90)
            else:
                next_date = current_date + timedelta(days=30)  # Default to monthly
            
            self.metrics.next_report_date = next_date
            
        except Exception as e:
            print(f"⚠️  Next report date calculation failed: {e}")
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            print("📊 Generating compliance report...")
            
            report = {
                'report_id': f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.now().isoformat(),
                'report_period': self.config.report_frequency,
                'compliance_summary': {
                    'overall_score': self.metrics.overall_compliance_score,
                    'status': 'compliant' if self.metrics.overall_compliance_score >= self.config.min_compliance_score else 'non_compliant',
                    'frameworks': {
                        'GDPR': self.metrics.gdpr_compliance_score,
                        'CCPA': self.metrics.ccpa_compliance_score,
                        'HIPAA': self.metrics.hipaa_compliance_score,
                        'SOX': self.metrics.sox_compliance_score
                    }
                },
                'violations_summary': {
                    'total_violations': self.metrics.total_violations,
                    'critical_violations': self.metrics.critical_violations,
                    'warning_violations': self.metrics.warning_violations,
                    'last_violation': self.metrics.last_violation_date.isoformat() if self.metrics.last_violation_date else None
                },
                'audit_summary': {
                    'total_audit_entries': self.metrics.audit_entries_count,
                    'audit_encryption_enabled': self.metrics.audit_encryption_enabled,
                    'retention_compliance': self.metrics.audit_retention_compliance
                },
                'recommendations': [
                    "Maintain regular compliance monitoring",
                    "Address identified violations promptly",
                    "Implement continuous improvement processes",
                    "Provide regular compliance training"
                ]
            }
            
            # Update report metrics
            self.metrics.reports_generated += 1
            self.metrics.last_report_date = datetime.now()
            self._calculate_next_report_date()
            
            print("✅ Compliance report generated successfully")
            
            return report
            
        except Exception as e:
            print(f"❌ Compliance report generation failed: {e}")
            return {'error': str(e)}
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """Get comprehensive compliance report"""
        try:
            return {
                'compliance_metrics': self.metrics.__dict__,
                'audit_trail': self.audit_trail,
                'violation_history': self.violation_history,
                'current_config': self.config.__dict__,
                'compliance_status': {
                    'active': self.compliance_active,
                    'last_check': self.last_compliance_check.isoformat() if self.last_compliance_check else None
                }
            }
            
        except Exception as e:
            print(f"❌ Compliance report generation failed: {e}")
            return {'error': str(e)}
    
    async def stop_compliance_monitoring(self):
        """Stop compliance monitoring"""
        try:
            self.compliance_active = False
            
            # Cancel compliance checking task
            if self.compliance_check_task:
                self.compliance_check_task.cancel()
                self.compliance_check_task = None
            
            print("🛑 Compliance monitoring stopped")
            
        except Exception as e:
            print(f"❌ Compliance monitoring stop failed: {e}")
    
    async def reset_metrics(self):
        """Reset compliance metrics"""
        try:
            self.metrics = ComplianceMetrics()
            self.audit_trail.clear()
            self.violation_history.clear()
            print("🔄 Compliance metrics reset")
            
        except Exception as e:
            print(f"❌ Metrics reset failed: {e}")


