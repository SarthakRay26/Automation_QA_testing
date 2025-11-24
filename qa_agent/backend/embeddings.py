"""
Embeddings module using SentenceTransformers.
Generates embeddings for documents and queries.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingModel:
    """
    Wrapper for SentenceTransformer model to generate embeddings.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
                       Default: 'all-MiniLM-L6-v2' (lightweight and efficient)
        """
        logger.info(f"Loading embedding model: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            logger.info(f"Successfully loaded model: {model_name}")
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
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
            batch_size: Batch size for encoding
            show_progress_bar: Whether to show progress bar
        
        Returns:
            List of embedding vectors
        """
        try:
            # Ensure texts is a list
            if isinstance(texts, str):
                texts = [texts]
            
            logger.info(f"Encoding {len(texts)} text(s)")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress_bar,
                convert_to_numpy=True
            )
            
            # Convert to list format
            embeddings_list = embeddings.tolist()
            
            logger.info(f"Successfully generated {len(embeddings_list)} embeddings")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Error encoding texts: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()
