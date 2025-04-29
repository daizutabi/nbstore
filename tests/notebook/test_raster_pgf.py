import re
from pathlib import Path

import nbformat
import pytest
from nbformat import NotebookNode
from PIL import Image

SOURCE_FORMATTER = """\
import matplotlib_inline.backend_inline
from nbstore.formatter import set_formatter
matplotlib_inline.backend_inline.set_matplotlib_formats("retina")
set_formatter("matplotlib", "pgf")
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
    assert len(data) == 2
    assert "text/plain" in data


@pytest.fixture(scope="module")
def text(nb: NotebookNode):
    from nbstore.notebook import get_data

    return get_data(nb, "fig")["text/plain"]


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
