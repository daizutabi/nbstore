def test_get_mime_content():
    from nbstore.content import get_mime_content

    assert get_mime_content({}) is None
