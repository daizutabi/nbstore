from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import nbformat

import nbstore.parsers.markdown
import nbstore.parsers.python

from .notebook import Notebook

if TYPE_CHECKING:
    from collections.abc import Iterable

    from nbformat import NotebookNode


class Store:
    src_dirs: list[Path]
    notebooks: dict[Path, Notebook]
    st_mtime: dict[Path, float]

    def __init__(self, src_dirs: Path | str | Iterable[Path | str]) -> None:
        if isinstance(src_dirs, (str, Path)):
            src_dirs = [src_dirs]

        self.src_dirs = [Path(src_dir) for src_dir in src_dirs]
        self.notebooks = {}
        self.st_mtime = {}

    def find_path(self, url: str) -> Path:
        if Path(url).is_absolute():
            return Path(url)

        for src_dir in self.src_dirs:
            abs_path = (src_dir / url).absolute()
            if abs_path.exists():
                return abs_path

        msg = f"Source file not found in any source directory: {url}"
        raise ValueError(msg)

    def get_notebook(self, url: str) -> Notebook:
        path = self.find_path(url)
        st_mtime = path.stat().st_mtime

        if self.st_mtime.get(path) != st_mtime:
            node = create_notebook_node(path)
            self.notebooks[path] = Notebook(node)
            self.st_mtime[path] = st_mtime

        return self.notebooks[path]


def create_notebook_node(path: str | Path) -> NotebookNode:
    path = Path(path)

    if path.suffix == ".ipynb":
        return nbformat.read(path, as_version=4)  # type: ignore

    text = path.read_text()

    if path.suffix == ".py":
        return create_notebook_node_python(text)

    raise NotImplementedError


def create_notebook_node_python(text: str) -> NotebookNode:
    node = nbformat.v4.new_notebook()
    node["metadata"]["language_info"] = {"name": "python"}

    for source in nbstore.parsers.python.iter_sources(text):
        cell = nbformat.v4.new_code_cell(source)
        node["cells"].append(cell)

    return node
