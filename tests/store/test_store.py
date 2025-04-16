import pytest

from nbstore.store import Store


def test_find_path(store: Store):
    path = store.find_path("add.ipynb")
    assert path.name == "add.ipynb"


def test_find_path_error_not_found(store: Store):
    with pytest.raises(ValueError, match="Source file not found"):
        store.find_path("unknown")
