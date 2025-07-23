"""
AASX File Generator Module
Comprehensive Python module for generating AASX (Asset Administration Shell Exchange) files.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


def auto_setup_dotnet_processor() -> bool:
    """
    Automatically set up the .NET AAS processor if not available.
    
    Returns:
        True if setup successful, False otherwise
    """
    try:
        from .dotnet_bridge import DotNetAasBridge
        
        bridge = DotNetAasBridge()
        
        if bridge.is_available():
            logger.info("✅ .NET AAS processor already available")
            return True
        
        logger.info("🔧 Auto-setting up .NET AAS processor...")
        
        # Try to build the processor
        if bridge._build_processor():
            logger.info("✅ .NET AAS processor auto-built successfully")
            return True
        else:
            logger.error("❌ Failed to auto-build .NET AAS processor")
            return False
            
    except Exception as e:
        logger.error(f"❌ Auto-setup failed: {e}")
        return False


# Try to import .NET bridge (primary method for AASX generation)
try:
    from .dotnet_bridge import DotNetAasBridge
    DOTNET_BRIDGE_AVAILABLE = True
    dotnet_bridge = DotNetAasBridge()
    
    # Auto-setup: If .NET processor not available, try to build it
    if not dotnet_bridge.is_available():
        logger.warning("⚠️  .NET processor not available. Auto-building it...")
        if auto_setup_dotnet_processor():
            # Re-initialize bridge after setup
            dotnet_bridge = DotNetAasBridge()
            if dotnet_bridge.is_available():
                logger.info("✅ .NET AAS processor ready after auto-setup")
            else:
                DOTNET_BRIDGE_AVAILABLE = False
        else:
            DOTNET_BRIDGE_AVAILABLE = False
            
except ImportError:
    DOTNET_BRIDGE_AVAILABLE = False
    dotnet_bridge = None
    logger.error("❌ DotNet bridge not available. This is required for proper AASX generation!")
    raise ImportError("DotNet bridge is required but not available")
except Exception as e:
    DOTNET_BRIDGE_AVAILABLE = False
    dotnet_bridge = None
    logger.error(f"❌ DotNet bridge initialization failed: {e}")
    raise ImportError(f"DotNet bridge initialization failed: {e}")

# Ensure we have the .NET processor available
if not DOTNET_BRIDGE_AVAILABLE:
    logger.error("❌ .NET AAS processor is required but not available!")
    logger.error("Required: .NET AAS processor for proper AASX generation")
    raise ImportError("NET AAS processor is required but not available")


class AASXGenerator:
    """
    Comprehensive AASX file generator for the QI Digital Platform.
    
    Uses the .NET AAS processor with official AAS Core libraries for proper AASX generation.
    """
    
    def __init__(self, output_dir: str = "generated_aasx"):
        """
        Initialize AASX generator.
        
        Args:
            output_dir: Directory where generated AASX files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure .NET processor is ready
        if not self.ensure_processor_ready():
            raise RuntimeError(".NET AAS processor setup failed! Cannot proceed with generation.")
    
    def ensure_processor_ready(self) -> bool:
        """
        Ensure the .NET AAS processor is ready for generation.
        Auto-setup if needed.
        
        Returns:
            True if processor is ready, False otherwise
        """
        global dotnet_bridge, DOTNET_BRIDGE_AVAILABLE
        
        if DOTNET_BRIDGE_AVAILABLE and dotnet_bridge and dotnet_bridge.is_available():
            logger.info(".NET AAS processor is ready for generation")
            return True
        
        logger.warning(".NET processor not ready. Attempting auto-setup...")
        
        if auto_setup_dotnet_processor():
            # Re-initialize after setup
            try:
                dotnet_bridge = DotNetAasBridge()
                DOTNET_BRIDGE_AVAILABLE = dotnet_bridge.is_available()
                
                if DOTNET_BRIDGE_AVAILABLE:
                    logger.info(".NET AAS processor ready after auto-setup")
                    return True
                else:
                    logger.error(".NET processor still not available after setup")
                    return False
            except Exception as e:
                logger.error(f"Failed to re-initialize .NET bridge: {e}")
                return False
        else:
            logger.error("Auto-setup failed")
            return False
    
    def generate_from_json(self, json_data: Dict[str, Any], base_name: str, 
                          embedded_files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate AASX file from JSON data using .NET processor.
        
        Args:
            json_data: AAS data as dictionary
            base_name: Base name for the AASX file
            embedded_files: Dictionary mapping AASX paths to file paths
            
        Returns:
            Dictionary containing generation result
        """
        logger.info(f"Generating AASX file: {base_name}")
        logger.debug(f"JSON data keys: {list(json_data.keys())}")
        logger.debug(f"Embedded files count: {len(embedded_files) if embedded_files else 0}")
        
        # Auto-setup: Ensure .NET processor is ready
        if not self.ensure_processor_ready():
            raise RuntimeError(".NET AAS processor setup failed! Cannot proceed with generation.")
        
        try:
            # Prepare output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{base_name}_generated_{timestamp}.aasx"
            output_path = self.output_dir / output_filename
            logger.debug(f"Output path: {output_path}")
            
            # Use .NET processor for generation
            logger.info("Using .NET AAS processor for generation...")
            logger.debug(f"Calling dotnet_bridge.generate_aasx_file...")
            result = dotnet_bridge.generate_aasx_file(json_data, str(output_path), embedded_files)
            logger.debug(f"DotNet bridge result: {result}")
            
            if result and result.get('success'):
                logger.info(f"Successfully generated AASX: {output_path}")
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "file_name": output_filename,
                    "generation_timestamp": timestamp,
                    "embedded_files_count": len(embedded_files) if embedded_files else 0,
                    "details": result
                }
            else:
                error_msg = f"Failed to generate AASX: {result.get('error', 'Unknown error') if result else 'No result from processor'}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "output_path": str(output_path)
                }
                
        except Exception as e:
            error_msg = f"Error generating AASX file: {e}"
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": error_msg,
                "output_path": str(output_path) if 'output_path' in locals() else None
            }
    
    def generate_from_json_file(self, json_file_path: str, embedded_files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate AASX file from JSON file.
        
        Args:
            json_file_path: Path to JSON file containing AAS data
            embedded_files: Dictionary mapping AASX paths to file paths
            
        Returns:
            Dictionary containing generation result
        """
        json_file = Path(json_file_path)
        if not json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
        
        try:
            # Load JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Generate AASX
            base_name = json_file.stem
            return self.generate_from_json(json_data, base_name, embedded_files)
            
        except Exception as e:
            error_msg = f"Error loading JSON file: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def generate_from_data(self, data: Dict[str, Any], base_name: str, aas_version: str = "2.0") -> Optional[str]:
        """
        Generate AASX file from data dictionary (compatibility method for scripts).
        
        Args:
            data: Dictionary containing AAS data and embedded files
            base_name: Base name for the AASX file
            aas_version: AAS version (not used in current implementation)
            
        Returns:
            Path to generated AASX file if successful, None otherwise
        """
        logger.info(f"Generating AASX from data: {base_name}")
        logger.debug(f"Data keys: {list(data.keys())}")
        
        try:
            # Extract embedded files from data if present
            embedded_files = None
            if '_embedded_files' in data:
                embedded_files = data['_embedded_files']
                # Convert Path objects to strings if needed
                if embedded_files:
                    embedded_files = {k: str(v) if hasattr(v, '__str__') else v 
                                    for k, v in embedded_files.items()}
                logger.info(f"Found {len(embedded_files)} embedded files in data")
                logger.debug(f"Embedded files: {embedded_files}")
            
            # Remove embedded files from data before JSON serialization
            json_data = {k: v for k, v in data.items() if k != '_embedded_files'}
            logger.debug(f"JSON data keys after cleanup: {list(json_data.keys())}")
            
            # Generate AASX using the existing method
            logger.info("Calling generate_from_json method...")
            result = self.generate_from_json(json_data, base_name, embedded_files)
            logger.debug(f"Generate result: {result}")
            
            if result.get('success'):
                output_path = result.get('output_path')
                logger.info(f"Successfully generated AASX: {output_path}")
                return output_path
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Failed to generate AASX: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error in generate_from_data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def validate_generated_aasx(self, aasx_path: str) -> Dict[str, Any]:
        """
        Validate the generated AASX file.
        
        Args:
            aasx_path: Path to generated AASX file
            
        Returns:
            Dictionary containing validation result
        """
        try:
            import zipfile
            
            with zipfile.ZipFile(aasx_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Check for required AASX files
                required_files = ['aasx/aasx-origin', '[Content_Types].xml']
                missing_files = [f for f in required_files if f not in file_list]
                
                # Check for XML content
                xml_files = [f for f in file_list if f.endswith('.xml') and 'aasx' in f and not f.startswith('[Content_Types]')]
                
                validation_result = {
                    "valid": True,
                    "file_path": aasx_path,
                    "total_files": len(file_list),
                    "missing_required": missing_files,
                    "xml_files": xml_files,
                    "has_aas_content": len(xml_files) > 0
                }
                
                if missing_files:
                    validation_result["valid"] = False
                    validation_result["error"] = f"Missing required files: {missing_files}"
                
                if not xml_files:
                    validation_result["valid"] = False
                    validation_result["error"] = "No AAS XML content found"
                
                return validation_result
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {e}",
                "file_path": aasx_path
            }


class AASXBatchGenerator:
    """
    Batch AASX generator for processing multiple JSON files.
    """
    
    def __init__(self, input_dir: str, output_dir: str = "generated_aasx"):
        """
        Initialize batch generator.
        
        Args:
            input_dir: Directory containing JSON files
            output_dir: Directory for generated AASX files
        """
        self.input_dir = Path(input_dir)
        self.generator = AASXGenerator(output_dir)
        self.results = []
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    def find_json_files(self) -> List[Path]:
        """
        Find all JSON files in the input directory.
        
        Returns:
            List of JSON file paths
        """
        return list(self.input_dir.rglob("*.json"))
    
    def generate_all(self, embedded_files_map: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Generate AASX files from all JSON files.
        
        Args:
            embedded_files_map: Dictionary mapping JSON file names to embedded files
            
        Returns:
            Dictionary containing batch generation results
        """
        json_files = self.find_json_files()
        
        if not json_files:
            logger.warning("No JSON files found in input directory")
            return {
                "success": False,
                "error": "No JSON files found",
                "total_files": 0,
                "results": []
            }
        
        logger.info(f"Found {len(json_files)} JSON files for processing")
        
        successful = 0
        failed = 0
        
        for json_file in json_files:
            logger.info(f"Processing: {json_file.name}")
            
            # Get embedded files for this JSON file if available
            embedded_files = None
            if embedded_files_map and json_file.name in embedded_files_map:
                embedded_files = embedded_files_map[json_file.name]
            
            # Generate AASX
            result = self.generator.generate_from_json_file(str(json_file), embedded_files)
            
            if result.get('success'):
                successful += 1
                logger.info(f"✅ Successfully generated: {json_file.name}")
            else:
                failed += 1
                logger.error(f"❌ Failed to generate: {json_file.name}")
            
            self.results.append({
                "input_file": str(json_file),
                "result": result
            })
        
        # Create summary
        summary = {
            "success": failed == 0,
            "total_files": len(json_files),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(json_files) * 100) if json_files else 0,
            "results": self.results
        }
        
        logger.info(f"Batch generation complete: {successful}/{len(json_files)} successful")
        return summary


def generate_aasx_from_json(json_data: Dict[str, Any], output_path: str, 
                           embedded_files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Convenience function to generate AASX from JSON data.
    
    Args:
        json_data: AAS data as dictionary
        output_path: Path where AASX file should be saved
        embedded_files: Dictionary mapping AASX paths to file paths
        
    Returns:
        Generation result dictionary
    """
    generator = AASXGenerator()
    base_name = Path(output_path).stem
    return generator.generate_from_json(json_data, base_name, embedded_files)


def generate_aasx_from_json_file(json_file_path: str, output_path: str,
                                embedded_files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Convenience function to generate AASX from JSON file.
    
    Args:
        json_file_path: Path to JSON file
        output_path: Path where AASX file should be saved
        embedded_files: Dictionary mapping AASX paths to file paths
        
    Returns:
        Generation result dictionary
    """
    generator = AASXGenerator()
    return generator.generate_from_json_file(json_file_path, embedded_files) 