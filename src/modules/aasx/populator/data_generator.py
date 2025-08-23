"""
Data Generation Utilities

Utilities for generating sample and test data for AASX processing operations.
"""

import json
import uuid
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AASXDataGenerator:
    """Generator for AASX-related test data."""
    
    def __init__(self):
        """Initialize data generator."""
        self.sample_aas_models = [
            "AssetAdministrationShell",
            "Submodel",
            "ConceptDescription",
            "Asset",
            "SubmodelElementCollection",
            "Property",
            "MultiLanguageProperty",
            "Range",
            "ReferenceElement",
            "Blob",
            "File",
            "AnnotatedRelationshipElement",
            "RelationshipElement",
            "Capability",
            "Entity",
            "BasicEventElement",
            "Operation",
            "OperationVariable",
            "Constraint",
            "Formula",
            "Qualifier"
        ]
        
        self.sample_identifiers = [
            "https://example.com/aas/1/1",
            "https://example.com/aas/1/2",
            "https://example.com/aas/2/1",
            "https://example.com/aas/2/2",
            "https://example.com/aas/3/1",
            "https://example.com/aas/3/2",
            "https://example.com/aas/4/1",
            "https://example.com/aas/4/2"
        ]
        
        self.sample_descriptions = [
            "Sample AAS model for testing purposes",
            "Generated test data for validation",
            "Example AAS structure for demonstration",
            "Test asset administration shell",
            "Sample submodel for testing",
            "Generated concept description",
            "Example property for testing",
            "Test multi-language property",
            "Sample range element",
            "Generated reference element"
        ]
    
    def generate_aasx_processing_job(self, **overrides) -> Dict[str, Any]:
        """
        Generate a sample AASX processing job.
        
        Args:
            **overrides: Override default values
            
        Returns:
            Dict[str, Any]: Sample processing job data
        """
        base_data = {
            "job_id": str(uuid.uuid4()),
            "file_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "job_type": random.choice(["extract", "generate", "validate", "convert"]),
            "status": random.choice(["pending", "processing", "completed", "failed"]),
            "priority": random.choice(["low", "normal", "high", "critical"]),
            "processed_by": f"user_{random.randint(1, 100)}",
            "org_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "processing_time_seconds": None,
            "file_size_bytes": random.randint(1024, 100 * 1024 * 1024),  # 1KB to 100MB
            "output_format": random.choice(["json", "xml", "yaml", "ttl"]),
            "validation_enabled": random.choice([True, False]),
            "quality_score": random.uniform(0.0, 1.0) if random.choice([True, False]) else None,
            "metadata": {
                "source_system": random.choice(["upload", "api", "scheduled", "manual"]),
                "processing_version": "2.0.0",
                "tags": random.sample(["test", "sample", "generated", "demo"], random.randint(1, 3))
            }
        }
        
        # Add processing time if completed
        if base_data["status"] in ["completed", "failed"]:
            base_data["started_at"] = (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat()
            base_data["completed_at"] = datetime.now().isoformat()
            base_data["processing_time_seconds"] = random.randint(10, 3600)
            
            if base_data["status"] == "failed":
                base_data["error_message"] = random.choice([
                    "File format not supported",
                    "Processing timeout",
                    "Invalid AAS structure",
                    "Memory limit exceeded",
                    "External processor error"
                ])
        
        # Apply overrides
        base_data.update(overrides)
        
        return base_data
    
    def generate_aasx_processing_metrics(self, job_id: str, **overrides) -> Dict[str, Any]:
        """
        Generate sample AASX processing metrics.
        
        Args:
            job_id: Job identifier
            **overrides: Override default values
            
        Returns:
            Dict[str, Any]: Sample metrics data
        """
        base_data = {
            "metric_id": random.randint(1000, 9999),
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": random.uniform(1.0, 3600.0),
            "memory_usage_mb": random.uniform(10.0, 2048.0),
            "cpu_usage_percent": random.uniform(5.0, 95.0),
            "file_size_mb": random.uniform(0.1, 100.0),
            "quality_score": random.uniform(0.0, 1.0),
            "accuracy_score": random.uniform(0.0, 1.0),
            "completeness_score": random.uniform(0.0, 1.0),
            "consistency_score": random.uniform(0.0, 1.0),
            "health_score": random.randint(50, 100),
            "error_count": random.randint(0, 10),
            "warning_count": random.randint(0, 20),
            "info_count": random.randint(0, 50),
            "validation_errors": random.randint(0, 5),
            "processing_steps": random.randint(5, 25),
            "external_calls": random.randint(0, 10),
            "cache_hits": random.randint(0, 100),
            "cache_misses": random.randint(0, 50),
            "network_latency_ms": random.uniform(1.0, 1000.0),
            "disk_io_mb_s": random.uniform(0.1, 100.0),
            "concurrent_jobs": random.randint(1, 10),
            "queue_length": random.randint(0, 20),
            "system_load": random.uniform(0.1, 10.0),
            "available_memory_mb": random.uniform(100.0, 8192.0),
            "disk_space_gb": random.uniform(1.0, 1000.0),
            "network_bandwidth_mbps": random.uniform(10.0, 1000.0),
            "temperature_celsius": random.uniform(20.0, 80.0),
            "power_consumption_watts": random.uniform(50.0, 500.0),
            "uptime_hours": random.uniform(1.0, 8760.0),  # Up to 1 year
            "last_maintenance": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "maintenance_schedule": random.choice(["daily", "weekly", "monthly", "quarterly", "yearly"]),
            "backup_status": random.choice(["success", "failed", "pending", "in_progress"]),
            "security_scan_status": random.choice(["clean", "warnings", "critical", "pending"]),
            "compliance_status": random.choice(["compliant", "non_compliant", "pending_review", "under_investigation"]),
            "performance_trend": random.choice(["improving", "stable", "declining", "fluctuating"]),
            "anomaly_detected": random.choice([True, False]),
            "recommendations": random.sample([
                "Consider increasing memory allocation",
                "Optimize processing algorithms",
                "Implement caching strategies",
                "Review error handling procedures",
                "Monitor system resources more closely"
            ], random.randint(0, 3))
        }
        
        # Apply overrides
        base_data.update(overrides)
        
        return base_data
    
    def generate_sample_aasx_file(self, file_path: str, **overrides) -> Dict[str, Any]:
        """
        Generate a sample AASX file structure.
        
        Args:
            file_path: Path to save the sample file
            **overrides: Override default values
            
        Returns:
            Dict[str, Any]: Sample AASX file data
        """
        sample_data = {
            "format": "aasx",
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "origin": {
                "aasx:origin": {
                    "@attributes": {
                        "xmlns:aasx": "http://www.admin-shell.io/aasx/1.0"
                    },
                    "aasx:origin": {
                        "aasx:first": "aas/aasx-origin.xml",
                        "aasx:last": "aas/aasx-origin.xml"
                    }
                }
            },
            "aas_content": {
                "aas/assetAdministrationShell.xml": {
                    "assetAdministrationShell": {
                        "@attributes": {
                            "xmlns:aas": "http://www.admin-shell.io/aas/3.0"
                        },
                        "id": random.choice(self.sample_identifiers),
                        "idShort": f"SampleAAS_{random.randint(1, 1000)}",
                        "modelType": "AssetAdministrationShell",
                        "description": [
                            {
                                "language": "en",
                                "text": random.choice(self.sample_descriptions)
                            }
                        ],
                        "asset": {
                            "kind": random.choice(["Instance", "Type"]),
                            "id": random.choice(self.sample_identifiers)
                        },
                        "submodels": [
                            {
                                "order": 1,
                                "semanticId": {
                                    "keys": [
                                        {
                                            "type": "GlobalReference",
                                            "value": random.choice(self.sample_identifiers)
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                },
                "aas/submodel.xml": {
                    "submodel": {
                        "@attributes": {
                            "xmlns:aas": "http://www.admin-shell.io/aas/3.0"
                        },
                        "id": random.choice(self.sample_identifiers),
                        "idShort": f"SampleSubmodel_{random.randint(1, 1000)}",
                        "modelType": "Submodel",
                        "description": [
                            {
                                "language": "en",
                                "text": random.choice(self.sample_descriptions)
                            }
                        ],
                        "submodelElements": [
                            {
                                "id": random.choice(self.sample_identifiers),
                                "idShort": f"Property_{random.randint(1, 100)}",
                                "modelType": "Property",
                                "value": f"Sample value {random.randint(1, 1000)}",
                                "valueType": random.choice(["string", "int", "float", "boolean"])
                            }
                        ]
                    }
                }
            },
            "metadata": {
                "total_files": random.randint(3, 10),
                "aas_files": random.randint(2, 5),
                "origin_file": True,
                "compression": "ZIP",
                "encryption": "None",
                "checksum": f"sha256:{uuid.uuid4().hex}",
                "tags": random.sample(["sample", "test", "generated", "demo", "aas"], random.randint(2, 4))
            }
        }
        
        # Apply overrides
        sample_data.update(overrides)
        
        # Save to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Sample AASX file generated: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save sample AASX file: {str(e)}")
        
        return sample_data
    
    def generate_batch_processing_data(self, count: int = 10, **overrides) -> List[Dict[str, Any]]:
        """
        Generate batch processing data.
        
        Args:
            count: Number of jobs to generate
            **overrides: Override default values
            
        Returns:
            List[Dict[str, Any]]: List of processing jobs
        """
        jobs = []
        for i in range(count):
            job = self.generate_aasx_processing_job(**overrides)
            jobs.append(job)
        return jobs
    
    def generate_batch_metrics_data(self, job_ids: List[str], **overrides) -> List[Dict[str, Any]]:
        """
        Generate batch metrics data.
        
        Args:
            job_ids: List of job identifiers
            **overrides: Override default values
            
        Returns:
            List[Dict[str, Any]]: List of metrics records
        """
        metrics = []
        for job_id in job_ids:
            metric = self.generate_aasx_processing_metrics(job_id, **overrides)
            metrics.append(metric)
        return metrics
    
    def generate_test_scenarios(self) -> Dict[str, Any]:
        """Generate test scenarios for AASX processing."""
        scenarios = {
            "valid_aasx": {
                "description": "Valid AASX file with proper structure",
                "expected_result": "success",
                "validation_should_pass": True,
                "quality_score_min": 0.8
            },
            "invalid_aasx": {
                "description": "Invalid AASX file with structural issues",
                "expected_result": "failure",
                "validation_should_pass": False,
                "quality_score_min": 0.0
            },
            "large_file": {
                "description": "Large AASX file (>50MB)",
                "expected_result": "success",
                "validation_should_pass": True,
                "quality_score_min": 0.7,
                "file_size_mb": 75
            },
            "small_file": {
                "description": "Small AASX file (<1MB)",
                "expected_result": "success",
                "validation_should_pass": True,
                "quality_score_min": 0.9,
                "file_size_mb": 0.5
            },
            "corrupted_file": {
                "description": "Corrupted AASX file",
                "expected_result": "failure",
                "validation_should_pass": False,
                "quality_score_min": 0.0
            },
            "empty_file": {
                "description": "Empty AASX file",
                "expected_result": "failure",
                "validation_should_pass": False,
                "quality_score_min": 0.0
            },
            "complex_structure": {
                "description": "Complex AAS structure with many elements",
                "expected_result": "success",
                "validation_should_pass": True,
                "quality_score_min": 0.8,
                "complexity": "high"
            },
            "simple_structure": {
                "description": "Simple AAS structure with minimal elements",
                "expected_result": "success",
                "validation_should_pass": True,
                "quality_score_min": 0.9,
                "complexity": "low"
            }
        }
        
        return scenarios


class TestDataPopulator:
    """Populator for test data in the database."""
    
    def __init__(self, connection_manager):
        """
        Initialize test data populator.
        
        Args:
            connection_manager: Database connection manager
        """
        self.connection_manager = connection_manager
        self.generator = AASXDataGenerator()
    
    async def populate_test_data(self, job_count: int = 50, metrics_per_job: int = 5):
        """
        Populate database with test data.
        
        Args:
            job_count: Number of processing jobs to create
            metrics_per_job: Number of metrics records per job
        """
        try:
            # Import repositories
            from ..repositories.aasx_processing_repository import AasxProcessingRepository
            from ..repositories.aasx_processing_metrics_repository import AasxProcessingMetricsRepository
            
            # Create repositories
            job_repo = AasxProcessingRepository(self.connection_manager)
            metrics_repo = AasxProcessingMetricsRepository(self.connection_manager)
            
            logger.info(f"Populating database with {job_count} jobs and {metrics_per_job} metrics per job")
            
            # Generate and insert jobs
            created_jobs = []
            for i in range(job_count):
                job_data = self.generator.generate_aasx_processing_job()
                
                # Ensure some jobs are completed for metrics
                if i < job_count // 2:
                    job_data["status"] = "completed"
                    job_data["started_at"] = (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
                    job_data["completed_at"] = datetime.now().isoformat()
                    job_data["processing_time_seconds"] = random.randint(10, 3600)
                
                # Create job
                job = await job_repo.create(job_data)
                created_jobs.append(job)
                
                # Generate metrics for completed jobs
                if job_data["status"] == "completed":
                    for j in range(metrics_per_job):
                        metric_data = self.generator.generate_aasx_processing_metrics(
                            job.job_id,
                            timestamp=(datetime.now() - timedelta(minutes=j * 5)).isoformat()
                        )
                        await metrics_repo.create(metric_data)
            
            logger.info(f"Successfully populated database with {len(created_jobs)} jobs")
            return created_jobs
            
        except Exception as e:
            logger.error(f"Failed to populate test data: {str(e)}")
            raise
    
    async def cleanup_test_data(self):
        """Clean up test data from database."""
        try:
            # Import repositories
            from ..repositories.aasx_processing_repository import AasxProcessingRepository
            from ..repositories.aasx_processing_metrics_repository import AasxProcessingMetricsRepository
            
            # Create repositories
            job_repo = AasxProcessingRepository(self.connection_manager)
            metrics_repo = AasxProcessingMetricsRepository(self.connection_manager)
            
            logger.info("Cleaning up test data from database")
            
            # Delete all test data (you might want to add a test flag to identify test records)
            # This is a simple cleanup - in production you'd want more sophisticated cleanup
            
            # Note: This will delete ALL data - use with caution!
            # Consider adding a test flag to your models for safer cleanup
            
        except Exception as e:
            logger.error(f"Failed to cleanup test data: {str(e)}")
            raise


# Factory functions
def create_data_generator() -> AASXDataGenerator:
    """Create AASX data generator instance."""
    return AASXDataGenerator()


def create_test_data_populator(connection_manager) -> TestDataPopulator:
    """Create test data populator instance."""
    return TestDataPopulator(connection_manager)

