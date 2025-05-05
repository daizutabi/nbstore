import nbformat
import pytest
from nbformat import NotebookNode

SOURCE_FORMATTER = """\
import matplotlib_inline.backend_inline
from nbstore.formatter import set_formatter
matplotlib_inline.backend_inline.set_matplotlib_formats("retina")
set_formatter("matplotlib", "pdf")
"""

SOURCE_FIG = """\
#| label: fig
import matplotlib.pyplot as plt
plt.plot([1, 10, 100], [-1, 0, 1])
"""


@pytest.fixture(scope="module")
def nb():
    from nbstore.notebook import execute

    nb = nbformat.v4.new_notebook()
    nb["cells"] = [
        nbformat.v4.new_code_cell(SOURCE_FORMATTER),
        nbformat.v4.new_code_cell(SOURCE_FIG),
    ]
    execute(nb)
    return nb


def test_data(nb: NotebookNode):
    from nbstore.notebook import get_data

    data = get_data(nb, "fig")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert "text/plain" in data
    assert "image/png" in data
    assert data["application/pdf"].startswith("JVBE")


def test_mime_content(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    mime_content = get_mime_content(nb, "fig")
    assert isinstance(mime_content, tuple)
    mime, content = mime_content
    assert mime == "application/pdf"
    assert isinstance(content, bytes)
