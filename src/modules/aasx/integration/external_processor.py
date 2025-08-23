"""
External Processor Integration

Integration with external AASX processing tools and executables.
"""

import os
import subprocess
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import asyncio
import json
import time

from ..config.settings import IntegrationConfig
from ..utils.validation_utils import validate_file_extension, validate_file_size

logger = logging.getLogger(__name__)


class ExternalProcessorError(Exception):
    """Exception raised during external processor operations."""
    pass


class ExternalProcessor:
    """Integration with external AASX processing tools."""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize external processor integration.
        
        Args:
            config: Integration configuration
        """
        self.config = config
        self.processor_path = config.aasx_processor_path
        self.enabled = config.enable_external_processor
        
        if self.enabled and not self.processor_path:
            logger.warning("External processor enabled but no path specified")
        
        if self.processor_path and not os.path.exists(self.processor_path):
            logger.error(f"External processor not found: {self.processor_path}")
    
    async def process_aasx_file(self, input_path: str, output_path: str, 
                               options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process AASX file using external processor.
        
        Args:
            input_path: Path to input AASX file
            output_path: Path for output file
            options: Processing options
            
        Returns:
            Dict[str, Any]: Processing results
        """
        if not self.enabled:
            raise ExternalProcessorError("External processor is disabled")
        
        if not self.processor_path or not os.path.exists(self.processor_path):
            raise ExternalProcessorError(f"External processor not available: {self.processor_path}")
        
        # Validate input file
        if not os.path.exists(input_path):
            raise ExternalProcessorError(f"Input file not found: {input_path}")
        
        # Prepare processing options
        processing_options = self._prepare_processing_options(options or {})
        
        try:
            # Execute external processor
            result = await self._execute_processor(input_path, output_path, processing_options)
            
            # Validate output
            if os.path.exists(output_path):
                result['output_file_size'] = os.path.getsize(output_path)
                result['output_file_exists'] = True
            else:
                result['output_file_exists'] = False
                logger.warning(f"Output file not created: {output_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"External processor failed: {str(e)}")
            raise ExternalProcessorError(f"Processing failed: {str(e)}")
    
    async def extract_aasx(self, input_path: str, output_dir: str, 
                          format_type: str = "json") -> Dict[str, Any]:
        """
        Extract AASX file using external processor.
        
        Args:
            input_path: Path to input AASX file
            output_dir: Output directory for extracted files
            format_type: Output format (json, xml, yaml)
            
        Returns:
            Dict[str, Any]: Extraction results
        """
        options = {
            'operation': 'extract',
            'output_format': format_type,
            'output_directory': output_dir
        }
        
        return await self.process_aasx_file(input_path, output_dir, options)
    
    async def generate_aasx(self, input_path: str, output_path: str, 
                           format_type: str = "aasx") -> Dict[str, Any]:
        """
        Generate AASX file using external processor.
        
        Args:
            input_path: Path to input file (json, xml, yaml)
            output_path: Path for output AASX file
            format_type: Output format (aasx, xml, json)
            
        Returns:
            Dict[str, Any]: Generation results
        """
        options = {
            'operation': 'generate',
            'output_format': format_type,
            'validate_output': True
        }
        
        return await self.process_aasx_file(input_path, output_path, options)
    
    async def validate_aasx(self, input_path: str) -> Dict[str, Any]:
        """
        Validate AASX file using external processor.
        
        Args:
            input_path: Path to AASX file
            
        Returns:
            Dict[str, Any]: Validation results
        """
        if not self.enabled or not self.processor_path:
            raise ExternalProcessorError("External processor not available")
        
        options = {
            'operation': 'validate',
            'strict_validation': True,
            'generate_report': True
        }
        
        # Create temporary output for validation report
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "validation_report.json")
            
            try:
                result = await self._execute_processor(input_path, output_path, options)
                
                # Read validation report if generated
                if os.path.exists(output_path):
                    try:
                        with open(output_path, 'r') as f:
                            validation_report = json.load(f)
                        result['validation_report'] = validation_report
                    except Exception as e:
                        logger.warning(f"Failed to read validation report: {str(e)}")
                
                return result
                
            except Exception as e:
                logger.error(f"Validation failed: {str(e)}")
                raise ExternalProcessorError(f"Validation failed: {str(e)}")
    
    async def batch_process(self, input_files: List[str], output_dir: str, 
                           operation: str = "extract") -> Dict[str, Any]:
        """
        Batch process multiple AASX files.
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory
            operation: Processing operation (extract, generate, validate)
            
        Returns:
            Dict[str, Any]: Batch processing results
        """
        if not self.enabled:
            raise ExternalProcessorError("External processor is disabled")
        
        results = {
            'total_files': len(input_files),
            'processed_files': 0,
            'failed_files': 0,
            'results': {}
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        for input_file in input_files:
            try:
                if operation == "extract":
                    output_path = os.path.join(output_dir, f"{Path(input_file).stem}_extracted")
                    result = await self.extract_aasx(input_file, output_path)
                elif operation == "generate":
                    output_path = os.path.join(output_dir, f"{Path(input_file).stem}.aasx")
                    result = await self.generate_aasx(input_file, output_path)
                elif operation == "validate":
                    result = await self.validate_aasx(input_file)
                else:
                    raise ValueError(f"Unsupported operation: {operation}")
                
                results['results'][input_file] = {
                    'status': 'success',
                    'result': result
                }
                results['processed_files'] += 1
                
            except Exception as e:
                logger.error(f"Failed to process {input_file}: {str(e)}")
                results['results'][input_file] = {
                    'status': 'failed',
                    'error': str(e)
                }
                results['failed_files'] += 1
        
        results['success_rate'] = results['processed_files'] / results['total_files']
        return results
    
    def _prepare_processing_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare processing options for external processor."""
        default_options = {
            'timeout': self.config.api_timeout_seconds,
            'verbose': True,
            'log_level': 'INFO'
        }
        
        # Merge with provided options
        processing_options = {**default_options, **options}
        
        # Validate options
        if 'timeout' in processing_options:
            processing_options['timeout'] = min(
                processing_options['timeout'], 
                self.config.api_timeout_seconds
            )
        
        return processing_options
    
    async def _execute_processor(self, input_path: str, output_path: str, 
                                options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute external processor with given options."""
        # Build command line arguments
        cmd_args = [self.processor_path]
        
        # Add input/output paths
        cmd_args.extend(['--input', input_path])
        cmd_args.extend(['--output', output_path])
        
        # Add options
        for key, value in options.items():
            if isinstance(value, bool):
                if value:
                    cmd_args.append(f'--{key}')
            else:
                cmd_args.extend([f'--{key}', str(value)])
        
        logger.info(f"Executing external processor: {' '.join(cmd_args)}")
        
        # Execute processor
        start_time = time.time()
        
        try:
            # Run processor with timeout
            process = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=options.get('timeout', self.config.api_timeout_seconds)
            )
            
            stdout, stderr = await process.communicate()
            
            execution_time = time.time() - start_time
            
            result = {
                'success': process.returncode == 0,
                'return_code': process.returncode,
                'execution_time': execution_time,
                'stdout': stdout.decode('utf-8') if stdout else '',
                'stderr': stderr.decode('utf-8') if stderr else '',
                'command': ' '.join(cmd_args)
            }
            
            if process.returncode != 0:
                logger.error(f"Processor failed with return code {process.returncode}")
                logger.error(f"Stderr: {result['stderr']}")
                raise ExternalProcessorError(f"Processor failed: {result['stderr']}")
            
            logger.info(f"External processor completed successfully in {execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            logger.error(f"Processor timed out after {execution_time:.2f}s")
            raise ExternalProcessorError(f"Processor timed out after {execution_time:.2f}s")
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Processor execution failed after {execution_time:.2f}s: {str(e)}")
            raise ExternalProcessorError(f"Processor execution failed: {str(e)}")
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about the external processor."""
        info = {
            'enabled': self.enabled,
            'available': False,
            'path': self.processor_path,
            'version': None,
            'capabilities': []
        }
        
        if not self.enabled or not self.processor_path:
            return info
        
        if not os.path.exists(self.processor_path):
            return info
        
        info['available'] = True
        
        # Try to get version information
        try:
            result = subprocess.run(
                [self.processor_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info['version'] = result.stdout.strip()
        except Exception:
            pass
        
        # Try to get help information for capabilities
        try:
            result = subprocess.run(
                [self.processor_path, '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                help_text = result.stdout.lower()
                if 'extract' in help_text:
                    info['capabilities'].append('extract')
                if 'generate' in help_text:
                    info['capabilities'].append('generate')
                if 'validate' in help_text:
                    info['capabilities'].append('validate')
                if 'convert' in help_text:
                    info['capabilities'].append('convert')
        except Exception:
            pass
        
        return info
    
    def test_processor(self) -> Dict[str, Any]:
        """Test external processor functionality."""
        test_result = {
            'processor_available': False,
            'basic_functionality': False,
            'test_file_processing': False,
            'errors': []
        }
        
        if not self.enabled:
            test_result['errors'].append("External processor is disabled")
            return test_result
        
        if not self.processor_path:
            test_result['errors'].append("No processor path specified")
            return test_result
        
        if not os.path.exists(self.processor_path):
            test_result['errors'].append(f"Processor not found: {self.processor_path}")
            return test_result
        
        test_result['processor_available'] = True
        
        # Test basic functionality (help command)
        try:
            result = subprocess.run(
                [self.processor_path, '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                test_result['basic_functionality'] = True
            else:
                test_result['errors'].append(f"Help command failed: {result.stderr}")
        except Exception as e:
            test_result['errors'].append(f"Help command error: {str(e)}")
        
        return test_result


# Factory function
def create_external_processor(config: Optional[IntegrationConfig] = None) -> ExternalProcessor:
    """
    Create external processor instance.
    
    Args:
        config: Optional integration configuration
        
    Returns:
        ExternalProcessor: External processor instance
    """
    if config is None:
        from ..config.settings import get_environment_config
        config = get_environment_config().integration
    
    return ExternalProcessor(config)
