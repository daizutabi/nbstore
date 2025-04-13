from nbstore.store import Store


def test_split(store: Store):
    path = store.find_path("plot.py")
    print(path)
    assert path is not None
