"""
Image Embeddings Module

This module provides embedding capabilities for image data using various
vision models and image processing techniques. It supports multiple image
formats and can handle both single images and batches of images.
"""

import asyncio
import logging
from typing import List, Optional, Tuple, Union, Dict, Any
from dataclasses import dataclass
import numpy as np
from PIL import Image, ImageOps
import io
import base64
import torch
import torchvision.transforms as transforms
from transformers import CLIPProcessor, CLIPModel, AutoProcessor, AutoModel
import requests

from .base_embeddings import BaseEmbeddingModel

logger = logging.getLogger(__name__)


@dataclass
class ImageMetadata:
    """Metadata for image content."""
    width: int
    height: int
    format: str
    mode: str
    file_size: Optional[int] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None


class ImageEmbeddingModel(BaseEmbeddingModel):
    """
    Image embedding model using various vision models.
    
    Supports multiple embedding approaches:
    - CLIP (Contrastive Language-Image Pre-training)
    - Vision Transformers (ViT)
    - ResNet-based models
    - Custom vision models
    """
    
    def __init__(self,
                 model_name: str = "openai/clip-vit-base-patch32",
                 embedding_dimension: int = 512,
                 image_size: Tuple[int, int] = (224, 224),
                 use_gpu: bool = False,
                 normalize_embeddings: bool = True,
                 preprocessing_pipeline: str = "clip"):
        """
        Initialize the image embedding model.
        
        Args:
            model_name: Name of the vision model to use
            embedding_dimension: Dimension of the output embeddings
            image_size: Target size for image processing (width, height)
            use_gpu: Whether to use GPU acceleration
            normalize_embeddings: Whether to normalize embeddings
            preprocessing_pipeline: Preprocessing pipeline to use
        """
        super().__init__(embedding_dimension=embedding_dimension)
        
        self.model_name = model_name
        self.image_size = image_size
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.normalize_embeddings = normalize_embeddings
        self.preprocessing_pipeline = preprocessing_pipeline
        
        # Initialize model and processor
        self.model = None
        self.processor = None
        self.device = torch.device("cuda" if self.use_gpu else "cpu")
        
        # Initialize the model
        self._initialize_model()
        
        logger.info(f"Initialized ImageEmbeddingModel with {model_name} on {self.device}")
    
    def _initialize_model(self):
        """Initialize the vision model and processor."""
        try:
            if "clip" in self.model_name.lower():
                self._initialize_clip_model()
            else:
                self._initialize_generic_vision_model()
                
        except Exception as e:
            logger.error(f"Error initializing image model {self.model_name}: {e}")
            # Fallback to a simpler model
            self._initialize_fallback_model()
    
    def _initialize_clip_model(self):
        """Initialize CLIP model and processor."""
        try:
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Update embedding dimension based on model
            self.embedding_dimension = self.model.config.projection_dim
            
        except Exception as e:
            logger.error(f"Error initializing CLIP model: {e}")
            raise
    
    def _initialize_generic_vision_model(self):
        """Initialize generic vision model and processor."""
        try:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Try to get embedding dimension from model config
            if hasattr(self.model.config, 'hidden_size'):
                self.embedding_dimension = self.model.config.hidden_size
            elif hasattr(self.model.config, 'projection_dim'):
                self.embedding_dimension = self.model.config.projection_dim
                
        except Exception as e:
            logger.error(f"Error initializing generic vision model: {e}")
            raise
    
    def _initialize_fallback_model(self):
        """Initialize a fallback model for basic image processing."""
        logger.warning("Using fallback image processing model")
        
        # Simple preprocessing pipeline
        self.processor = transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Simple feature extraction (placeholder)
        self.model = None
    
    async def generate_embedding(self, image_data: Union[bytes, str, Image.Image]) -> List[float]:
        """
        Generate embedding for an image.
        
        Args:
            image_data: Image data as bytes, base64 string, or PIL Image
            
        Returns:
            List of float values representing the image embedding
        """
        try:
            # Convert input to PIL Image
            image = self._prepare_image(image_data)
            
            # Extract metadata
            metadata = self._extract_image_metadata(image)
            
            # Generate embedding
            embedding = await self._generate_embedding_from_image(image)
            
            # Normalize if requested
            if self.normalize_embeddings and embedding is not None:
                embedding = self._normalize_embedding(embedding)
            
            logger.debug(f"Generated image embedding: {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating image embedding: {e}")
            raise
    
    def _prepare_image(self, image_data: Union[bytes, str, Image.Image]) -> Image.Image:
        """
        Prepare image data for processing.
        
        Args:
            image_data: Image data in various formats
            
        Returns:
            PIL Image object
        """
        try:
            if isinstance(image_data, Image.Image):
                return image_data
            
            elif isinstance(image_data, bytes):
                return Image.open(io.BytesIO(image_data))
            
            elif isinstance(image_data, str):
                # Check if it's a base64 string
                if image_data.startswith('data:image'):
                    # Remove data URL prefix
                    image_data = image_data.split(',')[1]
                
                # Decode base64
                image_bytes = base64.b64decode(image_data)
                return Image.open(io.BytesIO(image_bytes))
            
            elif isinstance(image_data, str) and (image_data.startswith('http://') or image_data.startswith('https://')):
                # Download image from URL
                response = requests.get(image_data)
                response.raise_for_status()
                return Image.open(io.BytesIO(response.content))
            
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
                
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            raise
    
    def _extract_image_metadata(self, image: Image.Image) -> ImageMetadata:
        """
        Extract metadata from image.
        
        Args:
            image: PIL Image object
            
        Returns:
            ImageMetadata object
        """
        return ImageMetadata(
            width=image.width,
            height=image.height,
            format=image.format or "unknown",
            mode=image.mode
        )
    
    async def _generate_embedding_from_image(self, image: Image.Image) -> List[float]:
        """
        Generate embedding from PIL Image.
        
        Args:
            image: PIL Image object
            
        Returns:
            List of float values representing the embedding
        """
        try:
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Generate embedding based on model type
            if self.model is not None:
                return await self._generate_model_embedding(processed_image)
            else:
                return await self._generate_fallback_embedding(processed_image)
                
        except Exception as e:
            logger.error(f"Error generating embedding from image: {e}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess image for model input.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image tensor
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply preprocessing based on pipeline
            if self.preprocessing_pipeline == "clip" and self.processor:
                # Use CLIP processor
                inputs = self.processor(images=image, return_tensors="pt")
                return inputs['pixel_values']
            
            elif self.preprocessing_pipeline == "generic" and self.processor:
                # Use generic processor
                inputs = self.processor(images=image, return_tensors="pt")
                return inputs['pixel_values']
            
            else:
                # Use fallback preprocessing
                return self._fallback_preprocessing(image)
                
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def _fallback_preprocessing(self, image: Image.Image) -> torch.Tensor:
        """
        Fallback preprocessing for images.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image tensor
        """
        # Basic preprocessing pipeline
        transform = transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        return transform(image).unsqueeze(0)  # Add batch dimension
    
    async def _generate_model_embedding(self, processed_image: torch.Tensor) -> List[float]:
        """
        Generate embedding using the loaded model.
        
        Args:
            processed_image: Preprocessed image tensor
            
        Returns:
            List of float values representing the embedding
        """
        try:
            with torch.no_grad():
                # Move to device
                processed_image = processed_image.to(self.device)
                
                # Generate embedding
                if hasattr(self.model, 'get_image_features'):
                    # CLIP model
                    outputs = self.model.get_image_features(pixel_values=processed_image)
                else:
                    # Generic vision model
                    outputs = self.model(pixel_values=processed_image)
                    # Use the last hidden state or pooler output
                    if hasattr(outputs, 'pooler_output'):
                        outputs = outputs.pooler_output
                    elif hasattr(outputs, 'last_hidden_state'):
                        outputs = outputs.last_hidden_state.mean(dim=1)
                    else:
                        outputs = outputs.logits
                
                # Convert to list
                embedding = outputs.cpu().numpy().flatten().tolist()
                
                return embedding
                
        except Exception as e:
            logger.error(f"Error generating model embedding: {e}")
            raise
    
    async def _generate_fallback_embedding(self, processed_image: torch.Tensor) -> List[float]:
        """
        Generate fallback embedding when no model is available.
        
        Args:
            processed_image: Preprocessed image tensor
            
        Returns:
            List of float values representing the embedding
        """
        try:
            # Simple feature extraction using the processed image
            # This is a placeholder implementation
            features = processed_image.flatten().numpy()
            
            # Reduce to target dimension using simple averaging
            if len(features) > self.embedding_dimension:
                # Average pooling to reduce dimensions
                step = len(features) // self.embedding_dimension
                reduced_features = []
                for i in range(self.embedding_dimension):
                    start_idx = i * step
                    end_idx = start_idx + step
                    reduced_features.append(float(np.mean(features[start_idx:end_idx])))
                return reduced_features
            else:
                # Pad with zeros if too short
                features = features.tolist()
                features.extend([0.0] * (self.embedding_dimension - len(features)))
                return features
                
        except Exception as e:
            logger.error(f"Error generating fallback embedding: {e}")
            raise
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        Normalize embedding vector.
        
        Args:
            embedding: List of float values
            
        Returns:
            Normalized embedding vector
        """
        try:
            embedding_array = np.array(embedding)
            norm = np.linalg.norm(embedding_array)
            
            if norm > 0:
                normalized = embedding_array / norm
                return normalized.tolist()
            else:
                return embedding
                
        except Exception as e:
            logger.warning(f"Error normalizing embedding: {e}")
            return embedding
    
    async def generate_batch_embeddings(self, image_data_list: List[Union[bytes, str, Image.Image]]) -> List[List[float]]:
        """
        Generate embeddings for a batch of images.
        
        Args:
            image_data_list: List of image data
            
        Returns:
            List of embedding vectors
        """
        try:
            tasks = [self.generate_embedding(image_data) for image_data in image_data_list]
            embeddings = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            results = []
            for i, embedding in enumerate(embeddings):
                if isinstance(embedding, Exception):
                    logger.error(f"Error generating embedding for image {i}: {embedding}")
                    results.append([0.0] * self.embedding_dimension)  # Zero embedding as fallback
                else:
                    results.append(embedding)
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return ['JPEG', 'PNG', 'BMP', 'TIFF', 'GIF', 'WEBP']
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dimension,
            'image_size': self.image_size,
            'device': str(self.device),
            'normalize_embeddings': self.normalize_embeddings,
            'preprocessing_pipeline': self.preprocessing_pipeline
        }


# Utility functions for image processing
def resize_image(image: Image.Image, size: Tuple[int, int], maintain_aspect_ratio: bool = True) -> Image.Image:
    """
    Resize image while optionally maintaining aspect ratio.
    
    Args:
        image: PIL Image object
        size: Target size (width, height)
        maintain_aspect_ratio: Whether to maintain aspect ratio
        
    Returns:
        Resized image
    """
    if maintain_aspect_ratio:
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    else:
        return image.resize(size, Image.Resampling.LANCZOS)


def convert_image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
    """
    Convert PIL Image to base64 string.
    
    Args:
        image: PIL Image object
        format: Image format
        
    Returns:
        Base64 encoded string
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/{format.lower()};base64,{img_str}"


def convert_base64_to_image(base64_str: str) -> Image.Image:
    """
    Convert base64 string to PIL Image.
    
    Args:
        base64_str: Base64 encoded image string
        
    Returns:
        PIL Image object
    """
    if base64_str.startswith('data:image'):
        base64_str = base64_str.split(',')[1]
    
    image_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_bytes))
