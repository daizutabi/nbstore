from __future__ import annotations

from pathlib import Path

import pytest

from nbstore.store import Store


@pytest.fixture(scope="session")
def src_dirs() -> list[Path]:
    src_dir = Path(__file__).parent / "src"
    return [src_dir / "jupyter", src_dir / "python"]


@pytest.fixture(scope="session")
def store(src_dirs: list[Path]) -> Store:
    return Store(src_dirs)
