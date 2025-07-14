#!/usr/bin/env python3
"""
AASX ETL Pipeline Runner Script

This script runs the complete ETL pipeline for processing AASX files
in the Quality Infrastructure Digital Platform.

Usage:
    python run_etl.py [--config config_etl.yaml] [--files file1.aasx file2.aasx]
    python run_etl.py --build  # Install missing packages
    python run_etl.py --check  # Check package availability
"""

import sys
import os
import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime
import time
import traceback
import subprocess
import importlib

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Define required packages for ETL pipeline
REQUIRED_PACKAGES = {
    'core': [
        'yaml',
        'pathlib',
        'logging',
        'json',
        'xml.etree.ElementTree',
        'zipfile',
        'datetime',
        'time',
        'traceback'
    ],
    'optional': [
        'aas_core3',
        'aasx_package', 
        'chromadb',
        'faiss',
        'qdrant_client',
        'sentence_transformers',
        'transformers',
        'torch',
        'numpy',
        'sklearn',  # This will import scikit-learn
        'scipy',
        'pandas',
        'neo4j',
        'openai',
        'anthropic',
        'huggingface_hub'
    ],
    'build_commands': {
        'chromadb': 'pip install chromadb',
        'faiss': 'pip install faiss-cpu',  # or faiss-gpu for GPU support
        'qdrant_client': 'pip install qdrant-client',
        'sentence_transformers': 'pip install sentence-transformers',
        'transformers': 'pip install transformers',
        'torch': 'pip install torch',
        'numpy': 'pip install numpy',
        'sklearn': 'pip install scikit-learn',  # sklearn is the import name for scikit-learn
        'scipy': 'pip install scipy',
        'pandas': 'pip install pandas',
        'neo4j': 'pip install neo4j',
        'openai': 'pip install openai',
        'anthropic': 'pip install anthropic',
        'huggingface_hub': 'pip install huggingface-hub'
    },
    'special_packages': {
        'aas_core3': 'AAS Core 3.0 library (available via .NET processor)',
        'aasx_package': 'AASX Package library (available via .NET processor)'
    }
}

try:
    from aasx.aasx_etl_pipeline import AASXETLPipeline, ETLPipelineConfig
    from aasx.aasx_transformer import TransformationConfig
    from aasx.aasx_loader import LoaderConfig
except ImportError as e:
    print(f"Error importing ETL modules: {e}")
    print("Please run: python run_etl.py --build")
    sys.exit(1)

def check_package_availability():
    """Check availability of required packages"""
    print("🔍 Checking package availability...")
    print("=" * 50)
    
    available_packages = []
    missing_packages = []
    
    # Check core packages
    print("📦 Core packages:")
    for package in REQUIRED_PACKAGES['core']:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
            available_packages.append(package)
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    # Check optional packages
    print("\n📦 Optional packages:")
    for package in REQUIRED_PACKAGES['optional']:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
            available_packages.append(package)
        except ImportError:
            if package in REQUIRED_PACKAGES['special_packages']:
                description = REQUIRED_PACKAGES['special_packages'][package]
                print(f"  ⚠️  {package} ({description})")
                # Don't add special packages to missing list - they're handled separately
            else:
                print(f"  ❌ {package}")
                missing_packages.append(package)
    
    print("\n" + "=" * 50)
    print(f"Available: {len(available_packages)}")
    print(f"Missing: {len(missing_packages)}")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run 'python run_etl.py --build' to install missing packages")
    
    return available_packages, missing_packages

def install_missing_packages():
    """Install missing packages"""
    print("🔧 Installing missing packages...")
    print("=" * 50)
    
    available_packages, missing_packages = check_package_availability()
    
    if not missing_packages:
        print("✅ All packages are already installed!")
        return True
    
    # Separate regular packages from special packages
    regular_packages = [p for p in missing_packages if p in REQUIRED_PACKAGES['build_commands']]
    special_packages = [p for p in missing_packages if p in REQUIRED_PACKAGES['special_packages']]
    
    # Check if we should use the complete setup script
    if special_packages or len(regular_packages) > 5:
        print("🔧 Multiple packages missing or AAS libraries needed")
        print("💡 Recommended: Use the complete setup script for better results")
        print("   python setup_etl.py")
        
        choice = input("\nUse complete setup script? (Y/n): ").lower()
        if choice != 'n':
            setup_script = Path(__file__).parent / "setup_etl.py"
            if setup_script.exists():
                print("🚀 Running complete setup script...")
                result = subprocess.run([sys.executable, str(setup_script)])
                return result.returncode == 0
            else:
                print("❌ Complete setup script not found")
                print("Continuing with manual installation...")
    
    # Install regular packages
    failed_installations = []
    
    for package in regular_packages:
        command = REQUIRED_PACKAGES['build_commands'][package]
        print(f"\n📦 Installing {package}...")
        print(f"  Command: {command}")
        
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  ✅ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {package}: {e.stderr}")
            failed_installations.append(package)
    
    # Handle special packages
    if special_packages:
        print(f"\n📦 Special packages detected:")
        for package in special_packages:
            description = REQUIRED_PACKAGES['special_packages'][package]
            print(f"  ⚠️  {package}: {description}")
        print("  These libraries are used by the .NET processor, not directly by Python")
        print("  They will be available when the .NET processor is built")
        print("  💡 Run 'python setup_etl.py' to set up the complete environment")
    
    print("\n" + "=" * 50)
    
    if failed_installations:
        print(f"❌ Failed to install: {', '.join(failed_installations)}")
        print("Please install these packages manually:")
        for package in failed_installations:
            if package in REQUIRED_PACKAGES['build_commands']:
                print(f"  {REQUIRED_PACKAGES['build_commands'][package]}")
        print("\n💡 Or run the complete setup script:")
        print("   python setup_etl.py")
        return False
    else:
        print("✅ All regular packages installed successfully!")
        if special_packages:
            print("⚠️  AAS libraries will be available via .NET processor")
            print("💡 Run 'python setup_etl.py' to set up the complete environment")
        return True

def build_dotnet_processor():
    """Build the .NET AAS processor"""
    print("🔧 Building .NET AAS processor...")
    print("=" * 50)
    
    # Check if .NET is available
    try:
        result = subprocess.run(
            ["dotnet", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ .NET version: {result.stdout.strip()}")
        else:
            print("❌ .NET not found. Please install .NET 6.0 SDK")
            return False
    except FileNotFoundError:
        print("❌ .NET not found. Please install .NET 6.0 SDK")
        return False
    
    # Build aas-processor
    aas_processor_dir = Path(__file__).parent.parent / "aas-processor"
    
    if not aas_processor_dir.exists():
        print("❌ aas-processor directory not found")
        return False
    
    try:
        print("📦 Restoring packages...")
        result = subprocess.run(
            ["dotnet", "restore"],
            cwd=aas_processor_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Package restore failed: {result.stderr}")
            return False
        
        print("🔨 Building project...")
        result = subprocess.run(
            ["dotnet", "build", "--configuration", "Release"],
            cwd=aas_processor_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False
        
        # Check if executable exists
        exe_path = aas_processor_dir / "bin" / "Release" / "net6.0" / "AasProcessor"
        if exe_path.exists():
            print(f"✅ AAS Processor built successfully: {exe_path}")
            return True
        else:
            print(f"❌ Executable not found at: {exe_path}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def setup_logging(config):
    """Setup logging configuration"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    
    # Create logs directory if it doesn't exist
    log_file = log_config.get('file_path', 'logs/etl_pipeline.log')
    
    # Use absolute path if running in Docker or if path is relative
    if not os.path.isabs(log_file):
        log_file = os.path.join(os.getcwd(), log_file)
    
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file) if log_config.get('file_path') else logging.NullHandler(),
            logging.StreamHandler() if log_config.get('console_output', True) else logging.NullHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def load_config(config_path):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def create_pipeline_config(config):
    """Create ETL pipeline configuration from config dict"""
    pipeline_config = config.get('pipeline', {})
    transform_config = config.get('transformation', {})
    load_config = config.get('database', {})
    vector_config = config.get('vector_database', {})
    
    # Create transformation config
    transformer_config = TransformationConfig(
        output_format=transform_config.get('output_formats', ['json'])[0],
        include_metadata=transform_config.get('include_metadata', True),
        flatten_structures=False,
        normalize_ids=transform_config.get('normalize_ids', True),
        add_timestamps=transform_config.get('add_timestamps', True),
        enrich_with_external_data=transform_config.get('enable_enrichment', True),
        quality_checks=transform_config.get('enable_quality_checks', True)
    )
    
    # Create loader config
    output_config = config.get('output', {})
    loader_config = LoaderConfig(
        output_directory=output_config.get('base_directory', 'output/etl_results'),
        database_path=load_config.get('sqlite_path', 'aasx_data.db'),
        vector_db_path=vector_config.get('path', 'output/vector_db'),
        backup_existing=load_config.get('backup_existing', True),
        separate_file_outputs=output_config.get('separate_file_outputs', False),
        include_filename_in_output=output_config.get('include_filename_in_output', False),
        systematic_structure=output_config.get('systematic_structure', True),
        folder_structure=output_config.get('folder_structure', 'timestamped_by_file')
    )
    
    # Create ETL pipeline config
    etl_config = ETLPipelineConfig(
        extract_config={},
        transform_config=transformer_config,
        load_config=loader_config,
        enable_validation=pipeline_config.get('enable_validation', True),
        enable_logging=pipeline_config.get('enable_logging', True),
        enable_backup=pipeline_config.get('enable_backup', True),
        parallel_processing=pipeline_config.get('parallel_processing', False),
        max_workers=pipeline_config.get('max_workers', 4)
    )
    
    return etl_config

def get_files_to_process(config, specific_files=None):
    """Get list of files to process"""
    input_config = config.get('input', {})
    source_dir = input_config.get('source_directory', 'data/aasx-examples')
    file_pattern = input_config.get('file_pattern', '*.aasx')
    recursive = input_config.get('recursive', False)
    
    source_path = Path(source_dir)
    if not source_path.exists():
        raise ValueError(f"Source directory does not exist: {source_dir}")
    
    if specific_files:
        # Process specific files
        files = []
        for file_name in specific_files:
            file_path = source_path / file_name
            if file_path.exists():
                files.append(file_path)
            else:
                print(f"Warning: File not found: {file_path}")
        return files
    
    # Process all files matching pattern
    if recursive:
        files = list(source_path.rglob(file_pattern))
    else:
        files = list(source_path.glob(file_pattern))
    
    return sorted(files)

def setup_output_directory(config):
    """Setup output directory"""
    output_config = config.get('output', {})
    base_dir = output_config.get('base_directory', 'output/etl_results')
    timestamped = output_config.get('timestamped_output', True)
    clean_output = output_config.get('clean_output', False)
    
    if timestamped:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(base_dir) / f"etl_run_{timestamp}"
    else:
        output_dir = Path(base_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean output directory if requested
    if clean_output and output_dir.exists():
        for file in output_dir.iterdir():
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                import shutil
                shutil.rmtree(file)
    
    return output_dir

def process_files(pipeline, files, config):
    """Process files through ETL pipeline"""
    logger = logging.getLogger(__name__)
    error_config = config.get('error_handling', {})
    continue_on_error = error_config.get('continue_on_error', True)
    max_consecutive_errors = error_config.get('max_consecutive_errors', 5)
    
    results = []
    consecutive_errors = 0
    start_time = time.time()
    
    logger.info(f"Starting to process {len(files)} files")
    
    for i, file_path in enumerate(files, 1):
        logger.info(f"Processing file {i}/{len(files)}: {file_path.name}")
        
        try:
            result = pipeline.process_aasx_file(file_path)
            results.append(result)
            
            if result['status'] == 'completed':
                logger.info(f"✓ Successfully processed: {file_path.name}")
                consecutive_errors = 0
            else:
                logger.error(f"✗ Failed to process: {file_path.name} - {result.get('error', 'Unknown error')}")
                consecutive_errors += 1
                
        except Exception as e:
            logger.error(f"✗ Error processing {file_path.name}: {e}")
            consecutive_errors += 1
            results.append({
                'file_path': str(file_path),
                'status': 'failed',
                'error': str(e)
            })
        
        # Check if we should stop due to too many consecutive errors
        if consecutive_errors >= max_consecutive_errors:
            logger.error(f"Stopping due to {consecutive_errors} consecutive errors")
            break
        
        # Check if we should continue on error
        if not continue_on_error and consecutive_errors > 0:
            logger.error("Stopping due to error (continue_on_error=False)")
            break
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = [r for r in results if r['status'] == 'completed']
    failed = [r for r in results if r['status'] == 'failed']
    
    logger.info(f"Processing completed:")
    logger.info(f"  - Total files: {len(files)}")
    logger.info(f"  - Successful: {len(successful)}")
    logger.info(f"  - Failed: {len(failed)}")
    logger.info(f"  - Total time: {total_time:.2f}s")
    
    return {
        'total_files': len(files),
        'successful': len(successful),
        'failed': len(failed),
        'total_time': total_time,
        'results': results
    }

def create_rag_dataset(pipeline, config):
    """Create RAG dataset if enabled"""
    rag_config = config.get('rag', {})
    if not rag_config.get('enabled', False):
        return None
    
    try:
        logger = logging.getLogger(__name__)
        logger.info("Creating RAG dataset...")
        
        output_path = rag_config.get('output_path', '../output/rag_dataset.json')
        rag_path = pipeline.create_rag_ready_dataset(output_path)
        
        logger.info(f"RAG dataset created: {rag_path}")
        return rag_path
        
    except Exception as e:
        logger.error(f"Error creating RAG dataset: {e}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run AASX ETL Pipeline')
    parser.add_argument('--config', default='webapp/config/config_etl.yaml', help='Configuration file path')
    parser.add_argument('--files', nargs='+', help='Specific files to process')
    parser.add_argument('--output-dir', help='Override output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--check', action='store_true', help='Check package availability')
    parser.add_argument('--build', action='store_true', help='Install missing packages and build .NET processor')
    parser.add_argument('--build-dotnet', action='store_true', help='Build .NET AAS processor only')
    
    args = parser.parse_args()
    
    # Handle build and check options
    if args.check:
        check_package_availability()
        return 0
    
    if args.build_dotnet:
        success = build_dotnet_processor()
        return 0 if success else 1
    
    if args.build:
        print("🚀 Building ETL Pipeline Environment")
        print("=" * 60)
        
        # Install Python packages
        print("\n📦 Step 1: Installing Python packages...")
        python_success = install_missing_packages()
        
        # Build .NET processor
        print("\n🔧 Step 2: Building .NET AAS processor...")
        dotnet_success = build_dotnet_processor()
        
        print("\n" + "=" * 60)
        if python_success and dotnet_success:
            print("✅ Build completed successfully!")
            print("You can now run: python run_etl.py")
            return 0
        else:
            print("❌ Build completed with errors. Please check the output above.")
            return 1
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    logger = setup_logging(config)
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check package availability before running
    print("🔍 Checking package availability...")
    available_packages, missing_packages = check_package_availability()
    
    if missing_packages:
        print(f"\n⚠️  Missing packages detected: {len(missing_packages)}")
        print("Some features may be limited. Run 'python run_etl.py --build' to install missing packages.")
        print("Continuing with available packages...\n")
    
    logger.info("=" * 60)
    logger.info("AASX ETL Pipeline Runner")
    logger.info("=" * 60)
    
    try:
        # Setup output directory
        output_dir = setup_output_directory(config)
        logger.info(f"Output directory: {output_dir}")
        
        # Create pipeline configuration
        etl_config = create_pipeline_config(config)
        
        # Create pipeline
        pipeline = AASXETLPipeline(etl_config)
        logger.info("ETL pipeline initialized")
        
        # Get files to process
        files = get_files_to_process(config, args.files)
        if not files:
            logger.error("No files found to process")
            return 1
        
        logger.info(f"Found {len(files)} files to process:")
        for file in files:
            logger.info(f"  - {file.name}")
        
        # Process files
        results = process_files(pipeline, files, config)
        
        # Create RAG dataset if enabled
        rag_path = create_rag_dataset(pipeline, config)
        
        # Print final statistics
        logger.info("=" * 60)
        logger.info("ETL Pipeline Results")
        logger.info("=" * 60)
        logger.info(f"Total files processed: {results['total_files']}")
        logger.info(f"Successful: {results['successful']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Total processing time: {results['total_time']:.2f}s")
        
        if results['successful'] > 0:
            avg_time = results['total_time'] / results['successful']
            logger.info(f"Average time per file: {avg_time:.2f}s")
        
        # Print pipeline statistics
        pipeline_stats = pipeline.get_pipeline_stats()
        logger.info(f"Pipeline statistics:")
        logger.info(f"  - Files processed: {pipeline_stats['files_processed']}")
        logger.info(f"  - Files failed: {pipeline_stats['files_failed']}")
        logger.info(f"  - Total processing time: {pipeline_stats['total_processing_time']:.2f}s")
        
        if rag_path:
            logger.info(f"RAG dataset: {rag_path}")
        
        logger.info("=" * 60)
        
        return 0 if results['failed'] == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
