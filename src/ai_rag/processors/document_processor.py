"""
Document processor for PDF and other document files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from .base_processor import BaseDataProcessor


class DocumentProcessor(BaseDataProcessor):
    """Processor for document files (PDF, DOCX, TXT, etc.)."""
    
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        return file_path.suffix.lower() in ['.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt']
    
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Process document file."""
        try:
            self.logger.info(f"Processing document file: {file_path}")
            
            # Extract text based on file type
            text_content = self._extract_text_from_document(file_path)
            
            # For PDFs, also extract image information
            images_info = []
            if file_path.suffix.lower() == '.pdf':
                images_info = self._extract_images_from_pdf(file_path)
                if images_info:
                    self.logger.info(f"Found {len(images_info)} images in PDF")
            
            # If no text content but images found, create descriptive content
            if not text_content and images_info:
                text_content = f"Document contains {len(images_info)} images"
                for i, img in enumerate(images_info[:3]):  # Limit to first 3 images
                    text_content += f"\nImage {i+1}: {img['width']}x{img['height']} pixels, {img['format']} format"
                if len(images_info) > 3:
                    text_content += f"\n... and {len(images_info) - 3} more images"
            
            # If still no content, create a basic description
            if not text_content:
                text_content = f"Document file: {file_path.name}"
                if images_info:
                    text_content += f" (contains {len(images_info)} images)"
                else:
                    text_content += " (minimal text content)"
            
            self.logger.info(f"Extracted document content: {text_content[:100]}...")
            
            # Generate embedding
            embedding = self._generate_embedding(text_content, file_path)
            if not embedding:
                return self._create_error_result(file_info, file_path, "Failed to generate embedding for document")
            
            # Prepare enhanced metadata
            metadata = {
                'project_id': project_id,
                'file_id': file_info.get('file_id'),
                'source_file': file_path.name,
                'content_type': 'document',
                'content_preview': text_content[:200] + "..." if len(text_content) > 200 else text_content,
                'file_path': str(file_path),
                'embedding_model': self.text_embedding_manager.get_model().get_model_info() if self.text_embedding_manager else None,
                'document_type': file_path.suffix.lower(),
                'text_length': len(text_content),
                'has_images': len(images_info) > 0,
                'image_count': len(images_info),
                'images_info': images_info[:5] if images_info else [],  # Limit to first 5 images
                'processing_notes': []
            }
            
            # Add processing notes
            if len(text_content) < 50:
                metadata['processing_notes'].append("Minimal text content detected")
            if images_info:
                metadata['processing_notes'].append(f"Extracted {len(images_info)} images")
            
            # Upload to vector database
            success = self._upload_to_vector_db(embedding, metadata, file_path)
            if not success:
                return self._create_error_result(file_info, file_path, "Failed to upload document to vector database")
            
            # Save embedding locally
            vector_data = {
                'id': self.vector_db.generate_vector_id(project_id, file_path.name),
                'vector': embedding,
                'payload': metadata
            }
            self._save_embedding_locally(project_id, file_path, vector_data)
            
            return self._create_success_result(file_info, file_path, vector_data['id'])
            
        except Exception as e:
            self.logger.error(f"Exception processing document {file_path}: {e}")
            return self._create_error_result(file_info, file_path, str(e))
    
    def _extract_text_from_document(self, file_path: Path) -> Optional[str]:
        """Extract text from document based on its type."""
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                return self._extract_text_from_docx(file_path)
            elif file_extension == '.doc':
                return self._extract_text_from_doc(file_path)
            elif file_extension == '.txt':
                return self._extract_text_from_txt(file_path)
            elif file_extension == '.rtf':
                return self._extract_text_from_rtf(file_path)
            elif file_extension == '.odt':
                return self._extract_text_from_odt(file_path)
            else:
                self.logger.error(f"Unsupported document type: {file_extension}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract text from {file_path}: {e}")
            return None
    
    def _extract_text_from_pdf(self, file_path: Path) -> Optional[str]:
        """Extract text from PDF file."""
        try:
            # Try PyPDF2 first
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    
                    # If minimal text, try to extract more metadata
                    if len(text.strip()) < 50:  # Very short text
                        self.logger.info(f"Minimal text extracted from PDF: '{text.strip()}'")
                        # Add some context about the PDF structure
                        text += f"\nPDF contains {len(pdf_reader.pages)} pages"
                        if len(pdf_reader.pages) > 0:
                            text += f"\nFirst page has {len(pdf_reader.pages[0].get('/Resources', {}).get('/XObject', {}))} objects"
                    
                    return text.strip() if text.strip() else None
            except ImportError:
                self.logger.warning("PyPDF2 not available, trying pdfplumber")
            
            # Try pdfplumber as fallback
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    image_count = 0
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        
                        # Count images on this page
                        if hasattr(page, 'images'):
                            image_count += len(page.images)
                    
                    # If minimal text but images found, add image information
                    if len(text.strip()) < 50 and image_count > 0:
                        text += f"\nPDF contains {image_count} images across {len(pdf.pages)} pages"
                        text += "\nThis appears to be an image-heavy document"
                    
                    return text.strip() if text.strip() else None
            except ImportError:
                self.logger.warning("pdfplumber not available, trying pymupdf")
            
            # Try pymupdf as final fallback
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                image_count = 0
                
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Count images on this page
                    image_list = page.get_images()
                    image_count += len(image_list)
                
                # If minimal text but images found, add image information
                if len(text.strip()) < 50 and image_count > 0:
                    text += f"\nPDF contains {image_count} images across {len(doc)} pages"
                    text += "\nThis appears to be an image-heavy document"
                
                doc.close()
                return text.strip() if text.strip() else None
            except ImportError:
                self.logger.error("No PDF extraction library available (PyPDF2, pdfplumber, or pymupdf)")
                return None
                
        except Exception as e:
            self.logger.error(f"PDF extraction failed for {file_path}: {e}")
            return None
    
    def _extract_images_from_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract images from PDF file."""
        images = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            
            for page_num, page in enumerate(doc):
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Convert to PIL Image for processing
                        from PIL import Image
                        import io
                        
                        img_data = pix.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        image_info = {
                            'page': page_num + 1,
                            'index': img_index,
                            'width': pil_image.width,
                            'height': pil_image.height,
                            'format': pil_image.format,
                            'mode': pil_image.mode,
                            'size_bytes': len(img_data)
                        }
                        
                        images.append(image_info)
                        pix = None  # Free memory
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
                        continue
            
            doc.close()
            return images
            
        except ImportError:
            self.logger.warning("PyMuPDF not available for image extraction")
            return []
        except Exception as e:
            self.logger.error(f"PDF image extraction failed for {file_path}: {e}")
            return []
    
    def _extract_text_from_docx(self, file_path: Path) -> Optional[str]:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip() if text.strip() else None
            
        except ImportError:
            self.logger.error("python-docx library not available for DOCX extraction")
            return None
        except Exception as e:
            self.logger.error(f"DOCX extraction failed for {file_path}: {e}")
            return None
    
    def _extract_text_from_doc(self, file_path: Path) -> Optional[str]:
        """Extract text from DOC file."""
        try:
            # Try using antiword if available
            import subprocess
            result = subprocess.run(['antiword', str(file_path)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip() if result.stdout.strip() else None
            else:
                self.logger.warning("antiword failed, trying textract")
                
        except (ImportError, FileNotFoundError):
            self.logger.warning("antiword not available, trying textract")
        
        # Try textract as fallback
        try:
            import textract
            text = textract.process(str(file_path)).decode('utf-8')
            return text.strip() if text.strip() else None
            
        except ImportError:
            self.logger.error("textract library not available for DOC extraction")
            return None
        except Exception as e:
            self.logger.error(f"DOC extraction failed for {file_path}: {e}")
            return None
    
    def _extract_text_from_txt(self, file_path: Path) -> Optional[str]:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text.strip() if text.strip() else None
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                return text.strip() if text.strip() else None
            except Exception as e:
                self.logger.error(f"TXT extraction failed for {file_path}: {e}")
                return None
        except Exception as e:
            self.logger.error(f"TXT extraction failed for {file_path}: {e}")
            return None
    
    def _extract_text_from_rtf(self, file_path: Path) -> Optional[str]:
        """Extract text from RTF file."""
        try:
            import striprtf
            with open(file_path, 'r', encoding='utf-8') as f:
                rtf_content = f.read()
            text = striprtf.rtf_to_text(rtf_content)
            return text.strip() if text.strip() else None
            
        except ImportError:
            self.logger.error("striprtf library not available for RTF extraction")
            return None
        except Exception as e:
            self.logger.error(f"RTF extraction failed for {file_path}: {e}")
            return None
    
    def _extract_text_from_odt(self, file_path: Path) -> Optional[str]:
        """Extract text from ODT file."""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Find the content.xml file
                content_file = None
                for name in zip_file.namelist():
                    if name.endswith('content.xml'):
                        content_file = name
                        break
                
                if content_file:
                    with zip_file.open(content_file) as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        
                        # Extract text from text:p elements
                        text_elements = []
                        for elem in root.iter():
                            if elem.tag.endswith('}p'):  # paragraph
                                text = ''.join(elem.itertext()).strip()
                                if text:
                                    text_elements.append(text)
                        
                        return '\n'.join(text_elements) if text_elements else None
                else:
                    self.logger.error(f"No content.xml found in ODT file: {file_path}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"ODT extraction failed for {file_path}: {e}")
            return None 