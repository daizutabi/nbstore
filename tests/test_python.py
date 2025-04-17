import pytest
from nbformat import NotebookNode

SOURCE = """\

def plot(x: int):
    print(x)

# %% #plot-1
plot(1)

if __name__ == "__main__":
    # %% #plot-2

    plot(2)

if __name__ == "__main__":
    #
    # %% #plot-3

    plot(3)

# %% #plot-4

plot(4)

"""


@pytest.fixture
def text():
    return SOURCE


@pytest.fixture
def blocks(text):
    from nbstore.python import _iter_main_blocks

    return list(_iter_main_blocks(text))


def test_blocks_0(blocks: list[str]):
    assert blocks[0].startswith("\ndef plot")
    assert blocks[0].endswith("plot(1)\n")


def test_blocks_1(blocks: list[str]):
    assert blocks[1].startswith("# %% #plot-2")
    assert blocks[1].endswith("plot(2)\n")


def test_blocks_2(blocks: list[str]):
    assert blocks[2].startswith("#\n# %% #plot-3")
    assert blocks[2].endswith("plot(3)\n")


def test_blocks_3(blocks: list[str]):
    assert blocks[3].startswith("# %% #plot-4")
    assert blocks[3].endswith("plot(4)\n\n")


@pytest.fixture
def sources(text):
    from nbstore.python import parse

    return list(parse(text))


def test_sources(sources: list[str]):
    assert len(sources) == 6


def test_sources_0(sources: list[str]):
    assert sources[0] == "\ndef plot(x: int):\n    print(x)"


def test_sources_1(sources: list[str]):
    assert sources[1] == "# %% #plot-1\nplot(1)"


def test_sources_2(sources: list[str]):
    assert sources[2] == "# %% #plot-2\n\nplot(2)"


def test_sources_3(sources: list[str]):
    assert sources[3] == "#"


def test_sources_4(sources: list[str]):
    assert sources[4] == "# %% #plot-3\n\nplot(3)"


def test_sources_5(sources: list[str]):
    assert sources[5] == "# %% #plot-4\n\nplot(4)"


SOURCE_NOTEBOOK = """\
def plot(x: int):
    print(x)  # noqa: T201


# %% #plot-1
plot(1)

if __name__ == "__main__":
    # %% #plot-2

    plot(2)

# %% #plot-3
plot(3)

if __name__ == "__main__":
    #
    # %% #plot-4

    plot(4)

# %% #plot-5

plot(5)
"""


@pytest.fixture(scope="module")
def nb():
    from nbstore.python import new_notebook

    return new_notebook(SOURCE_NOTEBOOK)


def test_len(nb: NotebookNode):
    assert len(nb["cells"]) == 7


def test_cell_0(nb: NotebookNode):
    assert nb.cells[0]["source"].startswith("def plot(x: int):\n    print(x)")
    assert nb.cells[4]["source"] == "#"


def test_cell_1(nb: NotebookNode):
    from nbstore.notebook import get_source

    assert get_source(nb, "plot-1") == "plot(1)"


def test_cell_2(nb: NotebookNode):
    from nbstore.notebook import get_source

    assert get_source(nb, "plot-2") == "\nplot(2)"


def test_cell_3(nb: NotebookNode):
    from nbstore.notebook import get_source

    assert get_source(nb, "plot-3") == "plot(3)"


def test_cell_4(nb: NotebookNode):
    from nbstore.notebook import get_source

    assert get_source(nb, "plot-4") == "\nplot(4)"


def test_cell_5(nb: NotebookNode):
    from nbstore.notebook import get_source

    assert get_source(nb, "plot-5") == "\nplot(5)"
