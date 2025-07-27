"""
Structured data processor for JSON and YAML files.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any
from .base_processor import BaseDataProcessor


class StructuredDataProcessor(BaseDataProcessor):
    """Processor for structured data files (JSON/YAML)."""
    
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        # Don't process graph files - they should be handled by GraphDataProcessor
        if '_graph' in file_path.name.lower():
            return False
        return file_path.suffix.lower() in ['.json', '.yaml', '.yml']
    
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Process structured data file."""
        try:
            self.logger.info(f"Processing structured data file: {file_path}")
            
            # Load data based on file type
            data = self._load_data(file_path)
            if not data:
                return self._create_error_result(file_info, file_path, "Failed to load data")
            
            # Extract meaningful text from structured data
            text_content = self._extract_text_from_structured_data(data)
            
            self.logger.info(f"Extracted text content: {text_content[:100]}...")
            
            if not text_content:
                return self._create_skipped_result(file_info, file_path, "No extractable text content")
            
            # Generate embedding
            embedding = self._generate_embedding(text_content, file_path)
            if not embedding:
                return self._create_error_result(file_info, file_path, "Failed to generate embedding")
            
            # Prepare metadata
            metadata = {
                'project_id': project_id,
                'file_id': file_info.get('file_id'),
                'source_file': file_path.name,
                'content_type': 'structured_data',
                'content_preview': text_content[:200] + "..." if len(text_content) > 200 else text_content,
                'file_path': str(file_path),
                'embedding_model': self.text_embedding_manager.get_model().get_model_info() if self.text_embedding_manager else None
            }
            
            # Upload to vector database
            success = self._upload_to_vector_db(embedding, metadata, file_path)
            if not success:
                return self._create_error_result(file_info, file_path, "Failed to upload to vector database")
            
            # Save embedding locally
            vector_data = {
                'id': self.vector_db.generate_vector_id(project_id, file_path.name),
                'vector': embedding,
                'payload': metadata
            }
            self._save_embedding_locally(project_id, file_path, vector_data)
            
            return self._create_success_result(file_info, file_path, vector_data['id'])
            
        except Exception as e:
            self.logger.error(f"Exception processing {file_path}: {e}")
            return self._create_error_result(file_info, file_path, str(e))
    
    def _load_data(self, file_path: Path) -> Dict[str, Any]:
        """Load data from file based on its type."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    return json.load(f)
                elif file_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    self.logger.error(f"Unsupported file type: {file_path.suffix}")
                    return None
        except Exception as e:
            self.logger.error(f"Failed to load data from {file_path}: {e}")
            return None
    
    def _extract_text_from_structured_data(self, data: Dict[str, Any]) -> str:
        """Extract meaningful text from structured data."""
        text_parts = []
        
        # Extract from assets
        if 'assets' in data:
            for asset in data['assets']:
                asset_text = f"Asset: {asset.get('idShort', '')}"
                if asset.get('description'):
                    asset_text += f" - {asset['description']}"
                if asset.get('category'):
                    asset_text += f" (Category: {asset['category']})"
                if asset.get('kind'):
                    asset_text += f" (Kind: {asset['kind']})"
                text_parts.append(asset_text)
        
        # Extract from submodels
        if 'submodels' in data:
            for submodel in data['submodels']:
                submodel_text = f"Submodel: {submodel.get('idShort', '')}"
                if submodel.get('description'):
                    submodel_text += f" - {submodel['description']}"
                if submodel.get('category'):
                    submodel_text += f" (Category: {submodel['category']})"
                if submodel.get('kind'):
                    submodel_text += f" (Kind: {submodel['kind']})"
                text_parts.append(submodel_text)
        
        # Extract from asset-submodel relationships
        if 'assetSubmodelRelationships' in data:
            for rel in data['assetSubmodelRelationships']:
                rel_text = f"Relationship: {rel.get('relationship_type', '')} between asset and submodel"
                text_parts.append(rel_text)
        
        # Extract from file relationships
        if 'fileRelationships' in data:
            for rel in data['fileRelationships']:
                rel_text = f"File: {rel.get('element_idShort', '')} - {rel.get('file_path', '')}"
                text_parts.append(rel_text)
        
        # Extract from embedded files
        if 'embeddedFiles' in data:
            for file_path, file_info in data['embeddedFiles'].items():
                file_text = f"Embedded File: {file_info.get('filename', file_path)}"
                if file_info.get('type'):
                    file_text += f" (Type: {file_info['type']})"
                if file_info.get('size'):
                    file_text += f" (Size: {file_info['size']} bytes)"
                text_parts.append(file_text)
        
        # Extract from other relevant fields
        for key in ['aasVersion', 'namespaces']:
            if key in data:
                text_parts.append(f"{key}: {str(data[key])}")
        
        # If no meaningful content found, create a basic description
        if not text_parts:
            text_parts.append("AASX Digital Twin Asset Administration Shell")
            if 'assets' in data and data['assets']:
                asset_names = [asset.get('idShort', '') for asset in data['assets'] if asset.get('idShort')]
                if asset_names:
                    text_parts.append(f"Contains assets: {', '.join(asset_names)}")
            if 'submodels' in data and data['submodels']:
                submodel_names = [submodel.get('idShort', '') for submodel in data['submodels'] if submodel.get('idShort')]
                if submodel_names:
                    text_parts.append(f"Contains submodels: {', '.join(submodel_names)}")
        
        extracted_text = " ".join(text_parts)
        self.logger.info(f"Extracted text length: {len(extracted_text)} characters")
        return extracted_text 