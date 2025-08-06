"""
Simulation Service

Handles business logic for physics simulation execution, monitoring, and management.
Integrated with the shared DigitalTwin database architecture.
"""

import logging
import uuid
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, BackgroundTasks

# Import shared database components
try:
    from src.shared.database.base_manager import BaseDatabaseManager
    from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
    from src.shared.models.digital_twin import DigitalTwin
    from src.shared.services.digital_twin_service import DigitalTwinService
except ImportError as e:
    logging.error(f"Shared database components not available: {e}")
    raise

# Import the physics modeling framework
try:
    from src.physics_modeling import DynamicPhysicsModelingFramework
    from src.physics_modeling.core.dynamic_types import PhysicsPlugin
    from src.physics_modeling.core.plugin_manager import PluginManager
    from src.physics_modeling.core.model_factory import ModelFactory
    from src.physics_modeling.simulation.simulation_engine import SimulationEngine
except ImportError as e:
    logging.warning(f"Physics Modeling modules not available: {e}")
    DynamicPhysicsModelingFramework = None
    PhysicsPlugin = None
    PluginManager = None
    ModelFactory = None
    SimulationEngine = None

logger = logging.getLogger(__name__)


class SimulationService:
    """Service for managing physics simulations using DigitalTwin data"""
    
    def __init__(self, db_manager: BaseDatabaseManager = None, digital_twin_service: DigitalTwinService = None):
        self.db_manager = db_manager
        self.digital_twin_repository = DigitalTwinRepository(db_manager) if db_manager else None
        self.digital_twin_service = digital_twin_service
        self.physics_framework = None
        self.active_simulations = {}  # In-memory storage for simulation status
        self._initialize_framework()
    
    def _initialize_framework(self):
        """Initialize the physics modeling framework"""
        if DynamicPhysicsModelingFramework is None:
            logger.error("Physics Modeling Framework not available")
            return
            
        try:
            self.physics_framework = DynamicPhysicsModelingFramework()
            logger.info("Physics Modeling Framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Physics Modeling Framework: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize Physics Modeling Framework"
            )
    
    def run_simulation(self, model_id: str, simulation_type: str, 
                      parameters: Optional[Dict[str, Any]] = None,
                      time_range: Optional[Dict[str, float]] = None,
                      output_format: str = "json") -> Dict[str, Any]:
        """
        Start a new simulation
        
        Args:
            model_id: ID of the physics model to simulate
            simulation_type: Type of simulation (steady_state, transient, optimization)
            parameters: Simulation parameters
            time_range: Time range for transient simulations
            output_format: Output format (json, csv, hdf5)
            
        Returns:
            Simulation response with simulation details
        """
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        try:
            # Generate unique simulation ID
            simulation_id = str(uuid.uuid4())
            
            # Validate model exists
            model = self.physics_framework.get_model(model_id)
            if not model:
                raise HTTPException(
                    status_code=404,
                    detail=f"Physics model {model_id} not found"
                )
            
            # Create simulation configuration
            simulation_config = {
                "simulation_id": simulation_id,
                "model_id": model_id,
                "simulation_type": simulation_type,
                "parameters": parameters or {},
                "time_range": time_range or {},
                "output_format": output_format,
                "started_at": datetime.utcnow().isoformat(),
                "status": "starting"
            }
            
            # Store simulation status
            self.active_simulations[simulation_id] = {
                "status": "starting",
                "progress": 0.0,
                "started_at": datetime.utcnow(),
                "model_id": model_id,
                "simulation_type": simulation_type,
                "parameters": parameters,
                "results": None,
                "error": None
            }
            
            # Start simulation in background
            asyncio.create_task(
                self._run_simulation_background(
                    simulation_id, model_id, simulation_type, 
                    parameters, time_range, output_format
                )
            )
            
            return {
                "simulation_id": simulation_id,
                "model_id": model_id,
                "status": "starting",
                "progress": 0.0,
                "results": None,
                "visualization_data": None,
                "execution_time": 0.0,
                "error": None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start simulation: {str(e)}"
            )
    
    async def _run_simulation_background(self, simulation_id: str, model_id: str,
                                       simulation_type: str, parameters: Optional[Dict[str, Any]],
                                       time_range: Optional[Dict[str, float]], output_format: str):
        """
        Run simulation in background task
        
        Args:
            simulation_id: ID of the simulation
            model_id: ID of the physics model
            simulation_type: Type of simulation
            parameters: Simulation parameters
            time_range: Time range for transient simulations
            output_format: Output format
        """
        start_time = time.time()
        
        try:
            # Update status to running
            if simulation_id in self.active_simulations:
                self.active_simulations[simulation_id]["status"] = "running"
                self.active_simulations[simulation_id]["progress"] = 10.0
            
            # Run the simulation using the framework
            simulation_results = await self.physics_framework.run_simulation_async(
                model_id=model_id,
                simulation_type=simulation_type,
                parameters=parameters,
                time_range=time_range,
                output_format=output_format,
                progress_callback=lambda progress: self._update_simulation_progress(simulation_id, progress)
            )
            
            # Update final status
            execution_time = time.time() - start_time
            if simulation_id in self.active_simulations:
                self.active_simulations[simulation_id].update({
                    "status": "completed",
                    "progress": 100.0,
                    "results": simulation_results,
                    "execution_time": execution_time,
                    "completed_at": datetime.utcnow()
                })
            
            logger.info(f"Simulation {simulation_id} completed successfully in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Simulation {simulation_id} failed: {e}")
            
            if simulation_id in self.active_simulations:
                self.active_simulations[simulation_id].update({
                    "status": "failed",
                    "progress": 0.0,
                    "error": str(e),
                    "execution_time": execution_time,
                    "failed_at": datetime.utcnow()
                })
    
    def _update_simulation_progress(self, simulation_id: str, progress: float):
        """Update simulation progress"""
        if simulation_id in self.active_simulations:
            self.active_simulations[simulation_id]["progress"] = progress
    
    def get_simulation_status(self, simulation_id: str) -> Dict[str, Any]:
        """
        Get simulation status and progress
        
        Args:
            simulation_id: ID of the simulation
            
        Returns:
            Simulation status and details
        """
        if simulation_id not in self.active_simulations:
            raise HTTPException(
                status_code=404,
                detail=f"Simulation {simulation_id} not found"
            )
        
        simulation = self.active_simulations[simulation_id]
        
        # Calculate execution time
        execution_time = 0.0
        if simulation["started_at"]:
            if simulation["status"] in ["completed", "failed"]:
                end_time = simulation.get("completed_at") or simulation.get("failed_at")
                if end_time:
                    execution_time = (end_time - simulation["started_at"]).total_seconds()
            else:
                execution_time = (datetime.utcnow() - simulation["started_at"]).total_seconds()
        
        return {
            "simulation_id": simulation_id,
            "model_id": simulation["model_id"],
            "status": simulation["status"],
            "progress": simulation["progress"],
            "results": simulation.get("results"),
            "visualization_data": simulation.get("visualization_data"),
            "execution_time": execution_time,
            "error": simulation.get("error"),
            "started_at": simulation["started_at"].isoformat() if simulation["started_at"] else None,
            "completed_at": simulation.get("completed_at").isoformat() if simulation.get("completed_at") else None
        }
    
    def cancel_simulation(self, simulation_id: str) -> Dict[str, Any]:
        """
        Cancel a running simulation
        
        Args:
            simulation_id: ID of the simulation to cancel
            
        Returns:
            Cancellation confirmation
        """
        if simulation_id not in self.active_simulations:
            raise HTTPException(
                status_code=404,
                detail=f"Simulation {simulation_id} not found"
            )
        
        simulation = self.active_simulations[simulation_id]
        
        if simulation["status"] not in ["starting", "running"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel simulation in {simulation['status']} status"
            )
        
        try:
            # Cancel simulation in framework
            if self.physics_framework:
                self.physics_framework.cancel_simulation(simulation_id)
            
            # Update status
            simulation.update({
                "status": "cancelled",
                "progress": 0.0,
                "cancelled_at": datetime.utcnow()
            })
            
            return {
                "simulation_id": simulation_id,
                "status": "cancelled",
                "cancelled_at": simulation["cancelled_at"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel simulation {simulation_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to cancel simulation: {str(e)}"
            )
    
    def get_simulation_results(self, simulation_id: str) -> Dict[str, Any]:
        """
        Get detailed simulation results
        
        Args:
            simulation_id: ID of the simulation
            
        Returns:
            Detailed simulation results
        """
        if simulation_id not in self.active_simulations:
            raise HTTPException(
                status_code=404,
                detail=f"Simulation {simulation_id} not found"
            )
        
        simulation = self.active_simulations[simulation_id]
        
        if simulation["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Simulation {simulation_id} is not completed (status: {simulation['status']})"
            )
        
        return {
            "simulation_id": simulation_id,
            "model_id": simulation["model_id"],
            "simulation_type": simulation["simulation_type"],
            "parameters": simulation["parameters"],
            "results": simulation["results"],
            "visualization_data": simulation.get("visualization_data"),
            "execution_time": simulation.get("execution_time", 0.0),
            "started_at": simulation["started_at"].isoformat() if simulation["started_at"] else None,
            "completed_at": simulation.get("completed_at").isoformat() if simulation.get("completed_at") else None
        }
    
    def list_simulations(self, model_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List simulations with optional filtering
        
        Args:
            model_id: Optional model ID to filter by
            status: Optional status to filter by
            
        Returns:
            List of simulation summaries
        """
        simulations = []
        
        for sim_id, simulation in self.active_simulations.items():
            # Apply filters
            if model_id and simulation["model_id"] != model_id:
                continue
            if status and simulation["status"] != status:
                continue
            
            # Calculate execution time
            execution_time = 0.0
            if simulation["started_at"]:
                if simulation["status"] in ["completed", "failed"]:
                    end_time = simulation.get("completed_at") or simulation.get("failed_at")
                    if end_time:
                        execution_time = (end_time - simulation["started_at"]).total_seconds()
                else:
                    execution_time = (datetime.utcnow() - simulation["started_at"]).total_seconds()
            
            simulations.append({
                "simulation_id": sim_id,
                "model_id": simulation["model_id"],
                "simulation_type": simulation["simulation_type"],
                "status": simulation["status"],
                "progress": simulation["progress"],
                "execution_time": execution_time,
                "started_at": simulation["started_at"].isoformat() if simulation["started_at"] else None,
                "error": simulation.get("error")
            })
        
        # Sort by start time (newest first)
        simulations.sort(key=lambda x: x["started_at"] or "", reverse=True)
        
        return simulations
    
    def get_active_simulations_count(self) -> int:
        """Get count of active simulations"""
        return len([
            sim for sim in self.active_simulations.values() 
            if sim["status"] in ["starting", "running"]
        ])
    
    def cleanup_completed_simulations(self, max_age_hours: int = 24):
        """
        Clean up old completed simulations to free memory
        
        Args:
            max_age_hours: Maximum age in hours for completed simulations
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for sim_id, simulation in self.active_simulations.items():
            if simulation["status"] in ["completed", "failed", "cancelled"]:
                if simulation.get("completed_at") or simulation.get("failed_at") or simulation.get("cancelled_at"):
                    end_time = simulation.get("completed_at") or simulation.get("failed_at") or simulation.get("cancelled_at")
                    if end_time < cutoff_time:
                        to_remove.append(sim_id)
        
        for sim_id in to_remove:
            del self.active_simulations[sim_id]
            logger.info(f"Cleaned up old simulation {sim_id}")
        
        return len(to_remove)
    
    def run_simulation_on_twin(self, twin_id: str, simulation_type: str,
                              parameters: Optional[Dict[str, Any]] = None,
                              time_range: Optional[Dict[str, float]] = None,
                              output_format: str = "json") -> Dict[str, Any]:
        """
        Run simulation on DigitalTwin using extracted data
        
        Args:
            twin_id: ID of the digital twin to simulate
            simulation_type: Type of simulation (steady_state, transient, optimization)
            parameters: Simulation parameters
            time_range: Time range for transient simulations
            output_format: Output format (json, csv, hdf5)
            
        Returns:
            Simulation response with simulation details
        """
        if not self.digital_twin_repository:
            raise HTTPException(
                status_code=503,
                detail="Digital Twin Repository not available"
            )
        
        if not self.physics_framework:
            raise HTTPException(
                status_code=503,
                detail="Physics Modeling system not available"
            )
        
        try:
            # Get the digital twin
            twin = self.digital_twin_repository.get_by_id(twin_id)
            if not twin:
                raise HTTPException(
                    status_code=404,
                    detail=f"Digital twin {twin_id} not found"
                )
            
            # Check if twin has extracted data
            if not twin.extracted_data_path:
                raise HTTPException(
                    status_code=400,
                    detail=f"Digital twin {twin_id} has no extracted data for simulation"
                )
            
            # Load extracted data
            try:
                with open(twin.extracted_data_path, 'r') as f:
                    extracted_data = json.load(f)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to load extracted data: {str(e)}"
                )
            
            # Generate unique simulation ID
            simulation_id = str(uuid.uuid4())
            
            # Create simulation configuration
            simulation_config = {
                "simulation_id": simulation_id,
                "twin_id": twin_id,
                "simulation_type": simulation_type,
                "parameters": parameters or {},
                "time_range": time_range or {},
                "output_format": output_format,
                "started_at": datetime.utcnow(),
                "status": "starting",
                "extracted_data": extracted_data
            }
            
            # Store simulation in memory for tracking
            self.active_simulations[simulation_id] = simulation_config
            
            # Update twin simulation status
            self.digital_twin_repository.update_physics_modeling(
                twin_id=twin_id,
                physics_data={
                    "simulation_status": "running",
                    "model_version": f"sim_{simulation_id}"
                }
            )
            
            # Start background simulation
            asyncio.create_task(
                self._run_twin_simulation_background(
                    simulation_id, twin_id, simulation_type, 
                    parameters, time_range, output_format, extracted_data
                )
            )
            
            logger.info(f"Started simulation {simulation_id} on twin {twin_id}")
            
            return {
                "simulation_id": simulation_id,
                "twin_id": twin_id,
                "simulation_type": simulation_type,
                "status": "starting",
                "started_at": simulation_config["started_at"].isoformat(),
                "message": f"Simulation started on {twin.twin_name}"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to start simulation on twin {twin_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start simulation: {str(e)}"
            )
    
    async def _run_twin_simulation_background(self, simulation_id: str, twin_id: str,
                                            simulation_type: str, parameters: Optional[Dict[str, Any]],
                                            time_range: Optional[Dict[str, float]], output_format: str,
                                            extracted_data: Dict[str, Any]):
        """Run simulation in background using DigitalTwin data"""
        try:
            # Update status to running
            self.active_simulations[simulation_id]["status"] = "running"
            
            # Run simulation using physics framework
            simulation_results = await self.physics_framework.run_simulation_async(
                simulation_id=simulation_id,
                twin_id=twin_id,
                simulation_type=simulation_type,
                parameters=parameters,
                time_range=time_range,
                output_format=output_format,
                extracted_data=extracted_data
            )
            
            # Update simulation status
            self.active_simulations[simulation_id].update({
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "results": simulation_results
            })
            
            # Store results in DigitalTwin
            self.digital_twin_repository.update_simulation_run(
                twin_id=twin_id,
                simulation_results=simulation_results
            )
            
            # Update twin simulation status
            self.digital_twin_repository.update_physics_modeling(
                twin_id=twin_id,
                physics_data={
                    "simulation_status": "completed",
                    "last_simulation_run": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Completed simulation {simulation_id} on twin {twin_id}")
            
        except Exception as e:
            logger.error(f"Simulation {simulation_id} failed: {e}")
            
            # Update simulation status to failed
            self.active_simulations[simulation_id].update({
                "status": "failed",
                "failed_at": datetime.utcnow(),
                "error": str(e)
            })
            
            # Update twin simulation status
            self.digital_twin_repository.update_physics_modeling(
                twin_id=twin_id,
                physics_data={
                    "simulation_status": "failed",
                    "last_error_message": str(e)
                }
            ) 