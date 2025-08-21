"""
Event Router

Routes events to appropriate handlers for Phase 2.
"""

import logging
from typing import Dict, Any, Callable, Awaitable
from datetime import datetime

from ..core.certificate_manager import CertificateManager
from ..models.certificate_event import EventType

logger = logging.getLogger(__name__)


class EventRouter:
    """Routes events to appropriate handlers."""
    
    def __init__(self, certificate_manager: CertificateManager):
        """Initialize the event router.
        
        Args:
            certificate_manager: Certificate manager instance
        """
        self.certificate_manager = certificate_manager
        self.handlers = self._setup_handlers()
        
        logger.info("EventRouter initialized successfully")
    
    def _setup_handlers(self) -> Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]]:
        """Setup event handlers mapping."""
        return {
            # AASX Module Events
            'aasx.file_uploaded': self._handle_file_upload,
            'aasx.etl_completed': self._handle_etl_completion,
            'aasx.etl_failed': self._handle_etl_failure,
            
            # Digital Twin Events
            'twin.registered': self._handle_twin_registration,
            'twin.health_updated': self._handle_twin_health_update,
            'twin.status_changed': self._handle_twin_status_change,
            
            # AI/RAG Events
            'ai.analysis_completed': self._handle_ai_completion,
            'ai.insights_updated': self._handle_ai_insights_update,
            'ai.rag_processed': self._handle_rag_processed,
            
            # Knowledge Graph Events
            'kg.graph_built': self._handle_kg_completion,
            'kg.relationships_updated': self._handle_kg_relationships_update,
            'kg.entities_extracted': self._handle_kg_entities_extracted,
            
            # Federated Learning Events
            'fl.participation_started': self._handle_fl_participation,
            'fl.round_completed': self._handle_fl_round_completion,
            'fl.model_updated': self._handle_fl_model_update,
            
            # Physics Modeling Events
            'physics.simulation_started': self._handle_physics_simulation_start,
            'physics.simulation_completed': self._handle_physics_completion,
            'physics.model_created': self._handle_physics_model_created,
            
            # Certificate Manager Events
            'certificate.created': self._handle_certificate_created,
            'certificate.updated': self._handle_certificate_updated,
            'certificate.exported': self._handle_certificate_exported,
            'certificate.signed': self._handle_certificate_signed
        }
    
    async def route_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Route event to appropriate handler.
        
        Args:
            event: Event data dictionary
            
        Returns:
            Processing result dictionary
        """
        try:
            event_type = event.get('event_type')
            
            if event_type not in self.handlers:
                logger.warning(f"Unknown event type: {event_type}")
                return {
                    'status': 'ignored',
                    'reason': f'unknown_event_type: {event_type}'
                }
            
            # Get handler and execute
            handler = self.handlers[event_type]
            result = await handler(event)
            
            logger.info(f"Event routed successfully: {event_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error routing event: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    # AASX Event Handlers
    async def _handle_file_upload(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AASX file upload event."""
        try:
            certificate_id = event.get('certificate_id')
            twin_name = event.get('twin_name', 'Unknown Twin')
            project_name = event.get('project_name', 'Unknown Project')
            use_case_name = event.get('use_case_name', 'Unknown Use Case')
            file_name = event.get('file_name', 'Unknown File')
            
            # Create new certificate if it doesn't exist
            certificate = self.certificate_manager.get_certificate(certificate_id)
            if not certificate:
                certificate = self.certificate_manager.create_certificate(
                    certificate_id,
                    twin_name=twin_name,
                    project_name=project_name,
                    use_case_name=use_case_name,
                    file_name=file_name
                )
            
            # Add file upload data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'aasx_file_upload',
                {
                    'file_name': file_name,
                    'upload_timestamp': event.get('timestamp'),
                    'file_size': event.get('data', {}).get('file_size'),
                    'file_type': event.get('data', {}).get('file_type')
                }
            )
            
            return {
                'action': 'certificate_created_or_updated',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling file upload: {e}")
            raise
    
    async def _handle_etl_completion(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ETL completion event."""
        try:
            certificate_id = event.get('certificate_id')
            etl_data = event.get('data', {})
            
            # Add ETL data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'etl',
                {
                    'status': 'completed',
                    'completion_timestamp': event.get('timestamp'),
                    'data_quality_score': etl_data.get('data_quality_score'),
                    'processed_records': etl_data.get('processed_records'),
                    'summary': etl_data.get('summary')
                }
            )
            
            return {
                'action': 'etl_data_added',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling ETL completion: {e}")
            raise
    
    async def _handle_etl_failure(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ETL failure event."""
        try:
            certificate_id = event.get('certificate_id')
            error_data = event.get('data', {})
            
            # Add ETL error data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'etl',
                {
                    'status': 'failed',
                    'error_timestamp': event.get('timestamp'),
                    'error_message': error_data.get('error_message'),
                    'error_code': error_data.get('error_code')
                }
            )
            
            return {
                'action': 'etl_error_logged',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling ETL failure: {e}")
            raise
    
    # Digital Twin Event Handlers
    async def _handle_twin_registration(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle twin registration event."""
        try:
            certificate_id = event.get('certificate_id')
            twin_data = event.get('data', {})
            
            # Add twin registration data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'twin_registration',
                {
                    'registration_timestamp': event.get('timestamp'),
                    'twin_id': twin_data.get('twin_id'),
                    'twin_name': twin_data.get('twin_name'),
                    'project_name': twin_data.get('project_name')
                }
            )
            
            return {
                'action': 'twin_registration_logged',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling twin registration: {e}")
            raise
    
    async def _handle_twin_health_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle twin health update event."""
        try:
            certificate_id = event.get('certificate_id')
            health_data = event.get('data', {})
            
            # Add health data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'twin_health',
                {
                    'update_timestamp': event.get('timestamp'),
                    'health_score': health_data.get('health_score'),
                    'status': health_data.get('status'),
                    'metrics': health_data.get('metrics', {})
                }
            )
            
            return {
                'action': 'health_data_updated',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling twin health update: {e}")
            raise
    
    async def _handle_twin_status_change(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle twin status change event."""
        try:
            certificate_id = event.get('certificate_id')
            status_data = event.get('data', {})
            
            # Add status change data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'twin_status',
                {
                    'change_timestamp': event.get('timestamp'),
                    'old_status': status_data.get('old_status'),
                    'new_status': status_data.get('new_status'),
                    'reason': status_data.get('reason')
                }
            )
            
            return {
                'action': 'status_change_logged',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling twin status change: {e}")
            raise
    
    # AI/RAG Event Handlers
    async def _handle_ai_completion(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI analysis completion event."""
        try:
            certificate_id = event.get('certificate_id')
            ai_data = event.get('data', {})
            
            # Add AI analysis data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'ai_analysis',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'analysis_type': ai_data.get('analysis_type'),
                    'confidence_score': ai_data.get('confidence_score'),
                    'insights_count': ai_data.get('insights_count'),
                    'summary': ai_data.get('summary')
                }
            )
            
            return {
                'action': 'ai_analysis_added',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling AI completion: {e}")
            raise
    
    async def _handle_ai_insights_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI insights update event."""
        try:
            certificate_id = event.get('certificate_id')
            insights_data = event.get('data', {})
            
            # Add insights update data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'ai_insights',
                {
                    'update_timestamp': event.get('timestamp'),
                    'insights_count': insights_data.get('insights_count'),
                    'new_insights': insights_data.get('new_insights', []),
                    'updated_insights': insights_data.get('updated_insights', [])
                }
            )
            
            return {
                'action': 'insights_updated',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling AI insights update: {e}")
            raise
    
    async def _handle_rag_processed(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RAG processing event."""
        try:
            certificate_id = event.get('certificate_id')
            rag_data = event.get('data', {})
            
            # Add RAG data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'ai_rag',
                {
                    'processing_timestamp': event.get('timestamp'),
                    'query_count': rag_data.get('query_count'),
                    'response_quality': rag_data.get('response_quality'),
                    'vector_db_status': rag_data.get('vector_db_status'),
                    'summary': rag_data.get('summary')
                }
            )
            
            return {
                'action': 'rag_data_added',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling RAG processing: {e}")
            raise
    
    # Knowledge Graph Event Handlers
    async def _handle_kg_completion(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge graph completion event."""
        try:
            certificate_id = event.get('certificate_id')
            kg_data = event.get('data', {})
            
            # Add KG data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'knowledge_graph',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'node_count': kg_data.get('node_count'),
                    'relationship_count': kg_data.get('relationship_count'),
                    'graph_density': kg_data.get('graph_density'),
                    'summary': kg_data.get('summary')
                }
            )
            
            return {
                'action': 'kg_data_added',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling KG completion: {e}")
            raise
    
    async def _handle_kg_relationships_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle KG relationships update event."""
        try:
            certificate_id = event.get('certificate_id')
            rel_data = event.get('data', {})
            
            # Add relationships update data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'kg_relationships',
                {
                    'update_timestamp': event.get('timestamp'),
                    'new_relationships': rel_data.get('new_relationships', []),
                    'updated_relationships': rel_data.get('updated_relationships', []),
                    'total_relationships': rel_data.get('total_relationships')
                }
            )
            
            return {
                'action': 'relationships_updated',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling KG relationships update: {e}")
            raise
    
    async def _handle_kg_entities_extracted(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle KG entities extraction event."""
        try:
            certificate_id = event.get('certificate_id')
            entity_data = event.get('data', {})
            
            # Add entities data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'kg_entities',
                {
                    'extraction_timestamp': event.get('timestamp'),
                    'entity_count': entity_data.get('entity_count'),
                    'entity_types': entity_data.get('entity_types', []),
                    'extraction_confidence': entity_data.get('extraction_confidence')
                }
            )
            
            return {
                'action': 'entities_extracted',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling KG entities extraction: {e}")
            raise
    
    # Federated Learning Event Handlers
    async def _handle_fl_participation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FL participation event."""
        try:
            certificate_id = event.get('certificate_id')
            fl_data = event.get('data', {})
            
            # Add FL participation data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'federated_learning',
                {
                    'participation_timestamp': event.get('timestamp'),
                    'session_id': fl_data.get('session_id'),
                    'participant_id': fl_data.get('participant_id'),
                    'model_type': fl_data.get('model_type')
                }
            )
            
            return {
                'action': 'fl_participation_logged',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling FL participation: {e}")
            raise
    
    async def _handle_fl_round_completion(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FL round completion event."""
        try:
            certificate_id = event.get('certificate_id')
            round_data = event.get('data', {})
            
            # Add FL round data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'fl_rounds',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'round_number': round_data.get('round_number'),
                    'participants_count': round_data.get('participants_count'),
                    'model_accuracy': round_data.get('model_accuracy'),
                    'contribution_score': round_data.get('contribution_score')
                }
            )
            
            return {
                'action': 'fl_round_completed',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling FL round completion: {e}")
            raise
    
    async def _handle_fl_model_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FL model update event."""
        try:
            certificate_id = event.get('certificate_id')
            model_data = event.get('data', {})
            
            # Add FL model update data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'fl_model',
                {
                    'update_timestamp': event.get('timestamp'),
                    'model_version': model_data.get('model_version'),
                    'improvement_score': model_data.get('improvement_score'),
                    'aggregation_method': model_data.get('aggregation_method')
                }
            )
            
            return {
                'action': 'fl_model_updated',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling FL model update: {e}")
            raise
    
    # Physics Modeling Event Handlers
    async def _handle_physics_simulation_start(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle physics simulation start event."""
        try:
            certificate_id = event.get('certificate_id')
            sim_data = event.get('data', {})
            
            # Add simulation start data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'physics_simulation',
                {
                    'start_timestamp': event.get('timestamp'),
                    'simulation_type': sim_data.get('simulation_type'),
                    'parameters': sim_data.get('parameters', {}),
                    'expected_duration': sim_data.get('expected_duration')
                }
            )
            
            return {
                'action': 'simulation_started',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling physics simulation start: {e}")
            raise
    
    async def _handle_physics_completion(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle physics simulation completion event."""
        try:
            certificate_id = event.get('certificate_id')
            physics_data = event.get('data', {})
            
            # Add physics results data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'physics_results',
                {
                    'completion_timestamp': event.get('timestamp'),
                    'simulation_type': physics_data.get('simulation_type'),
                    'results_summary': physics_data.get('results_summary'),
                    'accuracy_metrics': physics_data.get('accuracy_metrics', {}),
                    'validation_score': physics_data.get('validation_score')
                }
            )
            
            return {
                'action': 'physics_results_added',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling physics completion: {e}")
            raise
    
    async def _handle_physics_model_created(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle physics model creation event."""
        try:
            certificate_id = event.get('certificate_id')
            model_data = event.get('data', {})
            
            # Add physics model data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'physics_model',
                {
                    'creation_timestamp': event.get('timestamp'),
                    'model_type': model_data.get('model_type'),
                    'model_parameters': model_data.get('model_parameters', {}),
                    'training_metrics': model_data.get('training_metrics', {})
                }
            )
            
            return {
                'action': 'physics_model_created',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling physics model creation: {e}")
            raise
    
    # Certificate Manager Event Handlers
    async def _handle_certificate_created(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle certificate creation event."""
        try:
            certificate_id = event.get('certificate_id')
            
            # Certificate creation is handled by the certificate manager
            # This handler just logs the event
            logger.info(f"Certificate created: {certificate_id}")
            
            return {
                'action': 'certificate_created',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling certificate creation: {e}")
            raise
    
    async def _handle_certificate_updated(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle certificate update event."""
        try:
            certificate_id = event.get('certificate_id')
            update_data = event.get('data', {})
            
            # Add update data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'certificate_updates',
                {
                    'update_timestamp': event.get('timestamp'),
                    'updated_fields': update_data.get('updated_fields', []),
                    'update_reason': update_data.get('update_reason')
                }
            )
            
            return {
                'action': 'certificate_updated',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling certificate update: {e}")
            raise
    
    async def _handle_certificate_exported(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle certificate export event."""
        try:
            certificate_id = event.get('certificate_id')
            export_data = event.get('data', {})
            
            # Add export data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'certificate_exports',
                {
                    'export_timestamp': event.get('timestamp'),
                    'export_format': export_data.get('export_format'),
                    'file_path': export_data.get('file_path'),
                    'file_size': export_data.get('file_size')
                }
            )
            
            return {
                'action': 'certificate_exported',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling certificate export: {e}")
            raise
    
    async def _handle_certificate_signed(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle certificate signing event."""
        try:
            certificate_id = event.get('certificate_id')
            signature_data = event.get('data', {})
            
            # Add signature data to certificate
            self.certificate_manager.add_section_data(
                certificate_id,
                'certificate_signature',
                {
                    'signature_timestamp': event.get('timestamp'),
                    'signature_method': signature_data.get('signature_method'),
                    'signature_hash': signature_data.get('signature_hash'),
                    'signed_by': signature_data.get('signed_by')
                }
            )
            
            return {
                'action': 'certificate_signed',
                'certificate_id': certificate_id
            }
            
        except Exception as e:
            logger.error(f"Error handling certificate signing: {e}")
            raise 