"""
Text utilities for AI RAG module
Provides common text processing and analysis functions
"""

import re
import string
from typing import List, Dict, Set, Optional, Tuple
import logging
from collections import Counter
import hashlib

logger = logging.getLogger(__name__)


def clean_text(text: str, remove_punctuation: bool = False, lowercase: bool = True) -> str:
    """
    Clean and normalize text by removing extra whitespace and optionally punctuation.
    
    Args:
        text: Input text to clean
        remove_punctuation: Whether to remove punctuation
        lowercase: Whether to convert to lowercase
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    if lowercase:
        cleaned = cleaned.lower()
    
    if remove_punctuation:
        # Remove punctuation but keep spaces
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
    
    return cleaned


def extract_keywords(
    text: str,
    min_length: int = 3,
    max_keywords: int = 50,
    exclude_common: bool = True
) -> List[str]:
    """
    Extract keywords from text based on frequency and importance.
    
    Args:
        text: Input text to extract keywords from
        min_length: Minimum word length to consider
        max_keywords: Maximum number of keywords to return
        exclude_common: Whether to exclude common words
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Common words to exclude
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Clean text and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter words by length and common words
    if exclude_common:
        words = [word for word in words if len(word) >= min_length and word not in common_words]
    else:
        words = [word for word in words if len(word) >= min_length]
    
    # Count word frequencies
    word_counts = Counter(words)
    
    # Return top keywords
    return [word for word, _ in word_counts.most_common(max_keywords)]


def normalize_text(text: str) -> str:
    """
    Normalize text by standardizing whitespace, quotes, and common patterns.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Normalize quotes
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r'['']', "'", text)
    
    # Normalize dashes
    text = re.sub(r'[–—]', '-', text)
    
    # Normalize ellipsis
    text = re.sub(r'\.{3,}', '...', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def split_text_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
    separator: str = "\n"
) -> List[str]:
    """
    Split text into overlapping chunks for processing.
    
    Args:
        text: Input text to split
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        separator: Character to use as chunk separator
        
    Returns:
        List of text chunks
    """
    if not text or chunk_size <= 0:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end >= len(text):
            # Last chunk
            chunks.append(text[start:])
            break
        
        # Try to find a good break point
        if separator in text[start:end]:
            # Find the last separator in the chunk
            last_separator = text[start:end].rfind(separator)
            if last_separator > 0:
                end = start + last_separator + 1
        
        chunks.append(text[start:end])
        start = end - overlap
        
        # Ensure we don't go backwards
        if start <= 0:
            start = end
    
    return chunks


def calculate_text_similarity(text1: str, text2: str, method: str = "jaccard") -> float:
    """
    Calculate similarity between two text strings.
    
    Args:
        text1: First text string
        text2: Second text string
        method: Similarity method ('jaccard', 'cosine', 'levenshtein')
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    if method == "jaccard":
        return _jaccard_similarity(text1, text2)
    elif method == "cosine":
        return _cosine_similarity(text1, text2)
    elif method == "levenshtein":
        return _levenshtein_similarity(text1, text2)
    else:
        logger.warning(f"Unknown similarity method: {method}, using Jaccard")
        return _jaccard_similarity(text1, text2)


def _jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between two texts."""
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def _cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts."""
    words1 = re.findall(r'\b\w+\b', text1.lower())
    words2 = re.findall(r'\b\w+\b', text2.lower())
    
    # Create word frequency vectors
    freq1 = Counter(words1)
    freq2 = Counter(words2)
    
    # Get all unique words
    all_words = set(freq1.keys()).union(set(freq2.keys()))
    
    # Calculate dot product and magnitudes
    dot_product = sum(freq1[word] * freq2[word] for word in all_words)
    magnitude1 = sum(freq1[word] ** 2 for word in all_words) ** 0.5
    magnitude2 = sum(freq2[word] ** 2 for word in all_words) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def _levenshtein_similarity(text1: str, text2: str) -> float:
    """Calculate Levenshtein distance-based similarity between two texts."""
    def levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    distance = levenshtein_distance(text1, text2)
    max_length = max(len(text1), len(text2))
    
    if max_length == 0:
        return 1.0
    
    return 1.0 - (distance / max_length)


def extract_entities(text: str, entity_types: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """
    Extract named entities from text using simple pattern matching.
    
    Args:
        text: Input text to extract entities from
        entity_types: Types of entities to extract (e.g., ['email', 'url', 'phone'])
        
    Returns:
        Dictionary mapping entity types to lists of found entities
    """
    if not text:
        return {}
    
    entities = {}
    
    # Extract emails
    if entity_types is None or 'email' in entity_types:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['email'] = re.findall(email_pattern, text)
    
    # Extract URLs
    if entity_types is None or 'url' in entity_types:
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        entities['url'] = re.findall(url_pattern, text)
    
    # Extract phone numbers
    if entity_types is None or 'phone' in entity_types:
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        entities['phone'] = re.findall(phone_pattern, text)
    
    # Extract dates
    if entity_types is None or 'date' in entity_types:
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        entities['date'] = re.findall(date_pattern, text)
    
    return entities


def generate_text_hash(text: str, algorithm: str = "md5") -> str:
    """
    Generate a hash of the text for identification purposes.
    
    Args:
        text: Input text to hash
        algorithm: Hashing algorithm to use
        
    Returns:
        Hexadecimal hash string
    """
    if not text:
        return ""
    
    text_bytes = text.encode('utf-8')
    
    if algorithm == "md5":
        return hashlib.md5(text_bytes).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(text_bytes).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(text_bytes).hexdigest()
    else:
        logger.warning(f"Unknown hash algorithm: {algorithm}, using MD5")
        return hashlib.md5(text_bytes).hexdigest()



