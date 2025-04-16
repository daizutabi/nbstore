import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    return store.read_notebook("svg.ipynb")


def test_cell(nb: Notebook):
    cell = nb.get_cell("fig:svg")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_source(nb: Notebook):
    source = nb.get_source("fig:svg")
    assert isinstance(source, str)
    assert "plot" in source


def test_outputs(nb: Notebook):
    outputs = nb.get_outputs("fig:svg")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_data(nb: Notebook):
    data = nb.get_data("fig:svg")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/png" in data
    assert data["image/svg+xml"].startswith('<?xml version="1.0"')


def test_mime_content(nb: Notebook):
    mime_content = nb.get_mime_content("fig:svg")
    assert isinstance(mime_content, tuple)
    mime, content = mime_content
    assert mime == "image/svg+xml"
    assert isinstance(content, str)
    assert content.startswith('<?xml version="1.0"')
