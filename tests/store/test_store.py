import pytest

from nbstore.store import Store


def test_get_data_none(store: Store):
    with pytest.raises(ValueError, match="No output data"):
        store.get_data("pgf.ipynb", "fig:none")


def test_add_data(store: Store):
    from nbstore.store import get_data_by_type

    url = "add.ipynb"
    identifier = "fig:add"
    mime = "mime"
    data = "data"

    assert mime not in store.get_data(url, identifier)

    store.add_data(url, identifier, mime, data)

    assert mime in store.get_data(url, identifier)
    store.save_notebook(url)

    assert mime in store.get_data(url, identifier)

    outputs = store.get_outputs(url, identifier)
    output = get_data_by_type(outputs, "display_data")
    assert output
    del output[mime]

    store.save_notebook(url)

    assert mime not in store.get_data(url, identifier)


def test_get_language(store: Store):
    assert store.get_language("add.ipynb") == "python"
