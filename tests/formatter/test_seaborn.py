import base64
import io

import pytest
import seaborn.objects as so
from IPython.core.formatters import PDFFormatter, PlainTextFormatter, SVGFormatter
from IPython.core.interactiveshell import InteractiveShell
from IPython.lib.pretty import RepresentationPrinter
from seaborn.objects import Plot

from nbstore.formatter import FUNCTIONS


def get_func(fmt: str):
    functions = FUNCTIONS.get(("seaborn._core.plot", "Plot"))
    assert functions
    function = functions.get(fmt)
    assert function
    return function


@pytest.fixture(scope="module")
def plot():
    return so.Plot()


def test_pgf(plot: Plot):
    out = io.StringIO()
    rp = RepresentationPrinter(out)
    function = get_func("pgf")
    function(plot, rp, None)
    text = out.getvalue()
    assert text.startswith("%% Creator: Matplotlib, PGF backend")
    assert text.endswith("\\endgroup%\n")


def test_pdf(plot: Plot):
    function = get_func("pdf")
    data = function(plot)
    assert isinstance(data, bytes)
    assert base64.b64encode(data).decode().startswith("JVBER")


def test_svg(plot: Plot):
    function = get_func("svg")
    xml = function(plot)
    assert isinstance(xml, str)
    assert xml.startswith('<?xml version="1.0"')


def test_set_formatter_pgf():
    from nbstore.formatter import seaborn_plot_to_pgf, set_formatter

    ip = InteractiveShell()
    set_formatter("seaborn", "pgf", ip)
    formatter = ip.display_formatter.formatters["text/plain"]  # type:ignore
    assert isinstance(formatter, PlainTextFormatter)
    func = formatter.lookup_by_type("seaborn._core.plot.Plot")
    assert func is seaborn_plot_to_pgf


def test_set_formatter_pdf():
    from nbstore.formatter import seaborn_plot_to_pdf, set_formatter

    ip = InteractiveShell()
    set_formatter("seaborn", "pdf", ip)
    formatter = ip.display_formatter.formatters["application/pdf"]  # type:ignore
    assert isinstance(formatter, PDFFormatter)
    func = formatter.lookup_by_type("seaborn._core.plot.Plot")
    assert func is seaborn_plot_to_pdf


def test_set_formatter_svg():
    from nbstore.formatter import seaborn_plot_to_svg, set_formatter

    ip = InteractiveShell()
    set_formatter("seaborn", "svg", ip)
    formatter = ip.display_formatter.formatters["image/svg+xml"]  # type:ignore
    assert isinstance(formatter, SVGFormatter)
    func = formatter.lookup_by_type("seaborn._core.plot.Plot")
    assert func is seaborn_plot_to_svg
