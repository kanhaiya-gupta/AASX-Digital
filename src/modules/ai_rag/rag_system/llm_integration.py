"""
LLM Integration for RAG System
Provides integration with various language models for text generation and analysis.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from ..embedding_models.text_embeddings import TextEmbeddingManager


class LLMIntegration:
    """Integration with various language models for RAG operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize LLM integration.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # LLM settings
        self.model_provider = self.config.get('model_provider', 'openai')
        self.model_name = self.config.get('model_name', 'gpt-3.5-turbo')
        self.api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.max_tokens = self.config.get('max_tokens', 1000)
        self.temperature = self.config.get('temperature', 0.7)
        
        # Initialize model client
        self.client = self._initialize_client()
        
        self.logger.info(f"✅ LLM Integration initialized with {self.model_provider}")
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        try:
            if self.model_provider == 'openai':
                return self._initialize_openai_client()
            elif self.model_provider == 'anthropic':
                return self._initialize_anthropic_client()
            elif self.model_provider == 'local':
                return self._initialize_local_client()
            else:
                self.logger.warning(f"Unknown model provider: {self.model_provider}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM client: {e}")
            return None
    
    def _initialize_openai_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            if self.api_key:
                openai.api_key = self.api_key
                return openai
            else:
                self.logger.error("OpenAI API key not found")
                return None
        except ImportError:
            self.logger.error("OpenAI library not installed")
            return None
    
    def _initialize_anthropic_client(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
            if self.api_key:
                return anthropic.Anthropic(api_key=self.api_key)
            else:
                self.logger.error("Anthropic API key not found")
                return None
        except ImportError:
            self.logger.error("Anthropic library not installed")
            return None
    
    def _initialize_local_client(self):
        """Initialize local model client."""
        try:
            # Placeholder for local model integration
            self.logger.info("Local model integration not yet implemented")
            return None
        except Exception as e:
            self.logger.error(f"Failed to initialize local client: {e}")
            return None
    
    def generate_text(
        self, 
        prompt: str, 
        context: str = None,
        system_message: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the configured LLM.
        
        Args:
            prompt: User prompt
            context: Additional context
            system_message: System message for the model
            **kwargs: Additional parameters
            
        Returns:
            Generated text and metadata
        """
        try:
            if not self.client:
                return self._create_error_response("LLM client not available")
            
            # Prepare the full prompt
            full_prompt = self._prepare_prompt(prompt, context, system_message)
            
            # Generate response based on provider
            if self.model_provider == 'openai':
                response = self._generate_openai_response(full_prompt, **kwargs)
            elif self.model_provider == 'anthropic':
                response = self._generate_anthropic_response(full_prompt, **kwargs)
            else:
                response = self._create_error_response(f"Unsupported model provider: {self.model_provider}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            return self._create_error_response(str(e))
    
    def _prepare_prompt(self, prompt: str, context: str = None, system_message: str = None) -> str:
        """Prepare the full prompt with context and system message."""
        parts = []
        
        if system_message:
            parts.append(f"System: {system_message}")
        
        if context:
            parts.append(f"Context: {context}")
        
        parts.append(f"User: {prompt}")
        
        return "\n\n".join(parts)
    
    def _generate_openai_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        try:
            response = self.client.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature)
            )
            
            generated_text = response.choices[0].message.content
            
            return {
                'status': 'success',
                'text': generated_text,
                'model': self.model_name,
                'provider': 'openai',
                'usage': response.usage.to_dict() if hasattr(response, 'usage') else {},
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return self._create_error_response(f"OpenAI error: {str(e)}")
    
    def _generate_anthropic_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Anthropic."""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            generated_text = response.content[0].text
            
            return {
                'status': 'success',
                'text': generated_text,
                'model': self.model_name,
                'provider': 'anthropic',
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic generation failed: {e}")
            return self._create_error_response(f"Anthropic error: {str(e)}")
    
    def analyze_text(self, text: str, analysis_type: str = 'general') -> Dict[str, Any]:
        """
        Analyze text using the LLM.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis ('general', 'sentiment', 'summary', 'key_points')
            
        Returns:
            Analysis results
        """
        try:
            if analysis_type == 'sentiment':
                prompt = f"Analyze the sentiment of the following text and provide a brief explanation:\n\n{text}"
            elif analysis_type == 'summary':
                prompt = f"Provide a concise summary of the following text:\n\n{text}"
            elif analysis_type == 'key_points':
                prompt = f"Extract the key points from the following text:\n\n{text}"
            else:
                prompt = f"Analyze the following text and provide insights:\n\n{text}"
            
            return self.generate_text(prompt)
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}")
            return self._create_error_response(str(e))
    
    def generate_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        """
        Generate embeddings for texts using secure TextEmbeddingManager.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Embeddings and metadata
        """
        try:
            # Use secure TextEmbeddingManager instead of direct API calls
            embedding_manager = TextEmbeddingManager()
            model = embedding_manager.get_model()
            
            embeddings = []
            for text in texts:
                embedding = model.embed_text(text)
                if embedding:
                    embeddings.append(embedding)
                else:
                    self.logger.error(f"Failed to generate embedding for text: {text[:50]}...")
                    return self._create_error_response(f"Failed to generate embedding for text")
            
            return {
                'status': 'success',
                'embeddings': embeddings,
                'model': model.model_name if hasattr(model, 'model_name') else 'text-embedding-ada-002',
                'provider': 'secure_embedding_manager',
                'count': len(embeddings),
                'generated_at': datetime.now().isoformat()
            }
                
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            return self._create_error_response(str(e))
    

    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            'status': 'error',
            'error': error_message,
            'generated_at': datetime.now().isoformat()
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update LLM configuration."""
        self.config.update(new_config)
        
        # Update instance variables
        self.model_provider = self.config.get('model_provider', 'openai')
        self.model_name = self.config.get('model_name', 'gpt-3.5-turbo')
        self.api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.max_tokens = self.config.get('max_tokens', 1000)
        self.temperature = self.config.get('temperature', 0.7)
        
        # Reinitialize client
        self.client = self._initialize_client()
        
        self.logger.info("LLM configuration updated")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the LLM connection."""
        try:
            if not self.client:
                return {'status': 'error', 'message': 'Client not initialized'}
            
            # Simple test prompt
            test_response = self.generate_text("Hello, this is a test message.")
            
            if test_response.get('status') == 'success':
                return {'status': 'success', 'message': 'Connection test passed'}
            else:
                return {'status': 'error', 'message': 'Connection test failed'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Connection test failed: {str(e)}'}

