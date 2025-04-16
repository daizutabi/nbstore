from __future__ import annotations

from typing import TYPE_CHECKING

from .store import Store

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from nbstore.parsers.markdown import Element


class Parser:
    store: Store
    elems: list[str | Element]

    def __init__(self, src_dirs: Path | str | Iterable[Path | str]) -> None:
        self.store = Store(src_dirs)

    def parse(self) -> list[Element]:
        return list(iter_elements(self.text))
