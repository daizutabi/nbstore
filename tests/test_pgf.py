import io
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from IPython.lib.pretty import RepresentationPrinter
from PIL import Image


@pytest.fixture(scope="module")
def text():
    from nbstore.formatter import matplotlib_figure_to_pgf

    fig, axes = plt.subplots(1, 2, figsize=(4, 2))
    for i in [0, 1]:
        data = np.random.randn(10, 10)
        axes[i].imshow(data, interpolation="nearest", aspect=1)
        axes[i].set(xlabel="x", ylabel="α")

    out = io.StringIO()
    rp = RepresentationPrinter(out)

    matplotlib_figure_to_pgf(fig, rp, None)
    return out.getvalue()


def test_matplotlib_figure_to_pgf_raster(text: str):
    assert text.count("]{data:image/png;base64,iVBOR") == 2


def test_findall(text: str):
    from nbstore.pgf import BASE64_PATTERN

    assert len(BASE64_PATTERN.findall(text)) == 2


def test_convert(text: str):
    from nbstore.pgf import convert

    text = convert(text)

    for filename in re.findall(r"\\includegraphics\[.+?\]{(.+?)}", text):
        assert isinstance(filename, str)
        assert filename.endswith(".png")
        assert Path(filename).exists()
        image = Image.open(filename)
        assert image.format == "PNG"
        assert image.size == (141, 141)


def test_convert_none():
    from nbstore.pgf import convert

    assert convert("abc") == "abc"
