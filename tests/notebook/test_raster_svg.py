import nbformat
import pytest
from nbformat import NotebookNode

SOURCE_FORMATTER = """\
import matplotlib_inline.backend_inline
from nbstore.formatter import set_formatter
matplotlib_inline.backend_inline.set_matplotlib_formats("retina")
set_formatter("matplotlib", "svg")
"""

SOURCE_FIG = """\
# #fig
import matplotlib.pyplot as plt
import numpy as np
data = np.random.randn(50, 50)
fig, axes = plt.subplots(1, 2, figsize=(3, 2), gridspec_kw={"width_ratios": [1, 2]})
axes[0].imshow(data, interpolation="nearest", aspect=1)
axes[1].imshow(data, interpolation="nearest", aspect=1)
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
    assert "image/svg+xml" in data


@pytest.fixture(scope="module")
def svg(nb: NotebookNode):
    from nbstore.notebook import get_data

    return get_data(nb, "fig")["image/svg+xml"]


def test_svg(svg: str):
    assert svg.startswith('<?xml version="1.0" encoding="utf-8" standalone="no"?>')
    assert svg.count('<image xlink:href="data:image/png;base64,') == 2
