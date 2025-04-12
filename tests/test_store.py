import time
from pathlib import Path

import pytest

from nbstore.store import Store


def test_find_path(store: Store):
    path = store.find_path("add.ipynb")
    assert path.name == "add.ipynb"
    path = store.find_path("")
    assert path.name == "add.ipynb"


def test_find_path_error(store: Store):
    store.active_path = None
    with pytest.raises(ValueError, match="No active path."):
        store.find_path("")


def test_find_path_error_not_found(store: Store):
    with pytest.raises(ValueError, match="Source file not found"):
        store.find_path("unknown")


def test_set_active_path(store: Store):
    store.set_active_path("add.ipynb")
    assert store.active_path
    assert store.active_path.name == "add.ipynb"


def test_write(store: Store, tmp_path: Path):
    nb = store.get_notebook("add.ipynb")
    path = tmp_path / "tmp.ipynb"
    nb.write(path)
    store = Store(tmp_path)
    assert store.is_dirty("tmp.ipynb")
    nb = store.get_notebook("tmp.ipynb")
    assert not store.is_dirty("tmp.ipynb")
    time.sleep(0.1)
    nb.write()
    assert store.is_dirty("tmp.ipynb")


def test_needs_execution(store: Store):
    assert store.needs_execution("add.ipynb")
    nb = store.get_notebook("add.ipynb")
    nb.execute()
    assert not store.needs_execution("add.ipynb")
