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
        ("`a b c`", ["`a b c`"]),
        ("a 'b c' d", ["a", "'b c'", "d"]),
        ("a `b c` d", ["a", "`b c`", "d"]),
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

abc `![a](b){c}`

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


def test_elements_code_block(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[2]
    assert isinstance(x, CodeBlock)
    assert x.code == "![a](b){c}"
    assert x.identifier == ""
    assert x.classes == ["python"]
    assert x.attributes == {}


def test_elements_code_block_with_attributes(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[4]
    assert isinstance(x, CodeBlock)
    assert x.code == "xyz"
    assert x.identifier == "id"
    assert x.classes == [".text"]
    assert x.attributes == {"a": "b c"}


def test_elements_code_block_without_body(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[6]
    assert isinstance(x, CodeBlock)
    assert x.code == ""
    assert x.identifier == ""
    assert x.classes == ["nobody"]
    assert x.attributes == {}


def test_elements_code_block_without_attributes(elements):
    from nbstore.parsers.markdown import CodeBlock

    x = elements[8]
    assert isinstance(x, CodeBlock)
    assert x.code == "noattr"
    assert x.identifier == ""
    assert x.classes == []
    assert x.attributes == {}


@pytest.mark.parametrize(
    ("index", "expected"),
    [(1, "\n\nabc `![a](b){c}`\n\n"), (3, "\n\n"), (5, "\n\n")],
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


@pytest.mark.parametrize(
    ("markdown", "expected"),
    [
        ("```python {a #id1 b}\nprint(1)\n```", (["python", "a", "b"], "id1")),
        ("```{.python #id2 b}\nprint(2)\n```", ([".python", "b"], "id2")),
        ("```{python #id3 {a} }\nprint(3)\n```", (["python", "{a}"], "id3")),
        ("```bash {#id4}\necho hello\n```", (["bash"], "id4")),
        ("```python\nprint(4)\n```", (["python"], "")),
        ('```{python #id3 "{a}" }\np\n```', (["python", '"{a}"'], "id3")),
    ],
)
def test_markdown_code_blocks(markdown, expected):
    from nbstore.parsers.markdown import CodeBlock, iter_elements

    x = next(iter_elements(markdown))
    assert isinstance(x, CodeBlock)
    assert x.classes == expected[0]
    assert x.identifier == expected[1]


def test_code_block_url():
    from nbstore.parsers.markdown import CodeBlock, iter_elements

    x = next(iter_elements("```python a.ipynb#id c\nprint(1)\n```\n"))
    assert isinstance(x, CodeBlock)
    assert x.code == "print(1)"
    assert x.url == "a.ipynb"
    assert x.identifier == "id"
    assert x.classes == ["python", "c"]


def test_image_code():
    from nbstore.parsers.markdown import Image, iter_elements

    x = next(iter_elements("![alt](a.ipynb){#id `co de` b}"))
    assert isinstance(x, Image)
    assert x.code == "co de"
    assert x.url == "a.ipynb"
    assert x.identifier == "id"
    assert x.classes == ["b"]


SOURCE_LANG = """\

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

![alt](.md){#plot-1}

"""


def test_get_language():
    from nbstore.parsers.markdown import get_language

    assert get_language(SOURCE_LANG) == "python"


def test_get_language_none():
    from nbstore.parsers.markdown import get_language

    assert get_language("") is None


SOURCE_LANG_2 = """\

![alt](.md){#plot-1}

```python #_
println("hello")
```

```julia #plot-1
plot(1)
```
"""


def test_get_language_2():
    from nbstore.parsers.markdown import get_language

    assert get_language(SOURCE_LANG_2) == "julia"


SOURCE_LANG_URL = """\
![alt](a.ipynb){#_}
![alt](){#id1}
![alt](b.ipynb){#id2}
![alt](){#id3}
"""


def test_iter_elements_url():
    from nbstore.parsers.markdown import iter_elements

    images = list(iter_elements(SOURCE_LANG_URL))[1::2]
    assert len(images) == 3
    assert images[0].url == "a.ipynb"  # type: ignore
    assert images[1].url == "b.ipynb"  # type: ignore
    assert images[2].url == "b.ipynb"  # type: ignore
