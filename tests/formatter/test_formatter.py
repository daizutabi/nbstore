from nbstore.formatter import set_formatter


def test_set_formatter_without_ipython():
    set_formatter("matplotlib", "svg")
