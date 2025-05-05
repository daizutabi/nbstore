"""Utilities for working with Jupyter notebook content.

This module provides functions for extracting and manipulating content
from notebook cells, with a focus on cell identification by unique
identifiers and data extraction from cell outputs.
"""

from __future__ import annotations

import atexit
import base64
import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import nbformat

if TYPE_CHECKING:
    from nbformat import NotebookNode


def get_language(nb: NotebookNode, default: str = "python") -> str:
    """Get the programming language of a notebook.

    Extracts the language from notebook metadata, either from the kernelspec
    or language_info sections.

    Args:
        nb (NotebookNode): The notebook to examine.
        default (str): Default language to return if not found in metadata.

    Returns:
        str: The programming language name.
    """
    metadata = nb["metadata"]

    if "kernelspec" in metadata:
        return metadata["kernelspec"].get("language", default)

    if "language_info" in metadata:
        return metadata["language_info"].get("name", default)

    return default


def get_cell(nb: NotebookNode, identifier: str) -> dict[str, Any]:
    """Get a cell by its identifier.

    Searches for a cell whose source code starts with a specific identifier
    pattern, supporting both "# #" and "# %% #" prefixes.

    Args:
        nb (NotebookNode): The notebook to search.
        identifier (str): The identifier to look for.

    Returns:
        dict[str, Any]: The cell dictionary.

    Raises:
        ValueError: If no cell with the given identifier is found.
    """
    for cell in nb["cells"]:
        source: str = cell["source"]
        for prefix in ["# #", "# %% #", "#| label: "]:
            if source.startswith(f"{prefix}{identifier}\n"):
                return cell

    msg = f"Unknown identifier: {identifier}"
    raise ValueError(msg)


def get_source(
    nb: NotebookNode,
    identifier: str,
    *,
    include_identifier: bool = False,
) -> str:
    """Get the source code of a cell by its identifier.

    Extracts the source code from a cell, optionally including the
    identifier line.

    Args:
        nb (NotebookNode): The notebook to search.
        identifier (str): The identifier of the cell.
        include_identifier (bool): Whether to include the identifier line.

    Returns:
        str: The source code of the cell.

    Raises:
        ValueError: If no cell with the given identifier is found.
        NotImplementedError: If the cell has no source.
    """
    if source := get_cell(nb, identifier).get("source", ""):
        if include_identifier:
            return source

        return source.split("\n", 1)[1]

    raise NotImplementedError


def get_outputs(nb: NotebookNode, identifier: str) -> list:
    """Get the outputs of a cell by its identifier.

    Args:
        nb (NotebookNode): The notebook to search.
        identifier (str): The identifier of the cell.

    Returns:
        list: The outputs of the cell.
    """
    return get_cell(nb, identifier).get("outputs", [])


def _get_data_by_type(outputs: list, output_type: str) -> dict[str, str] | None:
    """Get data from outputs by output type.

    Internal helper function to extract data from outputs based on the output type.

    Args:
        outputs (list): List of output dictionaries.
        output_type (str): The type of output to look for.

    Returns:
        dict[str, str] | None: The data dictionary, or None if not found.
    """
    for output in outputs:
        if output["output_type"] == output_type:
            if output_type == "stream":
                return {"text/plain": output["text"]}

            return output["data"]

    return None


def get_stream(nb: NotebookNode, identifier: str) -> str | None:
    """Get the stream output of a cell by its identifier.

    Args:
        nb (NotebookNode): The notebook to search.
        identifier (str): The identifier of the cell.

    Returns:
        str | None: The stream output text, or None if not found.
    """
    outputs = get_outputs(nb, identifier)
    if data := _get_data_by_type(outputs, "stream"):
        return data["text/plain"]

    return None


def get_data(nb: NotebookNode, identifier: str) -> dict[str, str]:
    """Get the data outputs of a cell by its identifier.

    Tries to find data in various output types, prioritizing display_data,
    execute_result, and stream in that order.

    Args:
        nb (NotebookNode): The notebook to search.
        identifier (str): The identifier of the cell.

    Returns:
        dict[str, str]: The data dictionary, empty if no data is found.
    """
    outputs = get_outputs(nb, identifier)

    for type_ in ["display_data", "execute_result", "stream"]:
        if data := _get_data_by_type(outputs, type_):
            return _convert_data(data)

    return {}


def _convert_data(data: dict[str, str]) -> dict[str, str]:
    """Convert special data formats.

    Currently handles conversion of Matplotlib PGF backend outputs.

    Args:
        data (dict[str, str]): The data dictionary to convert.

    Returns:
        dict[str, str]: The converted data dictionary.
    """
    text = data.get("text/plain")
    if text and text.startswith("%% Creator: Matplotlib, PGF backend"):
        data["text/plain"] = _convert_pgf(text)

    return data


BASE64_PATTERN = re.compile(r"\{data:image/(?P<ext>.*?);base64,(?P<b64>.*?)\}")


def _convert_pgf(text: str) -> str:
    """Convert embedded base64 images in PGF text to file references.

    Args:
        text (str): The PGF text with embedded base64 images.

    Returns:
        str: The converted PGF text with file references.
    """

    def replace(match: re.Match) -> str:
        ext = match.group("ext")
        data = base64.b64decode(match.group("b64"))

        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(data)
            path = Path(tmp.name)

        atexit.register(lambda p=path: p.unlink(missing_ok=True))

        return f"{{{path.absolute()}}}"

    return BASE64_PATTERN.sub(replace, text)


def get_mime_content(
    nb: NotebookNode,
    identifier: str,
) -> tuple[str, str | bytes]:
    """Get the MIME content of a cell by its identifier.

    Extracts the content of a cell output based on MIME type, prioritizing
    SVG, HTML, PDF, other images, and plain text in that order.

    Args:
        nb (NotebookNode): The notebook to search.
        identifier (str): The identifier of the cell.

    Returns:
        tuple[str, str | bytes]: A tuple of (mime_type, content),
            or ("", "") if no content is found.
    """
    data = get_data(nb, identifier)
    for mime in ["image/svg+xml", "text/html"]:
        if text := data.get(mime):
            return mime, text

    if text := data.get("application/pdf"):
        return "application/pdf", base64.b64decode(text)

    for mime, text in data.items():
        if mime.startswith("image/"):
            return mime, base64.b64decode(text)

    if "text/plain" in data:
        return "text/plain", data["text/plain"]

    return "", ""


def add_data(nb: NotebookNode, identifier: str, mime: str, data: str) -> None:
    """Add data to a cell output by its identifier.

    Adds or updates data in a display_data output of a cell.

    Args:
        nb (NotebookNode): The notebook to modify.
        identifier (str): The identifier of the cell.
        mime (str): The MIME type of the data.
        data (str): The data content.
    """
    outputs = get_outputs(nb, identifier)
    if output := _get_data_by_type(outputs, "display_data"):
        output[mime] = data


def new_code_cell(identifier: str, source: str) -> NotebookNode:
    """Create a new code cell with an identifier.

    If the source doesn't already have an identifier, one is added.

    Args:
        identifier (str): The identifier for the cell.
        source (str): The source code.

    Returns:
        NotebookNode: A new code cell.
    """
    if not source.startswith("#") or f"#{identifier}" not in source.split("\n", 1)[0]:
        source = f"# #{identifier}\n{source}"

    return nbformat.v4.new_code_cell(source)


def execute(
    nb: NotebookNode,
    timeout: int = 600,
) -> tuple[NotebookNode, dict[str, Any]]:
    """Execute a notebook.

    Uses nbconvert's ExecutePreprocessor to run all cells in a notebook.

    Args:
        nb (NotebookNode): The notebook to execute.
        timeout (int): Maximum time in seconds to wait for each cell execution.

    Returns:
        tuple[NotebookNode, dict[str, Any]]: The executed notebook and execution info.

    Raises:
        ModuleNotFoundError: If nbconvert is not installed.
    """
    try:
        from nbconvert.preprocessors.execute import ExecutePreprocessor
    except ModuleNotFoundError:  # no cov
        msg = "nbconvert is not installed"
        raise ModuleNotFoundError(msg) from None

    ep = ExecutePreprocessor(timeout=timeout)
    return ep.preprocess(nb)


def equals(nb: NotebookNode, other: NotebookNode) -> bool:
    """Check if two notebooks have the same cells.

    Compares the number of cells and the source of each cell.

    Args:
        nb (NotebookNode): First notebook.
        other (NotebookNode): Second notebook.

    Returns:
        bool: True if the notebooks have the same cells, False otherwise.
    """
    if len(nb["cells"]) != len(other["cells"]):
        return False

    for cell1, cell2 in zip(nb["cells"], other["cells"], strict=False):
        if cell1["source"] != cell2["source"]:
            return False

    return True
