# src/loader.py
import logging
from pathlib import Path
from typing import Iterator, List
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from .parser import process_article  # Fixed relative import

logger = logging.getLogger(__name__)

class ArticleLoader(BaseLoader):
    """
    Custom Document Loader for DocBank articles.

    Takes the path to a specific article *directory* containing JSON files
    and loads the processed text content and metadata.
    """
    def __init__(self, file_path: str | Path) -> None:
        """
        Initializes the loader with the path to the article directory.

        Args:
            file_path: The path to the directory containing the article's JSON files.
            
        Raises:
            ValueError: If the provided path is not a directory.
            FileNotFoundError: If the provided path does not exist.
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Provided path '{file_path}' does not exist.")
        
        if not self.file_path.is_dir():
            raise ValueError(f"Provided path '{file_path}' is not a directory.")

    def lazy_load(self) -> Iterator[Document]:
        """
        Lazily loads documents from the specified article directory.

        This method processes the article using the imported 'process_article'
        function and yields Langchain Document objects one by one.
        
        Yields:
            Document: Langchain Document objects with processed content and metadata.
            
        Raises:
            Exception: If there's an error processing the article.
        """
        try:
            processed_docs = process_article(self.file_path, min_length=0)
            logger.info(f"Successfully processed {len(processed_docs)} documents from {self.file_path}")
            
            for doc_data in processed_docs:
                yield Document(
                    page_content=doc_data["page_content"],
                    metadata=doc_data["metadata"]
                )
        except Exception as e:
            logger.error(f"Error processing article from {self.file_path}: {str(e)}")
            raise