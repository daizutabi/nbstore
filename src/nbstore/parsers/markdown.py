from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Self


def _split(text: str) -> Iterator[str]:
    in_single_quote = False
    in_double_quote = False
    chars = list(text)
    start = 0

    for cursor, char in enumerate(chars):
        if cursor > 0 and chars[cursor - 1] == "\\":
            continue

        if char == "'":
            if in_single_quote:
                yield text[start : cursor + 1]
                start = cursor + 1
            in_single_quote = not in_single_quote

        elif char == '"':
            if in_double_quote:
                yield text[start : cursor + 1]
                start = cursor + 1
            in_double_quote = not in_double_quote

        elif char == " ":
            if not in_single_quote and not in_double_quote:
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

    code: str

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        text = match.group(0)
        body = match.group("body")

        if "\n" in body:
            attr, code = body.split("\n", 1)
        else:
            attr, code = body, ""
        attr = attr.strip()

        if attr.startswith("{") and attr.endswith("}"):
            attr = attr[1:-1]

        identifier, classes, attributes = parse(attr)
        return cls(text, identifier, classes, attributes, code)


@dataclass
class InlineCode(Element):
    pattern: ClassVar[re.Pattern] = re.compile(r"`([^`]+?)`", re.DOTALL)

    code: str

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        return cls(match.group(0), "", [], {}, match.group(1))


@dataclass
class Image(Element):
    pattern = re.compile(
        r"!\[(?P<alt>.*?)\]\((?P<url>.*?)\)\{(?P<attr>.*?)\}",
        re.MULTILINE | re.DOTALL,
    )

    alt: str
    url: str

    @classmethod
    def from_match(cls, match: re.Match[str]) -> Self:
        return cls(
            match.group(0),
            *parse(match.group("attr")),
            match.group("alt"),
            match.group("url"),
        )


def iter_elements(
    text: str,
    pos: int = 0,
    endpos: int | None = None,
    classes: tuple[type[Element], ...] = (CodeBlock, InlineCode, Image),
) -> Iterator[Element | str]:
    if not classes:
        yield text[pos:endpos]
        return

    for elem in classes[0].iter_elements(text, pos, endpos):
        if isinstance(elem, Element):
            yield elem

        else:
            yield from iter_elements(text, elem[0], elem[1], classes[1:])
