#!/usr/bin/env python3
"""
Main Entry Point for AASX Digital Twin Analytics Framework
Comprehensive framework for processing AASX files and building digital twin analytics
"""

import os
import sys
import logging
import argparse
import signal
import time
from pathlib import Path
import uvicorn

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AASXDigitalTwinFramework:
    """AASX Digital Twin Analytics Framework - Main Controller"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.webapp_dir = self.project_root / "webapp"
        self.running = False
        
    def check_environment(self) -> bool:
        """Check basic environment setup"""
        logger.info("🔍 Checking environment setup...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            logger.info(f"✅ Python {python_version.major}.{python_version.minor} detected")
        else:
            logger.error(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        
        # Check webapp directory
        if not self.webapp_dir.exists():
            logger.error("❌ Webapp directory not found!")
            return False
        
        # Check app.py
        app_path = self.webapp_dir / "app.py"
        if not app_path.exists():
            logger.error("❌ app.py not found in webapp directory!")
            return False
        
        # Check src directory (renamed from backend)
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            logger.error("❌ src directory not found! (renamed from backend)")
            return False
        
        logger.info("✅ Environment check passed")
        return True
    
    def check_dependencies(self) -> bool:
        """Check required Python packages"""
        logger.info("📦 Checking dependencies...")
        
        # Package name to import name mapping
        package_imports = {
            'fastapi': 'fastapi',
            'uvicorn': 'uvicorn', 
            'jinja2': 'jinja2',
            'python-multipart': 'multipart',
            'qdrant-client': 'qdrant_client',
            'openai': 'openai',
            'neo4j': 'neo4j',
            'pydantic': 'pydantic',
            'pyyaml': 'yaml',
            'requests': 'requests',
            'numpy': 'numpy',
            'pandas': 'pandas',
            'scikit-learn': 'sklearn'
        }
        
        missing_packages = []
        for package, import_name in package_imports.items():
            try:
                __import__(import_name)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
            logger.info("💡 Install with: pip install " + " ".join(missing_packages))
            return False
        
        logger.info("✅ All required packages available")
        return True
    
    def check_services(self) -> bool:
        """Check backend services (non-blocking)"""
        logger.info("🔌 Checking backend services...")
        
        services_status = {}
        
        # Check Neo4j
        try:
            from neo4j import GraphDatabase
            # Use environment variables with defaults for Docker setup
            neo4j_uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7688')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'Neo4j123')
            
            logger.info(f"🔌 Connecting to Neo4j at {neo4j_uri}")
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            driver.verify_connectivity()
            driver.close()
            services_status['Neo4j'] = "✅ Connected"
            logger.info("✅ Neo4j connection successful")
        except Exception as e:
            services_status['Neo4j'] = "⚠️  Connection failed"
            logger.warning(f"⚠️  Neo4j connection failed: {e}")
        
        # Check Qdrant
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient("localhost", port=6333)
            client.get_collections()
            services_status['Qdrant'] = "✅ Connected"
            logger.info("✅ Qdrant connection successful")
        except Exception as e:
            services_status['Qdrant'] = "⚠️  Connection failed"
            logger.warning(f"⚠️  Qdrant connection failed: {e}")
        
        # Check OpenAI
        if os.getenv('OPENAI_API_KEY'):
            services_status['OpenAI'] = "✅ Configured"
            logger.info("✅ OpenAI API key configured")
        else:
            services_status['OpenAI'] = "⚠️  Not configured"
            logger.warning("⚠️  OpenAI API key not found")
        
        # Log summary
        logger.info("📊 Service Status Summary:")
        for service, status in services_status.items():
            logger.info(f"   {service}: {status}")
        
        return True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("📡 Shutdown signal received")
        self.running = False
    
    def start_webapp(self, host: str = "0.0.0.0", port: int = 8000) -> bool:
        """Start the FastAPI webapp"""
        try:
            # Display startup information
            logger.info("🚀 Starting AASX Digital Twin Analytics Framework...")
            
            # Display startup information
            logger.info("")
            logger.info("📋 Available endpoints:")
            logger.info(f"   • Home: http://localhost:{port}/")
            logger.info(f"   • AASX ETL Pipeline: http://localhost:{port}/aasx")
            logger.info(f"   • Knowledge Graph: http://localhost:{port}/kg-neo4j")
            logger.info(f"   • AI/RAG System: http://localhost:{port}/ai-rag")
            logger.info(f"   • Twin Registry: http://localhost:{port}/twin-registry")
            logger.info(f"   • Certificates: http://localhost:{port}/certificates")
            logger.info(f"   • Analytics: http://localhost:{port}/analytics")
            logger.info(f"   • API Docs: http://localhost:{port}/docs")
            logger.info(f"   • Health: http://localhost:{port}/health")
            logger.info("")
            logger.info("🔧 Quick Start:")
            logger.info(f"   1. Open http://localhost:{port}/ in your browser")
            logger.info("   2. Start with AASX ETL Pipeline to process files")
            logger.info("   3. Explore the Knowledge Graph for relationships")
            logger.info("   4. Use AI/RAG for intelligent analysis")
            logger.info("   5. Manage digital twins in the registry")
            logger.info("   6. View analytics and insights")
            logger.info("")
            logger.info("🛑 Press Ctrl+C to stop the server")
            logger.info("")
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            self.running = True
            
            # Start uvicorn server
            uvicorn.run(
                "webapp.app:app",
                host=host,
                port=port,
                reload=False,  # Disable reload for production
                log_level="info"
            )
            
            return True
            
        except KeyboardInterrupt:
            logger.info("📡 Keyboard interrupt received")
            return True
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, skip_checks: bool = False) -> bool:
        """Run the AASX Digital Twin Analytics Framework"""
        try:
            # Environment check
            if not skip_checks and not self.check_environment():
                return False
            
            # Dependency check
            if not skip_checks and not self.check_dependencies():
                return False
            
            # Service check (non-blocking)
            if not skip_checks:
                self.check_services()
            
            # Start webapp
            return self.start_webapp(host, port)
            
        except Exception as e:
            logger.error(f"❌ Framework startup failed: {e}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AASX Digital Twin Analytics Framework - ETL, Knowledge Graph & AI/RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with default settings
  python main.py --port 8080        # Start on port 8080
  python main.py --host 127.0.0.1   # Bind to localhost only
  python main.py --skip-checks      # Skip dependency checks
  python main.py --check-only       # Only check environment
        """
    )
    
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the webapp to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the webapp on")
    parser.add_argument("--skip-checks", action="store_true", help="Skip dependency and service checks")
    parser.add_argument("--check-only", action="store_true", help="Only check environment and dependencies")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    framework = AASXDigitalTwinFramework()
    
    if args.check_only:
        logger.info("🔍 Running environment checks only...")
        success = (
            framework.check_environment() and
            framework.check_dependencies() and
            framework.check_services()
        )
        sys.exit(0 if success else 1)
    else:
        success = framework.run(args.host, args.port, args.skip_checks)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 