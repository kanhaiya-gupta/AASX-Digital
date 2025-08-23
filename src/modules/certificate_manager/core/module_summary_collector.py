"""
Module Summary Collector - Module Data Collection Service

Handles collection, aggregation, and summary generation of data
from all modules. Collects real-time data from various modules,
aggregates it into meaningful summaries, and provides insights
for certificate generation and validation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from ..models.certificates_registry import (
    CertificateRegistry,
    ModuleStatus,
    QualityLevel
)
from ..models.certificates_metrics import CertificateMetrics, MetricCategory
from ..services.certificates_registry_service import CertificatesRegistryService
from ..services.certificates_metrics_service import CertificatesMetricsService

logger = logging.getLogger(__name__)


class CollectionStatus(str, Enum):
    """Module data collection status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class DataSource(str, Enum):
    """Data source types"""
    AASX_MODULE = "aasx_module"
    TWIN_REGISTRY = "twin_registry"
    AI_RAG = "ai_rag"
    KG_NEO4J = "kg_neo4j"
    PHYSICS_MODELING = "physics_modeling"
    FEDERATED_LEARNING = "federated_learning"
    DATA_GOVERNANCE = "data_governance"


class ModuleSummaryCollector:
    """
    Module data collection and summary service
    
    Handles:
    - Real-time data collection from modules
    - Data aggregation and summarization
    - Quality assessment and validation
    - Progress tracking and completion monitoring
    - Data freshness and consistency checks
    - Summary generation for certificates
    """
    
    def __init__(
        self,
        registry_service: CertificatesRegistryService,
        metrics_service: CertificatesMetricsService
    ):
        """Initialize the module summary collector"""
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        
        # Collection status tracking
        self.collection_status: Dict[str, CollectionStatus] = {}
        
        # Data collection locks per certificate
        self.collection_locks: Dict[str, asyncio.Lock] = {}
        
        # Collection history
        self.collection_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Data freshness thresholds (in minutes)
        self.freshness_thresholds = {
            DataSource.AASX_MODULE: 30,
            DataSource.TWIN_REGISTRY: 60,
            DataSource.AI_RAG: 45,
            DataSource.KG_NEO4J: 90,
            DataSource.PHYSICS_MODELING: 120,
            DataSource.FEDERATED_LEARNING: 180,
            DataSource.DATA_GOVERNANCE: 60
        }
        
        logger.info("Module Summary Collector initialized successfully")
    
    async def start_data_collection(
        self,
        certificate_id: str,
        force_refresh: bool = False
    ) -> bool:
        """
        Start data collection for a certificate
        
        This is the main entry point for module data collection.
        Initiates collection from all modules and tracks progress.
        """
        try:
            # Acquire collection lock for this certificate
            if certificate_id not in self.collection_locks:
                self.collection_locks[certificate_id] = asyncio.Lock()
            
            async with self.collection_locks[certificate_id]:
                logger.info(f"Starting data collection for certificate: {certificate_id}")
                
                # Check if collection is already in progress
                if (certificate_id in self.collection_status and 
                    self.collection_status[certificate_id] == CollectionStatus.IN_PROGRESS and
                    not force_refresh):
                    logger.info(f"Data collection already in progress for certificate: {certificate_id}")
                    return True
                
                # Initialize collection status
                self.collection_status[certificate_id] = CollectionStatus.IN_PROGRESS
                
                # Start collection tasks for all modules
                collection_tasks = []
                for data_source in DataSource:
                    task = asyncio.create_task(
                        self._collect_module_data(certificate_id, data_source)
                    )
                    collection_tasks.append(task)
                
                # Wait for all collection tasks to complete
                results = await asyncio.gather(*collection_tasks, return_exceptions=True)
                
                # Analyze collection results
                successful_collections = sum(1 for r in results if not isinstance(r, Exception))
                total_modules = len(DataSource)
                
                # Determine final collection status
                if successful_collections == total_modules:
                    self.collection_status[certificate_id] = CollectionStatus.COMPLETED
                elif successful_collections > 0:
                    self.collection_status[certificate_id] = CollectionStatus.PARTIAL
                else:
                    self.collection_status[certificate_id] = CollectionStatus.FAILED
                
                # Generate summary
                summary = await self._generate_module_summary(certificate_id)
                
                # Update certificate with summary
                if summary:
                    await self._update_certificate_summary(certificate_id, summary)
                
                # Record collection history
                await self._record_collection_history(certificate_id, results, summary)
                
                logger.info(f"Data collection completed for certificate: {certificate_id} - Status: {self.collection_status[certificate_id].value}")
                return True
                
        except Exception as e:
            logger.error(f"Error starting data collection: {e}")
            self.collection_status[certificate_id] = CollectionStatus.FAILED
            return False
    
    async def _collect_module_data(
        self,
        certificate_id: str,
        data_source: DataSource
    ) -> Dict[str, Any]:
        """Collect data from a specific module"""
        try:
            logger.info(f"Collecting data from {data_source.value} for certificate: {certificate_id}")
            
            # Simulate data collection from module
            # In a real implementation, this would connect to the actual module
            module_data = await self._simulate_module_data_collection(data_source, certificate_id)
            
            # Validate collected data
            if not await self._validate_module_data(module_data):
                raise ValueError(f"Invalid data collected from {data_source.value}")
            
            # Store module data
            await self._store_module_data(certificate_id, data_source, module_data)
            
            # Update collection metrics
            await self._update_collection_metrics(certificate_id, data_source, module_data)
            
            logger.info(f"Successfully collected data from {data_source.value} for certificate: {certificate_id}")
            return module_data
            
        except Exception as e:
            logger.error(f"Error collecting data from {data_source.value}: {e}")
            raise
    
    async def _simulate_module_data_collection(
        self,
        data_source: DataSource,
        certificate_id: str
    ) -> Dict[str, Any]:
        """Simulate data collection from a module"""
        try:
            # Simulate different data structures for different modules
            if data_source == DataSource.AASX_MODULE:
                return {
                    "module_name": "AASX Module",
                    "data_type": "aasx_files",
                    "file_count": 15,
                    "total_size_mb": 245.7,
                    "processing_status": "completed",
                    "quality_score": 92.5,
                    "last_updated": datetime.utcnow().isoformat(),
                    "metadata": {
                        "file_types": [".aasx", ".xml", ".json"],
                        "validation_status": "validated",
                        "compliance_score": 95.0
                    }
                }
            elif data_source == DataSource.TWIN_REGISTRY:
                return {
                    "module_name": "Twin Registry",
                    "data_type": "digital_twins",
                    "twin_count": 8,
                    "active_twins": 7,
                    "registry_status": "active",
                    "quality_score": 88.3,
                    "last_updated": datetime.utcnow().isoformat(),
                    "metadata": {
                        "twin_types": ["asset", "process", "system"],
                        "sync_status": "synchronized",
                        "version_control": "enabled"
                    }
                }
            elif data_source == DataSource.AI_RAG:
                return {
                    "module_name": "AI RAG",
                    "data_type": "knowledge_base",
                    "document_count": 1250,
                    "indexed_terms": 8750,
                    "rag_status": "active",
                    "quality_score": 94.2,
                    "last_updated": datetime.utcnow().isoformat(),
                    "metadata": {
                        "embedding_model": "text-embedding-ada-002",
                        "chunk_size": 512,
                        "similarity_threshold": 0.85
                    }
                }
            elif data_source == DataSource.KG_NEO4J:
                return {
                    "module_name": "KG Neo4j",
                    "data_type": "knowledge_graph",
                    "node_count": 15420,
                    "relationship_count": 28750,
                    "graph_status": "active",
                    "quality_score": 91.8,
                    "last_updated": datetime.utcnow().isoformat(),
                    "metadata": {
                        "graph_algorithms": ["pagerank", "community_detection"],
                        "indexing_status": "indexed",
                        "query_performance": "optimized"
                    }
                }
            elif data_source == DataSource.PHYSICS_MODELING:
                return {
                    "module_name": "Physics Modeling",
                    "data_type": "simulation_models",
                    "model_count": 12,
                    "simulation_runs": 156,
                    "modeling_status": "active",
                    "quality_score": 89.7,
                    "last_updated": datetime.utcnow().isoformat(),
                    "metadata": {
                        "model_types": ["finite_element", "computational_fluid_dynamics"],
                        "validation_status": "validated",
                        "accuracy_score": 87.5
                    }
                }
            elif data_source == DataSource.FEDERATED_LEARNING:
                return {
                    "module_name": "Federated Learning",
                    "data_type": "ml_models",
                    "participant_count": 6,
                    "model_versions": 8,
                    "learning_status": "active",
                    "quality_score": 86.4,
                    "last_updated": datetime.utcnow().isoformat(),
                    "metadata": {
                        "algorithm": "federated_averaging",
                        "privacy_level": "high",
                        "convergence_status": "converged"
                    }
                }
            elif data_source == DataSource.DATA_GOVERNANCE:
                return {
                    "module_name": "Data Governance",
                    "data_type": "governance_rules",
                    "rule_count": 45,
                    "compliance_score": 93.1,
                    "governance_status": "active",
                    "quality_score": 90.2,
                    "last_updated": datetime.utcnow().isoformat(),
                    "metadata": {
                        "policy_types": ["data_quality", "access_control", "retention"],
                        "audit_status": "audited",
                        "enforcement_level": "strict"
                    }
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error simulating module data collection: {e}")
            return {}
    
    async def _validate_module_data(self, module_data: Dict[str, Any]) -> bool:
        """Validate collected module data"""
        try:
            required_fields = ["module_name", "data_type", "quality_score", "last_updated"]
            
            # Check required fields
            for field in required_fields:
                if field not in module_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate quality score
            quality_score = module_data.get("quality_score", 0)
            if not isinstance(quality_score, (int, float)) or quality_score < 0 or quality_score > 100:
                logger.error(f"Invalid quality score: {quality_score}")
                return False
            
            # Validate timestamp
            try:
                datetime.fromisoformat(module_data["last_updated"])
            except ValueError:
                logger.error(f"Invalid timestamp format: {module_data['last_updated']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating module data: {e}")
            return False
    
    async def _store_module_data(
        self,
        certificate_id: str,
        data_source: DataSource,
        module_data: Dict[str, Any]
    ) -> None:
        """Store collected module data"""
        try:
            # Store in metrics service
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.QUALITY,
                metric_name=f"{data_source.value}_quality_score",
                metric_value=module_data["quality_score"],
                metric_unit="percentage",
                additional_data=module_data
            )
            
            # Store collection timestamp
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.PERFORMANCE,
                metric_name=f"{data_source.value}_last_collection",
                metric_value=1.0,
                metric_unit="timestamp",
                additional_data={"collection_time": module_data["last_updated"]}
            )
            
        except Exception as e:
            logger.error(f"Error storing module data: {e}")
    
    async def _update_collection_metrics(
        self,
        certificate_id: str,
        data_source: DataSource,
        module_data: Dict[str, Any]
    ) -> None:
        """Update collection metrics"""
        try:
            # Update collection success metric
            await self.metrics_service.create_metrics(
                certificate_id=certificate_id,
                metric_category=MetricCategory.PERFORMANCE,
                metric_name=f"{data_source.value}_collection_success",
                metric_value=1.0,
                metric_unit="count",
                additional_data={
                    "module_name": module_data["module_name"],
                    "data_type": module_data["data_type"],
                    "collection_time": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating collection metrics: {e}")
    
    async def _generate_module_summary(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """Generate comprehensive module summary"""
        try:
            # Get all module metrics for this certificate
            metrics = await self.metrics_service.get_certificate_metrics(
                certificate_id, limit=100
            )
            
            # Group metrics by module
            module_summaries = {}
            overall_quality_score = 0.0
            total_modules = 0
            
            for data_source in DataSource:
                module_metrics = [
                    m for m in metrics 
                    if m.metric_name == f"{data_source.value}_quality_score"
                ]
                
                if module_metrics:
                    latest_metric = max(module_metrics, key=lambda m: m.recorded_at)
                    quality_score = latest_metric.metric_value
                    
                    module_summaries[data_source.value] = {
                        "quality_score": quality_score,
                        "last_updated": latest_metric.recorded_at.isoformat(),
                        "status": "active" if quality_score >= 80.0 else "degraded",
                        "data_freshness": await self._calculate_data_freshness(
                            latest_metric.recorded_at, data_source
                        )
                    }
                    
                    overall_quality_score += quality_score
                    total_modules += 1
            
            if total_modules > 0:
                overall_quality_score /= total_modules
            
            summary = {
                "certificate_id": certificate_id,
                "generated_at": datetime.utcnow().isoformat(),
                "overall_quality_score": round(overall_quality_score, 2),
                "total_modules": total_modules,
                "active_modules": sum(1 for m in module_summaries.values() if m["status"] == "active"),
                "degraded_modules": sum(1 for m in module_summaries.values() if m["status"] == "degraded"),
                "module_summaries": module_summaries,
                "data_freshness_overview": await self._generate_freshness_overview(module_summaries),
                "quality_trends": await self._generate_quality_trends(certificate_id, metrics)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating module summary: {e}")
            return None
    
    async def _calculate_data_freshness(
        self,
        last_updated: datetime,
        data_source: DataSource
    ) -> str:
        """Calculate data freshness for a module"""
        try:
            threshold_minutes = self.freshness_thresholds.get(data_source, 60)
            time_diff = datetime.utcnow() - last_updated
            minutes_diff = time_diff.total_seconds() / 60
            
            if minutes_diff <= threshold_minutes:
                return "fresh"
            elif minutes_diff <= threshold_minutes * 2:
                return "stale"
            else:
                return "outdated"
                
        except Exception as e:
            logger.error(f"Error calculating data freshness: {e}")
            return "unknown"
    
    async def _generate_freshness_overview(self, module_summaries: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data freshness overview"""
        try:
            freshness_counts = {"fresh": 0, "stale": 0, "outdated": 0, "unknown": 0}
            
            for module_summary in module_summaries.values():
                freshness = module_summary.get("data_freshness", "unknown")
                freshness_counts[freshness] += 1
            
            return {
                "overview": freshness_counts,
                "freshness_score": self._calculate_freshness_score(freshness_counts),
                "recommendations": self._generate_freshness_recommendations(freshness_counts)
            }
            
        except Exception as e:
            logger.error(f"Error generating freshness overview: {e}")
            return {}
    
    def _calculate_freshness_score(self, freshness_counts: Dict[str, int]) -> float:
        """Calculate overall freshness score"""
        try:
            total = sum(freshness_counts.values())
            if total == 0:
                return 0.0
            
            # Weight fresh data higher
            score = (
                freshness_counts["fresh"] * 1.0 +
                freshness_counts["stale"] * 0.6 +
                freshness_counts["outdated"] * 0.2
            ) / total
            
            return round(score * 100, 2)
            
        except Exception as e:
            logger.error(f"Error calculating freshness score: {e}")
            return 0.0
    
    def _generate_freshness_recommendations(self, freshness_counts: Dict[str, int]) -> List[str]:
        """Generate recommendations based on freshness data"""
        try:
            recommendations = []
            
            if freshness_counts["outdated"] > 0:
                recommendations.append("Some modules have outdated data and require immediate attention")
            
            if freshness_counts["stale"] > 2:
                recommendations.append("Multiple modules have stale data - consider scheduling refresh")
            
            if freshness_counts["fresh"] < 3:
                recommendations.append("Most modules need data refresh to maintain optimal performance")
            
            if not recommendations:
                recommendations.append("All modules have fresh data - system is operating optimally")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating freshness recommendations: {e}")
            return ["Unable to generate recommendations"]
    
    async def _generate_quality_trends(
        self,
        certificate_id: str,
        metrics: List[CertificateMetrics]
    ) -> Dict[str, Any]:
        """Generate quality trends analysis"""
        try:
            trends = {}
            
            for data_source in DataSource:
                quality_metrics = [
                    m for m in metrics 
                    if m.metric_name == f"{data_source.value}_quality_score"
                ]
                
                if len(quality_metrics) >= 2:
                    # Sort by timestamp
                    sorted_metrics = sorted(quality_metrics, key=lambda m: m.recorded_at)
                    
                    # Calculate trend
                    first_score = sorted_metrics[0].metric_value
                    last_score = sorted_metrics[-1].metric_value
                    score_change = last_score - first_score
                    
                    if score_change > 5:
                        trend = "improving"
                    elif score_change < -5:
                        trend = "declining"
                    else:
                        trend = "stable"
                    
                    trends[data_source.value] = {
                        "trend": trend,
                        "score_change": round(score_change, 2),
                        "first_score": first_score,
                        "last_score": last_score,
                        "data_points": len(quality_metrics)
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error generating quality trends: {e}")
            return {}
    
    async def _update_certificate_summary(
        self,
        certificate_id: str,
        summary: Dict[str, Any]
    ) -> None:
        """Update certificate with module summary"""
        try:
            # Update module summaries in certificate
            await self.registry_service.add_module_summary(
                certificate_id,
                {
                    "summary_data": summary,
                    "generated_at": summary["generated_at"],
                    "overall_quality_score": summary["overall_quality_score"],
                    "module_count": summary["total_modules"]
                }
            )
            
            # Update quality assessment
            await self.registry_service.update_quality_assessment(
                certificate_id,
                {
                    "overall_quality_score": summary["overall_quality_score"],
                    "data_completeness_score": summary["total_modules"] / len(DataSource) * 100,
                    "last_assessment": datetime.utcnow()
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating certificate summary: {e}")
    
    async def _record_collection_history(
        self,
        certificate_id: str,
        results: List[Any],
        summary: Optional[Dict[str, Any]]
    ) -> None:
        """Record collection history"""
        try:
            if certificate_id not in self.collection_history:
                self.collection_history[certificate_id] = []
            
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": self.collection_status[certificate_id].value,
                "results_count": len(results),
                "successful_collections": sum(1 for r in results if not isinstance(r, Exception)),
                "failed_collections": sum(1 for r in results if isinstance(r, Exception)),
                "summary_generated": summary is not None,
                "overall_quality_score": summary["overall_quality_score"] if summary else None
            }
            
            self.collection_history[certificate_id].append(history_entry)
            
            # Keep only last 10 entries
            if len(self.collection_history[certificate_id]) > 10:
                self.collection_history[certificate_id] = self.collection_history[certificate_id][-10:]
                
        except Exception as e:
            logger.error(f"Error recording collection history: {e}")
    
    async def get_collection_status(self, certificate_id: str) -> Optional[CollectionStatus]:
        """Get collection status for a certificate"""
        try:
            return self.collection_status.get(certificate_id)
        except Exception as e:
            logger.error(f"Error getting collection status: {e}")
            return None
    
    async def get_collection_history(self, certificate_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get collection history for a certificate"""
        try:
            return self.collection_history.get(certificate_id, [])[-limit:]
        except Exception as e:
            logger.error(f"Error getting collection history: {e}")
            return []
    
    async def get_data_freshness(self, certificate_id: str) -> Dict[str, Any]:
        """Get data freshness overview for a certificate"""
        try:
            # Get latest summary
            certificate = await self.registry_service.get_certificate(certificate_id)
            if not certificate or not certificate.module_summaries.summaries:
                return {}
            
            latest_summary = certificate.module_summaries.summaries[-1]
            return latest_summary.get("data_freshness_overview", {})
            
        except Exception as e:
            logger.error(f"Error getting data freshness: {e}")
            return {}
    
    async def force_data_refresh(self, certificate_id: str, module_name: Optional[str] = None) -> bool:
        """Force data refresh for a certificate or specific module"""
        try:
            if module_name:
                # Refresh specific module
                data_source = DataSource(module_name)
                await self._collect_module_data(certificate_id, data_source)
                logger.info(f"Forced refresh for module {module_name} in certificate {certificate_id}")
            else:
                # Refresh all modules
                await self.start_data_collection(certificate_id, force_refresh=True)
                logger.info(f"Forced refresh for all modules in certificate {certificate_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error forcing data refresh: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the module summary collector"""
        try:
            health_status = {
                "status": "healthy",
                "active_collections": sum(1 for s in self.collection_status.values() if s == CollectionStatus.IN_PROGRESS),
                "completed_collections": sum(1 for s in self.collection_status.values() if s == CollectionStatus.COMPLETED),
                "failed_collections": sum(1 for s in self.collection_status.values() if s == CollectionStatus.FAILED),
                "active_locks": len(self.collection_locks),
                "collection_history_size": sum(len(h) for h in self.collection_history.values()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
