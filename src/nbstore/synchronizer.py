from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeGuard

from .notebook import Notebook
from .parsers.markdown import CodeBlock, Image, get_language, iter_elements
from .store import Store

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path

    from nbstore.parsers.markdown import Element

SUFFIXES = (".ipynb", ".py")


@dataclass
class Parser:
    store: Store
    elems: list[str | Element] = field(default_factory=list, init=False)
    notebooks: dict[str, Notebook] = field(default_factory=dict, init=False)

    def parse(self, text: str) -> None:
        self.elems = list(iter_elements(text))
        language = get_language(self.elems)
        urls = set()
        cells: dict[str, list[str]] = {}

        notebooks = {}

        for elem in self.elems:
            if isinstance(elem, Image | CodeBlock):
                url = elem.url
                if url.endswith(SUFFIXES) and url not in notebooks:
                    notebooks[url] = self.store.read(elem.url)

            if _is_notebook_cell(elem, language) and elem.url.endswith(SUFFIXES):
                notebooks[elem.url] = elem.url


def get_urls(elems: Iterable[str | Element]) -> list[str]:
    urls = set()

    for elem in elems:
        if isinstance(elem, Image | CodeBlock):
            if elem.url.endswith((".ipynb", ".py")):
                urls.add(elem.url)

    return list(urls)


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


# def _is_notebook_cell(
#     elem: Element | str,
#     language: str | None,
# ) -> TypeGuard[CodeBlock]:
#     if language is None:
#         return False

#     if not isinstance(elem, CodeBlock):
#         return False

#     if not elem.identifier:
#         return False

#     return bool(elem.classes and elem.classes[0] in (language, f".{language}"))
