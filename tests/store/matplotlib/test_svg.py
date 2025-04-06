from nbstore.store import Store


def test_cell(store: Store):
    cell = store.get_cell("svg.ipynb", "fig:svg")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_source(store: Store):
    source = store.get_source("svg.ipynb", "fig:svg")
    assert isinstance(source, str)
    assert "plot" in source


def test_outputs(store: Store):
    outputs = store.get_outputs("svg.ipynb", "fig:svg")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_data(store: Store):
    data = store.get_data("svg.ipynb", "fig:svg")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/png" in data
    assert data["image/svg+xml"].startswith('<?xml version="1.0"')


def test_mime_content(store: Store):
    mime_content = store.get_mime_content("svg.ipynb", "fig:svg")
    assert isinstance(mime_content, tuple)
    mime, content = mime_content
    assert mime == "image/svg+xml"
    assert isinstance(content, str)
    assert content.startswith('<?xml version="1.0"')
