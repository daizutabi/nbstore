from pathlib import Path

import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store

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
    return Notebook(path)


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


def test_error():
    from nbstore.notebook import create_notebook_node_markdown

    with pytest.raises(ValueError, match="language not found"):
        create_notebook_node_markdown("")


@pytest.fixture
def nb_add(store: Store):
    yield store.get_notebook("add.ipynb")
    store.clear()


def test_from_store_without_source(nb_add: Notebook, store: Store):
    nb = store.get_notebook("add.ipynb")
    assert nb is nb_add


def test_extend(nb_add: Notebook):
    source = '```python #from_markdown\nprint("hello")\n```'
    assert len(nb_add.node["cells"]) == 3
    nb_add.extend(source)
    assert len(nb_add.node["cells"]) == 4


def test_extend_from_store(nb_add: Notebook, store: Store):
    source = '```python #from_markdown\nprint("hello")\n```'
    nb = store.get_notebook("add.ipynb", source)
    assert not nb.equals(nb_add)
    nb2 = store.get_notebook("add.ipynb", source)
    assert nb2.equals(nb)
