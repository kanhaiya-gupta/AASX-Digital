"""
Twin Registry Event System Demo

Demonstrates the event-driven automation capabilities of the Twin Registry module.
Phase 3: Event System & Automation showcase.

This script shows how to:
1. Initialize the Twin Registry service with event automation
2. Trigger file upload events to automatically create twins
3. Trigger ETL success/failure events to automatically create metrics
4. Monitor the event system status
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.modules.twin_registry import TwinRegistryService, EventType, EventPriority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_event_system():
    """Demonstrate the Twin Registry event system capabilities."""
    
    logger.info("🚀 Starting Twin Registry Event System Demo")
    logger.info("=" * 60)
    
    try:
        # Initialize the Twin Registry service
        logger.info("📋 Initializing Twin Registry Service...")
        twin_service = TwinRegistryService()
        await twin_service.initialize()
        
        # Check event manager status
        logger.info("📊 Checking Event Manager Status...")
        status = await twin_service.get_event_manager_status()
        logger.info(f"Event Manager Status: {status}")
        
        logger.info("=" * 60)
        logger.info("🎯 Demo 1: Automatic Twin Creation on File Upload")
        logger.info("-" * 40)
        
        # Simulate file upload events to automatically create twins
        file_uploads = [
            {
                "file_id": "file_001",
                "file_name": "manufacturing_plant.aasx",
                "file_type": "aasx",
                "project_id": "proj_001",
                "processed_by": "user_001",
                "org_id": "org_001",
                "dept_id": "dept_001"
            },
            {
                "file_id": "file_002", 
                "file_name": "energy_system.json",
                "file_type": "json",
                "project_id": "proj_002",
                "processed_by": "user_002",
                "org_id": "org_001",
                "dept_id": "dept_002"
            },
            {
                "file_id": "file_003",
                "file_name": "hybrid_workflow.xml",
                "file_type": "hybrid",
                "project_id": "proj_003",
                "processed_by": "user_001",
                "org_id": "org_001",
                "dept_id": "dept_001"
            }
        ]
        
        for file_data in file_uploads:
            logger.info(f"📁 Triggering file upload event for: {file_data['file_name']}")
            
            await twin_service.trigger_file_upload_event(
                file_id=file_data["file_id"],
                file_name=file_data["file_name"],
                file_type=file_data["file_type"],
                project_id=file_data["project_id"],
                processed_by=file_data["processed_by"],
                org_id=file_data["org_id"],
                dept_id=file_data["dept_id"]
            )
            
            # Brief pause to see events being processed
            await asyncio.sleep(1)
        
        logger.info("=" * 60)
        logger.info("🎯 Demo 2: Automatic Metrics Creation on ETL Success")
        logger.info("-" * 40)
        
        # Simulate ETL success events to automatically create metrics
        etl_successes = [
            {
                "twin_id": "twin_file_001_extraction",
                "processing_time": 2.5,
                "records_processed": 150,
                "success_rate": 0.98
            },
            {
                "twin_id": "twin_file_002_generation",
                "processing_time": 1.8,
                "records_processed": 75,
                "success_rate": 1.0
            },
            {
                "twin_id": "twin_file_003_hybrid",
                "processing_time": 3.2,
                "records_processed": 200,
                "success_rate": 0.95
            }
        ]
        
        for etl_data in etl_successes:
            logger.info(f"✅ Triggering ETL success event for: {etl_data['twin_id']}")
            
            await twin_service.trigger_etl_success_event(
                twin_id=etl_data["twin_id"],
                processing_time=etl_data["processing_time"],
                records_processed=etl_data["records_processed"],
                success_rate=etl_data["success_rate"]
            )
            
            # Brief pause to see events being processed
            await asyncio.sleep(1)
        
        logger.info("=" * 60)
        logger.info("🎯 Demo 3: Automatic Status Updates on ETL Failure")
        logger.info("-" * 40)
        
        # Simulate ETL failure event
        logger.info("❌ Triggering ETL failure event for: twin_file_001_extraction")
        
        await twin_service.trigger_etl_failure_event(
            twin_id="twin_file_001_extraction",
            error_message="Database connection timeout",
            failure_reason="network_error"
        )
        
        # Brief pause to see events being processed
        await asyncio.sleep(1)
        
        logger.info("=" * 60)
        logger.info("📊 Final Event Manager Status")
        logger.info("-" * 40)
        
        # Check final status
        final_status = await twin_service.get_event_manager_status()
        logger.info(f"Final Event Manager Status: {final_status}")
        
        # Get twin statistics
        logger.info("📈 Getting Twin Statistics...")
        stats = await twin_service.get_twin_statistics()
        logger.info(f"Twin Statistics: {stats}")
        
        logger.info("=" * 60)
        logger.info("🎉 Demo Completed Successfully!")
        logger.info("=" * 60)
        
        # Cleanup
        await twin_service.cleanup()
        
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {e}")
        raise


async def demo_manual_twin_operations():
    """Demonstrate manual twin operations alongside the event system."""
    
    logger.info("🔧 Manual Twin Operations Demo")
    logger.info("=" * 60)
    
    try:
        # Initialize service
        twin_service = TwinRegistryService()
        await twin_service.initialize()
        
        # Manually register a twin
        logger.info("📝 Manually registering a twin...")
        twin = await twin_service.register_twin(
            twin_id="manual_twin_001",
            registry_name="Manual_Registry_001",
            registry_type="manual",
            workflow_source="manual_creation",
            user_id="demo_user",
            org_id="demo_org",
            dept_id="demo_dept"
        )
        
        logger.info(f"✅ Manually created twin: {twin.twin_id}")
        
        # Get the twin
        retrieved_twin = await twin_service.get_twin_by_id("manual_twin_001")
        logger.info(f"📋 Retrieved twin: {retrieved_twin}")
        
        # Update twin health
        logger.info("💚 Updating twin health score...")
        await twin_service.update_health_score("manual_twin_001", 95)
        
        # Get updated twin
        updated_twin = await twin_service.get_twin_by_id("manual_twin_001")
        logger.info(f"📋 Updated twin: {updated_twin}")
        
        # Cleanup
        await twin_service.cleanup()
        
    except Exception as e:
        logger.error(f"❌ Manual operations demo failed: {e}")
        raise


async def main():
    """Main demo function."""
    logger.info("🎬 Twin Registry Event System Demo Suite")
    logger.info("=" * 60)
    
    try:
        # Run the main event system demo
        await demo_event_system()
        
        logger.info("\n" + "=" * 60)
        
        # Run the manual operations demo
        await demo_manual_twin_operations()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎊 All demos completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo suite failed: {e}")
        raise


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())

