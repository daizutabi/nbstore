import base64
import io

import matplotlib.pyplot as plt
import pytest
from IPython.core.formatters import PDFFormatter, PlainTextFormatter, SVGFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.lib.pretty import RepresentationPrinter
from matplotlib.figure import Figure

from nbstore.formatter import FUNCTIONS


def get_func(fmt: str):
    functions = FUNCTIONS.get(("matplotlib.figure", "Figure"))
    assert functions
    function = functions.get(fmt)
    assert function
    return function


@pytest.fixture(scope="module")
def fig():
    fig, ax = plt.subplots()
    ax.plot([-1, 1], [-1, 1])
    return fig


def test_pgf(fig: Figure):
    out = io.StringIO()
    rp = RepresentationPrinter(out)
    function = get_func("pgf")
    function(fig, rp, None)
    text = out.getvalue()
    assert text.startswith("%% Creator: Matplotlib, PGF backend")
    assert text.endswith("\\endgroup%\n")


def test_pdf(fig: Figure):
    function = get_func("pdf")
    data = function(fig)
    assert isinstance(data, bytes)
    assert base64.b64encode(data).decode().startswith("JVBER")


def test_svg(fig: Figure):
    function = get_func("svg")
    xml = function(fig)
    assert isinstance(xml, str)
    assert xml.startswith('<?xml version="1.0"')


def test_set_formatter_pgf():
    from nbstore.formatter import matplotlib_figure_to_pgf, set_formatter

    ip = InteractiveShell()
    set_formatter("matplotlib", "pgf", ip)
    formatter = ip.display_formatter.formatters["text/plain"]  # type:ignore
    assert isinstance(formatter, PlainTextFormatter)
    func = formatter.lookup_by_type("matplotlib.figure.Figure")
    assert func is matplotlib_figure_to_pgf


def test_set_formatter_pdf():
    from nbstore.formatter import matplotlib_figure_to_pdf, set_formatter

    ip = InteractiveShell()
    set_formatter("matplotlib", "pdf", ip)
    formatter = ip.display_formatter.formatters["application/pdf"]  # type:ignore
    assert isinstance(formatter, PDFFormatter)
    func = formatter.lookup_by_type("matplotlib.figure.Figure")
    assert func is matplotlib_figure_to_pdf


def test_set_formatter_svg():
    from nbstore.formatter import matplotlib_figure_to_svg, set_formatter

    ip = InteractiveShell()
    set_formatter("matplotlib", "svg", ip)
    formatter = ip.display_formatter.formatters["image/svg+xml"]  # type:ignore
    assert isinstance(formatter, SVGFormatter)
    func = formatter.lookup_by_type("matplotlib.figure.Figure")
    assert func is matplotlib_figure_to_svg
