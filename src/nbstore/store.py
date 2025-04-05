from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import nbformat

from .image import create_image_file, get_content

if TYPE_CHECKING:
    from nbformat import NotebookNode


class Store:
    notebook_dir: Path
    notebooks: dict[Path, NotebookNode]
    st_mtime: dict[Path, float]
    current_path: Path | None

    def __init__(self, notebook_dir: Path | str) -> None:
        self.notebook_dir = Path(notebook_dir)
        self.notebooks = {}
        self.st_mtime = {}
        self.current_path = None

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

    def get_abs_path(self, url: str) -> Path:
        if not url and self.current_path:
            return self.current_path

        abs_path = (self.notebook_dir / url).absolute()

        if abs_path.exists():
            self.current_path = abs_path
            return abs_path

        msg = "Unknown path."
        raise ValueError(msg)

    def get_notebook(self, url: str) -> NotebookNode:
        abs_path = self.get_abs_path(url)
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
        self._write(self.get_abs_path(url))

    def delete_data(self, url: str, identifier: str, mime: str) -> None:
        outputs = self.get_outputs(url, identifier)
        output = get_data_by_type(outputs, "display_data")
        if output and mime in output:
            del output[mime]

    def get_language(self, url: str) -> str:
        nb = self.get_notebook(url)
        return get_language(nb)

    def execute(self, url: str) -> NotebookNode:
        from nbconvert.preprocessors import ExecutePreprocessor

        nb = self.get_notebook(url)
        ep = ExecutePreprocessor(timeout=600)
        ep.preprocess(nb)
        return nb

    def get_content(self, url: str, identifier: str) -> tuple[str | bytes, str] | None:
        data = self.get_data(url, identifier)
        return get_content(data)

    def create_image_file(
        self,
        url: str,
        identifier: str,
        filename: Path | str,
        *,
        delete: bool = False,
    ) -> Path | None:
        data = self.get_data(url, identifier)
        return create_image_file(data, filename, delete=delete)


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
