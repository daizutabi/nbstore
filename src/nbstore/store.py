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
    src_dirs: list[Path]
    nodes: dict[Path, NotebookNode]
    st_mtime: dict[Path, float]
    url: str

    def __init__(self, src_dirs: Path | str | Iterable[Path | str]) -> None:
        if isinstance(src_dirs, (str, Path)):
            src_dirs = [src_dirs]

        self.src_dirs = [Path(src_dir) for src_dir in src_dirs]
        self.nodes = {}
        self.st_mtime = {}
        self.url = ""

    def find_path(self, url: str) -> Path:
        if Path(url).is_absolute():
            return Path(url)

        for src_dir in self.src_dirs:
            abs_path = (src_dir / url).absolute()
            if abs_path.exists():
                return abs_path

        msg = f"Source file not found in any source directory: {url}"
        raise ValueError(msg)

    def read(self, url: str) -> NotebookNode:
        url = self.url = url or self.url

        path = self.find_path(url)
        st_mtime = path.stat().st_mtime

        if self.st_mtime.get(path) != st_mtime:
            self.nodes[path] = read(path)
            self.st_mtime[path] = st_mtime

        return self.nodes[path]

    def write(self, url: str, notebook_node: NotebookNode) -> None:
        path = self.find_path(url)

        if path.suffix == ".ipynb":
            return nbformat.write(notebook_node, path)

        raise NotImplementedError


def read(path: str | Path) -> NotebookNode:
    path = Path(path)

    if path.suffix == ".ipynb":
        return nbformat.read(path, as_version=4)  # type: ignore

    text = path.read_text()

    if path.suffix == ".py":
        return nbstore.python.new_notebook(text)

    if path.suffix == ".md":
        return nbstore.markdown.new_notebook(text)

    raise NotImplementedError
