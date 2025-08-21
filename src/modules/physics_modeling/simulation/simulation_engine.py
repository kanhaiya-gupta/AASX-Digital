"""
Simulation engine for physics modeling framework.

This module provides the simulation engine that orchestrates the complete
simulation workflow from data loading to result storage.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base_simulation import BaseSimulation
from .result_processor import ResultProcessor
from src.shared.models.digital_twin import DigitalTwin

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Common simulation orchestration.
    
    This class handles the complete simulation workflow:
    - Loading digital twin data
    - Running plugin simulations
    - Processing results
    - Storing results in database
    """
    
    def __init__(self, digital_twin_repository, plugin_manager, file_repository=None):
        """
        Initialize the simulation engine.
        
        Args:
            digital_twin_repository: Repository for digital twins
            plugin_manager: Plugin manager instance
            file_repository: Repository for files (for tracing)
        """
        self.digital_twin_repo = digital_twin_repository
        self.plugin_manager = plugin_manager
        self.file_repo = file_repository
        self.result_processor = ResultProcessor()
        
        logger.info("Simulation engine initialized")
    
    def _get_trace_info(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace information for a twin (file_id).
        
        Args:
            twin_id: Digital twin ID (equals file_id)
            
        Returns:
            Trace information dictionary or None if not found
        """
        try:
            if not self.file_repo:
                logger.warning("File repository not available for tracing")
                return None
            
            trace_info = self.file_repo.get_file_trace_info(twin_id)
            if trace_info:
                logger.debug(f"Retrieved trace info for twin {twin_id}: {trace_info.get('use_case_name')} -> {trace_info.get('project_name')}")
                return trace_info
            else:
                logger.warning(f"No trace info found for twin: {twin_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get trace info for twin {twin_id}: {e}")
            return None
    
    def run_simulation_with_plugin(self, twin_id: str, plugin_id: str, 
                                  parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run a complete physics simulation using a specific plugin.
        
        Args:
            twin_id: Digital twin ID
            plugin_id: Plugin ID to use for simulation
            parameters: Simulation parameters
            
        Returns:
            Simulation results or None if simulation failed
        """
        try:
            logger.info(f"Starting simulation for twin {twin_id} with plugin {plugin_id}")
            
            # 1. Get plugin by ID
            plugin_info = self.plugin_manager.get_plugin_by_id(plugin_id)
            if not plugin_info:
                logger.error(f"Plugin {plugin_id} not found")
                return None
            
            # 2. Get digital twin and extracted data
            twin = self.digital_twin_repo.get_by_id(twin_id)
            if not twin:
                logger.error(f"Digital twin not found: {twin_id}")
                return None
            
            extracted_data = self._load_extracted_data(twin)
            if extracted_data is None:
                logger.error(f"Failed to load extracted data for twin: {twin_id}")
                return None
            
            # 3. Get the actual plugin instance
            plugin = self.plugin_manager.get_plugin_instance(plugin_id)
            if not plugin:
                logger.error(f"Plugin instance not found for plugin {plugin_id}")
                return None
            
            # 4. Run the plugin simulation
            plugin_results = self._run_plugin_simulation(plugin, parameters, extracted_data)
            if plugin_results is None:
                logger.error(f"Plugin simulation failed for twin {twin_id}")
                return None
            
            # 5. Process results
            processed_results = self.result_processor.process_results(plugin_results)
            
            # 6. Store results in twin
            physics_type = plugin_info.get('name', 'unknown')
            self._store_results_in_twin(twin, processed_results, physics_type)
            
            # 7. Prepare final results
            final_results = self._prepare_final_results(
                processed_results, None, twin_id, physics_type
            )
            
            logger.info(f"Simulation completed successfully for twin {twin_id}")
            return final_results
            
        except Exception as e:
            logger.error(f"Failed to run simulation with plugin {plugin_id} for twin {twin_id}: {e}")
            return None

    def run_simulation(self, twin_id: str, physics_type: str, 
                      parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run a complete physics simulation.
        
        Args:
            twin_id: Digital twin ID
            physics_type: Physics type identifier
            parameters: Simulation parameters
            
        Returns:
            Simulation results or None if simulation failed
        """
        try:
            logger.info(f"Starting simulation for twin {twin_id} with physics type {physics_type}")
            
            # 1. Get digital twin and extracted data
            twin = self.digital_twin_repo.get_by_id(twin_id)
            if not twin:
                logger.error(f"Digital twin not found: {twin_id}")
                return None
            
            extracted_data = self._load_extracted_data(twin)
            if extracted_data is None:
                logger.error(f"Failed to load extracted data for twin: {twin_id}")
                return None
            
            # 2. Get trace information (use case, project, file context)
            trace_info = self._get_trace_info(twin_id)
            if trace_info:
                # Enhance extracted data with trace information
                extracted_data['trace_info'] = {
                    'use_case_name': trace_info.get('use_case_name'),
                    'use_case_category': trace_info.get('use_case_category'),
                    'project_name': trace_info.get('project_name'),
                    'file_name': trace_info.get('filename'),
                    'original_filename': trace_info.get('original_filename')
                }
                logger.info(f"Added trace info for simulation: {trace_info.get('use_case_name')} -> {trace_info.get('project_name')} -> {trace_info.get('filename')}")
            else:
                logger.warning(f"Could not get trace info for twin: {twin_id}")
            
            # 3. Get plugin
            plugin = self.plugin_manager.get_plugin(physics_type)
            if not plugin:
                logger.error(f"Physics plugin not found: {physics_type}")
                return None
            
            # 4. Create base simulation
            simulation = BaseSimulation(extracted_data, parameters)
            
            # 5. Preprocess data
            preprocessed_data = simulation.preprocess()
            if not preprocessed_data:
                logger.error("Preprocessing failed")
                return None
            
            # 6. Run plugin simulation
            raw_results = self._run_plugin_simulation(plugin, parameters, extracted_data)
            if raw_results is None:
                logger.error("Plugin simulation failed")
                return None
            
            # 7. Store results in simulation object
            simulation.results = raw_results
            
            # 8. Postprocess results
            postprocessed_results = simulation.postprocess()
            if not postprocessed_results:
                logger.error("Postprocessing failed")
                return None
            
            # 8. Process results
            processed_results = self.result_processor.process_results(raw_results)
            
            # 9. Store results in digital twin
            self._store_results_in_twin(twin, processed_results, physics_type)
            
            # 10. Mark simulation as completed
            simulation.mark_completed()
            
            # 11. Prepare final results
            final_results = self._prepare_final_results(
                processed_results, simulation, twin_id, physics_type
            )
            
            logger.info(f"Simulation completed successfully for twin {twin_id}")
            return final_results
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return None
    
    def _load_extracted_data(self, twin: DigitalTwin) -> Optional[Dict[str, Any]]:
        """
        Load extracted data from digital twin.
        
        Args:
            twin: Digital twin instance
            
        Returns:
            Extracted data dictionary or None if loading failed
        """
        try:
            if not twin.extracted_data_path:
                logger.warning(f"No extracted data path for twin: {twin.twin_id}")
                return {}
            
            # This is a simplified version - in practice, you'd load from the actual path
            # For now, we'll return the physics_context if available
            if twin.physics_context:
                try:
                    return json.loads(twin.physics_context)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in physics_context for twin: {twin.twin_id}")
                    return {}
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to load extracted data for twin {twin.twin_id}: {e}")
            return None
    
    def _run_plugin_simulation(self, plugin, parameters: Dict[str, Any], 
                              extracted_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run the plugin simulation.
        
        Args:
            plugin: Physics plugin instance
            parameters: Simulation parameters
            extracted_data: Extracted data from ETL
            
        Returns:
            Raw simulation results or None if failed
        """
        try:
            # Set model data in plugin
            plugin.model_data = extracted_data
            
            # Run plugin's solve method
            raw_results = plugin.solve(parameters)
            
            if not isinstance(raw_results, dict):
                logger.error("Plugin solve() method must return a dictionary")
                return None
            
            logger.debug(f"Plugin simulation completed with {len(raw_results)} results")
            return raw_results
            
        except Exception as e:
            logger.error(f"Plugin simulation failed: {e}")
            return None
    
    def _store_results_in_twin(self, twin: DigitalTwin, results: Dict[str, Any], 
                              physics_type: str):
        """
        Store simulation results in digital twin.
        
        Args:
            twin: Digital twin instance
            results: Simulation results
            physics_type: Physics type identifier
        """
        try:
            # Initialize simulation history if not exists
            if not twin.simulation_history:
                twin.simulation_history = []
            
            # Create simulation record
            simulation_record = {
                'timestamp': datetime.now().isoformat(),
                'physics_type': physics_type,
                'results': results,
                'status': 'completed'
            }
            
            # Add to simulation history
            twin.simulation_history.append(simulation_record)
            
            # Update simulation status
            twin.simulation_status = 'completed'
            twin.last_simulation_run = datetime.now().isoformat()
            
            # Update digital twin in database
            self.digital_twin_repo.update(twin)
            
            logger.info(f"Results stored in digital twin: {twin.twin_id}")
            
        except Exception as e:
            logger.error(f"Failed to store results in digital twin: {e}")
    
    def _prepare_final_results(self, processed_results: Dict[str, Any], 
                              simulation: BaseSimulation, twin_id: str, 
                              physics_type: str) -> Dict[str, Any]:
        """
        Prepare final results for return.
        
        Args:
            processed_results: Processed simulation results
            simulation: Base simulation instance
            twin_id: Digital twin ID
            physics_type: Physics type identifier
            
        Returns:
            Final results dictionary
        """
        return {
            'simulation_id': f"{twin_id}_{physics_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'twin_id': twin_id,
            'physics_type': physics_type,
            'results': processed_results,
            'metadata': {
                'simulation_duration': simulation.get_simulation_duration(),
                'validation_errors': simulation.get_validation_errors(),
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            },
            'preprocessing': simulation.preprocessed_data,
            'postprocessing': simulation.postprocessed_results
        }
    
    def get_simulation_history(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation history for a digital twin.
        
        Args:
            twin_id: Digital twin ID
            
        Returns:
            Simulation history or None if not found
        """
        try:
            twin = self.digital_twin_repo.get_by_id(twin_id)
            if twin and twin.simulation_history:
                return {
                    'twin_id': twin_id,
                    'total_simulations': len(twin.simulation_history),
                    'last_simulation': twin.last_simulation_run,
                    'simulation_status': twin.simulation_status,
                    'history': twin.simulation_history
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get simulation history: {e}")
            return None
    
    def validate_simulation_setup(self, twin_id: str, physics_type: str, 
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate simulation setup before running.
        
        Args:
            twin_id: Digital twin ID
            physics_type: Physics type identifier
            parameters: Simulation parameters
            
        Returns:
            Validation results
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check if digital twin exists
            twin = self.digital_twin_repo.get_by_id(twin_id)
            if not twin:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Digital twin not found: {twin_id}")
            
            # Check if plugin exists
            plugin = self.plugin_manager.get_plugin(physics_type)
            if not plugin:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Physics plugin not found: {physics_type}")
            else:
                # Validate parameters with plugin
                param_errors = plugin.validate_input(parameters)
                if param_errors:
                    validation_results['valid'] = False
                    validation_results['errors'].extend([
                        f"Parameter '{key}': {error}" 
                        for key, error in param_errors.items()
                    ])
            
            # Check if twin has extracted data
            if twin and not twin.extracted_data_path and not twin.physics_context:
                validation_results['warnings'].append("No extracted data found for digital twin")
            
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results 