import json
import logging
from enum import StrEnum
from pathlib import Path
from typing import TypedDict, List, Dict, Type, Union

logger = logging.getLogger(__name__)


class Labels(StrEnum):
    ABSTRACT = "abstract"
    AUTHOR = "author"
    CAPTION = "caption"
    EQUATION = "equation"
    FIGURE = "figure"
    FOOTER = "footer"
    LIST = "list"
    PARAGRAPH = "paragraph"
    REFERENCE = "reference"
    SECTION = "section"
    TABLE = "table"
    TITLE = "title"
    DATE = "date"


class PageBlock(TypedDict):
    text: str
    label: Labels


def read_page_data(path: Path) -> List[Dict]:
    """
    Read and parse JSON data from a page file.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        List of dictionaries containing page data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        PermissionError: If the file can't be read due to permissions
    """
    try:
        with Path(path).open(encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Successfully read page data from {path}")
            return data
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {path}: {str(e)}")
        raise
    except PermissionError:
        logger.error(f"Permission denied reading file: {path}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading file {path}: {str(e)}")
        raise


def get_page_number(page_path: Path) -> int:
    """
    Extract page number from file path.
    
    Args:
        page_path: Path object for the page file
        
    Returns:
        Page number as integer
        
    Raises:
        ValueError: If page number cannot be extracted from filename
    """
    try:
        return int(page_path.stem.split("_")[-1])
    except (ValueError, IndexError) as e:
        logger.error(f"Cannot extract page number from filename: {page_path.name}")
        raise ValueError(f"Invalid filename format for page number extraction: {page_path.name}") from e


def collect_article_pages_paths(directory_path: Path) -> List[Path]:
    """
    Collect and sort all JSON page files from directory.
    
    Args:
        directory_path: Path to directory containing JSON files
        
    Returns:
        Sorted list of Path objects for JSON files
        
    Raises:
        FileNotFoundError: If directory doesn't exist
    """
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    
    json_files = list(directory_path.glob("**/*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in directory: {directory_path}")
        return []
    
    try:
        sorted_files = sorted(json_files, key=get_page_number)
        logger.info(f"Found {len(sorted_files)} JSON files in {directory_path}")
        return sorted_files
    except ValueError as e:
        logger.error(f"Error sorting files by page number: {str(e)}")
        raise


class IParser:
    """Base interface for parsers."""
    state: Labels = None

    @classmethod
    def get_next_parser(cls, label: Labels) -> Type['IParser']:
        """Get the appropriate parser for the given label."""
        raise NotImplementedError

    @classmethod
    def process(cls, page: List[Dict], text: str, label: Labels, previous_state: Type['IParser']) -> None:
        """Process text with the given label."""
        assert cls.state is not None


class ParserRegistry:
    """Registry for managing parser instances."""
    
    def __init__(self):
        self._parsers: Dict[Labels, Type[IParser]] = {}
        self._default_parsers: Dict[Labels, Type[IParser]] = {}
        
    def register_parser(self, label: Labels, parser_class: Type[IParser]) -> None:
        """Register a custom parser for a label."""
        self._parsers[label] = parser_class
        
    def get_parser(self, label: Labels) -> Type[IParser]:
        """Get parser for a label, creating default if needed."""
        if label in self._parsers:
            return self._parsers[label]
        
        if label not in self._default_parsers:
            self._default_parsers[label] = self._create_default_parser(label)
            
        return self._default_parsers[label]
    
    def _create_default_parser(self, label: Labels) -> Type[IParser]:
        """Create a default parser for a label."""
        class DefaultParserInstance(DefaultParser):
            state = label
        return DefaultParserInstance


# Global parser registry instance
parser_registry = ParserRegistry()


class DefaultParser(IParser):
    state: Labels = None

    @classmethod
    def get_next_parser(cls, label: Labels) -> Type[IParser]:
        if label != cls.state:
            return parser_registry.get_parser(label)
        return cls

    @classmethod
    def _process_text(cls, old_text: str, new_text: str, label: Labels) -> str:
        """Combine old and new text."""
        return f"{old_text} {new_text}".strip()

    @classmethod
    def process(cls, page: List[Dict], text: str, label: Labels, previous_state: Type[IParser]) -> None:
        assert cls.state is not None

        if not page or page[-1]["label"] != cls.state or issubclass(previous_state, IgnoredParser):
            page.append({"label": cls.state, "text": ''})

        page[-1]["text"] = cls._process_text(page[-1]["text"], text, label)


class AuthorParser(DefaultParser):
    state = Labels.AUTHOR

    @classmethod
    def get_next_parser(cls, label: Labels) -> Type[IParser]:
        if label in (Labels.PARAGRAPH, Labels.AUTHOR):
            return cls
        return super().get_next_parser(label)


class FooterParser(DefaultParser):
    state = Labels.FOOTER

    @classmethod
    def get_next_parser(cls, label: Labels) -> Type[IParser]:
        return cls

    @classmethod
    def _process_text(cls, old_text: str, new_text: str, label: Labels) -> str:
        if cls.state == label:
            return super()._process_text(old_text, new_text, label)
        return f"{old_text}\n{new_text}".strip()


class IgnoredParser(DefaultParser):
    """Parser that ignores content."""
    
    @classmethod
    def process(cls, page: List[Dict], text: str, label: Labels, previous_state: Type[IParser]) -> None:
        pass


class EquationParser(IgnoredParser):
    state = Labels.EQUATION


class FigureParser(IgnoredParser):
    state = Labels.FIGURE


# Register custom parsers
parser_registry.register_parser(Labels.AUTHOR, AuthorParser)
parser_registry.register_parser(Labels.FOOTER, FooterParser)
parser_registry.register_parser(Labels.EQUATION, EquationParser)
parser_registry.register_parser(Labels.FIGURE, FigureParser)


def process_page_data(page_data: List[PageBlock]) -> List[Dict]:
    """
    Process page data using appropriate parsers.
    
    Args:
        page_data: List of page blocks with text and labels
        
    Returns:
        List of processed page items
    """
    state = parser_registry.get_parser(Labels.PARAGRAPH)
    page = []

    for box in page_data:
        try:
            previous_state = state
            state = state.get_next_parser(box["label"])
            state.process(page, box["text"], box["label"], previous_state)
        except Exception as e:
            logger.error(f"Error processing box with label {box['label']}: {str(e)}")
            # Continue processing other boxes
            continue

    return page


def process_pages(pages_paths: List[Path]) -> List[tuple]:
    """
    Process multiple pages from file paths.
    
    Args:
        pages_paths: List of paths to page JSON files
        
    Returns:
        List of tuples (page_number, processed_page_data)
    """
    pages = []

    for page_path in pages_paths:
        try:
            page_data = read_page_data(page_path)
            page_number = get_page_number(page_path)
            page = process_page_data(page_data)
            pages.append((page_number, page))
        except Exception as e:
            logger.error(f"Error processing page {page_path}: {str(e)}")
            # Continue with other pages
            continue

    logger.info(f"Successfully processed {len(pages)} out of {len(pages_paths)} pages")
    return pages


def process_article(article_directory_path: Path, min_length: int = 20) -> List[Dict]:
    """
    Process an entire article from directory containing JSON page files.
    
    Args:
        article_directory_path: Path to directory with article JSON files
        min_length: Minimum length for paragraph content to be included
        
    Returns:
        List of dictionaries with page_content and metadata
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If directory is invalid or contains no processable files
    """
    if not isinstance(article_directory_path, Path):
        article_directory_path = Path(article_directory_path)
        
    result = []
    
    try:
        pages_paths = collect_article_pages_paths(article_directory_path)
        if not pages_paths:
            logger.warning(f"No JSON files found in {article_directory_path}")
            return result
            
        pages = process_pages(pages_paths)
        if not pages:
            logger.warning(f"No pages could be processed from {article_directory_path}")
            return result

        # Extract metadata from all pages
        meta_labels = {Labels.AUTHOR, Labels.TITLE, Labels.ABSTRACT}
        raw_meta: Dict[Labels, List[str]] = {}
        
        for page_number, page in pages:
            for item in page:
                if item["label"] in meta_labels:
                    if item["label"] not in raw_meta:
                        raw_meta[item["label"]] = []
                    raw_meta[item["label"]].append(item["text"])

        common_metadata = {
            "source": article_directory_path.name,
            **{label.value: "\n".join(raw_meta.get(label, [])) for label in meta_labels},
            "page": 0
        }

        # Process content from all pages
        for page_number, page in pages:
            metadata = common_metadata.copy()
            metadata["page"] = page_number + 1
            
            for item in page:
                if (item["label"] == Labels.PARAGRAPH and 
                    len(item["text"].strip()) > min_length):
                    result.append({
                        "page_content": item["text"].strip(),
                        "metadata": metadata
                    })

        logger.info(f"Processed article {article_directory_path.name}: {len(result)} content blocks")
        return result
        
    except Exception as e:
        logger.error(f"Error processing article {article_directory_path}: {str(e)}")
        raise