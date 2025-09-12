"""
Integration Service for Physics Modeling
=======================================

Provides comprehensive integration capabilities for physics modeling,
enabling cross-module connectivity and external system integration.

Features:
- Cross-module data flow management
- External system integration
- Data transformation and mapping
- Integration monitoring and health checks
- Event-driven integration patterns
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

# Import physics modeling components
from ..models.physics_modeling_registry import PhysicsModelingRegistry
from ..models.physics_modeling_metrics import PhysicsModelingMetrics
from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository

logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Integration type enumeration."""
    DATA_SYNC = "data_sync"
    EVENT_DRIVEN = "event_driven"
    API_INTEGRATION = "api_integration"
    FILE_TRANSFER = "file_transfer"
    DATABASE_SYNC = "database_sync"
    MESSAGE_QUEUE = "message_queue"


class IntegrationStatus(Enum):
    """Integration status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    MAINTENANCE = "maintenance"


class IntegrationDirection(Enum):
    """Integration direction enumeration."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class IntegrationEndpoint:
    """Integration endpoint configuration."""
    
    def __init__(
        self,
        endpoint_id: str,
        name: str,
        url: str,
        integration_type: IntegrationType,
        direction: IntegrationDirection,
        authentication: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_count: int = 3
    ):
        self.endpoint_id = endpoint_id
        self.name = name
        self.url = url
        self.integration_type = integration_type
        self.direction = direction
        self.authentication = authentication or {}
        self.headers = headers or {}
        self.timeout = timeout
        self.retry_count = retry_count
        self.status = IntegrationStatus.INACTIVE
        self.last_connection = None
        self.connection_count = 0
        self.error_count = 0
        self.last_error = None


class DataTransformation:
    """Data transformation configuration."""
    
    def __init__(
        self,
        transformation_id: str,
        name: str,
        source_format: str,
        target_format: str,
        transformation_rules: Dict[str, Any],
        validation_rules: Optional[List[str]] = None
    ):
        self.transformation_id = transformation_id
        self.name = name
        self.source_format = source_format
        self.target_format = target_format
        self.transformation_rules = transformation_rules
        self.validation_rules = validation_rules or []
        self.created_at = datetime.now()
        self.last_used = None
        self.usage_count = 0


class IntegrationService:
    """
    Comprehensive integration service for physics modeling.
    
    Provides:
    - Cross-module data flow management
    - External system integration
    - Data transformation and mapping
    - Integration monitoring and health checks
    - Event-driven integration patterns
    """

    def __init__(
        self,
        registry_repo: Optional[PhysicsModelingRegistryRepository] = None,
        metrics_repo: Optional[PhysicsModelingMetricsRepository] = None
    ):
        """Initialize the integration service."""
        self.registry_repo = registry_repo
        self.metrics_repo = metrics_repo
        
        # Initialize repositories if not provided
        if not self.registry_repo:
            from ..repositories.physics_modeling_registry_repository import PhysicsModelingRegistryRepository
            self.registry_repo = PhysicsModelingRegistryRepository()
        
        if not self.metrics_repo:
            from ..repositories.physics_modeling_metrics_repository import PhysicsModelingMetricsRepository
            self.metrics_repo = PhysicsModelingMetricsRepository()
        
        # Integration management
        self.endpoints: Dict[str, IntegrationEndpoint] = {}
        self.transformations: Dict[str, DataTransformation] = {}
        self.data_flows: Dict[str, Dict[str, Any]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Health monitoring
        self.health_metrics = {
            'total_endpoints': 0,
            'active_endpoints': 0,
            'error_endpoints': 0,
            'total_integrations': 0,
            'successful_integrations': 0,
            'failed_integrations': 0
        }
        
        logger.info("Integration service initialized")

    async def initialize(self) -> bool:
        """Initialize the integration service."""
        try:
            # Initialize repositories
            await self.registry_repo.initialize()
            await self.metrics_repo.initialize()
            
            # Initialize default integrations
            await self._initialize_default_integrations()
            
            logger.info("✅ Integration service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize integration service: {e}")
            return False

    async def register_endpoint(
        self,
        name: str,
        url: str,
        integration_type: IntegrationType,
        direction: IntegrationDirection,
        authentication: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_count: int = 3
    ) -> str:
        """
        Register a new integration endpoint.
        
        Args:
            name: Endpoint name
            url: Endpoint URL
            integration_type: Type of integration
            direction: Integration direction
            authentication: Authentication configuration
            headers: Custom headers
            timeout: Connection timeout
            retry_count: Retry attempts
            
        Returns:
            Endpoint ID
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            endpoint_id = str(uuid.uuid4())
            
            endpoint = IntegrationEndpoint(
                endpoint_id=endpoint_id,
                name=name,
                url=url,
                integration_type=integration_type,
                direction=direction,
                authentication=authentication,
                headers=headers,
                timeout=timeout,
                retry_count=retry_count
            )
            
            self.endpoints[endpoint_id] = endpoint
            self.health_metrics['total_endpoints'] += 1
            
            # Create registry record
            await self._create_integration_registry_record(endpoint)
            
            logger.info(f"✅ Integration endpoint {name} registered successfully")
            return endpoint_id
            
        except Exception as e:
            logger.error(f"Failed to register integration endpoint: {e}")
            raise

    async def connect_endpoint(self, endpoint_id: str) -> bool:
        """
        Connect to an integration endpoint.
        
        Args:
            endpoint_id: Endpoint identifier
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if endpoint_id not in self.endpoints:
                logger.warning(f"Endpoint {endpoint_id} not found")
                return False
            
            endpoint = self.endpoints[endpoint_id]
            endpoint.status = IntegrationStatus.CONNECTING
            
            # Simulate connection attempt
            await asyncio.sleep(0.1)  # Simulate connection time
            
            # Update endpoint status
            endpoint.status = IntegrationStatus.ACTIVE
            endpoint.last_connection = datetime.now()
            endpoint.connection_count += 1
            
            # Update health metrics
            self.health_metrics['active_endpoints'] += 1
            if endpoint.status == IntegrationStatus.ERROR:
                self.health_metrics['error_endpoints'] -= 1
            
            logger.info(f"✅ Connected to endpoint {endpoint.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to endpoint {endpoint_id}: {e}")
            if endpoint_id in self.endpoints:
                endpoint = self.endpoints[endpoint_id]
                endpoint.status = IntegrationStatus.ERROR
                endpoint.error_count += 1
                endpoint.last_error = str(e)
                self.health_metrics['error_endpoints'] += 1
            return False

    async def disconnect_endpoint(self, endpoint_id: str) -> bool:
        """
        Disconnect from an integration endpoint.
        
        Args:
            endpoint_id: Endpoint identifier
            
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if endpoint_id not in self.endpoints:
                logger.warning(f"Endpoint {endpoint_id} not found")
                return False
            
            endpoint = self.endpoints[endpoint_id]
            endpoint.status = IntegrationStatus.DISCONNECTED
            
            # Update health metrics
            if endpoint.status == IntegrationStatus.ACTIVE:
                self.health_metrics['active_endpoints'] -= 1
            
            logger.info(f"✅ Disconnected from endpoint {endpoint.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect from endpoint {endpoint_id}: {e}")
            return False

    async def register_data_transformation(
        self,
        name: str,
        source_format: str,
        target_format: str,
        transformation_rules: Dict[str, Any],
        validation_rules: Optional[List[str]] = None
    ) -> str:
        """
        Register a new data transformation.
        
        Args:
            name: Transformation name
            source_format: Source data format
            target_format: Target data format
            transformation_rules: Transformation rules
            validation_rules: Validation rules
            
        Returns:
            Transformation ID
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            transformation_id = str(uuid.uuid4())
            
            transformation = DataTransformation(
                transformation_id=transformation_id,
                name=name,
                source_format=source_format,
                target_format=target_format,
                transformation_rules=transformation_rules,
                validation_rules=validation_rules
            )
            
            self.transformations[transformation_id] = transformation
            
            logger.info(f"✅ Data transformation {name} registered successfully")
            return transformation_id
            
        except Exception as e:
            logger.error(f"Failed to register data transformation: {e}")
            raise

    async def transform_data(
        self,
        transformation_id: str,
        source_data: Any,
        source_format: str
    ) -> Optional[Any]:
        """
        Transform data using a registered transformation.
        
        Args:
            transformation_id: Transformation identifier
            source_data: Source data to transform
            source_format: Source data format
            
        Returns:
            Transformed data or None if transformation failed
        """
        try:
            if transformation_id not in self.transformations:
                logger.warning(f"Transformation {transformation_id} not found")
                return None
            
            transformation = self.transformations[transformation_id]
            
            # Validate source format
            if transformation.source_format != source_format:
                logger.warning(f"Source format mismatch: expected {transformation.source_format}, got {source_format}")
                return None
            
            # Apply transformation rules
            transformed_data = await self._apply_transformation_rules(
                transformation.transformation_rules,
                source_data
            )
            
            # Update transformation usage
            transformation.last_used = datetime.now()
            transformation.usage_count += 1
            
            # Record transformation metrics
            await self._record_transformation_metrics(transformation_id, True, "success")
            
            logger.info(f"✅ Data transformed successfully using {transformation.name}")
            return transformed_data
            
        except Exception as e:
            logger.error(f"Failed to transform data: {e}")
            
            # Record transformation metrics
            if transformation_id in self.transformations:
                await self._record_transformation_metrics(transformation_id, False, str(e))
            
            return None

    async def create_data_flow(
        self,
        name: str,
        source_endpoint_id: str,
        target_endpoint_id: str,
        transformation_id: Optional[str] = None,
        schedule: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new data flow between endpoints.
        
        Args:
            name: Data flow name
            source_endpoint_id: Source endpoint ID
            target_endpoint_id: Target endpoint ID
            transformation_id: Optional transformation ID
            schedule: Optional schedule (cron format)
            filters: Optional data filters
            
        Returns:
            Data flow ID
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            flow_id = str(uuid.uuid4())
            
            # Validate endpoints
            if source_endpoint_id not in self.endpoints:
                raise ValueError(f"Source endpoint {source_endpoint_id} not found")
            
            if target_endpoint_id not in self.endpoints:
                raise ValueError(f"Target endpoint {target_endpoint_id} not found")
            
            # Validate transformation if provided
            if transformation_id and transformation_id not in self.transformations:
                raise ValueError(f"Transformation {transformation_id} not found")
            
            data_flow = {
                'flow_id': flow_id,
                'name': name,
                'source_endpoint_id': source_endpoint_id,
                'target_endpoint_id': target_endpoint_id,
                'transformation_id': transformation_id,
                'schedule': schedule,
                'filters': filters or {},
                'status': 'active',
                'created_at': datetime.now(),
                'last_execution': None,
                'execution_count': 0,
                'success_count': 0,
                'error_count': 0
            }
            
            self.data_flows[flow_id] = data_flow
            self.health_metrics['total_integrations'] += 1
            
            logger.info(f"✅ Data flow {name} created successfully")
            return flow_id
            
        except Exception as e:
            logger.error(f"Failed to create data flow: {e}")
            raise

    async def execute_data_flow(self, flow_id: str, data: Any) -> bool:
        """
        Execute a data flow.
        
        Args:
            flow_id: Data flow identifier
            data: Data to flow
            
        Returns:
            True if execution successful, False otherwise
        """
        try:
            if flow_id not in self.data_flows:
                logger.warning(f"Data flow {flow_id} not found")
                return False
            
            flow = self.data_flows[flow_id]
            flow['last_execution'] = datetime.now()
            flow['execution_count'] += 1
            
            # Get endpoints
            source_endpoint = self.endpoints[flow['source_endpoint_id']]
            target_endpoint = self.endpoints[flow['target_endpoint_id']]
            
            # Apply filters
            filtered_data = await self._apply_data_filters(data, flow['filters'])
            
            # Transform data if transformation specified
            if flow['transformation_id']:
                transformed_data = await self.transform_data(
                    flow['transformation_id'],
                    filtered_data,
                    'raw'
                )
                if transformed_data is None:
                    flow['error_count'] += 1
                    self.health_metrics['failed_integrations'] += 1
                    return False
            else:
                transformed_data = filtered_data
            
            # Send data to target endpoint
            success = await self._send_data_to_endpoint(target_endpoint, transformed_data)
            
            if success:
                flow['success_count'] += 1
                self.health_metrics['successful_integrations'] += 1
                logger.info(f"✅ Data flow {flow['name']} executed successfully")
            else:
                flow['error_count'] += 1
                self.health_metrics['failed_integrations'] += 1
                logger.error(f"❌ Data flow {flow['name']} execution failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to execute data flow {flow_id}: {e}")
            if flow_id in self.data_flows:
                flow = self.data_flows[flow_id]
                flow['error_count'] += 1
                self.health_metrics['failed_integrations'] += 1
            return False

    async def register_event_handler(
        self,
        event_type: str,
        handler: Callable,
        priority: int = 0
    ) -> str:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Event handler function
            priority: Handler priority (higher = higher priority)
            
        Returns:
            Handler ID
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            handler_id = str(uuid.uuid4())
            
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            
            # Add handler with priority
            self.event_handlers[event_type].append({
                'handler_id': handler_id,
                'handler': handler,
                'priority': priority,
                'registered_at': datetime.now()
            })
            
            # Sort by priority (highest first)
            self.event_handlers[event_type].sort(key=lambda x: x['priority'], reverse=True)
            
            logger.info(f"✅ Event handler registered for {event_type}")
            return handler_id
            
        except Exception as e:
            logger.error(f"Failed to register event handler: {e}")
            raise

    async def trigger_event(self, event_type: str, event_data: Any) -> bool:
        """
        Trigger an event and execute registered handlers.
        
        Args:
            event_type: Type of event to trigger
            event_data: Event data
            
        Returns:
            True if event handled successfully, False otherwise
        """
        try:
            if event_type not in self.event_handlers:
                logger.debug(f"No handlers registered for event type {event_type}")
                return True
            
            handlers = self.event_handlers[event_type]
            success_count = 0
            total_handlers = len(handlers)
            
            for handler_info in handlers:
                try:
                    handler = handler_info['handler']
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data)
                    else:
                        handler(event_data)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Event handler {handler_info['handler_id']} failed: {e}")
            
            success_rate = success_count / total_handlers if total_handlers > 0 else 0
            
            # Record event metrics
            await self._record_event_metrics(event_type, success_rate, total_handlers)
            
            logger.info(f"✅ Event {event_type} triggered: {success_count}/{total_handlers} handlers successful")
            return success_rate >= 0.8  # 80% success threshold
            
        except Exception as e:
            logger.error(f"Failed to trigger event {event_type}: {e}")
            return False

    async def get_integration_health(self) -> Dict[str, Any]:
        """
        Get integration service health status.
        
        Returns:
            Health status information
        """
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Calculate endpoint health
            endpoint_health = {}
            for endpoint_id, endpoint in self.endpoints.items():
                endpoint_health[endpoint_id] = {
                    'name': endpoint.name,
                    'status': endpoint.status.value,
                    'last_connection': endpoint.last_connection.isoformat() if endpoint.last_connection else None,
                    'connection_count': endpoint.connection_count,
                    'error_count': endpoint.error_count,
                    'last_error': endpoint.last_error
                }
            
            # Calculate data flow health
            flow_health = {}
            for flow_id, flow in self.data_flows.items():
                flow_health[flow_id] = {
                    'name': flow['name'],
                    'status': flow['status'],
                    'execution_count': flow['execution_count'],
                    'success_count': flow['success_count'],
                    'error_count': flow['error_count'],
                    'success_rate': (flow['success_count'] / flow['execution_count'] * 100) if flow['execution_count'] > 0 else 0
                }
            
            health_status = {
                'service_status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'health_metrics': self.health_metrics,
                'endpoint_health': endpoint_health,
                'flow_health': flow_health,
                'total_event_handlers': sum(len(handlers) for handlers in self.event_handlers.values()),
                'total_transformations': len(self.transformations)
            }
            
            # Determine overall service status
            if self.health_metrics['error_endpoints'] > 0:
                health_status['service_status'] = 'degraded'
            if self.health_metrics['error_endpoints'] > self.health_metrics['total_endpoints'] * 0.5:
                health_status['service_status'] = 'unhealthy'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to get integration health: {e}")
            return {'service_status': 'error', 'error': str(e)}

    async def _initialize_default_integrations(self) -> None:
        """Initialize default integration configurations."""
        try:
            # Register default endpoints
            await self.register_endpoint(
                name="Twin Registry",
                url="internal://twin_registry",
                integration_type=IntegrationType.DATABASE_SYNC,
                direction=IntegrationDirection.BIDIRECTIONAL
            )
            
            await self.register_endpoint(
                name="Knowledge Graph",
                url="internal://kg_neo4j",
                integration_type=IntegrationType.DATA_SYNC,
                direction=IntegrationDirection.BIDIRECTIONAL
            )
            
            await self.register_endpoint(
                name="AI RAG System",
                url="internal://ai_rag",
                integration_type=IntegrationType.API_INTEGRATION,
                direction=IntegrationDirection.BIDIRECTIONAL
            )
            
            # Register default transformations
            await self.register_data_transformation(
                name="Physics Model to Twin",
                source_format="physics_model",
                target_format="twin_data",
                transformation_rules={
                    'model_id': 'twin_registry_id',
                    'model_name': 'twin_name',
                    'model_type': 'twin_category'
                }
            )
            
            await self.register_data_transformation(
                name="Simulation Results to Metrics",
                source_format="simulation_results",
                target_format="metrics_data",
                transformation_rules={
                    'execution_time': 'metric_value',
                    'simulation_id': 'metric_metadata.simulation_id',
                    'twin_id': 'metric_metadata.twin_id'
                }
            )
            
            logger.info("✅ Default integrations initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default integrations: {e}")

    async def _create_integration_registry_record(self, endpoint: IntegrationEndpoint) -> None:
        """Create a record in the physics modeling registry."""
        try:
            # Create registry record
            registry_record = PhysicsModelingRegistry(
                registry_id=None,  # Will be set by repository
                twin_registry_id=None,  # Not applicable for integrations
                model_name=f"integration_{endpoint.name}",
                model_type="integration",
                model_version="1.0.0",
                model_description=f"Integration endpoint: {endpoint.name}",
                model_status="active",
                model_parameters=json.dumps({
                    'url': endpoint.url,
                    'integration_type': endpoint.integration_type.value,
                    'direction': endpoint.direction.value,
                    'timeout': endpoint.timeout,
                    'retry_count': endpoint.retry_count
                }),
                model_metadata={
                    'endpoint_id': endpoint.endpoint_id,
                    'integration_type': endpoint.integration_type.value,
                    'direction': endpoint.direction.value,
                    'created_at': datetime.now().isoformat()
                },
                compliance_score=90.0,  # Default compliance score
                security_score=85.0,   # Default security score
                quality_score=80.0,    # Default quality score
                performance_score=75.0, # Default performance score
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to database
            await self.registry_repo.create(registry_record)
            
        except Exception as e:
            logger.error(f"Failed to create integration registry record: {e}")

    async def _apply_transformation_rules(
        self,
        transformation_rules: Dict[str, Any],
        source_data: Any
    ) -> Any:
        """Apply transformation rules to source data."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            if isinstance(source_data, dict):
                transformed_data = {}
                for target_key, source_key in transformation_rules.items():
                    if source_key in source_data:
                        transformed_data[target_key] = source_data[source_key]
                    else:
                        transformed_data[target_key] = None
                return transformed_data
            else:
                # For non-dict data, return as-is
                return source_data
                
        except Exception as e:
            logger.error(f"Failed to apply transformation rules: {e}")
            return source_data

    async def _apply_data_filters(
        self,
        data: Any,
        filters: Dict[str, Any]
    ) -> Any:
        """Apply data filters to input data."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            if not filters or not isinstance(data, dict):
                return data
            
            filtered_data = {}
            for key, value in data.items():
                if key in filters:
                    filter_rule = filters[key]
                    if isinstance(filter_rule, dict):
                        # Apply filter rule
                        if 'min' in filter_rule and value < filter_rule['min']:
                            continue
                        if 'max' in filter_rule and value > filter_rule['max']:
                            continue
                        if 'allowed_values' in filter_rule and value not in filter_rule['allowed_values']:
                            continue
                    
                    filtered_data[key] = value
                else:
                    # Include all keys not in filters
                    filtered_data[key] = value
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Failed to apply data filters: {e}")
            return data

    async def _send_data_to_endpoint(
        self,
        endpoint: IntegrationEndpoint,
        data: Any
    ) -> bool:
        """Send data to a specific endpoint."""
        try:
            await asyncio.sleep(0)  # Pure async
            
            # Simulate data sending
            if endpoint.integration_type == IntegrationType.DATABASE_SYNC:
                # Simulate database sync
                await asyncio.sleep(0.05)
            elif endpoint.integration_type == IntegrationType.API_INTEGRATION:
                # Simulate API call
                await asyncio.sleep(0.1)
            elif endpoint.integration_type == IntegrationType.FILE_TRANSFER:
                # Simulate file transfer
                await asyncio.sleep(0.2)
            else:
                # Default simulation
                await asyncio.sleep(0.1)
            
            # Simulate success (90% success rate)
            import random
            success = random.random() > 0.1
            
            if not success:
                endpoint.error_count += 1
                endpoint.last_error = "Simulated transmission error"
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send data to endpoint {endpoint.name}: {e}")
            endpoint.error_count += 1
            endpoint.last_error = str(e)
            return False

    async def _record_transformation_metrics(
        self,
        transformation_id: str,
        success: bool,
        details: str
    ) -> None:
        """Record transformation metrics."""
        try:
            # Create metrics record
            metrics = PhysicsModelingMetrics(
                physics_modeling_id=None,  # Will be set by repository
                metric_name="data_transformation",
                metric_value=1.0 if success else 0.0,
                metric_unit="count",
                metric_type="transformation",
                metric_category="data_integration",
                metric_timestamp=datetime.now(),
                metric_metadata={
                    'transformation_id': transformation_id,
                    'success': success,
                    'details': details
                }
            )
            
            # Save to database
            await self.metrics_repo.create(metrics)
            
        except Exception as e:
            logger.error(f"Failed to record transformation metrics: {e}")

    async def _record_event_metrics(
        self,
        event_type: str,
        success_rate: float,
        total_handlers: int
    ) -> None:
        """Record event metrics."""
        try:
            # Create metrics record
            metrics = PhysicsModelingMetrics(
                physics_modeling_id=None,  # Will be set by repository
                metric_name="event_handling",
                metric_value=success_rate,
                metric_unit="percentage",
                metric_type="event",
                metric_category="integration",
                metric_timestamp=datetime.now(),
                metric_metadata={
                    'event_type': event_type,
                    'success_rate': success_rate,
                    'total_handlers': total_handlers
                }
            )
            
            # Save to database
            await self.metrics_repo.create(metrics)
            
        except Exception as e:
            logger.error(f"Failed to record event metrics: {e}")

    async def close(self) -> None:
        """Close the integration service."""
        try:
            # Disconnect all endpoints
            for endpoint_id in list(self.endpoints.keys()):
                await self.disconnect_endpoint(endpoint_id)
            
            if self.registry_repo:
                await self.registry_repo.close()
            if self.metrics_repo:
                await self.metrics_repo.close()
            
            logger.info("✅ Integration service closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing integration service: {e}")





