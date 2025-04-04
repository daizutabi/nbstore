import pytest
from PIL import Image

from nbstore.store import Store


@pytest.fixture(scope="module", autouse=True)
def _execute(store: Store):
    return store.execute("png.ipynb")


def test_cell(store: Store):
    cell = store.get_cell("png.ipynb", "fig:png")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_source(store: Store):
    source = store.get_source("png.ipynb", "fig:png")
    assert isinstance(source, str)
    assert "plot" in source


def test_outputs(store: Store):
    outputs = store.get_outputs("png.ipynb", "fig:png")
    assert isinstance(outputs, list)
    assert len(outputs) == 2
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]
    assert isinstance(outputs[1], dict)
    assert outputs[1]["output_type"] == "display_data"


def test_data(store: Store):
    data = store.get_data("png.ipynb", "fig:png")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["image/png"].startswith("iVBO")


def test_image(store: Store):
    file = store.create_image_file("png.ipynb", "fig:png", "a", delete=True)
    assert file
    assert file.exists()
    assert file.name == "a.png"
    image = Image.open(file)
    assert image.format == "PNG"
    assert image.size == (1136, 826)


def test_image_none():
    from nbstore.image import create_image_file

    assert create_image_file({}, "a") is None
