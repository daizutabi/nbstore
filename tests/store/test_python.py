from pathlib import Path

import pytest

from nbstore.notebook import Notebook

SOURCE = """\
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
def path(tmp_path_factory: pytest.TempPathFactory):
    path = tmp_path_factory.mktemp("test") / "test.py"
    path.write_text(SOURCE)
    return path


@pytest.fixture(scope="module")
def nb(path: Path):
    from nbstore.store import read_notebook_node

    return Notebook(read_notebook_node(path))


def test_len(nb: Notebook):
    assert len(nb.node["cells"]) == 7


def test_cell_0(nb: Notebook):
    assert nb.node.cells[0]["source"].startswith("def plot(x: int):\n    print(x)")
    assert nb.node.cells[4]["source"] == "#"


def test_cell_1(nb: Notebook):
    assert nb.get_source("plot-1") == "plot(1)"


def test_cell_2(nb: Notebook):
    assert nb.get_source("plot-2") == "\nplot(2)"


def test_cell_3(nb: Notebook):
    assert nb.get_source("plot-3") == "plot(3)"


def test_cell_4(nb: Notebook):
    assert nb.get_source("plot-4") == "\nplot(4)"


def test_cell_5(nb: Notebook):
    assert nb.get_source("plot-5") == "\nplot(5)"
