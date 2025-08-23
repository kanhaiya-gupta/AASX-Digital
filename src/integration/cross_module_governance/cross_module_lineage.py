"""
Cross-Module Lineage Service

This service tracks data lineage across module boundaries, providing
visibility into how data flows and transforms between different modules
in the AAS Data Modeling Engine.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from .models import DataLineage, LineageType, ComplianceStatus


logger = logging.getLogger(__name__)


class CrossModuleLineageService:
    """
    Service for tracking data lineage across module boundaries.
    
    This service provides:
    - Data flow tracking between modules
    - Transformation history and details
    - Lineage querying and visualization
    - Compliance status tracking
    """
    
    def __init__(self):
        """Initialize the cross-module lineage service."""
        self.lineages: Dict[UUID, DataLineage] = {}
        self.module_lineages: Dict[str, Set[UUID]] = {}  # module_name -> lineage_ids
        self.data_lineages: Dict[str, Set[UUID]] = {}    # data_id -> lineage_ids
        self.is_monitoring = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def start_lineage_tracking(self) -> None:
        """Start automatic lineage tracking."""
        if self.is_monitoring:
            logger.warning("Lineage tracking is already running")
            return
        
        self.is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._lineage_monitoring_loop())
        logger.info("Started cross-module lineage tracking")
    
    async def stop_lineage_tracking(self) -> None:
        """Stop automatic lineage tracking."""
        self.is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped cross-module lineage tracking")
    
    async def _lineage_monitoring_loop(self) -> None:
        """Background task for monitoring lineage changes."""
        while self.is_monitoring:
            try:
                await self._process_lineage_updates()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in lineage monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def _process_lineage_updates(self) -> None:
        """Process any pending lineage updates."""
        # This would typically process lineage updates from event queues
        # For now, we'll just log that we're monitoring
        logger.debug("Processing lineage updates...")
    
    def create_lineage(
        self,
        source_module: str,
        target_module: str,
        source_data_id: str,
        target_data_id: str,
        lineage_type: LineageType = LineageType.DATA_FLOW,
        transformation_details: Optional[Dict[str, Any]] = None,
        data_schema: Optional[Dict[str, Any]] = None,
        quality_metrics: Optional[Dict[str, float]] = None
    ) -> DataLineage:
        """
        Create a new data lineage record.
        
        Args:
            source_module: Name of the source module
            target_module: Name of the target module
            source_data_id: ID of the source data
            target_data_id: ID of the target data
            lineage_type: Type of lineage relationship
            transformation_details: Details about data transformation
            data_schema: Schema information about the data
            quality_metrics: Quality metrics for the data
            
        Returns:
            Created DataLineage instance
        """
        lineage = DataLineage(
            source_module=source_module,
            target_module=target_module,
            source_data_id=source_data_id,
            target_data_id=target_data_id,
            lineage_type=lineage_type,
            transformation_details=transformation_details or {},
            data_schema=data_schema or {},
            quality_metrics=quality_metrics or {}
        )
        
        # Store lineage
        self.lineages[lineage.lineage_id] = lineage
        
        # Update indexes
        if source_module not in self.module_lineages:
            self.module_lineages[source_module] = set()
        if target_module not in self.module_lineages:
            self.module_lineages[target_module] = set()
        
        self.module_lineages[source_module].add(lineage.lineage_id)
        self.module_lineages[target_module].add(lineage.lineage_id)
        
        # Update data indexes
        if source_data_id not in self.data_lineages:
            self.data_lineages[source_data_id] = set()
        if target_data_id not in self.data_lineages:
            self.data_lineages[target_data_id] = set()
        
        self.data_lineages[source_data_id].add(lineage.lineage_id)
        self.data_lineages[target_data_id].add(lineage.lineage_id)
        
        logger.info(f"Created lineage: {source_module} -> {target_module} ({lineage_type.value})")
        return lineage
    
    def get_lineage_by_id(self, lineage_id: UUID) -> Optional[DataLineage]:
        """Get lineage by ID."""
        return self.lineages.get(lineage_id)
    
    def get_lineages_by_module(self, module_name: str) -> List[DataLineage]:
        """Get all lineages involving a specific module."""
        lineage_ids = self.module_lineages.get(module_name, set())
        return [self.lineages[lineage_id] for lineage_id in lineage_ids if lineage_id in self.lineages]
    
    def get_lineages_by_data_id(self, data_id: str) -> List[DataLineage]:
        """Get all lineages involving a specific data ID."""
        lineage_ids = self.data_lineages.get(data_id, set())
        return [self.lineages[lineage_id] for lineage_id in lineage_ids if lineage_id in self.lineages]
    
    def get_data_flow_path(
        self,
        start_module: str,
        end_module: str,
        max_depth: int = 5
    ) -> List[DataLineage]:
        """
        Get the data flow path between two modules.
        
        Args:
            start_module: Starting module name
            end_module: Ending module name
            max_depth: Maximum depth to search
            
        Returns:
            List of lineages forming the path
        """
        if start_module == end_module:
            return []
        
        visited = set()
        queue = [(start_module, [])]
        
        while queue and len(queue[0][1]) < max_depth:
            current_module, path = queue.pop(0)
            
            if current_module in visited:
                continue
            
            visited.add(current_module)
            
            # Get all lineages from current module
            lineages = self.get_lineages_by_module(current_module)
            
            for lineage in lineages:
                if lineage.target_module == end_module:
                    # Found the target
                    return path + [lineage]
                
                # Continue searching
                new_path = path + [lineage]
                queue.append((lineage.target_module, new_path))
        
        return []  # No path found
    
    def update_lineage_compliance(
        self,
        lineage_id: UUID,
        compliance_status: ComplianceStatus,
        compliance_notes: Optional[str] = None
    ) -> bool:
        """
        Update compliance status of a lineage.
        
        Args:
            lineage_id: ID of the lineage to update
            compliance_status: New compliance status
            compliance_notes: Optional notes about compliance
            
        Returns:
            True if updated successfully, False otherwise
        """
        if lineage_id not in self.lineages:
            logger.warning(f"Lineage not found: {lineage_id}")
            return False
        
        lineage = self.lineages[lineage_id]
        lineage.compliance_status = compliance_status
        lineage.updated_at = datetime.utcnow()
        
        if compliance_notes:
            lineage.metadata["compliance_notes"] = compliance_notes
        
        logger.info(f"Updated lineage compliance: {lineage_id} -> {compliance_status.value}")
        return True
    
    def get_lineage_summary(self) -> Dict[str, Any]:
        """Get summary of all lineages."""
        total_lineages = len(self.lineages)
        module_count = len(self.module_lineages)
        data_count = len(self.data_lineages)
        
        # Count by type
        type_counts = {}
        for lineage in self.lineages.values():
            lineage_type = lineage.lineage_type.value
            type_counts[lineage_type] = type_counts.get(lineage_type, 0) + 1
        
        # Count by compliance status
        compliance_counts = {}
        for lineage in self.lineages.values():
            status = lineage.compliance_status.value
            compliance_counts[status] = compliance_counts.get(status, 0) + 1
        
        return {
            "total_lineages": total_lineages,
            "modules_involved": module_count,
            "data_entities": data_count,
            "lineage_types": type_counts,
            "compliance_status": compliance_counts,
            "is_monitoring": self.is_monitoring
        }
    
    def export_lineage_data(self, format: str = "json") -> str:
        """
        Export lineage data in specified format.
        
        Args:
            format: Export format (json, csv, etc.)
            
        Returns:
            Exported data as string
        """
        if format.lower() == "json":
            import json
            data = {
                "lineages": [lineage.to_dict() for lineage in self.lineages.values()],
                "summary": self.get_lineage_summary(),
                "exported_at": datetime.utcnow().isoformat()
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_old_lineages(self, days_old: int = 90) -> int:
        """
        Clean up lineages older than specified days.
        
        Args:
            days_old: Remove lineages older than this many days
            
        Returns:
            Number of lineages removed
        """
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
        
        lineages_to_remove = []
        for lineage_id, lineage in self.lineages.items():
            if lineage.created_at < cutoff_date:
                lineages_to_remove.append(lineage_id)
        
        for lineage_id in lineages_to_remove:
            self._remove_lineage(lineage_id)
        
        logger.info(f"Cleaned up {len(lineages_to_remove)} old lineages")
        return len(lineages_to_remove)
    
    def _remove_lineage(self, lineage_id: UUID) -> None:
        """Remove a lineage and update indexes."""
        if lineage_id not in self.lineages:
            return
        
        lineage = self.lineages[lineage_id]
        
        # Remove from module indexes
        if lineage.source_module in self.module_lineages:
            self.module_lineages[lineage.source_module].discard(lineage_id)
        if lineage.target_module in self.module_lineages:
            self.module_lineages[lineage.target_module].discard(lineage_id)
        
        # Remove from data indexes
        if lineage.source_data_id in self.data_lineages:
            self.data_lineages[lineage.source_data_id].discard(lineage_id)
        if lineage.target_data_id in self.data_lineages:
            self.data_lineages[lineage.target_data_id].discard(lineage_id)
        
        # Remove lineage
        del self.lineages[lineage_id]


