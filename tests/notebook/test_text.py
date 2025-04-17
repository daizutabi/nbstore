import nbformat
import pytest
from nbformat import NotebookNode

SOURCE_STDOUT = """\
# #stdout
a = "stdout"
a
"""

SOURCE_STREAM = """\
# #stream
print("stream1")
print("stream2")
"""

SOURCE_BOTH = """\
# #both
print("print")
"hello"
"""

SOURCE_PANDAS = """\
# #pandas
import pandas as pd
pd.DataFrame({"a": [1, 2, 3]})
"""

SOURCE_POLARS = """\
# #polars
import polars as pl
pl.DataFrame({"a": [1, 2, 3]})
"""


@pytest.fixture(scope="module")
def nb():
    from nbstore.notebook import execute

    nb = nbformat.v4.new_notebook()
    nb["cells"] = [
        nbformat.v4.new_code_cell(SOURCE_STDOUT),
        nbformat.v4.new_code_cell(SOURCE_STREAM),
        nbformat.v4.new_code_cell(SOURCE_BOTH),
        nbformat.v4.new_code_cell(SOURCE_PANDAS),
        nbformat.v4.new_code_cell(SOURCE_POLARS),
    ]
    execute(nb)
    return nb


def test_mime_content_stdout(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    content = get_mime_content(nb, "stdout")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "'stdout'"


def test_mime_content_stream(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    content = get_mime_content(nb, "stream")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "stream1\nstream2\n"


def test_mime_content_both(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    content = get_mime_content(nb, "both")
    assert isinstance(content, tuple)
    assert content[0] == "text/plain"
    assert content[1] == "'hello'"


def test_mime_content_pandas(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    content = get_mime_content(nb, "pandas")
    assert isinstance(content, tuple)
    assert content[0] == "text/html"
    assert isinstance(content[1], str)
    assert content[1].startswith("<div>")


def test_mime_content_polars(nb: NotebookNode):
    from nbstore.notebook import get_mime_content

    content = get_mime_content(nb, "polars")
    assert isinstance(content, tuple)
    assert content[0] == "text/html"
    assert isinstance(content[1], str)
    assert content[1].startswith("<div>")
