from __future__ import annotations

import atexit
import base64
import copy
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import nbformat

if TYPE_CHECKING:
    from typing import Self

    from nbformat import NotebookNode


@dataclass
class Notebook:
    node: NotebookNode
    is_modified: bool = False
    is_executed: bool = False

    def equals(self, other: Notebook) -> bool:
        return equals(self.node, other.node)

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

    def get_language(self) -> str:
        return get_language(self.node)

    def get_cell(self, identifier: str) -> dict[str, Any]:
        return get_cell(self.node, identifier)

    def add_cell(self, identifier: str, source: str) -> Self:
        if not self.is_modified:
            self.node = copy.deepcopy(self.node)
            self.is_modified = True

        if (
            not source.startswith("#")
            or f"#{identifier}" not in source.split("\n", 1)[0]
        ):
            source = f"# #{identifier}\n{source}"

        cell = nbformat.v4.new_code_cell(source)
        self.node["cells"].append(cell)
        return self

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
        return convert_data(data)

    def add_data(self, identifier: str, mime: str, data: str) -> Self:
        outputs = self.get_outputs(identifier)
        if output := get_data_by_type(outputs, "display_data"):
            output[mime] = data
        return self

    def delete_data(self, identifier: str, mime: str) -> Self:
        outputs = self.get_outputs(identifier)
        output = get_data_by_type(outputs, "display_data")
        if output and mime in output:
            del output[mime]
        return self

    def get_mime_content(self, identifier: str) -> tuple[str, str | bytes] | None:
        data = self.get_data(identifier)
        return get_mime_content(data)


def equals(node: NotebookNode, other: NotebookNode) -> bool:
    if len(node["cells"]) != len(other["cells"]):
        return False

    for cell1, cell2 in zip(node["cells"], other["cells"], strict=False):
        if cell1["source"] != cell2["source"]:
            return False

    return True


def get_language(node: NotebookNode, default: str = "python") -> str:
    metadata = node["metadata"]
    if "kernelspec" in metadata:
        return metadata["kernelspec"].get("language", default)

    if "language_info" in metadata:
        return metadata["language_info"].get("name", default)

    return default


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


def convert_data(data: dict[str, str]) -> dict[str, str]:
    text = data.get("text/plain")
    if text and text.startswith("%% Creator: Matplotlib, PGF backend"):
        data["text/plain"] = convert_pgf(text)

    return data


BASE64_PATTERN = re.compile(r"\{data:image/(?P<ext>.*?);base64,(?P<b64>.*?)\}")


def convert_pgf(text: str) -> str:
    def replace(match: re.Match) -> str:
        ext = match.group("ext")
        data = base64.b64decode(match.group("b64"))

        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(data)
            path = Path(tmp.name)

        atexit.register(lambda p=path: p.unlink(missing_ok=True))

        return f"{{{path.absolute()}}}"

    return BASE64_PATTERN.sub(replace, text)


def get_mime_content(data: dict[str, str]) -> tuple[str, str | bytes] | None:
    """Get the content of a notebook cell.

    Args:
        data (dict[str, str]): The data of a notebook cell.

    Returns:
        tuple[str, str | bytes] | None: A tuple of the mime type and the content.
    """
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

    return None
