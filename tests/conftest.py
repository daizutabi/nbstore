from __future__ import annotations

from pathlib import Path

import pytest

from nbstore.store import Store


@pytest.fixture(scope="session")
def src_dir() -> Path:
    return Path(__file__).parent / "notebooks"


@pytest.fixture(scope="session")
def store(src_dir: Path) -> Store:
    return Store(src_dir)
