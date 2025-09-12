"""
Federated Learning Repositories
===============================

Enterprise-grade repositories for federated learning operations.
Provides data access layer for all federated learning tables.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from ..database.connection_manager import ConnectionManager
from ..models.federated_learning import (
    FederatedLearningRegistry,
    FederatedLearningMetrics,
    EnterpriseFederatedLearningMetrics,
    EnterpriseFederatedLearningComplianceTracking,
    EnterpriseFederatedLearningSecurityMetrics,
    EnterpriseFederatedLearningPerformanceAnalytics
)

logger = logging.getLogger(__name__)


class FederatedLearningRegistryRepository:
    """Repository for federated learning registry operations."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table_name = "federated_learning_registry"
    
    async def create(self, registry: FederatedLearningRegistry) -> bool:
        """Create a new federated learning registry entry."""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    registry_id, federation_name, registry_name, federation_type, federation_category,
                    integration_status, overall_health_score, health_status, lifecycle_status,
                    federation_participation_status, model_aggregation_status, privacy_compliance_status,
                    algorithm_execution_status, performance_score, data_quality_score, reliability_score,
                    compliance_score, security_level, access_control_level, encryption_enabled,
                    user_id, org_id, dept_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                registry.registry_id, registry.federation_name, registry.registry_name,
                registry.federation_type, registry.federation_category, registry.integration_status,
                registry.overall_health_score, registry.health_status, registry.lifecycle_status,
                registry.federation_participation_status, registry.model_aggregation_status,
                registry.privacy_compliance_status, registry.algorithm_execution_status,
                registry.performance_score, registry.data_quality_score, registry.reliability_score,
                registry.compliance_score, registry.security_level, registry.access_control_level,
                registry.encryption_enabled, registry.user_id, registry.org_id, registry.dept_id,
                registry.created_at, registry.updated_at
            )
            
            return await self.connection_manager.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"Error creating federated learning registry: {e}")
            return False
    
    async def get_by_id(self, registry_id: str) -> Optional[Dict[str, Any]]:
        """Get federated learning registry by ID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ?"
            return await self.connection_manager.fetch_one(query, (registry_id,))
        except Exception as e:
            logger.error(f"Error getting federated learning registry: {e}")
            return None
    
    async def update(self, registry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update federated learning registry."""
        try:
            set_clauses = ", ".join([f"{key} = ?" for key in update_data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clauses}, updated_at = ? WHERE registry_id = ?"
            
            values = list(update_data.values()) + [datetime.now().isoformat(), registry_id]
            return await self.connection_manager.execute_query(query, tuple(values))
            
        except Exception as e:
            logger.error(f"Error updating federated learning registry: {e}")
            return False
    
    async def delete(self, registry_id: str) -> bool:
        """Delete federated learning registry."""
        try:
            query = f"DELETE FROM {self.table_name} WHERE registry_id = ?"
            return await self.connection_manager.execute_query(query, (registry_id,))
        except Exception as e:
            logger.error(f"Error deleting federated learning registry: {e}")
            return False
    
    async def get_active_federations(self) -> List[Dict[str, Any]]:
        """Get all active federated learning sessions."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE lifecycle_status = 'active'"
            return await self.connection_manager.fetch_all(query)
        except Exception as e:
            logger.error(f"Error getting active federations: {e}")
            return []


class FederatedLearningMetricsRepository:
    """Repository for federated learning metrics operations."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table_name = "federated_learning_metrics"
    
    async def create(self, metrics: FederatedLearningMetrics) -> bool:
        """Create new federated learning metrics."""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    registry_id, health_score, response_time_ms, uptime_percentage, error_rate,
                    federation_participation_speed_sec, model_aggregation_speed_sec, privacy_compliance_speed_sec,
                    cpu_usage_percent, memory_usage_percent, gpu_usage_percent, network_throughput_mbps, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                metrics.registry_id, metrics.health_score, metrics.response_time_ms,
                metrics.uptime_percentage, metrics.error_rate, metrics.federation_participation_speed_sec,
                metrics.model_aggregation_speed_sec, metrics.privacy_compliance_speed_sec,
                metrics.cpu_usage_percent, metrics.memory_usage_percent, metrics.gpu_usage_percent,
                metrics.network_throughput_mbps, metrics.created_at
            )
            
            return await self.connection_manager.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"Error creating federated learning metrics: {e}")
            return False
    
    async def get_by_registry_id(self, registry_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics by registry ID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ?"
            return await self.connection_manager.fetch_one(query, (registry_id,))
        except Exception as e:
            logger.error(f"Error getting federated learning metrics: {e}")
            return None
    
    async def update_metrics(self, registry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update federated learning metrics."""
        try:
            set_clauses = ", ".join([f"{key} = ?" for key in update_data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clauses} WHERE registry_id = ?"
            
            values = list(update_data.values()) + [registry_id]
            return await self.connection_manager.execute_query(query, tuple(values))
            
        except Exception as e:
            logger.error(f"Error updating federated learning metrics: {e}")
            return False


class EnterpriseFederatedLearningRepository:
    """Repository for enterprise federated learning operations."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.metrics_repo = EnterpriseFederatedLearningMetricsRepository(connection_manager)
        self.compliance_repo = EnterpriseFederatedLearningComplianceTrackingRepository(connection_manager)
        self.security_repo = EnterpriseFederatedLearningSecurityMetricsRepository(connection_manager)
        self.performance_repo = EnterpriseFederatedLearningPerformanceAnalyticsRepository(connection_manager)
    
    async def get_enterprise_overview(self, registry_id: str) -> Dict[str, Any]:
        """Get comprehensive enterprise overview for a federation."""
        try:
            overview = {
                'metrics': await self.metrics_repo.get_by_registry_id(registry_id),
                'compliance': await self.compliance_repo.get_by_registry_id(registry_id),
                'security': await self.security_repo.get_by_registry_id(registry_id),
                'performance': await self.performance_repo.get_by_registry_id(registry_id)
            }
            return overview
        except Exception as e:
            logger.error(f"Error getting enterprise overview: {e}")
            return {}


class EnterpriseFederatedLearningMetricsRepository:
    """Repository for enterprise federated learning metrics."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table_name = "enterprise_federated_learning_metrics"
    
    async def create(self, metrics: EnterpriseFederatedLearningMetrics) -> bool:
        """Create enterprise metrics."""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    metrics_id, registry_id, enterprise_health_score, federation_efficiency_score,
                    privacy_preservation_score, model_quality_score, collaboration_effectiveness,
                    performance_trend, risk_assessment_score, compliance_adherence,
                    user_id, org_id, dept_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                metrics.metrics_id, metrics.registry_id, metrics.enterprise_health_score,
                metrics.federation_efficiency_score, metrics.privacy_preservation_score,
                metrics.model_quality_score, metrics.collaboration_effectiveness,
                metrics.performance_trend, metrics.risk_assessment_score, metrics.compliance_adherence,
                metrics.user_id, metrics.org_id, metrics.dept_id, metrics.created_at, metrics.updated_at
            )
            
            return await self.connection_manager.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"Error creating enterprise metrics: {e}")
            return False
    
    async def get_by_registry_id(self, registry_id: str) -> Optional[Dict[str, Any]]:
        """Get enterprise metrics by registry ID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ?"
            return await self.connection_manager.fetch_one(query, (registry_id,))
        except Exception as e:
            logger.error(f"Error getting enterprise metrics: {e}")
            return None


class EnterpriseFederatedLearningComplianceTrackingRepository:
    """Repository for enterprise compliance tracking."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table_name = "enterprise_federated_learning_compliance_tracking"
    
    async def create(self, compliance: EnterpriseFederatedLearningComplianceTracking) -> bool:
        """Create compliance tracking entry."""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    compliance_id, registry_id, compliance_framework, compliance_status,
                    privacy_policy_version, data_retention_policy, audit_trail_enabled,
                    last_audit_date, next_audit_date, compliance_score, risk_level,
                    user_id, org_id, dept_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                compliance.compliance_id, compliance.registry_id, compliance.compliance_framework,
                compliance.compliance_status, compliance.privacy_policy_version,
                compliance.data_retention_policy, compliance.audit_trail_enabled,
                compliance.last_audit_date, compliance.next_audit_date, compliance.compliance_score,
                compliance.risk_level, compliance.user_id, compliance.org_id, compliance.dept_id,
                compliance.created_at, compliance.updated_at
            )
            
            return await self.connection_manager.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"Error creating compliance tracking: {e}")
            return False
    
    async def get_by_registry_id(self, registry_id: str) -> Optional[Dict[str, Any]]:
        """Get compliance tracking by registry ID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ?"
            return await self.connection_manager.fetch_one(query, (registry_id,))
        except Exception as e:
            logger.error(f"Error getting compliance tracking: {e}")
            return None


class EnterpriseFederatedLearningSecurityMetricsRepository:
    """Repository for enterprise security metrics."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table_name = "enterprise_federated_learning_security_metrics"
    
    async def create(self, security: EnterpriseFederatedLearningSecurityMetrics) -> bool:
        """Create security metrics entry."""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    security_id, registry_id, security_score, threat_detection_score,
                    encryption_strength, authentication_method, access_control_score,
                    data_protection_score, incident_response_time, security_audit_score,
                    user_id, org_id, dept_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                security.security_id, security.registry_id, security.security_score,
                security.threat_detection_score, security.encryption_strength,
                security.authentication_method, security.access_control_score,
                security.data_protection_score, security.incident_response_time,
                security.security_audit_score, security.user_id, security.org_id,
                security.dept_id, security.created_at, security.updated_at
            )
            
            return await self.connection_manager.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"Error creating security metrics: {e}")
            return False
    
    async def get_by_registry_id(self, registry_id: str) -> Optional[Dict[str, Any]]:
        """Get security metrics by registry ID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ?"
            return await self.connection_manager.fetch_one(query, (registry_id,))
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return None


class EnterpriseFederatedLearningPerformanceAnalyticsRepository:
    """Repository for enterprise performance analytics."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.table_name = "enterprise_federated_learning_performance_analytics"
    
    async def create(self, analytics: EnterpriseFederatedLearningPerformanceAnalytics) -> bool:
        """Create performance analytics entry."""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    analytics_id, registry_id, performance_score, efficiency_score,
                    scalability_score, reliability_score, optimization_potential,
                    bottleneck_identification, performance_trend, recommendations,
                    user_id, org_id, dept_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                analytics.analytics_id, analytics.registry_id, analytics.performance_score,
                analytics.efficiency_score, analytics.scalability_score, analytics.reliability_score,
                analytics.optimization_potential, analytics.bottleneck_identification,
                analytics.performance_trend, analytics.recommendations, analytics.user_id,
                analytics.org_id, analytics.dept_id, analytics.created_at, analytics.updated_at
            )
            
            return await self.connection_manager.execute_query(query, values)
            
        except Exception as e:
            logger.error(f"Error creating performance analytics: {e}")
            return False
    
    async def get_by_registry_id(self, registry_id: str) -> Optional[Dict[str, Any]]:
        """Get performance analytics by registry ID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = ?"
            return await self.connection_manager.fetch_one(query, (registry_id,))
        except Exception as e:
            logger.error(f"Error getting performance analytics: {e}")
            return None





