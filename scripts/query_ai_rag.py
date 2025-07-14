#!/usr/bin/env python3
"""
Simple AI/RAG Query Runner
Quick script to run queries against the AI/RAG system
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ai_rag.ai_rag import EnhancedRAGSystem

async def run_query(query: str, analysis_type: str = "general", collection: str = "aasx_assets", limit: int = 5):
    """Run a single query against the AI/RAG system"""
    print(f"🤖 AI/RAG Query: {query}")
    print(f"📋 Analysis Type: {analysis_type}")
    print(f"🔍 Collection: {collection}")
    print("=" * 60)
    
    try:
        # Initialize RAG system
        rag_system = EnhancedRAGSystem()
        
        # Generate response
        response = await rag_system.generate_rag_response(query, analysis_type)
        
        print(f"\n💬 Response:")
        print(response.get('response', 'No response generated'))
        
        print(f"\n📊 Metadata:")
        metadata = response.get('metadata', {})
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        # Also do vector search
        print(f"\n🔍 Vector Search Results ({collection}):")
        vector_results = await rag_system.search_aasx_data(query, collection, limit)
        
        if vector_results:
            for i, result in enumerate(vector_results, 1):
                payload = result['payload']
                score = result['score']
                print(f"\n{i}. Score: {score:.3f}")
                print(f"   ID: {payload.get('id_short', 'Unknown')}")
                print(f"   Description: {payload.get('description', 'No description')[:100]}...")
        else:
            print("No vector search results found")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Quick AI/RAG Query Runner')
    parser.add_argument('query', help='Query to process')
    parser.add_argument('--analysis-type', default='general', 
                       choices=['general', 'quality', 'risk', 'optimization'],
                       help='Type of analysis')
    parser.add_argument('--collection', default='aasx_assets',
                       choices=['aasx_assets', 'aasx_submodels', 'quality_standards', 'compliance_data'],
                       help='Vector collection to search')
    parser.add_argument('--limit', type=int, default=5, help='Maximum results')
    
    args = parser.parse_args()
    
    asyncio.run(run_query(args.query, args.analysis_type, args.collection, args.limit))

if __name__ == "__main__":
    main() 