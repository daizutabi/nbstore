import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module")
def nb(store: Store):
    nb = store.get_notebook("seaborn.ipynb")
    assert not nb.is_executed
    nb.execute()
    assert nb.is_executed
    return nb


def test_outputs(nb: Notebook):
    outputs = nb.get_outputs("fig:seaborn")
    assert isinstance(outputs, list)
    assert len(outputs) == 1
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]


def test_data(nb: Notebook):
    data = nb.get_data("fig:seaborn")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["text/plain"].startswith("%% Creator: Matplotlib,")
