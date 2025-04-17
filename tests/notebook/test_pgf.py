import nbformat
import pytest
from nbformat import NotebookNode

SOURCE_FORMATTER = """\
import matplotlib_inline.backend_inline
from nbstore.formatter import set_formatter
matplotlib_inline.backend_inline.set_matplotlib_formats("retina")
set_formatter("matplotlib", "pgf")
"""

SOURCE_FIG = """\
# #fig
import matplotlib.pyplot as plt
plt.plot([1, 10, 100], [-1, 0, 1])
"""

SOURCE_STREAM = """\
# #stream
print(123)
"""

SOURCE_EMPTY = """\
# #empty
"""


@pytest.fixture(scope="module")
def nb():
    from nbstore.notebook import execute

    nb = nbformat.v4.new_notebook()
    nb["cells"] = [
        nbformat.v4.new_code_cell(SOURCE_FORMATTER),
        nbformat.v4.new_code_cell(SOURCE_FIG),
        nbformat.v4.new_code_cell(SOURCE_STREAM),
        nbformat.v4.new_code_cell(SOURCE_EMPTY),
    ]
    execute(nb)
    return nb


def test_cell(nb: NotebookNode):
    from nbstore.notebook import get_cell

    cell = get_cell(nb, "fig")
    assert isinstance(cell, dict)
    assert "cell_type" in cell


def test_cell_error(nb: NotebookNode):
    from nbstore.notebook import get_cell

    with pytest.raises(ValueError, match="Unknown identifier: unknown"):
        get_cell(nb, "unknown")


def test_source(nb: NotebookNode):
    from nbstore.notebook import get_source

    source = get_source(nb, "fig")
    assert isinstance(source, str)
    assert source.startswith("import")
    assert "plt.plot" in source


def test_source_with_identifier(nb: NotebookNode):
    from nbstore.notebook import get_source

    source = get_source(nb, "fig", include_identifier=True)
    assert isinstance(source, str)
    assert source.startswith("# #fig\n")


def test_outputs(nb: NotebookNode):
    from nbstore.notebook import get_outputs

    outputs = get_outputs(nb, "fig")
    assert isinstance(outputs, list)
    assert len(outputs) == 2


def test_data(nb: NotebookNode):
    from nbstore.notebook import get_data

    data = get_data(nb, "fig")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["text/plain"].startswith("%% Creator: Matplotlib,")


def test_stream(nb: NotebookNode):
    from nbstore.notebook import get_stream

    stream = get_stream(nb, "stream")
    assert isinstance(stream, str)
    assert stream == "123\n"


def test_stream_none(nb: NotebookNode):
    from nbstore.notebook import get_stream

    assert get_stream(nb, "empty") is None


def test_data_empty(nb: NotebookNode):
    from nbstore.notebook import get_data

    assert get_data(nb, "empty") == {}


def test_mime_content_empty(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    assert get_mime_content(nb, "empty") is None
