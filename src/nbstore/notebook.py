from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeGuard

import nbformat

import nbstore.parsers.markdown
import nbstore.parsers.python
import nbstore.pgf
from nbstore.parsers.markdown import CodeBlock

from .content import get_mime_content

if TYPE_CHECKING:
    from typing import Self

    from nbformat import NotebookNode

    from nbstore.parsers.markdown import Element


class Notebook:
    path: Path
    node: NotebookNode
    is_executed: bool

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.node = create_notebook_node(self.path)
        self.is_executed = False

    def extend(self, text: str) -> None:
        extend_notebook_cells(self.node, text)

    def equals(self, other: Notebook) -> bool:
        return equals(self.node, other.node)

    def get_cell(self, identifier: str) -> dict[str, Any]:
        return get_cell(self.node, identifier)

    def get_source(
        self,
        identifier: str,
        *,
        include_identifier: bool = False,
    ) -> str:
        return get_source(self.node, identifier, include_identifier=include_identifier)

    def get_outputs(self, identifier: str) -> list:
        return get_outputs(self.node, identifier)

    def get_stream(self, identifier: str) -> str | None:
        outputs = self.get_outputs(identifier)
        return get_stream(outputs)

    def get_data(self, identifier: str) -> dict[str, str]:
        outputs = self.get_outputs(identifier)
        data = get_data(outputs)
        return convert(data)

    def add_data(self, identifier: str, mime: str, data: str) -> None:
        outputs = self.get_outputs(identifier)
        if output := get_data_by_type(outputs, "display_data"):
            output[mime] = data

    def delete_data(self, identifier: str, mime: str) -> None:
        outputs = self.get_outputs(identifier)
        output = get_data_by_type(outputs, "display_data")
        if output and mime in output:
            del output[mime]

    def get_language(self) -> str:
        return get_language(self.node)

    def execute(self, timeout: int = 600) -> Self:
        try:
            from nbconvert.preprocessors import ExecutePreprocessor
        except ModuleNotFoundError:  # no cov
            msg = "nbconvert is not installed"
            raise ModuleNotFoundError(msg) from None

        ep = ExecutePreprocessor(timeout=timeout)
        ep.preprocess(self.node)
        self.is_executed = True
        return self

    def get_mime_content(self, identifier: str) -> tuple[str, str | bytes] | None:
        data = self.get_data(identifier)
        return get_mime_content(data)

    def write(self, path: str | Path | None = None) -> None:
        path = Path(path or self.path)
        if path.suffix == ".ipynb":
            nbformat.write(self.node, path or self.path)
        else:
            raise NotImplementedError


def get_cell(node: NotebookNode, identifier: str) -> dict[str, Any]:
    for cell in node["cells"]:
        source: str = cell["source"]
        for prefix in ["# #", "# %% #"]:
            if source.startswith(f"{prefix}{identifier}\n"):
                return cell

    msg = f"Unknown identifier: {identifier}"
    raise ValueError(msg)


def get_source(
    node: NotebookNode,
    identifier: str,
    *,
    include_identifier: bool = False,
) -> str:
    if source := get_cell(node, identifier).get("source", ""):
        if include_identifier:
            return source

        return source.split("\n", 1)[1]

    raise NotImplementedError


def get_outputs(node: NotebookNode, identifier: str) -> list:
    return get_cell(node, identifier).get("outputs", [])


def get_data_by_type(outputs: list, output_type: str) -> dict[str, str] | None:
    for output in outputs:
        if output["output_type"] == output_type:
            if output_type == "stream":
                return {"text/plain": output["text"]}

            return output["data"]

    return None


def get_stream(outputs: list) -> str | None:
    if data := get_data_by_type(outputs, "stream"):
        return data["text/plain"]

    return None


def get_data(outputs: list) -> dict[str, str]:
    for type_ in ["display_data", "execute_result", "stream"]:
        if data := get_data_by_type(outputs, type_):
            return data

    return {}


def get_language(node: NotebookNode, default: str = "python") -> str:
    metadata = node["metadata"]
    if "kernelspec" in metadata:
        return metadata["kernelspec"].get("language", default)

    if "language_info" in metadata:
        return metadata["language_info"].get("name", default)

    return default


def convert(data: dict[str, str]) -> dict[str, str]:
    text = data.get("text/plain")
    if text and text.startswith("%% Creator: Matplotlib, PGF backend"):
        data["text/plain"] = nbstore.pgf.convert(text)

    return data


def create_notebook_node(path: str | Path) -> NotebookNode:
    path = Path(path)

    if path.suffix == ".ipynb":
        return nbformat.read(path, as_version=4)  # type: ignore

    text = path.read_text()

    if path.suffix == ".py":
        return create_notebook_node_python(text)

    if path.suffix == ".md":
        return create_notebook_node_markdown(text)

    raise NotImplementedError


def create_notebook_node_python(text: str) -> NotebookNode:
    node = nbformat.v4.new_notebook()
    node["metadata"]["language_info"] = {"name": "python"}

    for source in nbstore.parsers.python.iter_sources(text):
        cell = nbformat.v4.new_code_cell(source)
        node["cells"].append(cell)

    return node


def create_notebook_node_markdown(text: str) -> NotebookNode:
    language = nbstore.parsers.markdown.get_language(text)

    if not language:
        msg = "language not found"
        raise ValueError(msg)

    node = nbformat.v4.new_notebook()
    node["metadata"]["language_info"] = {"name": language}
    extend_notebook_cells(node, text)
    return node


def extend_notebook_cells(node: NotebookNode, text: str) -> None:
    language = get_language(node)

    for code_block in nbstore.parsers.markdown.iter_elements(text):
        if _is_notebook_cell(code_block, language):
            source = f"# #{code_block.identifier}\n{code_block.code}"
            cell = nbformat.v4.new_code_cell(source)
            node["cells"].append(cell)


def _is_notebook_cell(elem: Element | str, language: str) -> TypeGuard[CodeBlock]:
    if not isinstance(elem, CodeBlock):
        return False

    if not elem.identifier:
        return False

    return bool(elem.classes and elem.classes[0] in (language, f".{language}"))


def equals(node: NotebookNode, other: NotebookNode) -> bool:
    if len(node["cells"]) != len(other["cells"]):
        return False

    for cell1, cell2 in zip(node["cells"], other["cells"], strict=False):
        if cell1["source"] != cell2["source"]:
            return False

    return True
