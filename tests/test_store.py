from pathlib import Path

import pytest

from nbstore.store import Store


def test_find_path(store: Store):
    path = store.find_path("add.ipynb")
    assert path.name == "add.ipynb"


def test_find_path_error_not_found(store: Store):
    with pytest.raises(ValueError, match="Source file not found"):
        store.find_path("unknown")


def test_write(store: Store, tmp_path: Path):
    nb = store.get_notebook("add.ipynb")
    path = tmp_path / "tmp.ipynb"
    nb.write(path)
    store = Store(tmp_path)
    nb_tmp = store.get_notebook("tmp.ipynb")
    assert nb_tmp.equals(nb)
