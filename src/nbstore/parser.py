from __future__ import annotations

from typing import TYPE_CHECKING

from .parsers.markdown import iter_elements
from .store import Store

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path

    from nbstore.parsers.markdown import Element


class Parser:
    store: Store
    elems: list[str | Element]

    def __init__(self, src_dirs: Path | str | Iterable[Path | str]) -> None:
        self.store = Store(src_dirs)
        self.elems = []

    def parse(self, text: str) -> None:
        self.elems = list(iter_elements(text))


# def create_notebook_node_markdown(text: str) -> NotebookNode:
#     language = nbstore.parsers.markdown.get_language(text)

#     if not language:
#         msg = "language not found"
#         raise ValueError(msg)

#     node = nbformat.v4.new_notebook()
#     node["metadata"]["language_info"] = {"name": language}
#     extend_notebook_cells(node, text)
#     return node


# def extend_notebook_cells(node: NotebookNode, text: str) -> None:
#     language = get_language(node)

#     for code_block in nbstore.parsers.markdown.iter_elements(text):
#         if _is_notebook_cell(code_block, language):
#             source = f"# #{code_block.identifier}\n{code_block.code}"
#             cell = nbformat.v4.new_code_cell(source)
#             node["cells"].append(cell)


# def _is_notebook_cell(elem: Element | str, language: str) -> TypeGuard[CodeBlock]:
#     if not isinstance(elem, CodeBlock):
#         return False

#     if not elem.identifier:
#         return False

#     return bool(elem.classes and elem.classes[0] in (language, f".{language}"))
