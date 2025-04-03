import base64

import holoviews as hv
import polars as pl
import pytest
from holoviews.core.options import Store
from holoviews.plotting.mpl.renderer import MPLRenderer

hv.extension("matplotlib")  # type: ignore


@pytest.fixture(scope="module")
def curve():
    df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
    return hv.Curve(df, "x", "y")


@pytest.fixture(scope="module")
def renderer():
    return Store.renderers["matplotlib"]


@pytest.fixture(scope="module")
def plot(renderer: MPLRenderer, curve):
    return renderer.get_plot(curve)


def test_pgf(renderer: MPLRenderer, plot):
    from nbstore.formatter import set_formatter

    set_formatter("holoviews", "pgf")

    data, metadata = renderer(plot, fmt="pgf")
    assert isinstance(data, bytes)
    assert data.startswith(b"%% Creator: Matplotlib, PGF backend")
    assert isinstance(metadata, dict)
    assert metadata["mime_type"] == "text/pgf"


@pytest.mark.parametrize(
    ("fmt", "text", "mime"),
    [("png", "iVBOR", "image/png"), ("pdf", "JVBER", "application/pdf")],
)
def test_png(renderer: MPLRenderer, plot, fmt, text, mime):
    data, metadata = renderer(plot, fmt=fmt)
    assert isinstance(data, bytes)
    assert base64.b64encode(data).decode().startswith(text)
    assert metadata["mime_type"] == mime


def test_svg(renderer: MPLRenderer, plot):
    xml, metadata = renderer(plot, fmt="svg")
    assert isinstance(xml, str)
    assert xml.startswith('<?xml version="1.0"')
    assert metadata["mime_type"] == "image/svg+xml"
