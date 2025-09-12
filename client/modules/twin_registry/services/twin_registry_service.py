"""
Twin Registry Service
====================

Core service for twin registry operations following AASX module pattern.
Handles CRUD operations, pagination, and twin lifecycle management.
Now fully integrated with src/twin_registry core services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import core Twin Registry services
try:
    from src.modules.twin_registry.core.twin_registry_service import TwinRegistryService as CoreTwinRegistryService
    from src.modules.twin_registry.core.twin_lifecycle_service import TwinLifecycleService
    from src.modules.twin_registry.core.twin_relationship_service import TwinRelationshipService
    from src.modules.twin_registry.core.twin_instance_service import TwinInstanceService
    from src.modules.twin_registry.core.twin_sync_service import TwinSyncService
    print("✅ Twin Registry core services imported successfully")
    CORE_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Twin Registry core services not available: {e}")
    CORE_SERVICES_AVAILABLE = False
    # Set to None for fallback
    CoreTwinRegistryService = None
    TwinLifecycleService = None
    TwinRelationshipService = None
    TwinInstanceService = None
    TwinSyncService = None

logger = logging.getLogger(__name__)

class TwinRegistryService:
    """
    Core twin registry service for managing digital twins.
    Now fully integrated with src/twin_registry core services.
    Follows the same pattern as AASX module services.
    """
    
    def __init__(self):
        """Initialize the twin registry service with core services."""
        if not CORE_SERVICES_AVAILABLE:
            logger.warning("⚠️ Core services not available - using fallback mode")
            self.core_registry = None
            self.lifecycle_service = None
            self.relationship_service = None
            self.instance_service = None
            self.sync_service = None
            return
        
        try:
            # Initialize core services from src/twin_registry
            self.core_registry = CoreTwinRegistryService()
            self.lifecycle_service = TwinLifecycleService()
            self.relationship_service = TwinRelationshipService()
            self.instance_service = TwinInstanceService()
            self.sync_service = TwinSyncService()
            
            logger.info("✅ Twin Registry Service initialized with all core services")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize core services: {e}")
            # Fallback to None if initialization fails
            self.core_registry = None
            self.lifecycle_service = None
            self.relationship_service = None
            self.instance_service = None
            self.sync_service = None
    
    async def initialize(self) -> None:
        """Initialize all core services"""
        if not CORE_SERVICES_AVAILABLE:
            logger.warning("⚠️ Core services not available - skipping initialization")
            return
            
        try:
            if self.core_registry:
                await self.core_registry.initialize()
            if self.lifecycle_service:
                await self.lifecycle_service.initialize()
            if self.relationship_service:
                await self.relationship_service.initialize()
            if self.instance_service:
                await self.instance_service.initialize()
            if self.sync_service:
                await self.sync_service.initialize()
                
            logger.info("✅ All core services initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize core services: {e}")
            raise
    
    async def get_all_twins(self, page: int = 1, page_size: int = 10, 
                           filters: Dict[str, Any] = None, twin_type: str = None, 
                           status: str = None, project_id: str = None) -> Dict[str, Any]:
        """
        Get all twins with pagination and filtering.
        Now uses core registry service for enhanced functionality.
        
        Args:
            page: Page number for pagination
            page_size: Number of twins per page
            filters: Dictionary of filters to apply (twin_type, status, project_id, etc.)
            
        Returns:
            Dictionary with twins, pagination info, and statistics
        """
        try:
            logger.info(f"Getting twins - page: {page}, size: {page_size}")
            
            # Use core registry service if available
            if self.core_registry:
                try:
                    # Get twins from core registry service
                    result = await self.core_registry.get_all_twins(
                        page=page, 
                        page_size=page_size,
                        filters={
                            'twin_type': twin_type,
                            'status': status,
                            'project_id': project_id
                        }
                    )
                    logger.info(f"✅ Retrieved twins from core registry service")
                    return result
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to basic method: {e}")
            
            # Fallback: Direct database query
            logger.warning("⚠️ Core registry service not available - using direct database query")
            try:
                # Import database manager directly
                from src.engine.database.database_factory import DatabaseFactory, DatabaseType
                from src.engine.database.connection_manager import ConnectionManager
                from pathlib import Path
                
                # Connect to database
                data_dir = Path("data")
                db_path = data_dir / "aasx_database.db"
                connection_manager = DatabaseFactory.create_connection_manager(
                    DatabaseType.SQLITE, 
                    str(db_path)
                )
                # Use the connection manager directly since we don't have a BaseDatabaseManager
                
                # Query twins directly
                query = "SELECT * FROM twin_registry ORDER BY created_at DESC LIMIT ? OFFSET ?"
                offset = (page - 1) * page_size
                result = db_manager.execute_query(query, (page_size, offset))
                
                # Get total count
                count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM twin_registry")
                total_count = count_result[0]['count'] if count_result else 0
                
                # Convert to expected format
                twins_data = []
                for row in result:
                    twin_dict = {
                        "id": row.get('registry_id', 'unknown'),
                        "registry_id": row.get('registry_id', 'unknown'),
                        "twin_id": row.get('twin_id', 'unknown'),
                        "twin_name": row.get('twin_name', 'Unknown Twin'),
                        "registry_name": row.get('registry_name', 'Unknown Registry'),
                        "twin_category": row.get('twin_category', 'generic'),
                        "twin_type": row.get('twin_type', 'physical'),
                        "twin_priority": row.get('twin_priority', 'normal'),
                        "twin_version": row.get('twin_version', '1.0.0'),
                        "registry_type": row.get('registry_type', 'extraction'),
                        "workflow_source": row.get('workflow_source', 'aasx_file'),
                        "integration_status": row.get('integration_status', 'pending'),
                        "overall_health_score": row.get('overall_health_score', 0),
                        "health_status": row.get('health_status', 'unknown'),
                        "lifecycle_status": row.get('lifecycle_status', 'created'),
                        "lifecycle_phase": row.get('lifecycle_phase', 'development'),
                        "operational_status": row.get('operational_status', 'stopped'),
                        "availability_status": row.get('availability_status', 'offline'),
                        "sync_status": row.get('sync_status', 'pending'),
                        "sync_frequency": row.get('sync_frequency', 'daily'),
                        "performance_score": row.get('performance_score', 0.0),
                        "data_quality_score": row.get('data_quality_score', 0.0),
                        "reliability_score": row.get('reliability_score', 0.0),
                        "compliance_score": row.get('compliance_score', 0.0),
                        "security_level": row.get('security_level', 'standard'),
                        "access_control_level": row.get('access_control_level', 'user'),
                        "encryption_enabled": bool(row.get('encryption_enabled', False)),
                        "audit_logging_enabled": bool(row.get('audit_logging_enabled', False)),
                        "user_id": row.get('user_id', 'unknown'),
                        "org_id": row.get('org_id', 'unknown'),
                        "owner_team": row.get('owner_team'),
                        "steward_user_id": row.get('steward_user_id'),
                        "created_at": row.get('created_at'),
                        "updated_at": row.get('updated_at'),
                        "activated_at": row.get('activated_at'),
                        "last_accessed_at": row.get('last_accessed_at'),
                        "last_modified_at": row.get('last_modified_at'),
                        "registry_config": row.get('registry_config', '{}'),
                        "registry_metadata": row.get('registry_metadata', '{}'),
                        "custom_attributes": row.get('custom_attributes', '{}'),
                        "tags": row.get('tags', '[]'),
                        "relationships": row.get('relationships', '[]'),
                        "dependencies": row.get('dependencies', '[]'),
                        "instances": row.get('instances', '[]')
                    }
                    twins_data.append(twin_dict)
                
                # Calculate pagination
                total_pages = (total_count + page_size - 1) // page_size
                
                # Get active twins count
                active_result = db_manager.execute_query("SELECT COUNT(*) as count FROM twin_registry WHERE integration_status = 'active'")
                active_count = active_result[0]['count'] if active_result else 0
                
                return {
                    "twins": twins_data,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total_count": total_count,
                        "total_pages": total_pages
                    },
                    "statistics": {
                        "total_twins": total_count,
                        "active_twins": active_count,
                        "error_twins": 0
                    }
                }
                
            except Exception as e:
                logger.error(f"❌ Direct database query failed: {e}")
                # Return empty result if direct query also fails
                return {
                    "twins": [],
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total_count": 0,
                        "total_pages": 0
                    },
                    "statistics": {
                        "total_twins": 0,
                        "active_twins": 0,
                        "error_twins": 0
                    }
                }
            
        except Exception as e:
            logger.error(f"❌ Error getting twins: {e}")
            raise
    
    async def get_twin_by_id(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific twin by ID with detailed information.
        Now uses core registry service for enhanced functionality.
        
        Args:
            twin_id: The ID of the twin to retrieve
            
        Returns:
            Dictionary with twin information and lifecycle details
        """
        try:
            logger.info(f"Getting twin by ID: {twin_id}")
            
            # Use core registry service if available
            if self.core_registry:
                try:
                    # Get twin from core registry service
                    result = await self.core_registry.get_twin_by_id(twin_id)
                    if result:
                        logger.info(f"✅ Retrieved twin {twin_id} from core registry service")
                        return result
                    else:
                        logger.warning(f"Twin {twin_id} not found in core registry")
                        return None
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to basic method: {e}")
            
            # Fallback: Return None with warning
            logger.warning("⚠️ Core registry service not available - returning None")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting twin {twin_id}: {e}")
            raise
    
    # ==================== Lifecycle Management ====================
    
    # Note: Twin start/stop operations are now handled by AASX-ETL module
    # These methods have been removed to avoid confusion
    
    async def sync_twin(self, twin_id: str, sync_data: Optional[Dict[str, Any]] = None, triggered_by: Optional[str] = None) -> Dict[str, Any]:
        """Sync a twin"""
        try:
            logger.info(f"Syncing twin {twin_id}")
            
            # Use core lifecycle service
            success = await self.lifecycle_service.sync_twin(twin_id, sync_data, triggered_by)
            
            if success:
                # Get updated twin information
                twin_info = await self.get_twin_by_id(twin_id)
                return {
                    "success": True,
                    "message": f"Twin {twin_id} synced successfully",
                    "twin": twin_info
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to sync twin {twin_id}"
                }
                
        except Exception as e:
            logger.error(f"Error syncing twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error syncing twin {twin_id}: {str(e)}"
            }
    
    # ==================== Relationship Management ====================
    
    async def create_relationship(
        self,
        source_twin_id: str,
        target_twin_id: str,
        relationship_type: str,
        relationship_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a relationship between twins"""
        try:
            logger.info(f"Creating relationship between {source_twin_id} and {target_twin_id}")
            
            # Use core relationship service
            relationship = await self.relationship_service.create_relationship(
                source_twin_id, target_twin_id, relationship_type, relationship_data
            )
            
            return {
                "success": True,
                "message": "Relationship created successfully",
                "relationship": relationship.dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return {
                "success": False,
                "message": f"Error creating relationship: {str(e)}"
            }
    
    async def get_twin_relationships(self, twin_id: str) -> Dict[str, Any]:
        """Get all relationships for a twin"""
        try:
            logger.info(f"Getting relationships for twin {twin_id}")
            
            # Use core relationship service
            relationships = await self.relationship_service.get_twin_relationships(twin_id)
            
            return {
                "success": True,
                "relationships": [rel.dict() for rel in relationships],
                "count": len(relationships)
            }
            
        except Exception as e:
            logger.error(f"Error getting relationships for twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error getting relationships: {str(e)}",
                "relationships": [],
                "count": 0
            }
    
    # ==================== Instance Management ====================
    
    async def create_instance(
        self,
        twin_id: str,
        instance_data: Dict[str, Any],
        instance_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new instance of a twin"""
        try:
            logger.info(f"Creating instance for twin {twin_id}")
            
            # Use core instance service
            instance = await self.instance_service.create_instance(
                twin_id, instance_data, instance_metadata, created_by
            )
            
            return {
                "success": True,
                "message": "Instance created successfully",
                "instance": instance.dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating instance for twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error creating instance: {str(e)}"
            }
    
    async def get_twin_instances(self, twin_id: str) -> Dict[str, Any]:
        """Get all instances of a twin"""
        try:
            logger.info(f"Getting instances for twin {twin_id}")
            
            # Use core instance service
            instances = await self.instance_service.get_twin_instances(twin_id)
            
            return {
                "success": True,
                "instances": [inst.dict() for inst in instances],
                "count": len(instances)
            }
            
        except Exception as e:
            logger.error(f"Error getting instances for twin {twin_id}: {e}")
            return {
                "success": False,
                "message": f"Error getting instances: {str(e)}",
                "instances": [],
                "count": 0
            }
    
    # ==================== Registry Analytics ====================
    
    async def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive registry summary"""
        try:
            logger.info("Getting registry summary")
            
            # Use core registry service
            summary = await self.core_registry.get_registry_summary()
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error getting registry summary: {e}")
            return {
                "success": False,
                "message": f"Error getting registry summary: {str(e)}",
                "summary": {}
            }
    
    # ==================== DEPRECATED METHODS (Moved to AASX-ETL) ====================
    
    async def create_twin(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        DEPRECATED: Twin creation is now handled by AASX-ETL module.
        This method is kept for backward compatibility but will be removed.
        """
        logger.warning("⚠️ create_twin is deprecated - use AASX-ETL module instead")
        return {
            "success": False,
            "message": "Twin creation is now handled by AASX-ETL module. Use the AASX-ETL page for twin operations.",
            "deprecated": True,
            "redirect_to": "aasx-etl"
        }
    
    async def update_twin(self, twin_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        DEPRECATED: Twin updates are now handled by AASX-ETL module.
        This method is kept for backward compatibility but will be removed.
        """
        logger.warning("⚠️ update_twin is deprecated - use AASX-ETL module instead")
        return {
            "success": False,
            "message": "Twin updates are now handled by AASX-ETL module. Use the AASX-ETL page for twin operations.",
            "deprecated": True,
            "redirect_to": "aasx-etl"
        }
    
    async def delete_twin(self, twin_id: str) -> Dict[str, Any]:
        """
        DEPRECATED: Twin deletion is now handled by AASX-ETL module.
        This method is kept for backward compatibility but will be removed.
        """
        logger.warning("⚠️ delete_twin is deprecated - use AASX-ETL module instead")
        return {
            "success": False,
            "message": "Twin deletion is now handled by AASX-ETL module. Use the AASX-ETL page for twin operations.",
            "deprecated": True,
            "redirect_to": "aasx-etl"
        }
    
    async def search_twins(self, query: str = "", twin_type: str = "", 
                          status: str = "", project_id: str = None, 
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Search twins using core registry service"""
        try:
            logger.info(f"Searching twins with query: {query}")
            
            # Use core registry service if available
            if self.core_registry:
                try:
                    # Search twins using core registry service
                    result = await self.core_registry.search_twins(
                        query=query,
                        filters={
                            'twin_type': twin_type,
                            'status': status,
                            'project_id': project_id
                        },
                        page=1,
                        page_size=limit
                    )
                    logger.info(f"✅ Found twins using core registry service")
                    # Extract twins from result dictionary
                    return result.get("twins", [])
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to basic method: {e}")
            
            # Fallback: Return empty list with warning
            logger.warning("⚠️ Core registry service not available - returning empty list")
            return []
                
        except Exception as e:
            logger.error(f"❌ Error searching twins: {e}")
            return []
    
    async def get_twin_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for all twins.
        Now uses core registry service for enhanced functionality.
        
        Returns:
            Dictionary with twin statistics
        """
        try:
            logger.info("Getting twin statistics")
            
            # Use core registry service if available
            if self.core_registry:
                try:
                    # Get statistics from core registry service
                    result = await self.core_registry.get_twin_statistics()
                    logger.info(f"✅ Retrieved statistics from core registry service")
                    return result
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to basic method: {e}")
            
            # Fallback: Return basic statistics with warning
            logger.warning("⚠️ Core registry service not available - returning basic statistics")
            return {
                "total_twins": 0,
                "active_count": 0,
                "error_count": 0,
                "status_distribution": {},
                "type_distribution": {},
                "last_updated": datetime.now().isoformat(),
                "note": "Core service not available - limited statistics"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting twin statistics: {e}")
            raise

    async def get_twin_metrics(self, twin_id: str, time_range: str = "30d") -> List[Dict[str, Any]]:
        """
        Get metrics for a specific twin.
        Now uses core services for real database operations.
        
        Args:
            twin_id: The ID of the twin
            time_range: Time range for metrics (e.g., "7d", "30d", "90d")
            
        Returns:
            List of metrics dictionaries
        """
        try:
            logger.info(f"Getting metrics for twin {twin_id}, time range: {time_range}")
            
            # Use core services if available
            if self.core_registry:
                try:
                    # Get metrics from core registry service
                    result = await self.core_registry.get_twin_metrics(twin_id, time_range)
                    logger.info(f"✅ Retrieved metrics for twin {twin_id} from core registry service")
                    return result
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to database query: {e}")
            
            # Fallback: Query database directly
            try:
                # Import database manager for direct query
                from src.shared.database.database_manager import DatabaseManager
                from pathlib import Path
                
                db_path = Path("data/aasx_database.db")
                if not db_path.exists():
                    logger.warning("Database not found, returning empty metrics")
                    return []
                
                # Direct database query for metrics
                import sqlite3
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get registry_id for the twin
                    cursor.execute("""
                        SELECT registry_id FROM twin_registry 
                        WHERE twin_id = ? OR twin_name = ?
                    """, (twin_id, twin_id))
                    registry_result = cursor.fetchone()
                    
                    if not registry_result:
                        logger.warning(f"Twin {twin_id} not found in registry")
                        return []
                    
                    registry_id = registry_result[0]
                    
                    # Query metrics table - using actual schema
                    cursor.execute("""
                        SELECT metric_id, registry_id, timestamp, health_score, 
                               response_time_ms, throughput_ops_per_sec, error_rate,
                               availability_percent, resource_usage, performance_indicators,
                               quality_metrics, compliance_metrics, security_metrics,
                               business_metrics, custom_metrics, alerts, recommendations,
                               created_at, updated_at
                        FROM twin_registry_metrics 
                        WHERE registry_id = ?
                        ORDER BY timestamp DESC
                        LIMIT 100
                    """, (registry_id,))
                    
                    metrics = []
                    for row in cursor.fetchall():
                        metric = {
                            "metric_id": row[0],
                            "registry_id": row[1],
                            "timestamp": row[2],
                            "health_score": row[3],
                            "response_time_ms": row[4],
                            "throughput_ops_per_sec": row[5],
                            "error_rate": row[6],
                            "availability_percent": row[7],
                            "resource_usage": row[8] if row[8] else "{}",
                            "performance_indicators": row[9] if row[9] else "{}",
                            "quality_metrics": row[10] if row[10] else "{}",
                            "compliance_metrics": row[11] if row[11] else "{}",
                            "security_metrics": row[12] if row[12] else "{}",
                            "business_metrics": row[13] if row[13] else "{}",
                            "custom_metrics": row[14] if row[14] else "{}",
                            "alerts": row[15] if row[15] else "[]",
                            "recommendations": row[16] if row[16] else "[]",
                            "created_at": row[17],
                            "updated_at": row[18]
                        }
                        metrics.append(metric)
                    
                    logger.info(f"✅ Retrieved {len(metrics)} metrics from database for twin {twin_id}")
                    return metrics
                    
            except Exception as db_error:
                logger.error(f"Database query failed: {db_error}")
                # Final fallback: return minimal mock data
                return [
                    {
                        "metric_id": f"metric_{twin_id}_001",
                        "timestamp": datetime.now().isoformat(),
                        "health_score": 85.5,
                        "response_time_ms": 150.0,
                        "error_rate": 0.02,
                        "note": "Fallback data - database unavailable"
                    }
                ]
            
        except Exception as e:
            logger.error(f"Error getting twin metrics: {e}")
            raise

    async def get_all_metrics(self, time_range: str = "30d") -> List[Dict[str, Any]]:
        """
        Get all metrics across all twins.
        Now uses core services for real database operations.
        
        Args:
            time_range: Time range for metrics (e.g., "7d", "30d", "90d")
            
        Returns:
            List of metrics dictionaries
        """
        try:
            logger.info(f"Getting all metrics, time range: {time_range}")
            
            # Use core services if available
            if self.core_registry:
                try:
                    # Get all metrics from core registry service
                    result = await self.core_registry.get_all_metrics(time_range)
                    logger.info(f"✅ Retrieved all metrics from core registry service")
                    return result
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to database query: {e}")
            
            # Fallback: Query database directly
            try:
                from pathlib import Path
                
                db_path = Path("data/aasx_database.db")
                if not db_path.exists():
                    logger.warning("Database not found, returning empty metrics")
                    return []
                
                # Direct database query for all metrics
                import sqlite3
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Query all metrics with registry information - using actual schema
                    cursor.execute("""
                        SELECT 
                            trm.metric_id, 
                            trm.registry_id,
                            tr.twin_name,
                            tr.registry_type,
                            trm.timestamp, 
                            trm.health_score, 
                            trm.response_time_ms, 
                            trm.throughput_ops_per_sec, 
                            trm.error_rate,
                            trm.availability_percent, 
                            trm.resource_usage,
                            trm.performance_indicators, 
                            trm.quality_metrics,
                            trm.compliance_metrics, 
                            trm.security_metrics, 
                            trm.business_metrics,
                            trm.custom_metrics, 
                            trm.alerts, 
                            trm.recommendations,
                            trm.created_at, 
                            trm.updated_at
                        FROM twin_registry_metrics trm
                        JOIN twin_registry tr ON trm.registry_id = tr.registry_id
                        ORDER BY trm.timestamp DESC
                        LIMIT 200
                    """)
                    
                    metrics = []
                    for row in cursor.fetchall():
                        metric = {
                            "metric_id": row[0],
                            "registry_id": row[1],
                            "twin_name": row[2],
                            "registry_type": row[3],
                            "timestamp": row[4],
                            "health_score": row[5],
                            "response_time_ms": row[6],
                            "throughput_ops_per_sec": row[7],
                            "error_rate": row[8],
                            "availability_percent": row[9],
                            "resource_usage": row[10] if row[10] else "{}",
                            "performance_indicators": row[11] if row[11] else "{}",
                            "quality_metrics": row[12] if row[12] else "{}",
                            "compliance_metrics": row[13] if row[13] else "{}",
                            "security_metrics": row[14] if row[14] else "{}",
                            "business_metrics": row[15] if row[15] else "{}",
                            "custom_metrics": row[16] if row[16] else "{}",
                            "alerts": row[17] if row[17] else "[]",
                            "recommendations": row[18] if row[18] else "[]",
                            "created_at": row[19],
                            "updated_at": row[20]
                        }
                        metrics.append(metric)
                    
                    logger.info(f"✅ Retrieved {len(metrics)} metrics from database")
                    return metrics
                    
            except Exception as db_error:
                logger.error(f"Database query failed: {db_error}")
                # Final fallback: return minimal mock data
                return [
                    {
                        "metric_id": "metric_global_001",
                        "registry_id": "test_registry_001",
                        "timestamp": datetime.now().isoformat(),
                        "health_score": 85.5,
                        "response_time_ms": 150.0,
                        "error_rate": 0.02,
                        "note": "Fallback data - database unavailable"
                    }
                ]
            
        except Exception as e:
            logger.error(f"Error getting all metrics: {e}")
            raise

    async def get_all_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all relationships across all twins.
        Now uses core services for real database operations.
        
        Returns:
            List of relationship dictionaries
        """
        try:
            logger.info("Getting all relationships")
            
            # Use core services if available
            if self.relationship_service:
                try:
                    # Get relationships from core relationship service
                    result = await self.relationship_service.get_all_relationships()
                    logger.info(f"✅ Retrieved relationships from core relationship service")
                    return result
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to database query: {e}")
            
            # Fallback: Query database directly
            try:
                from pathlib import Path
                
                db_path = Path("data/aasx_database.db")
                if not db_path.exists():
                    logger.warning("Database not found, returning empty relationships")
                    return []
                
                # Direct database query for relationships
                import sqlite3
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Query all relationships from JSON fields
                    cursor.execute("""
                        SELECT 
                            tr.registry_id,
                            tr.twin_name,
                            tr.registry_type,
                            tr.relationships
                        FROM twin_registry tr
                        WHERE tr.relationships != '[]' AND tr.relationships IS NOT NULL
                        ORDER BY tr.updated_at DESC
                    """)
                    
                    all_relationships = []
                    for row in cursor.fetchall():
                        registry_id, twin_name, registry_type, relationships_json = row
                        
                        try:
                            import json
                            relationships = json.loads(relationships_json) if relationships_json else []
                            
                            for rel in relationships:
                                relationship = {
                                    "relationship_id": rel.get("relationship_id", f"rel_{registry_id}_{len(all_relationships)}"),
                                    "source_twin_id": registry_id,
                                    "source_twin_name": twin_name,
                                    "target_twin_id": rel.get("target_twin_id", "unknown"),
                                    "relationship_type": rel.get("relationship_type", "unknown"),
                                    "description": rel.get("description", ""),
                                    "created_at": rel.get("created_at", ""),
                                    "is_active": rel.get("is_active", True),
                                    "registry_type": registry_type,
                                    "metadata": rel.get("metadata", {})
                                }
                                all_relationships.append(relationship)
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in relationships for registry {registry_id}")
                            continue
                    
                    logger.info(f"✅ Retrieved {len(all_relationships)} relationships from database")
                    return all_relationships
                    
            except Exception as db_error:
                logger.error(f"Database query failed: {db_error}")
                # Final fallback: return minimal mock data
                return [
                    {
                        "relationship_id": "rel_001",
                        "source_twin_id": "test_registry_001",
                        "target_twin_id": "test_registry_002",
                        "relationship_type": "depends_on",
                        "created_at": datetime.now().isoformat(),
                        "note": "Fallback data - database unavailable"
                    }
                ]
            
        except Exception as e:
            logger.error(f"Error getting all relationships: {e}")
            raise

    async def get_all_instances(self) -> List[Dict[str, Any]]:
        """
        Get all instances across all twins.
        Now uses core services for real database operations.
        
        Returns:
            List of instance dictionaries
        """
        try:
            logger.info("Getting all instances")
            
            # Use core services if available
            if self.instance_service:
                try:
                    # Get instances from core instance service
                    result = await self.instance_service.get_all_instances()
                    logger.info(f"✅ Retrieved instances from core instance service")
                    return result
                except Exception as e:
                    logger.warning(f"⚠️ Core service failed, falling back to database query: {e}")
            
            # Fallback: Query database directly
            try:
                from pathlib import Path
                
                db_path = Path("data/aasx_database.db")
                if not db_path.exists():
                    logger.warning("Database not found, returning empty instances")
                    return []
                
                # Direct database query for instances
                import sqlite3
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Query all instances from JSON fields
                    cursor.execute("""
                        SELECT 
                            tr.registry_id,
                            tr.twin_name,
                            tr.registry_type,
                            tr.instances
                        FROM twin_registry tr
                        WHERE tr.instances != '[]' AND tr.instances IS NOT NULL
                        ORDER BY tr.updated_at DESC
                    """)
                    
                    all_instances = []
                    for row in cursor.fetchall():
                        registry_id, twin_name, registry_type, instances_json = row
                        
                        try:
                            import json
                            instances = json.loads(instances_json) if instances_json else []
                            
                            for inst in instances:
                                instance = {
                                    "instance_id": inst.get("instance_id", f"inst_{registry_id}_{len(all_instances)}"),
                                    "registry_id": registry_id,
                                    "twin_name": twin_name,
                                    "instance_name": inst.get("instance_name", "Unknown Instance"),
                                    "instance_type": inst.get("instance_type", "snapshot"),
                                    "version": inst.get("version", "1.0.0"),
                                    "created_at": inst.get("created_at", ""),
                                    "instance_data": inst.get("instance_data", {}),
                                    "is_active": inst.get("is_active", True),
                                    "registry_type": registry_type,
                                    "metadata": inst.get("instance_metadata", {})
                                }
                                all_instances.append(instance)
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in instances for registry {registry_id}")
                            continue
                    
                    logger.info(f"✅ Retrieved {len(all_instances)} instances from database")
                    return all_instances
                    
            except Exception as db_error:
                logger.error(f"Database query failed: {db_error}")
                # Final fallback: return minimal mock data
                return [
                    {
                        "instance_id": "inst_001",
                        "registry_id": "test_registry_001",
                        "instance_name": "Test Instance",
                        "instance_type": "snapshot",
                        "version": "1.0.0",
                        "created_at": datetime.now().isoformat(),
                        "note": "Fallback data - database unavailable"
                    }
                ]
            
        except Exception as e:
            logger.error(f"Error getting all instances: {e}")
            raise
    
    def _convert_twin_to_dict(self, twin: Any) -> Dict[str, Any]:
        """
        Generic converter for twin objects to dictionary format.
        Works with any twin object structure.
        """
        try:
            # Generic field mapping that works with any twin object
            twin_dict = {
                "twin_id": getattr(twin, 'twin_id', getattr(twin, 'id', '')),
                "twin_name": getattr(twin, 'twin_name', getattr(twin, 'name', '')),
                "description": getattr(twin, 'description', ''),
                "twin_type": getattr(twin, 'twin_type', getattr(twin, 'type', '')),
                "status": getattr(twin, 'status', 'active'),
                "project_id": getattr(twin, 'project_id', ''),
                "file_id": getattr(twin, 'file_id', ''),
                "created_at": getattr(twin, 'created_at', datetime.now()).isoformat() if hasattr(twin, 'created_at') and twin.created_at else datetime.now().isoformat(),
                "updated_at": getattr(twin, 'updated_at', datetime.now()).isoformat() if hasattr(twin, 'updated_at') and twin.updated_at else datetime.now().isoformat(),
                # Add health information if available
                "health_score": getattr(twin, 'health_score', 0),
                "error_count": getattr(twin, 'error_count', 0),
                "health_status": getattr(twin, 'health_status', 'unknown')
            }
            
            logger.debug(f"Converted twin {twin_dict['twin_id']} to dict: {twin_dict}")
            return twin_dict
            
        except Exception as e:
            logger.error(f"Error converting twin to dict: {e}")
            # Return minimal twin info
            return {
                "twin_id": getattr(twin, 'twin_id', getattr(twin, 'id', 'unknown')),
                "twin_name": "Error loading twin",
                "description": "",
                "twin_type": "",
                "status": "error",
                "project_id": "",
                "file_id": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "health_score": 0,
                "error_count": 0,
                "health_status": "unknown"
            } 