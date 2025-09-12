"""
Image processor for image files with OCR capabilities.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base_processor import BaseDataProcessor


class ImageProcessor(BaseDataProcessor):
    """Processor for image files with OCR text extraction."""
    
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        return file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp']
    
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Process image file."""
        try:
            self.logger.info(f"Processing image file: {file_path}")
            
            # Extract text from image using OCR
            text_content = self._extract_text_from_image(file_path)
            
            if not text_content:
                return self._create_skipped_result(file_info, file_path, "No text content extracted from image")
            
            self.logger.info(f"Extracted image text content: {text_content[:100]}...")
            
            # Generate embedding
            embedding = self._generate_embedding(text_content, file_path)
            if not embedding:
                return self._create_error_result(file_info, file_path, "Failed to generate embedding for image")
            
            # Get image metadata
            image_metadata = self._get_image_metadata(file_path)
            
            # Prepare metadata
            metadata = {
                'project_id': project_id,
                'file_id': file_info.get('file_id'),
                'source_file': file_path.name,
                'content_type': 'image',
                'content_preview': text_content[:200] + "..." if len(text_content) > 200 else text_content,
                'file_path': str(file_path),
                'embedding_model': self.text_embedding_manager.get_model().get_model_info() if self.text_embedding_manager else None,
                'image_type': file_path.suffix.lower(),
                'text_length': len(text_content),
                'image_metadata': image_metadata
            }
            
            # Upload to vector database
            success = self._upload_to_vector_db(embedding, metadata, file_path)
            if not success:
                return self._create_error_result(file_info, file_path, "Failed to upload image to vector database")
            
            # Save embedding locally
            vector_data = {
                'id': file_info.get('file_id'),  # Use file_id directly for deterministic mapping
                'vector': embedding,
                'payload': metadata
            }
            self._save_embedding_locally(project_id, file_path, vector_data)
            
            return self._create_success_result(file_info, file_path, vector_data['id'])
            
        except Exception as e:
            self.logger.error(f"Exception processing image {file_path}: {e}")
            return self._create_error_result(file_info, file_path, str(e))
    
    def _extract_text_from_image(self, file_path: Path) -> Optional[str]:
        """Extract text from image using OCR."""
        try:
            # Try Tesseract OCR first
            text = self._extract_text_with_tesseract(file_path)
            if text:
                return text
            
            # Try EasyOCR as fallback
            text = self._extract_text_with_easyocr(file_path)
            if text:
                return text
            
            # Try PaddleOCR as final fallback
            text = self._extract_text_with_paddleocr(file_path)
            if text:
                return text
            
            self.logger.warning(f"No OCR text extracted from {file_path}")
            return None
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed for {file_path}: {e}")
            return None
    
    def _extract_text_with_tesseract(self, file_path: Path) -> Optional[str]:
        """Extract text using Tesseract OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            # Open image
            image = Image.open(file_path)
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            return text.strip() if text.strip() else None
            
        except ImportError:
            self.logger.warning("pytesseract not available")
            return None
        except Exception as e:
            self.logger.error(f"Tesseract OCR failed for {file_path}: {e}")
            return None
    
    def _extract_text_with_easyocr(self, file_path: Path) -> Optional[str]:
        """Extract text using EasyOCR."""
        try:
            import easyocr
            
            # Initialize reader (first time will download models)
            reader = easyocr.Reader(['en'])
            
            # Read text from image
            results = reader.readtext(str(file_path))
            
            # Extract text from results
            text_parts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only include high-confidence results
                    text_parts.append(text)
            
            return ' '.join(text_parts) if text_parts else None
            
        except ImportError:
            self.logger.warning("easyocr not available")
            return None
        except Exception as e:
            self.logger.error(f"EasyOCR failed for {file_path}: {e}")
            return None
    
    def _extract_text_with_paddleocr(self, file_path: Path) -> Optional[str]:
        """Extract text using PaddleOCR - disabled due to dependency conflicts."""
        self.logger.warning("PaddleOCR disabled due to PyMuPDF dependency conflicts")
        return None
    
    def _get_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get basic image metadata."""
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                metadata = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
                
                # Try to get additional metadata
                try:
                    if hasattr(img, 'info'):
                        metadata['info'] = dict(img.info)
                except:
                    pass
                
                return metadata
                
        except Exception as e:
            self.logger.warning(f"Failed to get image metadata for {file_path}: {e}")
            return {
                'format': file_path.suffix.lower(),
                'error': str(e)
            }
    
    def _extract_image_features(self, file_path: Path) -> Optional[List[float]]:
        """Extract image features for potential future use."""
        try:
            # This could be used for image similarity search in the future
            # For now, we'll just extract basic features using PIL
            from PIL import Image
            import numpy as np
            
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to standard size
                img = img.resize((224, 224))
                
                # Convert to numpy array and normalize
                img_array = np.array(img) / 255.0
                
                # Flatten for basic feature extraction
                features = img_array.flatten()
                
                # Take first 1000 features (or all if less)
                return features[:1000].tolist()
                
        except Exception as e:
            self.logger.warning(f"Failed to extract image features for {file_path}: {e}")
            return None 