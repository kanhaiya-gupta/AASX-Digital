"""
Knowledge Graph Neo4j Module Integrations

Integration classes for connecting KG Neo4j with other modules and external systems.
Provides seamless communication and data flow between different components.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

from ..events import (
    KGNeo4jEventManager,
    EventPriority,
    GraphCreationEvent,
    Neo4jOperationEvent,
    AIInsightsEvent
)

logger = logging.getLogger(__name__)


class BaseModuleIntegration:
    """Base class for module integrations."""
    
    def __init__(self, name: str, event_manager: KGNeo4jEventManager):
        """Initialize the base integration."""
        self.name = name
        self.event_manager = event_manager
        self.is_active = False
        self.last_heartbeat = None
        self.connection_status = "disconnected"
        
        logger.info(f"Module integration {self.name} initialized")
    
    async def connect(self) -> bool:
        """Establish connection to the module."""
        try:
            self.is_active = True
            self.connection_status = "connected"
            self.last_heartbeat = datetime.now(timezone.utc)
            logger.info(f"Module integration {self.name} connected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect {self.name}: {e}")
            self.connection_status = "failed"
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the module."""
        try:
            self.is_active = False
            self.connection_status = "disconnected"
            logger.info(f"Module integration {self.name} disconnected")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect {self.name}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check integration health."""
        return {
            "name": self.name,
            "is_active": self.is_active,
            "connection_status": self.connection_status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }
    
    async def send_heartbeat(self) -> None:
        """Send heartbeat to maintain connection."""
        if self.is_active:
            self.last_heartbeat = datetime.now(timezone.utc)
            logger.debug(f"Heartbeat sent to {self.name}")


class AASXIntegration(BaseModuleIntegration):
    """Integration with AASX module for file processing workflows."""
    
    def __init__(self, event_manager: KGNeo4jEventManager):
        """Initialize AASX integration."""
        super().__init__("AASX", event_manager)
        self.processed_files = 0
        self.failed_files = 0
    
    async def process_aasx_file(self, file_id: str, file_path: str, user_id: str, org_id: str, dept_id: str) -> str:
        """Process an AASX file and create a knowledge graph."""
        try:
            logger.info(f"Processing AASX file {file_id} for graph creation")
            
            # Create graph creation event
            event_id = await self.event_manager.publish_graph_creation(
                file_id=file_id,
                graph_name=f"Graph_AASX_{file_id[:8]}",
                workflow_source="aasx_file",
                graph_config={
                    "file_path": file_path,
                    "source_module": "AASX",
                    "processing_method": "aasx_extraction"
                },
                user_id=user_id,
                org_id=org_id,
                dept_id=dept_id,
                priority=EventPriority.HIGH
            )
            
            # Simulate AASX processing workflow
            await asyncio.sleep(0.1)
            
            self.processed_files += 1
            logger.info(f"AASX file {file_id} processed successfully, event: {event_id}")
            
            return event_id
            
        except Exception as e:
            self.failed_files += 1
            error_msg = f"Failed to process AASX file {file_id}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    async def get_processing_status(self, file_id: str) -> Dict[str, Any]:
        """Get the processing status of an AASX file."""
        try:
            # Query event manager for recent events
            recent_events = await self.event_manager.get_recent_events(
                event_type="graph_creation",
                limit=100
            )
            
            # Find events for this file
            file_events = [e for e in recent_events if e.get("file_id") == file_id]
            
            if file_events:
                latest_event = file_events[-1]
                return {
                    "file_id": file_id,
                    "status": latest_event.get("status", "unknown"),
                    "event_id": latest_event.get("event_id"),
                    "timestamp": latest_event.get("timestamp"),
                    "priority": latest_event.get("priority")
                }
            else:
                return {
                    "file_id": file_id,
                    "status": "not_found",
                    "message": "No processing events found for this file"
                }
                
        except Exception as e:
            logger.error(f"Failed to get processing status for {file_id}: {e}")
            return {
                "file_id": file_id,
                "status": "error",
                "error": str(e)
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get AASX integration statistics."""
        return {
            "name": self.name,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "success_rate": (self.processed_files - self.failed_files) / max(self.processed_files, 1),
            "is_active": self.is_active,
            "connection_status": self.connection_status
        }


class TwinRegistryIntegration(BaseModuleIntegration):
    """Integration with Twin Registry module for twin-based workflows."""
    
    def __init__(self, event_manager: KGNeo4jEventManager):
        """Initialize Twin Registry integration."""
        super().__init__("Twin Registry", event_manager)
        self.processed_twins = 0
        self.enhanced_twins = 0
    
    async def process_twin_registry_update(self, twin_id: str, twin_data: Dict[str, Any], user_id: str, org_id: str, dept_id: str) -> str:
        """Process a twin registry update and enhance the knowledge graph."""
        try:
            logger.info(f"Processing twin registry update {twin_id} for graph enhancement")
            
            # Create graph creation event for twin-based graph
            event_id = await self.event_manager.publish_graph_creation(
                file_id=twin_id,  # Use twin_id as file_id for consistency
                graph_name=f"Graph_Twin_{twin_id[:8]}",
                workflow_source="twin_registry",
                graph_config={
                    "twin_id": twin_id,
                    "twin_data": twin_data,
                    "source_module": "Twin Registry",
                    "processing_method": "twin_enhancement"
                },
                user_id=user_id,
                org_id=org_id,
                dept_id=dept_id,
                priority=EventPriority.HIGH
            )
            
            # Simulate twin processing workflow
            await asyncio.sleep(0.1)
            
            self.processed_twins += 1
            logger.info(f"Twin registry update {twin_id} processed successfully, event: {event_id}")
            
            return event_id
            
        except Exception as e:
            error_msg = f"Failed to process twin registry update {twin_id}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    async def enhance_existing_graph(self, graph_id: str, twin_data: Dict[str, Any]) -> str:
        """Enhance an existing knowledge graph with twin registry data."""
        try:
            logger.info(f"Enhancing existing graph {graph_id} with twin data")
            
            # Create AI insights event for enhancement
            event_id = await self.event_manager.publish_ai_insights(
                graph_id=graph_id,
                ai_operation_type="enhancement",
                ai_model_version="twin_registry_v1.0",
                confidence_score=0.95,
                analysis_data={
                    "enhancement_source": "twin_registry",
                    "twin_data": twin_data,
                    "enhancement_type": "graph_expansion"
                },
                insights_count=len(twin_data.get("properties", {})),
                processing_duration_ms=500.0
            )
            
            self.enhanced_twins += 1
            logger.info(f"Graph {graph_id} enhanced successfully, event: {event_id}")
            
            return event_id
            
        except Exception as e:
            error_msg = f"Failed to enhance graph {graph_id}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get Twin Registry integration statistics."""
        return {
            "name": self.name,
            "processed_twins": self.processed_twins,
            "enhanced_twins": self.enhanced_twins,
            "is_active": self.is_active,
            "connection_status": self.connection_status
        }


class AIRAGIntegration(BaseModuleIntegration):
    """Integration with AI RAG systems for intelligent graph operations."""
    
    def __init__(self, event_manager: KGNeo4jEventManager):
        """Initialize AI RAG integration."""
        super().__init__("AI RAG", event_manager)
        self.ai_requests = 0
        self.ai_responses = 0
        self.model_versions = ["gpt-4", "claude-3", "llama-3", "custom-bert"]
    
    async def request_ai_analysis(self, graph_id: str, analysis_type: str, query: str, user_id: str, org_id: str, dept_id: str) -> str:
        """Request AI analysis of a knowledge graph."""
        try:
            logger.info(f"Requesting AI analysis for graph {graph_id}: {analysis_type}")
            
            # Create AI insights event
            event_id = await self.event_manager.publish_ai_insights(
                graph_id=graph_id,
                ai_operation_type=analysis_type,
                ai_model_version="gpt-4",  # Default model
                confidence_score=0.0,  # Will be updated by AI response
                analysis_data={
                    "query": query,
                    "analysis_type": analysis_type,
                    "request_timestamp": datetime.now(timezone.utc).isoformat()
                },
                insights_count=0,  # Will be updated by AI response
                processing_duration_ms=0.0  # Will be updated by AI response
            )
            
            self.ai_requests += 1
            logger.info(f"AI analysis requested for graph {graph_id}, event: {event_id}")
            
            # Simulate AI processing
            await asyncio.sleep(0.2)
            
            return event_id
            
        except Exception as e:
            error_msg = f"Failed to request AI analysis for graph {graph_id}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    async def process_ai_response(self, graph_id: str, event_id: str, ai_response: Dict[str, Any]) -> bool:
        """Process AI response and update the knowledge graph."""
        try:
            logger.info(f"Processing AI response for graph {graph_id}, event: {event_id}")
            
            # Update the graph with AI insights
            # This would typically involve updating the graph structure
            # For now, we'll just log the response
            
            self.ai_responses += 1
            logger.info(f"AI response processed for graph {graph_id}")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to process AI response for graph {graph_id}: {e}"
            logger.error(error_msg)
            return False
    
    async def train_ai_model(self, graph_id: str, training_data: Dict[str, Any], model_config: Dict[str, Any]) -> str:
        """Train an AI model using knowledge graph data."""
        try:
            logger.info(f"Training AI model for graph {graph_id}")
            
            # Create AI insights event for training
            event_id = await self.event_manager.publish_ai_insights(
                graph_id=graph_id,
                ai_operation_type="training",
                ai_model_version=model_config.get("model_type", "custom"),
                confidence_score=0.0,  # Will be updated after training
                analysis_data={
                    "training_data": training_data,
                    "model_config": model_config,
                    "training_start": datetime.now(timezone.utc).isoformat()
                },
                insights_count=0,
                processing_duration_ms=0.0
            )
            
            logger.info(f"AI model training initiated for graph {graph_id}, event: {event_id}")
            
            return event_id
            
        except Exception as e:
            error_msg = f"Failed to initiate AI model training for graph {graph_id}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get AI RAG integration statistics."""
        return {
            "name": self.name,
            "ai_requests": self.ai_requests,
            "ai_responses": self.ai_responses,
            "available_models": self.model_versions,
            "is_active": self.is_active,
            "connection_status": self.connection_status
        }


# Integration Registry for easy access
INTEGRATION_REGISTRY = {
    "aasx": AASXIntegration,
    "twin_registry": TwinRegistryIntegration,
    "ai_rag": AIRAGIntegration
}


def get_integration(integration_type: str, event_manager: KGNeo4jEventManager) -> BaseModuleIntegration:
    """Get an integration instance by type."""
    if integration_type not in INTEGRATION_REGISTRY:
        raise ValueError(f"Unknown integration type: {integration_type}")
    
    integration_class = INTEGRATION_REGISTRY[integration_type]
    return integration_class(event_manager)


def get_available_integrations() -> List[str]:
    """Get list of available integration types."""
    return list(INTEGRATION_REGISTRY.keys())
