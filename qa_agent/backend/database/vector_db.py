"""
Vector Database module using ChromaDB.
Handles storage and retrieval of document embeddings.
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorDatabase:
    """
    Manages ChromaDB operations for storing and retrieving document chunks.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing ChromaDB at {persist_directory}")
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = None
    
    def create_collection(self, collection_name: str = "qa_documents"):
        """
        Create or get a collection in ChromaDB.
        
        Args:
            collection_name: Name of the collection
        """
        try:
            logger.info(f"Creating/Getting collection: {collection_name}")
            
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "QA Agent document embeddings"}
            )
            
            logger.info(f"Collection '{collection_name}' ready")
            return self.collection
            
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Add documents with embeddings to the collection.
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        try:
            if not self.collection:
                raise ValueError("Collection not initialized. Call create_collection first.")
            
            logger.info(f"Adding {len(documents)} documents to collection")
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query the collection with embedding vectors.
        
        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
        
        Returns:
            Query results including documents and metadata
        """
        try:
            if not self.collection:
                raise ValueError("Collection not initialized. Call create_collection first.")
            
            logger.info(f"Querying collection for top {n_results} results")
            
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            
            logger.info(f"Query returned {len(results.get('documents', [[]])[0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying collection: {str(e)}")
            raise
    
    def clear_collection(self):
        """
        Clear all documents from the collection.
        """
        try:
            if self.collection:
                logger.info("Clearing collection")
                self.client.delete_collection(self.collection.name)
                self.collection = None
                logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Number of documents
        """
        try:
            if not self.collection:
                return 0
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting collection count: {str(e)}")
            return 0
