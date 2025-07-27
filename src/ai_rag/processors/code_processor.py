"""
Code processor for programming language files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from .base_processor import BaseDataProcessor


class CodeProcessor(BaseDataProcessor):
    """Processor for code files (Python, JavaScript, C++, etc.)."""
    
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        code_extensions = [
            # Python
            '.py', '.pyx', '.pyi', '.pyw',
            # JavaScript/TypeScript
            '.js', '.jsx', '.ts', '.tsx',
            # Java
            '.java', '.class',
            # C/C++
            '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx',
            # C#
            '.cs',
            # Go
            '.go',
            # Rust
            '.rs',
            # PHP
            '.php',
            # Ruby
            '.rb',
            # Swift
            '.swift',
            # Kotlin
            '.kt', '.kts',
            # Scala
            '.scala',
            # R
            '.r',
            # MATLAB
            '.m',
            # Shell scripts
            '.sh', '.bash', '.zsh', '.fish',
            # PowerShell
            '.ps1', '.psm1',
            # Batch
            '.bat', '.cmd',
            # Makefile
            'Makefile', 'makefile',
            # Markdown
            '.md', '.markdown',
            # HTML
            '.html', '.htm', '.xhtml',
            # CSS
            '.css', '.scss', '.sass', '.less',
            # SQL
            '.sql',
            # Docker
            'Dockerfile', '.dockerfile',
            # Terraform
            '.tf', '.tfvars',
            # Other code-related
            '.txt', '.log'
        ]
        
        # Only process files that are clearly code files
        # Don't process data files that should be handled by specialized processors
        return file_path.suffix.lower() in code_extensions or file_path.name in code_extensions
    
    def process(self, project_id: str, file_info: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Process code file."""
        try:
            self.logger.info(f"Processing code file: {file_path}")
            
            # Extract meaningful text from code
            text_content = self._extract_text_from_code(file_path)
            
            if not text_content:
                return self._create_skipped_result(file_info, file_path, "No meaningful content extracted from code file")
            
            self.logger.info(f"Extracted code text content: {text_content[:100]}...")
            
            # Generate embedding
            embedding = self._generate_embedding(text_content, file_path)
            if not embedding:
                return self._create_error_result(file_info, file_path, "Failed to generate embedding for code file")
            
            # Get code metadata
            code_metadata = self._get_code_metadata(file_path)
            
            # Prepare metadata
            metadata = {
                'project_id': project_id,
                'file_id': file_info.get('file_id'),
                'source_file': file_path.name,
                'content_type': 'code',
                'content_preview': text_content[:200] + "..." if len(text_content) > 200 else text_content,
                'file_path': str(file_path),
                'embedding_model': self.text_embedding_manager.get_model().get_model_info() if self.text_embedding_manager else None,
                'code_type': file_path.suffix.lower(),
                'text_length': len(text_content),
                'code_metadata': code_metadata
            }
            
            # Upload to vector database
            success = self._upload_to_vector_db(embedding, metadata, file_path)
            if not success:
                return self._create_error_result(file_info, file_path, "Failed to upload code to vector database")
            
            # Save embedding locally
            vector_data = {
                'id': self.vector_db.generate_vector_id(project_id, file_path.name),
                'vector': embedding,
                'payload': metadata
            }
            self._save_embedding_locally(project_id, file_path, vector_data)
            
            return self._create_success_result(file_info, file_path, vector_data['id'])
            
        except Exception as e:
            self.logger.error(f"Exception processing code {file_path}: {e}")
            return self._create_error_result(file_info, file_path, str(e))
    
    def _extract_text_from_code(self, file_path: Path) -> Optional[str]:
        """Extract meaningful text from code file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return None
            
            # Extract meaningful content based on file type
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.py':
                return self._extract_python_content(content)
            elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
                return self._extract_javascript_content(content)
            elif file_extension in ['.java']:
                return self._extract_java_content(content)
            elif file_extension in ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx']:
                return self._extract_cpp_content(content)
            elif file_extension in ['.cs']:
                return self._extract_csharp_content(content)
            elif file_extension in ['.md', '.markdown']:
                return self._extract_markdown_content(content)
            elif file_extension in ['.json', '.yaml', '.yml']:
                return self._extract_config_content(content, file_extension)
            elif file_extension in ['.xml', '.html', '.htm']:
                return self._extract_xml_content(content)
            elif file_extension in ['.sql']:
                return self._extract_sql_content(content)
            else:
                return self._extract_generic_content(content)
                
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return self._extract_generic_content(content)
            except Exception as e:
                self.logger.error(f"Failed to read code file {file_path}: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to extract text from code file {file_path}: {e}")
            return None
    
    def _extract_python_content(self, content: str) -> str:
        """Extract meaningful content from Python code."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Skip empty lines and comments
                if not line.startswith('import ') and not line.startswith('from '):
                    # Include function definitions, class definitions, and docstrings
                    if any(keyword in line for keyword in ['def ', 'class ', '"""', "'''"]):
                        meaningful_lines.append(line)
                    elif line.startswith('    ') or line.startswith('\t'):
                        # Include indented code (function bodies, etc.)
                        meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_javascript_content(self, content: str) -> str:
        """Extract meaningful content from JavaScript/TypeScript code."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                # Skip comments
                if any(keyword in line for keyword in ['function ', 'class ', 'const ', 'let ', 'var ', 'export ', 'import ']):
                    meaningful_lines.append(line)
                elif line.startswith('    ') or line.startswith('\t'):
                    # Include indented code
                    meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_java_content(self, content: str) -> str:
        """Extract meaningful content from Java code."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                # Skip comments
                if any(keyword in line for keyword in ['public ', 'private ', 'protected ', 'class ', 'interface ', 'enum ', 'import ', 'package ']):
                    meaningful_lines.append(line)
                elif line.startswith('    ') or line.startswith('\t'):
                    # Include indented code
                    meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_cpp_content(self, content: str) -> str:
        """Extract meaningful content from C++ code."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                # Skip comments
                if any(keyword in line for keyword in ['class ', 'struct ', 'enum ', 'namespace ', '#include ', 'using ', 'template<']):
                    meaningful_lines.append(line)
                elif line.startswith('    ') or line.startswith('\t'):
                    # Include indented code
                    meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_csharp_content(self, content: str) -> str:
        """Extract meaningful content from C# code."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                # Skip comments
                if any(keyword in line for keyword in ['public ', 'private ', 'protected ', 'class ', 'interface ', 'enum ', 'using ', 'namespace ']):
                    meaningful_lines.append(line)
                elif line.startswith('    ') or line.startswith('\t'):
                    # Include indented code
                    meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_markdown_content(self, content: str) -> str:
        """Extract meaningful content from Markdown."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Include headers, lists, and regular text
                if line.startswith('#') or line.startswith('- ') or line.startswith('* ') or line.startswith('1. '):
                    meaningful_lines.append(line)
                elif not line.startswith('```') and not line.startswith('---'):
                    # Include regular text, skip code blocks and separators
                    meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_config_content(self, content: str, file_type: str) -> str:
        """Extract meaningful content from configuration files."""
        if file_type == '.json':
            # For JSON, include the structure
            return content
        elif file_type in ['.yaml', '.yml']:
            # For YAML, include the structure
            return content
        else:
            return self._extract_generic_content(content)
    
    def _extract_xml_content(self, content: str) -> str:
        """Extract meaningful content from XML/HTML."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<!--'):
                # Skip comments
                if '<' in line and '>' in line:
                    meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_sql_content(self, content: str) -> str:
        """Extract meaningful content from SQL."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('/*'):
                # Skip comments
                if any(keyword in line.upper() for keyword in ['SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE ', 'ALTER ', 'DROP ', 'TABLE ', 'VIEW ', 'INDEX ']):
                    meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _extract_generic_content(self, content: str) -> str:
        """Extract meaningful content from generic text files."""
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//') and not line.startswith('/*'):
                # Skip comments
                meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines)
    
    def _get_code_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get code file metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            metadata = {
                'file_size': len(content),
                'total_lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'language': self._detect_language(file_path),
                'has_comments': any(line.strip().startswith(('#', '//', '/*', '--')) for line in lines),
                'has_functions': any('def ' in line or 'function ' in line or 'public ' in line for line in lines),
                'has_classes': any('class ' in line for line in lines)
            }
            
            return metadata
            
        except Exception as e:
            self.logger.warning(f"Failed to get code metadata for {file_path}: {e}")
            return {
                'language': self._detect_language(file_path),
                'error': str(e)
            }
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension = file_path.suffix.lower()
        
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'React JSX',
            '.ts': 'TypeScript',
            '.tsx': 'React TypeScript',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.h': 'C/C++ Header',
            '.hpp': 'C++ Header',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.m': 'MATLAB',
            '.sh': 'Shell Script',
            '.ps1': 'PowerShell',
            '.bat': 'Batch Script',
            '.sql': 'SQL',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.html': 'HTML',
            '.htm': 'HTML',
            '.css': 'CSS',
            '.md': 'Markdown',
            '.markdown': 'Markdown'
        }
        
        return language_map.get(extension, 'Unknown') 