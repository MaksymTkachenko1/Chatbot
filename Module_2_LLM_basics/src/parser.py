import json
import logging
from enum import StrEnum
from pathlib import Path
from typing import TypedDict


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


def read_page_data(path: Path) -> list:
    with Path(path).open() as f:
        return json.load(f)


def get_page_number(page_path) -> int:
    return int(page_path.stem.split("_")[-1])


def collect_article_pages_paths(directory_path: Path) -> list[Path]:
    return sorted([p for p in directory_path.glob("**/*.json")], key=get_page_number)


class IParser:
    state = None

    @classmethod
    def get_next_parser(cls, label: Labels):
        raise NotImplementedError

    @classmethod
    def process(cls, page: list[dict], text: str, label: Labels, previous_state):
        assert cls.state is not None


class DefaultParser(IParser):
    state = None

    @classmethod
    def get_next_parser(cls, label: Labels) -> IParser.__class__:
        global PARSERS

        if label != cls.state:
            if label not in PARSERS:
                logging.warning(f"Parser for label '{label}' not found, creating default parser.")
            return PARSERS.get(label, get_default_parser(label))

        return cls

    @classmethod
    def _process_text(cls, old_text: str, new_text: str, label: Labels) -> str:
        return f"{old_text} {new_text}"

    @classmethod
    def process(cls, page: list[dict], text: str, label: Labels, previous_state: IParser.__class__) -> None:
        assert cls.state is not None

        if not page or page[-1]["label"] != cls.state or issubclass(previous_state, IgnoredParser):
            page.append({"label": cls.state, "text": ''})

        page[-1]["text"] = cls._process_text(page[-1]["text"], text, label)


class AuthorParser(DefaultParser):
    state = Labels.AUTHOR

    @classmethod
    def get_next_parser(cls, label: Labels):
        if label in (Labels.PARAGRAPH, Labels.AUTHOR):
            return cls

        return super().get_next_parser(label)


class FooterParser(DefaultParser):
    state = Labels.FOOTER

    @classmethod
    def get_next_parser(cls, label: Labels) -> IParser.__class__:
        return cls

    @classmethod
    def _process_text(cls, old_text: str, new_text: str, label: Labels) -> str:
        if cls.state == label:
            return super()._process_text(old_text, new_text, label)
        return f"{old_text}\n{new_text}"


class IgnoredParser(DefaultParser):
    @classmethod
    def process(cls, page: list[dict], text: str, label: Labels, previous_state: IParser.__class__) -> None:
        pass


class EquationParser(IgnoredParser):
    state = Labels.EQUATION


class FigureParser(IgnoredParser):
    state = Labels.FIGURE


CUSTOM_PARSERS = {
    Labels.AUTHOR: AuthorParser,
    Labels.FOOTER: FooterParser,
    Labels.EQUATION: EquationParser,
    Labels.FIGURE: FigureParser,
}


def get_default_parser(label: Labels) -> IParser.__class__:
    class Parser(DefaultParser):
        state = label

    return Parser


PARSERS = {
    p: (CUSTOM_PARSERS[p] if p in CUSTOM_PARSERS else get_default_parser(p))
    for p in Labels
}


def process_page_data(page_data: list[PageBlock]):
    state = get_default_parser(Labels.PARAGRAPH)
    page = []

    for box in page_data:
        previous_state = state
        state = state.get_next_parser(box["label"])
        state.process(page, box["text"], box["label"], previous_state)

    return page


def process_pages(pages_paths: list[Path]) -> list:
    pages = []

    for page_path in pages_paths:
        page_data = read_page_data(page_path)
        page_number = get_page_number(page_path)
        page = process_page_data(page_data)
        pages.append((page_number, page))

    return pages


def process_article(article_directory_path, min_length: int = 20) -> list:
    result = []
    pages_paths = collect_article_pages_paths(article_directory_path)
    pages = process_pages(pages_paths)

    meta_labels = {Labels.AUTHOR, Labels.TITLE, Labels.ABSTRACT}
    raw_meta = {}
    for page_number, page in pages:
        for item in page:
            if item["label"] in meta_labels:
                raw_meta[item["label"]] = raw_meta.get(item["label"], [])
                raw_meta[item["label"]].append(item["text"])

    common_metadata = {
        "source": article_directory_path.name,
        **{label: "\n".join(raw_meta.get(label, [])) for label in meta_labels},
        "page": 0
    }

    for page_number, page in pages:
        metadata = common_metadata.copy()
        metadata["page"] = page_number + 1
        for item in page:
            if item["label"] is Labels.PARAGRAPH and len(item["text"]) > min_length:
                result.append({
                    "page_content": item["text"],
                    "metadata": metadata
                })

    return result