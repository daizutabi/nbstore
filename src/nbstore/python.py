"""Convert Python scripts to Jupyter notebooks.

This module provides utilities for parsing Python scripts and converting them
to notebook format, with support for cell markers and code block extraction.
"""

from __future__ import annotations

import re
import textwrap
from typing import TYPE_CHECKING

import nbformat

if TYPE_CHECKING:
    from collections.abc import Iterator

    from nbformat import NotebookNode


def _split_indent(text: str) -> Iterator[str]:
    """Split text at the first unindented line after indented lines.

    Handles code blocks with mixed indentation by splitting at the first
    non-indented line after indented lines. This is useful for extracting
    code blocks like if __name__ == "__main__" sections.

    Args:
        text (str): The text to split.

    Yields:
        str: The split text blocks.
    """
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
    """Iterate through text blocks separated by pattern matches.

    Splits the text at lines matching the pattern and yields each block.

    Args:
        text (str): The text to iterate through.
        pattern (re.Pattern): The pattern to match.
        dedent (bool): Whether to dedent indented blocks.

    Yields:
        str: The text blocks.
    """
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
    """Iterate through main blocks in the text.

    Splits the text at 'if __name__ == "__main__":' lines and yields each block.

    Args:
        text (str): The text to iterate through.

    Yields:
        str: The main blocks.
    """
    yield from _iter(text, MAIN_PATTERN, dedent=True)


CELL_PATTERN = re.compile(r"# %%")


def _iter_sources(text: str) -> Iterator[str]:
    """Iterate through cell sources in the text.

    Splits the text at '# %%' cell markers and yields each cell.

    Args:
        text (str): The text to iterate through.

    Yields:
        str: The cell sources.
    """
    yield from _iter(text, CELL_PATTERN, dedent=False)


def parse(text: str) -> Iterator[str]:
    """Parse the text and yield sources.

    First splits the text at 'if __name__ == "__main__":' lines,
    then splits each block at '# %%' cell markers.

    Args:
        text (str): The text to parse.

    Yields:
        str: The sources.
    """
    for block in _iter_main_blocks(text):
        for source in _iter_sources(block):
            yield source.rstrip()


def new_notebook(text: str) -> NotebookNode:
    """Create a new notebook from Python code.

    Parses the Python code, extracts cell sources, and creates a notebook
    with a code cell for each source.

    Args:
        text (str): The Python code to convert.

    Returns:
        NotebookNode: The created notebook.
    """
    node = nbformat.v4.new_notebook()
    node["metadata"]["language_info"] = {"name": "python"}

    for source in parse(text):
        cell = nbformat.v4.new_code_cell(source)
        node["cells"].append(cell)

    return node
