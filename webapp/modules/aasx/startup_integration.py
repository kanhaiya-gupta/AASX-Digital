"""
Startup Integration for ETL Twin Registry
Initializes the ETL integration when the webapp starts
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Global integration instances
_etl_integration = None
_etl_integration_task = None
_file_upload_integration = None
_file_upload_integration_task = None

async def initialize_etl_twin_registry_integration():
    """Initialize the ETL Twin Registry integration"""
    global _etl_integration, _integration_task
    
    try:
        logger.info("🚀 Initializing ETL Twin Registry Integration...")
        
        # Import the integration module
        from .etl_twin_registry_integration import ETLTwinRegistryIntegration
        
        # Create integration instance
        _etl_integration = ETLTwinRegistryIntegration()
        
        # Start the integration
        await _etl_integration.start()
        
        logger.info("✅ ETL Twin Registry Integration initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize ETL Twin Registry Integration: {e}")
        return False

async def initialize_file_upload_twin_registry_integration():
    """Initialize the File Upload Twin Registry integration"""
    global _file_upload_integration, _file_upload_task
    
    try:
        logger.info("🚀 Initializing File Upload Twin Registry Integration...")
        
        # Import the integration module
        from .file_upload_twin_registry_integration import FileUploadTwinRegistryIntegration
        
        # Create integration instance
        _file_upload_integration = FileUploadTwinRegistryIntegration()
        
        # Start the integration
        await _file_upload_integration.start()
        
        logger.info("✅ File Upload Twin Registry Integration initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize File Upload Twin Registry Integration: {e}")
        return False

async def shutdown_etl_twin_registry_integration():
    """Shutdown the ETL Twin Registry integration"""
    global _etl_integration, _etl_integration_task
    
    try:
        if _etl_integration:
            logger.info("🛑 Shutting down ETL Twin Registry Integration...")
            await _etl_integration.stop()
            _etl_integration = None
            logger.info("✅ ETL Twin Registry Integration shut down successfully")
        
        if _etl_integration_task:
            _etl_integration_task.cancel()
            _etl_integration_task = None
            
    except Exception as e:
        logger.error(f"❌ Error shutting down ETL Twin Registry Integration: {e}")

async def shutdown_file_upload_twin_registry_integration():
    """Shutdown the File Upload Twin Registry integration"""
    global _file_upload_integration, _file_upload_integration_task
    
    try:
        if _file_upload_integration:
            logger.info("🛑 Shutting down File Upload Twin Registry Integration...")
            await _file_upload_integration.stop()
            _file_upload_integration = None
            logger.info("✅ File Upload Twin Registry Integration shut down successfully")
        
        if _file_upload_integration_task:
            _file_upload_integration_task.cancel()
            _file_upload_integration_task = None
            
    except Exception as e:
        logger.error(f"❌ Error shutting down File Upload Twin Registry Integration: {e}")

def get_etl_integration():
    """Get the global ETL integration instance"""
    global _etl_integration
    return _etl_integration

def get_file_upload_integration():
    """Get the global File Upload integration instance"""
    global _file_upload_integration
    return _file_upload_integration

def is_etl_integration_active():
    """Check if the ETL integration is active"""
    global _etl_integration
    return _etl_integration is not None and _etl_integration.is_active

def is_file_upload_integration_active():
    """Check if the File Upload integration is active"""
    global _file_upload_integration
    return _file_upload_integration is not None and _file_upload_integration.is_active

def is_integration_active():
    """Check if any integration is active"""
    return is_etl_integration_active() or is_file_upload_integration_active()

async def start_etl_integration_background():
    """Start the ETL integration in the background"""
    global _etl_integration_task
    
    try:
        if not _etl_integration_task or _etl_integration_task.done():
            _etl_integration_task = asyncio.create_task(
                initialize_etl_twin_registry_integration()
            )
            logger.info("✅ ETL Twin Registry Integration background task started")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start ETL integration background task: {e}")
        return False

async def start_file_upload_integration_background():
    """Start the File Upload integration in the background"""
    global _file_upload_integration_task
    
    try:
        if not _file_upload_integration_task or _file_upload_integration_task.done():
            _file_upload_integration_task = asyncio.create_task(
                initialize_file_upload_twin_registry_integration()
            )
            logger.info("✅ File Upload Twin Registry Integration background task started")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start File Upload integration background task: {e}")
        return False

async def start_integration_background():
    """Start all integrations in the background"""
    try:
        etl_success = await start_etl_integration_background()
        upload_success = await start_file_upload_integration_background()
        
        return etl_success and upload_success
        
    except Exception as e:
        logger.error(f"❌ Failed to start integrations background tasks: {e}")
        return False

def setup_integration_hooks(app):
    """Setup integration hooks for the Flask/FastAPI app"""
    try:
        # For Flask
        if hasattr(app, 'before_first_request'):
            @app.before_first_request
            def before_first_request():
                asyncio.run(initialize_etl_twin_registry_integration())
                asyncio.run(initialize_file_upload_twin_registry_integration())
        
        # For FastAPI
        if hasattr(app, 'add_event_handler'):
            @app.on_event("startup")
            async def startup_event():
                await initialize_etl_twin_registry_integration()
                await initialize_file_upload_twin_registry_integration()
            
            @app.on_event("shutdown")
            async def shutdown_event():
                await shutdown_etl_twin_registry_integration()
                await shutdown_file_upload_twin_registry_integration()
        
        logger.info("✅ Twin Registry Integration hooks setup successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup integration hooks: {e}")

# Auto-initialization for standalone usage
if __name__ == "__main__":
    async def main():
        """Main function for standalone testing"""
        try:
            logger.info("🚀 Testing Twin Registry Integrations...")
            
            # Initialize both integrations
            etl_success = await initialize_etl_twin_registry_integration()
            upload_success = await initialize_file_upload_twin_registry_integration()
            
            if etl_success and upload_success:
                logger.info("🎉 Both integrations initialized successfully!")
                
                # Keep running for a bit to test
                await asyncio.sleep(5)
                
                # Shutdown both integrations
                await shutdown_etl_twin_registry_integration()
                await shutdown_file_upload_twin_registry_integration()
                logger.info("✅ Both integrations shutdown successfully!")
            else:
                logger.error("❌ Some integrations failed to initialize!")
                
        except Exception as e:
            logger.error(f"❌ Main function failed: {e}")
    
    # Run the main function
    asyncio.run(main())
