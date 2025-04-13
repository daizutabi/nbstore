import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    nb = store.get_notebook("png.ipynb")
    assert not nb.is_executed
    nb.execute()
    assert nb.is_executed
    return nb


def test_cell(nb: Notebook):
    cell = nb.get_cell("fig:png")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_source(nb: Notebook):
    source = nb.get_source("fig:png")
    assert isinstance(source, str)
    assert "plot" in source


def test_outputs(nb: Notebook):
    outputs = nb.get_outputs("fig:png")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_data(nb: Notebook):
    data = nb.get_data("fig:png")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["image/png"].startswith("iVBO")


def test_mime_content(nb: Notebook):
    data = nb.get_mime_content("fig:png")
    assert isinstance(data, tuple)
    assert len(data) == 2
    assert data[0] == "image/png"
    assert isinstance(data[1], bytes)
