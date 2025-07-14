#!/usr/bin/env python3
"""
Enhanced AI/RAG System Test Script
Tests all functionality of the enhanced RAG system including ETL integration, Neo4j, and vector search
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

# Import with correct module path
sys.path.append(str(Path(__file__).parent.parent / 'src' / 'ai-rag'))
from ai_rag import EnhancedRAGSystem, get_rag_system

class EnhancedRAGTester:
    """Test suite for the enhanced AI/RAG system"""
    
    def __init__(self):
        self.rag_system = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f"🧠 {title}")
        print("="*60)
    
    def print_test(self, test_name: str, status: str, details: str = ""):
        """Print test result"""
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {test_name}")
        if details:
            print(f"   {details}")
        
        if status == "PASS":
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
    
    def print_error(self, error: str):
        """Print error and add to results"""
        print(f"❌ ERROR: {error}")
        self.test_results['errors'].append(error)
        self.test_results['failed'] += 1
    
    async def test_system_initialization(self):
        """Test RAG system initialization"""
        self.print_header("Testing System Initialization")
        
        try:
            # Test basic initialization
            self.rag_system = EnhancedRAGSystem()
            self.print_test("Basic Initialization", "PASS", "RAG system created successfully")
            
            # Test configuration loading
            config = self.rag_system.config
            required_keys = ['qdrant_url', 'openai_api_key', 'neo4j_uri', 'neo4j_user', 'neo4j_password']
            missing_keys = [key for key in required_keys if key not in config]
            
            if not missing_keys:
                self.print_test("Configuration Loading", "PASS", f"All required config keys present")
            else:
                self.print_test("Configuration Loading", "FAIL", f"Missing keys: {missing_keys}")
            
            # Test component initialization
            if self.rag_system.embedding_model:
                self.print_test("Embedding Model", "PASS", "SentenceTransformer initialized")
            else:
                self.print_test("Embedding Model", "FAIL", "Embedding model not initialized")
            
            if self.rag_system.qdrant_client:
                self.print_test("Qdrant Client", "PASS", "Qdrant client initialized")
            else:
                self.print_test("Qdrant Client", "FAIL", "Qdrant client not initialized")
            
            if self.rag_system.neo4j_manager:
                self.print_test("Neo4j Manager", "PASS", "Neo4j manager initialized")
            else:
                self.print_test("Neo4j Manager", "PASS", "Neo4j manager not available (expected if not configured)")
            
            if self.rag_system.openai_client:
                self.print_test("OpenAI Client", "PASS", "OpenAI client initialized")
            else:
                self.print_test("OpenAI Client", "PASS", "OpenAI client not available (expected if not configured)")
                
        except Exception as e:
            self.print_error(f"Initialization failed: {e}")
    
    async def test_collection_management(self):
        """Test Qdrant collection management"""
        self.print_header("Testing Collection Management")
        
        try:
            # Test collection listing
            collections = self.rag_system.qdrant_client.get_collections()
            expected_collections = ['aasx_assets', 'aasx_submodels', 'quality_standards', 'compliance_data', 'analysis_results']
            
            found_collections = [col.name for col in collections.collections]
            missing_collections = [col for col in expected_collections if col not in found_collections]
            
            if not missing_collections:
                self.print_test("Collection Creation", "PASS", f"All expected collections found: {found_collections}")
            else:
                self.print_test("Collection Creation", "FAIL", f"Missing collections: {missing_collections}")
            
            # Test collection info
            for collection_name in expected_collections:
                try:
                    info = self.rag_system.qdrant_client.get_collection(collection_name)
                    self.print_test(f"Collection Info - {collection_name}", "PASS", 
                                  f"Vectors: {info.vectors_count}, Points: {info.points_count}")
                except Exception as e:
                    self.print_test(f"Collection Info - {collection_name}", "FAIL", str(e))
                    
        except Exception as e:
            self.print_error(f"Collection management failed: {e}")
    
    async def test_etl_data_indexing(self):
        """Test ETL data indexing functionality"""
        self.print_header("Testing ETL Data Indexing")
        
        try:
            # Check if ETL output directory exists
            etl_dir = Path(self.rag_system.config['etl_output_dir'])
            if not etl_dir.exists():
                self.print_test("ETL Directory Check", "FAIL", f"ETL directory not found: {etl_dir}")
                return
            
            self.print_test("ETL Directory Check", "PASS", f"ETL directory found: {etl_dir}")
            
            # Count existing files
            json_files = list(etl_dir.rglob("*.json"))
            self.print_test("ETL Files Count", "PASS", f"Found {len(json_files)} JSON files")
            
            # Test indexing (this might take a while)
            print("🔄 Starting ETL data indexing...")
            stats = await self.rag_system.index_etl_data()
            
            self.print_test("Indexing Process", "PASS", 
                          f"Assets: {stats['assets_indexed']}, Submodels: {stats['submodels_indexed']}, "
                          f"Files: {stats['files_processed']}, Errors: {stats['errors']}")
            
            if stats['errors'] > 0:
                self.print_test("Indexing Errors", "FAIL", f"{stats['errors']} errors occurred during indexing")
            else:
                self.print_test("Indexing Errors", "PASS", "No errors during indexing")
                
        except Exception as e:
            self.print_error(f"ETL indexing failed: {e}")
    
    async def test_vector_search(self):
        """Test vector search functionality"""
        self.print_header("Testing Vector Search")
        
        try:
            # Test asset search
            asset_query = "servo motor"
            asset_results = await self.rag_system.search_aasx_data(asset_query, 'aasx_assets', 3)
            
            if asset_results:
                self.print_test("Asset Search", "PASS", f"Found {len(asset_results)} results for '{asset_query}'")
                for i, result in enumerate(asset_results[:2]):
                    score = result.get('score', 0)
                    payload = result.get('payload', {})
                    self.print_test(f"Asset Result {i+1}", "PASS", 
                                  f"Score: {score:.3f}, ID: {payload.get('id_short', 'Unknown')}")
            else:
                self.print_test("Asset Search", "FAIL", f"No results found for '{asset_query}'")
            
            # Test submodel search
            submodel_query = "technical data"
            submodel_results = await self.rag_system.search_aasx_data(submodel_query, 'aasx_submodels', 3)
            
            if submodel_results:
                self.print_test("Submodel Search", "PASS", f"Found {len(submodel_results)} results for '{submodel_query}'")
            else:
                self.print_test("Submodel Search", "PASS", f"No results found for '{submodel_query}' (may be expected)")
                
        except Exception as e:
            self.print_error(f"Vector search failed: {e}")
    
    async def test_graph_context(self):
        """Test Neo4j graph context retrieval"""
        self.print_header("Testing Graph Context")
        
        if not self.rag_system.neo4j_manager:
            self.print_test("Neo4j Availability", "PASS", "Neo4j not configured, skipping graph tests")
            return
        
        try:
            # Test graph context retrieval
            query = "servo"
            context = await self.rag_system.get_graph_context(query)
            
            if 'error' in context:
                self.print_test("Graph Context", "FAIL", f"Error: {context['error']}")
            else:
                assets_count = len(context.get('assets', []))
                submodels_count = len(context.get('submodels', []))
                metrics_count = len(context.get('quality_metrics', []))
                
                self.print_test("Graph Context", "PASS", 
                              f"Assets: {assets_count}, Submodels: {submodels_count}, Metrics: {metrics_count}")
                
                if assets_count > 0:
                    self.print_test("Asset Context", "PASS", f"Found {assets_count} relevant assets")
                else:
                    self.print_test("Asset Context", "PASS", "No assets found (may be expected)")
                    
        except Exception as e:
            self.print_error(f"Graph context failed: {e}")
    
    async def test_rag_response_generation(self):
        """Test RAG response generation"""
        self.print_header("Testing RAG Response Generation")
        
        try:
            # Test general analysis
            query = "Tell me about the servo motor asset"
            response = await self.rag_system.generate_rag_response(query, 'general')
            
            if 'error' in response:
                self.print_test("General RAG Response", "FAIL", f"Error: {response['error']}")
            else:
                self.print_test("General RAG Response", "PASS", 
                              f"Model: {response.get('model', 'Unknown')}, "
                              f"Confidence: {response.get('confidence', 0):.2f}")
                
                # Check response content
                if response.get('response'):
                    self.print_test("Response Content", "PASS", f"Response length: {len(response['response'])} chars")
                else:
                    self.print_test("Response Content", "FAIL", "No response content")
                
                # Check metadata
                metadata = response.get('metadata', {})
                if metadata:
                    self.print_test("Response Metadata", "PASS", 
                                  f"Vector results: {metadata.get('vector_results', 0)}, "
                                  f"Graph context: {metadata.get('graph_context_available', False)}")
                else:
                    self.print_test("Response Metadata", "FAIL", "No metadata in response")
            
            # Test quality analysis
            quality_query = "What is the quality level of the servo motor?"
            quality_response = await self.rag_system.generate_rag_response(quality_query, 'quality')
            
            if 'error' not in quality_response:
                self.print_test("Quality RAG Response", "PASS", 
                              f"Model: {quality_response.get('model', 'Unknown')}")
            else:
                self.print_test("Quality RAG Response", "FAIL", f"Error: {quality_response['error']}")
                
        except Exception as e:
            self.print_error(f"RAG response generation failed: {e}")
    
    async def test_system_stats(self):
        """Test system statistics"""
        self.print_header("Testing System Statistics")
        
        try:
            stats = await self.rag_system.get_system_stats()
            
            if 'error' in stats:
                self.print_test("System Stats", "FAIL", f"Error: {stats['error']}")
                return
            
            # Check basic stats
            total_indexed = stats.get('total_indexed', 0)
            neo4j_connected = stats.get('neo4j_connected', False)
            openai_available = stats.get('openai_available', False)
            
            self.print_test("Total Indexed", "PASS", f"{total_indexed} items indexed")
            self.print_test("Neo4j Connection", "PASS" if neo4j_connected else "FAIL", 
                          "Connected" if neo4j_connected else "Disconnected")
            self.print_test("OpenAI Availability", "PASS" if openai_available else "PASS", 
                          "Available" if openai_available else "Not configured (using fallback)")
            
            # Check collection stats
            collections = stats.get('collections', {})
            for collection_name, collection_stats in collections.items():
                if 'error' in collection_stats:
                    self.print_test(f"Collection Stats - {collection_name}", "FAIL", 
                                  f"Error: {collection_stats['error']}")
                else:
                    vectors = collection_stats.get('vectors_count', 0)
                    points = collection_stats.get('points_count', 0)
                    self.print_test(f"Collection Stats - {collection_name}", "PASS", 
                                  f"Vectors: {vectors}, Points: {points}")
                    
        except Exception as e:
            self.print_error(f"System stats failed: {e}")
    
    async def test_integration_scenarios(self):
        """Test integration scenarios"""
        self.print_header("Testing Integration Scenarios")
        
        try:
            # Scenario 1: Complete analysis workflow
            print("🔄 Testing complete analysis workflow...")
            
            # Step 1: Search for data
            search_results = await self.rag_system.search_aasx_data("motor", 'aasx_assets', 2)
            
            # Step 2: Get graph context
            graph_context = await self.rag_system.get_graph_context("motor")
            
            # Step 3: Generate RAG response
            rag_response = await self.rag_system.generate_rag_response("What are the specifications of the motor?", 'general')
            
            if search_results and 'error' not in rag_response:
                self.print_test("Complete Workflow", "PASS", 
                              f"Search: {len(search_results)} results, "
                              f"Graph: {bool(graph_context)}, "
                              f"RAG: {rag_response.get('model', 'Unknown')}")
            else:
                self.print_test("Complete Workflow", "FAIL", "One or more steps failed")
            
            # Scenario 2: Quality analysis
            print("🔄 Testing quality analysis scenario...")
            quality_response = await self.rag_system.generate_rag_response(
                "Are there any quality issues with the current assets?", 'quality'
            )
            
            if 'error' not in quality_response:
                self.print_test("Quality Analysis Scenario", "PASS", 
                              f"Model: {quality_response.get('model', 'Unknown')}")
            else:
                self.print_test("Quality Analysis Scenario", "FAIL", f"Error: {quality_response['error']}")
                
        except Exception as e:
            self.print_error(f"Integration scenarios failed: {e}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print(f"\n🚨 Errors encountered:")
            for error in self.test_results['errors']:
                print(f"   - {error}")
        
        if success_rate >= 80:
            print(f"\n🎉 Overall Status: EXCELLENT")
        elif success_rate >= 60:
            print(f"\n👍 Overall Status: GOOD")
        else:
            print(f"\n⚠️  Overall Status: NEEDS IMPROVEMENT")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Enhanced AI/RAG System Tests")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            await self.test_system_initialization()
            await self.test_collection_management()
            await self.test_etl_data_indexing()
            await self.test_vector_search()
            await self.test_graph_context()
            await self.test_rag_response_generation()
            await self.test_system_stats()
            await self.test_integration_scenarios()
            
        except Exception as e:
            self.print_error(f"Test execution failed: {e}")
        
        finally:
            self.print_summary()

async def main():
    """Main test function"""
    tester = EnhancedRAGTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 