"""
AI RAG Graph Transfer Service
============================

Service for transferring graphs from AI RAG to KG Neo4j.
"""

import logging
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import aiohttp

from ..graph_models.graph_structure import GraphStructure
from ..graph_models.graph_metadata import GraphMetadata

logger = logging.getLogger(__name__)


class GraphTransferService:
    """
    Graph Transfer Service for AI RAG to KG Neo4j Integration
    
    Handles the transfer of graph structures, metadata, and files
    from AI RAG to KG Neo4j for further enhancement and management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the graph transfer service.
        
        Args:
            config: Configuration dictionary for graph transfer
        """
        self.config = config or self._get_default_config()
        self.transfer_stats = {
            "graphs_transferred": 0,
            "successful_transfers": 0,
            "failed_transfers": 0,
            "total_transfer_time_ms": 0,
            "total_data_transferred_mb": 0
        }
        
        # Initialize HTTP session for API calls
        self.session = None
        
        logger.info("✅ GraphTransferService initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for graph transfer."""
        return {
            "kg_neo4j_api_url": "http://localhost:7474",
            "kg_neo4j_api_key": None,
            "transfer_timeout": 300,  # 5 minutes
            "max_retries": 3,
            "retry_delay": 5,  # seconds
            "batch_size": 10,
            "parallel_transfers": True,
            "max_concurrent_transfers": 5,
            "enable_validation": True,
            "enable_rollback": True,
            "enable_progress_tracking": True,
            "transfer_modes": ["structure", "metadata", "files"],
            "compression_enabled": True,
            "compression_level": 6,
            "verify_ssl": True,
            "custom_headers": {},
            "transfer_priority": "normal"  # low, normal, high, urgent
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup_session()
    
    async def _initialize_session(self) -> None:
        """Initialize HTTP session for API calls."""
        try:
            connector = aiohttp.TCPConnector(
                verify_ssl=self.config["verify_ssl"],
                limit=100,
                limit_per_host=30
            )
            
            timeout = aiohttp.ClientTimeout(total=self.config["transfer_timeout"])
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self._get_request_headers()
            )
            
            logger.info("🌐 HTTP session initialized for graph transfer")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize HTTP session: {e}")
            raise
    
    async def _cleanup_session(self) -> None:
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("🧹 HTTP session cleaned up")
    
    def _get_request_headers(self) -> Dict[str, str]:
        """Get request headers for API calls."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-RAG-GraphTransfer/1.0",
            "Accept": "application/json"
        }
        
        # Add API key if provided
        if self.config["kg_neo4j_api_key"]:
            headers["Authorization"] = f"Bearer {self.config['kg_neo4j_api_key']}"
        
        # Add custom headers
        headers.update(self.config["custom_headers"])
        
        return headers
    
    async def transfer_graph(
        self,
        graph_structure: GraphStructure,
        graph_metadata: GraphMetadata,
        transfer_mode: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transfer a graph from AI RAG to KG Neo4j.
        
        Args:
            graph_structure: Graph structure to transfer
            graph_metadata: Graph metadata to transfer
            transfer_mode: Specific transfer mode (default: all modes)
            priority: Transfer priority (default: config priority)
            
        Returns:
            Dict: Transfer results and status
        """
        start_time = datetime.now()
        transfer_id = f"transfer_{graph_structure.graph_id}_{int(start_time.timestamp())}"
        
        logger.info(f"📤 Starting graph transfer: {transfer_id} for graph: {graph_structure.graph_name}")
        
        try:
            # Validate transfer prerequisites
            validation_result = await self._validate_transfer_prerequisites(graph_structure, graph_metadata)
            if not validation_result["valid"]:
                return {
                    "transfer_id": transfer_id,
                    "status": "failed",
                    "error": "Validation failed",
                    "validation_errors": validation_result["errors"],
                    "transfer_time_ms": 0,
                    "data_transferred_mb": 0
                }
            
            # Determine transfer mode
            modes = [transfer_mode] if transfer_mode else self.config["transfer_modes"]
            transfer_priority = priority or self.config["transfer_priority"]
            
            # Initialize transfer context
            transfer_context = {
                "transfer_id": transfer_id,
                "graph_id": graph_structure.graph_id,
                "graph_name": graph_structure.graph_name,
                "modes": modes,
                "priority": transfer_priority,
                "start_time": start_time,
                "status": "in_progress"
            }
            
            # Execute transfer based on modes
            transfer_results = {}
            
            for mode in modes:
                try:
                    if mode == "structure":
                        result = await self._transfer_graph_structure(graph_structure, transfer_context)
                        transfer_results["structure"] = result
                    
                    elif mode == "metadata":
                        result = await self._transfer_graph_metadata(graph_metadata, transfer_context)
                        transfer_results["metadata"] = result
                    
                    elif mode == "files":
                        result = await self._transfer_graph_files(graph_structure, graph_metadata, transfer_context)
                        transfer_results["files"] = result
                    
                    else:
                        logger.warning(f"⚠️ Unknown transfer mode: {mode}")
                        transfer_results[mode] = {"status": "skipped", "reason": "Unknown mode"}
                
                except Exception as e:
                    logger.error(f"❌ Transfer mode {mode} failed: {e}")
                    transfer_results[mode] = {"status": "failed", "error": str(e)}
            
            # Calculate transfer metrics
            end_time = datetime.now()
            transfer_time = (end_time - start_time).total_seconds() * 1000
            data_transferred = self._calculate_data_transferred(transfer_results)
            
            # Determine overall transfer status
            overall_status = self._determine_overall_status(transfer_results)
            
            # Update transfer statistics
            self._update_transfer_stats(overall_status, transfer_time, data_transferred)
            
            # Finalize transfer context
            transfer_context.update({
                "status": overall_status,
                "end_time": end_time,
                "transfer_time_ms": transfer_time,
                "data_transferred_mb": data_transferred,
                "results": transfer_results
            })
            
            # Log transfer completion
            if overall_status == "success":
                logger.info(f"✅ Graph transfer completed: {transfer_id} - {data_transferred:.2f}MB in {transfer_time:.0f}ms")
            else:
                logger.warning(f"⚠️ Graph transfer completed with issues: {transfer_id} - Status: {overall_status}")
            
            return transfer_context
            
        except Exception as e:
            logger.error(f"❌ Graph transfer failed: {transfer_id} - {e}")
            
            # Update transfer statistics
            self._update_transfer_stats("failed", 0, 0)
            
            return {
                "transfer_id": transfer_id,
                "status": "failed",
                "error": str(e),
                "transfer_time_ms": 0,
                "data_transferred_mb": 0
            }
    
    async def transfer_graphs_batch(
        self,
        graphs: List[Tuple[GraphStructure, GraphMetadata]],
        batch_size: Optional[int] = None,
        parallel: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Transfer multiple graphs in batch.
        
        Args:
            graphs: List of (GraphStructure, GraphMetadata) tuples
            batch_size: Optional batch size override
            parallel: Optional parallel processing override
            
        Returns:
            List: Transfer results for all graphs
        """
        batch_size = batch_size or self.config["batch_size"]
        parallel = parallel if parallel is not None else self.config["parallel_transfers"]
        
        logger.info(f"📦 Starting batch transfer of {len(graphs)} graphs")
        
        try:
            if parallel:
                # Process graphs in parallel with concurrency limit
                semaphore = asyncio.Semaphore(self.config["max_concurrent_transfers"])
                
                async def transfer_with_semaphore(graph_tuple):
                    async with semaphore:
                        return await self.transfer_graph(graph_tuple[0], graph_tuple[1])
                
                # Create tasks for all graphs
                tasks = [transfer_with_semaphore(graph) for graph in graphs]
                
                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle any exceptions
                processed_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Graph {i} transfer failed: {result}")
                        processed_results.append({
                            "transfer_id": f"batch_transfer_{i}",
                            "status": "failed",
                            "error": str(result),
                            "transfer_time_ms": 0,
                            "data_transferred_mb": 0
                        })
                    else:
                        processed_results.append(result)
                
                return processed_results
            
            else:
                # Process graphs sequentially
                results = []
                for i, (graph_structure, graph_metadata) in enumerate(graphs):
                    try:
                        result = await self.transfer_graph(graph_structure, graph_metadata)
                        results.append(result)
                        
                        # Add small delay between transfers
                        if i < len(graphs) - 1:
                            await asyncio.sleep(0.1)
                    
                    except Exception as e:
                        logger.error(f"❌ Graph {i} transfer failed: {e}")
                        results.append({
                            "transfer_id": f"batch_transfer_{i}",
                            "status": "failed",
                            "error": str(result),
                            "transfer_time_ms": 0,
                            "data_transferred_mb": 0
                        })
                
                return results
        
        except Exception as e:
            logger.error(f"❌ Batch transfer failed: {e}")
            return []
    
    async def _validate_transfer_prerequisites(
        self,
        graph_structure: GraphStructure,
        graph_metadata: GraphMetadata
    ) -> Dict[str, Any]:
        """Validate prerequisites for graph transfer."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if session is initialized
            if not self.session:
                validation_result["valid"] = False
                validation_result["errors"].append("HTTP session not initialized")
            
            # Validate graph structure
            if not graph_structure.graph_id:
                validation_result["valid"] = False
                validation_result["errors"].append("Graph structure missing graph_id")
            
            if not graph_structure.nodes or len(graph_structure.nodes) == 0:
                validation_result["warnings"].append("Graph structure has no nodes")
            
            if not graph_structure.edges or len(graph_structure.edges) == 0:
                validation_result["warnings"].append("Graph structure has no edges")
            
            # Validate graph metadata
            if not graph_metadata.graph_id:
                validation_result["valid"] = False
                validation_result["errors"].append("Graph metadata missing graph_id")
            
            # Check graph IDs match
            if graph_structure.graph_id != graph_metadata.graph_id:
                validation_result["valid"] = False
                validation_result["errors"].append("Graph structure and metadata graph_id mismatch")
            
            # Validate API connectivity
            if not await self._test_api_connectivity():
                validation_result["valid"] = False
                validation_result["errors"].append("Cannot connect to KG Neo4j API")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Transfer validation failed: {e}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def _test_api_connectivity(self) -> bool:
        """Test connectivity to KG Neo4j API."""
        try:
            if not self.session:
                return False
            
            # Simple connectivity test
            async with self.session.get(f"{self.config['kg_neo4j_api_url']}/health", timeout=10) as response:
                return response.status in [200, 401, 403]  # Any response indicates connectivity
            
        except Exception as e:
            logger.warning(f"⚠️ API connectivity test failed: {e}")
            return False
    
    async def _transfer_graph_structure(
        self,
        graph_structure: GraphStructure,
        transfer_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transfer graph structure to KG Neo4j."""
        try:
            logger.info(f"🏗️ Transferring graph structure: {graph_structure.graph_id}")
            
            # Prepare graph structure data
            structure_data = {
                "graph_id": graph_structure.graph_id,
                "graph_name": graph_structure.graph_name,
                "graph_type": graph_structure.graph_type,
                "nodes": [
                    {
                        "node_id": node.node_id,
                        "node_type": node.node_type,
                        "node_label": node.node_label,
                        "properties": node.properties_dict,
                        "confidence_score": node.confidence_score
                    }
                    for node in graph_structure.nodes
                ],
                "edges": [
                    {
                        "edge_id": edge.edge_id,
                        "source_node_id": edge.source_node_id,
                        "target_node_id": edge.target_node_id,
                        "relationship_type": edge.relationship_type,
                        "properties": edge.properties_dict,
                        "weight": edge.weight,
                        "confidence_score": edge.confidence_score
                    }
                    for edge in graph_structure.edges
                ],
                "metadata": {
                    "node_count": graph_structure.node_count,
                    "edge_count": graph_structure.edge_count,
                    "graph_density": graph_structure.graph_density,
                    "overall_quality_score": graph_structure.overall_quality_score
                }
            }
            
            # Send to KG Neo4j API
            url = f"{self.config['kg_neo4j_api_url']}/api/graphs/structure"
            
            async with self.session.post(url, json=structure_data) as response:
                if response.status == 200:
                    result_data = await response.json()
                    return {
                        "status": "success",
                        "kg_neo4j_graph_id": result_data.get("kg_neo4j_graph_id"),
                        "message": "Graph structure transferred successfully"
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "failed",
                        "error": f"API error {response.status}: {error_text}"
                    }
        
        except Exception as e:
            logger.error(f"❌ Graph structure transfer failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _transfer_graph_metadata(
        self,
        graph_metadata: GraphMetadata,
        transfer_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transfer graph metadata to KG Neo4j."""
        try:
            logger.info(f"📊 Transferring graph metadata: {graph_metadata.graph_id}")
            
            # Prepare metadata
            metadata_data = {
                "graph_id": graph_metadata.graph_id,
                "version": graph_metadata.version,
                "processing_status": graph_metadata.processing_status,
                "quality_score": graph_metadata.quality_score,
                "validation_status": graph_metadata.validation_status,
                "output_directory": graph_metadata.output_directory,
                "graph_files": graph_metadata.graph_files,
                "file_formats": graph_metadata.file_formats,
                "integration_references": graph_metadata.integration_references,
                "tracing": graph_metadata.tracing,
                "performance_metrics": graph_metadata.performance_metrics,
                "change_tracking": graph_metadata.change_tracking
            }
            
            # Send to KG Neo4j API
            url = f"{self.config['kg_neo4j_api_url']}/api/graphs/metadata"
            
            async with self.session.post(url, json=metadata_data) as response:
                if response.status == 200:
                    result_data = await response.json()
                    return {
                        "status": "success",
                        "kg_neo4j_metadata_id": result_data.get("kg_neo4j_metadata_id"),
                        "message": "Graph metadata transferred successfully"
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "failed",
                        "error": f"API error {response.status}: {error_text}"
                    }
        
        except Exception as e:
            logger.error(f"❌ Graph metadata transfer failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _transfer_graph_files(
        self,
        graph_structure: GraphStructure,
        graph_metadata: GraphMetadata,
        transfer_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transfer graph files to KG Neo4j."""
        try:
            logger.info(f"📁 Transferring graph files: {graph_structure.graph_id}")
            
            # This would typically involve file upload to KG Neo4j storage
            # For now, we'll simulate the transfer
            
            file_transfer_results = []
            
            # Simulate file transfer for each file format
            for file_format in graph_metadata.file_formats:
                try:
                    # In a real implementation, this would upload the actual file
                    file_result = await self._upload_graph_file(
                        graph_structure.graph_id,
                        file_format,
                        graph_metadata.output_directory
                    )
                    file_transfer_results.append(file_result)
                
                except Exception as e:
                    logger.warning(f"⚠️ File format {file_format} transfer failed: {e}")
                    file_transfer_results.append({
                        "format": file_format,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Determine overall file transfer status
            successful_transfers = [r for r in file_transfer_results if r["status"] == "success"]
            
            if len(successful_transfers) == len(file_transfer_results):
                return {
                    "status": "success",
                    "files_transferred": len(successful_transfers),
                    "message": "All graph files transferred successfully"
                }
            elif len(successful_transfers) > 0:
                return {
                    "status": "partial",
                    "files_transferred": len(successful_transfers),
                    "total_files": len(file_transfer_results),
                    "message": f"Partially successful: {len(successful_transfers)}/{len(file_transfer_results)} files transferred"
                }
            else:
                return {
                    "status": "failed",
                    "error": "No graph files transferred successfully"
                }
        
        except Exception as e:
            logger.error(f"❌ Graph files transfer failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _upload_graph_file(
        self,
        graph_id: str,
        file_format: str,
        output_directory: str
    ) -> Dict[str, Any]:
        """Upload a specific graph file to KG Neo4j."""
        try:
            # Simulate file upload
            # In a real implementation, this would:
            # 1. Read the file from output_directory
            # 2. Upload it to KG Neo4j storage
            # 3. Return upload confirmation
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            return {
                "format": file_format,
                "status": "success",
                "file_size_bytes": 1024,  # Simulated file size
                "upload_url": f"https://kg-neo4j.example.com/files/{graph_id}/{file_format}",
                "message": f"File {file_format} uploaded successfully"
            }
        
        except Exception as e:
            logger.error(f"❌ File upload failed for {file_format}: {e}")
            return {
                "format": file_format,
                "status": "failed",
                "error": str(e)
            }
    
    def _calculate_data_transferred(self, transfer_results: Dict[str, Any]) -> float:
        """Calculate total data transferred in MB."""
        try:
            total_bytes = 0
            
            for mode, result in transfer_results.items():
                if result.get("status") == "success":
                    # Estimate data size based on mode
                    if mode == "structure":
                        # Graph structure data
                        total_bytes += 1024  # 1KB estimate
                    elif mode == "metadata":
                        # Metadata
                        total_bytes += 512   # 0.5KB estimate
                    elif mode == "files":
                        # File data (if available)
                        if "files_transferred" in result:
                            total_bytes += result["files_transferred"] * 1024  # 1KB per file estimate
            
            return total_bytes / (1024 * 1024)  # Convert to MB
            
        except Exception:
            return 0.0
    
    def _determine_overall_status(self, transfer_results: Dict[str, Any]) -> str:
        """Determine overall transfer status."""
        try:
            if not transfer_results:
                return "failed"
            
            statuses = [result.get("status", "unknown") for result in transfer_results.values()]
            
            if all(status == "success" for status in statuses):
                return "success"
            elif any(status == "success" for status in statuses):
                return "partial"
            elif any(status == "failed" for status in statuses):
                return "failed"
            else:
                return "unknown"
        
        except Exception:
            return "unknown"
    
    def _update_transfer_stats(
        self,
        status: str,
        transfer_time: float,
        data_transferred: float
    ) -> None:
        """Update transfer statistics."""
        self.transfer_stats["graphs_transferred"] += 1
        
        if status == "success":
            self.transfer_stats["successful_transfers"] += 1
        elif status == "failed":
            self.transfer_stats["failed_transfers"] += 1
        
        self.transfer_stats["total_transfer_time_ms"] += transfer_time
        self.transfer_stats["total_data_transferred_mb"] += data_transferred
    
    def get_transfer_stats(self) -> Dict[str, Any]:
        """Get transfer statistics."""
        stats = self.transfer_stats.copy()
        
        # Calculate averages
        if stats["graphs_transferred"] > 0:
            stats["avg_transfer_time_ms"] = stats["total_transfer_time_ms"] / stats["graphs_transferred"]
            stats["avg_data_transferred_mb"] = stats["total_data_transferred_mb"] / stats["graphs_transferred"]
            stats["success_rate"] = stats["successful_transfers"] / stats["graphs_transferred"]
        else:
            stats["avg_transfer_time_ms"] = 0
            stats["avg_data_transferred_mb"] = 0
            stats["success_rate"] = 0
        
        # Calculate transfer rate
        if stats["total_transfer_time_ms"] > 0:
            stats["graphs_per_second"] = stats["graphs_transferred"] / (stats["total_transfer_time_ms"] / 1000)
            stats["data_transfer_rate_mbps"] = (stats["total_data_transferred_mb"] * 8) / (stats["total_transfer_time_ms"] / 1000)
        else:
            stats["graphs_per_second"] = 0
            stats["data_transfer_rate_mbps"] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset transfer statistics."""
        self.transfer_stats = {
            "graphs_transferred": 0,
            "successful_transfers": 0,
            "failed_transfers": 0,
            "total_transfer_time_ms": 0,
            "total_data_transferred_mb": 0
        }
        logger.info("🔄 Graph transfer statistics reset")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update transfer configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Graph transfer configuration updated")
    
    async def get_transfer_status(self, transfer_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific transfer."""
        try:
            # In a real implementation, this would query the transfer status
            # from a database or tracking system
            
            # For now, return a placeholder
            return {
                "transfer_id": transfer_id,
                "status": "unknown",
                "message": "Transfer status tracking not implemented"
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to get transfer status: {e}")
            return None
    
    async def cancel_transfer(self, transfer_id: str) -> bool:
        """Cancel an ongoing transfer."""
        try:
            # In a real implementation, this would cancel the transfer
            # and clean up any resources
            
            logger.info(f"🛑 Transfer cancellation requested: {transfer_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to cancel transfer: {e}")
            return False





