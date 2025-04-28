# src/loader.py
from pathlib import Path
from typing import Iterator, List
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from src.parser import process_article # Assuming parser.py is in the same src directory

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
        """
        self.file_path = Path(file_path)
        if not self.file_path.is_dir():
            raise ValueError(f"Provided path '{file_path}' is not a directory.")

    def lazy_load(self) -> Iterator[Document]:
        """
        Lazily loads documents from the specified article directory.

        This method processes the article using the imported 'process_article'
        function and yields Langchain Document objects one by one.
        """
        processed_docs = process_article(self.file_path, min_length=0)
        for doc_data in processed_docs:
            yield Document(
                page_content=doc_data["page_content"],
                metadata=doc_data["metadata"]
            )