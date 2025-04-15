from pathlib import Path

import pytest

from nbstore.notebook import Notebook

SOURCE = """\
import matplotlib.pyplot as plt

def plot(x):
    plt.plot([x])

# %% #plot-1
plot(1)

if __name__ == "__main__":
    # %% #plot-2

    plot(2)
"""


@pytest.fixture(scope="module")
def path(tmp_path_factory: pytest.TempPathFactory):
    path = tmp_path_factory.mktemp("test") / "test.py"
    path.write_text(SOURCE)
    return path


@pytest.fixture(scope="module")
def nb(path: Path):
    return Notebook(path)


def test_source_1(nb: Notebook):
    assert nb.get_source("plot-1") == "plot(1)"


def test_source_2(nb: Notebook):
    assert nb.get_source("plot-2") == "\nplot(2)"


def test_language(nb: Notebook):
    assert nb.get_language() == "python"
    nb.execute()
    assert nb.get_language() == "python"
