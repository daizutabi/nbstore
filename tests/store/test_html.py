import pytest

from nbstore.store import Store


@pytest.fixture(scope="module", autouse=True)
def _execute(store: Store):
    return store.execute("html.ipynb")


def test_outputs(store: Store):
    outputs = store.get_outputs("html.ipynb", "html:text")
    assert isinstance(outputs, list)
    assert len(outputs) == 1
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/html" in outputs[0]["data"]


def test_data(store: Store):
    data = store.get_data("html.ipynb", "html:text")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/html" in data
    assert data["text/html"] == "<p><strong>Hello, World!</strong></p>"


def test_mime_content(store: Store):
    content = store.get_mime_content("html.ipynb", "html:text")
    assert isinstance(content, tuple)
    assert len(content) == 2
    assert isinstance(content[1], str)
    assert content[0] == "text/html"
    assert content[1] == "<p><strong>Hello, World!</strong></p>"


def test_mime_content_png(store: Store):
    content = store.get_mime_content("html.ipynb", "html:png")
    assert isinstance(content, tuple)
    assert len(content) == 2
    assert isinstance(content[1], str)
    assert content[0] == "text/html"
    assert content[1].startswith("<img src='data:image/png;base64,iVBOR")
