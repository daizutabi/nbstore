import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture
def nb(store: Store):
    return store.read_notebook("add.ipynb")


def test_add_cell(nb: Notebook, store: Store):
    assert nb.equals(store.read_notebook("add.ipynb"))
    nb.add_cell("new", "print('hello')")
    assert nb.get_source("new") == "print('hello')"
    assert not nb.equals(store.read_notebook("add.ipynb"))


def test_add_cell_with_identifier(nb: Notebook):
    nb.add_cell("new", "# #new\nprint('hello')")
    assert nb.get_source("new") == "print('hello')"


def test_equal(nb: Notebook):
    from nbstore.notebook import equals

    node = nb.node
    nb.add_cell("new", "# #new\nprint('hello')")
    node1 = nb.node
    nb.node = node
    nb.add_cell("new", "# #new\nprint('world')")
    node2 = nb.node
    assert not equals(node1, node2)
