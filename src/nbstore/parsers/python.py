from __future__ import annotations

import re
import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def _split_indent(text: str) -> Iterator[str]:
    lines = text.split("\n")

    for line in lines:
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            break
        else:
            yield text
            return

    for cursor, line in enumerate(lines):
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            block = "\n".join(lines[:cursor])
            yield textwrap.dedent(block)
            yield "\n".join(lines[cursor:])
            return

    yield textwrap.dedent(text)


def _iter(text: str, pattern: re.Pattern, *, dedent: bool = False) -> Iterator[str]:
    start = 0
    lines = text.split("\n")

    for cursor, line in enumerate(lines):
        if pattern.match(line):
            if cursor > start:
                block = "\n".join(lines[start:cursor])
                if dedent:
                    yield from _split_indent(block)
                else:
                    yield block
            start = cursor + (1 if dedent else 0)

    if start < len(lines):
        block = "\n".join(lines[start:])
        if dedent:
            yield from _split_indent(block)
        else:
            yield block


MAIN_PATTERN = re.compile(r"if\s+__name__\s*==\s*['\"]__main__['\"]\s*:")


def _iter_main_blocks(text: str) -> Iterator[str]:
    yield from _iter(text, MAIN_PATTERN, dedent=True)


CELL_PATTERN = re.compile(r"# %%")


def _iter_cells(text: str) -> Iterator[str]:
    yield from _iter(text, CELL_PATTERN, dedent=False)


def iter_cells(text: str) -> Iterator[str]:
    for block in _iter_main_blocks(text):
        yield from _iter_cells(block)
