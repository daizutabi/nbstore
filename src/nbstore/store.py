from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .notebook import Notebook

if TYPE_CHECKING:
    from collections.abc import Iterable


class Store:
    src_dirs: list[Path]
    active_path: Path | None
    notebooks: dict[Path, Notebook]
    st_mtime: dict[Path, float]

    def __init__(self, src_dirs: Path | str | Iterable[Path | str]) -> None:
        if isinstance(src_dirs, (str, Path)):
            src_dirs = [src_dirs]

        self.src_dirs = [Path(src_dir) for src_dir in src_dirs]
        self.active_path = None
        self.notebooks = {}
        self.st_mtime = {}

    def find_path(self, url: str) -> Path:
        if not url:
            if self.active_path:
                return self.active_path

            msg = "No active path."
            raise ValueError(msg)

        for src_dir in self.src_dirs:
            abs_path = (src_dir / url).absolute()
            if abs_path.exists():
                self.active_path = abs_path
                return abs_path

        msg = f"Source file not found in any source directory: {url}"
        raise ValueError(msg)

    def is_dirty(self, url: str) -> bool:
        path = self.find_path(url)
        if path not in self.st_mtime:
            return True

        return self.st_mtime[path] != path.stat().st_mtime

    def get_notebook(self, url: str) -> Notebook:
        path = self.find_path(url)
        st_mtime = path.stat().st_mtime

        if self.st_mtime.get(path) != st_mtime:
            self.st_mtime[path] = st_mtime
            self.notebooks[path] = Notebook(path)

        return self.notebooks[path]

    def needs_execution(self, url: str) -> bool:
        notebook = self.get_notebook(url)
        return not notebook.is_executed
