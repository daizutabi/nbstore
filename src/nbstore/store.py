"""Core functionality for reading and managing notebook files.

This module provides the main interface for accessing notebook content
from various file formats and managing notebook instances in memory.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import nbformat

import nbstore.markdown
import nbstore.python

if TYPE_CHECKING:
    from collections.abc import Iterable

    from nbformat import NotebookNode


class Store:
    """Manage notebook files from one or more source directories.

    Provides a centralized interface for reading notebook files and caching
    their content for efficient access. Automatically reloads files when
    they have been modified on disk.

    Attributes:
        src_dirs: List of source directories to search for notebook files.
        nodes: Dictionary mapping file paths to their notebook nodes.
        st_mtime: Dictionary mapping file paths to their last modification times.
        url: String representing the last accessed URL.
    """

    src_dirs: list[Path]
    nodes: dict[Path, NotebookNode]
    st_mtime: dict[Path, float]
    url: str

    def __init__(self, src_dirs: str | Path | Iterable[str | Path]) -> None:
        """Initialize a new Store instance.

        Args:
            src_dirs (str | Path | Iterable[str | Path]): One or more directories
                to search for notebook files. Can be a single path or a collection
                of paths.
        """
        if isinstance(src_dirs, (str, Path)):
            src_dirs = [src_dirs]

        self.src_dirs = [Path(src_dir) for src_dir in src_dirs]
        self.nodes = {}
        self.st_mtime = {}
        self.url = ""

    def find_path(self, url: str) -> Path:
        """Find the absolute path of a notebook file.

        Searches for the notebook file in the source directories. If the URL is
        an absolute path, it is returned directly.

        Args:
            url (str): The URL or relative path of the notebook file.

        Returns:
            Path: The absolute path to the notebook file.

        Raises:
            ValueError: If the file cannot be found in any source directory.
        """
        if Path(url).is_absolute():
            return Path(url)

        for src_dir in self.src_dirs:
            abs_path = (src_dir / url).absolute()
            if abs_path.exists():
                return abs_path

        msg = f"Source file not found in any source directory: {url}"
        raise ValueError(msg)

    def read(self, url: str) -> NotebookNode:
        """Read a notebook file and return its content.

        If the file has been modified since it was last read, it is reloaded.
        If no URL is provided, the last URL is used.

        Args:
            url (str): The URL or relative path of the notebook file.

        Returns:
            NotebookNode: The notebook content.
        """
        url = self.url = url or self.url

        path = self.find_path(url)
        st_mtime = path.stat().st_mtime

        if self.st_mtime.get(path) != st_mtime:
            self.nodes[path] = read(path)
            self.st_mtime[path] = st_mtime

        return self.nodes[path]

    def write(self, url: str, notebook_node: NotebookNode) -> None:
        """Write a notebook node to a file.

        Currently only supports writing to .ipynb files.

        Args:
            url (str): The URL or relative path of the notebook file.
            notebook_node (NotebookNode): The notebook content to write.

        Raises:
            NotImplementedError: If the file format is not supported for writing.
        """
        url = url or self.url

        path = self.find_path(url)

        if path.suffix == ".ipynb":
            return nbformat.write(notebook_node, path)

        raise NotImplementedError


def read(path: str | Path) -> NotebookNode:
    """Read a notebook file and return its content.

    Supports .ipynb, .py, and .md file formats.

    Args:
        path (str | Path): The path to the notebook file.

    Returns:
        NotebookNode: The notebook content.

    Raises:
        NotImplementedError: If the file format is not supported.
    """
    path = Path(path)

    if path.suffix == ".ipynb":
        return nbformat.read(path, as_version=4)  # type: ignore

    text = path.read_text()

    if path.suffix == ".py":
        return nbstore.python.new_notebook(text)

    if path.suffix == ".md":
        return nbstore.markdown.new_notebook(text)

    raise NotImplementedError
