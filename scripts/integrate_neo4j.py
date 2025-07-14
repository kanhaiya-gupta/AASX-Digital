#!/usr/bin/env python3
"""
Neo4j Integration Script for AASX ETL Pipeline

This script provides comprehensive integration with Neo4j graph database
for importing and analyzing AASX data from the ETL pipeline output.

Usage:
    python integrate_neo4j.py --import-dir output/etl_results/
    python integrate_neo4j.py --analyze
    python integrate_neo4j.py --query "MATCH (n:Node) RETURN count(n)"
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will use system environment variables
import pandas as pd

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from kg_neo4j.neo4j_manager import Neo4jManager
from kg_neo4j.graph_analyzer import AASXGraphAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse():
    """Setup command line argument parsing"""
    parser = argparse.ArgumentParser(
        description='Neo4j Integration for AASX ETL Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import all graph files from ETL output
  python integrate_neo4j.py --import-dir output/etl_results/
  
  # Run comprehensive analysis
  python integrate_neo4j.py --analyze
  
  # Execute custom Cypher query
  python integrate_neo4j.py --query "MATCH (n:Node) RETURN count(n)"
  
  # Import specific file
  python integrate_neo4j.py --import-file output/etl_results/file/aasx_data_graph.json
  
  # Export analysis to CSV
  python integrate_neo4j.py --analyze --export-csv analysis_results.csv
        """
    )
    
    # Import options
    parser.add_argument('--import-dir', type=str, 
                       help='Directory containing ETL output with graph files')
    parser.add_argument('--import-file', type=str,
                       help='Specific graph file to import')
    
    # Analysis options
    parser.add_argument('--analyze', action='store_true',
                       help='Run comprehensive graph analysis')
    parser.add_argument('--query', type=str,
                       help='Execute custom Cypher query')
    parser.add_argument('--export-csv', type=str,
                       help='Export analysis results to CSV file')
    
    # Neo4j connection options
    parser.add_argument('--uri', type=str, 
                       help='Neo4j connection URI (defaults to NEO4J_URI env var)')
    parser.add_argument('--user', type=str, 
                       help='Neo4j username (defaults to NEO4J_USER env var)')
    parser.add_argument('--password', type=str, 
                       help='Neo4j password (defaults to NEO4J_PASSWORD env var)')
    
    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without executing')
    
    return parser

def find_graph_files(directory: Path) -> List[Path]:
    """Find all graph files in the directory"""
    graph_files = []
    
    if directory.exists():
        # Find all *_graph.json files recursively
        graph_files = list(directory.rglob("*_graph.json"))
        logger.info(f"Found {len(graph_files)} graph files in {directory}")
    else:
        logger.error(f"Directory does not exist: {directory}")
    
    return graph_files

def import_graph_files(neo4j_manager: Neo4jManager, graph_files: List[Path], dry_run: bool = False):
    """Import multiple graph files to Neo4j"""
    logger.info(f"Starting import of {len(graph_files)} graph files...")
    
    for i, graph_file in enumerate(graph_files, 1):
        logger.info(f"Processing {i}/{len(graph_files)}: {graph_file.name}")
        
        if dry_run:
            logger.info(f"DRY RUN: Would import {graph_file}")
            continue
        
        try:
            neo4j_manager.import_graph_file(graph_file)
            logger.info(f"✓ Successfully imported {graph_file.name}")
        except Exception as e:
            logger.error(f"✗ Failed to import {graph_file.name}: {e}")

def run_analysis(analyzer: AASXGraphAnalyzer, export_csv: Optional[str] = None):
    """Run comprehensive graph analysis"""
    logger.info("Running comprehensive graph analysis...")
    
    results = {}
    
    # 1. Network Statistics
    logger.info("1. Network Statistics")
    try:
        stats = analyzer.get_network_statistics()
        results['network_statistics'] = stats
        print("\n📊 Network Statistics:")
        print(stats.to_string(index=False))
    except Exception as e:
        logger.error(f"Error getting network statistics: {e}")
    
    # 2. Quality Distribution
    logger.info("2. Quality Distribution Analysis")
    try:
        quality_dist = analyzer.get_quality_distribution()
        results['quality_distribution'] = quality_dist
        print("\n🎯 Quality Distribution:")
        print(quality_dist.to_string(index=False))
    except Exception as e:
        logger.error(f"Error getting quality distribution: {e}")
    
    # 3. Compliance Analysis
    logger.info("3. Compliance Analysis")
    try:
        compliance = analyzer.analyze_compliance_network()
        results['compliance_analysis'] = compliance
        print("\n✅ Compliance Analysis:")
        print(compliance.to_string(index=False))
    except Exception as e:
        logger.error(f"Error analyzing compliance: {e}")
    
    # 4. Entity Type Distribution
    logger.info("4. Entity Type Distribution")
    try:
        entity_dist = analyzer.get_entity_type_distribution()
        results['entity_distribution'] = entity_dist
        print("\n🏷️ Entity Type Distribution:")
        print(entity_dist.to_string(index=False))
    except Exception as e:
        logger.error(f"Error getting entity distribution: {e}")
    
    # 5. Relationship Analysis
    logger.info("5. Relationship Analysis")
    try:
        rel_analysis = analyzer.analyze_relationships()
        results['relationship_analysis'] = rel_analysis
        print("\n🔗 Relationship Analysis:")
        print(rel_analysis.to_string(index=False))
    except Exception as e:
        logger.error(f"Error analyzing relationships: {e}")
    
    # Export to CSV if requested
    if export_csv:
        try:
            export_analysis_to_csv(results, export_csv)
            logger.info(f"Analysis results exported to: {export_csv}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    return results

def export_analysis_to_csv(results: Dict[str, pd.DataFrame], output_file: str):
    """Export analysis results to CSV file"""
    with pd.ExcelWriter(output_file.replace('.csv', '.xlsx'), engine='openpyxl') as writer:
        for analysis_name, df in results.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=analysis_name[:31], index=False)
    
    logger.info(f"Analysis results exported to Excel: {output_file.replace('.csv', '.xlsx')}")

def execute_custom_query(neo4j_manager: Neo4jManager, query: str):
    """Execute a custom Cypher query"""
    logger.info(f"Executing custom query: {query}")
    
    try:
        result = neo4j_manager.execute_query(query)
        
        if result:
            print("\n🔍 Query Results:")
            if isinstance(result, list) and result:
                # Convert to DataFrame for better display
                df = pd.DataFrame(result)
                print(df.to_string(index=False))
            else:
                print(result)
        else:
            print("No results returned")
            
    except Exception as e:
        logger.error(f"Error executing query: {e}")

def main():
    """Main function"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("Neo4j Integration for AASX ETL Pipeline")
    logger.info("=" * 60)
    
    # Validate arguments
    if not any([args.import_dir, args.import_file, args.analyze, args.query]):
        logger.error("No action specified. Use --help for usage information.")
        return 1
    
    try:
        # Get Neo4j connection parameters from args or environment
        uri = args.uri or os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
        user = args.user or os.getenv('NEO4J_USER', 'neo4j')
        password = args.password or os.getenv('NEO4J_PASSWORD', 'password')
        
        # Initialize Neo4j manager
        logger.info(f"Connecting to Neo4j at {uri}")
        neo4j_manager = Neo4jManager(uri, user, password)
        
        # Test connection
        if not neo4j_manager.test_connection():
            logger.error("Failed to connect to Neo4j. Check connection parameters.")
            return 1
        
        logger.info("✓ Successfully connected to Neo4j")
        
        # Import graph files
        if args.import_dir:
            import_dir = Path(args.import_dir)
            graph_files = find_graph_files(import_dir)
            
            if graph_files:
                import_graph_files(neo4j_manager, graph_files, args.dry_run)
            else:
                logger.warning(f"No graph files found in {import_dir}")
        
        elif args.import_file:
            graph_file = Path(args.import_file)
            if graph_file.exists():
                if not args.dry_run:
                    neo4j_manager.import_graph_file(graph_file)
                    logger.info(f"✓ Successfully imported {graph_file.name}")
                else:
                    logger.info(f"DRY RUN: Would import {graph_file}")
            else:
                logger.error(f"Graph file not found: {graph_file}")
        
        # Initialize analyzer for analysis
        analyzer = None
        if args.analyze or args.query:
            analyzer = AASXGraphAnalyzer(uri, user, password)
        
        # Run analysis
        if args.analyze:
            run_analysis(analyzer, args.export_csv)
        
        # Execute custom query
        if args.query:
            execute_custom_query(neo4j_manager, args.query)
        
        logger.info("=" * 60)
        logger.info("Neo4j integration completed successfully")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error("Check Neo4j connection and try again.")
        return 1
    
    finally:
        # Clean up connections
        if 'neo4j_manager' in locals():
            neo4j_manager.close()
        if 'analyzer' in locals() and analyzer:
            analyzer.close()

if __name__ == "__main__":
    sys.exit(main()) 