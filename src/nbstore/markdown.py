"""Convert Markdown files to Jupyter notebooks.

This module provides utilities for parsing Markdown files and converting them
to notebook format, with support for code blocks, images, and custom attributes.
It implements a robust parser for Markdown syntax including code blocks with
language specification and attributes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, ClassVar, TypeGuard

import nbformat

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Self

    from nbformat import NotebookNode


def _split(text: str) -> Iterator[str]:
    """Split text into parts while respecting quoted strings.

    Splits text by spaces, treating quoted strings as single parts, and
    handling escaped quotes correctly.

    Args:
        text (str): The text to split.

    Yields:
        str: The split parts.
    """
    in_quotes = {'"': False, "'": False, "`": False}

    chars = list(text)
    start = 0

    for cursor, char in enumerate(chars):
        if cursor > 0 and chars[cursor - 1] == "\\":
            continue

        for q, in_ in in_quotes.items():
            if char == q:
                if in_:
                    yield text[start : cursor + 1]
                    start = cursor + 1
                in_quotes[q] = not in_

        if char == " ":
            if not any(in_quotes.values()):
                if start < cursor:
                    yield text[start:cursor]
                start = cursor + 1

    if start < len(text):
        yield text[start:]


def split(text: str) -> Iterator[str]:
    """Split text into parts, handling key=value pairs.

    Builds on _split by additionally recognizing and combining key=value
    pairs into single parts.

    Args:
        text (str): The text to split.

    Yields:
        str: The split parts.
    """
    parts = list(_split(text))

    start = 0
    for cursor, part in enumerate(parts):
        if part == "=" and 0 < cursor < len(parts) - 1:
            if start < cursor - 1:
                yield from parts[start : cursor - 1]
            yield f"{parts[cursor - 1]}={parts[cursor + 1]}"
            start = cursor + 2

    if start < len(parts):
        yield from parts[start:]


def _iter(
    pattern: re.Pattern,
    text: str,
    pos: int = 0,
    endpos: int | None = None,
) -> Iterator[re.Match[str] | tuple[int, int]]:
    r"""Iterate over matches of a regex pattern in the given text.

    Search for all occurrences of the specified regex pattern
    in the provided text. Yield the segments of text between matches
    as well as the matches themselves. This allows for processing
    both the matched content and the surrounding text in a single iteration.

    Args:
        pattern (re.Pattern): The compiled regex pattern to search for in the text.
        text (str): The text to search for matches.
        pos (int): The starting position in the text to search for matches.
        endpos (int | None): The ending position in the text to search for matches.

    Yields:
        re.Match | tuple[int, int]: Segments of text and match objects. The segments
        are the parts of the text that are not matched by the pattern, and the
        matches are the regex match objects.

    Examples:
        >>> import re
        >>> pattern = re.compile(r'\d+')
        >>> text = "There are 2 apples and 3 oranges."
        >>> matches = list(_iter(pattern, text))
        >>> matches[0]
        (0, 10)
        >>> matches[1]
        <re.Match object; span=(10, 11), match='2'>
        >>> matches[2]
        (11, 23)
        >>> matches[3]
        <re.Match object; span=(23, 24), match='3'>
        >>> matches[4]
        (24, 33)

    """
    if endpos is None:
        endpos = len(text)

    cursor = pos

    for match in pattern.finditer(text, pos, endpos=endpos):
        start, end = match.start(), match.end()

        if cursor < start:
            yield cursor, start

        yield match

        cursor = end

    if cursor < endpos:
        yield cursor, endpos


def _strip_quotes(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _quote(value: str) -> str:
    if any(c in value for c in " \t\n\r\"'=<>&"):
        if '"' in value:
            return f"'{value}'"
        return f'"{value}"'
    return value


def _parse(text: str) -> tuple[str, list[str], dict[str, str]]:
    """Parse attribute text into identifier, classes, and attributes.

    Parses a string like "#id .class1 .class2 key1=value1 key2=value2"
    into its components.

    Args:
        text (str): The attribute text to parse.

    Returns:
        tuple[str, list[str], dict[str, str]]: A tuple containing:
            - identifier: The ID (without the '#')
            - classes: List of class names (with or without the '.')
            - attributes: Dictionary of attribute key-value pairs
    """
    identifier = ""
    classes = []
    attributes = {}

    for part in split(text):
        if part.startswith("#"):
            identifier = part[1:]
        elif part.startswith("`") and part.endswith("`"):  # for source syntax
            classes.append(part)
        elif "=" in part:
            key, value = part.split("=", 1)
            attributes[key] = _strip_quotes(value)
        else:
            classes.append(part)  # Do not remove the optional leading dot

    return identifier, classes, attributes


@dataclass
class Element:
    """Base class for Markdown elements with attributes.

    Represents a structured element in a Markdown document, with support
    for identifiers, classes, attributes, and other properties.

    Attributes:
        pattern: Regular expression pattern to match the element in text.
        text: The original text of the element.
        identifier: The ID of the element.
        classes: List of class names for the element.
        attributes: Dictionary of attribute key-value pairs.
        code: The code content of the element (for code blocks).
        url: The URL of the element (for links and images).
    """

    pattern: ClassVar[re.Pattern]
    text: str
    identifier: str
    classes: list[str]
    attributes: dict[str, str]
    source: str = ""
    url: str = ""
    indent: str = ""

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        """Create an element from a regex match.

        Args:
            match (re.Match[str]): The regex match object.

        Returns:
            Self: The created element.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError

    @classmethod
    def iter_elements(
        cls,
        text: str,
        pos: int = 0,
        endpos: int | None = None,
    ) -> Iterator[Self | tuple[int, int]]:
        """Iterate through elements in the text.

        Finds all occurrences of the element pattern in the text and
        yields either element instances or text spans.

        Args:
            text (str): The text to search.
            pos (int): The starting position.
            endpos (int | None): The ending position.

        Yields:
            Self | tuple[int, int]: Element instances or text spans.
        """
        for match in _iter(cls.pattern, text, pos, endpos):
            if isinstance(match, re.Match):
                yield cls.from_match(match)

            else:
                yield match

    def iter_parts(
        self,
        *,
        include_identifier: bool = False,
        include_classes: bool = True,
        include_attributes: bool = True,
    ) -> Iterator[str]:
        """Iterate through the parts of the element's attributes.

        Args:
            include_identifier (bool): Whether to include the identifier.
            include_classes (bool): Whether to include the classes.
            include_attributes (bool): Whether to include the attributes.

        Yields:
            str: The parts of the element's attributes.
        """
        if include_identifier and self.identifier:
            yield f"#{self.identifier}"

        if include_classes:
            yield from self.classes

        if include_attributes:
            yield from (f"{k}={_quote(v)}" for k, v in self.attributes.items())


@dataclass
class CodeBlock(Element):
    """A code block in Markdown.

    Represents a fenced code block, with support for language specification
    and attributes.

    Example:
        ```python #id
        print("Hello, world!")
        ```
    """

    pattern: ClassVar[re.Pattern] = re.compile(
        r"^(?P<pre> *[~`]{3,})(?P<body>.*?)\n(?P=pre)",
        re.MULTILINE | re.DOTALL,
    )

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        text = match.group(0)
        body = match.group("body")

        if "\n" in body:
            attr, source = body.split("\n", 1)
        else:
            attr, source = body, ""

        attr = " ".join(_remove_braces(attr.strip()))
        identifier, classes, attributes = _parse(attr)

        url = ""

        if not identifier:
            for k, cls_ in enumerate(classes):
                if "#" in cls_:
                    url, identifier = cls_.split("#", 1)
                    classes = classes[:k] + classes[k + 1 :]
                    break

        return cls(text, identifier, classes, attributes, source=source, url=url)


def _remove_braces(text: str) -> Iterator[str]:
    in_brace = False

    for part in _split(text):
        if part.startswith("{") and part.endswith("}") and in_brace:
            yield part
        elif part.startswith("{") and not in_brace:
            if part.endswith("}"):
                yield part[1:-1]
            else:
                yield part[1:]
                in_brace = True
        elif part.endswith("}") and in_brace:
            yield part[:-1]
            in_brace = False
        else:
            yield part


@dataclass
class Image(Element):
    """An image in Markdown.

    Represents an image with alt text, URL, and attributes.

    Example:
        `![Alt text](image.png){#id .class width=100}`
    """

    pattern = re.compile(
        r"(?<![`])!\[(?P<alt>.*?)\]\((?P<url>.*?)\)\{(?P<attr>.*?)\}(?![`])",
        re.MULTILINE | re.DOTALL,
    )

    alt: str = ""

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        identifier, classes, attributes = _parse(match.group("attr"))

        source = ""

        for k, cls_ in enumerate(classes):
            if cls_.startswith("`") and cls_.endswith("`"):
                source = cls_[1:-1]
                classes = classes[:k] + classes[k + 1 :]
                break

        return cls(
            match.group(0),
            identifier,
            classes,
            attributes,
            source=source,
            url=match.group("url"),
            alt=match.group("alt"),
        )


def parse(
    text: str,
    pos: int = 0,
    endpos: int | None = None,
    classes: tuple[type[Element], ...] = (CodeBlock, Image),
) -> Iterator[CodeBlock | Image | str]:
    """Parse the text and yield elements.

    Finds all occurrences of the specified element types in the text and
    yields either element instances or text segments between elements.

    Args:
        text (str): The text to search.
        pos (int): The starting position.
        endpos (int | None): The ending position.
        classes (tuple[type[Element], ...]): The element types to find.

    Yields:
        Element | str: Element instances or text segments.
    """
    if not classes:
        yield text[pos:endpos]
        return

    indent = ""
    for elem in classes[0].iter_elements(text, pos, endpos):
        if isinstance(elem, tuple):
            prev = text[elem[0] : elem[1]]
            if "\n" not in prev:
                indent = ""
            else:
                indent = prev.rsplit("\n", 1)[-1]
                if not all(c.isspace() for c in indent):
                    indent = ""
            yield from parse(text, elem[0], elem[1] - len(indent), classes[1:])

        elif isinstance(elem, CodeBlock | Image):
            if isinstance(elem, Image):
                elem.indent = indent
            indent = ""
            yield elem

        else:
            raise NotImplementedError


@cache
def get_language(text: str) -> str:
    """Get the language of a Markdown document.

    Determines the primary programming language used in the document's
    code blocks.

    Args:
        text (str): The Markdown text.

    Returns:
        str: The detected language, or "python" if not detected.
    """
    languages = {}
    identifiers = []

    for elem in parse(text):
        if isinstance(elem, CodeBlock) and elem.identifier and elem.classes:
            language = elem.classes[0].removeprefix(".")
            languages[elem.identifier] = language
        elif isinstance(elem, Image) and elem.identifier and elem.url in (".md", ""):
            if elem.identifier in languages:
                return languages[elem.identifier]
            identifiers.append(elem.identifier)

    for identifier in identifiers:
        if identifier in languages:
            return languages[identifier]

    if languages:
        return next(iter(languages.values()))

    return ""


def is_target_code_block(elem: Element | str, language: str) -> TypeGuard[CodeBlock]:
    """Check if an element is a code block with the target language.

    Args:
        elem (Element | str): The element to check.
        language (str): The target language.

    Returns:
        TypeGuard[CodeBlock]: True if the element is a code block with the
            target language, False otherwise.
    """
    if not language:
        return False

    if not isinstance(elem, CodeBlock):
        return False

    if not elem.identifier:
        return False

    return bool(elem.classes and elem.classes[0] in (language, f".{language}"))


def new_notebook(text: str) -> NotebookNode:
    """Create a new notebook from Markdown text.

    Parses the Markdown text, extracts code blocks, and creates a notebook
    with a code cell for each code block.

    Args:
        text (str): The Markdown text.

    Returns:
        NotebookNode: The created notebook.
    """
    language = get_language(text)

    if not language:
        msg = "language not found"
        raise ValueError(msg)

    node = nbformat.v4.new_notebook()
    node["metadata"]["language_info"] = {"name": language}

    for code_block in parse(text):
        if is_target_code_block(code_block, language):
            source = f"# #{code_block.identifier}\n{code_block.source}"
            cell = nbformat.v4.new_code_cell(source)
            node["cells"].append(cell)

    return node
