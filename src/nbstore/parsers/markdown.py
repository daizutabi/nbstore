from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Self


def _split(text: str) -> Iterator[str]:
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


def parse(text: str) -> tuple[str, list[str], dict[str, str]]:
    identifier = ""
    classes = []
    attributes = {}

    for part in split(text):
        if part.startswith("#"):
            identifier = part[1:]
        elif "=" in part:
            key, value = part.split("=", 1)
            attributes[key] = _strip_quotes(value)
        else:
            classes.append(part)  # Do not remove the optional leading dot

    return identifier, classes, attributes


@dataclass
class Element:
    pattern: ClassVar[re.Pattern]
    text: str
    identifier: str
    classes: list[str]
    attributes: dict[str, str]
    code: str = ""
    url: str = ""

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        raise NotImplementedError

    @classmethod
    def iter_elements(
        cls,
        text: str,
        pos: int = 0,
        endpos: int | None = None,
    ) -> Iterator[Self | tuple[int, int]]:
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
        if include_identifier and self.identifier:
            yield f"#{self.identifier}"

        if include_classes:
            yield from self.classes

        if include_attributes:
            yield from (f"{k}={_quote(v)}" for k, v in self.attributes.items())


@dataclass
class CodeBlock(Element):
    pattern: ClassVar[re.Pattern] = re.compile(
        r"^(?P<pre> *[~`]{3,})(?P<body>.*?)\n(?P=pre)",
        re.MULTILINE | re.DOTALL,
    )

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        text = match.group(0)
        body = match.group("body")

        if "\n" in body:
            attr, code = body.split("\n", 1)
        else:
            attr, code = body, ""

        attr = " ".join(_remove_braces(attr.strip()))
        identifier, classes, attributes = parse(attr)

        url = ""

        if not identifier:
            for k, cls_ in enumerate(classes):
                if "#" in cls_:
                    url, identifier = cls_.split("#", 1)
                    classes = classes[:k] + classes[k + 1 :]
                    break

        return cls(text, identifier, classes, attributes, code=code, url=url)


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
    pattern = re.compile(
        r"(?<![`])!\[(?P<alt>.*?)\]\((?P<url>.*?)\)\{(?P<attr>.*?)\}(?![`])",
        re.MULTILINE | re.DOTALL,
    )

    alt: str = ""

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        identifier, classes, attributes = parse(match.group("attr"))

        code = ""

        for k, cls_ in enumerate(classes):
            if cls_.startswith("`") and cls_.endswith("`"):
                code = cls_[1:-1]
                classes = classes[:k] + classes[k + 1 :]
                break

        return cls(
            match.group(0),
            identifier,
            classes,
            attributes,
            code=code,
            url=match.group("url"),
            alt=match.group("alt"),
        )


def iter_elements(
    text: str,
    pos: int = 0,
    endpos: int | None = None,
    classes: tuple[type[Element], ...] = (CodeBlock, Image),
    url: str = "",
) -> Iterator[Element | str]:
    if not classes:
        yield text[pos:endpos]
        return

    for elem in classes[0].iter_elements(text, pos, endpos):
        if isinstance(elem, Image):
            if not elem.url:
                elem.url = url
            else:
                url = elem.url

            if elem.identifier == "_":  # Just set url, do not yield
                continue

        if isinstance(elem, Element):
            yield elem

        else:
            yield from iter_elements(text, elem[0], elem[1], classes[1:], url)


def get_language(text: str) -> str | None:
    """Get the language of the first code block in the text.

    If there is no code block for a Jupyter notebook, return None.

    Args:
        text (str): The text to get the language from.

    Returns:
        str | None: The language of the first code block with an
        identifier and a class, or None if there is no relevant code block.
    """
    languages = {}
    identifiers = []

    for elem in iter_elements(text):
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

    return None
