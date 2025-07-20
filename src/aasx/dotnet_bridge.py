"""
.NET AAS Processor Bridge
Python interface to call the .NET AAS processor for advanced AASX processing.
"""

import subprocess
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DotNetAasBridge:
    """
    Bridge to .NET AAS processor for advanced AASX processing.
    """
    
    def __init__(self, dotnet_project_path: str = "aas-processor"):
        """
        Initialize the .NET bridge.
        
        Args:
            dotnet_project_path: Path to the .NET AAS processor project
        """
        # Get the absolute path to the .NET project
        current_dir = Path(__file__).parent.parent.parent  # Go up from src/aasx/dotnet_bridge.py
        self.dotnet_project_path = current_dir / dotnet_project_path
        
        # Check for environment variable override
        env_path = os.getenv('AAS_PROCESSOR_PATH')
        if env_path:
            self.processor_exe = Path(env_path)
            if self.processor_exe.exists():
                logger.info(f"Using .NET processor from environment: {self.processor_exe}")
                return
        
        # Check for pre-built processor in container
        container_processor = Path("/app/aas-processor/AasProcessor.dll")
        if container_processor.exists():
            self.processor_exe = container_processor
            logger.info(f"Using pre-built .NET processor: {self.processor_exe}")
            return
        
        self.processor_exe = None
        self._build_processor()
    
    def _build_processor(self) -> bool:
        """
        Build the .NET AAS processor.
        
        Returns:
            True if build successful, False otherwise
        """
        try:
            if not self.dotnet_project_path.exists():
                logger.warning(f".NET project not found at: {self.dotnet_project_path}")
                return False
            
            # Build the project
            result = subprocess.run(
                ["dotnet", "build", "--configuration", "Release"],
                cwd=self.dotnet_project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to build .NET project: {result.stderr}")
                return False
            
            # Find the executable
            exe_path = self.dotnet_project_path / "bin" / "Release" / "net6.0" / "AasProcessor.exe"
            if exe_path.exists():
                self.processor_exe = exe_path
                logger.info(f".NET AAS processor built successfully: {self.processor_exe}")
                return True
            else:
                logger.error(f"Processor executable not found at: {exe_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error building .NET processor: {e}")
            return False
    
    def process_aasx_file(self, aasx_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process an AASX file using the .NET processor with complete structure preservation.
        This method preserves all AAS XML content, relationships, and metadata for perfect round-trip conversion.
        
        Args:
            aasx_file_path: Path to the AASX file
            
        Returns:
            Dictionary containing complete AAS data with full structure or None if failed
        """
        if not self.processor_exe:
            logger.error(".NET processor not available")
            return None
        
        try:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_output = temp_file.name
            
            # Call the .NET processor with complete processing
            if str(self.processor_exe).endswith('.dll'):
                # Use dotnet to run the DLL
                cmd = ["dotnet", str(self.processor_exe), "process-enhanced", aasx_file_path, temp_output]
            else:
                # Direct executable
                cmd = [str(self.processor_exe), "process-enhanced", aasx_file_path, temp_output]
            
            logger.info(f"Calling .NET processor for complete AASX processing")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Longer timeout for complete processing
            )
            
            logger.debug(f".NET processor stdout: {result.stdout}")
            logger.debug(f".NET processor stderr: {result.stderr}")
            logger.debug(f".NET processor return code: {result.returncode}")
            
            if result.returncode != 0:
                logger.error(f".NET processor complete processing failed: {result.stderr}")
                return None
            
            # Read the output
            with open(temp_output, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clean up
            os.unlink(temp_output)
            
            logger.info(f"Successfully processed AASX file with complete .NET processor")
            return data
            
        except Exception as e:
            logger.error(f"Error calling complete .NET processor: {e}")
            return None

    def process_aasx_file_enhanced(self, aasx_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process an AASX file using the enhanced .NET processor for complete structure preservation.
        
        Args:
            aasx_file_path: Path to the AASX file
            
        Returns:
            Dictionary containing enhanced AAS data with complete structure or None if failed
        """
        if not self.processor_exe:
            logger.error(".NET processor not available")
            return None
        
        try:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_output = temp_file.name
            
            # Call the .NET processor with enhanced processing
            if str(self.processor_exe).endswith('.dll'):
                # Use dotnet to run the DLL
                cmd = ["dotnet", str(self.processor_exe), "process-enhanced", aasx_file_path, temp_output]
            else:
                # Direct executable
                cmd = [str(self.processor_exe), "process-enhanced", aasx_file_path, temp_output]
            
            logger.info(f"Calling .NET processor for enhanced AASX processing")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Longer timeout for enhanced processing
            )
            
            logger.debug(f".NET processor stdout: {result.stdout}")
            logger.debug(f".NET processor stderr: {result.stderr}")
            logger.debug(f".NET processor return code: {result.returncode}")
            
            if result.returncode != 0:
                logger.error(f".NET processor enhanced processing failed: {result.stderr}")
                return None
            
            # Read the output
            with open(temp_output, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clean up
            os.unlink(temp_output)
            
            logger.info(f"Successfully processed AASX file with enhanced .NET processor")
            return data
            
        except Exception as e:
            logger.error(f"Error calling enhanced .NET processor: {e}")
            return None
    
    def generate_aasx_file(self, json_data: Dict[str, Any], output_path: str, embedded_files: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate an AASX file from JSON data using the .NET processor.
        
        Args:
            json_data: AAS data as dictionary
            output_path: Path where AASX file should be saved
            embedded_files: Dictionary mapping AASX paths to file paths
            
        Returns:
            Dictionary containing generation result or None if failed
        """
        if not self.processor_exe:
            logger.error(".NET processor not available")
            return None
        
        try:
            # Convert JSON data to string
            json_string = json.dumps(json_data, ensure_ascii=False)
            
            # Convert embedded files to JSON string if provided
            embedded_files_string = json.dumps(embedded_files or {}, ensure_ascii=False) if embedded_files else None
            
            # Call the .NET processor for generation
            if str(self.processor_exe).endswith('.dll'):
                # Use dotnet to run the DLL
                cmd = ["dotnet", str(self.processor_exe), "generate", "--json", json_string, "--output", output_path]
                if embedded_files_string:
                    cmd.extend(["--embedded", embedded_files_string])
            else:
                # Direct executable
                cmd = [str(self.processor_exe), "generate", "--json", json_string, "--output", output_path]
                if embedded_files_string:
                    cmd.extend(["--embedded", embedded_files_string])
            
            logger.info(f"Calling .NET processor for AASX generation")
            logger.debug(f"Command: {' '.join(cmd[:4])} [JSON_DATA] {' '.join(cmd[5:])}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            logger.debug(f".NET processor stdout: {result.stdout}")
            logger.debug(f".NET processor stderr: {result.stderr}")
            logger.debug(f".NET processor return code: {result.returncode}")
            
            if result.returncode != 0:
                logger.error(f".NET processor generation failed: {result.stderr}")
                return None
            
            # Parse result
            try:
                if result.stdout.strip():
                    return json.loads(result.stdout)
                else:
                    return {
                        "success": True,
                        "output_path": output_path,
                        "message": "AASX generated successfully"
                    }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "output_path": output_path,
                    "message": "AASX generated successfully (no detailed output)"
                }
                
        except subprocess.TimeoutExpired:
            logger.error(".NET processor generation timed out")
            return None
        except Exception as e:
            logger.error(f"Error calling .NET processor for generation: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if the .NET processor is available.
        
        Returns:
            True if available, False otherwise
        """
        return self.processor_exe is not None and self.processor_exe.exists()


def test_dotnet_bridge():
    """
    Test the .NET bridge functionality.
    """
    print("🧪 Testing .NET AAS Bridge")
    print("=" * 40)
    
    bridge = DotNetAasBridge()
    
    if not bridge.is_available():
        print("❌ .NET processor not available")
        print("   Make sure you have:")
        print("   - .NET 6.0 SDK installed")
        print("   - AasCore.Aas3.Package NuGet package")
        print("   - Built the aas-processor project")
        return False
    
    print("✅ .NET processor is available")
    
    # Test with a sample AASX file
    aasx_dir = Path("AasxPackageExplorer/content-for-demo")
    aasx_files = list(aasx_dir.glob("*.aasx"))
    
    if aasx_files:
        test_file = aasx_files[0]
        print(f"📁 Testing with: {test_file.name}")
        
        result = bridge.process_aasx_file(str(test_file))
        
        if result:
            print("✅ .NET processing successful!")
            print(f"   Processing method: {result.get('processing_method')}")
            print(f"   Assets found: {len(result.get('assets', []))}")
            print(f"   Submodels found: {len(result.get('submodels', []))}")
            print(f"   Concept descriptions: {len(result.get('concept_descriptions', []))}")
            print(f"   Documents found: {len(result.get('documents', []))}")
            
            # Show first asset details
            if result.get('assets'):
                first_asset = result['assets'][0]
                print(f"   First asset: {first_asset.get('idShort', 'Unknown')}")
                print(f"   Asset ID: {first_asset.get('id', 'Unknown')}")
            
            return True
        else:
            print("❌ .NET processing failed")
            return False
    else:
        print("⚠️  No AASX files found for testing")
        return False


if __name__ == "__main__":
    test_dotnet_bridge() 