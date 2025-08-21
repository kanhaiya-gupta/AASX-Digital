"""
Certificate Manager Core

Main certificate management system for creating, updating, and managing
digital certificates for AASX Digital Twin Analytics.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging

# Add the src directory to the Python path
src_root = Path(__file__).parent.parent.parent
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

from src.shared.database.connection_manager import DatabaseConnectionManager
from src.shared.repositories.base_repository import BaseRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.use_case_repository import UseCaseRepository
from src.shared.repositories.project_repository import ProjectRepository

from ..models.certificate import Certificate, CertificateStatus, CertificateVisibility, RetentionPolicy
from ..models.certificate_version import CertificateVersion
from ..models.certificate_event import CertificateEvent, EventType, EventStatus
from ..models.certificate_export import CertificateExport, ExportFormat, ExportStatus

# Set up logging
logger = logging.getLogger(__name__)


class CertificateManager:
    """Main certificate management system."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the Certificate Manager."""
        self.db_path = db_path or "certificates.db"
        self.db_manager = DatabaseConnectionManager(Path(self.db_path))
        
        # Initialize repositories
        self.certificate_repo = CertificateRepository(self.db_manager)
        self.version_repo = CertificateVersionRepository(self.db_manager)
        self.event_repo = CertificateEventRepository(self.db_manager)
        self.export_repo = CertificateExportRepository(self.db_manager)
        
        # External repositories for data integration
        self.file_repo = FileRepository(self.db_manager)
        self.use_case_repo = UseCaseRepository(self.db_manager)
        self.project_repo = ProjectRepository(self.db_manager)
        
        # Initialize database tables
        self._initialize_database()
        
        logger.info("Certificate Manager initialized successfully")
    
    def _initialize_database(self) -> None:
        """Initialize database tables."""
        try:
            # Create tables if they don't exist
            self.certificate_repo.create_table()
            self.version_repo.create_table()
            self.event_repo.create_table()
            self.export_repo.create_table()
            
            logger.info("Certificate Manager database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_certificate(self, twin_id: str, **kwargs) -> Certificate:
        """Create a new certificate for a digital twin."""
        try:
            # Get twin information from existing repositories
            twin_info = self._get_twin_info(twin_id)
            
            # Convert string enum values to proper enum objects
            processed_kwargs = {}
            for key, value in kwargs.items():
                if key == 'status' and isinstance(value, str):
                    processed_kwargs[key] = CertificateStatus(value)
                elif key == 'visibility' and isinstance(value, str):
                    processed_kwargs[key] = CertificateVisibility(value)
                elif key == 'retention_policy' and isinstance(value, str):
                    processed_kwargs[key] = RetentionPolicy(value)
                else:
                    processed_kwargs[key] = value
            
            # Create certificate with twin information
            certificate_data = {
                'twin_id': twin_id,
                'twin_name': twin_info.get('twin_name', 'Unknown Twin'),
                'project_name': twin_info.get('project_name', 'Unknown Project'),
                'use_case_name': twin_info.get('use_case_name', 'Unknown Use Case'),
                'file_name': twin_info.get('file_name', 'Unknown File'),
                'uploaded_at': twin_info.get('uploaded_at', datetime.now()),
                **processed_kwargs
            }
            
            certificate = Certificate(**certificate_data)
            
            # Save to database
            self.certificate_repo.create(certificate)
            
            # Create initial version
            initial_version = CertificateVersion(
                certificate_id=certificate.certificate_id,
                version="1.0.0"
            )
            self.version_repo.create(initial_version)
            
            # Create certificate creation event
            creation_event = CertificateEvent(
                certificate_id=certificate.certificate_id,
                event_type=EventType.CERTIFICATE_CREATED,
                module_name="certificate_manager",
                data_snapshot={
                    'twin_id': twin_id,
                    'twin_info': {
                        'twin_name': twin_info.get('twin_name'),
                        'project_name': twin_info.get('project_name'),
                        'use_case_name': twin_info.get('use_case_name'),
                        'file_name': twin_info.get('file_name'),
                        'uploaded_at': twin_info.get('uploaded_at').isoformat() if isinstance(twin_info.get('uploaded_at'), datetime) else str(twin_info.get('uploaded_at'))
                    },
                    'certificate_data': {
                        'twin_id': twin_id,
                        'twin_name': certificate_data.get('twin_name'),
                        'project_name': certificate_data.get('project_name'),
                        'use_case_name': certificate_data.get('use_case_name'),
                        'file_name': certificate_data.get('file_name'),
                        'uploaded_at': certificate_data.get('uploaded_at').isoformat() if isinstance(certificate_data.get('uploaded_at'), datetime) else str(certificate_data.get('uploaded_at'))
                    }
                }
            )
            self.event_repo.create(creation_event)
            
            logger.info(f"Created certificate {certificate.certificate_id} for twin {twin_id}")
            return certificate
            
        except Exception as e:
            logger.error(f"Failed to create certificate for twin {twin_id}: {e}")
            raise
    
    def get_certificate(self, certificate_id: str) -> Optional[Certificate]:
        """Get a certificate by ID."""
        try:
            return self.certificate_repo.get_by_id(certificate_id)
        except Exception as e:
            logger.error(f"Failed to get certificate {certificate_id}: {e}")
            return None
    
    def update_certificate(self, certificate_id: str, **kwargs) -> Optional[Certificate]:
        """Update a certificate."""
        try:
            certificate = self.get_certificate(certificate_id)
            if not certificate:
                return None
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(certificate, key):
                    setattr(certificate, key, value)
            
            # Update timestamp
            certificate.updated_at = datetime.now()
            
            # Save to database
            self.certificate_repo.update(certificate)
            
            # Create update event
            update_event = CertificateEvent(
                certificate_id=certificate_id,
                event_type=EventType.CERTIFICATE_UPDATED,
                module_name="certificate_manager",
                data_snapshot={'updates': kwargs}
            )
            self.event_repo.create(update_event)
            
            logger.info(f"Updated certificate {certificate_id}")
            return certificate
            
        except Exception as e:
            logger.error(f"Failed to update certificate {certificate_id}: {e}")
            return None
    
    def delete_certificate(self, certificate_id: str) -> bool:
        """Delete a certificate and all associated data."""
        try:
            # Delete associated data first
            self.version_repo.delete_by_certificate_id(certificate_id)
            self.event_repo.delete_by_certificate_id(certificate_id)
            self.export_repo.delete_by_certificate_id(certificate_id)
            
            # Delete certificate
            success = self.certificate_repo.delete(certificate_id)
            
            if success:
                logger.info(f"Deleted certificate {certificate_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete certificate {certificate_id}: {e}")
            return False
    
    def list_certificates(self, **filters) -> List[Certificate]:
        """List certificates with optional filters."""
        try:
            return self.certificate_repo.list_all(**filters)
        except Exception as e:
            logger.error(f"Failed to list certificates: {e}")
            return []
    
    def get_certificate_version(self, certificate_id: str, version: str = "latest") -> Optional[CertificateVersion]:
        """Get a specific version of a certificate."""
        try:
            if version == "latest":
                return self.version_repo.get_latest_version(certificate_id)
            else:
                return self.version_repo.get_by_version(certificate_id, version)
        except Exception as e:
            logger.error(f"Failed to get certificate version {certificate_id}:{version}: {e}")
            return None
    
    def create_new_version(self, certificate_id: str, increment_type: str = "patch") -> Optional[CertificateVersion]:
        """Create a new version of a certificate."""
        try:
            current_version = self.get_certificate_version(certificate_id)
            if not current_version:
                return None
            
            new_version_number = current_version.increment_version(increment_type)
            
            new_version = CertificateVersion(
                certificate_id=certificate_id,
                version=new_version_number,
                sections=current_version.sections.copy()  # Copy current sections
            )
            
            self.version_repo.create(new_version)
            
            # Update certificate current version
            self.update_certificate(certificate_id, current_version=new_version_number)
            
            # Create version event
            version_event = CertificateEvent(
                certificate_id=certificate_id,
                event_type=EventType.VERSION_CREATED,
                module_name="certificate_manager",
                data_snapshot={
                    'old_version': current_version.version,
                    'new_version': new_version_number,
                    'increment_type': increment_type
                }
            )
            self.event_repo.create(version_event)
            
            logger.info(f"Created new version {new_version_number} for certificate {certificate_id}")
            return new_version
            
        except Exception as e:
            logger.error(f"Failed to create new version for certificate {certificate_id}: {e}")
            return None
    
    def add_section_data(self, certificate_id: str, section_name: str, section_data: Dict[str, Any], version: str = "latest") -> bool:
        """Add or update section data in a certificate version."""
        try:
            cert_version = self.get_certificate_version(certificate_id, version)
            if not cert_version:
                return False
            
            cert_version.add_section(section_name, section_data)
            self.version_repo.update(cert_version)
            
            # Create module event
            module_event = CertificateEvent(
                certificate_id=certificate_id,
                event_type=self._get_module_event_type(section_name),
                module_name=section_name,
                data_snapshot={'section_data': section_data}
            )
            self.event_repo.create(module_event)
            
            logger.info(f"Added section {section_name} to certificate {certificate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add section {section_name} to certificate {certificate_id}: {e}")
            return False
    
    def get_certificate_events(self, certificate_id: str, event_type: Optional[EventType] = None) -> List[CertificateEvent]:
        """Get events for a certificate."""
        try:
            return self.event_repo.get_by_certificate_id(certificate_id, event_type)
        except Exception as e:
            logger.error(f"Failed to get events for certificate {certificate_id}: {e}")
            return []
    
    def create_export(self, certificate_id: str, format: ExportFormat, version: str = "latest") -> Optional[CertificateExport]:
        """Create an export for a certificate."""
        try:
            # Check if certificate exists and can be exported
            certificate = self.get_certificate(certificate_id)
            if not certificate or not certificate.can_be_exported():
                return None
            
            # Create export record
            export = CertificateExport(
                certificate_id=certificate_id,
                version=version,
                format=format
            )
            
            self.export_repo.create(export)
            
            logger.info(f"Created export {format.value} for certificate {certificate_id}")
            return export
            
        except Exception as e:
            logger.error(f"Failed to create export for certificate {certificate_id}: {e}")
            return None
    
    def get_certificate_stats(self, certificate_id: str) -> Dict[str, Any]:
        """Get statistics for a certificate."""
        try:
            certificate = self.get_certificate(certificate_id)
            if not certificate:
                return {}
            
            events = self.get_certificate_events(certificate_id)
            versions = self.version_repo.get_all_versions(certificate_id)
            exports = self.export_repo.get_by_certificate_id(certificate_id)
            
            return {
                'certificate': certificate.to_dict(),
                'events_count': len(events),
                'versions_count': len(versions),
                'exports_count': len(exports),
                'health_score': certificate.calculate_health_score(),
                'last_updated': certificate.updated_at.isoformat(),
                'is_public': certificate.is_publicly_accessible(),
                'can_export': certificate.can_be_exported()
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for certificate {certificate_id}: {e}")
            return {}
    
    def _get_twin_info(self, twin_id: str) -> Dict[str, Any]:
        """Get twin information from existing repositories."""
        try:
            # Try to get file information first (Phase 2 will have this)
            try:
                file_info = self.file_repo.get_file_trace_info(twin_id)
                
                if file_info:
                    return {
                        'twin_name': f"DT - {file_info.get('use_case_name', 'Unknown')} - {file_info.get('project_name', 'Unknown')} - {file_info.get('file_name', 'Unknown')}",
                        'project_name': file_info.get('project_name', 'Unknown Project'),
                        'use_case_name': file_info.get('use_case_name', 'Unknown Use Case'),
                        'file_name': file_info.get('file_name', 'Unknown File'),
                        'uploaded_at': datetime.now()  # We'll get this from file info in Phase 2
                    }
            except Exception as file_error:
                # In Phase 1, the files table might not exist yet
                logger.debug(f"File repository not available for {twin_id}: {file_error}")
            
            # Fallback to basic info for Phase 1
            return {
                'twin_name': f"DT - Phase1 - Test - {twin_id}",
                'project_name': 'Phase 1 Test Project',
                'use_case_name': 'Phase 1 Test Use Case',
                'file_name': twin_id,
                'uploaded_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Failed to get twin info for {twin_id}: {e}")
            return {
                'twin_name': f"DT - Phase1 - Test - {twin_id}",
                'project_name': 'Phase 1 Test Project',
                'use_case_name': 'Phase 1 Test Use Case',
                'file_name': twin_id,
                'uploaded_at': datetime.now()
            }
    
    def _get_module_event_type(self, section_name: str) -> EventType:
        """Get the appropriate event type for a module section."""
        event_type_map = {
            'etl': EventType.ETL_COMPLETED,
            'ai_rag': EventType.AI_RAG_COMPLETED,
            'knowledge_graph': EventType.KNOWLEDGE_GRAPH_UPDATED,
            'federated_learning': EventType.FEDERATED_LEARNING_UPDATED,
            'physics_modeling': EventType.PHYSICS_MODELING_COMPLETED
        }
        
        return event_type_map.get(section_name, EventType.CERTIFICATE_UPDATED)
    
    def __str__(self) -> str:
        """String representation."""
        return f"CertificateManager(db_path='{self.db_path}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"CertificateManager(db_path='{self.db_path}')"


# Repository classes for database operations
class CertificateRepository(BaseRepository[Certificate]):
    """Repository for certificate operations."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        super().__init__(db_manager, Certificate)
    
    def _get_table_name(self) -> str:
        """Get the table name for certificates."""
        return "certificates"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for certificates table."""
        return [
            "certificate_id", "twin_id", "twin_name", "project_name", "use_case_name",
            "file_name", "uploaded_at", "created_at", "updated_at", "status",
            "current_version", "visibility", "access_level", "template_id",
            "retention_policy", "signature", "signature_timestamp", "metadata"
        ]
    
    def _get_primary_key_column(self) -> str:
        """Get the primary key column name."""
        return "certificate_id"
    
    def create(self, model: Certificate) -> Certificate:
        """Create a new certificate record with JSON serialization."""
        try:
            model.validate()
            data = model.to_dict()
            
            # Convert datetime to string for database storage
            for field in ['created_at', 'updated_at', 'uploaded_at', 'signature_timestamp']:
                if field in data and isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
            
            # Serialize dictionary fields to JSON strings
            if 'metadata' in data and isinstance(data['metadata'], dict):
                import json
                data['metadata'] = json.dumps(data['metadata'])
            
            columns = self._get_columns()
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            
            query = f"""
                INSERT INTO {self.table_name} ({column_names})
                VALUES ({placeholders})
            """
            
            values = tuple(data[col] for col in columns)
            self.db_manager.execute_update(query, values)
            
            logger.info(f"Created {self.table_name} record: {model.certificate_id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create {self.table_name} record: {e}")
            raise
    
    def create_table(self) -> None:
        """Create the certificates table."""
        query = """
        CREATE TABLE IF NOT EXISTS certificates (
            certificate_id TEXT PRIMARY KEY,
            twin_id TEXT NOT NULL,
            twin_name TEXT NOT NULL,
            project_name TEXT NOT NULL,
            use_case_name TEXT NOT NULL,
            file_name TEXT NOT NULL,
            uploaded_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'pending',
            current_version TEXT NOT NULL DEFAULT '1.0.0',
            visibility TEXT NOT NULL DEFAULT 'private',
            access_level TEXT DEFAULT 'project_members',
            template_id TEXT DEFAULT 'default',
            retention_policy TEXT DEFAULT 'keep_all',
            signature TEXT,
            signature_timestamp TIMESTAMP,
            metadata TEXT
        )
        """
        self.db_manager.execute_query(query)
    
    def list_all(self, **filters) -> List[Certificate]:
        """List all certificates with optional filters."""
        query = "SELECT * FROM certificates WHERE 1=1"
        params = []
        
        for key, value in filters.items():
            if hasattr(Certificate, key):
                query += f" AND {key} = ?"
                params.append(value)
        
        query += " ORDER BY created_at DESC"
        
        results = self.db_manager.execute_query(query, params)
        return [Certificate.from_dict(dict(row)) for row in results]
    
    def update(self, model: Certificate) -> Certificate:
        """Update a certificate record."""
        try:
            model.validate()
            data = model.to_dict()
            
            # Convert datetime to string for database storage
            for field in ['created_at', 'updated_at', 'uploaded_at', 'signature_timestamp']:
                if field in data and isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
            
            # Serialize dictionary fields to JSON strings
            if 'metadata' in data and isinstance(data['metadata'], dict):
                import json
                data['metadata'] = json.dumps(data['metadata'])
            
            # Remove id field as it's the primary key
            data.pop('id', None)
            
            columns = self._get_columns()
            set_clause = ', '.join([f"{col} = ?" for col in columns if col != 'certificate_id'])
            
            query = f"""
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE certificate_id = ?
            """
            
            values = tuple(data[col] for col in columns if col != 'certificate_id') + (model.certificate_id,)
            self.db_manager.execute_update(query, values)
            
            logger.info(f"Updated {self.table_name} record: {model.certificate_id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to update {self.table_name} record: {e}")
            raise
    
    def delete(self, certificate_id: str) -> bool:
        """Delete a certificate record."""
        query = "DELETE FROM certificates WHERE certificate_id = ?"
        return self.db_manager.execute_update(query, (certificate_id,)) > 0


class CertificateVersionRepository(BaseRepository[CertificateVersion]):
    """Repository for certificate version operations."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        super().__init__(db_manager, CertificateVersion)
    
    def _get_table_name(self) -> str:
        """Get the table name for certificate versions."""
        return "certificate_versions"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for certificate_versions table."""
        return [
            "certificate_id", "version", "content_hash", "sections",
            "summary_data", "reference_links", "export_cache", "signature_metadata",
            "created_at", "created_by"
        ]
    
    def create(self, model: CertificateVersion) -> CertificateVersion:
        """Create a new certificate version record with JSON serialization."""
        try:
            model.validate()
            data = model.to_dict()
            
            # Remove fields that don't exist in the database
            data.pop('id', None)  # Remove id field as it's auto-increment
            data.pop('sections_count', None)  # Remove computed fields
            data.pop('content_size', None)
            data.pop('is_empty', None)
            
            # Convert datetime to string for database storage
            if 'created_at' in data and isinstance(data['created_at'], datetime):
                data['created_at'] = data['created_at'].isoformat()
            
            # Serialize dictionary fields to JSON strings
            import json
            for field in ['sections', 'summary_data', 'reference_links', 'export_cache', 'signature_metadata']:
                if field in data:
                    if isinstance(data[field], dict):
                        data[field] = json.dumps(data[field])
                    elif data[field] is None:
                        data[field] = None
                    else:
                        # Keep the value as is if it's already a string or other type
                        pass
            
            columns = self._get_columns()
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            
            query = f"""
                INSERT INTO {self.table_name} ({column_names})
                VALUES ({placeholders})
            """
            
            values = tuple(data[col] for col in columns)
            self.db_manager.execute_update(query, values)
            
            logger.info(f"Created {self.table_name} record: {model.certificate_id} v{model.version}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create {self.table_name} record: {e}")
            raise
    
    def create_table(self) -> None:
        """Create the certificate_versions table."""
        query = """
        CREATE TABLE IF NOT EXISTS certificate_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT NOT NULL,
            version TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            sections TEXT,
            summary_data TEXT,
            reference_links TEXT,
            export_cache TEXT,
            signature_metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT DEFAULT 'system',
            FOREIGN KEY (certificate_id) REFERENCES certificates(certificate_id),
            UNIQUE(certificate_id, version)
        )
        """
        self.db_manager.execute_query(query)
    
    def get_latest_version(self, certificate_id: str) -> Optional[CertificateVersion]:
        """Get the latest version of a certificate."""
        query = """
        SELECT * FROM certificate_versions 
        WHERE certificate_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
        """
        result = self.db_manager.execute_query(query, [certificate_id])
        if result:
            return CertificateVersion.from_dict(dict(result[0]))
        return None
    
    def get_by_version(self, certificate_id: str, version: str) -> Optional[CertificateVersion]:
        """Get a specific version of a certificate."""
        query = "SELECT * FROM certificate_versions WHERE certificate_id = ? AND version = ?"
        result = self.db_manager.execute_query(query, [certificate_id, version])
        if result:
            return CertificateVersion.from_dict(dict(result[0]))
        return None
    
    def get_all_versions(self, certificate_id: str) -> List[CertificateVersion]:
        """Get all versions of a certificate."""
        query = "SELECT * FROM certificate_versions WHERE certificate_id = ? ORDER BY created_at DESC"
        results = self.db_manager.execute_query(query, [certificate_id])
        return [CertificateVersion.from_dict(dict(row)) for row in results]
    
    def delete_by_certificate_id(self, certificate_id: str) -> bool:
        """Delete all versions of a certificate."""
        query = "DELETE FROM certificate_versions WHERE certificate_id = ?"
        return self.db_manager.execute_update(query, (certificate_id,)) > 0

    def update(self, model: CertificateVersion) -> CertificateVersion:
        """Update a certificate version record."""
        try:
            model.validate()
            data = model.to_dict()
            
            # Remove fields that don't exist in the database
            data.pop('id', None)  # Remove id field as it's auto-increment
            data.pop('sections_count', None)  # Remove computed fields
            data.pop('content_size', None)
            data.pop('is_empty', None)
            
            # Convert datetime to string for database storage
            if 'created_at' in data and isinstance(data['created_at'], datetime):
                data['created_at'] = data['created_at'].isoformat()
            
            # Serialize dictionary fields to JSON strings
            import json
            for field in ['sections', 'summary_data', 'reference_links', 'export_cache', 'signature_metadata']:
                if field in data:
                    if isinstance(data[field], dict):
                        data[field] = json.dumps(data[field])
                    elif data[field] is None:
                        data[field] = None
                    else:
                        # Keep the value as is if it's already a string or other type
                        pass
            
            columns = self._get_columns()
            set_clause = ', '.join([f"{col} = ?" for col in columns if col not in ['certificate_id', 'version']])
            
            query = f"""
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE certificate_id = ? AND version = ?
            """
            
            values = tuple(data[col] for col in columns if col not in ['certificate_id', 'version']) + (model.certificate_id, model.version)
            self.db_manager.execute_update(query, values)
            
            logger.info(f"Updated {self.table_name} record: {model.certificate_id} v{model.version}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to update {self.table_name} record: {e}")
            raise


class CertificateEventRepository(BaseRepository[CertificateEvent]):
    """Repository for certificate event operations."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        super().__init__(db_manager, CertificateEvent)
    
    def _get_table_name(self) -> str:
        """Get the table name for certificate events."""
        return "certificate_events"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for certificate_events table."""
        return [
            "certificate_id", "event_id", "event_type", "module_name",
            "event_hash", "data_snapshot", "status", "processed_at", "created_at"
        ]
    
    def create(self, model: CertificateEvent) -> CertificateEvent:
        """Create a new certificate event record with JSON serialization."""
        try:
            model.validate()
            data = model.to_dict()
            
            # Remove fields that don't exist in the database
            data.pop('id', None)  # Remove id field as it's auto-increment
            
            # Convert datetime to string for database storage
            if 'created_at' in data and isinstance(data['created_at'], datetime):
                data['created_at'] = data['created_at'].isoformat()
            if 'processed_at' in data and isinstance(data['processed_at'], datetime):
                data['processed_at'] = data['processed_at'].isoformat()
            
            # Serialize dictionary fields to JSON strings
            import json
            if 'data_snapshot' in data and isinstance(data['data_snapshot'], dict):
                data['data_snapshot'] = json.dumps(data['data_snapshot'])
            elif 'data_snapshot' in data and data['data_snapshot'] is None:
                data['data_snapshot'] = None
            
            columns = self._get_columns()
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            
            query = f"""
                INSERT INTO {self.table_name} ({column_names})
                VALUES ({placeholders})
            """
            
            values = tuple(data[col] for col in columns)
            self.db_manager.execute_update(query, values)
            
            logger.info(f"Created {self.table_name} record: {model.event_id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create {self.table_name} record: {e}")
            raise
    
    def create_table(self) -> None:
        """Create the certificate_events table."""
        query = """
        CREATE TABLE IF NOT EXISTS certificate_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            module_name TEXT NOT NULL,
            event_hash TEXT NOT NULL,
            data_snapshot TEXT,
            status TEXT DEFAULT 'pending',
            processed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (certificate_id) REFERENCES certificates(certificate_id)
        )
        """
        self.db_manager.execute_query(query)
    
    def get_by_certificate_id(self, certificate_id: str, event_type: Optional[EventType] = None) -> List[CertificateEvent]:
        """Get all events for a certificate."""
        query = "SELECT * FROM certificate_events WHERE certificate_id = ?"
        params = [certificate_id]
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)
        
        query += " ORDER BY created_at DESC"
        
        results = self.db_manager.execute_query(query, params)
        return [CertificateEvent.from_dict(dict(row)) for row in results]
    
    def delete_by_certificate_id(self, certificate_id: str) -> bool:
        """Delete all events for a certificate."""
        query = "DELETE FROM certificate_events WHERE certificate_id = ?"
        return self.db_manager.execute_update(query, (certificate_id,)) > 0


class CertificateExportRepository(BaseRepository[CertificateExport]):
    """Repository for certificate export operations."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        super().__init__(db_manager, CertificateExport)
    
    def _get_table_name(self) -> str:
        """Get the table name for certificate exports."""
        return "certificate_exports"
    
    def _get_columns(self) -> List[str]:
        """Get the list of column names for certificate_exports table."""
        return [
            "certificate_id", "version", "format", "file_path", "file_hash",
            "file_size", "generated_at", "expires_at", "status", "metadata"
        ]
    
    def create_table(self) -> None:
        """Create the certificate_exports table."""
        query = """
        CREATE TABLE IF NOT EXISTS certificate_exports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT NOT NULL,
            version TEXT NOT NULL,
            format TEXT NOT NULL,
            file_path TEXT,
            file_hash TEXT,
            file_size INTEGER,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            status TEXT DEFAULT 'pending',
            metadata TEXT,
            FOREIGN KEY (certificate_id) REFERENCES certificates(certificate_id),
            UNIQUE(certificate_id, version, format)
        )
        """
        self.db_manager.execute_query(query)
    
    def get_by_certificate_id(self, certificate_id: str) -> List[CertificateExport]:
        """Get all exports for a certificate."""
        query = "SELECT * FROM certificate_exports WHERE certificate_id = ? ORDER BY generated_at DESC"
        results = self.db_manager.execute_query(query, [certificate_id])
        return [CertificateExport.from_dict(dict(row)) for row in results]
    
    def delete_by_certificate_id(self, certificate_id: str) -> bool:
        """Delete all exports for a certificate."""
        query = "DELETE FROM certificate_exports WHERE certificate_id = ?"
        return self.db_manager.execute_update(query, (certificate_id,)) > 0 