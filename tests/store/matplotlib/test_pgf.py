import pytest

from nbstore.store import Store


@pytest.fixture(scope="module", autouse=True)
def _execute(store: Store):
    return store.execute("pgf.ipynb")


def test_cell(store: Store):
    cell = store.get_cell("pgf.ipynb", "fig:pgf")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_source(store: Store):
    source = store.get_source("pgf.ipynb", "fig:pgf")
    assert isinstance(source, str)
    assert source.startswith("import")
    assert "plot" in source


def test_outputs(store: Store):
    outputs = store.get_outputs("pgf.ipynb", "fig:pgf")
    assert isinstance(outputs, list)
    assert len(outputs) == 1
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "display_data"
    assert "text/plain" in outputs[0]["data"]


def test_data(store: Store):
    data = store.get_data("pgf.ipynb", "fig:pgf")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["text/plain"].startswith("%% Creator: Matplotlib,")


def test_stream(store: Store):
    assert store.get_stream("pgf.ipynb", "fig:stream") == "123\n"
