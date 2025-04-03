from __future__ import annotations

from pathlib import Path

import pytest

from nbstore.store import Store


@pytest.fixture(scope="session")
def notebook_dir() -> Path:
    return Path(__file__).parent / "notebooks"


@pytest.fixture(scope="session")
def store(notebook_dir):
    return Store(notebook_dir)
