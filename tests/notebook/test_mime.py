from pathlib import Path

import nbformat
from nbformat import NotebookNode


def test_language_kernel():
    from nbstore.notebook import get_data

    path = Path(__file__).parent.joinpath("mime.ipynb")
    nb = nbformat.read(path, as_version=4)
    assert isinstance(nb, NotebookNode)
    data = get_data(nb, "plot")
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/svg+xml" in data
    assert "image/png" in data
