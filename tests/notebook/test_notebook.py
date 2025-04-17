from pathlib import Path

import nbformat
from nbformat import NotebookNode


def test_language_kernel():
    from nbstore.notebook import get_language

    path = Path(__file__).parent.joinpath("kernel.ipynb")
    nb = nbformat.read(path, as_version=4)
    assert isinstance(nb, NotebookNode)
    assert get_language(nb) == "python"


def test_language_info():
    from nbstore.notebook import execute, get_language

    nb = nbformat.v4.new_notebook()
    execute(nb)
    assert get_language(nb) == "python"


def test_language_default():
    from nbstore.notebook import get_language

    nb = nbformat.v4.new_notebook()
    assert isinstance(nb, NotebookNode)
    assert get_language(nb, "julia") == "julia"


SOURCE = """\
# #fig
import matplotlib.pyplot as plt
plt.plot([1, 10, 100], [-1, 0, 1])
"""


def test_add_data():
    from nbstore.notebook import add_data, execute, get_data

    nb = nbformat.v4.new_notebook()
    nb["cells"] = [nbformat.v4.new_code_cell(SOURCE)]
    execute(nb)
    add_data(nb, "fig", "image/pdf", "test")
    data = get_data(nb, "fig")
    assert data["image/pdf"] == "test"


def test_new_code_cell():
    from nbstore.notebook import new_code_cell

    cell = new_code_cell("fig", 'print("test")')
    assert cell["source"] == '# #fig\nprint("test")'


def test_new_code_cell_with_identifier():
    from nbstore.notebook import new_code_cell

    cell = new_code_cell("fig", '# #fig abc\nprint("test")')
    assert cell["source"] == '# #fig abc\nprint("test")'


def test_equals():
    from nbstore.notebook import equals

    nb1 = nbformat.v4.new_notebook()
    nb1["cells"] = [nbformat.v4.new_code_cell("a")]
    nb2 = nbformat.v4.new_notebook()
    assert not equals(nb1, nb2)
    nb2["cells"] = [nbformat.v4.new_code_cell("a")]
    assert equals(nb1, nb2)
    nb2["cells"] = [nbformat.v4.new_code_cell("b")]
    assert not equals(nb1, nb2)
