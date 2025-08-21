"""
Module Discovery Service

This service automatically discovers and registers available task modules
within the AAS Data Modeling Engine ecosystem.

The discovery service scans for modules, validates their availability,
and maintains a registry of discovered modules for use by other
integration services.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from .models import ModuleInfo, ModuleType, ModuleStatus


logger = logging.getLogger(__name__)


class ModuleDiscoveryService:
    """
    Service for discovering and registering available task modules.
    
    This service automatically scans the system for available modules,
    validates their health, and maintains a registry of discovered
    modules for use by the integration layer.
    """
    
    def __init__(self, discovery_interval: int = 300):
        """
        Initialize the module discovery service.
        
        Args:
            discovery_interval: Interval in seconds between discovery scans
        """
        self.discovery_interval = discovery_interval
        self.discovered_modules: Dict[str, ModuleInfo] = {}
        self.discovery_history: List[Dict] = []
        self.is_discovering = False
        self.last_discovery = None
        
        # Module discovery patterns
        self.module_patterns = {
            ModuleType.TWIN_REGISTRY: {
                "name": "twin_registry",
                "description": "Digital Twin Registry Management",
                "capabilities": ["twin_creation", "twin_query", "twin_update", "twin_deletion"]
            },
            ModuleType.AASX: {
                "name": "aasx",
                "description": "AASX File Processing and ETL",
                "capabilities": ["aasx_import", "aasx_export", "aasx_validation", "aasx_transformation"]
            },
            ModuleType.AI_RAG: {
                "name": "ai_rag",
                "description": "AI-Powered Retrieval-Augmented Generation",
                "capabilities": ["text_analysis", "semantic_search", "content_generation", "knowledge_extraction"]
            },
            ModuleType.KG_NEO4J: {
                "name": "kg_neo4j",
                "description": "Knowledge Graph Management with Neo4j",
                "capabilities": ["graph_query", "graph_analysis", "relationship_mapping", "knowledge_inference"]
            },
            ModuleType.FEDERATED_LEARNING: {
                "name": "federated_learning",
                "description": "Distributed Machine Learning",
                "capabilities": ["model_training", "model_aggregation", "privacy_preservation", "distributed_inference"]
            },
            ModuleType.PHYSICS_MODELING: {
                "name": "physics_modeling",
                "description": "Physics-Based Modeling and Simulation",
                "capabilities": ["simulation_execution", "parameter_optimization", "result_analysis", "model_validation"]
            },
            ModuleType.CERTIFICATE_MANAGER: {
                "name": "certificate_manager",
                "description": "Digital Certificate Management",
                "capabilities": ["certificate_issuance", "certificate_validation", "revocation_management", "chain_verification"]
            }
        }
    
    async def start_discovery(self) -> None:
        """Start the automatic module discovery process."""
        if self.is_discovering:
            logger.warning("Module discovery is already running")
            return
        
        self.is_discovering = True
        logger.info("Starting automatic module discovery service")
        
        # Run discovery as a background task
        self._discovery_task = asyncio.create_task(self._discovery_loop())
    
    async def _discovery_loop(self) -> None:
        """Background task for continuous discovery."""
        try:
            while self.is_discovering:
                await self.perform_discovery()
                await asyncio.sleep(self.discovery_interval)
        except Exception as e:
            logger.error(f"Error in module discovery service: {e}")
            self.is_discovering = False
            raise
    
    async def stop_discovery(self) -> None:
        """Stop the automatic module discovery process."""
        self.is_discovering = False
        
        # Cancel the background task if it exists
        if hasattr(self, '_discovery_task') and self._discovery_task:
            try:
                self._discovery_task.cancel()
                await self._discovery_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling
            except Exception as e:
                logger.warning(f"Error cancelling discovery task: {e}")
        
        logger.info("Stopped automatic module discovery service")
    
    async def perform_discovery(self) -> None:
        """Perform a single discovery scan for available modules."""
        logger.debug("Starting module discovery scan")
        start_time = datetime.utcnow()
        
        try:
            # Discover modules from different sources
            discovered_modules = []
            
            # 1. Discover from src/modules directory
            src_modules = await self._discover_from_src_modules()
            discovered_modules.extend(src_modules)
            
            # 2. Discover from webapp modules
            webapp_modules = await self._discover_from_webapp_modules()
            discovered_modules.extend(webapp_modules)
            
            # 3. Discover from environment variables
            env_modules = await self._discover_from_environment()
            discovered_modules.extend(env_modules)
            
            # Update discovered modules registry
            await self._update_discovery_registry(discovered_modules)
            
            # Record discovery history
            discovery_record = {
                "timestamp": start_time,
                "modules_found": len(discovered_modules),
                "total_modules": len(self.discovered_modules),
                "status": "success"
            }
            self.discovery_history.append(discovery_record)
            
            self.last_discovery = start_time
            logger.info(f"Discovery scan completed: {len(self.discovered_modules)} unique modules found")
            
        except Exception as e:
            logger.error(f"Error during discovery scan: {e}")
            discovery_record = {
                "timestamp": start_time,
                "modules_found": 0,
                "total_modules": len(self.discovered_modules),
                "status": "error",
                "error": str(e)
            }
            self.discovery_history.append(discovery_record)
    
    async def _discover_from_src_modules(self) -> List[ModuleInfo]:
        """Discover modules from the src/modules directory."""
        discovered = []
        src_modules_path = Path("src/modules")
        
        if not src_modules_path.exists():
            logger.debug("src/modules directory not found")
            return discovered
        
        try:
            for module_dir in src_modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith("_"):
                    module_info = await self._create_module_info_from_directory(module_dir)
                    if module_info:
                        discovered.append(module_info)
        except Exception as e:
            logger.error(f"Error discovering from src/modules: {e}")
        
        return discovered
    
    async def _discover_from_webapp_modules(self) -> List[ModuleInfo]:
        """Discover modules from the webapp/modules directory."""
        discovered = []
        webapp_modules_path = Path("webapp/modules")
        
        if not webapp_modules_path.exists():
            logger.debug("webapp/modules directory not found")
            return discovered
        
        try:
            for module_dir in webapp_modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith("_"):
                    module_info = await self._create_module_info_from_webapp_directory(module_dir)
                    if module_info:
                        discovered.append(module_info)
        except Exception as e:
            logger.error(f"Error discovering from webapp/modules: {e}")
        
        return discovered
    
    async def _discover_from_environment(self) -> List[ModuleInfo]:
        """Discover modules from environment variables."""
        discovered = []
        
        # Check for module URLs in environment variables
        for key, value in os.environ.items():
            if key.startswith("MODULE_") and key.endswith("_URL"):
                module_name = key[7:-4].lower()  # Remove MODULE_ and _URL
                module_info = await self._create_module_info_from_environment(module_name, value)
                if module_info:
                    discovered.append(module_info)
        
        return discovered
    
    async def _create_module_info_from_directory(self, module_dir: Path) -> Optional[ModuleInfo]:
        """Create ModuleInfo from a module directory."""
        try:
            module_name = module_dir.name
            
            # Determine module type
            module_type = self._get_module_type_from_name(module_name)
            if not module_type:
                return None
            
            # Get module pattern
            pattern = self.module_patterns.get(module_type, {})
            
            # Check for __init__.py to confirm it's a Python module
            init_file = module_dir / "__init__.py"
            if not init_file.exists():
                return None
            
            # Create module info
            module_info = ModuleInfo(
                name=pattern.get("name", module_name),
                module_type=module_type,
                description=pattern.get("description", f"{module_name} module"),
                capabilities=pattern.get("capabilities", []),
                base_url=f"src/modules/{module_name}",
                metadata={
                    "discovery_source": "src_modules",
                    "module_path": str(module_dir),
                    "has_init": True
                }
            )
            
            return module_info
            
        except Exception as e:
            logger.error(f"Error creating module info from directory {module_dir}: {e}")
            return None
    
    async def _create_module_info_from_webapp_directory(self, module_dir: Path) -> Optional[ModuleInfo]:
        """Create ModuleInfo from a webapp module directory."""
        try:
            module_name = module_dir.name
            
            # Determine module type
            module_type = self._get_module_type_from_name(module_name)
            if not module_type:
                return None
            
            # Get module pattern
            pattern = self.module_patterns.get(module_type, {})
            
            # Check for routes.py to confirm it's a webapp module
            routes_file = module_dir / "routes.py"
            if not routes_file.exists():
                return None
            
            # Create module info
            module_info = ModuleInfo(
                name=pattern.get("name", module_name),
                module_type=module_type,
                description=pattern.get("description", f"{module_name} webapp module"),
                capabilities=pattern.get("capabilities", []),
                base_url=f"webapp/modules/{module_name}",
                api_endpoint=f"/api/{module_name}",
                metadata={
                    "discovery_source": "webapp_modules",
                    "module_path": str(module_dir),
                    "has_routes": True
                }
            )
            
            return module_info
            
        except Exception as e:
            logger.error(f"Error creating module info from webapp directory {module_dir}: {e}")
            return None
    
    async def _create_module_info_from_environment(self, module_name: str, url: str) -> Optional[ModuleInfo]:
        """Create ModuleInfo from environment variable."""
        try:
            # Determine module type
            module_type = self._get_module_type_from_name(module_name)
            if not module_type:
                return None
            
            # Get module pattern
            pattern = self.module_patterns.get(module_type, {})
            
            # Create module info
            module_info = ModuleInfo(
                name=pattern.get("name", module_name),
                module_type=module_type,
                description=pattern.get("description", f"{module_name} external module"),
                capabilities=pattern.get("capabilities", []),
                base_url=url,
                api_endpoint=f"{url}/api",
                metadata={
                    "discovery_source": "environment",
                    "external_url": url
                }
            )
            
            return module_info
            
        except Exception as e:
            logger.error(f"Error creating module info from environment {module_name}: {e}")
            return None
    
    def _get_module_type_from_name(self, module_name: str) -> Optional[ModuleType]:
        """Get ModuleType from module name."""
        name_mapping = {
            "twin_registry": ModuleType.TWIN_REGISTRY,
            "aasx": ModuleType.AASX,
            "ai_rag": ModuleType.AI_RAG,
            "kg_neo4j": ModuleType.KG_NEO4J,
            "federated_learning": ModuleType.FEDERATED_LEARNING,
            "physics_modeling": ModuleType.PHYSICS_MODELING,
            "certificate_manager": ModuleType.CERTIFICATE_MANAGER
        }
        return name_mapping.get(module_name)
    
    async def _update_discovery_registry(self, discovered_modules: List[ModuleInfo]) -> None:
        """Update the discovered modules registry."""
        current_time = datetime.utcnow()
        
        # Update existing modules
        for module_info in discovered_modules:
            if module_info.name in self.discovered_modules:
                # Update last seen timestamp
                existing = self.discovered_modules[module_info.name]
                existing.last_seen = current_time
                existing.metadata.update(module_info.metadata)
            else:
                # Add new module
                self.discovered_modules[module_info.name] = module_info
                logger.info(f"Discovered new module: {module_info.name} ({module_info.module_type.value})")
        
        # Mark modules as offline if not seen recently
        offline_threshold = current_time - timedelta(minutes=10)
        for module_name, module_info in self.discovered_modules.items():
            if module_info.last_seen < offline_threshold:
                logger.warning(f"Module {module_name} appears to be offline (last seen: {module_info.last_seen})")
    
    def get_discovered_modules(self) -> List[ModuleInfo]:
        """Get list of all discovered modules."""
        return list(self.discovered_modules.values())
    
    def get_module_by_name(self, module_name: str) -> Optional[ModuleInfo]:
        """Get a specific module by name."""
        return self.discovered_modules.get(module_name)
    
    def get_modules_by_type(self, module_type: ModuleType) -> List[ModuleInfo]:
        """Get all modules of a specific type."""
        return [module for module in self.discovered_modules.values() 
                if module.module_type == module_type]
    
    def get_discovery_history(self, limit: int = 100) -> List[Dict]:
        """Get discovery history with optional limit."""
        return self.discovery_history[-limit:] if self.discovery_history else []
    
    def get_discovery_status(self) -> Dict:
        """Get current discovery service status."""
        return {
            "is_discovering": self.is_discovering,
            "last_discovery": self.last_discovery,
            "total_modules": len(self.discovered_modules),
            "discovery_interval": self.discovery_interval,
            "discovery_history_count": len(self.discovery_history)
        }
