"""
Digital Twin Repository
======================

Data access layer for digital twins in the AAS Data Modeling framework.
"""

import json
from typing import List, Optional, Dict, Any
from ..database.base_manager import BaseDatabaseManager
from ..models.digital_twin import DigitalTwin
from .base_repository import BaseRepository

class DigitalTwinRepository(BaseRepository[DigitalTwin]):
    """Repository for digital twin operations."""
    
    def __init__(self, db_manager: BaseDatabaseManager):
        super().__init__(db_manager, DigitalTwin)
    
    def _get_table_name(self) -> str:
        return "digital_twins"
    
    def _get_columns(self) -> List[str]:
        return [
            "twin_id", "twin_name", "file_id", "status", "metadata", 
            "created_at", "updated_at"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name for digital_twins table."""
        return "twin_id"
    
    def get_by_file_id(self, file_id: str) -> Optional[DigitalTwin]:
        """Get digital twin by file ID."""
        query = "SELECT * FROM digital_twins WHERE file_id = ?"
        results = self.db_manager.execute_query(query, (file_id,))
        if results:
            return self.model_class.from_dict(results[0])
        return None
    
    def get_by_status(self, status: str) -> List[DigitalTwin]:
        """Get digital twins by status."""
        query = "SELECT * FROM digital_twins WHERE status = ?"
        results = self.db_manager.execute_query(query, (status,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_active_twins(self) -> List[DigitalTwin]:
        """Get all active digital twins."""
        query = "SELECT * FROM digital_twins WHERE status = 'active'"
        results = self.db_manager.execute_query(query)
        return [self.model_class.from_dict(row) for row in results]
    
    def search_twins(self, search_term: str) -> List[DigitalTwin]:
        """Search digital twins by name."""
        query = "SELECT * FROM digital_twins WHERE twin_name LIKE ?"
        search_pattern = f"%{search_term}%"
        results = self.db_manager.execute_query(query, (search_pattern,))
        return [self.model_class.from_dict(row) for row in results]
    
    def get_twin_with_file_info(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get digital twin with complete file information."""
        query = """
            SELECT 
                dt.*,
                f.filename,
                f.original_filename,
                f.project_id,
                f.status as file_status,
                p.name as project_name,
                uc.name as use_case_name
            FROM digital_twins dt
            JOIN files f ON dt.file_id = f.file_id
            LEFT JOIN projects p ON f.project_id = p.project_id
            LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
            LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
            WHERE dt.twin_id = ?
        """
        results = self.db_manager.execute_query(query, (twin_id,))
        if results:
            return results[0]
        return None
    
    def update_status(self, twin_id: str, status: str) -> bool:
        """Update digital twin status."""
        query = "UPDATE digital_twins SET status = ?, updated_at = datetime('now') WHERE twin_id = ?"
        try:
            affected_rows = self.db_manager.execute_update(query, (status, twin_id))
            return affected_rows > 0
        except Exception:
            return False
    
    def update_federated_participation(self, twin_id: str, participation_status: str) -> bool:
        """Update federated participation status."""
        query = "UPDATE digital_twins SET federated_participation_status = ?, updated_at = datetime('now') WHERE twin_id = ?"
        try:
            affected_rows = self.db_manager.execute_update(query, (participation_status, twin_id))
            return affected_rows > 0
        except Exception:
            return False
    
    def update_federated_metadata(self, twin_id: str, federated_data: Dict[str, Any]) -> bool:
        """Update federated learning metadata for a digital twin."""
        try:
            # Get current twin data
            twin = self.get_by_id(twin_id)
            if not twin:
                return False
            
            # Update federated learning fields
            updates = []
            params = []
            
            if 'federated_participation_status' in federated_data:
                updates.append("federated_participation_status = ?")
                params.append(federated_data['federated_participation_status'])
            
            if 'data_privacy_level' in federated_data:
                updates.append("data_privacy_level = ?")
                params.append(federated_data['data_privacy_level'])
            
            if 'secure_aggregation_enabled' in federated_data:
                updates.append("secure_aggregation_enabled = ?")
                params.append(1 if federated_data['secure_aggregation_enabled'] else 0)
            
            if 'federated_contribution_score' in federated_data:
                updates.append("federated_contribution_score = ?")
                params.append(federated_data['federated_contribution_score'])
            
            if 'data_sharing_permissions' in federated_data:
                updates.append("data_sharing_permissions = ?")
                params.append(json.dumps(federated_data['data_sharing_permissions']))
            
            if updates:
                updates.append("updated_at = datetime('now')")
                params.append(twin_id)
                
                query = f"UPDATE digital_twins SET {', '.join(updates)} WHERE twin_id = ?"
                affected_rows = self.db_manager.execute_update(query, params)
                return affected_rows > 0
            
            return True
            
        except Exception as e:
            print(f"Error updating federated metadata: {e}")
            return False
    
    def update_federated_learning_round(self, twin_id: str, round_number: int, model_version: str = None, 
                                       contribution_score: int = None, sync_timestamp: str = None) -> bool:
        """Update federated learning round information."""
        try:
            updates = []
            params = []
            
            updates.append("federated_round_number = ?")
            params.append(round_number)
            
            if model_version:
                updates.append("federated_model_version = ?")
                params.append(model_version)
            
            if contribution_score is not None:
                updates.append("federated_contribution_score = ?")
                params.append(contribution_score)
            
            if sync_timestamp:
                updates.append("federated_last_sync = ?")
                params.append(sync_timestamp)
            
            updates.append("updated_at = datetime('now')")
            params.append(twin_id)
            
            query = f"UPDATE digital_twins SET {', '.join(updates)} WHERE twin_id = ?"
            affected_rows = self.db_manager.execute_update(query, params)
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error updating federated learning round: {e}")
            return False
    
    def update_physics_modeling(self, twin_id: str, physics_data: Dict[str, Any]) -> bool:
        """Update physics modeling fields for a digital twin."""
        try:
            updates = []
            params = []
            
            if 'extracted_data_path' in physics_data:
                updates.append("extracted_data_path = ?")
                params.append(physics_data['extracted_data_path'])
            
            if 'physics_context' in physics_data:
                updates.append("physics_context = ?")
                params.append(json.dumps(physics_data['physics_context']))
            
            if 'simulation_status' in physics_data:
                updates.append("simulation_status = ?")
                params.append(physics_data['simulation_status'])
            
            if 'model_version' in physics_data:
                updates.append("model_version = ?")
                params.append(physics_data['model_version'])
            
            if updates:
                updates.append("updated_at = datetime('now')")
                params.append(twin_id)
                
                query = f"UPDATE digital_twins SET {', '.join(updates)} WHERE twin_id = ?"
                affected_rows = self.db_manager.execute_update(query, params)
                return affected_rows > 0
            
            return True
            
        except Exception as e:
            print(f"Error updating physics modeling: {e}")
            return False
    
    def update_simulation_run(self, twin_id: str, simulation_results: Dict[str, Any], 
                             run_timestamp: str = None) -> bool:
        """Update simulation run information."""
        try:
            import json
            from datetime import datetime
            
            # Get current simulation history
            current_twin = self.get_by_id(twin_id)
            if not current_twin:
                return False
            
            # Parse existing simulation history
            try:
                simulation_history = json.loads(current_twin.simulation_history) if current_twin.simulation_history else []
            except:
                simulation_history = []
            
            # Add new simulation run
            new_run = {
                'timestamp': run_timestamp or datetime.now().isoformat(),
                'results': simulation_results,
                'status': simulation_results.get('status', 'completed')
            }
            simulation_history.append(new_run)
            
            # Update simulation fields
            updates = [
                "simulation_history = ?",
                "last_simulation_run = ?",
                "simulation_status = ?",
                "updated_at = datetime('now')"
            ]
            
            params = [
                json.dumps(simulation_history),
                new_run['timestamp'],
                simulation_results.get('status', 'completed'),
                twin_id
            ]
            
            query = f"UPDATE digital_twins SET {', '.join(updates)} WHERE twin_id = ?"
            affected_rows = self.db_manager.execute_update(query, params)
            return affected_rows > 0
            
        except Exception as e:
            print(f"Error updating simulation run: {e}")
            return False
    
    def update_health_monitoring(self, twin_id: str, health_data: Dict[str, Any]) -> bool:
        """Update health monitoring fields for a digital twin."""
        try:
            from datetime import datetime
            
            updates = []
            params = []
            
            if 'health_status' in health_data:
                updates.append("health_status = ?")
                params.append(health_data['health_status'])
            
            if 'health_score' in health_data:
                updates.append("health_score = ?")
                params.append(health_data['health_score'])
            
            if 'error_count' in health_data:
                updates.append("error_count = ?")
                params.append(health_data['error_count'])
            
            if 'last_error_message' in health_data:
                updates.append("last_error_message = ?")
                params.append(health_data['last_error_message'])
            
            if 'maintenance_required' in health_data:
                updates.append("maintenance_required = ?")
                params.append(1 if health_data['maintenance_required'] else 0)
            
            if 'next_maintenance_date' in health_data:
                updates.append("next_maintenance_date = ?")
                params.append(health_data['next_maintenance_date'])
            
            # Always update last_health_check
            updates.append("last_health_check = ?")
            params.append(datetime.now().isoformat())
            
            if updates:
                updates.append("updated_at = datetime('now')")
                params.append(twin_id)
                
                query = f"UPDATE digital_twins SET {', '.join(updates)} WHERE twin_id = ?"
                affected_rows = self.db_manager.execute_update(query, params)
                return affected_rows > 0
            
            return True
            
        except Exception as e:
            print(f"Error updating health monitoring: {e}")
            return False
    
    def get_federated_twins(self, participation_status: str = None) -> List[DigitalTwin]:
        """Get digital twins by federated participation status."""
        if participation_status:
            query = "SELECT * FROM digital_twins WHERE federated_participation_status = ?"
            results = self.db_manager.execute_query(query, (participation_status,))
        else:
            query = "SELECT * FROM digital_twins WHERE federated_participation_status IN ('active', 'inactive')"
            results = self.db_manager.execute_query(query)
        
        return [self.model_class.from_dict(row) for row in results]
    
    def get_federated_learning_stats(self) -> Dict[str, Any]:
        """Get federated learning statistics."""
        query = """
            SELECT 
                COUNT(*) as total_twins,
                COUNT(CASE WHEN federated_participation_status = 'active' THEN 1 END) as active_participants,
                COUNT(CASE WHEN federated_participation_status = 'inactive' THEN 1 END) as inactive_participants,
                COUNT(CASE WHEN federated_participation_status = 'excluded' THEN 1 END) as excluded_participants,
                AVG(federated_contribution_score) as avg_contribution_score,
                COUNT(CASE WHEN secure_aggregation_enabled = 1 THEN 1 END) as secure_aggregation_enabled_count
            FROM digital_twins
        """
        results = self.db_manager.execute_query(query)
        
        if results:
            result = results[0]
            return {
                "total_twins": result["total_twins"] or 0,
                "active_participants": result["active_participants"] or 0,
                "inactive_participants": result["inactive_participants"] or 0,
                "excluded_participants": result["excluded_participants"] or 0,
                "avg_contribution_score": round(result["avg_contribution_score"] or 0, 2),
                "secure_aggregation_enabled_count": result["secure_aggregation_enabled_count"] or 0,
                "participation_rate": round(((result["active_participants"] or 0) / (result["total_twins"] or 1)) * 100, 2)
            }
        
        return {
            "total_twins": 0,
            "active_participants": 0,
            "inactive_participants": 0,
            "excluded_participants": 0,
            "avg_contribution_score": 0.0,
            "secure_aggregation_enabled_count": 0,
            "participation_rate": 0.0
        }
    
    def get_twin_statistics(self) -> Dict[str, Any]:
        """Get digital twin statistics."""
        query = """
            SELECT 
                COUNT(*) as total_twins,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_twins,
                COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive_twins,
                COUNT(CASE WHEN status = 'orphaned' THEN 1 END) as orphaned_twins
            FROM digital_twins
        """
        results = self.db_manager.execute_query(query)
        
        if results:
            return {
                "total_twins": results[0]["total_twins"] or 0,
                "active_twins": results[0]["active_twins"] or 0,
                "inactive_twins": results[0]["inactive_twins"] or 0,
                "orphaned_twins": results[0]["orphaned_twins"] or 0
            }
        return {
            "total_twins": 0,
            "active_twins": 0,
            "inactive_twins": 0,
            "orphaned_twins": 0
        }
    
    def check_twin_exists(self, file_id: str) -> bool:
        """Check if a digital twin exists for a file."""
        query = "SELECT COUNT(*) as count FROM digital_twins WHERE file_id = ?"
        results = self.db_manager.execute_query(query, (file_id,))
        return results[0]["count"] > 0 if results else False
    
    def create(self, project_id: str, file_id: str, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new digital twin for a file with all columns populated."""
        import json
        import os
        from datetime import datetime
        
        # twin_id should be the same as file_id for 1:1 relationship
        twin_id = file_id
        
        # Get file info to build proper twin name: "DT - Use Case - Project Name - Filename"
        file_info = self._get_file_info(file_id)
        if file_info:
            use_case_name = file_info.get('use_case_name', 'Unknown Use Case')
            project_name = file_info.get('project_name', 'Unknown Project')
            filename = file_info.get('filename', 'Unknown File')
            # Remove file extension from filename
            filename_without_ext = os.path.splitext(filename)[0]
            twin_name = f"DT - {use_case_name} - {project_name} - {filename_without_ext}"
        else:
            # Fallback if file info not available
            twin_name = twin_data.get('twin_name', 'DT - Unknown Use Case - Unknown Project - Unknown File')
        
        # Extract ETL results and user preferences
        etl_results = twin_data.get('metadata', {})
        user_consent = twin_data.get('user_consent', False)
        federated_setting = twin_data.get('federated_learning', 'not_allowed')
        privacy_level = twin_data.get('data_privacy_level', 'private')
        output_dir = twin_data.get('output_directory', '')
        
        # Prepare all column values
        current_time = datetime.now().isoformat()
        
        # Health monitoring fields - will be calculated by service layer
        health_status = "unknown"  # Will be updated by service layer health check
        last_health_check = None
        error_count = 0
        last_error_message = None
        maintenance_required = False
        next_maintenance_date = None
        
        # Physics modeling fields
        extracted_data_path = output_dir
        physics_context = json.dumps(etl_results.get('etl_results', {}))
        simulation_history = json.dumps([])
        last_simulation_run = None
        simulation_status = "pending"
        model_version = f"ETL-{current_time}"
        
        # Federated Learning fields
        federated_node_id = None
        federated_participation_status = "active" if user_consent and federated_setting in ['allowed', 'conditional'] else "inactive"
        federated_model_version = None
        federated_last_sync = None
        federated_contribution_score = 0
        federated_round_number = 0  # Add missing federated_round_number
        federated_health_status = "unknown"
        
        # Privacy & Security fields
        data_privacy_level = privacy_level
        data_sharing_permissions = json.dumps({})
        differential_privacy_epsilon = 1.0
        secure_aggregation_enabled = True if user_consent else False
        
        # Core fields
        status = "active"
        metadata = json.dumps(twin_data.get('metadata', {}))
        
        # Complete INSERT query with all columns
        query = """
            INSERT INTO digital_twins (
                twin_id, twin_name, file_id, status, metadata,
                health_status, last_health_check, health_score, error_count, last_error_message, 
                maintenance_required, next_maintenance_date,
                extracted_data_path, physics_context, simulation_history, last_simulation_run, 
                simulation_status, model_version,
                federated_node_id, federated_participation_status, federated_model_version, 
                federated_last_sync, federated_contribution_score, federated_round_number, federated_health_status,
                data_privacy_level, data_sharing_permissions, differential_privacy_epsilon, 
                secure_aggregation_enabled,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            params = (
                twin_id, twin_name, file_id, status, metadata,
                health_status, last_health_check, 0, error_count, last_error_message,  # health_score will be calculated by service
                maintenance_required, next_maintenance_date,
                extracted_data_path, physics_context, simulation_history, last_simulation_run,
                simulation_status, model_version,
                federated_node_id, federated_participation_status, federated_model_version,
                federated_last_sync, federated_contribution_score, federated_round_number, federated_health_status,
                data_privacy_level, data_sharing_permissions, differential_privacy_epsilon,
                secure_aggregation_enabled,
                current_time, current_time
            )
            
            self.db_manager.execute_insert(query, params)
            
            # Note: Health score calculation should be done by DigitalTwinService after creation
            # The service layer will call perform_health_check() to calculate proper health score
            
            return {
                'twin_id': twin_id,
                'twin_name': twin_name,
                'file_id': file_id,
                'status': status,
                'health_score': 0,  # Will be calculated by service layer
                'federated_participation_status': federated_participation_status,
                'data_privacy_level': data_privacy_level,
                'metadata': twin_data.get('metadata', {})
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information with use case and project details for twin naming."""
        query = """
            SELECT 
                f.filename,
                p.name as project_name,
                uc.name as use_case_name
            FROM files f
            LEFT JOIN projects p ON f.project_id = p.project_id
            LEFT JOIN project_use_case_links puc ON p.project_id = puc.project_id
            LEFT JOIN use_cases uc ON puc.use_case_id = uc.use_case_id
            WHERE f.file_id = ?
        """
        results = self.db_manager.execute_query(query, (file_id,))
        if results:
            return results[0]
        return None 