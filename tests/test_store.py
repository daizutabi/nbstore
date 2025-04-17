from pathlib import Path

import nbformat
import pytest

from nbstore.store import Store

SOURCE = """\
# #fig
import matplotlib.pyplot as plt
plt.plot([1, 10, 100], [-1, 0, 1])
"""


@pytest.fixture(scope="module")
def store(tmp_path_factory: pytest.TempPathFactory):
    src_dir = tmp_path_factory.mktemp("test")
    nb = nbformat.v4.new_notebook()
    nb["cells"] = [nbformat.v4.new_code_cell(SOURCE)]
    nbformat.write(nb, src_dir / "a.ipynb")
    return Store(src_dir)


def test_find_path(store: Store):
    path = store.find_path("a.ipynb")
    assert path.name == "a.ipynb"
    path = store.find_path(path.absolute().as_posix())
    assert path.name == "a.ipynb"


def test_find_path_error(store: Store):
    with pytest.raises(ValueError, match="Source file not found"):
        store.find_path("unknown")


def test_read(store: Store):
    from nbstore.notebook import get_source

    nb = store.read("a.ipynb")
    assert get_source(nb, "fig").startswith("import matplotlib.pyplot as plt")
    nb = store.read("")
    assert get_source(nb, "fig").startswith("import matplotlib.pyplot as plt")
    assert store.url == "a.ipynb"


def test_write(store: Store):
    from nbstore.notebook import get_source

    nb = store.read("a.ipynb")
    nb["cells"].append(nbformat.v4.new_code_cell("# #test\n123"))
    store.write("a.ipynb", nb)
    nb = store.read("a.ipynb")
    assert get_source(nb, "test") == "123"


def test_read_python(tmp_path: Path):
    from nbstore.notebook import get_source
    from nbstore.store import read

    path = tmp_path / "test.py"
    path.write_text("# %% #id1\nprint(1)\n# %% #id2\nprint(2)")
    nb = read(path)
    assert get_source(nb, "id1") == "print(1)"
    assert get_source(nb, "id2") == "print(2)"


def test_read_markdown(tmp_path: Path):
    from nbstore.notebook import get_language, get_source
    from nbstore.store import read

    path = tmp_path / "test.md"
    path.write_text("```julia #id1\nprintln(1)\n```\n")
    nb = read(path)
    assert get_language(nb) == "julia"
    assert get_source(nb, "id1") == "println(1)"
