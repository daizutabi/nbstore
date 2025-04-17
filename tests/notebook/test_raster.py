import re
from pathlib import Path

import pytest
from PIL import Image

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    return store.read_notebook("raster.ipynb")


def test_data(nb: Notebook):
    data = nb.get_data("fig:raster")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data


@pytest.fixture(scope="module")
def text(nb: Notebook):
    return nb.get_data("fig:raster")["text/plain"]


def test_backend(text: str):
    assert text.startswith("%% Creator: Matplotlib, PGF backend")


def test_convert(text: str):
    i = 0

    for k, filename in enumerate(
        re.findall(r"\{\\includegraphics\[.+?\]\{(.+?)\}\}", text),
    ):
        assert isinstance(filename, str)
        assert filename.endswith(".png")
        assert Path(filename).exists()
        image = Image.open(filename)
        assert image.format == "PNG"
        if k == 0:
            assert image.size == (71, 71)
        else:
            assert image.size == (141, 141)
        i += 1

    assert i == 2
