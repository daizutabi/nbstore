import pytest

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
    from nbstore.parsers.python import _iter_main_blocks

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
def cells(text):
    from nbstore.parsers.python import iter_cells

    return list(iter_cells(text))


def test_cells(cells: list[str]):
    assert len(cells) == 6


def test_cells_0(cells: list[str]):
    assert cells[0] == "\ndef plot(x: int):\n    print(x)\n"


def test_cells_1(cells: list[str]):
    assert cells[1] == "# %% #plot-1\nplot(1)\n"


def test_cells_2(cells: list[str]):
    assert cells[2] == "# %% #plot-2\n\nplot(2)\n"


def test_cells_3(cells: list[str]):
    assert cells[3] == "#"


def test_cells_4(cells: list[str]):
    assert cells[4] == "# %% #plot-3\n\nplot(3)\n"


def test_cells_5(cells: list[str]):
    assert cells[5] == "# %% #plot-4\n\nplot(4)\n\n"
