"""
Twin Integration Service
=======================

Service for AASX and external integrations.
Handles integration with AASX files, external systems, and APIs.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import asyncio

# Import shared services
from src.shared.services.digital_twin_service import DigitalTwinService
from src.shared.repositories.digital_twin_repository import DigitalTwinRepository
from src.shared.repositories.file_repository import FileRepository
from src.shared.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)

class TwinIntegrationService:
    """
    Service for AASX and external integrations.
    Handles integration with AASX files, external systems, and APIs.
    """
    
    def __init__(self, twin_service: DigitalTwinService):
        """Initialize the twin integration service."""
        self.twin_service = twin_service
        self.twin_repo = twin_service.get_repository()
        
        # Get additional repositories from twin service
        self.file_repo = getattr(twin_service, 'file_repo', None)
        self.project_repo = getattr(twin_service, 'project_repo', None)
        
        logger.info("Twin Integration Service initialized")
    
    async def integrate_with_aasx_file(self, file_id: str, twin_id: str = None) -> Dict[str, Any]:
        """
        Integrate a twin with an AASX file.
        
        Args:
            file_id: The AASX file ID to integrate with
            twin_id: Optional twin ID (if None, will create new twin)
            
        Returns:
            Integration result
        """
        try:
            logger.info(f"Integrating with AASX file: {file_id}")
            
            # Get file information
            file_info = self.file_repo.get_by_id(file_id) if self.file_repo else None
            if not file_info:
                raise Exception(f"AASX file not found: {file_id}")
            
            # If no twin_id provided, create new twin
            if not twin_id:
                twin_data = {
                    'file_id': file_id,
                    'twin_name': f"Twin for {getattr(file_info, 'filename', 'Unknown File')}",
                    'status': 'active',
                    'health_status': 'healthy',
                    'health_score': 100,
                    'metadata': {
                        'aasx_file_id': file_id,
                        'integration_type': 'aasx_file',
                        'integrated_at': datetime.now().isoformat()
                    }
                }
                
                created_twin = self.twin_service.register_digital_twin(file_id, twin_data)
                twin_id = created_twin.twin_id if created_twin else None
                
                if not twin_id:
                    raise Exception("Failed to create twin for AASX integration")
            else:
                # Update existing twin with AASX integration
                twin = self.twin_repo.get_by_id(twin_id)
                if not twin:
                    raise Exception(f"Twin not found: {twin_id}")
                
                # Update twin metadata with AASX integration info
                metadata = getattr(twin, 'metadata', {})
                metadata.update({
                    'aasx_file_id': file_id,
                    'integration_type': 'aasx_file',
                    'integrated_at': datetime.now().isoformat()
                })
                twin.metadata = metadata
                twin.updated_at = datetime.now().isoformat()
                
                updated_twin = self.twin_repo.update(twin)
                if not updated_twin:
                    raise Exception(f"Failed to update twin for AASX integration: {twin_id}")
            
            result = {
                "success": True,
                "message": f"Successfully integrated twin {twin_id} with AASX file {file_id}",
                "twin_id": twin_id,
                "file_id": file_id,
                "integration_type": "aasx_file",
                "integrated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully integrated twin {twin_id} with AASX file {file_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to integrate with AASX file {file_id}: {str(e)}")
            raise Exception(f"Failed to integrate with AASX file {file_id}: {str(e)}")
    
    async def get_aasx_integrations(self, twin_id: str = None) -> List[Dict[str, Any]]:
        """
        Get AASX integrations for twins.
        
        Args:
            twin_id: Optional twin ID to filter by
            
        Returns:
            List of AASX integrations
        """
        try:
            logger.info(f"Getting AASX integrations - twin_id: {twin_id}")
            
            all_twins = self.twin_repo.get_all()
            integrations = []
            
            for twin in all_twins:
                metadata = getattr(twin, 'metadata', {})
                
                # Check if twin has AASX integration
                if metadata.get('integration_type') == 'aasx_file':
                    # Apply twin filter if specified
                    if twin_id and getattr(twin, 'twin_id', '') != twin_id:
                        continue
                    
                    integration = {
                        "twin_id": getattr(twin, 'twin_id', ''),
                        "twin_name": getattr(twin, 'twin_name', ''),
                        "file_id": metadata.get('aasx_file_id', ''),
                        "integration_type": metadata.get('integration_type', ''),
                        "integrated_at": metadata.get('integrated_at', ''),
                        "twin_status": getattr(twin, 'status', ''),
                        "health_status": getattr(twin, 'health_status', '')
                    }
                    
                    # Get file information if available
                    if self.file_repo and integration["file_id"]:
                        file_info = self.file_repo.get_by_id(integration["file_id"])
                        if file_info:
                            integration["file_name"] = getattr(file_info, 'filename', '')
                            integration["file_status"] = getattr(file_info, 'status', '')
                    
                    integrations.append(integration)
            
            logger.info(f"Found {len(integrations)} AASX integrations")
            return integrations
            
        except Exception as e:
            logger.error(f"Failed to get AASX integrations: {str(e)}")
            raise Exception(f"Failed to get AASX integrations: {str(e)}")
    
    async def sync_with_external_system(self, twin_id: str, external_system: str, 
                                      sync_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize twin with external system.
        
        Args:
            twin_id: The twin ID to sync
            external_system: External system identifier
            sync_config: Synchronization configuration
            
        Returns:
            Sync result
        """
        try:
            logger.info(f"Syncing twin {twin_id} with external system: {external_system}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            # Perform external system sync (placeholder implementation)
            sync_result = await self._perform_external_sync(twin, external_system, sync_config)
            
            # Update twin metadata with sync information
            metadata = getattr(twin, 'metadata', {})
            if 'external_syncs' not in metadata:
                metadata['external_syncs'] = {}
            
            metadata['external_syncs'][external_system] = {
                'last_sync': datetime.now().isoformat(),
                'sync_status': sync_result.get('status', 'unknown'),
                'sync_config': sync_config
            }
            
            twin.metadata = metadata
            twin.updated_at = datetime.now().isoformat()
            
            updated_twin = self.twin_repo.update(twin)
            if not updated_twin:
                raise Exception(f"Failed to update twin after sync: {twin_id}")
            
            result = {
                "success": True,
                "message": f"Successfully synced twin {twin_id} with {external_system}",
                "twin_id": twin_id,
                "external_system": external_system,
                "sync_result": sync_result,
                "synced_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully synced twin {twin_id} with {external_system}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to sync twin {twin_id} with {external_system}: {str(e)}")
            raise Exception(f"Failed to sync twin {twin_id} with {external_system}: {str(e)}")
    
    async def get_external_integrations(self, twin_id: str = None) -> List[Dict[str, Any]]:
        """
        Get external system integrations for twins.
        
        Args:
            twin_id: Optional twin ID to filter by
            
        Returns:
            List of external integrations
        """
        try:
            logger.info(f"Getting external integrations - twin_id: {twin_id}")
            
            all_twins = self.twin_repo.get_all()
            integrations = []
            
            for twin in all_twins:
                metadata = getattr(twin, 'metadata', {})
                external_syncs = metadata.get('external_syncs', {})
                
                # Apply twin filter if specified
                if twin_id and getattr(twin, 'twin_id', '') != twin_id:
                    continue
                
                for system_name, sync_info in external_syncs.items():
                    integration = {
                        "twin_id": getattr(twin, 'twin_id', ''),
                        "twin_name": getattr(twin, 'twin_name', ''),
                        "external_system": system_name,
                        "last_sync": sync_info.get('last_sync', ''),
                        "sync_status": sync_info.get('sync_status', ''),
                        "sync_config": sync_info.get('sync_config', {}),
                        "twin_status": getattr(twin, 'status', ''),
                        "health_status": getattr(twin, 'health_status', '')
                    }
                    integrations.append(integration)
            
            logger.info(f"Found {len(integrations)} external integrations")
            return integrations
            
        except Exception as e:
            logger.error(f"Failed to get external integrations: {str(e)}")
            raise Exception(f"Failed to get external integrations: {str(e)}")
    
    async def validate_integration(self, twin_id: str, integration_type: str) -> Dict[str, Any]:
        """
        Validate integration status for a twin.
        
        Args:
            twin_id: The twin ID to validate
            integration_type: Type of integration to validate ('aasx', 'external')
            
        Returns:
            Validation result
        """
        try:
            logger.info(f"Validating {integration_type} integration for twin: {twin_id}")
            
            # Get twin
            twin = self.twin_repo.get_by_id(twin_id)
            if not twin:
                raise Exception(f"Twin not found: {twin_id}")
            
            metadata = getattr(twin, 'metadata', {})
            validation_result = {
                "twin_id": twin_id,
                "integration_type": integration_type,
                "valid": False,
                "issues": [],
                "details": {}
            }
            
            if integration_type == "aasx":
                # Validate AASX integration
                if metadata.get('integration_type') == 'aasx_file':
                    file_id = metadata.get('aasx_file_id', '')
                    if file_id:
                        # Check if file exists
                        if self.file_repo:
                            file_info = self.file_repo.get_by_id(file_id)
                            if file_info:
                                validation_result["valid"] = True
                                validation_result["details"] = {
                                    "file_id": file_id,
                                    "file_name": getattr(file_info, 'filename', ''),
                                    "file_status": getattr(file_info, 'status', '')
                                }
                            else:
                                validation_result["issues"].append(f"AASX file not found: {file_id}")
                        else:
                            validation_result["valid"] = True
                            validation_result["details"] = {"file_id": file_id}
                    else:
                        validation_result["issues"].append("No AASX file ID in metadata")
                else:
                    validation_result["issues"].append("No AASX integration found")
            
            elif integration_type == "external":
                # Validate external integrations
                external_syncs = metadata.get('external_syncs', {})
                if external_syncs:
                    validation_result["valid"] = True
                    validation_result["details"] = {
                        "external_systems": list(external_syncs.keys()),
                        "sync_count": len(external_syncs)
                    }
                    
                    # Check sync status
                    for system_name, sync_info in external_syncs.items():
                        if sync_info.get('sync_status') != 'success':
                            validation_result["issues"].append(f"Sync failed for {system_name}")
                else:
                    validation_result["issues"].append("No external integrations found")
            
            else:
                validation_result["issues"].append(f"Unknown integration type: {integration_type}")
            
            validation_result["validated_at"] = datetime.now().isoformat()
            
            logger.info(f"Integration validation completed for twin {twin_id}: {validation_result['valid']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate integration for twin {twin_id}: {str(e)}")
            raise Exception(f"Failed to validate integration for twin {twin_id}: {str(e)}")
    
    async def get_integration_health(self, twin_id: str = None) -> Dict[str, Any]:
        """
        Get integration health status for twins.
        
        Args:
            twin_id: Optional twin ID to filter by
            
        Returns:
            Integration health information
        """
        try:
            logger.info(f"Getting integration health - twin_id: {twin_id}")
            
            all_twins = self.twin_repo.get_all()
            health_summary = {
                "total_twins": len(all_twins),
                "integrated_twins": 0,
                "aasx_integrations": 0,
                "external_integrations": 0,
                "healthy_integrations": 0,
                "issues": []
            }
            
            for twin in all_twins:
                # Apply twin filter if specified
                if twin_id and getattr(twin, 'twin_id', '') != twin_id:
                    continue
                
                metadata = getattr(twin, 'metadata', {})
                has_integration = False
                
                # Check AASX integration
                if metadata.get('integration_type') == 'aasx_file':
                    health_summary["aasx_integrations"] += 1
                    has_integration = True
                
                # Check external integrations
                external_syncs = metadata.get('external_syncs', {})
                if external_syncs:
                    health_summary["external_integrations"] += len(external_syncs)
                    has_integration = True
                    
                    # Check sync status
                    for system_name, sync_info in external_syncs.items():
                        if sync_info.get('sync_status') == 'success':
                            health_summary["healthy_integrations"] += 1
                        else:
                            health_summary["issues"].append(f"Sync issue for twin {getattr(twin, 'twin_id', '')} with {system_name}")
                
                if has_integration:
                    health_summary["integrated_twins"] += 1
            
            # Calculate health score
            total_integrations = health_summary["aasx_integrations"] + health_summary["external_integrations"]
            if total_integrations > 0:
                health_score = (health_summary["healthy_integrations"] / total_integrations) * 100
            else:
                health_score = 100
            
            health_summary["health_score"] = health_score
            health_summary["health_status"] = "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical"
            health_summary["generated_at"] = datetime.now().isoformat()
            
            logger.info(f"Integration health summary: {health_summary['health_status']} (score: {health_score:.1f}%)")
            return health_summary
            
        except Exception as e:
            logger.error(f"Failed to get integration health: {str(e)}")
            raise Exception(f"Failed to get integration health: {str(e)}")
    
    async def _perform_external_sync(self, twin, external_system: str, 
                                   sync_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform external system synchronization (placeholder implementation).
        
        Args:
            twin: Twin object
            external_system: External system identifier
            sync_config: Synchronization configuration
            
        Returns:
            Sync result
        """
        try:
            # Simulate external sync process
            await asyncio.sleep(1)  # Simulate network delay
            
            # Placeholder sync logic
            sync_result = {
                "status": "success",
                "message": f"Successfully synced with {external_system}",
                "sync_type": sync_config.get('sync_type', 'full'),
                "records_synced": 150,
                "errors": 0,
                "duration_ms": 1200
            }
            
            # Simulate occasional failures
            if external_system == "problematic_system":
                sync_result["status"] = "failed"
                sync_result["message"] = "External system unavailable"
                sync_result["errors"] = 5
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error performing external sync: {str(e)}")
            return {
                "status": "failed",
                "message": f"Sync failed: {str(e)}",
                "errors": 1
            }
    
    async def export_integration_data(self, twin_id: str = None, 
                                    format: str = "json") -> Dict[str, Any]:
        """
        Export integration data for twins.
        
        Args:
            twin_id: Optional twin ID to filter by
            format: Export format ('json', 'csv')
            
        Returns:
            Exported integration data
        """
        try:
            logger.info(f"Exporting integration data - twin_id: {twin_id}, format: {format}")
            
            # Get integration data
            aasx_integrations = await self.get_aasx_integrations(twin_id)
            external_integrations = await self.get_external_integrations(twin_id)
            
            # Combine data
            integration_data = {
                "aasx_integrations": aasx_integrations,
                "external_integrations": external_integrations,
                "export_metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "total_aasx_integrations": len(aasx_integrations),
                    "total_external_integrations": len(external_integrations)
                }
            }
            
            # Format data
            if format == "json":
                formatted_data = integration_data
            elif format == "csv":
                # Convert to CSV format
                csv_data = []
                
                # AASX integrations
                for integration in aasx_integrations:
                    csv_data.append({
                        "integration_type": "aasx",
                        "twin_id": integration.get("twin_id", ""),
                        "twin_name": integration.get("twin_name", ""),
                        "file_id": integration.get("file_id", ""),
                        "file_name": integration.get("file_name", ""),
                        "integrated_at": integration.get("integrated_at", ""),
                        "status": integration.get("twin_status", "")
                    })
                
                # External integrations
                for integration in external_integrations:
                    csv_data.append({
                        "integration_type": "external",
                        "twin_id": integration.get("twin_id", ""),
                        "twin_name": integration.get("twin_name", ""),
                        "external_system": integration.get("external_system", ""),
                        "last_sync": integration.get("last_sync", ""),
                        "sync_status": integration.get("sync_status", ""),
                        "status": integration.get("twin_status", "")
                    })
                
                formatted_data = self._convert_to_csv(csv_data)
            else:
                formatted_data = integration_data
            
            result = {
                "format": format,
                "twin_id": twin_id,
                "exported_at": datetime.now().isoformat(),
                "data": formatted_data
            }
            
            logger.info(f"Integration data exported successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to export integration data: {str(e)}")
            raise Exception(f"Failed to export integration data: {str(e)}")
    
    def _convert_to_csv(self, data: List[Dict[str, Any]]) -> str:
        """Convert data to CSV format."""
        try:
            if not data:
                return ""
            
            # Get headers from first item
            headers = list(data[0].keys())
            csv_lines = [','.join(headers)]
            
            for item in data:
                row = [str(item.get(header, '')) for header in headers]
                csv_lines.append(','.join(row))
            
            return '\n'.join(csv_lines)
            
        except Exception as e:
            logger.error(f"Error converting to CSV: {str(e)}")
            return str(data) 