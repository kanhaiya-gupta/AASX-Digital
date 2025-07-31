"""
Digital Twin Service
===================

Business logic for digital twin management in the AAS Data Modeling framework.
Handles twin registration, status management, and file relationships.
"""

import json
from typing import List, Optional, Dict, Any
from .base_service import BaseService
from ..models.digital_twin import DigitalTwin
from ..repositories.digital_twin_repository import DigitalTwinRepository
from ..repositories.file_repository import FileRepository
from ..repositories.project_repository import ProjectRepository

class DigitalTwinService(BaseService[DigitalTwin]):
    """Service for digital twin business logic."""
    
    def __init__(self, db_manager, file_repository: FileRepository, project_repository: ProjectRepository):
        super().__init__(db_manager)
        self.file_repository = file_repository
        self.project_repository = project_repository
    
    def get_repository(self) -> DigitalTwinRepository:
        """Get the digital twin repository."""
        return DigitalTwinRepository(self.db_manager)
    
    def register_digital_twin(self, file_id: str, twin_data: Dict[str, Any]) -> DigitalTwin:
        """Register a digital twin for a file with business validation."""
        # Validate business rules
        self._validate_twin_registration(file_id, twin_data)
        
        # Check if twin already exists for this file
        existing_twin = self.get_repository().get_by_file_id(file_id)
        if existing_twin:
            if existing_twin.status == "active":
                self._raise_business_error(f"Digital twin already exists for file {file_id} with active status")
            else:
                # Update existing twin
                return self._update_existing_twin(existing_twin.id, twin_data)
        
        # Generate twin name if not provided
        if not twin_data.get("twin_name"):
            twin_data["twin_name"] = self._generate_twin_name(file_id)
        
        # Get file information to get project_id
        file_info = self.file_repository.get_by_id(file_id)
        if not file_info:
            self._raise_business_error(f"File {file_id} not found")
        
        project_id = file_info.project_id if hasattr(file_info, 'project_id') else file_info.get('project_id')
        if not project_id:
            self._raise_business_error(f"File {file_id} is not associated with any project")
        
        # Set file_id for the digital twin
        twin_data["file_id"] = file_id
        
        # Create twin using the custom repository method
        twin_result = self.get_repository().create(
            project_id=project_id,
            file_id=file_id,
            twin_data=twin_data
        )
        
        # Convert result to DigitalTwin object if needed
        if isinstance(twin_result, dict):
            twin = self.get_repository().model_class.from_dict(twin_result)
        else:
            twin = twin_result
        
        self.logger.info(f"Registered digital twin: {twin.twin_name} for file: {file_id}")
        return twin
    
    def get_twin_with_file_info(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin with complete file information."""
        twin = self.get_by_id(twin_id)
        if not twin:
            return None
        
        # Get file information
        file = self.file_repository.get_by_id(twin.file_id)
        
        # Get project and use case information
        project_info = None
        if file:
            project_info = self.project_repository.get_project_hierarchy_info(file.project_id)
        
        return {
            "twin": twin,
            "file": file,
            "project_info": project_info
        }
    
    def get_twins_by_status(self, status: str) -> List[DigitalTwin]:
        """Get all digital twins with a specific status."""
        valid_statuses = ["created", "processing", "active", "failed", "archived"]
        if status not in valid_statuses:
            self._raise_business_error(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        return self.get_repository().get_by_status(status)
    
    def get_active_twins(self) -> List[DigitalTwin]:
        """Get all active digital twins."""
        return self.get_repository().get_active_twins()
    
    def update_twin_status(self, twin_id: str, new_status: str) -> bool:
        """Update digital twin status with business validation."""
        # Validate twin exists
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        # Validate status
        valid_statuses = ["created", "processing", "active", "failed", "archived"]
        if new_status not in valid_statuses:
            self._raise_business_error(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Validate status transition
        self._validate_status_transition(twin.status, new_status)
        
        # Update status
        update_data = {"status": new_status}
        success = self.update(twin_id, update_data)
        
        if success:
            self.logger.info(f"Updated twin {twin_id} status from {twin.status} to {new_status}")
        
        return success
    
    def deactivate_twin(self, twin_id: str) -> bool:
        """Deactivate a digital twin."""
        return self.update_twin_status(twin_id, "inactive")
    
    def orphan_twin(self, twin_id: str) -> bool:
        """Mark a digital twin as orphaned (file deleted)."""
        return self.update_twin_status(twin_id, "orphaned")
    
    def search_twins(self, search_term: str) -> List[DigitalTwin]:
        """Search digital twins by name."""
        if not search_term or len(search_term.strip()) < 2:
            self._raise_business_error("Search term must be at least 2 characters")
        
        return self.get_repository().search_twins(search_term.strip())
    
    def get_twin_statistics(self) -> Dict[str, Any]:
        """Get comprehensive digital twin statistics."""
        return self.get_repository().get_twin_statistics()
    
    def check_twin_exists(self, file_id: str) -> bool:
        """Check if a digital twin exists for a file."""
        return self.get_repository().check_twin_exists(file_id)
    
    def get_twin_by_file_id(self, file_id: str) -> Optional[DigitalTwin]:
        """Get digital twin by file ID."""
        return self.get_repository().get_by_file_id(file_id)
    
    # Health monitoring methods
    def update_health_status(self, twin_id: str, health_status: str, health_score: int) -> bool:
        """Update twin health status and score."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        update_data = {
            "health_status": health_status,
            "health_score": health_score,
            "last_health_check": self._get_current_timestamp()
        }
        
        success = self.update(twin_id, update_data)
        if success:
            self.logger.info(f"Updated health status for twin {twin_id}: {health_status} (score: {health_score})")
        
        return success
    
    def record_error(self, twin_id: str, error_message: str) -> bool:
        """Record an error for a twin and update health score."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        update_data = {
            "error_count": twin.error_count + 1,
            "last_error_message": error_message,
            "last_health_check": self._get_current_timestamp()
        }
        
        # Update health score based on new error
        twin.error_count = update_data["error_count"]
        twin.last_error_message = error_message
        twin.update_health_score()
        
        update_data["health_score"] = twin.health_score
        update_data["health_status"] = twin.health_status
        
        success = self.update(twin_id, update_data)
        if success:
            self.logger.warning(f"Recorded error for twin {twin_id}: {error_message}")
        
        return success
    
    def perform_health_check(self, twin_id: str) -> Dict[str, Any]:
        """Perform comprehensive health check on a twin."""
        twin = self.get_by_id(twin_id)
        if not twin:
            return {"status": "error", "message": "Twin not found"}
        
        # Perform health checks
        health_checks = {
            "etl_status": self._check_etl_status(twin),
            "data_integrity": self._check_data_integrity(twin),
            "physics_context": self._check_physics_context(twin),
            "system_integration": self._check_system_integration(twin)
        }
        
        # Calculate overall health score
        overall_score = self._calculate_overall_health_score(health_checks)
        health_status = self._determine_health_status(overall_score)
        
        # Update twin health
        self.update_health_status(twin_id, health_status, overall_score)
        
        return {
            "twin_id": twin_id,
            "health_status": health_status,
            "health_score": overall_score,
            "checks": health_checks,
            "timestamp": self._get_current_timestamp()
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all twins."""
        all_twins = self.get_all()
        
        health_summary = {
            "total_twins": len(all_twins),
            "active_twins": len([t for t in all_twins if t.status == "active"]),
            "healthy": len([t for t in all_twins if t.health_status == "healthy"]),
            "warning": len([t for t in all_twins if t.health_status == "warning"]),
            "critical": len([t for t in all_twins if t.health_status == "critical"]),
            "offline": len([t for t in all_twins if t.health_status == "offline"]),
            "average_health_score": sum(t.health_score for t in all_twins) / len(all_twins) if all_twins else 0,
            "health_distribution": {
                "healthy": len([t for t in all_twins if t.health_status == "healthy"]),
                "warning": len([t for t in all_twins if t.health_status == "warning"]),
                "critical": len([t for t in all_twins if t.health_status == "critical"]),
                "offline": len([t for t in all_twins if t.health_status == "offline"])
            }
        }
        
        return health_summary
    
    # ETL integration methods
    def update_etl_status(self, twin_id: str, etl_success: bool, extracted_data_path: str = None) -> bool:
        """Update twin ETL status after ETL completion."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        if etl_success:
            # First transition to processing if not already there
            if twin.status == "created":
                self.update_twin_status(twin_id, "processing")
            
            # Then update with ETL data
            update_data = {
                "extracted_data_path": extracted_data_path,
                "last_health_check": self._get_current_timestamp()
            }
            self.logger.info(f"ETL completed successfully for twin {twin_id}")
        else:
            update_data = {
                "status": "failed",
                "last_health_check": self._get_current_timestamp()
            }
            self.logger.error(f"ETL failed for twin {twin_id}")
        
        success = self.update(twin_id, update_data)
        return success
    
    def update_physics_context(self, twin_id: str, physics_context: Dict[str, Any]) -> bool:
        """Update twin physics context with extracted parameters."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        update_data = {
            "physics_context": physics_context,
            "last_health_check": self._get_current_timestamp()
        }
        
        success = self.update(twin_id, update_data)
        if success:
            self.logger.info(f"Updated physics context for twin {twin_id}")
        
        return success
    
    def mark_twin_active(self, twin_id: str) -> bool:
        """Mark twin as active after successful ETL and health check."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        # Calculate health score based on current state
        health_score = twin.calculate_health_score()
        
        # Update status and health, preserving existing data
        update_data = {
            "status": "active",
            "health_status": "healthy" if health_score >= 80 else "warning" if health_score >= 50 else "critical",
            "health_score": health_score,
            "last_health_check": self._get_current_timestamp(),
            # Preserve existing data that was set during ETL
            "extracted_data_path": twin.extracted_data_path,
            "physics_context": twin.physics_context
        }
        
        success = self.update(twin_id, update_data)
        if success:
            self.logger.info(f"Marked twin {twin_id} as active with health score {health_score}")
        
        return success
    
    # Physics modeling methods
    def update_simulation_status(self, twin_id: str, status: str, results: Dict[str, Any] = None) -> bool:
        """Update twin simulation status and history."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        # Validate simulation status
        valid_statuses = ["pending", "running", "completed", "failed"]
        if status not in valid_statuses:
            self._raise_business_error(f"Invalid simulation status. Must be one of: {', '.join(valid_statuses)}")
        
        update_data = {
            "simulation_status": status,
            "last_simulation_run": self._get_current_timestamp() if status in ["completed", "failed"] else None
        }
        
        # Add to simulation history if completed or failed
        if status in ["completed", "failed"] and results:
            simulation_record = {
                "timestamp": self._get_current_timestamp(),
                "status": status,
                "results": results
            }
            
            # Ensure simulation_history is a list
            if isinstance(twin.simulation_history, list):
                twin.simulation_history.append(simulation_record)
            else:
                # If it's a string (from database), parse it or start fresh
                try:
                    if isinstance(twin.simulation_history, str):
                        history = json.loads(twin.simulation_history) if twin.simulation_history else []
                    else:
                        history = []
                    history.append(simulation_record)
                    twin.simulation_history = history
                except (json.JSONDecodeError, AttributeError):
                    twin.simulation_history = [simulation_record]
            
            update_data["simulation_history"] = twin.simulation_history
        
        success = self.update(twin_id, update_data)
        if success:
            self.logger.info(f"Updated simulation status for twin {twin_id}: {status}")
        
        return success
    
    def get_physics_ready_twins(self, health_threshold: int = 70) -> List[DigitalTwin]:
        """Get twins that are ready for physics modeling based on health threshold."""
        all_twins = self.get_all()
        
        ready_twins = [
            twin for twin in all_twins
            if twin.status == "active" 
            and twin.health_score >= health_threshold
            and twin.extracted_data_path
            and twin.physics_context
        ]
        
        self.logger.info(f"Found {len(ready_twins)} twins ready for physics modeling (threshold: {health_threshold})")
        return ready_twins
    
    # Federated Learning Integration Methods
    
    def perform_federated_health_check(self, twin_id: str) -> Dict[str, Any]:
        """Perform federated-specific health checks."""
        twin = self.get_by_id(twin_id)
        if not twin:
            return {"status": "error", "message": "Twin not found"}
        
        # Perform federated-specific health checks
        federated_checks = {
            "federated_participation": self._check_federated_participation(twin),
            "data_quality_for_federated": self._check_data_quality_for_federated(twin),
            "privacy_compliance": self._check_privacy_compliance(twin),
            "model_synchronization": self._check_model_synchronization(twin)
        }
        
        # Calculate federated health score
        federated_health_score = self._calculate_federated_health_score(federated_checks)
        federated_health_status = self._determine_federated_health_status(federated_health_score)
        
        # Update twin federated health
        update_data = {
            "federated_health_status": federated_health_status,
            "federated_contribution_score": federated_health_score
        }
        self.update(twin_id, update_data)
        
        return {
            "twin_id": twin_id,
            "federated_health_status": federated_health_status,
            "federated_health_score": federated_health_score,
            "checks": federated_checks,
            "timestamp": self._get_current_timestamp()
        }
    
    def get_federated_ready_twins(self, privacy_level: str = "public", health_threshold: int = 70) -> List[DigitalTwin]:
        """Get twins ready for federated learning."""
        all_twins = self.get_all()
        
        ready_twins = [
            twin for twin in all_twins
            if twin.status == "active"
            and twin.federated_participation_status == "active"
            and twin.health_score >= health_threshold
            and twin.data_privacy_level == privacy_level
            and twin.extracted_data_path
            and twin.physics_context
        ]
        
        self.logger.info(f"Found {len(ready_twins)} twins ready for federated learning (privacy: {privacy_level}, health: {health_threshold})")
        return ready_twins
    
    def update_federated_participation(self, twin_id: str, status: str) -> bool:
        """Update federated participation status."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        valid_statuses = ["active", "inactive", "excluded"]
        if status not in valid_statuses:
            self._raise_business_error(f"Invalid federated status. Must be one of: {valid_statuses}")
        
        update_data = {
            "federated_participation_status": status,
            "federated_last_sync": self._get_current_timestamp()
        }
        
        success = self.update(twin_id, update_data)
        if success:
            self.logger.info(f"Updated twin {twin_id} federated participation to {status}")
        
        return success
    
    def calculate_federated_contribution(self, twin_id: str) -> int:
        """Calculate twin's contribution score for federated learning."""
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        contribution_score = 0
        
        # Data quality contribution (0-40 points)
        if twin.extracted_data_path:
            contribution_score += 20
        if twin.physics_context:
            contribution_score += 20
        
        # Health contribution (0-30 points)
        health_contribution = min(twin.health_score // 3, 30)
        contribution_score += health_contribution
        
        # Participation contribution (0-20 points)
        if twin.federated_participation_status == "active":
            contribution_score += 20
        
        # Privacy compliance contribution (0-10 points)
        if twin.secure_aggregation_enabled:
            contribution_score += 10
        
        # Update the contribution score
        update_data = {"federated_contribution_score": contribution_score}
        self.update(twin_id, update_data)
        
        self.logger.info(f"Calculated federated contribution score for twin {twin_id}: {contribution_score}")
        return contribution_score
    
    def delete_twin(self, twin_id: str) -> bool:
        """Delete a digital twin."""
        # Validate twin exists
        twin = self.get_by_id(twin_id)
        if not twin:
            self._raise_business_error(f"Digital twin {twin_id} not found")
        
        # Check if twin is active
        if twin.status == "active":
            self._raise_business_error("Cannot delete an active digital twin")
        
        # Delete the twin
        success = self.delete(twin_id)
        
        if success:
            self.logger.warning(f"Deleted digital twin: {twin.twin_name}")
        
        return success
    
    # Business Logic Validation Methods
    
    def _validate_twin_registration(self, file_id: str, twin_data: Dict[str, Any]) -> None:
        """Validate digital twin registration business rules."""
        # Validate file exists
        file = self.file_repository.get_by_id(file_id)
        if not file:
            self._raise_business_error(f"File {file_id} not found")
        
        # Validate twin name if provided
        twin_name = twin_data.get("twin_name")
        if twin_name:
            self._validate_field_length(twin_data, "twin_name", 200)
        
        # Validate status if provided
        status = twin_data.get("status", "created")
        valid_statuses = ["created", "processing", "active", "failed", "archived"]
        if status not in valid_statuses:
            self._raise_business_error(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    def _validate_status_transition(self, current_status: str, new_status: str) -> None:
        """Validate status transition rules."""
        # Define allowed transitions for twin lifecycle
        allowed_transitions = {
            "created": ["processing", "failed"],
            "processing": ["active", "failed"],
            "active": ["failed", "archived"],
            "failed": ["processing", "archived"],
            "archived": []  # No transitions from archived
        }
        
        if new_status not in allowed_transitions.get(current_status, []):
            self._raise_business_error(f"Invalid status transition from {current_status} to {new_status}")
    
    def _generate_twin_name(self, file_id: str) -> str:
        """Generate twin name based on file information."""
        # Get file information
        file = self.file_repository.get_by_id(file_id)
        if not file:
            return f"Digital Twin - {file_id}"
        
        # Get project information
        project_info = self.project_repository.get_project_hierarchy_info(file.project_id)
        if not project_info or not project_info.get("primary_use_case"):
            return f"Digital Twin - {file.original_filename}"
        
        # Generate name: Use Case - Project Name - Filename
        use_case_name = project_info["primary_use_case"]["name"]
        project_name = project_info["project"].name
        filename = file.original_filename
        
        return f"{use_case_name} - {project_name} - {filename}"
    
    def _update_existing_twin(self, twin_id: str, twin_data: Dict[str, Any]) -> DigitalTwin:
        """Update existing twin instead of creating new one."""
        # Update twin metadata
        update_data = {
            "twin_name": twin_data.get("twin_name"),
            "status": twin_data.get("status", "active"),
            "metadata": twin_data.get("metadata")
        }
        
        twin = self.update(twin_id, update_data)
        
        if twin:
            self.logger.info(f"Updated existing digital twin: {twin.twin_name}")
        
        return twin
    
    # Override base methods for digital twin-specific logic
    
    def _validate_create(self, data: Dict[str, Any]) -> None:
        """Validate digital twin creation."""
        # Note: This is called after _validate_twin_registration, so we don't need to duplicate validation
        pass
    
    def _validate_update(self, entity_id: str, data: Dict[str, Any]) -> None:
        """Validate digital twin update."""
        # Check if twin exists
        twin = self.get_by_id(entity_id)
        if not twin:
            self._raise_business_error(f"Digital twin {entity_id} not found")
        
        # Validate twin name if being updated
        if "twin_name" in data:
            self._validate_field_length(data, "twin_name", 200)
        
        # Validate status transition if being updated
        if "status" in data:
            self._validate_status_transition(twin.status, data["status"])
    
    def _validate_delete(self, entity_id: str) -> None:
        """Validate digital twin deletion."""
        # Check if twin exists
        twin = self.get_by_id(entity_id)
        if not twin:
            self._raise_business_error(f"Digital twin {entity_id} not found")
        
        # Check if twin is active
        if twin.status == "active":
            self._raise_business_error("Cannot delete an active digital twin")
    
    def _post_create(self, entity: DigitalTwin) -> None:
        """Post-creation logic for digital twins."""
        self.logger.info(f"Digital twin '{entity.twin_name}' created for file {entity.file_id}")
    
    def _post_update(self, entity: DigitalTwin) -> None:
        """Post-update logic for digital twins."""
        self.logger.info(f"Digital twin '{entity.twin_name}' updated")
    
    def _post_delete(self, entity_id: str) -> None:
        """Post-deletion logic for digital twins."""
        self.logger.warning(f"Digital twin {entity_id} deleted - audit trail required")
    
    # Health check helper methods
    def _check_etl_status(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check ETL status of a twin."""
        return {
            "status": "pass" if twin.status == "active" else "fail",
            "message": f"ETL status: {twin.status}",
            "score": 100 if twin.status == "active" else 0
        }
    
    def _check_data_integrity(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check data integrity of a twin."""
        import os
        
        if not twin.extracted_data_path:
            return {
                "status": "fail",
                "message": "No extracted data path specified",
                "score": 0
            }
        
        if not os.path.exists(twin.extracted_data_path):
            return {
                "status": "fail",
                "message": f"Extracted data path does not exist: {twin.extracted_data_path}",
                "score": 0
            }
        
        return {
            "status": "pass",
            "message": "Data integrity verified",
            "score": 100
        }
    
    def _check_physics_context(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check physics context of a twin."""
        if not twin.physics_context:
            return {
                "status": "fail",
                "message": "No physics context available",
                "score": 0
            }
        
        # Basic validation of physics context structure
        required_keys = ["type", "parameters"]
        missing_keys = [key for key in required_keys if key not in twin.physics_context]
        
        if missing_keys:
            return {
                "status": "fail",
                "message": f"Missing required physics context keys: {missing_keys}",
                "score": 50
            }
        
        return {
            "status": "pass",
            "message": "Physics context validated",
            "score": 100
        }
    
    def _check_system_integration(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check system integration of a twin."""
        # Check if file still exists
        file = self.file_repository.get_by_id(twin.file_id)
        if not file:
            return {
                "status": "fail",
                "message": "Referenced file not found",
                "score": 0
            }
        
        # Check if project hierarchy is valid
        project_info = self.project_repository.get_project_hierarchy_info(file.project_id)
        if not project_info:
            return {
                "status": "fail",
                "message": "Project hierarchy not found",
                "score": 50
            }
        
        return {
            "status": "pass",
            "message": "System integration verified",
            "score": 100
        }
    
    def _calculate_overall_health_score(self, health_checks: Dict[str, Any]) -> int:
        """Calculate overall health score from individual checks."""
        total_score = 0
        check_count = 0
        
        for check_name, check_result in health_checks.items():
            if isinstance(check_result, dict) and "score" in check_result:
                total_score += check_result["score"]
                check_count += 1
        
        return total_score // check_count if check_count > 0 else 0
    
    def _determine_health_status(self, health_score: int) -> str:
        """Determine health status based on score."""
        if health_score >= 80:
            return "healthy"
        elif health_score >= 50:
            return "warning"
        else:
            return "critical"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # Federated Learning Helper Methods
    
    def _check_federated_participation(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check federated participation status."""
        return {
            "status": "pass" if twin.federated_participation_status == "active" else "fail",
            "message": f"Federated participation: {twin.federated_participation_status}",
            "score": 100 if twin.federated_participation_status == "active" else 0
        }
    
    def _check_data_quality_for_federated(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check data quality for federated learning."""
        score = 0
        message = "Data quality check"
        
        if twin.extracted_data_path:
            score += 50
            message += ": extracted data available"
        
        if twin.physics_context:
            score += 50
            message += ": physics context available"
        
        return {
            "status": "pass" if score >= 80 else "fail",
            "message": message,
            "score": score
        }
    
    def _check_privacy_compliance(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check privacy compliance for federated learning."""
        score = 0
        message = "Privacy compliance check"
        
        if twin.secure_aggregation_enabled:
            score += 50
            message += ": secure aggregation enabled"
        
        if twin.differential_privacy_epsilon > 0:
            score += 50
            message += ": differential privacy configured"
        
        return {
            "status": "pass" if score >= 80 else "fail",
            "message": message,
            "score": score
        }
    
    def _check_model_synchronization(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Check model synchronization status."""
        if not twin.federated_model_version:
            return {
                "status": "fail",
                "message": "No federated model version set",
                "score": 0
            }
        
        return {
            "status": "pass",
            "message": f"Model version: {twin.federated_model_version}",
            "score": 100
        }
    
    def _calculate_federated_health_score(self, federated_checks: Dict[str, Any]) -> int:
        """Calculate federated health score from individual checks."""
        total_score = 0
        check_count = 0
        
        for check_name, check_result in federated_checks.items():
            if isinstance(check_result, dict) and "score" in check_result:
                total_score += check_result["score"]
                check_count += 1
        
        return total_score // check_count if check_count > 0 else 0
    
    def _determine_federated_health_status(self, federated_health_score: int) -> str:
        """Determine federated health status based on score."""
        if federated_health_score >= 80:
            return "healthy"
        elif federated_health_score >= 50:
            return "warning"
        else:
            return "critical" 