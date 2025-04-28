# src/retriever.py
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_chroma import Chroma

class ArticleRetriever:
    """
    Simplified Retriever for DocBank articles.

    This retriever interfaces with a Chroma vector database to retrieve
    relevant documents based on a query and optional filters.
    """
    def __init__(self, vectordb: Chroma):
        """
        Initializes the retriever with a Chroma vector database instance.

        Args:
            vectordb: An instance of the Chroma vector database.
        """
        self.vectordb = vectordb

    def get_relevant_documents(self, query: str, query_filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Retrieves relevant documents from the vector database.

        Args:
            query: The search query string.
            query_filter: Optional filter to narrow down the search results.

        Returns:
            A list of Langchain Document objects relevant to the query.
        """
        return self.vectordb.similarity_search(query=query, k=5, filter=query_filter)