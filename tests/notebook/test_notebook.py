# import nbformat
import pytest

# from nbstore.notebook import Notebook
# from nbstore.store import Store


# @pytest.fixture(scope="module")
# def nb(store: Store):
#     return store.read("add.ipynb")


# def test_add_delete(nb: Notebook):
#     nb.add_data("add", "text/plain", "text")
#     data = nb.get_data("add")
#     assert data["text/plain"] == "text"
#     nb.delete_data("add", "text/plain")
#     data = nb.get_data("add")
#     assert "text/plain" not in data


# def test_language(nb: Notebook):
#     assert nb.get_language() == "python"


# def test_stream_none(nb: Notebook):
#     assert nb.get_stream("add") is None


# def test_data_empty(nb: Notebook):
#     assert nb.get_data("empty") == {}


# def test_source_include_identifier(nb: Notebook):
#     source = nb.get_source("add", include_identifier=True)
#     assert source.startswith("# #add\n")


# def test_get_mime_content():
#     from nbstore.notebook import get_mime_content

#     assert get_mime_content({}) is None


# @pytest.fixture
# def nb():
#     node = nbformat.v4.new_notebook()
#     return Notebook(node)


# def test_add_cell(nb: Notebook):
#     nb.add_cell("new", "print('hello')")
#     assert nb.get_source("new") == "print('hello')"


# def test_add_cell_with_identifier(nb: Notebook):
#     nb.add_cell("new", "# #new\nprint('hello')")
#     assert nb.get_source("new") == "print('hello')"


# @pytest.mark.parametrize(("text", "expected"), [("world", False), ("hello", True)])
# def test_equal(nb: Notebook, text: str, expected: bool):
#     from nbstore.notebook import equals

#     node = nb.node
#     nb.add_cell("new", "# #new\nprint('hello')")
#     assert nb.equals(Notebook(node)) is False
#     node1 = nb.node
#     nb.node = node
#     nb.add_cell("new", f"# #new\nprint('{text}')")
#     node2 = nb.node
#     assert equals(node1, node2) is expected
#     assert Notebook(node1).equals(Notebook(node2)) is expected
