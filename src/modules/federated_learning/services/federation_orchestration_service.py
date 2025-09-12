"""
Federation Orchestration Service
================================

Core service for orchestrating federated learning operations.
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


class FederationOrchestrationService:
    """Service for orchestrating federated learning operations"""
    
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
    
    async def create_federation(
        self,
        federation_name: str,
        registry_name: str,
        federation_type: str,
        federation_category: str,
        user_id: str,
        org_id: str,
        dept_id: str,
        **kwargs
    ) -> Optional[FederatedLearningRegistry]:
        """Create a new federation (async)"""
        try:
            # Generate unique registry ID
            registry_id = f"fl_{federation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
            
            # Create registry instance
            registry = FederatedLearningRegistry(
                registry_id=registry_id,
                federation_name=federation_name,
                registry_name=registry_name,
                federation_type=federation_type,
                federation_category=federation_category,
                user_id=user_id,
                org_id=org_id,
                dept_id=dept_id,
                **kwargs
            )
            
            # Set initial status
            await registry.update_health_status()
            
            # Persist to database
            success = await self.registry_repo.create(registry)
            if not success:
                raise Exception("Failed to create federation in database")
            
            # Create initial metrics
            await self._create_initial_metrics(registry_id)
            
            print(f"✅ Federation '{federation_name}' created successfully with ID: {registry_id}")
            return registry
            
        except Exception as e:
            print(f"❌ Failed to create federation: {e}")
            return None
    
    async def _create_initial_metrics(self, registry_id: str) -> bool:
        """Create initial metrics for a new federation (async)"""
        try:
            initial_metrics = FederatedLearningMetrics(
                registry_id=registry_id,
                health_score=100.0,  # Start with perfect health
                response_time_ms=0.0,
                uptime_percentage=100.0,
                error_rate=0.0,
                federation_participation_speed_sec=0.0,
                aggregation_speed_sec=0.0,
                privacy_compliance_speed_sec=0.0,
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                gpu_usage_percent=0.0,
                network_throughput_mbps=0.0
            )
            
            success = await self.metrics_repo.create(initial_metrics)
            return success
            
        except Exception as e:
            print(f"❌ Failed to create initial metrics: {e}")
            return False
    
    async def start_federation_cycle(self, registry_id: str) -> bool:
        """Start a federation learning cycle (async)"""
        try:
            # Get federation details
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                raise Exception(f"Federation {registry_id} not found")
            
            # Update status
            update_data = {
                'lifecycle_status': 'active',
                'federation_participation_status': 'active',
                'algorithm_execution_status': 'running'
            }
            
            success = await self.registry_repo.update(registry_id, update_data)
            if not success:
                raise Exception("Failed to update federation status")
            
            # Update metrics
            await self._update_federation_metrics(registry_id, 'cycle_started')
            
            print(f"✅ Federation cycle started for {registry.federation_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start federation cycle: {e}")
            return False
    
    async def stop_federation_cycle(self, registry_id: str) -> bool:
        """Stop a federation learning cycle (async)"""
        try:
            # Get federation details
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                raise Exception(f"Federation {registry_id} not found")
            
            # Update status
            update_data = {
                'lifecycle_status': 'paused',
                'federation_participation_status': 'inactive',
                'algorithm_execution_status': 'stopped'
            }
            
            success = await self.registry_repo.update(registry_id, update_data)
            if not success:
                raise Exception("Failed to update federation status")
            
            # Update metrics
            await self._update_federation_metrics(registry_id, 'cycle_stopped')
            
            print(f"✅ Federation cycle stopped for {registry.federation_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop federation cycle: {e}")
            return False
    
    async def _update_federation_metrics(self, registry_id: str, event: str) -> None:
        """Update federation metrics based on events (async)"""
        try:
            # Get current metrics
            current_metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            if not current_metrics:
                return
            
            # Update based on event
            update_data = {}
            if event == 'cycle_started':
                update_data['federation_participation_speed_sec'] = 0.0  # Reset timer
            elif event == 'cycle_stopped':
                update_data['federation_participation_speed_sec'] = current_metrics.federation_participation_speed_sec
            
            if update_data:
                await self.metrics_repo.update(current_metrics.metric_id, update_data)
                
        except Exception as e:
            print(f"⚠️  Failed to update federation metrics: {e}")
    
    async def get_federation_status(self, registry_id: str) -> Dict[str, Any]:
        """Get comprehensive federation status (async)"""
        try:
            # Get registry and metrics
            registry = await self.registry_repo.get_by_id(registry_id)
            if not registry:
                return {'error': 'Federation not found'}
            
            metrics = await self.metrics_repo.get_latest_by_registry_id(registry_id)
            
            # Calculate health and performance
            health_score = await registry.calculate_overall_health()
            is_healthy = await registry.is_healthy()
            
            if metrics:
                performance_score = await metrics.calculate_overall_performance_score()
                is_performing = await metrics.is_performing_well()
            else:
                performance_score = 0.0
                is_performing = False
            
            return {
                'registry_id': registry_id,
                'federation_name': registry.federation_name,
                'status': {
                    'lifecycle': registry.lifecycle_status,
                    'participation': registry.federation_participation_status,
                    'algorithm': registry.algorithm_execution_status,
                    'aggregation': registry.aggregation_status
                },
                'health': {
                    'overall_score': health_score,
                    'is_healthy': is_healthy,
                    'status': registry.health_status
                },
                'performance': {
                    'score': performance_score,
                    'is_performing_well': is_performing
                },
                'compliance': {
                    'framework': registry.compliance_framework,
                    'status': registry.compliance_status,
                    'risk_level': registry.risk_level
                },
                'last_updated': registry.updated_at.isoformat() if registry.updated_at else None
            }
            
        except Exception as e:
            print(f"❌ Failed to get federation status: {e}")
            return {'error': str(e)}
    
    async def get_all_federations(
        self,
        user_id: Optional[str] = None,
        dept_id: Optional[str] = None,
        health_status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all federations with optional filtering (async)"""
        try:
            # Get registries based on filters
            if user_id:
                registries = await self.registry_repo.get_by_user(user_id)
            elif dept_id:
                registries = await self.registry_repo.get_by_department(dept_id)
            elif health_status:
                registries = await self.registry_repo.get_by_health_status(health_status)
            else:
                registries = await self.registry_repo.get_all(limit=limit)
            
            # Convert to summary format
            results = []
            for registry in registries:
                summary = await registry.to_summary_dict()
                results.append(summary)
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to get federations: {e}")
            return []
    
    async def update_federation_config(
        self,
        registry_id: str,
        config_updates: Dict[str, Any]
    ) -> bool:
        """Update federation configuration (async)"""
        try:
            # Validate updates
            allowed_updates = {
                'federation_name', 'registry_name', 'federation_category',
                'security_level', 'access_control_level', 'encryption_enabled',
                'compliance_framework', 'risk_level'
            }
            
            filtered_updates = {
                k: v for k, v in config_updates.items() 
                if k in allowed_updates
            }
            
            if not filtered_updates:
                raise Exception("No valid configuration updates provided")
            
            # Update registry
            success = await self.registry_repo.update(registry_id, filtered_updates)
            if not success:
                raise Exception("Failed to update federation configuration")
            
            print(f"✅ Federation configuration updated for {registry_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update federation configuration: {e}")
            return False
    
    async def get_federation_analytics(
        self,
        registry_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get federation analytics and trends (async)"""
        try:
            # Get performance trends
            trends = await self.metrics_repo.get_performance_trends(registry_id, days)
            
            # Get health summary
            health_summary = await self.registry_repo.get_health_summary()
            
            # Get compliance summary
            compliance_summary = await self.registry_repo.get_compliance_summary()
            
            # Get alerts
            alerts = await self.metrics_repo.get_alerts(registry_id)
            
            return {
                'performance_trends': trends,
                'health_summary': health_summary,
                'compliance_summary': compliance_summary,
                'alerts': alerts,
                'analysis_period_days': days
            }
            
        except Exception as e:
            print(f"❌ Failed to get federation analytics: {e}")
            return {'error': str(e)}
    
    async def cleanup_inactive_federations(self, days_threshold: int = 30) -> int:
        """Clean up inactive federations (async)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            
            # Get inactive federations
            all_registries = await self.registry_repo.get_all(limit=1000)
            inactive_count = 0
            
            for registry in all_registries:
                if (registry.lifecycle_status == 'inactive' and 
                    registry.updated_at and 
                    registry.updated_at < cutoff_date):
                    
                    # Delete federation and associated metrics
                    await self.registry_repo.delete(registry.registry_id)
                    
                    # Get and delete metrics
                    metrics = await self.metrics_repo.get_by_registry_id(registry.registry_id)
                    for metric in metrics:
                        await self.metrics_repo.delete(metric.metric_id)
                    
                    inactive_count += 1
            
            if inactive_count > 0:
                print(f"✅ Cleaned up {inactive_count} inactive federations")
            
            return inactive_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup inactive federations: {e}")
            return 0





