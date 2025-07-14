#!/usr/bin/env python3
"""
Vector Database Backup Script

This script creates local backups of the global Qdrant vector database,
including collections metadata and optional point data export.

Usage:
    python scripts/backup_vector_db.py [--include-points] [--backup-dir BACKUP_DIR]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Any, Optional

def check_qdrant_connection(url: str = "http://localhost:6333") -> bool:
    """Check if Qdrant server is accessible"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_collections(url: str = "http://localhost:6333") -> List[Dict[str, Any]]:
    """Get all collections from Qdrant"""
    try:
        response = requests.get(f"{url}/collections", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('collections', [])
    except requests.RequestException as e:
        print(f"Error getting collections: {e}")
        return []

def get_collection_info(url: str, collection_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific collection"""
    try:
        response = requests.get(f"{url}/collections/{collection_name}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting collection info for {collection_name}: {e}")
        return None

def get_collection_points(url: str, collection_name: str, limit: int = 1000) -> Optional[Dict[str, Any]]:
    """Get points from a collection (limited to prevent memory issues)"""
    try:
        response = requests.post(
            f"{url}/collections/{collection_name}/points/scroll",
            json={"limit": limit, "with_payload": True, "with_vector": False},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting points for {collection_name}: {e}")
        return None

def create_backup(backup_dir: str, include_points: bool = False, 
                 qdrant_url: str = "http://localhost:6333") -> bool:
    """Create a comprehensive backup of the vector database"""
    
    # Create backup directory
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Checking Qdrant connection at {qdrant_url}...")
    if not check_qdrant_connection(qdrant_url):
        print("❌ Cannot connect to Qdrant server. Is it running?")
        return False
    
    print("✅ Qdrant server is accessible")
    
    # Get all collections
    print("📋 Getting collections...")
    collections = get_collections(qdrant_url)
    
    if not collections:
        print("⚠️  No collections found in vector database")
        return True
    
    print(f"📊 Found {len(collections)} collections")
    
    # Create backup metadata
    backup_metadata = {
        "backup_timestamp": datetime.now().isoformat(),
        "qdrant_url": qdrant_url,
        "total_collections": len(collections),
        "backup_type": "full" if include_points else "metadata_only",
        "collections": []
    }
    
    # Process each collection
    for i, collection in enumerate(collections, 1):
        collection_name = collection.get('name', 'unknown')
        print(f"📦 Processing collection {i}/{len(collections)}: {collection_name}")
        
        # Get detailed collection info
        collection_info = get_collection_info(qdrant_url, collection_name)
        
        collection_backup = {
            "name": collection_name,
            "info": collection_info,
            "points": None
        }
        
        # Get points if requested
        if include_points and collection_info:
            print(f"  📥 Downloading points for {collection_name}...")
            points_data = get_collection_points(qdrant_url, collection_name)
            if points_data:
                collection_backup["points"] = points_data
                print(f"  ✅ Downloaded {len(points_data.get('result', {}).get('points', []))} points")
            else:
                print(f"  ⚠️  Failed to download points for {collection_name}")
        
        backup_metadata["collections"].append(collection_backup)
    
    # Save backup metadata
    metadata_file = backup_path / "backup_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(backup_metadata, f, indent=2, ensure_ascii=False)
    
    # Save individual collection files
    collections_dir = backup_path / "collections"
    collections_dir.mkdir(exist_ok=True)
    
    for collection_backup in backup_metadata["collections"]:
        collection_name = collection_backup["name"]
        collection_file = collections_dir / f"{collection_name}.json"
        
        with open(collection_file, 'w', encoding='utf-8') as f:
            json.dump(collection_backup, f, indent=2, ensure_ascii=False)
    
    # Create summary report
    summary = {
        "backup_summary": {
            "timestamp": backup_metadata["backup_timestamp"],
            "total_collections": len(collections),
            "collections_with_points": sum(1 for c in backup_metadata["collections"] if c["points"]),
            "backup_size_mb": sum(
                os.path.getsize(collections_dir / f"{c['name']}.json") 
                for c in backup_metadata["collections"]
            ) / (1024 * 1024)
        },
        "collection_names": [c["name"] for c in backup_metadata["collections"]]
    }
    
    summary_file = backup_path / "backup_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Vector database backup completed!")
    print(f"📁 Backup location: {backup_path}")
    print(f"📊 Total collections: {len(collections)}")
    print(f"📄 Metadata file: {metadata_file}")
    print(f"📋 Summary file: {summary_file}")
    
    if include_points:
        print(f"💾 Collections with points: {summary['backup_summary']['collections_with_points']}")
        print(f"📏 Backup size: {summary['backup_summary']['backup_size_mb']:.2f} MB")
    
    return True

def restore_backup_info(backup_dir: str) -> None:
    """Show information about how to restore from backup"""
    print("\n🔄 To restore from this backup:")
    print("1. Stop the Qdrant server")
    print("2. Replace Qdrant data directory with backup data")
    print("3. Restart Qdrant server")
    print("\n📖 For detailed restore instructions, see:")
    print("   https://qdrant.tech/documentation/guides/backup/")

def main():
    parser = argparse.ArgumentParser(
        description="Backup Qdrant vector database locally",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create metadata-only backup
  python scripts/backup_vector_db.py
  
  # Create full backup with points data
  python scripts/backup_vector_db.py --include-points
  
  # Specify custom backup directory
  python scripts/backup_vector_db.py --backup-dir /path/to/backup
        """
    )
    
    parser.add_argument(
        "--include-points",
        action="store_true",
        help="Include point data in backup (can be large)"
    )
    
    parser.add_argument(
        "--backup-dir",
        default=f"backups/vector_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Backup directory path (default: backups/vector_db_YYYYMMDD_HHMMSS)"
    )
    
    parser.add_argument(
        "--qdrant-url",
        default="http://localhost:6333",
        help="Qdrant server URL (default: http://localhost:6333)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Vector Database Backup Tool")
    print("=" * 50)
    print(f"📁 Backup directory: {args.backup_dir}")
    print(f"🔗 Qdrant URL: {args.qdrant_url}")
    print(f"📦 Include points: {args.include_points}")
    print()
    
    success = create_backup(
        backup_dir=args.backup_dir,
        include_points=args.include_points,
        qdrant_url=args.qdrant_url
    )
    
    if success:
        restore_backup_info(args.backup_dir)
        sys.exit(0)
    else:
        print("❌ Backup failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 