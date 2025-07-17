"""
Federated Learning Engine
Main coordinator for federated learning across digital twins
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import random

from .twin_processors import (
    AdditiveManufacturingProcessor,
    SmartGridProcessor,
    HydrogenStationProcessor
)
from .cross_twin_learning import CrossTwinLearning
from .federation_server import FederationServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederatedLearningEngine:
    """
    Main federated learning engine for coordinating learning across digital twins
    """
    
    def __init__(self):
        self.twins = {
            'twin_1': {
                'id': 'twin_1',
                'type': 'additive_manufacturing',
                'name': 'Example AAS Additive Manufacturing',
                'health_score': 77.0,
                'status': 'good',
                'uptime': '6d 0h 0m',
                'performance_metrics': {
                    'cpu_usage': 18.0,
                    'memory_usage': 38.0,
                    'response_time': 2.0,
                    'error_rate': 1.5
                },
                'data_characteristics': ['manufacturing_metrics', 'quality_control', 'material_data'],
                'unique_features': ['print_parameters', 'layer_quality', 'material_efficiency'],
                'data_volume': 'medium',
                'update_frequency': 'hourly',
                'privacy_level': 'high',
                'optimization_opportunity': 'Improve health score from 77% to 85%+'
            },
            'twin_2': {
                'id': 'twin_2',
                'type': 'smart_grid_substation',
                'name': 'Example AAS Smart Grid Substation',
                'health_score': 80.9,
                'status': 'good',
                'uptime': '1h 0m',
                'performance_metrics': {
                    'cpu_usage': 5.0,
                    'memory_usage': 43.4,
                    'response_time': 2.0,
                    'error_rate': 0.5
                },
                'data_characteristics': ['power_metrics', 'grid_stability', 'energy_efficiency'],
                'unique_features': ['voltage_control', 'load_balancing', 'fault_detection'],
                'data_volume': 'high',
                'update_frequency': 'real_time',
                'privacy_level': 'critical',
                'optimization_opportunity': 'Maintain high health score, optimize resource usage'
            },
            'twin_3': {
                'id': 'twin_3',
                'type': 'hydrogen_filling_station',
                'name': 'Example AAS Hydrogen Filling Station',
                'health_score': 80.4,
                'status': 'good',
                'uptime': '3d 0h 0m',
                'performance_metrics': {
                    'cpu_usage': 18.0,
                    'memory_usage': 47.2,
                    'response_time': 0.1,
                    'error_rate': 1.5
                },
                'data_characteristics': ['safety_metrics', 'pressure_data', 'flow_rates'],
                'unique_features': ['pressure_control', 'safety_systems', 'efficiency_metrics'],
                'data_volume': 'medium',
                'update_frequency': 'continuous',
                'privacy_level': 'critical',
                'optimization_opportunity': 'Leverage fast response time (0.1s) for real-time optimization'
            }
        }
        
        # Initialize components
        self.federation_server = FederationServer()
        self.cross_twin_learning = CrossTwinLearning()
        self.local_processors = {}
        self.monitoring_system = MonitoringSystem()
        self.performance_tracker = PerformanceTracker()
        
        # Initialize local processors for each twin
        self._initialize_local_processors()
        
        # Federation state
        self.aggregation_round = 0
        self.is_federation_active = False
        self.last_aggregation_time = None
        self.federation_metrics = {}
        
        logger.info("🚀 Federated Learning Engine initialized with 3 digital twins")
    
    def _initialize_local_processors(self):
        """Initialize local data processors for each twin"""
        self.local_processors = {
            'twin_1': AdditiveManufacturingProcessor(),
            'twin_2': SmartGridProcessor(),
            'twin_3': HydrogenStationProcessor()
        }
        logger.info("✅ Local processors initialized for all twins")
    
    def start_federation(self) -> Dict[str, Any]:
        """Start federated learning federation"""
        logger.info("🔄 Starting federated learning federation...")
        
        self.is_federation_active = True
        self.aggregation_round = 0
        
        # Initialize federation server
        self.federation_server.initialize_federation(self.twins)
        
        # Start monitoring
        self.monitoring_system.start_monitoring()
        
        return {
            'status': 'success',
            'message': 'Federated learning federation started',
            'twins_count': len(self.twins),
            'aggregation_round': self.aggregation_round,
            'timestamp': datetime.now().isoformat()
        }
    
    def stop_federation(self) -> Dict[str, Any]:
        """Stop federated learning federation"""
        logger.info("🛑 Stopping federated learning federation...")
        
        self.is_federation_active = False
        
        # Stop monitoring
        self.monitoring_system.stop_monitoring()
        
        return {
            'status': 'success',
            'message': 'Federated learning federation stopped',
            'final_aggregation_round': self.aggregation_round,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_federated_learning_cycle(self) -> Dict[str, Any]:
        """Run one complete federated learning cycle"""
        if not self.is_federation_active:
            return {'error': 'Federation not active'}
        
        cycle_start_time = time.time()
        logger.info(f"🔄 Starting federated learning cycle {self.aggregation_round + 1}")
        
        try:
            # Step 1: Local training on each twin
            local_updates = {}
            for twin_id, processor in self.local_processors.items():
                logger.info(f"📊 Training local model for {twin_id}")
                self.monitoring_system.log_training_start(twin_id)
                
                update = processor.train_local_model(
                    self.federation_server.get_global_model_weights()
                )
                local_updates[twin_id] = update
                
                self.monitoring_system.log_training_complete(twin_id, update)
            
            # Step 2: Federated aggregation
            logger.info("🔗 Aggregating models from all twins")
            self.monitoring_system.log_aggregation_start()
            
            global_model = self.federation_server.aggregate_twin_models(local_updates)
            self.aggregation_round += 1
            
            self.monitoring_system.log_aggregation_complete()
            
            # Step 3: Generate cross-twin insights
            logger.info("🧠 Generating cross-twin insights")
            self.monitoring_system.log_insights_generation_start()
            
            insights = self.cross_twin_learning.generate_cross_twin_insights(global_model)
            
            self.monitoring_system.log_insights_generation_complete()
            
            # Step 4: Distribute enhanced model back to twins
            for twin_id, processor in self.local_processors.items():
                processor.update_model(global_model)
            
            # Step 5: Track performance improvements
            performance_improvements = self.performance_tracker.track_improvements()
            
            cycle_duration = time.time() - cycle_start_time
            self.last_aggregation_time = datetime.now()
            
            # Update federation metrics
            self.federation_metrics = {
                'aggregation_round': self.aggregation_round,
                'cycle_duration': cycle_duration,
                'twin_contributions': self.federation_server.get_twin_contributions(),
                'performance_metrics': self.monitoring_system.get_performance_metrics(),
                'performance_improvements': performance_improvements,
                'insights': insights
            }
            
            logger.info(f"✅ Federated learning cycle {self.aggregation_round} completed in {cycle_duration:.2f}s")
            
            return {
                'status': 'success',
                'aggregation_round': self.aggregation_round,
                'cycle_duration': cycle_duration,
                'global_model': global_model,
                'insights': insights,
                'twin_contributions': self.federation_server.get_twin_contributions(),
                'performance_metrics': self.monitoring_system.get_performance_metrics(),
                'performance_improvements': performance_improvements,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in federated learning cycle: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'aggregation_round': self.aggregation_round
            }
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get current federation status"""
        return {
            'is_active': self.is_federation_active,
            'aggregation_round': self.aggregation_round,
            'last_aggregation_time': self.last_aggregation_time.isoformat() if self.last_aggregation_time else None,
            'twins_count': len(self.twins),
            'twins_status': {twin_id: twin_info for twin_id, twin_info in self.twins.items()},
            'federation_metrics': self.federation_metrics
        }
    
    def get_twin_performance(self, twin_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific twin"""
        if twin_id not in self.twins:
            return {'error': f'Twin {twin_id} not found'}
        
        twin_info = self.twins[twin_id]
        processor = self.local_processors.get(twin_id)
        
        return {
            'twin_id': twin_id,
            'twin_info': twin_info,
            'local_performance': processor.get_performance_metrics() if processor else {},
            'health_score': twin_info['health_score'],
            'optimization_opportunity': twin_info['optimization_opportunity']
        }
    
    def get_cross_twin_insights(self) -> Dict[str, Any]:
        """Get cross-twin learning insights"""
        return self.cross_twin_learning.get_current_insights()
    
    def get_federation_metrics(self) -> Dict[str, Any]:
        """Get detailed federation metrics"""
        return self.federation_metrics


class MonitoringSystem:
    """System for monitoring federated learning activities"""
    
    def __init__(self):
        self.monitoring_active = False
        self.training_logs = {}
        self.aggregation_logs = []
        self.performance_metrics = {}
    
    def start_monitoring(self):
        """Start monitoring system"""
        self.monitoring_active = True
        logger.info("📊 Monitoring system started")
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        self.monitoring_active = False
        logger.info("📊 Monitoring system stopped")
    
    def log_training_start(self, twin_id: str):
        """Log start of training for a twin"""
        self.training_logs[twin_id] = {
            'start_time': datetime.now(),
            'status': 'training'
        }
    
    def log_training_complete(self, twin_id: str, update: Dict[str, Any]):
        """Log completion of training for a twin"""
        if twin_id in self.training_logs:
            self.training_logs[twin_id].update({
                'end_time': datetime.now(),
                'status': 'completed',
                'update_size': len(str(update)),
                'loss': update.get('loss', 0)
            })
    
    def log_aggregation_start(self):
        """Log start of aggregation"""
        self.aggregation_logs.append({
            'start_time': datetime.now(),
            'status': 'aggregating'
        })
    
    def log_aggregation_complete(self):
        """Log completion of aggregation"""
        if self.aggregation_logs:
            self.aggregation_logs[-1].update({
                'end_time': datetime.now(),
                'status': 'completed'
            })
    
    def log_insights_generation_start(self):
        """Log start of insights generation"""
        pass
    
    def log_insights_generation_complete(self):
        """Log completion of insights generation"""
        pass
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            'monitoring_active': self.monitoring_active,
            'training_logs': self.training_logs,
            'aggregation_logs': self.aggregation_logs,
            'metrics': self.performance_metrics
        }


class PerformanceTracker:
    """Track performance improvements across federated learning cycles"""
    
    def __init__(self):
        self.improvement_history = []
        self.baseline_metrics = {}
    
    def track_improvements(self) -> Dict[str, Any]:
        """Track performance improvements"""
        # Simulate performance improvements
        improvements = {
            'twin_1': {
                'health_score_improvement': 2.1,
                'cpu_optimization': 1.5,
                'memory_optimization': 2.0
            },
            'twin_2': {
                'health_score_improvement': 1.8,
                'cpu_optimization': 0.8,
                'memory_optimization': 1.2
            },
            'twin_3': {
                'health_score_improvement': 1.9,
                'cpu_optimization': 1.2,
                'memory_optimization': 1.8
            }
        }
        
        self.improvement_history.append({
            'timestamp': datetime.now().isoformat(),
            'improvements': improvements
        })
        
        return improvements 