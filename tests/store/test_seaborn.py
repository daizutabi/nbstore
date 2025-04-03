import pytest

from nbstore.store import Store


@pytest.fixture(scope="module", autouse=True)
def _execute(store: Store):
    return store.execute("seaborn.ipynb")


def test_outputs(store: Store):
    outputs = store.get_outputs("seaborn.ipynb", "fig:seaborn")
    assert isinstance(outputs, list)
    assert len(outputs) == 1
    assert isinstance(outputs[0], dict)
    assert outputs[0]["output_type"] == "execute_result"
    assert "text/plain" in outputs[0]["data"]


def test_data(store: Store):
    data = store.get_data("seaborn.ipynb", "fig:seaborn")
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "text/plain" in data
    assert "image/png" in data
    assert data["text/plain"].startswith("%% Creator: Matplotlib,")
