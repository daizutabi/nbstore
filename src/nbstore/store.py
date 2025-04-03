from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat import NotebookNode

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class Store:
    notebook_dir: Path
    notebooks: dict[Path, NotebookNode] = field(default_factory=dict, init=False)
    st_mtime: dict[Path, float] = field(default_factory=dict, init=False)
    current_path: Path | None = field(default=None, init=False)

    def _read(self, abs_path: Path) -> NotebookNode:
        mtime = abs_path.stat().st_mtime

        if (nb_ := self.notebooks.get(abs_path)) and self.st_mtime[abs_path] == mtime:
            return nb_

        nb: NotebookNode = nbformat.read(abs_path, as_version=4)  # type: ignore

        self.notebooks[abs_path] = nb
        self.st_mtime[abs_path] = mtime

        return nb

    def _write(self, abs_path: Path) -> None:
        if nb := self.notebooks.get(abs_path):
            nbformat.write(nb, abs_path)

    def _get_abs_path(self, url: str) -> Path:
        if not url and self.current_path:
            return self.current_path

        abs_path = (self.notebook_dir / url).absolute()

        if abs_path.exists():
            self.current_path = abs_path
            return abs_path

        msg = "Unknown path."
        raise ValueError(msg)

    def get_notebook(self, url: str) -> NotebookNode:
        abs_path = self._get_abs_path(url)
        return self._read(abs_path)

    def get_cell(self, url: str, identifier: str) -> dict[str, Any]:
        nb = self.get_notebook(url)
        return get_cell(nb, identifier)

    def get_source(self, url: str, identifier: str) -> str:
        nb = self.get_notebook(url)
        return get_source(nb, identifier)

    def get_outputs(self, url: str, identifier: str) -> list:
        nb = self.get_notebook(url)
        return get_outputs(nb, identifier)

    def get_stream(self, url: str, identifier: str) -> str | None:
        outputs = self.get_outputs(url, identifier)
        return get_stream(outputs)

    def get_data(self, url: str, identifier: str) -> dict[str, str]:
        outputs = self.get_outputs(url, identifier)
        return get_data(outputs)

    def add_data(self, url: str, identifier: str, mime: str, data: str) -> None:
        outputs = self.get_outputs(url, identifier)
        if output := get_data_by_type(outputs, "display_data"):
            output[mime] = data

    def save_notebook(self, url: str) -> None:
        self._write(self._get_abs_path(url))

    def delete_data(self, url: str, identifier: str, mime: str) -> None:
        outputs = self.get_outputs(url, identifier)
        output = get_data_by_type(outputs, "display_data")
        if output and mime in output:
            del output[mime]

    def get_language(self, url: str) -> str:
        nb = self.get_notebook(url)
        return get_language(nb)

    def execute(self, url: str) -> NotebookNode:
        nb = self.get_notebook(url)
        ep = ExecutePreprocessor(timeout=600)
        ep.preprocess(nb)
        return nb


def get_cell(nb: NotebookNode, identifier: str) -> dict[str, Any]:
    for cell in nb["cells"]:
        source: str = cell["source"]
        if source.startswith(f"# #{identifier}\n"):
            return cell

    msg = f"Unknown identifier: {identifier}"
    raise ValueError(msg)


def get_source(nb: NotebookNode, identifier: str) -> str:
    if source := get_cell(nb, identifier).get("source", ""):
        source = "\n".join(source.split("\n")[1:])

    return source


def get_outputs(nb: NotebookNode, identifier: str) -> list:
    return get_cell(nb, identifier).get("outputs", [])


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
    for type_ in ["display_data", "execute_result"]:
        if data := get_data_by_type(outputs, type_):
            return data

    msg = "No output data"
    raise ValueError(msg)


def get_language(nb: dict) -> str:
    return nb["metadata"]["kernelspec"]["language"]
