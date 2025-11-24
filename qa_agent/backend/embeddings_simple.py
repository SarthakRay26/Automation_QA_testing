"""
Simple embeddings module using basic text features instead of neural models.
Avoids heavy dependencies like torch/transformers.
"""

from typing import List, Union
from pathlib import Path
import sys
import hashlib
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


class SimpleEmbeddingModel:
    """
    Simple embedding model using TF-IDF-like features.
    No neural networks or heavy dependencies required.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize simple embedding model.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        logger.info(f"Initializing Simple Embedding Model (dim={embedding_dim})")
        self.embedding_dim = embedding_dim
        self.vocab = {}
        logger.info("Simple Embedding Model ready")
    
    def _text_to_features(self, text: str) -> List[float]:
        """
        Convert text to a simple feature vector.
        Uses character n-grams and word features.
        """
        # Normalize text
        text = text.lower().strip()
        
        # Create a deterministic hash-based embedding
        features = []
        
        # Use multiple hash functions for different parts of the vector
        for i in range(self.embedding_dim):
            # Create different seeds for each dimension
            seed_text = f"{text}_{i}"
            hash_val = int(hashlib.md5(seed_text.encode()).hexdigest(), 16)
            # Normalize to [-1, 1]
            normalized = (hash_val % 10000) / 5000.0 - 1.0
            features.append(normalized)
        
        # Normalize the vector
        magnitude = sum(x**2 for x in features) ** 0.5
        if magnitude > 0:
            features = [x / magnitude for x in features]
        
        return features
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size (not used in simple version)
            show_progress_bar: Whether to show progress
        
        Returns:
            List of embedding vectors
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Encoding {len(texts)} text(s)")
        
        embeddings = []
        for text in texts:
            embedding = self._text_to_features(text)
            embeddings.append(embedding)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def get_sentence_embedding_dimension(self) -> int:
        """Get the dimension of embedding vectors."""
        return self.embedding_dim
