import nbformat
import pytest
from nbformat import NotebookNode

SOURCE = """\
# #fig
import matplotlib.pyplot as plt
plt.plot([1, 10, 100], [-1, 0, 1])
"""


@pytest.fixture(scope="module")
def nb():
    from nbstore.notebook import execute

    nb = nbformat.v4.new_notebook()
    nb["cells"] = [nbformat.v4.new_code_cell(SOURCE)]
    execute(nb)
    return nb


def test_data(nb: NotebookNode):
    from nbstore.notebook import get_data

    data = get_data(nb, "fig")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["image/png"].startswith("iVBO")


def test_mime_content(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    data = get_mime_content(nb, "fig")
    assert isinstance(data, tuple)
    assert len(data) == 2
    assert data[0] == "image/png"
    assert isinstance(data[1], bytes)
