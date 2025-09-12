"""
AASX Integration
================

Integration with Asset Administration Shell (AAS) exchange format.
Handles AASX file operations, AAS model management, and federated learning integration.
"""

import asyncio
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from src.engine.database.connection_manager import ConnectionManager
from src.engine.services.core_system import RegistryService, MetricsService


@dataclass
class AASXConfig:
    """Configuration for AASX integration"""
    # Integration settings
    auto_import_enabled: bool = True
    validation_enabled: bool = True
    caching_enabled: bool = True
    backup_enabled: bool = True
    
    # File processing settings
    max_file_size_mb: int = 100
    supported_formats: List[str] = None
    import_timeout_seconds: int = 300
    batch_processing_size: int = 50
    
    # AAS model settings
    aas_version: str = "3.0"
    validate_schema: bool = True
    required_elements: List[str] = None
    optional_elements: List[str] = None
    
    # Caching settings
    cache_ttl_hours: int = 24
    max_cache_size: int = 1000
    cache_cleanup_interval_hours: int = 6
    
    # Backup settings
    backup_directory: str = "./aasx_backups"
    max_backup_files: int = 10
    backup_retention_days: int = 30
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.aasx', '.xml', '.json']
        if self.required_elements is None:
            self.required_elements = ['assetAdministrationShell', 'submodel', 'conceptDescription']
        if self.optional_elements is None:
            self.optional_elements = ['asset', 'constraint', 'qualifier', 'formula']


@dataclass
class AASXMetrics:
    """Metrics for AASX integration"""
    # File processing metrics
    files_processed: int = 0
    files_imported: int = 0
    files_failed: int = 0
    processing_time: float = 0.0
    
    # AAS model metrics
    aas_models_created: int = 0
    aas_models_updated: int = 0
    aas_models_deleted: int = 0
    validation_errors: int = 0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_size: int = 0
    cache_evictions: int = 0
    
    # Backup metrics
    backups_created: int = 0
    backups_failed: int = 0
    backup_size_mb: float = 0.0
    
    # Performance metrics
    average_processing_time: float = 0.0
    memory_usage_mb: float = 0.0


class AASXIntegration:
    """Integration with Asset Administration Shell (AAS) exchange format"""
    
    def __init__(
        self,
        connection_manager: ConnectionManager,
        registry_service: RegistryService,
        metrics_service: MetricsService,
        config: Optional[AASXConfig] = None
    ):
        """Initialize AASX Integration"""
        self.connection_manager = connection_manager
        self.registry_service = registry_service
        self.metrics_service = metrics_service
        self.config = config or AASXConfig()
        
        # Integration state
        self.processed_files: Dict[str, Dict[str, Any]] = {}
        self.aas_models: Dict[str, Dict[str, Any]] = {}
        self.file_cache: Dict[str, Dict[str, Any]] = {}
        self.import_queue: asyncio.Queue = asyncio.Queue()
        
        # Processing state
        self.processing_active = False
        self.import_task = None
        self.last_cleanup = datetime.now()
        
        # Metrics tracking
        self.metrics = AASXMetrics()
        
        # Initialize backup directory
        self._init_backup_directory()
    
    def _init_backup_directory(self):
        """Initialize backup directory"""
        try:
            backup_path = Path(self.config.backup_directory)
            backup_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Backup directory initialized: {backup_path.absolute()}")
        except Exception as e:
            print(f"⚠️  Failed to initialize backup directory: {e}")
    
    async def start_integration(self):
        """Start the AASX integration"""
        try:
            print("🚀 Starting AASX Integration...")
            
            # Start file processing if enabled
            if self.config.auto_import_enabled:
                await self.start_file_processing()
            
            print("✅ AASX Integration started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start AASX Integration: {e}")
            raise
    
    async def stop_integration(self):
        """Stop the AASX integration"""
        try:
            print("🛑 Stopping AASX Integration...")
            
            # Stop file processing
            if self.processing_active:
                await self.stop_file_processing()
            
            print("✅ AASX Integration stopped successfully")
            
        except Exception as e:
            print(f"❌ Failed to stop AASX Integration: {e}")
            raise
    
    async def start_file_processing(self):
        """Start automatic file processing"""
        try:
            if self.processing_active:
                print("⚠️  File processing already active")
                return
            
            self.processing_active = True
            self.import_task = asyncio.create_task(self._file_processing_loop())
            print("📁 AASX file processing started")
            
        except Exception as e:
            print(f"❌ Failed to start file processing: {e}")
            self.processing_active = False
    
    async def stop_file_processing(self):
        """Stop automatic file processing"""
        try:
            if not self.processing_active:
                return
            
            self.processing_active = False
            
            if self.import_task and not self.import_task.done():
                self.import_task.cancel()
                try:
                    await self.import_task
                except asyncio.CancelledError:
                    pass
            
            print("📁 AASX file processing stopped")
            
        except Exception as e:
            print(f"❌ Failed to stop file processing: {e}")
    
    async def _file_processing_loop(self):
        """Main file processing loop"""
        try:
            while self.processing_active:
                try:
                    # Process files from queue
                    while not self.import_queue.empty():
                        file_path = await asyncio.wait_for(
                            self.import_queue.get(), 
                            timeout=1.0
                        )
                        await self._process_aasx_file(file_path)
                        self.import_queue.task_done()
                    
                    # Perform cleanup if needed
                    if self._should_perform_cleanup():
                        await self._perform_cleanup()
                    
                    await asyncio.sleep(1)  # Small delay to prevent busy waiting
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ File processing loop error: {e}")
                    
        except asyncio.CancelledError:
            print("📁 File processing loop cancelled")
        except Exception as e:
            print(f"❌ File processing loop error: {e}")
            self.processing_active = False
    
    def _should_perform_cleanup(self) -> bool:
        """Check if cleanup should be performed"""
        return (datetime.now() - self.last_cleanup).total_seconds() > (self.config.cache_cleanup_interval_hours * 3600)
    
    async def _perform_cleanup(self):
        """Perform cache and backup cleanup"""
        try:
            print("🧹 Performing AASX integration cleanup...")
            
            # Clean up expired cache entries
            await self._cleanup_cache()
            
            # Clean up old backup files
            await self._cleanup_backups()
            
            self.last_cleanup = datetime.now()
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    async def _cleanup_cache(self):
        """Clean up expired cache entries"""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self.file_cache.items():
                if current_time > entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.file_cache[key]
                self.metrics.cache_evictions += 1
            
            self.metrics.cache_size = len(self.file_cache)
            
            if expired_keys:
                print(f"🗑️  Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            print(f"⚠️  Cache cleanup failed: {e}")
    
    async def _cleanup_backups(self):
        """Clean up old backup files"""
        try:
            backup_path = Path(self.config.backup_directory)
            if not backup_path.exists():
                return
            
            # Get all backup files
            backup_files = list(backup_path.glob("*.aasx"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backup files
            current_time = datetime.now()
            removed_count = 0
            
            for backup_file in backup_files[self.config.max_backup_files:]:
                try:
                    file_age = current_time - datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_age.days > self.config.backup_retention_days:
                        backup_file.unlink()
                        removed_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to remove old backup {backup_file}: {e}")
            
            if removed_count > 0:
                print(f"🗑️  Cleaned up {removed_count} old backup files")
                
        except Exception as e:
            print(f"⚠️  Backup cleanup failed: {e}")
    
    async def import_aasx_file(self, file_path: str) -> Dict[str, Any]:
        """Import an AASX file"""
        try:
            print(f"📥 Importing AASX file: {file_path}")
            
            # Add to processing queue
            await self.import_queue.put(file_path)
            
            return {
                'success': True,
                'message': f'File {file_path} added to import queue',
                'queue_position': self.import_queue.qsize()
            }
            
        except Exception as e:
            print(f"❌ Failed to queue AASX file: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _process_aasx_file(self, file_path: str):
        """Process a single AASX file"""
        try:
            start_time = datetime.now()
            self.metrics.files_processed += 1
            
            print(f"🔄 Processing AASX file: {file_path}")
            
            # Validate file
            if not await self._validate_file(file_path):
                self.metrics.files_failed += 1
                return
            
            # Parse AASX file
            aas_model = await self._parse_aasx_file(file_path)
            if not aas_model:
                self.metrics.files_failed += 1
                return
            
            # Validate AAS model
            if self.config.validation_enabled:
                validation_result = await self._validate_aas_model(aas_model)
                if not validation_result['valid']:
                    print(f"⚠️  AAS model validation failed: {validation_result['errors']}")
                    self.metrics.validation_errors += 1
            
            # Store AAS model
            model_id = aas_model.get('id', f"aas_{len(self.aas_models)}")
            self.aas_models[model_id] = aas_model
            
            # Create backup if enabled
            if self.config.backup_enabled:
                await self._create_backup(file_path)
            
            # Cache file data if enabled
            if self.config.caching_enabled:
                await self._cache_file_data(file_path, aas_model)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.processing_time = processing_time
            self.metrics.files_imported += 1
            self.metrics.aas_models_created += 1
            
            # Update average processing time
            total_files = self.metrics.files_processed
            current_avg = self.metrics.average_processing_time
            self.metrics.average_processing_time = ((current_avg * (total_files - 1)) + processing_time) / total_files
            
            print(f"✅ AASX file processed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Failed to process AASX file {file_path}: {e}")
            self.metrics.files_failed += 1
    
    async def _validate_file(self, file_path: str) -> bool:
        """Validate AASX file before processing"""
        try:
            file_path_obj = Path(file_path)
            
            # Check if file exists
            if not file_path_obj.exists():
                print(f"❌ File does not exist: {file_path}")
                return False
            
            # Check file size
            file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                print(f"❌ File too large: {file_size_mb:.2f}MB > {self.config.max_file_size_mb}MB")
                return False
            
            # Check file format
            file_extension = file_path_obj.suffix.lower()
            if file_extension not in self.config.supported_formats:
                print(f"❌ Unsupported file format: {file_extension}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ File validation failed: {e}")
            return False
    
    async def _parse_aasx_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse AASX file and extract AAS model"""
        try:
            file_path_obj = Path(file_path)
            file_extension = file_path_obj.suffix.lower()
            
            if file_extension == '.json':
                return await self._parse_json_file(file_path)
            elif file_extension == '.xml':
                return await self._parse_xml_file(file_path)
            elif file_extension == '.aasx':
                return await self._parse_aasx_package(file_path)
            else:
                print(f"❌ Unsupported file format for parsing: {file_extension}")
                return None
                
        except Exception as e:
            print(f"❌ AASX file parsing failed: {e}")
            return None
    
    async def _parse_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse JSON AAS file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                aas_model = json.loads(content)
                
            # Validate basic structure
            if not isinstance(aas_model, dict):
                print("❌ Invalid JSON structure: root must be an object")
                return None
            
            return aas_model
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"❌ JSON file reading failed: {e}")
            return None
    
    async def _parse_xml_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse XML AAS file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Convert XML to dictionary (simplified)
            aas_model = self._xml_to_dict(root)
            
            return aas_model
            
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return None
        except Exception as e:
            print(f"❌ XML file reading failed: {e}")
            return None
    
    async def _parse_aasx_package(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse AASX package file"""
        try:
            # AASX is a ZIP-based format, simplified parsing for demonstration
            # In practice, this would use proper AASX libraries
            
            # For now, return a mock AAS model
            aas_model = {
                'id': f"aasx_{Path(file_path).stem}",
                'version': self.config.aas_version,
                'assetAdministrationShell': {
                    'id': f"aas_{Path(file_path).stem}",
                    'assetInformation': {
                        'assetKind': 'Instance'
                    }
                },
                'submodels': [],
                'conceptDescriptions': [],
                'imported_from': file_path,
                'parsed_at': datetime.now().isoformat()
            }
            
            return aas_model
            
        except Exception as e:
            print(f"❌ AASX package parsing failed: {e}")
            return None
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add element attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add element text if it exists and is not just whitespace
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Process child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            child_tag = child.tag
            
            if child_tag in result:
                # If tag already exists, convert to list
                if not isinstance(result[child_tag], list):
                    result[child_tag] = [result[child_tag]]
                result[child_tag].append(child_data)
            else:
                result[child_tag] = child_data
        
        return result
    
    async def _validate_aas_model(self, aas_model: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AAS model structure"""
        try:
            errors = []
            
            # Check required elements
            for element in self.config.required_elements:
                if element not in aas_model:
                    errors.append(f"Missing required element: {element}")
                elif aas_model[element] is None:
                    errors.append(f"Required element is null: {element}")
            
            # Check AAS version compatibility
            if 'version' in aas_model:
                version = aas_model['version']
                if version != self.config.aas_version:
                    errors.append(f"Version mismatch: expected {self.config.aas_version}, got {version}")
            
            # Check for basic structure
            if 'id' not in aas_model:
                errors.append("Missing AAS ID")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {e}"]
            }
    
    async def _create_backup(self, file_path: str):
        """Create backup of processed file"""
        try:
            if not self.config.backup_enabled:
                return
            
            backup_path = Path(self.config.backup_directory)
            file_name = Path(file_path).name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"{timestamp}_{file_name}"
            
            # Copy file to backup directory
            import shutil
            shutil.copy2(file_path, backup_file)
            
            # Update backup metrics
            self.metrics.backups_created += 1
            backup_size_mb = backup_file.stat().st_size / (1024 * 1024)
            self.metrics.backup_size_mb += backup_size_mb
            
            print(f"💾 Backup created: {backup_file}")
            
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            self.metrics.backups_failed += 1
    
    async def _cache_file_data(self, file_path: str, aas_model: Dict[str, Any]):
        """Cache file data"""
        try:
            if not self.config.caching_enabled:
                return
            
            cache_key = str(Path(file_path).absolute())
            cache_entry = {
                'data': aas_model,
                'file_path': file_path,
                'cached_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=self.config.cache_ttl_hours)
            }
            
            self.file_cache[cache_key] = cache_entry
            self.metrics.cache_size = len(self.file_cache)
            
        except Exception as e:
            print(f"⚠️  Failed to cache file data: {e}")
    
    async def get_aas_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get AAS model by ID"""
        try:
            return self.aas_models.get(model_id)
            
        except Exception as e:
            print(f"❌ Failed to get AAS model: {e}")
            return None
    
    async def get_all_aas_models(self) -> List[Dict[str, Any]]:
        """Get all AAS models"""
        try:
            return list(self.aas_models.values())
            
        except Exception as e:
            print(f"❌ Failed to get all AAS models: {e}")
            return []
    
    async def search_aas_models(self, query: str) -> List[Dict[str, Any]]:
        """Search AAS models by query"""
        try:
            results = []
            query_lower = query.lower()
            
            for model in self.aas_models.values():
                # Simple text search in model data
                model_text = json.dumps(model, default=str).lower()
                if query_lower in model_text:
                    results.append(model)
            
            return results
            
        except Exception as e:
            print(f"❌ AAS model search failed: {e}")
            return []
    
    async def export_aas_model(self, model_id: str, format: str = 'json') -> Optional[str]:
        """Export AAS model to specified format"""
        try:
            model = self.aas_models.get(model_id)
            if not model:
                print(f"❌ AAS model not found: {model_id}")
                return None
            
            if format.lower() == 'json':
                return json.dumps(model, indent=2, default=str)
            elif format.lower() == 'xml':
                # Convert to XML (simplified)
                return self._dict_to_xml(model)
            else:
                print(f"❌ Unsupported export format: {format}")
                return None
                
        except Exception as e:
            print(f"❌ AAS model export failed: {e}")
            return None
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str = 'aas') -> str:
        """Convert dictionary to XML string (simplified)"""
        try:
            # Simplified XML conversion for demonstration
            xml_parts = [f'<{root_name}>']
            
            for key, value in data.items():
                if isinstance(value, dict):
                    xml_parts.append(self._dict_to_xml(value, key))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            xml_parts.append(self._dict_to_xml(item, key))
                        else:
                            xml_parts.append(f'<{key}>{item}</{key}>')
                else:
                    xml_parts.append(f'<{key}>{value}</{key}>')
            
            xml_parts.append(f'</{root_name}>')
            return ''.join(xml_parts)
            
        except Exception as e:
            print(f"⚠️  XML conversion failed: {e}")
            return f'<{root_name}>Error converting to XML</{root_name}>'
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and metrics"""
        try:
            return {
                'processing_active': self.processing_active,
                'queue_size': self.import_queue.qsize(),
                'processed_files_count': len(self.processed_files),
                'aas_models_count': len(self.aas_models),
                'cache_size': len(self.file_cache),
                'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
                'metrics': self.metrics.__dict__
            }
            
        except Exception as e:
            print(f"❌ Failed to get integration status: {e}")
            return {'error': str(e)}
    
    async def clear_cache(self):
        """Clear the file cache"""
        try:
            self.file_cache.clear()
            self.metrics.cache_size = 0
            self.metrics.cache_evictions += len(self.file_cache)
            print("🗑️  File cache cleared")
            
        except Exception as e:
            print(f"❌ Failed to clear cache: {e}")
    
    async def reset_metrics(self):
        """Reset integration metrics"""
        try:
            self.metrics = AASXMetrics()
            print("🔄 Integration metrics reset")
            
        except Exception as e:
            print(f"❌ Failed to reset metrics: {e}")





