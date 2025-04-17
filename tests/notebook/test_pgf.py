import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    store.read_notebook("pgf.ipynb")
    nb = store.read_notebook("")
    assert not nb.is_executed
    nb.execute()
    assert nb.is_executed
    return nb


def test_cell(nb: Notebook):
    cell = nb.get_cell("fig:pgf")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_source(nb: Notebook):
    source = nb.get_source("fig:pgf")
    assert isinstance(source, str)
    assert source.startswith("import")
    assert "plot" in source


def test_outputs(nb: Notebook):
    outputs = nb.get_outputs("fig:pgf")
    assert isinstance(outputs, list)
    assert len(outputs) == 1
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "display_data"
    assert "text/plain" in outputs[0]["data"]


def test_data(nb: Notebook):
    data = nb.get_data("fig:pgf")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["text/plain"].startswith("%% Creator: Matplotlib,")


def test_stream(nb: Notebook):
    assert nb.get_stream("fig:stream") == "123\n"
