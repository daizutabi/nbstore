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
    store.delete_data(url, identifier, mime)
    store.save_notebook(url)

    assert mime not in store.get_data(url, identifier)


def test_get_language(store: Store):
    assert store.get_language("add.ipynb") == "python"


def test_get_cell_error(store: Store):
    with pytest.raises(ValueError, match="Unknown identifier: fig:invalid"):
        store.get_data("pgf.ipynb", "fig:invalid")


def test_current_path(store: Store):
    a = store.get_source("pgf.ipynb", "fig:stream")
    b = store.get_source("", "fig:stream")
    assert a == b


def test_abs_path_error(store: Store):
    with pytest.raises(ValueError, match="Unknown path."):
        store.get_source("unknown.ipynb", "fig:stream")


def test_stream_none():
    from nbstore.store import get_stream

    assert get_stream([]) is None
