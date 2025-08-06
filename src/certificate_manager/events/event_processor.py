"""
Event Processor

Processes events and manages certificate updates for Phase 2.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.certificate_manager import CertificateManager
from ..models.certificate_event import CertificateEvent, EventType, EventStatus

logger = logging.getLogger(__name__)


class EventProcessor:
    """Processes events and manages certificate updates."""
    
    def __init__(self, certificate_manager: Optional[CertificateManager] = None):
        """Initialize the event processor.
        
        Args:
            certificate_manager: Certificate manager instance
        """
        self.certificate_manager = certificate_manager or CertificateManager()
        self.processing_queue: List[Dict[str, Any]] = []
        self.is_processing = False
        
        logger.info("EventProcessor initialized successfully")
    
    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single event.
        
        Args:
            event: Event data dictionary
            
        Returns:
            Processing result dictionary
        """
        try:
            # Validate event
            if not self._validate_event(event):
                return {
                    'status': 'error',
                    'error': 'Invalid event structure'
                }
            
            # Create certificate event record
            certificate_event = self._create_certificate_event(event)
            
            # Process based on event type
            result = await self._process_event_by_type(event, certificate_event)
            
            # Update event status
            self._update_event_status(certificate_event, EventStatus.COMPLETED)
            
            logger.info(f"Event processed successfully: {event.get('event_type')}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            
            # Update event status to failed
            if 'certificate_event' in locals():
                self._update_event_status(certificate_event, EventStatus.FAILED)
            
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def process_events_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple events in batch.
        
        Args:
            events: List of event data dictionaries
            
        Returns:
            List of processing results
        """
        results = []
        
        for event in events:
            try:
                result = await self.process_event(event)
                results.append(result)
                
                # Small delay between events to prevent overwhelming the system
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing event in batch: {e}")
                results.append({
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def _validate_event(self, event: Dict[str, Any]) -> bool:
        """Validate event structure.
        
        Args:
            event: Event data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['event_type', 'module_name', 'timestamp']
        
        for field in required_fields:
            if field not in event:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate event type
        valid_event_types = [
            'aasx.file_uploaded', 'aasx.etl_completed', 'aasx.etl_failed',
            'twin.registered', 'twin.health_updated', 'twin.status_changed',
            'ai.analysis_completed', 'ai.insights_updated', 'ai.rag_processed',
            'kg.graph_built', 'kg.relationships_updated', 'kg.entities_extracted',
            'fl.participation_started', 'fl.round_completed', 'fl.model_updated',
            'physics.simulation_started', 'physics.simulation_completed', 'physics.model_created',
            'certificate.created', 'certificate.updated', 'certificate.exported', 'certificate.signed'
        ]
        
        if event.get('event_type') not in valid_event_types:
            logger.error(f"Invalid event type: {event.get('event_type')}")
            return False
        
        return True
    
    def _create_certificate_event(self, event: Dict[str, Any]) -> CertificateEvent:
        """Create a certificate event record.
        
        Args:
            event: Event data dictionary
            
        Returns:
            CertificateEvent instance
        """
        try:
            # Map event type to EventType enum
            event_type = self._map_event_type(event.get('event_type'))
            
            certificate_event = CertificateEvent(
                certificate_id=event.get('certificate_id'),
                event_id=event.get('event_id'),
                event_type=event_type,
                module_name=event.get('module_name'),
                data_snapshot=event.get('data', {}),
                status=EventStatus.PENDING
            )
            
            # Save to database
            self.certificate_manager.event_repo.create(certificate_event)
            
            return certificate_event
            
        except Exception as e:
            logger.error(f"Error creating certificate event: {e}")
            raise
    
    def _map_event_type(self, event_type: str) -> EventType:
        """Map string event type to EventType enum.
        
        Args:
            event_type: String event type
            
        Returns:
            EventType enum value
        """
        event_type_mapping = {
            # AASX events
            'aasx.file_uploaded': EventType.FILE_UPLOADED,
            'aasx.etl_completed': EventType.ETL_COMPLETED,
            'aasx.etl_failed': EventType.ETL_FAILED,
            
            # Twin events
            'twin.registered': EventType.TWIN_REGISTERED,
            'twin.health_updated': EventType.TWIN_HEALTH_UPDATED,
            'twin.status_changed': EventType.TWIN_STATUS_CHANGED,
            
            # AI events
            'ai.analysis_completed': EventType.AI_ANALYSIS_COMPLETED,
            'ai.insights_updated': EventType.AI_INSIGHTS_UPDATED,
            'ai.rag_processed': EventType.AI_RAG_PROCESSED,
            
            # Knowledge Graph events
            'kg.graph_built': EventType.KG_GRAPH_BUILT,
            'kg.relationships_updated': EventType.KG_RELATIONSHIPS_UPDATED,
            'kg.entities_extracted': EventType.KG_ENTITIES_EXTRACTED,
            
            # Federated Learning events
            'fl.participation_started': EventType.FL_PARTICIPATION_STARTED,
            'fl.round_completed': EventType.FL_ROUND_COMPLETED,
            'fl.model_updated': EventType.FL_MODEL_UPDATED,
            
            # Physics events
            'physics.simulation_started': EventType.PHYSICS_SIMULATION_STARTED,
            'physics.simulation_completed': EventType.PHYSICS_SIMULATION_COMPLETED,
            'physics.model_created': EventType.PHYSICS_MODEL_CREATED,
            
            # Certificate events
            'certificate.created': EventType.CERTIFICATE_CREATED,
            'certificate.updated': EventType.CERTIFICATE_UPDATED,
            'certificate.exported': EventType.CERTIFICATE_EXPORTED,
            'certificate.signed': EventType.CERTIFICATE_SIGNED
        }
        
        return event_type_mapping.get(event_type, EventType.MODULE_EVENT)
    
    async def _process_event_by_type(self, event: Dict[str, Any], certificate_event: CertificateEvent) -> Dict[str, Any]:
        """Process event based on its type.
        
        Args:
            event: Event data dictionary
            certificate_event: CertificateEvent instance
            
        Returns:
            Processing result dictionary
        """
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        
        try:
            # Get or create certificate
            certificate = self.certificate_manager.get_certificate(certificate_id)
            if not certificate:
                # Create certificate for new events
                certificate = self.certificate_manager.create_certificate(
                    certificate_id,
                    twin_name=event.get('twin_name', 'Unknown Twin'),
                    project_name=event.get('project_name', 'Unknown Project'),
                    use_case_name=event.get('use_case_name', 'Unknown Use Case'),
                    file_name=event.get('file_name', 'Unknown File')
                )
            
            # Process based on event type
            if event_type.startswith('aasx.'):
                return await self._process_aasx_event(event, certificate)
            elif event_type.startswith('twin.'):
                return await self._process_twin_event(event, certificate)
            elif event_type.startswith('ai.'):
                return await self._process_ai_event(event, certificate)
            elif event_type.startswith('kg.'):
                return await self._process_kg_event(event, certificate)
            elif event_type.startswith('fl.'):
                return await self._process_fl_event(event, certificate)
            elif event_type.startswith('physics.'):
                return await self._process_physics_event(event, certificate)
            elif event_type.startswith('certificate.'):
                return await self._process_certificate_event(event, certificate)
            else:
                return {
                    'status': 'ignored',
                    'reason': f'Unknown event type: {event_type}'
                }
                
        except Exception as e:
            logger.error(f"Error processing event by type: {e}")
            raise
    
    async def _process_aasx_event(self, event: Dict[str, Any], certificate) -> Dict[str, Any]:
        """Process AASX module event."""
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        data = event.get('data', {})
        
        if event_type == 'aasx.file_uploaded':
            # Add file upload data
            self.certificate_manager.add_section_data(
                certificate_id,
                'aasx_file_upload',
                {
                    'file_name': data.get('file_name'),
                    'upload_timestamp': event.get('timestamp'),
                    'file_size': data.get('file_size'),
                    'file_type': data.get('file_type')
                }
            )
            
        elif event_type == 'aasx.etl_completed':
            # Add ETL completion data
            self.certificate_manager.add_section_data(
                certificate_id,
                'etl',
                {
                    'status': 'completed',
                    'completion_timestamp': event.get('timestamp'),
                    'data_quality_score': data.get('data_quality_score'),
                    'processed_records': data.get('processed_records'),
                    'summary': data.get('summary')
                }
            )
            
        elif event_type == 'aasx.etl_failed':
            # Add ETL failure data
            self.certificate_manager.add_section_data(
                certificate_id,
                'etl',
                {
                    'status': 'failed',
                    'error_timestamp': event.get('timestamp'),
                    'error_message': data.get('error_message'),
                    'error_code': data.get('error_code')
                }
            )
        
        return {
            'status': 'processed',
            'action': f'aasx_{event_type.split(".")[1]}',
            'certificate_id': certificate_id
        }
    
    async def _process_twin_event(self, event: Dict[str, Any], certificate) -> Dict[str, Any]:
        """Process Digital Twin module event."""
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        data = event.get('data', {})
        
        if event_type == 'twin.registered':
            self.certificate_manager.add_section_data(
                certificate_id,
                'twin_registration',
                {
                    'registration_timestamp': event.get('timestamp'),
                    'twin_id': data.get('twin_id'),
                    'twin_name': data.get('twin_name'),
                    'project_name': data.get('project_name')
                }
            )
            
        elif event_type == 'twin.health_updated':
            self.certificate_manager.add_section_data(
                certificate_id,
                'twin_health',
                {
                    'update_timestamp': event.get('timestamp'),
                    'health_score': data.get('health_score'),
                    'status': data.get('status'),
                    'metrics': data.get('metrics', {})
                }
            )
            
        elif event_type == 'twin.status_changed':
            self.certificate_manager.add_section_data(
                certificate_id,
                'twin_status',
                {
                    'change_timestamp': event.get('timestamp'),
                    'old_status': data.get('old_status'),
                    'new_status': data.get('new_status'),
                    'reason': data.get('reason')
                }
            )
        
        return {
            'status': 'processed',
            'action': f'twin_{event_type.split(".")[1]}',
            'certificate_id': certificate_id
        }
    
    async def _process_ai_event(self, event: Dict[str, Any], certificate) -> Dict[str, Any]:
        """Process AI/RAG module event."""
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        data = event.get('data', {})
        
        if event_type == 'ai.analysis_completed':
            self.certificate_manager.add_section_data(
                certificate_id,
                'ai_analysis',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'analysis_type': data.get('analysis_type'),
                    'confidence_score': data.get('confidence_score'),
                    'insights_count': data.get('insights_count'),
                    'summary': data.get('summary')
                }
            )
            
        elif event_type == 'ai.insights_updated':
            self.certificate_manager.add_section_data(
                certificate_id,
                'ai_insights',
                {
                    'update_timestamp': event.get('timestamp'),
                    'insights_count': data.get('insights_count'),
                    'new_insights': data.get('new_insights', []),
                    'updated_insights': data.get('updated_insights', [])
                }
            )
            
        elif event_type == 'ai.rag_processed':
            self.certificate_manager.add_section_data(
                certificate_id,
                'ai_rag',
                {
                    'processing_timestamp': event.get('timestamp'),
                    'query_count': data.get('query_count'),
                    'response_quality': data.get('response_quality'),
                    'vector_db_status': data.get('vector_db_status'),
                    'summary': data.get('summary')
                }
            )
        
        return {
            'status': 'processed',
            'action': f'ai_{event_type.split(".")[1]}',
            'certificate_id': certificate_id
        }
    
    async def _process_kg_event(self, event: Dict[str, Any], certificate) -> Dict[str, Any]:
        """Process Knowledge Graph module event."""
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        data = event.get('data', {})
        
        if event_type == 'kg.graph_built':
            self.certificate_manager.add_section_data(
                certificate_id,
                'knowledge_graph',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'node_count': data.get('node_count'),
                    'relationship_count': data.get('relationship_count'),
                    'graph_density': data.get('graph_density'),
                    'summary': data.get('summary')
                }
            )
            
        elif event_type == 'kg.relationships_updated':
            self.certificate_manager.add_section_data(
                certificate_id,
                'kg_relationships',
                {
                    'update_timestamp': event.get('timestamp'),
                    'new_relationships': data.get('new_relationships', []),
                    'updated_relationships': data.get('updated_relationships', []),
                    'total_relationships': data.get('total_relationships')
                }
            )
            
        elif event_type == 'kg.entities_extracted':
            self.certificate_manager.add_section_data(
                certificate_id,
                'kg_entities',
                {
                    'extraction_timestamp': event.get('timestamp'),
                    'entity_count': data.get('entity_count'),
                    'entity_types': data.get('entity_types', []),
                    'extraction_confidence': data.get('extraction_confidence')
                }
            )
        
        return {
            'status': 'processed',
            'action': f'kg_{event_type.split(".")[1]}',
            'certificate_id': certificate_id
        }
    
    async def _process_fl_event(self, event: Dict[str, Any], certificate) -> Dict[str, Any]:
        """Process Federated Learning module event."""
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        data = event.get('data', {})
        
        if event_type == 'fl.participation_started':
            self.certificate_manager.add_section_data(
                certificate_id,
                'federated_learning',
                {
                    'participation_timestamp': event.get('timestamp'),
                    'session_id': data.get('session_id'),
                    'participant_id': data.get('participant_id'),
                    'model_type': data.get('model_type')
                }
            )
            
        elif event_type == 'fl.round_completed':
            self.certificate_manager.add_section_data(
                certificate_id,
                'fl_rounds',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'round_number': data.get('round_number'),
                    'participants_count': data.get('participants_count'),
                    'model_accuracy': data.get('model_accuracy'),
                    'contribution_score': data.get('contribution_score')
                }
            )
            
        elif event_type == 'fl.model_updated':
            self.certificate_manager.add_section_data(
                certificate_id,
                'fl_model',
                {
                    'update_timestamp': event.get('timestamp'),
                    'model_version': data.get('model_version'),
                    'improvement_score': data.get('improvement_score'),
                    'aggregation_method': data.get('aggregation_method')
                }
            )
        
        return {
            'status': 'processed',
            'action': f'fl_{event_type.split(".")[1]}',
            'certificate_id': certificate_id
        }
    
    async def _process_physics_event(self, event: Dict[str, Any], certificate) -> Dict[str, Any]:
        """Process Physics Modeling module event."""
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        data = event.get('data', {})
        
        if event_type == 'physics.simulation_started':
            self.certificate_manager.add_section_data(
                certificate_id,
                'physics_simulation',
                {
                    'start_timestamp': event.get('timestamp'),
                    'simulation_type': data.get('simulation_type'),
                    'parameters': data.get('parameters', {}),
                    'expected_duration': data.get('expected_duration')
                }
            )
            
        elif event_type == 'physics.simulation_completed':
            self.certificate_manager.add_section_data(
                certificate_id,
                'physics_results',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'simulation_type': data.get('simulation_type'),
                    'results_summary': data.get('results_summary'),
                    'accuracy_metrics': data.get('accuracy_metrics', {}),
                    'validation_score': data.get('validation_score')
                }
            )
            
        elif event_type == 'physics.model_created':
            self.certificate_manager.add_section_data(
                certificate_id,
                'physics_model',
                {
                    'creation_timestamp': event.get('timestamp'),
                    'model_type': data.get('model_type'),
                    'model_parameters': data.get('model_parameters', {}),
                    'training_metrics': data.get('training_metrics', {})
                }
            )
        
        return {
            'status': 'processed',
            'action': f'physics_{event_type.split(".")[1]}',
            'certificate_id': certificate_id
        }
    
    async def _process_certificate_event(self, event: Dict[str, Any], certificate) -> Dict[str, Any]:
        """Process Certificate Manager event."""
        event_type = event.get('event_type')
        certificate_id = event.get('certificate_id')
        data = event.get('data', {})
        
        if event_type == 'certificate.updated':
            self.certificate_manager.add_section_data(
                certificate_id,
                'certificate_updates',
                {
                    'update_timestamp': event.get('timestamp'),
                    'updated_fields': data.get('updated_fields', []),
                    'update_reason': data.get('update_reason')
                }
            )
            
        elif event_type == 'certificate.exported':
            self.certificate_manager.add_section_data(
                certificate_id,
                'certificate_exports',
                {
                    'export_timestamp': event.get('timestamp'),
                    'export_format': data.get('export_format'),
                    'file_path': data.get('file_path'),
                    'file_size': data.get('file_size')
                }
            )
            
        elif event_type == 'certificate.signed':
            self.certificate_manager.add_section_data(
                certificate_id,
                'certificate_signature',
                {
                    'signature_timestamp': event.get('timestamp'),
                    'signature_method': data.get('signature_method'),
                    'signature_hash': data.get('signature_hash'),
                    'signed_by': data.get('signed_by')
                }
            )
        
        return {
            'status': 'processed',
            'action': f'certificate_{event_type.split(".")[1]}',
            'certificate_id': certificate_id
        }
    
    def _update_event_status(self, certificate_event: CertificateEvent, status: EventStatus) -> None:
        """Update certificate event status.
        
        Args:
            certificate_event: CertificateEvent instance
            status: New status
        """
        try:
            certificate_event.status = status
            certificate_event.processed_at = datetime.now()
            self.certificate_manager.event_repo.update(certificate_event)
            
        except Exception as e:
            logger.error(f"Error updating event status: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics.
        
        Returns:
            Dictionary with processing stats
        """
        return {
            'queue_size': len(self.processing_queue),
            'is_processing': self.is_processing,
            'total_events_processed': 0  # TODO: Implement counter
        } 