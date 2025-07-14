#!/usr/bin/env python3
"""
AI/RAG System CLI for AASX Data Analysis

This script provides a command-line interface for the enhanced AI/RAG system
that integrates with ETL pipeline, Neo4j knowledge graph, and vector database.
Queries are loaded from a YAML configuration file.

Usage:
    python run_ai_rag.py --query-name quality_issues
    python run_ai_rag.py --category quality_analysis
    python run_ai_rag.py --demo
    python run_ai_rag.py --list-queries
"""

import argparse
import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will use system environment variables

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Also add the current directory for local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from ai_rag.ai_rag import EnhancedRAGSystem
except ImportError as e:
    print(f"❌ Error importing EnhancedRAGSystem: {e}")
    print(f"📁 Backend path: {src_path}")
    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Python path: {sys.path}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryManager:
    """Manages queries loaded from YAML configuration"""
    
    def __init__(self, config_file: str = "config/ai_rag_queries.yaml"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.settings = self.config.get('settings', {})
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if not self.config_file.exists():
                logger.warning(f"Config file not found: {self.config_file}")
                return {}
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def get_query_by_name(self, query_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific query by name"""
        for category, queries in self.config.get('queries', {}).items():
            for query in queries:
                if query.get('name') == query_name:
                    return self._merge_with_defaults(query)
        
        # Check demo queries
        for query in self.config.get('demo_queries', []):
            if query.get('name') == query_name:
                return self._merge_with_defaults(query)
        
        return None
    
    def get_queries_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all queries in a category"""
        queries = self.config.get('queries', {}).get(category, [])
        return [self._merge_with_defaults(q) for q in queries]
    
    def get_demo_queries(self) -> List[Dict[str, Any]]:
        """Get all demo queries"""
        queries = self.config.get('demo_queries', [])
        return [self._merge_with_defaults(q) for q in queries]
    
    def list_all_queries(self) -> Dict[str, List[str]]:
        """List all available queries organized by category"""
        result = {}
        
        # Regular queries by category
        for category, queries in self.config.get('queries', {}).items():
            result[category] = [q.get('name', 'unnamed') for q in queries]
        
        # Demo queries
        demo_queries = [q.get('name', 'unnamed') for q in self.config.get('demo_queries', [])]
        if demo_queries:
            result['demo_queries'] = demo_queries
        
        return result
    
    def _merge_with_defaults(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Merge query with default settings"""
        return {
            'analysis_type': self.settings.get('default_analysis_type', 'general'),
            'collection': self.settings.get('default_collection', 'aasx_assets'),
            'limit': self.settings.get('default_limit', 5),
            **query
        }

def setup_argparse():
    """Setup command line argument parsing"""
    parser = argparse.ArgumentParser(
        description='AI/RAG System for AASX Data Analysis (YAML Query Configuration)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a specific query by name
  python run_ai_rag.py --query-name quality_issues
  
  # Run all queries in a category
  python run_ai_rag.py --category quality_analysis
  
  # Run demo queries
  python run_ai_rag.py --demo
  
  # List all available queries
  python run_ai_rag.py --list-queries
  
  # Index ETL data
  python run_ai_rag.py --index-etl output/etl_results/
  
  # Custom query (overrides YAML)
  python run_ai_rag.py --custom-query "What are the quality issues?" --analysis-type quality
        """
    )
    
    # Query options
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument('--query-name', type=str,
                            help='Name of predefined query to run')
    query_group.add_argument('--category', type=str,
                            help='Run all queries in a category')
    query_group.add_argument('--custom-query', type=str,
                            help='Custom query (overrides YAML configuration)')
    query_group.add_argument('--demo', action='store_true',
                            help='Run demo queries')
    query_group.add_argument('--list-queries', action='store_true',
                            help='List all available queries')
    
    # Analysis options
    parser.add_argument('--analysis-type', type=str, default='general',
                       choices=['general', 'quality', 'risk', 'optimization'],
                       help='Type of analysis (for custom queries)')
    parser.add_argument('--collection', type=str, default='aasx_assets',
                       choices=['aasx_assets', 'aasx_submodels', 'quality_standards', 'compliance_data'],
                       help='Vector collection to search (for custom queries)')
    parser.add_argument('--limit', type=int, default=5,
                       help='Maximum number of results (for custom queries)')
    
    # Indexing options
    parser.add_argument('--index-etl', type=str, 
                       help='Directory containing ETL output to index')
    
    # System options
    parser.add_argument('--stats', action='store_true',
                       help='Show system statistics')
    parser.add_argument('--config-file', type=str, default='config/ai_rag_queries.yaml',
                       help='Path to YAML configuration file')
    
    # Output options
    parser.add_argument('--output', type=str,
                       help='Output file for results (JSON format)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    return parser

async def run_query_by_name(rag_system: EnhancedRAGSystem, query_manager: QueryManager, query_name: str):
    """Run a specific query by name"""
    query_config = query_manager.get_query_by_name(query_name)
    if not query_config:
        print(f"❌ Query '{query_name}' not found")
        return None
    
    print(f"🔍 Running query: {query_name}")
    print(f"📝 Query: {query_config['query']}")
    print(f"📋 Analysis Type: {query_config['analysis_type']}")
    print(f"🔍 Collection: {query_config['collection']}")
    print(f"📊 Limit: {query_config['limit']}")
    if query_config.get('description'):
        print(f"📖 Description: {query_config['description']}")
    print("=" * 60)
    
    return await process_query(rag_system, query_config['query'], query_config['analysis_type'])

async def run_category_queries(rag_system: EnhancedRAGSystem, query_manager: QueryManager, category: str):
    """Run all queries in a category"""
    queries = query_manager.get_queries_by_category(category)
    if not queries:
        print(f"❌ Category '{category}' not found or empty")
        return []
    
    print(f"📂 Running all queries in category: {category}")
    print(f"📊 Found {len(queries)} queries")
    print("=" * 60)
    
    results = []
    for i, query_config in enumerate(queries, 1):
        print(f"\n🔄 Query {i}/{len(queries)}: {query_config['name']}")
        result = await process_query(rag_system, query_config['query'], query_config['analysis_type'])
        if result:
            results.append({
                'query_name': query_config['name'],
                'result': result
            })
    
    return results

async def run_demo_queries(rag_system: EnhancedRAGSystem, query_manager: QueryManager):
    """Run demo queries"""
    queries = query_manager.get_demo_queries()
    if not queries:
        print("❌ No demo queries found")
        return []
    
    print("🎯 Running Demo Queries:")
    print("=" * 60)
    
    results = []
    for i, query_config in enumerate(queries, 1):
        print(f"\n🔄 Demo Query {i}/{len(queries)}: {query_config['name']}")
        result = await process_query(rag_system, query_config['query'], query_config['analysis_type'])
        if result:
            results.append({
                'query_name': query_config['name'],
                'result': result
            })
    
    return results

def list_queries(query_manager: QueryManager):
    """List all available queries"""
    queries = query_manager.list_all_queries()
    
    print("📋 Available Queries:")
    print("=" * 60)
    
    for category, query_names in queries.items():
        print(f"\n📂 {category.replace('_', ' ').title()}:")
        for name in query_names:
            print(f"  • {name}")
    
    print(f"\n📊 Total categories: {len(queries)}")
    total_queries = sum(len(names) for names in queries.values())
    print(f"📊 Total queries: {total_queries}")

async def index_etl_data(rag_system: EnhancedRAGSystem, etl_dir: str):
    """Index ETL data into vector database"""
    logger.info(f"Indexing ETL data from: {etl_dir}")
    
    try:
        stats = await rag_system.index_etl_data(etl_dir)
        
        print("\n📊 Indexing Results:")
        print(f"  Assets indexed: {stats['assets_indexed']}")
        print(f"  Submodels indexed: {stats['submodels_indexed']}")
        print(f"  Files processed: {stats['files_processed']}")
        print(f"  Errors: {stats['errors']}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error indexing ETL data: {e}")
        raise

async def process_query(rag_system: EnhancedRAGSystem, query: str, analysis_type: str = 'general'):
    """Process a query with the RAG system"""
    logger.info(f"Processing query: {query}")
    logger.info(f"Analysis type: {analysis_type}")
    
    try:
        # Generate RAG response
        response = await rag_system.generate_rag_response(query, analysis_type)
        
        print(f"\n🤖 RAG Response ({analysis_type.upper()}):")
        print("=" * 50)
        print(response.get('response', 'No response generated'))
        print("\n📋 Metadata:")
        metadata = response.get('metadata', {})
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        print(f"❌ Error: {e}")
        return None

async def get_system_stats(rag_system: EnhancedRAGSystem):
    """Get system statistics"""
    logger.info("Getting system statistics")
    
    try:
        stats = await rag_system.get_system_stats()
        
        print("\n📈 System Statistics:")
        print("=" * 50)
        print(f"Neo4j Connected: {'✅' if stats['neo4j_connected'] else '❌'}")
        print(f"OpenAI Available: {'✅' if stats['openai_available'] else '❌'}")
        print(f"Total Indexed: {stats['total_indexed']}")
        
        print("\n📊 Collection Statistics:")
        for collection, info in stats['collections'].items():
            if 'error' in info:
                print(f"  {collection}: ❌ {info['error']}")
            else:
                print(f"  {collection}: {info['vectors_count']} vectors, {info['points_count']} points")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise

async def main():
    """Main function"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 60)
    print("🚀 AI/RAG System for AASX Data Analysis")
    print("📄 Using YAML Query Configuration")
    print("=" * 60)
    
    try:
        # Initialize query manager
        query_manager = QueryManager(args.config_file)
        
        # Initialize RAG system
        logger.info("Initializing RAG system...")
        rag_system = EnhancedRAGSystem()
        
        results = {}
        
        # List queries if requested
        if args.list_queries:
            list_queries(query_manager)
            return
        
        # Index ETL data if requested
        if args.index_etl:
            etl_stats = await index_etl_data(rag_system, args.index_etl)
            results['indexing'] = etl_stats
        
        # Get system stats if requested
        if args.stats:
            stats = await get_system_stats(rag_system)
            results['stats'] = stats
        
        # Process queries based on arguments
        if args.query_name:
            result = await run_query_by_name(rag_system, query_manager, args.query_name)
            if result:
                results['query_response'] = result
        
        elif args.category:
            category_results = await run_category_queries(rag_system, query_manager, args.category)
            results['category_results'] = category_results
        
        elif args.demo:
            demo_results = await run_demo_queries(rag_system, query_manager)
            results['demo_results'] = demo_results
        
        elif args.custom_query:
            print(f"🔍 Running custom query: {args.custom_query}")
            result = await process_query(rag_system, args.custom_query, args.analysis_type)
            if result:
                results['custom_query_response'] = result
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results saved to: {args.output}")
        
        print("\n" + "=" * 60)
        print("✅ AI/RAG system operation completed successfully")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 