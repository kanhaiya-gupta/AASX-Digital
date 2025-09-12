"""
Module Integrations for AI RAG

This module handles integration with other modules in the system:
- AASX Integration: File processing coordination
- Twin Registry Integration: Health score and performance monitoring
- KG Neo4j Integration: Knowledge graph enhancement coordination
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from ..events.event_types import (
    BaseEvent, EventPriority, EventStatus, EventCategory,
    IntegrationEvent, IntegrationSuccessEvent, IntegrationFailureEvent
)
from ..events.event_bus import EventBus
from ..events.event_logger import EventLogger


class IntegrationStatus(str, Enum):
    """Integration status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


class IntegrationType(str, Enum):
    """Integration type enumeration"""
    AASX = "aasx"
    TWIN_REGISTRY = "twin_registry"
    KG_NEO4J = "kg_neo4j"
    EXTERNAL_API = "external_api"


@dataclass
class IntegrationMetrics:
    """Integration performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    last_request_time: Optional[datetime] = None
    error_rate: float = 0.0
    throughput_per_minute: float = 0.0


class IntegrationConfig(BaseModel):
    """Configuration for module integrations"""
    integration_type: IntegrationType
    enabled: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 1
    batch_size: int = 100
    health_check_interval_seconds: int = 60
    performance_thresholds: Dict[str, float] = Field(default_factory=dict)
    
    # Module-specific settings
    aasx_settings: Dict[str, Any] = Field(default_factory=dict)
    twin_registry_settings: Dict[str, Any] = Field(default_factory=dict)
    kg_neo4j_settings: Dict[str, Any] = Field(default_factory=dict)


class AASXIntegration:
    """Integration with AASX module for file processing coordination"""
    
    def __init__(self, config: IntegrationConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.metrics = IntegrationMetrics()
        self.status = IntegrationStatus.PENDING
        
    async def process_aasx_file(self, file_path: str, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process AASX file and coordinate with AI RAG processing"""
        try:
            self.status = IntegrationStatus.IN_PROGRESS
            start_time = datetime.now()
            
            # Publish AASX integration event
            event = IntegrationEvent(
                event_id=f"aasx_integration_{datetime.now().timestamp()}",
                event_type="aasx_integration",
                event_category=EventCategory.INTEGRATION,
                priority=EventPriority.HIGH,
                source="ai_rag_integration",
                target="aasx_module",
                metadata={
                    "aasx_file_path": file_path,
                    "aasx_metadata": file_metadata,
                    "integration_status": "processing"
                }
            )
            await self.event_bus.publish(event)
            
            # Simulate AASX processing coordination
            # In real implementation, this would call AASX module APIs
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Update metrics
            self._update_metrics(start_time, True)
            
            result = {
                "status": "success",
                "aasx_file_id": f"aasx_{datetime.now().timestamp()}",
                "processing_metadata": file_metadata,
                "ai_rag_ready": True
            }
            
            # Publish completion event
            completion_event = IntegrationSuccessEvent(
                event_id=f"aasx_completion_{datetime.now().timestamp()}",
                event_type="aasx_integration_completed",
                event_category=EventCategory.INTEGRATION,
                priority=EventPriority.HIGH,
                source="ai_rag_integration",
                target="aasx_module",
                metadata={
                    "aasx_file_path": file_path,
                    "aasx_metadata": file_metadata,
                    "integration_status": "completed",
                    "result": result
                }
            )
            await self.event_bus.publish(completion_event)
            
            self.status = IntegrationStatus.COMPLETED
            return result
            
        except Exception as e:
            self.logger.error(f"AASX integration error: {e}")
            self._update_metrics(datetime.now(), False)
            self.status = IntegrationStatus.FAILED
            
            # Publish error event
            error_event = IntegrationFailureEvent(
                event_id=f"aasx_error_{datetime.now().timestamp()}",
                event_type="aasx_integration_failed",
                event_category=EventCategory.ERROR,
                priority=EventPriority.HIGH,
                source="ai_rag_integration",
                target="aasx_module",
                error_message=str(e),
                metadata={
                    "aasx_file_path": file_path,
                    "aasx_metadata": file_metadata,
                    "integration_status": "failed"
                }
            )
            await self.event_bus.publish(error_event)
            
            raise
    
    async def get_aasx_status(self, file_id: str) -> Dict[str, Any]:
        """Get status of AASX file processing"""
        # Simulate AASX status check
        return {
            "file_id": file_id,
            "status": "processed",
            "ai_rag_ready": True,
            "last_updated": datetime.now().isoformat()
        }
    
    def _update_metrics(self, start_time: datetime, success: bool):
        """Update integration metrics"""
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        self.metrics.average_response_time_ms = (
            (self.metrics.average_response_time_ms * (self.metrics.total_requests - 1) + response_time) 
            / self.metrics.total_requests
        )
        
        self.metrics.last_request_time = datetime.now()
        self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests


class TwinRegistryIntegration:
    """Integration with Twin Registry module for health score and performance monitoring"""
    
    def __init__(self, config: IntegrationConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.metrics = IntegrationMetrics()
        self.status = IntegrationStatus.PENDING
        
    async def sync_twin_health_scores(self, twin_ids: List[str]) -> Dict[str, Any]:
        """Synchronize twin health scores with Twin Registry"""
        try:
            self.status = IntegrationStatus.IN_PROGRESS
            start_time = datetime.now()
            
            # Publish twin registry integration event
            event = IntegrationEvent(
                event_id=f"twin_registry_sync_{datetime.now().timestamp()}",
                event_type="twin_registry_sync",
                event_category=EventCategory.INTEGRATION,
                priority=EventPriority.NORMAL,
                source="ai_rag_integration",
                target="twin_registry_module",
                metadata={
                    "twin_ids": twin_ids,
                    "sync_type": "health_scores",
                    "integration_status": "processing"
                }
            )
            await self.event_bus.publish(event)
            
            # Simulate twin registry health score sync
            # In real implementation, this would call Twin Registry module APIs
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Update metrics
            self._update_metrics(start_time, True)
            
            result = {
                "status": "success",
                "synced_twins": len(twin_ids),
                "health_scores": {twin_id: 0.85 for twin_id in twin_ids},  # Mock data
                "last_sync": datetime.now().isoformat()
            }
            
            # Publish completion event
            completion_event = IntegrationSuccessEvent(
                event_id=f"twin_registry_completion_{datetime.now().timestamp()}",
                event_type="twin_registry_sync_completed",
                event_category=EventCategory.INTEGRATION,
                priority=EventPriority.NORMAL,
                source="ai_rag_integration",
                target="twin_registry_module",
                metadata={
                    "twin_ids": twin_ids,
                    "sync_type": "health_scores",
                    "integration_status": "completed",
                    "result": result
                }
            )
            await self.event_bus.publish(completion_event)
            
            self.status = IntegrationStatus.COMPLETED
            return result
            
        except Exception as e:
            self.logger.error(f"Twin Registry integration error: {e}")
            self._update_metrics(datetime.now(), False)
            self.status = IntegrationStatus.FAILED
            
            # Publish error event
            error_event = IntegrationFailureEvent(
                event_id=f"twin_registry_error_{datetime.now().timestamp()}",
                event_type="twin_registry_sync_failed",
                event_category=EventCategory.ERROR,
                priority=EventPriority.NORMAL,
                source="ai_rag_integration",
                target="twin_registry_module",
                error_message=str(e),
                metadata={
                    "twin_ids": twin_ids,
                    "sync_type": "health_scores",
                    "integration_status": "failed"
                }
            )
            await self.event_bus.publish(error_event)
            
            raise
    
    async def get_twin_performance_metrics(self, twin_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific twin"""
        # Simulate twin performance metrics retrieval
        return {
            "twin_id": twin_id,
            "health_score": 0.85,
            "performance_metrics": {
                "response_time_ms": 150,
                "throughput_per_minute": 100,
                "error_rate": 0.02
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _update_metrics(self, start_time: datetime, success: bool):
        """Update integration metrics"""
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        self.metrics.average_response_time_ms = (
            (self.metrics.average_response_time_ms * (self.metrics.total_requests - 1) + response_time) 
            / self.metrics.total_requests
        )
        
        self.metrics.last_request_time = datetime.now()
        self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests


class KGNeo4jIntegration:
    """Integration with KG Neo4j module for knowledge graph enhancement coordination"""
    
    def __init__(self, config: IntegrationConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.metrics = IntegrationMetrics()
        self.status = IntegrationStatus.PENDING
        
    async def enhance_knowledge_graph(self, graph_id: str, enhancement_config: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate knowledge graph enhancement with KG Neo4j"""
        try:
            self.status = IntegrationStatus.IN_PROGRESS
            start_time = datetime.now()
            
            # Publish KG Neo4j integration event
            event = IntegrationEvent(
                event_id=f"kg_neo4j_enhancement_{datetime.now().timestamp()}",
                event_type="kg_neo4j_enhancement",
                event_category=EventCategory.INTEGRATION,
                priority=EventPriority.HIGH,
                source="ai_rag_integration",
                target="kg_neo4j_module",
                metadata={
                    "graph_id": graph_id,
                    "enhancement_type": "graph_enhancement",
                    "enhancement_config": enhancement_config,
                    "integration_status": "processing"
                }
            )
            await self.event_bus.publish(event)
            
            # Simulate KG Neo4j graph enhancement
            # In real implementation, this would call KG Neo4j module APIs
            await asyncio.sleep(0.2)  # Simulate processing time
            
            # Update metrics
            self._update_metrics(start_time, True)
            
            result = {
                "status": "success",
                "graph_id": graph_id,
                "enhancement_applied": True,
                "enhancement_metadata": {
                    "enhanced_nodes": 25,
                    "enhanced_relationships": 15,
                    "quality_improvement": 0.12
                },
                "completion_time": datetime.now().isoformat()
            }
            
            # Publish completion event
            completion_event = IntegrationSuccessEvent(
                event_id=f"kg_neo4j_completion_{datetime.now().timestamp()}",
                event_type="kg_neo4j_enhancement_completed",
                event_category=EventCategory.INTEGRATION,
                priority=EventPriority.HIGH,
                source="ai_rag_integration",
                target="kg_neo4j_module",
                metadata={
                    "graph_id": graph_id,
                    "enhancement_type": "graph_enhancement",
                    "enhancement_config": enhancement_config,
                    "integration_status": "completed",
                    "result": result
                }
            )
            await self.event_bus.publish(completion_event)
            
            self.status = IntegrationStatus.COMPLETED
            return result
            
        except Exception as e:
            self.logger.error(f"KG Neo4j integration error: {e}")
            self._update_metrics(datetime.now(), False)
            self.status = IntegrationStatus.FAILED
            
            # Publish error event
            error_event = IntegrationFailureEvent(
                event_id=f"kg_neo4j_error_{datetime.now().timestamp()}",
                event_type="kg_neo4j_enhancement_failed",
                event_category=EventCategory.ERROR,
                priority=EventPriority.HIGH,
                source="ai_rag_integration",
                target="kg_neo4j_module",
                error_message=str(e),
                metadata={
                    "graph_id": graph_id,
                    "enhancement_type": "graph_enhancement",
                    "enhancement_config": enhancement_config,
                    "integration_status": "failed"
                }
            )
            await self.event_bus.publish(error_event)
            
            raise
    
    async def get_graph_enhancement_status(self, graph_id: str) -> Dict[str, Any]:
        """Get status of graph enhancement process"""
        # Simulate graph enhancement status check
        return {
            "graph_id": graph_id,
            "enhancement_status": "completed",
            "enhancement_progress": 100,
            "last_updated": datetime.now().isoformat()
        }
    
    def _update_metrics(self, start_time: datetime, success: bool):
        """Update integration metrics"""
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        self.metrics.average_response_time_ms = (
            (self.metrics.average_response_time_ms * (self.metrics.total_requests - 1) + response_time) 
            / self.metrics.total_requests
        )
        
        self.metrics.last_request_time = datetime.now()
        self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests


class ModuleIntegrationManager:
    """Manages all module integrations with centralized coordination"""
    
    def __init__(self, configs: List[IntegrationConfig], event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations
        self.integrations: Dict[IntegrationType, Union[AASXIntegration, TwinRegistryIntegration, KGNeo4jIntegration]] = {}
        
        for config in configs:
            if config.integration_type == IntegrationType.AASX:
                self.integrations[config.integration_type] = AASXIntegration(config, event_bus)
            elif config.integration_type == IntegrationType.TWIN_REGISTRY:
                self.integrations[config.integration_type] = TwinRegistryIntegration(config, event_bus)
            elif config.integration_type == IntegrationType.KG_NEO4J:
                self.integrations[config.integration_type] = KGNeo4jIntegration(config, event_bus)
        
        self.logger.info(f"Initialized {len(self.integrations)} module integrations")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        status = {}
        for integration_type, integration in self.integrations.items():
            status[integration_type.value] = {
                "status": integration.status.value,
                "metrics": {
                    "total_requests": integration.metrics.total_requests,
                    "successful_requests": integration.metrics.successful_requests,
                    "failed_requests": integration.metrics.failed_requests,
                    "error_rate": integration.metrics.error_rate,
                    "average_response_time_ms": integration.metrics.average_response_time_ms
                }
            }
        return status
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all integrations"""
        health_status = {}
        for integration_type, integration in self.integrations.items():
            try:
                # Simple health check based on status
                health_status[integration_type.value] = integration.status != IntegrationStatus.FAILED
            except Exception as e:
                self.logger.error(f"Health check failed for {integration_type.value}: {e}")
                health_status[integration_type.value] = False
        
        return health_status
    
    def get_integration(self, integration_type: IntegrationType):
        """Get a specific integration by type"""
        return self.integrations.get(integration_type)
    
    async def shutdown_all(self):
        """Shutdown all integrations gracefully"""
        for integration_type, integration in self.integrations.items():
            try:
                integration.status = IntegrationStatus.DISABLED
                self.logger.info(f"Shutdown {integration_type.value} integration")
            except Exception as e:
                self.logger.error(f"Error shutting down {integration_type.value}: {e}")
