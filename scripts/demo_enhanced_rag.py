#!/usr/bin/env python3
"""
Enhanced AI/RAG System Demo Script
Demonstrates the capabilities of the enhanced RAG system
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

# Import with correct module path
sys.path.append(str(Path(__file__).parent.parent / 'src' / 'ai-rag'))
from ai_rag import EnhancedRAGSystem

class EnhancedRAGDemo:
    """Demo class for the enhanced AI/RAG system"""
    
    def __init__(self):
        self.rag_system = None
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f"🎯 {title}")
        print("="*60)
    
    def print_section(self, title: str):
        """Print a section header"""
        print(f"\n📋 {title}")
        print("-" * 40)
    
    async def initialize_system(self):
        """Initialize the RAG system"""
        self.print_header("Initializing Enhanced AI/RAG System")
        
        try:
            self.rag_system = EnhancedRAGSystem()
            print("✅ RAG system initialized successfully")
            
            # Show configuration
            config = self.rag_system.config
            print(f"🔧 Configuration:")
            print(f"   - Qdrant URL: {config.get('qdrant_url', 'Not set')}")
            print(f"   - Neo4j URI: {config.get('neo4j_uri', 'Not set')}")
            print(f"   - OpenAI: {'Configured' if config.get('openai_api_key') else 'Not configured'}")
            print(f"   - ETL Output: {config.get('etl_output_dir', 'Not set')}")
            
        except Exception as e:
            print(f"❌ Failed to initialize RAG system: {e}")
            return False
        
        return True
    
    async def demo_etl_indexing(self):
        """Demo ETL data indexing"""
        self.print_section("ETL Data Indexing Demo")
        
        try:
            print("🔄 Indexing ETL data...")
            stats = await self.rag_system.index_etl_data()
            
            print(f"✅ Indexing completed:")
            print(f"   - Assets indexed: {stats['assets_indexed']}")
            print(f"   - Submodels indexed: {stats['submodels_indexed']}")
            print(f"   - Files processed: {stats['files_processed']}")
            print(f"   - Errors: {stats['errors']}")
            
        except Exception as e:
            print(f"❌ ETL indexing failed: {e}")
    
    async def demo_vector_search(self):
        """Demo vector search capabilities"""
        self.print_section("Vector Search Demo")
        
        # Demo queries
        demo_queries = [
            ("servo motor", "aasx_assets"),
            ("technical data", "aasx_submodels"),
            ("hydrogen", "aasx_assets"),
            ("manufacturing", "aasx_submodels")
        ]
        
        for query, collection in demo_queries:
            print(f"\n🔍 Searching for '{query}' in {collection}...")
            
            try:
                results = await self.rag_system.search_aasx_data(query, collection, 3)
                
                if results:
                    print(f"✅ Found {len(results)} results:")
                    for i, result in enumerate(results[:2], 1):
                        payload = result['payload']
                        score = result['score']
                        print(f"   {i}. {payload.get('id_short', 'Unknown')} (Score: {score:.3f})")
                        print(f"      Description: {payload.get('description', 'No description')[:100]}...")
                else:
                    print(f"ℹ️  No results found for '{query}'")
                    
            except Exception as e:
                print(f"❌ Search failed: {e}")
    
    async def demo_graph_context(self):
        """Demo graph context retrieval"""
        self.print_section("Graph Context Demo")
        
        if not self.rag_system.neo4j_manager:
            print("ℹ️  Neo4j not configured, skipping graph context demo")
            return
        
        demo_queries = ["servo", "hydrogen", "manufacturing", "quality"]
        
        for query in demo_queries:
            print(f"\n🌐 Getting graph context for '{query}'...")
            
            try:
                context = await self.rag_system.get_graph_context(query)
                
                if 'error' in context:
                    print(f"❌ Graph context error: {context['error']}")
                else:
                    assets = context.get('assets', [])
                    submodels = context.get('submodels', [])
                    metrics = context.get('quality_metrics', [])
                    
                    print(f"✅ Graph context retrieved:")
                    print(f"   - Assets: {len(assets)}")
                    print(f"   - Submodels: {len(submodels)}")
                    print(f"   - Quality metrics: {len(metrics)}")
                    
                    if assets:
                        print(f"   - Sample asset: {assets[0].get('id_short', 'Unknown')}")
                    
            except Exception as e:
                print(f"❌ Graph context failed: {e}")
    
    async def demo_rag_responses(self):
        """Demo RAG response generation"""
        self.print_section("RAG Response Generation Demo")
        
        # Demo scenarios
        demo_scenarios = [
            {
                "query": "Tell me about the servo motor asset and its specifications",
                "type": "general",
                "description": "General asset information"
            },
            {
                "query": "What is the quality level of the current assets?",
                "type": "quality",
                "description": "Quality assessment"
            },
            {
                "query": "What are the main risk factors for the hydrogen filling station?",
                "type": "risk",
                "description": "Risk analysis"
            },
            {
                "query": "How can we optimize the 3D printer performance?",
                "type": "optimization",
                "description": "Optimization recommendations"
            }
        ]
        
        for scenario in demo_scenarios:
            print(f"\n🤖 {scenario['description']}:")
            print(f"Query: '{scenario['query']}'")
            print(f"Type: {scenario['type']}")
            
            try:
                response = await self.rag_system.generate_rag_response(
                    scenario['query'], scenario['type']
                )
                
                if 'error' in response:
                    print(f"❌ RAG response error: {response['error']}")
                else:
                    print(f"✅ Response generated:")
                    print(f"   Model: {response.get('model', 'Unknown')}")
                    print(f"   Confidence: {response.get('confidence', 0):.2f}")
                    print(f"   Response: {response.get('response', 'No response')[:200]}...")
                    
                    # Show metadata
                    metadata = response.get('metadata', {})
                    if metadata:
                        print(f"   Vector results: {metadata.get('vector_results', 0)}")
                        print(f"   Graph context available: {metadata.get('graph_context_available', False)}")
                
            except Exception as e:
                print(f"❌ RAG response failed: {e}")
    
    async def demo_system_capabilities(self):
        """Demo overall system capabilities"""
        self.print_section("System Capabilities Demo")
        
        try:
            # Get system stats
            stats = await self.rag_system.get_system_stats()
            
            if 'error' in stats:
                print(f"❌ Failed to get system stats: {stats['error']}")
                return
            
            print("📊 System Statistics:")
            print(f"   - Total indexed items: {stats.get('total_indexed', 0)}")
            print(f"   - Neo4j connected: {stats.get('neo4j_connected', False)}")
            print(f"   - OpenAI available: {stats.get('openai_available', False)}")
            
            # Show collection details
            collections = stats.get('collections', {})
            print(f"\n🗂️  Collection Details:")
            for collection_name, collection_stats in collections.items():
                if 'error' not in collection_stats:
                    vectors = collection_stats.get('vectors_count', 0)
                    points = collection_stats.get('points_count', 0)
                    print(f"   - {collection_name}: {vectors} vectors, {points} points")
                else:
                    print(f"   - {collection_name}: Error - {collection_stats['error']}")
            
            # Demo integration workflow
            print(f"\n🔄 Integration Workflow Demo:")
            print("1. Vector search for relevant data")
            print("2. Retrieve graph context")
            print("3. Generate AI-powered response")
            print("4. Provide insights and recommendations")
            
        except Exception as e:
            print(f"❌ System capabilities demo failed: {e}")
    
    async def run_demo(self):
        """Run the complete demo"""
        self.print_header("Enhanced AI/RAG System Demo")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize system
        if not await self.initialize_system():
            return
        
        # Run demos
        await self.demo_etl_indexing()
        await self.demo_vector_search()
        await self.demo_graph_context()
        await self.demo_rag_responses()
        await self.demo_system_capabilities()
        
        # Summary
        self.print_header("Demo Complete")
        print("🎉 Enhanced AI/RAG System demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ ETL data integration and indexing")
        print("✅ Vector similarity search")
        print("✅ Neo4j knowledge graph integration")
        print("✅ AI-powered response generation")
        print("✅ Multiple analysis types (general, quality, risk, optimization)")
        print("✅ System monitoring and statistics")

async def main():
    """Main demo function"""
    demo = EnhancedRAGDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main()) 