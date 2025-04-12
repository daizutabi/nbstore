import base64

import pytest

from nbstore.notebook import Notebook
from nbstore.store import Store


@pytest.fixture(scope="module", params=["holoviews", "hvplot"])
def lib(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture(scope="module")
def nb(store: Store, lib: str):
    nb = store.get_notebook(f"{lib}.ipynb")
    assert not nb.is_executed
    nb.execute()
    assert nb.is_executed
    return nb


@pytest.fixture(scope="module")
def data(nb: Notebook, lib: str):
    return nb.get_data(f"fig:{lib}")


def test_type(data: dict):
    assert isinstance(data, dict)


def test_len(data: dict):
    assert len(data) == 3


@pytest.mark.parametrize("mime", ["text/html", "text/pgf", "text/plain"])
def test_mime(data: dict, mime):
    assert mime in data


def test_data_decode(data: dict):
    text = data["text/pgf"]
    assert isinstance(text, str)
    text = base64.b64decode(text).decode(encoding="utf-8")
    assert text.startswith("%% Creator: Matplotlib,")
