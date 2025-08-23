"""
AASX Digital Twin Analytics Framework - Modules Package

This package provides comprehensive module management and integration capabilities for the
AASX Digital Twin Analytics Framework. It serves as the central registry for all
available modules, enabling seamless cross-module communication, discovery, and orchestration.

The modules package contains specialized domain modules that work together to provide
end-to-end digital twin analytics capabilities:

Core Modules:
- certificate_manager: Digital certificate generation and management
- twin_registry: Digital twin lifecycle and registry management
- aasx: AASX file processing and ETL operations
- ai_rag: AI-powered retrieval augmented generation
- kg_neo4j: Knowledge graph and Neo4j integration
- physics_modeling: Physics-based modeling and simulation
- federated_learning: Distributed machine learning capabilities
- data_governance: Data quality and governance management

Integration Features:
- Module discovery and health monitoring
- Cross-module data synchronization
- Workflow orchestration
- Event broadcasting and subscription
- Performance monitoring and optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import importlib
import inspect

logger = logging.getLogger(__name__)

# Module registry for dynamic discovery and loading
MODULE_REGISTRY = {}

# Module status tracking
MODULE_STATUS = {}

# Module dependencies mapping
MODULE_DEPENDENCIES = {
    'certificate_manager': ['twin_registry', 'aasx', 'ai_rag', 'kg_neo4j', 'physics_modeling', 'federated_learning', 'data_governance'],
    'twin_registry': ['aasx', 'data_governance'],
    'aasx': ['data_governance'],
    'ai_rag': ['kg_neo4j', 'data_governance'],
    'kg_neo4j': ['data_governance'],
    'physics_modeling': ['twin_registry', 'data_governance'],
    'federated_learning': ['twin_registry', 'data_governance'],
    'data_governance': []
}

# Module priority for initialization order
MODULE_PRIORITY = [
    'data_governance',      # Foundation layer
    'aasx',                 # Main AASX orchestration
    'twin_registry',        # Twin management
    'kg_neo4j',            # Knowledge infrastructure
    'ai_rag',              # AI capabilities
    'physics_modeling',     # Modeling capabilities
    'federated_learning',   # Learning capabilities
    'certificate_manager'   # Integration and certification
]


class ModuleRegistry:
    """
    Central module registry for managing all available modules.
    
    Provides module discovery, health monitoring, dependency management,
    and cross-module communication capabilities.
    """
    
    def __init__(self):
        self.modules = {}
        self.module_instances = {}
        self.health_status = {}
        self.dependencies = MODULE_DEPENDENCIES
        self.priority_order = MODULE_PRIORITY
        self._initialized = False
        self._logger = logging.getLogger(f"{__name__}.ModuleRegistry")
    
    async def discover_modules(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all available modules in the modules directory.
        
        Returns:
            Dict containing module information and metadata
        """
        modules_dir = Path(__file__).parent
        discovered_modules = {}
        
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('_'):
                module_name = module_dir.name
                module_init = module_dir / '__init__.py'
                
                if module_init.exists():
                    try:
                        # Try to import the module
                        module_spec = importlib.util.spec_from_file_location(
                            module_name, 
                            str(module_init)
                        )
                        if module_spec and module_spec.loader:
                            module = importlib.util.module_from_spec(module_spec)
                            module_spec.loader.exec_module(module)
                            
                            # Extract module metadata
                            module_info = {
                                'name': module_name,
                                'path': str(module_dir),
                                'version': getattr(module, '__version__', 'unknown'),
                                'author': getattr(module, '__author__', 'unknown'),
                                'description': getattr(module, '__doc__', ''),
                                'available': True,
                                'main_class': None,
                                'exports': []
                            }
                            
                            # Look for main service class
                            for attr_name in dir(module):
                                attr = getattr(module, attr_name)
                                if inspect.isclass(attr) and 'Manager' in attr_name:
                                    module_info['main_class'] = attr_name
                                    break
                            
                            # Get exported symbols
                            if hasattr(module, '__all__'):
                                module_info['exports'] = module.__all__
                            
                            discovered_modules[module_name] = module_info
                            self._logger.info(f"Discovered module: {module_name} v{module_info['version']}")
                            
                    except Exception as e:
                        self._logger.warning(f"Failed to discover module {module_name}: {e}")
                        discovered_modules[module_name] = {
                            'name': module_name,
                            'path': str(module_dir),
                            'available': False,
                            'error': str(e)
                        }
        
        return discovered_modules
    
    async def initialize_modules(self, modules_to_init: Optional[List[str]] = None) -> bool:
        """
        Initialize specified modules or all available modules.
        
        Args:
            modules_to_init: List of module names to initialize, or None for all
            
        Returns:
            bool: True if all modules initialized successfully
        """
        if self._initialized:
            self._logger.info("Module registry already initialized")
            return True
        
        try:
            # Discover available modules
            discovered = await self.discover_modules()
            self.modules = discovered
            
            # Determine which modules to initialize
            if modules_to_init is None:
                modules_to_init = [name for name, info in discovered.items() if info.get('available', False)]
            
            # Initialize modules in priority order
            initialized_count = 0
            for module_name in self.priority_order:
                if module_name in modules_to_init and module_name in discovered:
                    if await self._initialize_single_module(module_name):
                        initialized_count += 1
                    else:
                        self._logger.error(f"Failed to initialize module: {module_name}")
            
            self._initialized = True
            self._logger.info(f"Successfully initialized {initialized_count}/{len(modules_to_init)} modules")
            return initialized_count == len(modules_to_init)
            
        except Exception as e:
            self._logger.error(f"Failed to initialize modules: {e}")
            return False
    
    async def _initialize_single_module(self, module_name: str) -> bool:
        """
        Initialize a single module.
        
        Args:
            module_name: Name of the module to initialize
            
        Returns:
            bool: True if initialization successful
        """
        try:
            module_info = self.modules.get(module_name)
            if not module_info or not module_info.get('available', False):
                return False
            
            # Check dependencies
            dependencies = self.dependencies.get(module_name, [])
            for dep in dependencies:
                if dep not in self.module_instances:
                    self._logger.warning(f"Module {module_name} depends on {dep} which is not initialized")
                    return False
            
            # Import and initialize the module
            module_path = f"src.modules.{module_name}"
            module = importlib.import_module(module_path)
            
            # Look for main service class
            main_class_name = module_info.get('main_class')
            if main_class_name and hasattr(module, main_class_name):
                main_class = getattr(module, main_class_name)
                if inspect.isclass(main_class):
                    # Create instance if it has async __init__ or no __init__
                    try:
                        if hasattr(main_class, '__init__') and inspect.iscoroutinefunction(main_class.__init__):
                            instance = await main_class()
                        else:
                            instance = main_class()
                        self.module_instances[module_name] = instance
                        self._logger.info(f"Initialized module {module_name} with instance of {main_class_name}")
                    except Exception as e:
                        self._logger.warning(f"Could not instantiate {main_class_name} for {module_name}: {e}")
                        # Still mark as available even without instance
                        self.module_instances[module_name] = None
            
            # Update status
            self.health_status[module_name] = {
                'status': 'initialized',
                'timestamp': asyncio.get_event_loop().time(),
                'dependencies': dependencies,
                'main_class': main_class_name
            }
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize module {module_name}: {e}")
            self.health_status[module_name] = {
                'status': 'failed',
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }
            return False
    
    async def get_module(self, module_name: str) -> Optional[Any]:
        """
        Get a module instance by name.
        
        Args:
            module_name: Name of the module to retrieve
            
        Returns:
            Module instance or None if not found/initialized
        """
        return self.module_instances.get(module_name)
    
    async def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Module information dictionary or None if not found
        """
        return self.modules.get(module_name)
    
    async def list_available_modules(self) -> List[str]:
        """
        Get list of all available modules.
        
        Returns:
            List of module names
        """
        return list(self.modules.keys())
    
    async def list_initialized_modules(self) -> List[str]:
        """
        Get list of all initialized modules.
        
        Returns:
            List of initialized module names
        """
        return list(self.module_instances.keys())
    
    async def get_module_health(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get health status of a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Health status dictionary or None if not found
        """
        return self.health_status.get(module_name)
    
    async def get_all_module_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status of all modules.
        
        Returns:
            Dictionary mapping module names to health status
        """
        return self.health_status.copy()
    
    async def check_module_dependencies(self, module_name: str) -> Dict[str, bool]:
        """
        Check dependency status for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary mapping dependency names to availability status
        """
        dependencies = self.dependencies.get(module_name, [])
        return {dep: dep in self.module_instances for dep in dependencies}
    
    async def restart_module(self, module_name: str) -> bool:
        """
        Restart a specific module.
        
        Args:
            module_name: Name of the module to restart
            
        Returns:
            bool: True if restart successful
        """
        try:
            # Remove from instances
            if module_name in self.module_instances:
                del self.module_instances[module_name]
            
            # Remove from health status
            if module_name in self.health_status:
                del self.health_status[module_name]
            
            # Re-initialize
            return await self._initialize_single_module(module_name)
            
        except Exception as e:
            self._logger.error(f"Failed to restart module {module_name}: {e}")
            return False


# Global module registry instance
module_registry = ModuleRegistry()

# Convenience functions for easy access
async def get_module(module_name: str) -> Optional[Any]:
    """Get a module instance by name."""
    return await module_registry.get_module(module_name)

async def get_module_info(module_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a module."""
    return await module_registry.get_module_info(module_name)

async def list_available_modules() -> List[str]:
    """Get list of all available modules."""
    return await module_registry.list_available_modules()

async def list_initialized_modules() -> List[str]:
    """Get list of all initialized modules."""
    return await module_registry.list_initialized_modules()

async def get_module_health(module_name: str) -> Optional[Dict[str, Any]]:
    """Get health status of a specific module."""
    return await module_registry.get_module_health(module_name)

async def get_all_module_health() -> Dict[str, Dict[str, Any]]:
    """Get health status of all modules."""
    return await module_registry.get_all_module_health()

async def initialize_modules(modules_to_init: Optional[List[str]] = None) -> bool:
    """Initialize specified modules or all available modules."""
    return await module_registry.initialize_modules(modules_to_init)

async def check_module_dependencies(module_name: str) -> Dict[str, bool]:
    """Check dependency status for a specific module."""
    return await module_registry.check_module_dependencies(module_name)

async def restart_module(module_name: str) -> bool:
    """Restart a specific module."""
    return await module_registry.restart_module(module_name)


# Module-specific imports for direct access
try:
    from .certificate_manager import CertificateManager, get_certificate_manager
    from .certificate_manager import Certificate, CertificateStatus, CertificateVisibility, RetentionPolicy
    from .certificate_manager import CertificateVersion, CertificateEvent, EventType, EventStatus
    from .certificate_manager import CertificateExport, ExportFormat, ExportStatus
except ImportError:
    # Module not available yet
    pass

try:
    from .twin_registry import TwinRegistry
except ImportError:
    pass

try:
    from .aasx import AasxProcessor
except ImportError:
    pass

try:
    from .ai_rag import AIRagService
except ImportError:
    pass

try:
    from .kg_neo4j import KnowledgeGraphService
except ImportError:
    pass

try:
    from .physics_modeling import PhysicsModelingService
except ImportError:
    pass

try:
    from .federated_learning import FederatedLearningService
except ImportError:
    pass

try:
    from .data_governance import DataGovernanceService
except ImportError:
    pass


# Export all public symbols
__all__ = [
    # Module registry and management
    'ModuleRegistry',
    'module_registry',
    'get_module',
    'get_module_info',
    'list_available_modules',
    'list_initialized_modules',
    'get_module_health',
    'get_all_module_health',
    'initialize_modules',
    'check_module_dependencies',
    'restart_module',
    
    # Module dependencies
    'MODULE_DEPENDENCIES',
    'MODULE_PRIORITY',
    
    # Certificate Manager (if available)
    'CertificateManager',
    'get_certificate_manager',
    'Certificate',
    'CertificateStatus',
    'CertificateVisibility',
    'RetentionPolicy',
    'CertificateVersion',
    'CertificateEvent',
    'EventType',
    'EventStatus',
    'CertificateExport',
    'ExportFormat',
    'ExportStatus',
]

__version__ = "1.0.0"
__author__ = "AASX Digital Twin Analytics Framework"
