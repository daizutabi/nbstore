from pathlib import Path

import nbformat
import pytest
from nbformat import NotebookNode


@pytest.fixture(scope="module")
def nb():
    path = Path(__file__).parent.joinpath("mime.ipynb")
    nb = nbformat.read(path, as_version=4)
    assert isinstance(nb, NotebookNode)
    return nb


def test_mime(nb: NotebookNode):
    from nbstore.notebook import get_data

    data = get_data(nb, "plot")
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/svg+xml" in data
    assert "image/png" in data


def test_text(nb: NotebookNode):
    from nbstore.notebook import get_data

    data = get_data(nb, "text")
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/svg+xml" in data
    assert "image/png" in data
    assert "font-family: 'DejaVu Sans', 'Harano Aji Gothic';" in data["image/svg+xml"]
