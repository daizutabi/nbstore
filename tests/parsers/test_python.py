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
def sources(text):
    from nbstore.parsers.python import iter_sources

    return list(iter_sources(text))


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
