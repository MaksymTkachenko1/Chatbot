# src/retriever.py
import logging
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_chroma import Chroma

logger = logging.getLogger(__name__)


class ArticleRetriever:
    """
    Simplified Retriever for DocBank articles.

    This retriever interfaces with a Chroma vector database to retrieve
    relevant documents based on a query and optional filters.
    """
    
    def __init__(self, vectordb: Chroma, default_k: int = 5):
        """
        Initializes the retriever with a Chroma vector database instance.

        Args:
            vectordb: An instance of the Chroma vector database.
            default_k: Default number of documents to retrieve.
            
        Raises:
            ValueError: If vectordb is None or default_k is not positive.
        """
        if vectordb is None:
            raise ValueError("vectordb cannot be None")
        if default_k <= 0:
            raise ValueError("default_k must be a positive integer")
            
        self.vectordb = vectordb
        self.default_k = default_k
        logger.info(f"ArticleRetriever initialized with default_k={default_k}")

    def get_relevant_documents(
        self, 
        query: str, 
        k: Optional[int] = None, 
        query_filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Retrieves relevant documents from the vector database.

        Args:
            query: The search query string.
            k: Number of documents to retrieve. If None, uses default_k.
            query_filter: Optional filter to narrow down the search results.

        Returns:
            A list of Langchain Document objects relevant to the query.
            
        Raises:
            ValueError: If query is empty or None.
            Exception: If there's an error during retrieval.
        """
        # Validate input parameters
        if not query or not query.strip():
            raise ValueError("Query cannot be empty or None")
            
        if k is None:
            k = self.default_k
        elif k <= 0:
            raise ValueError("k must be a positive integer")
            
        try:
            logger.debug(f"Retrieving {k} documents for query: '{query[:50]}...'")
            
            documents = self.vectordb.similarity_search(
                query=query.strip(), 
                k=k, 
                filter=query_filter
            )
            
            logger.info(f"Successfully retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents for query '{query[:50]}...': {str(e)}")
            raise
    
    def get_relevant_documents_with_scores(
        self, 
        query: str, 
        k: Optional[int] = None, 
        query_filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """
        Retrieves relevant documents with similarity scores from the vector database.

        Args:
            query: The search query string.
            k: Number of documents to retrieve. If None, uses default_k.
            query_filter: Optional filter to narrow down the search results.

        Returns:
            A list of tuples (Document, score) relevant to the query.
            
        Raises:
            ValueError: If query is empty or None.
            Exception: If there's an error during retrieval.
        """
        # Validate input parameters
        if not query or not query.strip():
            raise ValueError("Query cannot be empty or None")
            
        if k is None:
            k = self.default_k
        elif k <= 0:
            raise ValueError("k must be a positive integer")
            
        try:
            logger.debug(f"Retrieving {k} documents with scores for query: '{query[:50]}...'")
            
            documents_with_scores = self.vectordb.similarity_search_with_score(
                query=query.strip(), 
                k=k, 
                filter=query_filter
            )
            
            logger.info(f"Successfully retrieved {len(documents_with_scores)} documents with scores")
            return documents_with_scores
            
        except Exception as e:
            logger.error(f"Error retrieving documents with scores for query '{query[:50]}...': {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """
        Performs a basic health check on the vector database.
        
        Returns:
            True if the database is accessible, False otherwise.
        """
        try:
            # Try to get collection info or perform a simple operation
            collection = self.vectordb._collection
            if collection is None:
                logger.warning("Vector database collection is None")
                return False
                
            # Try a simple count operation
            count = collection.count()
            logger.info(f"Health check passed. Collection contains {count} documents")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False