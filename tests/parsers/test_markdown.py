import pytest


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", []),
        ("'", ["'"]),
        ("''", ["''"]),
        ('"', ['"']),
        ('""', ['""']),
        (" ", []),
        ("   ", []),
        ("=", ["="]),
        (" =", ["="]),
        ("= ", ["="]),
        ("abc", ["abc"]),
        ("αβ γδ", ["αβ", "γδ"]),
        (" a  b  c ", ["a", "b", "c"]),
        ('"a b c"', ['"a b c"']),
        ("'a b c'", ["'a b c'"]),
        ("a 'b c' d", ["a", "'b c'", "d"]),
        ('a "b c" d', ["a", '"b c"', "d"]),
        (r"a 'b \'c\' d' e", ["a", r"'b \'c\' d'", "e"]),
        ("a=b", ["a=b"]),
        ("a = b", ["a=b"]),
        ("a = b c = d", ["a=b", "c=d"]),
        ("a = b c =", ["a=b", "c", "="]),
        ("a='b c' d = 'e f'", ["a='b c'", "d='e f'"]),
    ],
)
def test_split(text, expected):
    from nbstore.parsers.markdown import split

    assert list(split(text)) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("a", "a"),
        ("a b", '"a b"'),
        ("a b c", '"a b c"'),
    ],
)
def test_quote(value, expected):
    from nbstore.parsers.markdown import _quote

    assert _quote(value) == expected


def test_quote_single():
    from nbstore.parsers.markdown import _quote

    assert _quote('a "b" c') == "'a {} c'".format('"b"')


SOURCE = """\
![a](b.ipynb){ #c .s k=v}

abc ``![a](b){c}``

```python
![a](b){c}
```

``` {.text #id a = 'b c'}
xyz
```

```nobody
```

```
noattr
```
"""


@pytest.fixture(scope="module")
def elements():
    from nbstore.parsers.markdown import iter_elements

    return list(iter_elements(SOURCE))


def test_elements_image(elements):
    from nbstore.parsers.markdown import Image

    x = elements[0]
    assert isinstance(x, Image)
    assert x.alt == "a"
    assert x.url == "b.ipynb"
    assert x.identifier == "c"
    assert x.classes == [".s"]
    assert x.attributes == {"k": "v"}


def test_elements_inline_code(elements):
    from nbstore.parsers.markdown import InlineCode

    x = elements[2]
    assert isinstance(x, InlineCode)
    assert x.code == "![a](b){c}"


def test_elements_code_block(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[4]
    assert isinstance(x, CodeBlock)
    assert x.code == "![a](b){c}"
    assert x.identifier == ""
    assert x.classes == ["python"]
    assert x.attributes == {}


def test_elements_code_block_with_attributes(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[6]
    assert isinstance(x, CodeBlock)
    assert x.code == "xyz"
    assert x.identifier == "id"
    assert x.classes == [".text"]
    assert x.attributes == {"a": "b c"}


def test_elements_code_block_without_body(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[8]
    assert isinstance(x, CodeBlock)
    assert x.code == ""
    assert x.identifier == ""
    assert x.classes == ["nobody"]
    assert x.attributes == {}


def test_elements_code_block_without_attributes(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[10]
    assert isinstance(x, CodeBlock)
    assert x.code == "noattr"
    assert x.identifier == ""
    assert x.classes == []
    assert x.attributes == {}


@pytest.mark.parametrize(
    ("index", "expected"),
    [(1, "\n\nabc `"), (3, "`\n\n"), (5, "\n\n")],
)
def test_elements_str(elements, index, expected):
    x = elements[index]
    assert isinstance(x, str)
    assert x == expected


def test_join(elements):
    x = [x if isinstance(x, str) else x.text for x in elements]
    assert "".join(x) == SOURCE


def test_iter_parts():
    from nbstore.parsers.markdown import Element

    x = Element("", "id", ["a", "b"], {"k": "v"})
    assert list(x.iter_parts()) == ["a", "b", "k=v"]
    assert list(x.iter_parts(include_identifier=True)) == ["#id", "a", "b", "k=v"]
