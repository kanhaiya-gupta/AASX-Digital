"""
Federation Engine
================

Main coordinator for federated learning process.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

from src.engine.services.core_system import RegistryService, MetricsService
from src.engine.database.connection_manager import ConnectionManager
from .local_trainer import LocalTrainer
from .aggregation_server import AggregationServer
from .federated_learning_service import FederatedLearningService

logger = logging.getLogger(__name__)

class FederationEngine:
    """Main federated learning coordinator"""
    
    def __init__(self, connection_manager: ConnectionManager, registry_service: RegistryService, metrics_service: MetricsService):
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.local_trainer = LocalTrainer(connection_manager, registry_service, metrics_service)
        self.aggregation_server = AggregationServer()
        self.fl_service = FederatedLearningService(connection_manager, registry_service, metrics_service)
        
        # Active federation sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def start_federation(self, twin_ids: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Start federated learning session"""
        try:
            logger.info(f"Starting federated learning session with twins: {twin_ids}")
            
            # Validate twins exist and are ready for federation
            ready_twins = await self.fl_service.get_federated_ready_twins()
            ready_twin_ids = [twin['twin_id'] for twin in ready_twins]
            
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
            
            # Persist federation session to database using ConnectionManager
            try:
                self._persist_federation_session(session_id, session_config, valid_twins)
                logger.info(f"Federation session {session_id} persisted to database")
            except Exception as db_error:
                logger.warning(f"Failed to persist session to database: {str(db_error)}")
                # Continue with in-memory session
            
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
    
    async def _persist_federation_session(self, session_id: str, session_config: Dict[str, Any], twin_ids: List[str]) -> None:
        """Persist federation session to database using existing schema"""
        try:
            # Insert into federated_learning_registry table
            registry_data = {
                'registry_id': session_id,
                'federation_name': f"federation_{session_id[:8]}",
                'registry_name': f"session_{session_id[:8]}",
                'federation_type': 'federated_learning',
                'federation_category': 'collaborative_training',
                'integration_status': 'active',
                'overall_health_score': 100,
                'health_status': 'healthy',
                'lifecycle_status': 'active',
                'federation_participation_status': 'active',
                'model_aggregation_status': 'ready',
                'privacy_compliance_status': 'compliant',
                'algorithm_execution_status': 'ready',
                'performance_score': 100,
                'data_quality_score': 100,
                'reliability_score': 100,
                'compliance_score': 100,
                'security_level': 'high',
                'access_control_level': 'restricted',
                'encryption_enabled': True,
                'user_id': 'system',
                'org_id': 'default',
                'dept_id': 'default',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Use ConnectionManager to insert data
            query = """
                INSERT INTO federated_learning_registry (
                    registry_id, federation_name, registry_name, federation_type, federation_category,
                    integration_status, overall_health_score, health_status, lifecycle_status,
                    federation_participation_status, model_aggregation_status, privacy_compliance_status,
                    algorithm_execution_status, performance_score, data_quality_score, reliability_score,
                    compliance_score, security_level, access_control_level, encryption_enabled,
                    user_id, org_id, dept_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = tuple(registry_data.values())
            await self.connection_manager.execute_query(query, values)
            
            # Insert initial metrics
            metrics_data = {
                'registry_id': session_id,
                'health_score': 100,
                'response_time_ms': 0,
                'uptime_percentage': 100,
                'error_rate': 0,
                'federation_participation_speed_sec': 0,
                'model_aggregation_speed_sec': 0,
                'privacy_compliance_speed_sec': 0,
                'cpu_usage_percent': 0,
                'memory_usage_percent': 0,
                'gpu_usage_percent': 0,
                'network_throughput_mbps': 0,
                'created_at': datetime.now().isoformat()
            }
            
            metrics_query = """
                INSERT INTO federated_learning_metrics (
                    registry_id, health_score, response_time_ms, uptime_percentage, error_rate,
                    federation_participation_speed_sec, model_aggregation_speed_sec, privacy_compliance_speed_sec,
                    cpu_usage_percent, memory_usage_percent, gpu_usage_percent, network_throughput_mbps, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            metrics_values = tuple(metrics_data.values())
            await self.connection_manager.execute_query(metrics_query, metrics_values)
            
            logger.info(f"Federation session {session_id} successfully persisted to database")
            
        except Exception as e:
            logger.error(f"Error persisting federation session to database: {str(e)}")
            raise
    
    async def _update_federation_metrics(self, session_id: str, participating_twins: int, current_round: int) -> None:
        """Update metrics in the federated_learning_metrics table."""
        try:
            # Fetch current metrics for the session
            current_metrics = await self.connection_manager.fetch_one(
                "SELECT * FROM federated_learning_metrics WHERE registry_id = ?", (session_id,)
            )

            if not current_metrics:
                # If no metrics exist, insert initial ones
                initial_metrics_data = {
                    'registry_id': session_id,
                    'health_score': 100,
                    'response_time_ms': 0,
                    'uptime_percentage': 100,
                    'error_rate': 0,
                    'federation_participation_speed_sec': 0,
                    'model_aggregation_speed_sec': 0,
                    'privacy_compliance_speed_sec': 0,
                    'cpu_usage_percent': 0,
                    'memory_usage_percent': 0,
                    'gpu_usage_percent': 0,
                    'network_throughput_mbps': 0,
                    'created_at': datetime.now().isoformat()
                }
                await self.connection_manager.execute_query(
                    "INSERT INTO federated_learning_metrics (registry_id, health_score, response_time_ms, uptime_percentage, error_rate, federation_participation_speed_sec, model_aggregation_speed_sec, privacy_compliance_speed_sec, cpu_usage_percent, memory_usage_percent, gpu_usage_percent, network_throughput_mbps, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    tuple(initial_metrics_data.values())
                )
                current_metrics = await self.connection_manager.fetch_one(
                    "SELECT * FROM federated_learning_metrics WHERE registry_id = ?", (session_id,)
                )

            # Update fields based on new data
            update_fields = []
            update_values = [session_id]
            update_params = []

            if participating_twins is not None:
                update_fields.append("federation_participation_speed_sec = ?")
                update_values.append(participating_twins)
                update_params.append("federation_participation_speed_sec")

            if current_round is not None:
                update_fields.append("model_aggregation_speed_sec = ?")
                update_values.append(current_round)
                update_params.append("model_aggregation_speed_sec")

            if update_fields:
                update_query = "UPDATE federated_learning_metrics SET " + ", ".join(update_fields) + " WHERE registry_id = ?"
                update_values.append(session_id)
                await self.connection_manager.execute_query(update_query, tuple(update_values))
                logger.info(f"Metrics for session {session_id} updated in database.")
            else:
                logger.info(f"No new metrics to update for session {session_id}.")

        except Exception as e:
            logger.error(f"Error updating metrics in database: {str(e)}")
            raise
    
    async def run_cycle(self, session_id: str) -> Dict[str, Any]:
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
                    twin_data = await self.local_trainer.load_twin_data(twin_id)
                    
                    # Train local model
                    global_model = session.get('global_model', {})
                    local_update = await self.local_trainer.train_local_model(global_model, twin_id)
                    
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
            
            # Update metrics in database
            try:
                await self._update_federation_metrics(session_id, len(local_updates), session['current_round'])
            except Exception as metrics_error:
                logger.warning(f"Failed to update metrics: {str(metrics_error)}")
            
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
    
    async def stop_federation(self, session_id: str) -> Dict[str, Any]:
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
            
            # Update database status
            try:
                await self._update_federation_status(session_id, 'stopped')
                logger.info(f"Federation session {session_id} status updated in database")
            except Exception as db_error:
                logger.warning(f"Failed to update database status: {str(db_error)}")
            
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
    
    async def _update_federation_status(self, session_id: str, status: str) -> None:
        """Update federation status in the database."""
        try:
            update_query = """
                UPDATE federated_learning_registry 
                SET lifecycle_status = ?, updated_at = ? 
                WHERE registry_id = ?
            """
            await self.connection_manager.execute_query(update_query, (status, datetime.now().isoformat(), session_id))
            logger.info(f"Federation session {session_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error updating federation status: {str(e)}")
            raise
    
    async def get_status(self, session_id: str) -> Dict[str, Any]:
        """Get federation status"""
        try:
            # Check in-memory sessions first
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                return {
                    'status': 'success',
                    'session_id': session_id,
                    'data': session,
                    'source': 'memory'
                }
            
            # If not in memory, try to fetch from database
            try:
                db_session = await self._get_federation_session_from_db(session_id)
                if db_session:
                    return {
                        'status': 'success',
                        'session_id': session_id,
                        'data': db_session,
                        'source': 'database'
                    }
            except Exception as db_error:
                logger.warning(f"Failed to fetch from database: {str(db_error)}")
            
            return {
                'status': 'error',
                'message': f'Session {session_id} not found'
            }
            
        except Exception as e:
            logger.error(f"Error getting federation status: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to get federation status: {str(e)}'
            }
    
    async def _get_federation_session_from_db(self, session_id: str) -> Dict[str, Any]:
        """Get federation session from database."""
        try:
            # Get registry data
            registry_query = "SELECT * FROM federated_learning_registry WHERE registry_id = ?"
            registry_data = await self.connection_manager.fetch_one(registry_query, (session_id,))
            
            if not registry_data:
                return None
            
            # Get metrics data
            metrics_query = "SELECT * FROM federated_learning_metrics WHERE registry_id = ?"
            metrics_data = await self.connection_manager.fetch_one(metrics_query, (session_id,))
            
            # Combine data
            session_data = {
                'session_id': session_id,
                'federation_name': registry_data.get('federation_name'),
                'status': registry_data.get('lifecycle_status'),
                'health_score': registry_data.get('overall_health_score'),
                'performance_score': registry_data.get('performance_score'),
                'created_at': registry_data.get('created_at'),
                'updated_at': registry_data.get('updated_at'),
                'metrics': metrics_data
            }
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error fetching federation session from database: {str(e)}")
            raise 