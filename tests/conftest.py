from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def _read_write():
    path = Path("tests/notebooks/pgf.ipynb")
    nb = path.read_text("utf-8")
    yield
    path.write_text(nb, "utf-8")


@pytest.fixture(scope="session")
def notebook_dir() -> Path:
    return Path("tests/notebooks")


@pytest.fixture(scope="session")
def store(notebook_dir):
    from nbstore.store import Store

    return Store([notebook_dir])


@pytest.fixture(params=["png", "pgf", "pdf", "svg"])
def fmt(request: pytest.FixtureRequest):
    return request.param
