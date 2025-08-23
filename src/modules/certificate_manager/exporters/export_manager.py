"""
Export Manager for Certificate Manager

Orchestrates all export operations and manages multiple exporters.
Provides a unified interface for certificate exports in multiple formats.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

from .base_exporter import BaseExporter, ExportFormat, ExportOptions
from .html_exporter import HTMLExporter
from .pdf_exporter import PDFExporter
from .json_exporter import JSONExporter
from .xml_exporter import XMLExporter

logger = logging.getLogger(__name__)


class ExportManager:
    """
    Export orchestration service
    
    Manages multiple exporters and provides a unified interface
    for certificate exports in various formats.
    """
    
    def __init__(self):
        """Initialize the export manager"""
        self.exporters: Dict[ExportFormat, BaseExporter] = {}
        self.export_queue: asyncio.Queue = asyncio.Queue()
        self.active_exports: Dict[str, Dict[str, Any]] = {}
        self.export_history: List[Dict[str, Any]] = []
        self.export_locks: Dict[str, asyncio.Lock] = {}
        
        # Initialize all exporters
        self._initialize_exporters()
        
        # Start export processor
        self._export_processor_task: Optional[asyncio.Task] = None
        self._start_export_processor()
        
        logger.info("Export Manager initialized successfully")
    
    def _initialize_exporters(self) -> None:
        """Initialize all available exporters"""
        self.exporters[ExportFormat.HTML] = HTMLExporter()
        self.exporters[ExportFormat.PDF] = PDFExporter()
        self.exporters[ExportFormat.JSON] = JSONExporter()
        self.exporters[ExportFormat.XML] = XMLExporter()
        
        logger.info(f"Initialized {len(self.exporters)} exporters")
    
    def _start_export_processor(self) -> None:
        """Start the background export processor"""
        self._export_processor_task = asyncio.create_task(self._process_export_queue())
        logger.info("Export processor started")
    
    async def export_certificate(
        self,
        certificate_data: Dict[str, Any],
        export_formats: List[ExportFormat],
        options: Optional[ExportOptions] = None,
        output_dir: Optional[Path] = None,
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Export certificate in multiple formats
        
        Args:
            certificate_data: Certificate data to export
            export_formats: List of formats to export
            options: Export configuration options
            output_dir: Directory to save exported files
            priority: Export priority (1=high, 5=low)
            
        Returns:
            Dictionary containing export job information
        """
        certificate_id = certificate_data.get("certificate_id", "unknown")
        
        # Create export job
        export_job = {
            "job_id": f"export_{certificate_id}_{asyncio.get_event_loop().time()}",
            "certificate_id": certificate_id,
            "export_formats": export_formats,
            "options": options or ExportOptions(),
            "output_dir": output_dir or Path("exports"),
            "priority": priority,
            "status": "queued",
            "created_at": asyncio.get_event_loop().time(),
            "results": {}
        }
        
        # Add to export queue
        await self.export_queue.put((priority, export_job))
        
        # Update active exports
        self.active_exports[export_job["job_id"]] = export_job
        
        logger.info(f"Export job {export_job['job_id']} queued for {len(export_formats)} formats")
        
        return export_job
    
    async def export_certificate_sync(
        self,
        certificate_data: Dict[str, Any],
        export_format: ExportFormat,
        options: Optional[ExportOptions] = None,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Export certificate synchronously in a single format
        
        Args:
            certificate_data: Certificate data to export
            export_format: Format to export
            options: Export configuration options
            output_path: Path to save exported file
            
        Returns:
            Dictionary containing export result
        """
        if export_format not in self.exporters:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        exporter = self.exporters[export_format]
        
        # Generate output path if not provided
        if not output_path:
            filename = f"certificate_{certificate_data.get('certificate_id', 'unknown')}.{export_format.value}"
            output_path = Path("exports") / filename
        
        # Perform export
        result = await exporter.export_certificate(certificate_data, options, output_path)
        
        # Record in history
        self.export_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "certificate_id": certificate_data.get("certificate_id"),
            "format": export_format.value,
            "success": True,
            "file_size": result.get("file_size", 0)
        })
        
        return result
    
    async def get_export_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an export job"""
        return self.active_exports.get(job_id)
    
    async def get_all_export_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all active export jobs"""
        return list(self.active_exports.values())
    
    async def cancel_export(self, job_id: str) -> bool:
        """Cancel an export job"""
        if job_id in self.active_exports:
            job = self.active_exports[job_id]
            job["status"] = "cancelled"
            logger.info(f"Export job {job_id} cancelled")
            return True
        return False
    
    async def get_export_history(
        self,
        certificate_id: Optional[str] = None,
        format_type: Optional[ExportFormat] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get export history with optional filtering"""
        history = self.export_history.copy()
        
        # Filter by certificate ID
        if certificate_id:
            history = [h for h in history if h.get("certificate_id") == certificate_id]
        
        # Filter by format
        if format_type:
            history = [h for h in history if h.get("format") == format_type.value]
        
        # Sort by timestamp (newest first) and limit results
        history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return history[:limit]
    
    async def get_supported_formats(self) -> List[Dict[str, Any]]:
        """Get information about supported export formats"""
        formats = []
        for format_type, exporter in self.exporters.items():
            formats.append({
                "format": format_type.value,
                "mime_type": await self._get_mime_type(format_type),
                "file_extension": format_type.value,
                "supports_styling": await self._get_supports_styling(format_type),
                "supports_metadata": True,
                "supports_metrics": True
            })
        return formats
    
    async def validate_export_request(
        self,
        certificate_data: Dict[str, Any],
        export_formats: List[ExportFormat],
        options: Optional[ExportOptions] = None
    ) -> Dict[str, Any]:
        """
        Validate an export request before processing
        
        Args:
            certificate_data: Certificate data to validate
            export_formats: Formats to validate
            options: Export options to validate
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "format_validations": {}
        }
        
        # Validate certificate data
        if not certificate_data:
            validation_result["valid"] = False
            validation_result["errors"].append("Certificate data is required")
            return validation_result
        
        # Validate export formats
        for format_type in export_formats:
            if format_type not in self.exporters:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Unsupported export format: {format_type.value}")
                continue
            
            # Validate with specific exporter
            exporter = self.exporters[format_type]
            try:
                is_valid = await exporter.validate_export_data(certificate_data, options or ExportOptions())
                validation_result["format_validations"][format_type.value] = is_valid
                
                if not is_valid:
                    validation_result["warnings"].append(f"Format {format_type.value} validation failed")
            except Exception as e:
                validation_result["format_validations"][format_type.value] = False
                validation_result["warnings"].append(f"Format {format_type.value} validation error: {str(e)}")
        
        # Check if any format validation failed
        if any(not valid for valid in validation_result["format_validations"].values()):
            validation_result["warnings"].append("Some export formats failed validation")
        
        return validation_result
    
    async def _process_export_queue(self) -> None:
        """Background task to process export queue"""
        try:
            while True:
                # Get next export job from queue
                priority, export_job = await self.export_queue.get()
                
                try:
                    await self._process_export_job(export_job)
                except Exception as e:
                    logger.error(f"Failed to process export job {export_job['job_id']}: {e}")
                    export_job["status"] = "failed"
                    export_job["error"] = str(e)
                
                finally:
                    # Mark task as done
                    self.export_queue.task_done()
                    
        except asyncio.CancelledError:
            logger.info("Export processor cancelled")
        except Exception as e:
            logger.error(f"Export processor error: {e}")
    
    async def _process_export_job(self, export_job: Dict[str, Any]) -> None:
        """Process a single export job"""
        job_id = export_job["job_id"]
        certificate_id = export_job["certificate_id"]
        
        logger.info(f"Processing export job {job_id} for certificate {certificate_id}")
        
        # Update status
        export_job["status"] = "processing"
        export_job["started_at"] = asyncio.get_event_loop().time()
        
        # Process each format
        for format_type in export_job["export_formats"]:
            if format_type not in self.exporters:
                export_job["results"][format_type.value] = {
                    "success": False,
                    "error": f"Unsupported format: {format_type.value}"
                }
                continue
            
            try:
                # Generate output path
                filename = f"certificate_{certificate_id}.{format_type.value}"
                output_path = export_job["output_dir"] / filename
                
                # Perform export
                exporter = self.exporters[format_type]
                result = await exporter.export_certificate(
                    export_job["certificate_data"],
                    export_job["options"],
                    output_path
                )
                
                export_job["results"][format_type.value] = {
                    "success": True,
                    "file_path": str(output_path),
                    "file_size": result.get("file_size", 0),
                    "mime_type": result.get("mime_type", "")
                }
                
                logger.info(f"Exported {format_type.value} for job {job_id}")
                
            except Exception as e:
                export_job["results"][format_type.value] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"Failed to export {format_type.value} for job {job_id}: {e}")
        
        # Update final status
        export_job["status"] = "completed"
        export_job["completed_at"] = asyncio.get_event_loop().time()
        
        # Record in history
        self.export_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "job_id": job_id,
            "certificate_id": certificate_id,
            "formats": [f.value for f in export_job["export_formats"]],
            "success": all(r.get("success", False) for r in export_job["results"].values()),
            "total_size": sum(r.get("file_size", 0) for r in export_job["results"].values() if r.get("success"))
        })
        
        logger.info(f"Export job {job_id} completed")
    
    async def _get_mime_type(self, format_type: ExportFormat) -> str:
        """Get MIME type for export format"""
        mime_types = {
            ExportFormat.HTML: "text/html",
            ExportFormat.PDF: "application/pdf",
            ExportFormat.JSON: "application/json",
            ExportFormat.XML: "application/xml"
        }
        return mime_types.get(format_type, "application/octet-stream")
    
    async def _get_supports_styling(self, format_type: ExportFormat) -> bool:
        """Check if format supports styling"""
        styling_support = {
            ExportFormat.HTML: True,
            ExportFormat.PDF: False,
            ExportFormat.JSON: False,
            ExportFormat.XML: False
        }
        return styling_support.get(format_type, False)
    
    async def stop_export_processor(self) -> None:
        """Stop the export processor"""
        if self._export_processor_task:
            self._export_processor_task.cancel()
            try:
                await self._export_processor_task
            except asyncio.CancelledError:
                pass
            self._export_processor_task = None
            logger.info("Export processor stopped")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the export manager"""
        return {
            "status": "healthy",
            "active_exports": len(self.active_exports),
            "queue_size": self.export_queue.qsize(),
            "exporters": len(self.exporters),
            "export_history_size": len(self.export_history),
            "processor_running": self._export_processor_task is not None and not self._export_processor_task.done()
        } 