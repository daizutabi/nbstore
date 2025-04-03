import io
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from IPython.lib.pretty import RepresentationPrinter
from PIL import Image

from nbstore.formatter import RASTER_BEGIN, RASTER_END


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
    assert f"\n{RASTER_BEGIN}\n" in text
    assert text.endswith(f"\n{RASTER_END}")


def test_split(text: str):
    from nbstore.pgf import split

    text, images = split(text)
    assert text.startswith("%% Creator: Matplotlib, PGF backend")
    assert text.endswith("\\endgroup%\n")

    assert len(images) == 2

    for name, data in images.items():
        assert name in text
        assert data.startswith("iVBOR")
        assert not data.endswith("\n")


def test_split_none():
    from nbstore.pgf import split

    text, images = split("abc")
    assert text == "abc"
    assert not images


def test_convert_pgf_text(text: str):
    from nbstore.pgf import convert

    text = convert(text)

    for k, x in enumerate(re.findall(r"\\includegraphics\[.+?\]{(.+?)}", text)):
        assert x.endswith(f"-img{k}.png")
        assert Path(x).exists()
        image = Image.open(x)
        assert image.format == "PNG"
        assert image.size == (141, 141)


def test_convert_none():
    from nbstore.pgf import convert

    assert convert("abc") == "abc"
