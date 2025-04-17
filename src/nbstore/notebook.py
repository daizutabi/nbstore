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
    metadata = nb["metadata"]

    if "kernelspec" in metadata:
        return metadata["kernelspec"].get("language", default)

    if "language_info" in metadata:
        return metadata["language_info"].get("name", default)

    return default


def get_cell(nb: NotebookNode, identifier: str) -> dict[str, Any]:
    for cell in nb["cells"]:
        source: str = cell["source"]
        for prefix in ["# #", "# %% #"]:
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
    if source := get_cell(nb, identifier).get("source", ""):
        if include_identifier:
            return source

        return source.split("\n", 1)[1]

    raise NotImplementedError


def get_outputs(nb: NotebookNode, identifier: str) -> list:
    return get_cell(nb, identifier).get("outputs", [])


def _get_data_by_type(outputs: list, output_type: str) -> dict[str, str] | None:
    for output in outputs:
        if output["output_type"] == output_type:
            if output_type == "stream":
                return {"text/plain": output["text"]}

            return output["data"]

    return None


def get_stream(nb: NotebookNode, identifier: str) -> str | None:
    outputs = get_outputs(nb, identifier)
    if data := _get_data_by_type(outputs, "stream"):
        return data["text/plain"]

    return None


def get_data(nb: NotebookNode, identifier: str) -> dict[str, str]:
    outputs = get_outputs(nb, identifier)

    for type_ in ["display_data", "execute_result", "stream"]:
        if data := _get_data_by_type(outputs, type_):
            return _convert_data(data)

    return {}


def _convert_data(data: dict[str, str]) -> dict[str, str]:
    text = data.get("text/plain")
    if text and text.startswith("%% Creator: Matplotlib, PGF backend"):
        data["text/plain"] = _convert_pgf(text)

    return data


BASE64_PATTERN = re.compile(r"\{data:image/(?P<ext>.*?);base64,(?P<b64>.*?)\}")


def _convert_pgf(text: str) -> str:
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
) -> tuple[str, str | bytes] | None:
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

    return None


def add_data(nb: NotebookNode, identifier: str, mime: str, data: str) -> None:
    outputs = get_outputs(nb, identifier)
    if output := _get_data_by_type(outputs, "display_data"):
        output[mime] = data


def new_code_cell(identifier: str, source: str) -> NotebookNode:
    if not source.startswith("#") or f"#{identifier}" not in source.split("\n", 1)[0]:
        source = f"# #{identifier}\n{source}"

    return nbformat.v4.new_code_cell(source)


def execute(
    nb: NotebookNode,
    timeout: int = 600,
) -> tuple[NotebookNode, dict[str, Any]]:
    try:
        from nbconvert.preprocessors.execute import ExecutePreprocessor
    except ModuleNotFoundError:  # no cov
        msg = "nbconvert is not installed"
        raise ModuleNotFoundError(msg) from None

    ep = ExecutePreprocessor(timeout=timeout)
    return ep.preprocess(nb)


def equals(nb: NotebookNode, other: NotebookNode) -> bool:
    if len(nb["cells"]) != len(other["cells"]):
        return False

    for cell1, cell2 in zip(nb["cells"], other["cells"], strict=False):
        if cell1["source"] != cell2["source"]:
            return False

    return True
