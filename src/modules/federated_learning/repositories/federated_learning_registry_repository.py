"""
Federated Learning Registry Repository
=====================================

Repository for federated learning registry operations using engine ConnectionManager.
Implements pure async patterns for optimal performance.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from src.engine.database.connection_manager import ConnectionManager
from ..models.federated_learning_registry import FederatedLearningRegistry


class FederatedLearningRegistryRepository:
    """Repository for federated learning registry operations"""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize repository with connection manager"""
        self.connection_manager = connection_manager
        self.table_name = "federated_learning_registry"
    
    async def create(self, registry: FederatedLearningRegistry) -> bool:
        """Create a new registry entry (async)"""
        try:
            query = f"""
                INSERT INTO {self.table_name} (
                    registry_id, federation_name, registry_name, federation_type, federation_category,
                    aasx_integration_id, twin_registry_id, kg_neo4j_id, physics_modeling_id, ai_rag_id, certificate_manager_id,
                    integration_status, overall_health_score, health_status, lifecycle_status,
                    federation_participation_status, aggregation_status, privacy_compliance_status, algorithm_execution_status,
                    performance_score, data_quality_score, reliability_score, compliance_score,
                    security_level, access_control_level, encryption_enabled,
                    compliance_framework, compliance_status, last_audit_date, next_audit_date, audit_details, risk_level,
                    security_score, threat_detection_score, encryption_strength, authentication_method, access_control_score, 
                    data_protection_score, incident_response_time, security_audit_score, last_security_scan, security_details,
                    efficiency_score, scalability_score, optimization_potential, bottleneck_identification, performance_trend, 
                    last_optimization_date, optimization_suggestions,
                    user_id, org_id, dept_id, created_at, updated_at, metadata
                ) VALUES (:registry_id, :federation_name, :registry_name, :federation_type, :federation_category,
                    :aasx_integration_id, :twin_registry_id, :kg_neo4j_id, :physics_modeling_id, :ai_rag_id, :certificate_manager_id,
                    :integration_status, :overall_health_score, :health_status, :lifecycle_status,
                    :federation_participation_status, :aggregation_status, :privacy_compliance_status, :algorithm_execution_status,
                    :performance_score, :data_quality_score, :reliability_score, :compliance_score,
                    :security_level, :access_control_level, :encryption_enabled,
                    :compliance_framework, :compliance_status, :last_audit_date, :next_audit_date, :audit_details, :risk_level,
                    :security_score, :threat_detection_score, :encryption_strength, :authentication_method, :access_control_score, 
                    :data_protection_score, :incident_response_time, :security_audit_score, :last_security_scan, :security_details,
                    :efficiency_score, :scalability_score, :optimization_potential, :bottleneck_identification, :performance_trend, 
                    :last_optimization_date, :optimization_suggestions,
                    :user_id, :org_id, :dept_id, :created_at, :updated_at, :metadata)
            """
            
            params = {
                'registry_id': registry.registry_id,
                'federation_name': registry.federation_name,
                'registry_name': registry.registry_name,
                'federation_type': registry.federation_type,
                'federation_category': registry.federation_category,
                'aasx_integration_id': registry.aasx_integration_id,
                'twin_registry_id': registry.twin_registry_id,
                'kg_neo4j_id': registry.kg_neo4j_id,
                'physics_modeling_id': registry.physics_modeling_id,
                'ai_rag_id': registry.ai_rag_id,
                'certificate_manager_id': registry.certificate_manager_id,
                'integration_status': registry.integration_status,
                'overall_health_score': registry.overall_health_score,
                'health_status': registry.health_status,
                'lifecycle_status': registry.lifecycle_status,
                'federation_participation_status': registry.federation_participation_status,
                'aggregation_status': registry.aggregation_status,
                'privacy_compliance_status': registry.privacy_compliance_status,
                'algorithm_execution_status': registry.algorithm_execution_status,
                'performance_score': registry.performance_score,
                'data_quality_score': registry.data_quality_score,
                'reliability_score': registry.reliability_score,
                'compliance_score': registry.compliance_score,
                'security_level': registry.security_level,
                'access_control_level': registry.access_control_level,
                'encryption_enabled': registry.encryption_enabled,
                'compliance_framework': registry.compliance_framework,
                'compliance_status': registry.compliance_status,
                'last_audit_date': registry.last_audit_date,
                'next_audit_date': registry.next_audit_date,
                'audit_details': str(registry.audit_details) if registry.audit_details else None,
                'risk_level': registry.risk_level,
                'security_score': registry.security_score,
                'threat_detection_score': registry.threat_detection_score,
                'encryption_strength': registry.encryption_strength,
                'authentication_method': registry.authentication_method,
                'access_control_score': registry.access_control_score,
                'data_protection_score': registry.data_protection_score,
                'incident_response_time': registry.incident_response_time,
                'security_audit_score': registry.security_audit_score,
                'last_security_scan': registry.last_security_scan,
                'security_details': str(registry.security_details) if registry.security_details else None,
                'efficiency_score': registry.efficiency_score,
                'scalability_score': registry.scalability_score,
                'optimization_potential': registry.optimization_potential,
                'bottleneck_identification': registry.bottleneck_identification,
                'performance_trend': registry.performance_trend,
                'last_optimization_date': registry.last_optimization_date,
                'optimization_suggestions': str(registry.optimization_suggestions) if registry.optimization_suggestions else None,
                'user_id': registry.user_id,
                'org_id': registry.org_id,
                'dept_id': registry.dept_id,
                'created_at': registry.created_at,
                'updated_at': registry.updated_at,
                'metadata': str(registry.metadata) if registry.metadata else None
            }
            
            await self.connection_manager.execute_update(query, params)
            return True
            
        except Exception as e:
            print(f"Error creating registry: {e}")
            return False
    
    async def get_by_id(self, registry_id: str) -> Optional[FederatedLearningRegistry]:
        """Get registry by ID (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE registry_id = :registry_id"
            result = await self.connection_manager.execute_query(query, {"registry_id": registry_id})
            
            if result and len(result) > 0:
                return self._row_to_model(result[0])
            return None
            
        except Exception as e:
            print(f"Error fetching registry by ID: {e}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[FederatedLearningRegistry]:
        """Get all registries with pagination (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            results = await self.connection_manager.execute_query(query, {"limit": limit, "offset": offset})
            
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching all registries: {e}")
            return []
    
    async def get_by_federation_type(self, federation_type: str) -> List[FederatedLearningRegistry]:
        """Get registries by federation type (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE federation_type = :federation_type ORDER BY created_at DESC"
            results = await self.connection_manager.execute_query(query, {"federation_type": federation_type})
            
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching registries by type: {e}")
            return []
    
    async def get_by_health_status(self, health_status: str) -> List[FederatedLearningRegistry]:
        """Get registries by health status (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE health_status = :health_status ORDER BY overall_health_score DESC"
            results = await self.connection_manager.execute_query(query, {"health_status": health_status})
            
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching registries by health status: {e}")
            return []
    
    async def get_by_user(self, user_id: str) -> List[FederatedLearningRegistry]:
        """Get registries by user ID (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE user_id = :user_id ORDER BY created_at DESC"
            results = await self.connection_manager.execute_query(query, {"user_id": user_id})
            
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching registries by user: {e}")
            return []
    
    async def get_by_department(self, dept_id: str) -> List[FederatedLearningRegistry]:
        """Get registries by department ID (async)"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE dept_id = :dept_id ORDER BY created_at DESC"
            results = await self.connection_manager.execute_query(query, {"dept_id": dept_id})
            
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching registries by department: {e}")
            return []
    
    async def update(self, registry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update registry (async)"""
        try:
            # Build dynamic update query
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                if key in ['audit_details', 'security_details', 'optimization_suggestions', 'metadata']:
                    set_clauses.append(f"{key} = ?")
                    params.append(str(value) if value else None)
                elif key in ['last_audit_date', 'next_audit_date', 'last_security_scan', 'last_optimization_date']:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = ?")
            params.append(datetime.now())
            
            # Add registry_id for WHERE clause
            params.append(registry_id)
            
            query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE registry_id = ?"
            await self.connection_manager.execute_query(query, params)
            
            return True
            
        except Exception as e:
            print(f"Error updating registry: {e}")
            return False
    
    async def delete(self, registry_id: str) -> bool:
        """Delete registry (async)"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE registry_id = ?"
            await self.connection_manager.execute_query(query, (registry_id,))
            return True
            
        except Exception as e:
            print(f"Error deleting registry: {e}")
            return False
    
    async def search(self, search_term: str, limit: int = 50) -> List[FederatedLearningRegistry]:
        """Search registries by name or description (async)"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE federation_name LIKE :search_pattern OR registry_name LIKE :search_pattern OR federation_category LIKE :search_pattern
                ORDER BY created_at DESC LIMIT :limit
            """
            search_pattern = f"%{search_term}%"
            params = {"search_pattern": search_pattern, "limit": limit}
            
            results = await self.connection_manager.execute_query(query, params)
            return [self._row_to_model(row) for row in results]
            
        except Exception as e:
            print(f"Error searching registries: {e}")
            return []
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics (async)"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_registries,
                    AVG(overall_health_score) as avg_health_score,
                    COUNT(CASE WHEN health_status = 'healthy' THEN 1 END) as healthy_count,
                    COUNT(CASE WHEN health_status = 'warning' THEN 1 END) as warning_count,
                    COUNT(CASE WHEN health_status = 'critical' THEN 1 END) as critical_count
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            print(f"Error getting health summary: {e}")
            return {}
    
    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary statistics (async)"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_registries,
                    COUNT(CASE WHEN compliance_status = 'compliant' THEN 1 END) as compliant_count,
                    COUNT(CASE WHEN compliance_status = 'non_compliant' THEN 1 END) as non_compliant_count,
                    COUNT(CASE WHEN compliance_status = 'pending' THEN 1 END) as pending_count,
                    AVG(security_score) as avg_security_score
                FROM {self.table_name}
            """
            
            result = await self.connection_manager.execute_query(query, {})
            return dict(result[0]) if result and len(result) > 0 else {}
            
        except Exception as e:
            print(f"Error getting compliance summary: {e}")
            return {}
    
    def _row_to_model(self, row: Dict[str, Any]) -> FederatedLearningRegistry:
        """Convert database row to model instance"""
        # Parse JSON fields
        if row.get('audit_details'):
            try:
                import json
                row['audit_details'] = json.loads(row['audit_details'])
            except:
                row['audit_details'] = {}
        
        if row.get('security_details'):
            try:
                import json
                row['security_details'] = json.loads(row['security_details'])
            except:
                row['security_details'] = {}
        
        if row.get('optimization_suggestions'):
            try:
                import json
                row['optimization_suggestions'] = json.loads(row['optimization_suggestions'])
            except:
                row['optimization_suggestions'] = []
        
        if row.get('metadata'):
            try:
                import json
                row['metadata'] = json.loads(row['metadata'])
            except:
                row['metadata'] = {}
        
        return FederatedLearningRegistry(**row)
