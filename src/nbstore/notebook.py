from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import nbformat

import nbstore.pgf

from .content import get_mime_content

if TYPE_CHECKING:
    from typing import Self

    from nbformat import NotebookNode


class Notebook:
    path: Path
    node: NotebookNode
    is_executed: bool

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.node = nbformat.read(self.path, as_version=4)  # type: ignore
        self.is_executed = False

    def write(self) -> None:
        nbformat.write(self.node, self.path)

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


def get_cell(node: NotebookNode, identifier: str) -> dict[str, Any]:
    for cell in node["cells"]:
        source: str = cell["source"]
        if source.startswith(f"# #{identifier}\n"):
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


def get_language(node: NotebookNode) -> str:
    return node["metadata"]["kernelspec"]["language"]


def convert(data: dict[str, str]) -> dict[str, str]:
    text = data.get("text/plain")
    if text and text.startswith("%% Creator: Matplotlib, PGF backend"):
        data["text/plain"] = nbstore.pgf.convert(text)

    return data
