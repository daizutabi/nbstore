from pathlib import Path

import nbformat
import pytest

from nbstore.notebook import Notebook

SOURCE = """\

```python #_
import matplotlib.pyplot as plt

def plot(x):
    plt.plot([x])
```

```julia #_
println("hello")
```

```python #plot-1
plot(1)
```

```{.python #plot-2}
plot(2)
```

```python
plot(3)
```

![alt](.md){#plot-2}

"""


@pytest.fixture(scope="module")
def path(tmp_path_factory: pytest.TempPathFactory):
    path = tmp_path_factory.mktemp("test") / "test.md"
    path.write_text(SOURCE)
    return path


@pytest.fixture(scope="module")
def nb(path: Path):
    from nbstore.store import create_notebook_node

    node = create_notebook_node(path)
    return Notebook(node)


@pytest.fixture(scope="module")
def test_len(nb: Notebook):
    assert len(nb.node["cells"]) == 4


def test_source_1(nb: Notebook):
    assert nb.get_source("plot-1") == "plot(1)"


def test_source_2(nb: Notebook):
    assert nb.get_source("plot-2") == "plot(2)"


def test_language(nb: Notebook):
    assert nb.get_language() == "python"
    nb.execute()
    assert nb.get_language() == "python"


def test_language_default():
    from nbstore.notebook import get_language

    nb = nbformat.v4.new_notebook()
    assert get_language(nb, "julia") == "julia"
