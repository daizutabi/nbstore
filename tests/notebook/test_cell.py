import nbformat
import pytest

from nbstore.notebook import Notebook


@pytest.fixture
def nb():
    node = nbformat.v4.new_notebook()
    return Notebook(node)


def test_add_cell(nb: Notebook):
    nb.add_cell("new", "print('hello')")
    assert nb.get_source("new") == "print('hello')"


def test_add_cell_with_identifier(nb: Notebook):
    nb.add_cell("new", "# #new\nprint('hello')")
    assert nb.get_source("new") == "print('hello')"


@pytest.mark.parametrize(("text", "expected"), [("world", False), ("hello", True)])
def test_equal(nb: Notebook, text: str, expected: bool):
    from nbstore.notebook import equals

    node = nb.node
    nb.add_cell("new", "# #new\nprint('hello')")
    assert nb.equals(Notebook(node)) is False
    node1 = nb.node
    nb.node = node
    nb.add_cell("new", f"# #new\nprint('{text}')")
    node2 = nb.node
    assert equals(node1, node2) is expected
    assert Notebook(node1).equals(Notebook(node2)) is expected
