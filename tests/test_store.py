import nbformat
import pytest

from nbstore.store import Store


def test_find_path(store: Store):
    path = store.find_path("add.ipynb")
    assert path.name == "add.ipynb"


def test_find_path_error_not_found(store: Store):
    with pytest.raises(ValueError, match="Source file not found"):
        store.find_path("unknown")


def test_write_notebook(tmp_path_factory: pytest.TempPathFactory):
    src_dir = tmp_path_factory.mktemp("test")
    path = src_dir.joinpath("a.ipynb")
    path.touch()
    store = Store(src_dir)

    node = nbformat.v4.new_notebook()
    node["cells"] = [nbformat.v4.new_code_cell("# #id\nprint(1)")]
    store.write("a.ipynb", Notebook(node))

    nb = store.read(path.as_posix())
    assert nb.get_source("id") == "print(1)"
