"""
Federation Engine
================

Main coordinator for federated learning process.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.database.base_manager import BaseDatabaseManager
from .local_trainer import LocalTrainer
from .aggregation_server import AggregationServer
from .federated_learning_service import FederatedLearningService

logger = logging.getLogger(__name__)

class FederationEngine:
    """Main federated learning coordinator"""
    
    def __init__(self, db_manager: BaseDatabaseManager, digital_twin_service: DigitalTwinService):
        self.db_manager = db_manager
        self.digital_twin_service = digital_twin_service
        self.local_trainer = LocalTrainer(db_manager, digital_twin_service)
        self.aggregation_server = AggregationServer()
        self.fl_service = FederatedLearningService(digital_twin_service)
        
        # Active federation sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def start_federation(self, twin_ids: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Start federated learning session"""
        try:
            logger.info(f"Starting federated learning session with twins: {twin_ids}")
            
            # Validate twins exist and are ready for federation
            ready_twins = self.fl_service.get_federated_ready_twins()
            ready_twin_ids = [twin.twin_id for twin in ready_twins]
            
            valid_twins = [twin_id for twin_id in twin_ids if twin_id in ready_twin_ids]
            if not valid_twins:
                return {
                    'status': 'error',
                    'message': 'No valid twins found for federated learning'
                }
            
            # Create federation session
            session_id = str(uuid.uuid4())
            session_config = {
                'session_id': session_id,
                'twin_ids': valid_twins,
                'config': config,
                'status': 'active',
                'start_time': datetime.now().isoformat(),
                'current_round': 0,
                'total_rounds': config.get('total_rounds', 10),
                'global_model': None
            }
            
            self.active_sessions[session_id] = session_config
            
            logger.info(f"Federation session {session_id} started successfully")
            
            return {
                'status': 'success',
                'session_id': session_id,
                'message': f'Federation session started with {len(valid_twins)} twins',
                'data': session_config
            }
            
        except Exception as e:
            logger.error(f"Error starting federation: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to start federation: {str(e)}'
            }
    
    def run_cycle(self, session_id: str) -> Dict[str, Any]:
        """Run one federated learning cycle"""
        try:
            if session_id not in self.active_sessions:
                return {
                    'status': 'error',
                    'message': f'Session {session_id} not found or not active'
                }
            
            session = self.active_sessions[session_id]
            twin_ids = session['twin_ids']
            current_round = session['current_round']
            total_rounds = session['total_rounds']
            
            logger.info(f"Running federation cycle {current_round + 1}/{total_rounds} for session {session_id}")
            
            # Step 1: Local training for each twin
            local_updates = []
            for twin_id in twin_ids:
                try:
                    # Load twin data
                    twin_data = self.local_trainer.load_twin_data(twin_id)
                    
                    # Train local model
                    global_model = session.get('global_model', {})
                    local_update = self.local_trainer.train_local_model(global_model, twin_id)
                    
                    # Apply privacy mechanisms
                    private_update = self.local_trainer.apply_privacy_mechanisms(local_update)
                    
                    # Validate updates
                    if self.local_trainer.validate_updates(private_update):
                        local_updates.append(private_update)
                        logger.info(f"Twin {twin_id} completed local training successfully")
                    else:
                        logger.warning(f"Twin {twin_id} update validation failed")
                        
                except Exception as e:
                    logger.error(f"Error in local training for twin {twin_id}: {str(e)}")
            
            if not local_updates:
                return {
                    'status': 'error',
                    'message': 'No valid local updates received'
                }
            
            # Step 2: Aggregate models
            aggregated_model = self.aggregation_server.aggregate_models(local_updates)
            
            # Step 3: Update global model
            session['global_model'] = aggregated_model
            session['current_round'] += 1
            
            # Check if federation is complete
            if session['current_round'] >= total_rounds:
                session['status'] = 'completed'
                session['end_time'] = datetime.now().isoformat()
                logger.info(f"Federation session {session_id} completed")
            
            return {
                'status': 'success',
                'session_id': session_id,
                'round': session['current_round'],
                'participating_twins': len(local_updates),
                'message': f'Federation cycle {session["current_round"]} completed successfully',
                'data': {
                    'aggregated_model': aggregated_model,
                    'session_status': session['status']
                }
            }
            
        except Exception as e:
            logger.error(f"Error running federation cycle: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to run federation cycle: {str(e)}'
            }
    
    def stop_federation(self, session_id: str) -> Dict[str, Any]:
        """Stop federated learning session"""
        try:
            if session_id not in self.active_sessions:
                return {
                    'status': 'error',
                    'message': f'Session {session_id} not found'
                }
            
            session = self.active_sessions[session_id]
            session['status'] = 'stopped'
            session['end_time'] = datetime.now().isoformat()
            
            logger.info(f"Federation session {session_id} stopped")
            
            return {
                'status': 'success',
                'session_id': session_id,
                'message': 'Federation session stopped successfully',
                'data': session
            }
            
        except Exception as e:
            logger.error(f"Error stopping federation: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to stop federation: {str(e)}'
            }
    
    def get_status(self, session_id: str) -> Dict[str, Any]:
        """Get federation status"""
        try:
            if session_id not in self.active_sessions:
                return {
                    'status': 'error',
                    'message': f'Session {session_id} not found'
                }
            
            session = self.active_sessions[session_id]
            
            return {
                'status': 'success',
                'session_id': session_id,
                'data': session
            }
            
        except Exception as e:
            logger.error(f"Error getting federation status: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to get federation status: {str(e)}'
            } 