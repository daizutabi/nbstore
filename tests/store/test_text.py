import pytest

from nbstore.store import Store


@pytest.fixture(scope="module", autouse=True)
def _execute(store: Store):
    return store.execute("text.ipynb")


def test_mime_content_stdout(store: Store):
    content = store.get_mime_content("text.ipynb", "text:stdout")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "'stdout'"


def test_mime_content_stream(store: Store):
    content = store.get_mime_content("text.ipynb", "text:stream")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "stream1\nstream2"


def test_mime_content_both(store: Store):
    content = store.get_mime_content("text.ipynb", "text:both")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "'hello'"


def test_mime_content_pandas(store: Store):
    content = store.get_mime_content("text.ipynb", "text:pandas")
    assert isinstance(content, tuple)
    assert content[0] == "text/html"
    assert isinstance(content[1], str)
    assert content[1].startswith("<div>")


def test_mime_content_polars(store: Store):
    content = store.get_mime_content("text.ipynb", "text:polars")
    assert isinstance(content, tuple)
    assert content[0] == "text/html"
    assert isinstance(content[1], str)
    assert content[1].startswith("<div>")
