import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    nb = store.read_notebook("html.ipynb")
    assert not nb.is_executed
    nb.execute()
    assert nb.is_executed
    return nb


def test_outputs(nb: Notebook):
    outputs = nb.get_outputs("html:text")
    assert isinstance(outputs, list)
    assert len(outputs) == 1
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/html" in outputs[0]["data"]


def test_data(nb: Notebook):
    data = nb.get_data("html:text")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/html" in data
    assert data["text/html"] == "<p><strong>Hello, World!</strong></p>"


def test_mime_content(nb: Notebook):
    content = nb.get_mime_content("html:text")
    assert isinstance(content, tuple)
    assert len(content) == 2
    assert isinstance(content[1], str)
    assert content[0] == "text/html"
    assert content[1] == "<p><strong>Hello, World!</strong></p>"


def test_mime_content_png(nb: Notebook):
    content = nb.get_mime_content("html:png")
    assert isinstance(content, tuple)
    assert len(content) == 2
    assert isinstance(content[1], str)
    assert content[0] == "text/html"
    assert content[1].startswith("<img src='data:image/png;base64,iVBOR")
