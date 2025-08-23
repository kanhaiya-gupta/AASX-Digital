"""
Twin Registry Integration
========================

Integration with digital twin registry for federated learning.
Handles twin discovery, registration, metadata management, and synchronization.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class TwinRegistryConfig:
    """Configuration for twin registry integration"""
    # Integration settings
    auto_discovery_enabled: bool = True
    metadata_sync_enabled: bool = True
    health_check_enabled: bool = True
    cache_enabled: bool = True
    
    # Discovery settings
    discovery_interval_minutes: int = 5
    max_discovery_retries: int = 3
    discovery_timeout_seconds: int = 30
    
    # Metadata settings
    metadata_cache_ttl_hours: int = 24
    metadata_validation_enabled: bool = True
    required_metadata_fields: List[str] = None
    
    # Health check settings
    health_check_interval_minutes: int = 10
    health_check_timeout_seconds: int = 15
    min_health_score: float = 0.7
    
    # Synchronization settings
    sync_batch_size: int = 100
    sync_retry_attempts: int = 3
    sync_timeout_seconds: int = 60
    
    def __post_init__(self):
        if self.required_metadata_fields is None:
            self.required_metadata_fields = [
                'twin_id', 'name', 'type', 'status', 'created_at', 'updated_at'
            ]


@dataclass
class TwinRegistryMetrics:
    """Metrics for twin registry integration"""
    # Discovery metrics
    twins_discovered: int = 0
    discovery_attempts: int = 0
    discovery_failures: int = 0
    discovery_time: float = 0.0
    
    # Registration metrics
    twins_registered: int = 0
    registration_attempts: int = 0
    registration_failures: int = 0
    registration_time: float = 0.0
    
    # Metadata metrics
    metadata_syncs: int = 0
    metadata_updates: int = 0
    metadata_validation_failures: int = 0
    metadata_sync_time: float = 0.0
    
    # Health check metrics
    health_checks_performed: int = 0
    health_check_failures: int = 0
    average_health_score: float = 0.0
    health_check_time: float = 0.0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_size: int = 0
    cache_evictions: int = 0


class TwinRegistryIntegration:
    """Integration with digital twin registry for federated learning"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[TwinRegistryConfig] = None
    ):
        """Initialize Twin Registry Integration"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or TwinRegistryConfig()
        
        # Integration state
        self.discovered_twins: Dict[str, Dict[str, Any]] = {}
        self.registered_twins: Dict[str, Dict[str, Any]] = {}
        self.metadata_cache: Dict[str, Dict[str, Any]] = {}
        self.health_scores: Dict[str, float] = {}
        
        # Discovery state
        self.discovery_active = False
        self.last_discovery = None
        self.discovery_task = None
        
        # Health monitoring state
        self.health_monitoring_active = False
        self.health_check_task = None
        
        # Metrics tracking
        self.metrics = TwinRegistryMetrics()
        
    async def start_integration(self):
        """Start the twin registry integration"""
        try:
            print("🚀 Starting Twin Registry Integration...")
            
            # Start discovery if enabled
            if self.config.auto_discovery_enabled:
                await self.start_discovery()
            
            # Start health monitoring if enabled
            if self.config.health_check_enabled:
                await self.start_health_monitoring()
            
            print("✅ Twin Registry Integration started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start Twin Registry Integration: {e}")
            raise
    
    async def stop_integration(self):
        """Stop the twin registry integration"""
        try:
            print("🛑 Stopping Twin Registry Integration...")
            
            # Stop discovery
            if self.discovery_active:
                await self.stop_discovery()
            
            # Stop health monitoring
            if self.health_monitoring_active:
                await self.stop_health_monitoring()
            
            print("✅ Twin Registry Integration stopped successfully")
            
        except Exception as e:
            print(f"❌ Failed to stop Twin Registry Integration: {e}")
            raise
    
    async def start_discovery(self):
        """Start automatic twin discovery"""
        try:
            if self.discovery_active:
                print("⚠️  Discovery already active")
                return
            
            self.discovery_active = True
            self.discovery_task = asyncio.create_task(self._discovery_loop())
            print("🔍 Twin discovery started")
            
        except Exception as e:
            print(f"❌ Failed to start discovery: {e}")
            self.discovery_active = False
    
    async def stop_discovery(self):
        """Stop automatic twin discovery"""
        try:
            if not self.discovery_active:
                return
            
            self.discovery_active = False
            
            if self.discovery_task and not self.discovery_task.done():
                self.discovery_task.cancel()
                try:
                    await self.discovery_task
                except asyncio.CancelledError:
                    pass
            
            print("🔍 Twin discovery stopped")
            
        except Exception as e:
            print(f"❌ Failed to stop discovery: {e}")
    
    async def _discovery_loop(self):
        """Main discovery loop"""
        try:
            while self.discovery_active:
                await self._perform_discovery()
                await asyncio.sleep(self.config.discovery_interval_minutes * 60)
                
        except asyncio.CancelledError:
            print("🔍 Discovery loop cancelled")
        except Exception as e:
            print(f"❌ Discovery loop error: {e}")
            self.discovery_active = False
    
    async def _perform_discovery(self):
        """Perform a single discovery cycle"""
        try:
            start_time = datetime.now()
            self.metrics.discovery_attempts += 1
            
            print(f"🔍 Performing twin discovery (attempt {self.metrics.discovery_attempts})")
            
            # Simulate twin discovery from registry
            # In practice, this would query the actual twin registry
            discovered_twins = await self._discover_twins_from_registry()
            
            # Process discovered twins
            for twin in discovered_twins:
                await self._process_discovered_twin(twin)
            
            # Update discovery metrics
            discovery_time = (datetime.now() - start_time).total_seconds()
            self.metrics.discovery_time = discovery_time
            self.last_discovery = datetime.now()
            
            print(f"✅ Discovery completed: {len(discovered_twins)} twins found in {discovery_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Discovery failed: {e}")
            self.metrics.discovery_failures += 1
    
    async def _discover_twins_from_registry(self) -> List[Dict[str, Any]]:
        """Discover twins from the registry service"""
        try:
            # Simulate registry query
            # In practice, this would use the actual registry service
            
            # Generate mock twin data for demonstration
            mock_twins = []
            for i in range(5):  # Simulate finding 5 twins
                twin = {
                    'twin_id': f"twin_{uuid.uuid4().hex[:8]}",
                    'name': f"Digital Twin {i+1}",
                    'type': 'manufacturing',
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'metadata': {
                        'location': f'Factory {i+1}',
                        'capabilities': ['sensor_data', 'process_control'],
                        'federated_learning_enabled': True
                    }
                }
                mock_twins.append(twin)
            
            return mock_twins
            
        except Exception as e:
            print(f"❌ Registry discovery failed: {e}")
            return []
    
    async def _process_discovered_twin(self, twin: Dict[str, Any]):
        """Process a discovered twin"""
        try:
            twin_id = twin['twin_id']
            
            # Check if twin is already known
            if twin_id in self.discovered_twins:
                # Update existing twin
                await self._update_twin_metadata(twin_id, twin)
            else:
                # Add new twin
                await self._add_discovered_twin(twin)
            
            # Cache metadata if enabled
            if self.config.cache_enabled:
                await self._cache_twin_metadata(twin_id, twin)
            
        except Exception as e:
            print(f"❌ Failed to process twin {twin.get('twin_id', 'unknown')}: {e}")
    
    async def _add_discovered_twin(self, twin: Dict[str, Any]):
        """Add a newly discovered twin"""
        try:
            twin_id = twin['twin_id']
            self.discovered_twins[twin_id] = twin
            self.metrics.twins_discovered += 1
            
            print(f"🆕 New twin discovered: {twin.get('name', twin_id)}")
            
            # Validate metadata
            if self.config.metadata_validation_enabled:
                validation_result = await self._validate_twin_metadata(twin)
                if not validation_result['valid']:
                    print(f"⚠️  Twin {twin_id} metadata validation failed: {validation_result['errors']}")
            
        except Exception as e:
            print(f"❌ Failed to add discovered twin: {e}")
    
    async def _update_twin_metadata(self, twin_id: str, twin: Dict[str, Any]):
        """Update existing twin metadata"""
        try:
            old_twin = self.discovered_twins[twin_id]
            self.discovered_twins[twin_id] = twin
            
            # Check for significant changes
            if old_twin.get('status') != twin.get('status'):
                print(f"🔄 Twin {twin_id} status changed: {old_twin.get('status')} → {twin.get('status')}")
            
            if old_twin.get('updated_at') != twin.get('updated_at'):
                print(f"🔄 Twin {twin_id} metadata updated")
            
        except Exception as e:
            print(f"❌ Failed to update twin metadata: {e}")
    
    async def _validate_twin_metadata(self, twin: Dict[str, Any]) -> Dict[str, Any]:
        """Validate twin metadata against required fields"""
        try:
            errors = []
            
            # Check required fields
            for field in self.config.required_metadata_fields:
                if field not in twin:
                    errors.append(f"Missing required field: {field}")
                elif twin[field] is None:
                    errors.append(f"Required field is null: {field}")
            
            # Check metadata structure
            if 'metadata' not in twin:
                errors.append("Missing metadata section")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {e}"]
            }
    
    async def _cache_twin_metadata(self, twin_id: str, twin: Dict[str, Any]):
        """Cache twin metadata"""
        try:
            if not self.config.cache_enabled:
                return
            
            # Add to cache with TTL
            cache_entry = {
                'data': twin,
                'cached_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=self.config.metadata_cache_ttl_hours)
            }
            
            self.metadata_cache[twin_id] = cache_entry
            self.metrics.cache_size = len(self.metadata_cache)
            
        except Exception as e:
            print(f"⚠️  Failed to cache twin metadata: {e}")
    
    async def start_health_monitoring(self):
        """Start health monitoring for discovered twins"""
        try:
            if self.health_monitoring_active:
                print("⚠️  Health monitoring already active")
                return
            
            self.health_monitoring_active = True
            self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
            print("💚 Twin health monitoring started")
            
        except Exception as e:
            print(f"❌ Failed to start health monitoring: {e}")
            self.health_monitoring_active = False
    
    async def stop_health_monitoring(self):
        """Stop health monitoring"""
        try:
            if not self.health_monitoring_active:
                return
            
            self.health_monitoring_active = False
            
            if self.health_check_task and not self.health_check_task.done():
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            print("💚 Twin health monitoring stopped")
            
        except Exception as e:
            print(f"❌ Failed to stop health monitoring: {e}")
    
    async def _health_monitoring_loop(self):
        """Main health monitoring loop"""
        try:
            while self.health_monitoring_active:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval_minutes * 60)
                
        except asyncio.CancelledError:
            print("💚 Health monitoring loop cancelled")
        except Exception as e:
            print(f"❌ Health monitoring loop error: {e}")
            self.health_monitoring_active = False
    
    async def _perform_health_checks(self):
        """Perform health checks for all discovered twins"""
        try:
            start_time = datetime.now()
            self.metrics.health_checks_performed += 1
            
            print(f"💚 Performing health checks for {len(self.discovered_twins)} twins")
            
            # Check health for each twin
            for twin_id in list(self.discovered_twins.keys()):
                try:
                    health_score = await self._check_twin_health(twin_id)
                    self.health_scores[twin_id] = health_score
                    
                    # Check if health score is below threshold
                    if health_score < self.config.min_health_score:
                        print(f"⚠️  Twin {twin_id} health score low: {health_score:.2f}")
                        
                except Exception as e:
                    print(f"❌ Health check failed for twin {twin_id}: {e}")
                    self.metrics.health_check_failures += 1
            
            # Calculate average health score
            if self.health_scores:
                self.metrics.average_health_score = sum(self.health_scores.values()) / len(self.health_scores)
            
            # Update health check metrics
            health_check_time = (datetime.now() - start_time).total_seconds()
            self.metrics.health_check_time = health_check_time
            
            print(f"✅ Health checks completed in {health_check_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Health checks failed: {e}")
            self.metrics.health_check_failures += 1
    
    async def _check_twin_health(self, twin_id: str) -> float:
        """Check health of a specific twin"""
        try:
            # Simulate health check
            # In practice, this would check actual twin health metrics
            
            # Generate health score based on twin status and metadata
            twin = self.discovered_twins.get(twin_id, {})
            
            # Base health score
            health_score = 0.8  # Default good health
            
            # Adjust based on status
            status = twin.get('status', 'unknown')
            if status == 'active':
                health_score += 0.1
            elif status == 'inactive':
                health_score -= 0.2
            elif status == 'error':
                health_score -= 0.5
            
            # Adjust based on metadata freshness
            updated_at = twin.get('updated_at')
            if updated_at:
                try:
                    last_update = datetime.fromisoformat(updated_at)
                    hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
                    
                    if hours_since_update < 1:
                        health_score += 0.1
                    elif hours_since_update > 24:
                        health_score -= 0.3
                        
                except ValueError:
                    pass
            
            # Ensure health score is between 0 and 1
            health_score = max(0.0, min(1.0, health_score))
            
            return health_score
            
        except Exception as e:
            print(f"⚠️  Health check calculation failed for twin {twin_id}: {e}")
            return 0.5  # Default neutral health score
    
    async def get_twin_info(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific twin"""
        try:
            # Check cache first
            if self.config.cache_enabled and twin_id in self.metadata_cache:
                cache_entry = self.metadata_cache[twin_id]
                
                # Check if cache is still valid
                if datetime.now() < cache_entry['expires_at']:
                    self.metrics.cache_hits += 1
                    return cache_entry['data']
                else:
                    # Remove expired cache entry
                    del self.metadata_cache[twin_id]
                    self.metrics.cache_evictions += 1
            
            # Check discovered twins
            if twin_id in self.discovered_twins:
                self.metrics.cache_misses += 1
                return self.discovered_twins[twin_id]
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get twin info: {e}")
            return None
    
    async def get_all_twins(self) -> List[Dict[str, Any]]:
        """Get all discovered twins"""
        try:
            return list(self.discovered_twins.values())
            
        except Exception as e:
            print(f"❌ Failed to get all twins: {e}")
            return []
    
    async def get_twins_by_type(self, twin_type: str) -> List[Dict[str, Any]]:
        """Get twins filtered by type"""
        try:
            return [
                twin for twin in self.discovered_twins.values()
                if twin.get('type') == twin_type
            ]
            
        except Exception as e:
            print(f"❌ Failed to get twins by type: {e}")
            return []
    
    async def get_twins_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get twins filtered by status"""
        try:
            return [
                twin for twin in self.discovered_twins.values()
                if twin.get('status') == status
            ]
            
        except Exception as e:
            print(f"❌ Failed to get twins by status: {e}")
            return []
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and metrics"""
        try:
            return {
                'discovery_active': self.discovery_active,
                'health_monitoring_active': self.health_monitoring_active,
                'last_discovery': self.last_discovery.isoformat() if self.last_discovery else None,
                'discovered_twins_count': len(self.discovered_twins),
                'registered_twins_count': len(self.registered_twins),
                'cache_size': len(self.metadata_cache),
                'metrics': self.metrics.__dict__,
                'health_scores': self.health_scores
            }
            
        except Exception as e:
            print(f"❌ Failed to get integration status: {e}")
            return {'error': str(e)}
    
    async def clear_cache(self):
        """Clear the metadata cache"""
        try:
            self.metadata_cache.clear()
            self.metrics.cache_size = 0
            self.metrics.cache_evictions += len(self.metadata_cache)
            print("🗑️  Metadata cache cleared")
            
        except Exception as e:
            print(f"❌ Failed to clear cache: {e}")
    
    async def reset_metrics(self):
        """Reset integration metrics"""
        try:
            self.metrics = TwinRegistryMetrics()
            print("🔄 Integration metrics reset")
            
        except Exception as e:
            print(f"❌ Failed to reset metrics: {e}")

