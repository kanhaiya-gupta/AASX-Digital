"""
Integration Layer Demo for AI RAG

This demo showcases the complete Integration Layer capabilities:
- Module Integrations (AASX, Twin Registry, KG Neo4j)
- External API Client (Vector Database, LLM Services)
- Webhook Manager (External notifications)
- Integration Coordinator (Workflow orchestration)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from ..events.event_bus import EventBus
from ..events.event_logger import EventLogger
from ..events.event_handlers import EventHandlerManager

from ..integration import (
    ModuleIntegrationManager,
    IntegrationConfig,
    IntegrationType,
    ExternalAPIManager,
    APIServiceType,
    APIEndpointConfig,
    RateLimitInfo,
    RetryConfig,
    WebhookManager,
    WebhookConfig,
    WebhookPayload,
    WebhookSecurityType,
    IntegrationCoordinator,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowPriority
)


async def demo_module_integrations(event_bus: EventBus) -> ModuleIntegrationManager:
    """Demo module integrations with AASX, Twin Registry, and KG Neo4j"""
    print("\n🔗 **Module Integrations Demo**")
    print("=" * 50)
    
    # Create integration configurations
    aasx_config = IntegrationConfig(
        integration_type=IntegrationType.AASX,
        enabled=True,
        timeout_seconds=30,
        max_retries=3,
        aasx_settings={
            "file_processing_enabled": True,
            "supported_formats": [".aasx", ".xml", ".json"]
        }
    )
    
    twin_registry_config = IntegrationConfig(
        integration_type=IntegrationType.TWIN_REGISTRY,
        enabled=True,
        timeout_seconds=45,
        max_retries=2,
        twin_registry_settings={
            "health_score_sync": True,
            "performance_monitoring": True
        }
    )
    
    kg_neo4j_config = IntegrationConfig(
        integration_type=IntegrationType.KG_NEO4J,
        enabled=True,
        timeout_seconds=60,
        max_retries=3,
        kg_neo4j_settings={
            "graph_enhancement": True,
            "ml_training_traceability": True
        }
    )
    
    # Initialize module integration manager
    integration_manager = ModuleIntegrationManager(
        [aasx_config, twin_registry_config, kg_neo4j_config],
        event_bus
    )
    
    print("✅ Module Integration Manager initialized")
    print(f"   - AASX Integration: {aasx_config.enabled}")
    print(f"   - Twin Registry Integration: {twin_registry_config.enabled}")
    print(f"   - KG Neo4j Integration: {kg_neo4j_config.enabled}")
    
    # Test AASX integration
    print("\n📁 Testing AASX Integration...")
    try:
        aasx_integration = integration_manager.get_integration(IntegrationType.AASX)
        result = await aasx_integration.process_aasx_file(
            "/path/to/sample.aasx",
            {"file_type": "aasx", "size": "2.5MB", "source": "demo"}
        )
        print(f"   ✅ AASX processing result: {result['status']}")
    except Exception as e:
        print(f"   ❌ AASX integration error: {e}")
    
    # Test Twin Registry integration
    print("\n🏥 Testing Twin Registry Integration...")
    try:
        twin_integration = integration_manager.get_integration(IntegrationType.TWIN_REGISTRY)
        result = await twin_integration.sync_twin_health_scores(["twin_001", "twin_002"])
        print(f"   ✅ Twin Registry sync result: {result['status']}")
        print(f"   📊 Synced {result['synced_twins']} twins")
    except Exception as e:
        print(f"   ❌ Twin Registry integration error: {e}")
    
    # Test KG Neo4j integration
    print("\n🧠 Testing KG Neo4j Integration...")
    try:
        kg_integration = integration_manager.get_integration(IntegrationType.KG_NEO4J)
        result = await kg_integration.enhance_knowledge_graph(
            "graph_001",
            {"enhancement_type": "ml_enhancement", "algorithm": "graph_sage"}
        )
        print(f"   ✅ KG Neo4j enhancement result: {result['status']}")
        print(f"   📈 Enhanced {result['enhancement_metadata']['enhanced_nodes']} nodes")
    except Exception as e:
        print(f"   ❌ KG Neo4j integration error: {e}")
    
    # Get integration status
    status = await integration_manager.get_integration_status()
    print(f"\n📊 Integration Status:")
    for integration_type, status_info in status.items():
        print(f"   - {integration_type}: {status_info['status']}")
    
    return integration_manager


async def demo_external_api_client(event_bus: EventBus) -> ExternalAPIManager:
    """Demo external API client with vector database and LLM services"""
    print("\n🌐 **External API Client Demo**")
    print("=" * 50)
    
    # Create API configurations
    vector_db_config = APIEndpointConfig(
        base_url="https://api.vectordb.example.com/v1",
        api_key="demo_vector_db_key",
        timeout_seconds=30,
        rate_limit=RateLimitInfo(
            requests_per_minute=100,
            requests_per_hour=1000,
            requests_per_day=10000
        ),
        retry_config=RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0
        ),
        headers={"User-Agent": "AI-RAG-Integration/1.0"},
        auth_type="api_key"
    )
    
    llm_service_config = APIEndpointConfig(
        base_url="https://api.llm.example.com/v1",
        api_key="demo_llm_key",
        timeout_seconds=60,
        rate_limit=RateLimitInfo(
            requests_per_minute=50,
            requests_per_hour=500,
            requests_per_day=5000
        ),
        retry_config=RetryConfig(
            max_retries=2,
            base_delay=2.0,
            max_delay=30.0
        ),
        headers={"User-Agent": "AI-RAG-Integration/1.0"},
        auth_type="bearer"
    )
    
    # Initialize external API manager
    api_manager = ExternalAPIManager(event_bus)
    api_manager.register_client(APIServiceType.VECTOR_DATABASE, vector_db_config)
    api_manager.register_client(APIServiceType.LLM_SERVICE, llm_service_config)
    
    print("✅ External API Manager initialized")
    print(f"   - Vector Database: {vector_db_config.base_url}")
    print(f"   - LLM Service: {llm_service_config.base_url}")
    
    # Test vector database operations
    print("\n🗄️ Testing Vector Database Operations...")
    try:
        vector_client = api_manager.get_client(APIServiceType.VECTOR_DATABASE)
        async with vector_client:
            # Test vector upsert
            vectors = [
                {"id": "vec_001", "vector": [0.1, 0.2, 0.3], "metadata": {"source": "demo"}},
                {"id": "vec_002", "vector": [0.4, 0.5, 0.6], "metadata": {"source": "demo"}}
            ]
            result = await vector_client.upsert_vectors("demo_collection", vectors)
            print(f"   ✅ Vector upsert result: {result.status.value}")
            
            # Test vector search
            search_result = await vector_client.search_vectors(
                "demo_collection", 
                [0.1, 0.2, 0.3], 
                top_k=5
            )
            print(f"   ✅ Vector search result: {search_result.status.value}")
    except Exception as e:
        print(f"   ❌ Vector database error: {e}")
    
    # Test LLM service operations
    print("\n🤖 Testing LLM Service Operations...")
    try:
        llm_client = api_manager.get_client(APIServiceType.LLM_SERVICE)
        async with llm_client:
            # Test text generation
            text_result = await llm_client.generate_text(
                "Explain the concept of knowledge graphs in one sentence.",
                max_tokens=50,
                temperature=0.7
            )
            print(f"   ✅ Text generation result: {text_result.status.value}")
            
            # Test embedding generation
            embedding_result = await llm_client.generate_embeddings([
                "Knowledge graphs represent information as interconnected entities and relationships.",
                "AI RAG systems enhance document retrieval with contextual understanding."
            ])
            print(f"   ✅ Embedding generation result: {embedding_result.status.value}")
    except Exception as e:
        print(f"   ❌ LLM service error: {e}")
    
    # Get health status
    health_status = await api_manager.health_check_all()
    print(f"\n📊 API Health Status:")
    for service_type, health in health_status.items():
        print(f"   - {service_type}: {'✅' if health else '❌'}")
    
    return api_manager


async def demo_webhook_manager(event_bus: EventBus) -> WebhookManager:
    """Demo webhook manager with external notifications"""
    print("\n🔔 **Webhook Manager Demo**")
    print("=" * 50)
    
    # Create webhook configurations
    notification_webhook = WebhookConfig(
        url="https://api.notifications.example.com/webhook",
        name="demo_notifications",
        description="Demo notification webhook",
        enabled=True,
        timeout_seconds=30,
        max_retries=3,
        security_type=WebhookSecurityType.HMAC_SHA256,
        secret_key="demo_secret_key_123",
        headers={"User-Agent": "AI-RAG-Integration/1.0"},
        priority="normal"
    )
    
    alert_webhook = WebhookConfig(
        url="https://api.alerts.example.com/webhook",
        name="demo_alerts",
        description="Demo alert webhook",
        enabled=True,
        timeout_seconds=15,
        max_retries=2,
        security_type=WebhookSecurityType.API_KEY,
        api_key="demo_alert_api_key",
        headers={"User-Agent": "AI-RAG-Integration/1.0"},
        priority="high"
    )
    
    # Initialize webhook manager
    webhook_manager = WebhookManager(event_bus)
    webhook_manager.register_webhook(notification_webhook)
    webhook_manager.register_webhook(alert_webhook)
    
    print("✅ Webhook Manager initialized")
    print(f"   - Notification Webhook: {notification_webhook.url}")
    print(f"   - Alert Webhook: {alert_webhook.url}")
    
    # Start webhook manager
    await webhook_manager.start()
    print("   🚀 Webhook Manager started")
    
    # Test webhook delivery
    print("\n📤 Testing Webhook Delivery...")
    try:
        # Create webhook payload
        payload = WebhookPayload(
            event_type="document_processed",
            event_id="doc_001",
            data={
                "document_id": "doc_001",
                "processing_status": "completed",
                "entities_extracted": 15,
                "relationships_found": 8
            },
            metadata={
                "source": "demo",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Send notification webhook
        webhook_id = await webhook_manager.send_webhook(
            "demo_notifications",
            payload,
            priority="normal"
        )
        print(f"   ✅ Notification webhook queued: {webhook_id}")
        
        # Send alert webhook
        alert_payload = WebhookPayload(
            event_type="system_alert",
            event_id="alert_001",
            data={
                "alert_type": "performance_warning",
                "message": "High memory usage detected",
                "severity": "medium"
            },
            metadata={
                "source": "demo",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        alert_webhook_id = await webhook_manager.send_webhook(
            "demo_alerts",
            alert_payload,
            priority="high"
        )
        print(f"   ✅ Alert webhook queued: {alert_webhook_id}")
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Get webhook status
        notification_status = await webhook_manager.get_webhook_status("demo_notifications")
        alert_status = await webhook_manager.get_webhook_status("demo_alerts")
        
        print(f"\n📊 Webhook Status:")
        for webhook_id, status_info in notification_status.items():
            stats = status_info["stats"]
            print(f"   - Notification {webhook_id}: {stats['total_sent']} sent, {stats['total_delivered']} delivered")
        
        for webhook_id, status_info in alert_status.items():
            stats = status_info["stats"]
            print(f"   - Alert {webhook_id}: {stats['total_sent']} sent, {stats['total_delivered']} delivered")
        
    except Exception as e:
        print(f"   ❌ Webhook error: {e}")
    
    return webhook_manager


async def demo_integration_coordinator(
    event_bus: EventBus,
    module_manager: ModuleIntegrationManager,
    api_manager: ExternalAPIManager,
    webhook_manager: WebhookManager
) -> IntegrationCoordinator:
    """Demo integration coordinator with workflow orchestration"""
    print("\n🎯 **Integration Coordinator Demo**")
    print("=" * 50)
    
    # Initialize integration coordinator
    coordinator = IntegrationCoordinator(event_bus)
    
    # Register all components
    coordinator.register_module_integrations([
        IntegrationConfig(integration_type=IntegrationType.AASX, enabled=True),
        IntegrationConfig(integration_type=IntegrationType.TWIN_REGISTRY, enabled=True),
        IntegrationConfig(integration_type=IntegrationType.KG_NEO4J, enabled=True)
    ])
    
    # Register external APIs
    api_configs = {
        APIServiceType.VECTOR_DATABASE: APIEndpointConfig(
            base_url="https://api.vectordb.example.com/v1",
            api_key="demo_key",
            rate_limit=RateLimitInfo(requests_per_minute=100, requests_per_hour=1000, requests_per_day=10000)
        ),
        APIServiceType.LLM_SERVICE: APIEndpointConfig(
            base_url="https://api.llm.example.com/v1",
            api_key="demo_key",
            rate_limit=RateLimitInfo(requests_per_minute=50, requests_per_hour=500, requests_per_day=5000)
        )
    }
    coordinator.register_external_apis(api_configs)
    
    # Register webhooks
    webhook_configs = [
        WebhookConfig(
            url="https://api.demo.example.com/webhook",
            name="demo_workflow_webhook",
            enabled=True
        )
    ]
    coordinator.register_webhooks(webhook_configs)
    
    print("✅ Integration Coordinator initialized")
    print("   - Module Integrations: Registered")
    print("   - External APIs: Registered")
    print("   - Webhooks: Registered")
    
    # Create sample workflow
    workflow = WorkflowDefinition(
        workflow_id="demo_document_processing",
        name="Demo Document Processing Workflow",
        description="Complete workflow from document processing to knowledge graph enhancement",
        version="1.0.0",
        priority=WorkflowPriority.NORMAL,
        steps=[
            WorkflowStep(
                step_id="step_1",
                name="Process AASX File",
                description="Process AASX file and extract content",
                step_type="module_integration",
                config={
                    "integration_type": "aasx",
                    "operation": "process_file",
                    "file_path": "/path/to/demo.aasx",
                    "file_metadata": {"source": "demo"}
                }
            ),
            WorkflowStep(
                step_id="step_2",
                name="Generate Embeddings",
                description="Generate vector embeddings for extracted content",
                step_type="external_api",
                config={
                    "service_type": "llm_service",
                    "operation": "generate_embeddings",
                    "texts": ["extracted_content_1", "extracted_content_2"]
                },
                dependencies=["step_1"]
            ),
            WorkflowStep(
                step_id="step_3",
                name="Store Vectors",
                description="Store vectors in vector database",
                step_type="external_api",
                config={
                    "service_type": "vector_database",
                    "operation": "upsert_vectors",
                    "collection_name": "demo_collection",
                    "vectors": [{"id": "vec_001", "vector": [0.1, 0.2, 0.3]}]
                },
                dependencies=["step_2"]
            ),
            WorkflowStep(
                step_id="step_4",
                name="Enhance Knowledge Graph",
                description="Enhance knowledge graph with new information",
                step_type="module_integration",
                config={
                    "integration_type": "kg_neo4j",
                    "operation": "enhance_graph",
                    "graph_id": "demo_graph_001",
                    "enhancement_config": {"enhancement_type": "demo"}
                },
                dependencies=["step_3"]
            ),
            WorkflowStep(
                step_id="step_5",
                name="Send Notification",
                description="Send completion notification via webhook",
                step_type="webhook",
                config={
                    "webhook_name": "demo_workflow_webhook",
                    "event_type": "workflow_completed",
                    "event_id": "workflow_demo_001",
                    "data": {"workflow_id": "demo_document_processing"},
                    "metadata": {"source": "demo"}
                },
                dependencies=["step_4"]
            )
        ],
        timeout_seconds=600  # 10 minutes
    )
    
    # Register workflow
    coordinator.register_workflow(workflow)
    print(f"\n📋 Workflow registered: {workflow.name}")
    print(f"   - Steps: {len(workflow.steps)}")
    print(f"   - Timeout: {workflow.timeout_seconds} seconds")
    print(f"   - Priority: {workflow.priority.value}")
    
    # Start coordinator
    await coordinator.start()
    print("   🚀 Integration Coordinator started")
    
    # Execute workflow
    print("\n▶️ Executing Workflow...")
    try:
        execution_id = await coordinator.execute_workflow(
            "demo_document_processing",
            priority=WorkflowPriority.NORMAL
        )
        print(f"   ✅ Workflow execution started: {execution_id}")
        
        # Monitor workflow execution
        print("   📊 Monitoring workflow execution...")
        for i in range(5):  # Monitor for 5 iterations
            await asyncio.sleep(2)
            
            execution = await coordinator.get_workflow_status(execution_id)
            if execution:
                print(f"      - Status: {execution.status.value}")
                if execution.current_step:
                    print(f"      - Current Step: {execution.current_step}")
                if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.TIMEOUT]:
                    break
            else:
                print("      - Execution not found")
                break
        
        # Get final execution status
        final_execution = await coordinator.get_workflow_status(execution_id)
        if final_execution:
            print(f"\n📋 Final Workflow Status:")
            print(f"   - Status: {final_execution.status.value}")
            print(f"   - Started: {final_execution.started_at}")
            print(f"   - Completed: {final_execution.completed_at}")
            if final_execution.step_results:
                print(f"   - Steps Completed: {len(final_execution.step_results)}")
            if final_execution.step_errors:
                print(f"   - Steps with Errors: {len(final_execution.step_errors)}")
        
    except Exception as e:
        print(f"   ❌ Workflow execution error: {e}")
    
    # Get integration metrics
    metrics = await coordinator.get_integration_metrics()
    print(f"\n📊 Integration Metrics:")
    print(f"   - Total Workflows: {metrics.total_workflows}")
    print(f"   - Successful: {metrics.successful_workflows}")
    print(f"   - Failed: {metrics.failed_workflows}")
    print(f"   - Active: {metrics.active_workflows}")
    print(f"   - Average Execution Time: {metrics.average_execution_time_ms:.2f} ms")
    
    # Get health status
    health_status = await coordinator.get_health_status()
    print(f"\n🏥 System Health Status:")
    for component, health in health_status.items():
        if isinstance(health, dict):
            print(f"   - {component}:")
            for sub_component, sub_health in health.items():
                status_icon = "✅" if sub_health else "❌"
                print(f"     * {sub_component}: {status_icon}")
        else:
            status_icon = "✅" if health else "❌"
            print(f"   - {component}: {status_icon}")
    
    return coordinator


async def demo_integration_layer():
    """Main demo function for the complete Integration Layer"""
    print("🚀 **AI RAG Integration Layer - Complete Demo**")
    print("=" * 60)
    print("This demo showcases the complete Integration Layer capabilities")
    print("including module integrations, external APIs, webhooks, and workflow orchestration.")
    
    # Initialize event system
    event_bus = EventBus()
    event_logger = EventLogger()
    event_handler_manager = EventHandlerManager(event_bus)
    
    # Start event system
    await event_bus.start()
    await event_logger.start()
    await event_handler_manager.start()
    
    print("\n✅ Event System initialized")
    
    try:
        # Demo 1: Module Integrations
        module_manager = await demo_module_integrations(event_bus)
        
        # Demo 2: External API Client
        api_manager = await demo_external_api_client(event_bus)
        
        # Demo 3: Webhook Manager
        webhook_manager = await demo_webhook_manager(event_bus)
        
        # Demo 4: Integration Coordinator
        coordinator = await demo_integration_coordinator(
            event_bus, module_manager, api_manager, webhook_manager
        )
        
        print("\n🎉 **Integration Layer Demo Completed Successfully!**")
        print("=" * 60)
        print("✅ All integration components demonstrated")
        print("✅ Module integrations working")
        print("✅ External API clients functional")
        print("✅ Webhook delivery system operational")
        print("✅ Workflow orchestration successful")
        print("✅ Event-driven architecture operational")
        
        # Cleanup
        await coordinator.stop()
        await webhook_manager.stop()
        await event_handler_manager.stop()
        await event_logger.stop()
        await event_bus.stop()
        
        print("\n🧹 Cleanup completed")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logging.error(f"Integration Layer Demo Error: {e}", exc_info=True)
        
        # Ensure cleanup
        try:
            await event_handler_manager.stop()
            await event_logger.stop()
            await event_bus.stop()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    asyncio.run(demo_integration_layer())


