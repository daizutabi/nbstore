import pytest

from nbstore.store import Store


@pytest.fixture(scope="module", autouse=True)
def _execute(store: Store):
    return store.execute("pdf.ipynb")


def test_cell(store: Store):
    cell = store.get_cell("pdf.ipynb", "fig:pdf")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_source(store: Store):
    source = store.get_source("pdf.ipynb", "fig:pdf")
    assert isinstance(source, str)
    assert "plot" in source


def test_outputs(store: Store):
    outputs = store.get_outputs("pdf.ipynb", "fig:pdf")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_data(store: Store):
    data = store.get_data("pdf.ipynb", "fig:pdf")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/png" in data
    assert data["application/pdf"].startswith("JVBE")


def test_image(store: Store):
    file = store.create_image_file("pdf.ipynb", "fig:pdf", "a", delete=True)
    assert file
    assert file.exists()
    assert file.name == "a.pdf"
