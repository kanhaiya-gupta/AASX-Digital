"""
AI RAG Graph Sync Manager
=========================

Service for synchronizing graphs between AI RAG and KG Neo4j.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import hashlib
import json

from ..graph_models.graph_structure import GraphStructure
from ..graph_models.graph_metadata import GraphMetadata
from .graph_transfer_service import GraphTransferService

logger = logging.getLogger(__name__)


class GraphSyncManager:
    """
    Graph Synchronization Manager for AI RAG and KG Neo4j Integration
    
    Manages synchronization between AI RAG graphs and KG Neo4j,
    including conflict resolution, version management, and consistency checks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the graph sync manager.
        
        Args:
            config: Configuration dictionary for graph synchronization
        """
        self.config = config or self._get_default_config()
        self.sync_stats = {
            "sync_operations": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "conflicts_resolved": 0,
            "graphs_updated": 0,
            "total_sync_time_ms": 0
        }
        
        # Initialize transfer service
        self.transfer_service = GraphTransferService(self.config.get("transfer_config", {}))
        
        # Track sync state
        self.sync_state = {}
        self.conflict_resolution_strategies = self._initialize_conflict_strategies()
        
        logger.info("✅ GraphSyncManager initialized with configuration")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for graph synchronization."""
        return {
            "sync_interval_minutes": 15,
            "enable_auto_sync": True,
            "enable_conflict_detection": True,
            "enable_version_control": True,
            "conflict_resolution_strategy": "ai_rag_wins",  # ai_rag_wins, kg_neo4j_wins, manual, merge
            "sync_modes": ["structure", "metadata", "files"],
            "enable_incremental_sync": True,
            "enable_rollback": True,
            "max_sync_retries": 3,
            "sync_timeout": 600,  # 10 minutes
            "enable_parallel_sync": True,
            "max_concurrent_syncs": 3,
            "enable_sync_validation": True,
            "enable_sync_logging": True,
            "sync_priority": "normal",  # low, normal, high, urgent
            "enable_health_checks": True,
            "health_check_interval": 300,  # 5 minutes
            "transfer_config": {
                "kg_neo4j_api_url": "http://localhost:7474",
                "transfer_timeout": 300,
                "max_retries": 3
            }
        }
    
    async def start_sync_manager(self) -> None:
        """Start the graph sync manager."""
        try:
            logger.info("🚀 Starting Graph Sync Manager")
            
            # Initialize sync state
            await self._initialize_sync_state()
            
            # Start health monitoring if enabled
            if self.config["enable_health_checks"]:
                asyncio.create_task(self._health_monitoring_loop())
            
            # Start auto-sync if enabled
            if self.config["enable_auto_sync"]:
                asyncio.create_task(self._auto_sync_loop())
            
            logger.info("✅ Graph Sync Manager started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Graph Sync Manager: {e}")
            raise
    
    async def stop_sync_manager(self) -> None:
        """Stop the graph sync manager."""
        try:
            logger.info("🛑 Stopping Graph Sync Manager")
            
            # Stop background tasks
            # In a real implementation, this would properly cancel tasks
            
            logger.info("✅ Graph Sync Manager stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop Graph Sync Manager: {e}")
    
    async def sync_graph(
        self,
        graph_id: str,
        sync_mode: Optional[str] = None,
        force_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronize a specific graph between AI RAG and KG Neo4j.
        
        Args:
            graph_id: ID of the graph to synchronize
            sync_mode: Specific sync mode (default: all modes)
            force_sync: Force synchronization even if not needed
            
        Returns:
            Dict: Synchronization results and status
        """
        start_time = datetime.now()
        sync_id = f"sync_{graph_id}_{int(start_time.timestamp())}"
        
        logger.info(f"🔄 Starting graph synchronization: {sync_id} for graph: {graph_id}")
        
        try:
            # Check if sync is needed
            if not force_sync and not await self._is_sync_needed(graph_id):
                return {
                    "sync_id": sync_id,
                    "graph_id": graph_id,
                    "status": "skipped",
                    "reason": "No synchronization needed",
                    "sync_time_ms": 0
                }
            
            # Get graph data from AI RAG
            ai_rag_graph = await self._get_ai_rag_graph(graph_id)
            if not ai_rag_graph:
                return {
                    "sync_id": sync_id,
                    "graph_id": graph_id,
                    "status": "failed",
                    "error": "Graph not found in AI RAG",
                    "sync_time_ms": 0
                }
            
            # Get graph data from KG Neo4j
            kg_neo4j_graph = await self._get_kg_neo4j_graph(graph_id)
            
            # Detect conflicts
            conflicts = []
            if self.config["enable_conflict_detection"] and kg_neo4j_graph:
                conflicts = await self._detect_conflicts(ai_rag_graph, kg_neo4j_graph)
            
            # Resolve conflicts if any
            if conflicts:
                resolution_result = await self._resolve_conflicts(conflicts, ai_rag_graph, kg_neo4j_graph)
                if not resolution_result["resolved"]:
                    return {
                        "sync_id": sync_id,
                        "graph_id": graph_id,
                        "status": "failed",
                        "error": "Conflicts could not be resolved",
                        "conflicts": conflicts,
                        "sync_time_ms": 0
                    }
                
                # Update graph with resolved conflicts
                ai_rag_graph = resolution_result["resolved_graph"]
                self.sync_stats["conflicts_resolved"] += len(conflicts)
            
            # Perform synchronization
            sync_result = await self._perform_sync(ai_rag_graph, kg_neo4j_graph, sync_mode)
            
            # Update sync state
            await self._update_sync_state(graph_id, sync_result)
            
            # Calculate sync metrics
            end_time = datetime.now()
            sync_time = (end_time - start_time).total_seconds() * 1000
            
            # Update sync statistics
            self._update_sync_stats(sync_result["status"], sync_time)
            
            # Finalize sync result
            sync_result.update({
                "sync_id": sync_id,
                "graph_id": graph_id,
                "sync_time_ms": sync_time,
                "conflicts_detected": len(conflicts),
                "conflicts_resolved": len(conflicts) if conflicts else 0
            })
            
            # Log sync completion
            if sync_result["status"] == "success":
                logger.info(f"✅ Graph synchronization completed: {sync_id} in {sync_time:.0f}ms")
            else:
                logger.warning(f"⚠️ Graph synchronization completed with issues: {sync_id} - Status: {sync_result['status']}")
            
            return sync_result
            
        except Exception as e:
            logger.error(f"❌ Graph synchronization failed: {sync_id} - {e}")
            
            # Update sync statistics
            self._update_sync_stats("failed", 0)
            
            return {
                "sync_id": sync_id,
                "graph_id": graph_id,
                "status": "failed",
                "error": str(e),
                "sync_time_ms": 0
            }
    
    async def sync_graphs_batch(
        self,
        graph_ids: List[str],
        sync_mode: Optional[str] = None,
        parallel: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Synchronize multiple graphs in batch.
        
        Args:
            graph_ids: List of graph IDs to synchronize
            sync_mode: Optional sync mode override
            parallel: Optional parallel processing override
            
        Returns:
            List: Synchronization results for all graphs
        """
        parallel = parallel if parallel is not None else self.config["enable_parallel_sync"]
        
        logger.info(f"📦 Starting batch synchronization of {len(graph_ids)} graphs")
        
        try:
            if parallel:
                # Process graphs in parallel with concurrency limit
                semaphore = asyncio.Semaphore(self.config["max_concurrent_syncs"])
                
                async def sync_with_semaphore(graph_id):
                    async with semaphore:
                        return await self.sync_graph(graph_id, sync_mode)
                
                # Create tasks for all graphs
                tasks = [sync_with_semaphore(graph_id) for graph_id in graph_ids]
                
                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle any exceptions
                processed_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Graph {graph_ids[i]} sync failed: {result}")
                        processed_results.append({
                            "sync_id": f"batch_sync_{i}",
                            "graph_id": graph_ids[i],
                            "status": "failed",
                            "error": str(result),
                            "sync_time_ms": 0
                        })
                    else:
                        processed_results.append(result)
                
                return processed_results
            
            else:
                # Process graphs sequentially
                results = []
                for graph_id in graph_ids:
                    try:
                        result = await self.sync_graph(graph_id, sync_mode)
                        results.append(result)
                        
                        # Add small delay between syncs
                        await asyncio.sleep(0.1)
                    
                    except Exception as e:
                        logger.error(f"❌ Graph {graph_id} sync failed: {e}")
                        results.append({
                            "sync_id": f"batch_sync_{graph_id}",
                            "status": "failed",
                            "error": str(e),
                            "sync_time_ms": 0
                        })
                
                return results
        
        except Exception as e:
            logger.error(f"❌ Batch synchronization failed: {e}")
            return []
    
    async def _initialize_sync_state(self) -> None:
        """Initialize synchronization state."""
        try:
            # In a real implementation, this would load sync state from database
            self.sync_state = {}
            logger.info("🔄 Synchronization state initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize sync state: {e}")
    
    async def _health_monitoring_loop(self) -> None:
        """Health monitoring loop for sync manager."""
        while True:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config["health_check_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _auto_sync_loop(self) -> None:
        """Auto-synchronization loop."""
        while True:
            try:
                await self._perform_auto_sync()
                await asyncio.sleep(self.config["sync_interval_minutes"] * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Auto-sync failed: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _perform_health_check(self) -> None:
        """Perform health check of sync manager."""
        try:
            # Check transfer service health
            transfer_health = await self.transfer_service.get_transfer_status("health_check")
            
            # Check sync state health
            sync_health = {
                "sync_state_entries": len(self.sync_state),
                "last_sync_time": max([state.get("last_sync_time", datetime.min) for state in self.sync_state.values()], default=datetime.min),
                "pending_syncs": len([state for state in self.sync_state.values() if state.get("status") == "pending"])
            }
            
            # Log health status
            logger.info(f"🏥 Sync Manager Health Check - Transfer: {transfer_health}, Sync: {sync_health}")
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    async def _perform_auto_sync(self) -> None:
        """Perform automatic synchronization of graphs."""
        try:
            # Get graphs that need synchronization
            graphs_to_sync = await self._get_graphs_needing_sync()
            
            if graphs_to_sync:
                logger.info(f"🔄 Auto-sync: Found {len(graphs_to_sync)} graphs needing synchronization")
                
                # Perform batch sync
                results = await self.sync_graphs_batch(graphs_to_sync, parallel=True)
                
                # Log results
                successful = [r for r in results if r["status"] == "success"]
                failed = [r for r in results if r["status"] == "failed"]
                
                logger.info(f"✅ Auto-sync completed: {len(successful)} successful, {len(failed)} failed")
            else:
                logger.info("✅ Auto-sync: No graphs need synchronization")
        
        except Exception as e:
            logger.error(f"❌ Auto-sync failed: {e}")
    
    async def _is_sync_needed(self, graph_id: str) -> bool:
        """Check if synchronization is needed for a graph."""
        try:
            # Get last sync time
            last_sync = self.sync_state.get(graph_id, {}).get("last_sync_time")
            
            if not last_sync:
                return True  # Never synced
            
            # Check if enough time has passed
            time_since_sync = datetime.now() - last_sync
            return time_since_sync.total_seconds() > (self.config["sync_interval_minutes"] * 60)
            
        except Exception as e:
            logger.error(f"❌ Failed to check sync need: {e}")
            return True  # Default to needing sync
    
    async def _get_ai_rag_graph(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """Get graph data from AI RAG."""
        try:
            # In a real implementation, this would query the AI RAG database
            # For now, return a mock graph structure
            
            return {
                "graph_id": graph_id,
                "graph_name": f"AI_RAG_Graph_{graph_id}",
                "graph_type": "knowledge_graph",
                "nodes": [
                    {
                        "node_id": f"node_{graph_id}_1",
                        "node_type": "entity",
                        "node_label": "Sample Entity",
                        "properties": {"confidence": 0.95},
                        "confidence_score": 0.95
                    }
                ],
                "edges": [
                    {
                        "edge_id": f"edge_{graph_id}_1",
                        "source_node_id": f"node_{graph_id}_1",
                        "target_node_id": f"node_{graph_id}_2",
                        "relationship_type": "RELATES_TO",
                        "properties": {"weight": 1.0},
                        "weight": 1.0,
                        "confidence_score": 0.9
                    }
                ],
                "metadata": {
                    "node_count": 1,
                    "edge_count": 1,
                    "graph_density": 1.0,
                    "overall_quality_score": 0.925
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get AI RAG graph: {e}")
            return None
    
    async def _get_kg_neo4j_graph(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """Get graph data from KG Neo4j."""
        try:
            # In a real implementation, this would query the KG Neo4j API
            # For now, return None (no existing graph)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get KG Neo4j graph: {e}")
            return None
    
    async def _detect_conflicts(
        self,
        ai_rag_graph: Dict[str, Any],
        kg_neo4j_graph: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between AI RAG and KG Neo4j graphs."""
        conflicts = []
        
        try:
            # Check for structural conflicts
            if ai_rag_graph.get("node_count", 0) != kg_neo4j_graph.get("node_count", 0):
                conflicts.append({
                    "type": "structural",
                    "field": "node_count",
                    "ai_rag_value": ai_rag_graph.get("node_count"),
                    "kg_neo4j_value": kg_neo4j_graph.get("node_count"),
                    "severity": "high"
                })
            
            if ai_rag_graph.get("edge_count", 0) != kg_neo4j_graph.get("edge_count", 0):
                conflicts.append({
                    "type": "structural",
                    "field": "edge_count",
                    "ai_rag_value": ai_rag_graph.get("edge_count"),
                    "kg_neo4j_value": kg_neo4j_graph.get("edge_count"),
                    "severity": "high"
                })
            
            # Check for metadata conflicts
            if ai_rag_graph.get("graph_name") != kg_neo4j_graph.get("graph_name"):
                conflicts.append({
                    "type": "metadata",
                    "field": "graph_name",
                    "ai_rag_value": ai_rag_graph.get("graph_name"),
                    "kg_neo4j_value": kg_neo4j_graph.get("graph_name"),
                    "severity": "medium"
                })
            
            # Check for content conflicts (simplified)
            ai_rag_hash = self._calculate_graph_hash(ai_rag_graph)
            kg_neo4j_hash = self._calculate_graph_hash(kg_neo4j_graph)
            
            if ai_rag_hash != kg_neo4j_hash:
                conflicts.append({
                    "type": "content",
                    "field": "graph_content",
                    "ai_rag_value": ai_rag_hash[:8],
                    "kg_neo4j_value": kg_neo4j_hash[:8],
                    "severity": "critical"
                })
            
            logger.info(f"🔍 Detected {len(conflicts)} conflicts between AI RAG and KG Neo4j graphs")
            
        except Exception as e:
            logger.error(f"❌ Conflict detection failed: {e}")
        
        return conflicts
    
    def _calculate_graph_hash(self, graph: Dict[str, Any]) -> str:
        """Calculate hash of graph content for conflict detection."""
        try:
            # Create a simplified representation for hashing
            graph_repr = {
                "nodes": sorted([(n["node_id"], n["node_type"], n["node_label"]) for n in graph.get("nodes", [])]),
                "edges": sorted([(e["source_node_id"], e["target_node_id"], e["relationship_type"]) for e in graph.get("edges", [])])
            }
            
            graph_str = json.dumps(graph_repr, sort_keys=True)
            return hashlib.md5(graph_str.encode()).hexdigest()
            
        except Exception:
            return "unknown"
    
    async def _resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
        ai_rag_graph: Dict[str, Any],
        kg_neo4j_graph: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflicts between graphs."""
        try:
            strategy = self.config["conflict_resolution_strategy"]
            resolved_graph = ai_rag_graph.copy()
            
            logger.info(f"🔧 Resolving {len(conflicts)} conflicts using strategy: {strategy}")
            
            for conflict in conflicts:
                if strategy == "ai_rag_wins":
                    # AI RAG values take precedence
                    resolved_graph = self._apply_ai_rag_value(resolved_graph, conflict)
                
                elif strategy == "kg_neo4j_wins":
                    # KG Neo4j values take precedence
                    resolved_graph = self._apply_kg_neo4j_value(resolved_graph, conflict, kg_neo4j_graph)
                
                elif strategy == "merge":
                    # Merge values intelligently
                    resolved_graph = self._merge_values(resolved_graph, conflict, kg_neo4j_graph)
                
                elif strategy == "manual":
                    # Manual resolution required
                    logger.warning(f"⚠️ Manual conflict resolution required for: {conflict}")
                    continue
            
            return {
                "resolved": True,
                "resolved_graph": resolved_graph,
                "conflicts_resolved": len(conflicts),
                "strategy_used": strategy
            }
            
        except Exception as e:
            logger.error(f"❌ Conflict resolution failed: {e}")
            return {
                "resolved": False,
                "error": str(e)
            }
    
    def _apply_ai_rag_value(
        self,
        graph: Dict[str, Any],
        conflict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply AI RAG value to resolve conflict."""
        # AI RAG values are already in the graph, so no changes needed
        return graph
    
    def _apply_kg_neo4j_value(
        self,
        graph: Dict[str, Any],
        conflict: Dict[str, Any],
        kg_neo4j_graph: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply KG Neo4j value to resolve conflict."""
        try:
            field = conflict["field"]
            kg_value = conflict["kg_neo4j_value"]
            
            if field == "node_count":
                graph["metadata"]["node_count"] = kg_value
            elif field == "edge_count":
                graph["metadata"]["edge_count"] = kg_value
            elif field == "graph_name":
                graph["graph_name"] = kg_value
            
            return graph
            
        except Exception as e:
            logger.error(f"❌ Failed to apply KG Neo4j value: {e}")
            return graph
    
    def _merge_values(
        self,
        graph: Dict[str, Any],
        conflict: Dict[str, Any],
        kg_neo4j_graph: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge values intelligently to resolve conflict."""
        try:
            field = conflict["field"]
            
            if field == "node_count":
                # Take the higher count
                ai_rag_count = graph["metadata"]["node_count"]
                kg_count = conflict["kg_neo4j_value"]
                graph["metadata"]["node_count"] = max(ai_rag_count, kg_count)
            
            elif field == "edge_count":
                # Take the higher count
                ai_rag_count = graph["metadata"]["edge_count"]
                kg_count = conflict["kg_neo4j_value"]
                graph["metadata"]["edge_count"] = max(ai_rag_count, kg_count)
            
            elif field == "graph_name":
                # Prefer AI RAG name but add suffix if different
                ai_rag_name = graph["graph_name"]
                kg_name = conflict["kg_neo4j_value"]
                if ai_rag_name != kg_name:
                    graph["graph_name"] = f"{ai_rag_name}_merged"
            
            return graph
            
        except Exception as e:
            logger.error(f"❌ Failed to merge values: {e}")
            return graph
    
    async def _perform_sync(
        self,
        ai_rag_graph: Dict[str, Any],
        kg_neo4j_graph: Optional[Dict[str, Any]],
        sync_mode: Optional[str]
    ) -> Dict[str, Any]:
        """Perform the actual synchronization."""
        try:
            # Determine sync mode
            modes = [sync_mode] if sync_mode else self.config["sync_modes"]
            
            sync_results = {}
            
            for mode in modes:
                try:
                    if mode == "structure":
                        result = await self._sync_graph_structure(ai_rag_graph, kg_neo4j_graph)
                        sync_results["structure"] = result
                    
                    elif mode == "metadata":
                        result = await self._sync_graph_metadata(ai_rag_graph, kg_neo4j_graph)
                        sync_results["metadata"] = result
                    
                    elif mode == "files":
                        result = await self._sync_graph_files(ai_rag_graph, kg_neo4j_graph)
                        sync_results["files"] = result
                    
                    else:
                        logger.warning(f"⚠️ Unknown sync mode: {mode}")
                        sync_results[mode] = {"status": "skipped", "reason": "Unknown mode"}
                
                except Exception as e:
                    logger.error(f"❌ Sync mode {mode} failed: {e}")
                    sync_results[mode] = {"status": "failed", "error": str(e)}
            
            # Determine overall sync status
            overall_status = self._determine_overall_sync_status(sync_results)
            
            return {
                "status": overall_status,
                "sync_results": sync_results,
                "modes_synced": modes
            }
            
        except Exception as e:
            logger.error(f"❌ Synchronization failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _sync_graph_structure(
        self,
        ai_rag_graph: Dict[str, Any],
        kg_neo4j_graph: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synchronize graph structure."""
        try:
            if not kg_neo4j_graph:
                # Create new graph in KG Neo4j
                result = await self.transfer_service.transfer_graph(
                    GraphStructure(**ai_rag_graph),
                    GraphMetadata(graph_id=ai_rag_graph["graph_id"]),
                    transfer_mode="structure"
                )
                return {
                    "status": "created",
                    "message": "New graph structure created in KG Neo4j",
                    "kg_neo4j_graph_id": result.get("kg_neo4j_graph_id")
                }
            else:
                # Update existing graph
                result = await self.transfer_service.transfer_graph(
                    GraphStructure(**ai_rag_graph),
                    GraphMetadata(graph_id=ai_rag_graph["graph_id"]),
                    transfer_mode="structure"
                )
                return {
                    "status": "updated",
                    "message": "Graph structure updated in KG Neo4j",
                    "kg_neo4j_graph_id": result.get("kg_neo4j_graph_id")
                }
        
        except Exception as e:
            logger.error(f"❌ Graph structure sync failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _sync_graph_metadata(
        self,
        ai_rag_graph: Dict[str, Any],
        kg_neo4j_graph: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synchronize graph metadata."""
        try:
            # Create metadata object
            metadata = GraphMetadata(
                graph_id=ai_rag_graph["graph_id"],
                version="1.0",
                processing_status="completed",
                quality_score=ai_rag_graph["metadata"]["overall_quality_score"]
            )
            
            result = await self.transfer_service.transfer_graph(
                GraphStructure(**ai_rag_graph),
                metadata,
                transfer_mode="metadata"
            )
            
            return {
                "status": "synced",
                "message": "Graph metadata synchronized",
                "kg_neo4j_metadata_id": result.get("kg_neo4j_metadata_id")
            }
        
        except Exception as e:
            logger.error(f"❌ Graph metadata sync failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _sync_graph_files(
        self,
        ai_rag_graph: Dict[str, Any],
        kg_neo4j_graph: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synchronize graph files."""
        try:
            # Create metadata with file information
            metadata = GraphMetadata(
                graph_id=ai_rag_graph["graph_id"],
                file_formats=["cypher", "graphml", "jsonld"],
                output_directory=f"output/graphs/ai_rag/{ai_rag_graph['graph_id']}"
            )
            
            result = await self.transfer_service.transfer_graph(
                GraphStructure(**ai_rag_graph),
                metadata,
                transfer_mode="files"
            )
            
            return {
                "status": "synced",
                "message": "Graph files synchronized",
                "files_transferred": result.get("files_transferred", 0)
            }
        
        except Exception as e:
            logger.error(f"❌ Graph files sync failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _determine_overall_sync_status(self, sync_results: Dict[str, Any]) -> str:
        """Determine overall synchronization status."""
        try:
            if not sync_results:
                return "failed"
            
            statuses = [result.get("status", "unknown") for result in sync_results.values()]
            
            if all(status in ["created", "updated", "synced"] for status in statuses):
                return "success"
            elif any(status in ["created", "updated", "synced"] for status in statuses):
                return "partial"
            elif any(status == "failed" for status in statuses):
                return "failed"
            else:
                return "unknown"
        
        except Exception:
            return "unknown"
    
    async def _update_sync_state(self, graph_id: str, sync_result: Dict[str, Any]) -> None:
        """Update synchronization state for a graph."""
        try:
            self.sync_state[graph_id] = {
                "last_sync_time": datetime.now(),
                "status": sync_result["status"],
                "sync_id": sync_result.get("sync_id"),
                "modes_synced": sync_result.get("modes_synced", []),
                "last_sync_result": sync_result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update sync state: {e}")
    
    async def _get_graphs_needing_sync(self) -> List[str]:
        """Get list of graphs that need synchronization."""
        try:
            # In a real implementation, this would query the database
            # For now, return an empty list
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get graphs needing sync: {e}")
            return []
    
    def _update_sync_stats(self, status: str, sync_time: float) -> None:
        """Update synchronization statistics."""
        self.sync_stats["sync_operations"] += 1
        
        if status == "success":
            self.sync_stats["successful_syncs"] += 1
        elif status == "failed":
            self.sync_stats["failed_syncs"] += 1
        
        self.sync_stats["total_sync_time_ms"] += sync_time
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics."""
        stats = self.sync_stats.copy()
        
        # Calculate averages
        if stats["sync_operations"] > 0:
            stats["avg_sync_time_ms"] = stats["total_sync_time_ms"] / stats["sync_operations"]
            stats["success_rate"] = stats["successful_syncs"] / stats["sync_operations"]
        else:
            stats["avg_sync_time_ms"] = 0
            stats["success_rate"] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset synchronization statistics."""
        self.sync_stats = {
            "sync_operations": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "conflicts_resolved": 0,
            "graphs_updated": 0,
            "total_sync_time_ms": 0
        }
        logger.info("🔄 Synchronization statistics reset")
    
    def _initialize_conflict_strategies(self) -> Dict[str, Any]:
        """Initialize conflict resolution strategies."""
        return {
            "ai_rag_wins": "AI RAG values take precedence",
            "kg_neo4j_wins": "KG Neo4j values take precedence",
            "merge": "Intelligently merge values",
            "manual": "Require manual resolution"
        }
    
    def get_conflict_strategies(self) -> Dict[str, str]:
        """Get available conflict resolution strategies."""
        return self.conflict_resolution_strategies.copy()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update synchronization configuration."""
        self.config.update(new_config)
        logger.info("⚙️ Synchronization configuration updated")

