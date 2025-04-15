import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    nb = store.get_notebook("text.ipynb")
    assert not nb.is_executed
    nb.execute()
    assert nb.is_executed
    return nb


def test_mime_content_stdout(nb: Notebook):
    content = nb.get_mime_content("text:stdout")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "'stdout'"


def test_mime_content_stream(nb: Notebook):
    content = nb.get_mime_content("text:stream")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "stream1\nstream2\n"


def test_mime_content_both(nb: Notebook):
    content = nb.get_mime_content("text:both")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "'hello'"


def test_mime_content_pandas(nb: Notebook):
    content = nb.get_mime_content("text:pandas")
    assert isinstance(content, tuple)
    assert content[0] == "text/html"
    assert isinstance(content[1], str)
    assert content[1].startswith("<div>")


def test_mime_content_polars(nb: Notebook):
    content = nb.get_mime_content("text:polars")
    assert isinstance(content, tuple)
    assert content[0] == "text/html"
    assert isinstance(content[1], str)
    assert content[1].startswith("<div>")
