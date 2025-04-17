import nbformat
import pytest
from nbformat import NotebookNode

SOURCE = """\
# #html
from IPython.display import HTML
HTML("<p><strong>Hello, World!</strong></p>")
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

    data = get_data(nb, "html")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/html" in data
    assert data["text/html"] == "<p><strong>Hello, World!</strong></p>"


def test_mime_content(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    content = get_mime_content(nb, "html")
    assert isinstance(content, tuple)
    assert len(content) == 2
    assert isinstance(content[1], str)
    assert content[0] == "text/html"
    assert content[1] == "<p><strong>Hello, World!</strong></p>"
