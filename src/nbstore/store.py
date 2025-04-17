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

    def read_notebook_node(self, url: str) -> NotebookNode:
        url = self.url = url or self.url

        path = self.find_path(url)
        st_mtime = path.stat().st_mtime

        if self.st_mtime.get(path) != st_mtime:
            self.nodes[path] = read_notebook_node(path)
            self.st_mtime[path] = st_mtime

        return self.nodes[path]

    def read_notebook(self, url: str) -> Notebook:
        return Notebook(self.read_notebook_node(url))

    def write_notebook_node(self, url: str, notebook_node: NotebookNode) -> None:
        path = self.find_path(url)
        if path.suffix == ".ipynb":
            nbformat.write(notebook_node, path)
        else:
            raise NotImplementedError

    def write_notebook(self, url: str, notebook: Notebook) -> None:
        self.write_notebook_node(url, notebook.node)


def read_notebook_node(path: str | Path) -> NotebookNode:
    path = Path(path)

    if path.suffix == ".ipynb":
        return nbformat.read(path, as_version=4)  # type: ignore

    text = path.read_text()

    if path.suffix == ".py":
        return convert_python_to_node(text)

    if path.suffix == ".md":
        return convert_markdown_to_node(text)

    raise NotImplementedError


def convert_python_to_node(text: str) -> NotebookNode:
    node = nbformat.v4.new_notebook()
    node["metadata"]["language_info"] = {"name": "python"}

    for source in nbstore.parsers.python.iter_sources(text):
        cell = nbformat.v4.new_code_cell(source)
        node["cells"].append(cell)

    return node


def convert_markdown_to_node(text: str) -> NotebookNode:
    language = nbstore.parsers.markdown.get_language(text)

    if not language:
        msg = "language not found"
        raise ValueError(msg)

    node = nbformat.v4.new_notebook()
    node["metadata"]["language_info"] = {"name": language}

    for code_block in nbstore.parsers.markdown.iter_elements(text):
        if nbstore.parsers.markdown.is_target_code_block(code_block, language):
            source = f"# #{code_block.identifier}\n{code_block.code}"
            cell = nbformat.v4.new_code_cell(source)
            node["cells"].append(cell)

    return node
