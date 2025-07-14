#!/usr/bin/env python3
"""
Test Data Migration Script
Tests the data migration from ETL pipeline's ChromaDB to AI/RAG system's Qdrant
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ai_rag.data_migration import DataMigrationManager
from ai_rag.ai_rag import EnhancedRAGSystem

async def test_migration_status():
    """Test migration status and data availability"""
    print("🔍 Testing Data Migration Status")
    print("=" * 60)
    
    try:
        # Initialize migration manager
        migration_manager = DataMigrationManager()
        
        # Get migration status
        status = migration_manager.get_migration_status()
        
        print(f"📊 Migration Status:")
        print(f"  ETL Pipeline Collections: {status.get('chromadb_collections', [])}")
        print(f"  AI/RAG System Collections: {status.get('qdrant_collections', [])}")
        print(f"  Pending Migrations: {status.get('pending_migrations', [])}")
        print(f"  Migration Needed: {status.get('migration_needed', False)}")
        
        return status
        
    except Exception as e:
        print(f"❌ Error testing migration status: {e}")
        return None

async def test_data_migration():
    """Test actual data migration"""
    print("\n🔄 Testing Data Migration")
    print("=" * 60)
    
    try:
        # Initialize migration manager
        migration_manager = DataMigrationManager()
        
        # Check if migration is needed
        status = migration_manager.get_migration_status()
        
        if not status.get('migration_needed', False):
            print("✅ No migration needed - data already synchronized")
            return True
        
        # Perform migration
        print("🔄 Starting migration...")
        result = migration_manager.migrate_all_collections()
        
        print(f"📊 Migration Result:")
        print(f"  Status: {result['status']}")
        print(f"  Migrated Collections: {result.get('migrated_collections', 0)}")
        print(f"  Total Collections: {result.get('total_collections', 0)}")
        
        if result['status'] == 'completed':
            print("✅ Migration completed successfully!")
            return True
        else:
            print(f"❌ Migration failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

async def test_rag_system_data():
    """Test RAG system with migrated data"""
    print("\n🤖 Testing RAG System with Migrated Data")
    print("=" * 60)
    
    try:
        # Initialize RAG system
        rag_system = EnhancedRAGSystem()
        
        # Get data status
        data_status = await rag_system.get_data_status()
        
        print(f"📊 RAG System Data Status:")
        print(f"  ETL Pipeline: {data_status.get('etl_pipeline', {})}")
        print(f"  AI/RAG System: {data_status.get('ai_rag_system', {})}")
        
        # Test search functionality
        test_queries = [
            "quality control",
            "manufacturing process",
            "asset management"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            try:
                results = await rag_system.search_aasx_data(query, limit=3)
                print(f"  Found {len(results)} results")
                
                for i, result in enumerate(results, 1):
                    payload = result['payload']
                    score = result['score']
                    print(f"  {i}. Score: {score:.3f} - {payload.get('content', 'No content')[:50]}...")
                    
            except Exception as e:
                print(f"  ❌ Search failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RAG system: {e}")
        return False

async def test_sync_functionality():
    """Test the sync functionality"""
    print("\n🔄 Testing Sync Functionality")
    print("=" * 60)
    
    try:
        # Initialize RAG system
        rag_system = EnhancedRAGSystem()
        
        # Test sync
        sync_result = await rag_system.sync_etl_data()
        
        print(f"📊 Sync Result:")
        print(f"  Status: {sync_result['status']}")
        print(f"  Message: {sync_result['message']}")
        
        if sync_result['status'] == 'success':
            print("✅ Sync completed successfully!")
            return True
        else:
            print(f"❌ Sync failed: {sync_result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        return False

async def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="Test data migration functionality")
    parser.add_argument("--test", choices=["status", "migration", "rag", "sync", "all"], 
                       default="all", help="Test to run")
    args = parser.parse_args()
    
    print("🚀 Data Migration Test Suite")
    print("=" * 60)
    
    results = {}
    
    if args.test in ["status", "all"]:
        results['status'] = await test_migration_status()
    
    if args.test in ["migration", "all"]:
        results['migration'] = await test_data_migration()
    
    if args.test in ["rag", "all"]:
        results['rag'] = await test_rag_system_data()
    
    if args.test in ["sync", "all"]:
        results['sync'] = await test_sync_functionality()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 