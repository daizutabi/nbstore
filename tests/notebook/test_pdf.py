import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    nb = store.read_notebook("pdf.ipynb")
    assert not nb.is_executed
    nb.execute()
    assert nb.is_executed
    return nb


def test_source(nb: Notebook):
    source = nb.get_source("fig:pdf")
    assert isinstance(source, str)
    assert "plot" in source


def test_outputs(nb: Notebook):
    outputs = nb.get_outputs("fig:pdf")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_mime_content(nb: Notebook):
    data = nb.get_mime_content("fig:pdf")
    assert isinstance(data, tuple)
    assert len(data) == 2
    assert data[0] == "application/pdf"
    assert isinstance(data[1], bytes)


def test_data(nb: Notebook):
    data = nb.get_data("fig:pdf")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/png" in data
    assert data["application/pdf"].startswith("JVBE")
