import nbformat
import pytest
from nbformat import NotebookNode


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
    from nbstore.markdown import split

    assert list(split(text)) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("a", '"a"'),
        ("a b", '"a b"'),
        ("a b c", '"a b c"'),
    ],
)
def test_quote(value, expected):
    from nbstore.markdown import _quote

    assert _quote(value) == expected


def test_quote_single():
    from nbstore.markdown import _quote

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
    from nbstore.markdown import parse

    return list(parse(SOURCE))


def test_elements_image(elements):
    from nbstore.markdown import Image

    x = elements[0]
    assert isinstance(x, Image)
    assert x.alt == "a"
    assert x.url == "b.ipynb"
    assert x.identifier == "c"
    assert x.classes == [".s"]
    assert x.attributes == {"k": "v"}


def test_elements_code_block(elements):
    from nbstore.markdown import CodeBlock

    x = elements[2]
    assert isinstance(x, CodeBlock)
    assert x.source == "![a](b){c}"
    assert x.identifier == ""
    assert x.classes == ["python"]
    assert x.attributes == {}


def test_elements_code_block_with_attributes(elements):
    from nbstore.markdown import CodeBlock

    x = elements[4]
    assert isinstance(x, CodeBlock)
    assert x.source == "xyz"
    assert x.identifier == "id"
    assert x.classes == [".text"]
    assert x.attributes == {"a": "b c"}


def test_elements_code_block_without_body(elements):
    from nbstore.markdown import CodeBlock

    x = elements[6]
    assert isinstance(x, CodeBlock)
    assert x.source == ""
    assert x.identifier == ""
    assert x.classes == ["nobody"]
    assert x.attributes == {}


def test_elements_code_block_without_attributes(elements):
    from nbstore.markdown import CodeBlock

    x = elements[8]
    assert isinstance(x, CodeBlock)
    assert x.source == "noattr"
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
    from nbstore.markdown import Element

    x = Element("", "id", ["a", "b"], {"k": "v"})
    assert list(x.iter_parts()) == ["a", "b", 'k="v"']
    assert list(x.iter_parts(include_identifier=True)) == ["#id", "a", "b", 'k="v"']


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
    from nbstore.markdown import CodeBlock, parse

    x = next(parse(markdown))
    assert isinstance(x, CodeBlock)
    assert x.classes == expected[0]
    assert x.identifier == expected[1]


def test_code_block_url():
    from nbstore.markdown import CodeBlock, parse

    x = next(parse("```python a.ipynb#id c\nprint(1)\n```\n"))
    assert isinstance(x, CodeBlock)
    assert x.source == "print(1)"
    assert x.url == "a.ipynb"
    assert x.identifier == "id"
    assert x.classes == ["python", "c"]


def test_image_code():
    from nbstore.markdown import Image, parse

    x = next(parse("![alt](a.ipynb){#id `co de` b}"))
    assert isinstance(x, Image)
    assert x.source == "co de"
    assert x.url == "a.ipynb"
    assert x.identifier == "id"
    assert x.classes == ["b"]


def test_image_code_eq():
    from nbstore.markdown import Image, parse

    x = next(parse("![alt](a.ipynb){#id `a=1;b=2` b}"))
    assert isinstance(x, Image)
    assert x.source == "a=1;b=2"
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
    from nbstore.markdown import get_language

    assert get_language(SOURCE_LANG) == "python"


def test_get_language_none():
    from nbstore.markdown import get_language

    assert get_language("") == ""


SOURCE_LANG_AFTER = """\

![alt](.md){#plot-1}

```python #_
println("hello")
```

```julia #plot-1
plot(1)
```
"""


def test_get_language_after():
    from nbstore.markdown import get_language

    assert get_language(SOURCE_LANG_AFTER) == "julia"


@pytest.mark.parametrize(
    ("language", "expected"),
    [("julia", True), ("python", False), (".julia", True), (".python", False)],
)
def test_is_target_code_block(language, expected):
    from nbstore.markdown import CodeBlock, is_target_code_block

    code = CodeBlock("", "id", [language], {})
    assert is_target_code_block(code, "julia") == expected


def test_is_target_code_block_no_language():
    from nbstore.markdown import is_target_code_block

    assert not is_target_code_block("", "")


def test_is_target_code_block_str():
    from nbstore.markdown import is_target_code_block

    assert not is_target_code_block("python", "python")


def test_is_target_code_block_no_identifier():
    from nbstore.markdown import CodeBlock, is_target_code_block

    code = CodeBlock("", "", [], {})
    assert not is_target_code_block(code, "python")


SOURCE_NOTEBOOK = """\

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
def nb():
    from nbstore.markdown import new_notebook

    return new_notebook(SOURCE_NOTEBOOK)


@pytest.fixture(scope="module")
def test_len(nb: NotebookNode):
    assert len(nb["cells"]) == 4


def test_source_1(nb: NotebookNode):
    from nbstore.notebook import get_source

    assert get_source(nb, "plot-1") == "plot(1)"


def test_source_2(nb: NotebookNode):
    from nbstore.notebook import get_source

    assert get_source(nb, "plot-2") == "plot(2)"


def test_language_default():
    from nbstore.notebook import get_language

    nb = nbformat.v4.new_notebook()
    assert get_language(nb, "julia") == "julia"


def test_language_error():
    from nbstore.markdown import new_notebook

    with pytest.raises(ValueError, match="language not found"):
        new_notebook("hello")


SOURCE_INDENT_IMAGE = """\
![alt](.md){#id-0}
 ![alt](.md){#id-1}

def fgi
    ![alt](.md){#id-4}
jkl
a ![alt](.md){#id-a} ![alt](.md){#id-b}
"""


def test_indent_image():
    from nbstore.markdown import Image, parse

    elems = [e for e in parse(SOURCE_INDENT_IMAGE) if isinstance(e, Image)]
    assert len(elems) == 5
    assert elems[0].indent == ""
    assert elems[1].indent == " "
    assert elems[1].text == " ![alt](.md){#id-1}"
    assert elems[2].indent == "    "
    assert elems[2].text == "    ![alt](.md){#id-4}"
    assert elems[3].indent == ""
    assert elems[3].text == "![alt](.md){#id-a}"
    assert elems[4].indent == ""
    assert elems[4].text == "![alt](.md){#id-b}"


def test_join_image():
    from nbstore.markdown import parse

    elems = parse(SOURCE_INDENT_IMAGE)
    x = [e if isinstance(e, str) else e.text for e in elems]
    assert "".join(x) == SOURCE_INDENT_IMAGE


SOURCE_INDENT_CODE_BLOCK = """\
```python
a
  b
```
a

    ```python
    a
      b
    ```
    d
"""


def test_indent_code_block():
    from nbstore.markdown import CodeBlock, parse

    elems = [e for e in parse(SOURCE_INDENT_CODE_BLOCK) if isinstance(e, CodeBlock)]
    assert len(elems) == 2
    assert elems[0].indent == ""
    assert elems[0].source == "a\n  b"
    assert elems[0].text.startswith("```python")
    assert elems[1].indent == "    "
    assert elems[1].source == "a\n  b"
    assert elems[1].text.startswith("    ```python")


def test_join_code_block():
    from nbstore.markdown import parse

    elems = parse(SOURCE_INDENT_CODE_BLOCK)
    x = [e if isinstance(e, str) else e.text for e in elems]
    assert "".join(x) == SOURCE_INDENT_CODE_BLOCK


def test_comment():
    from nbstore.markdown import parse

    text = "<!-- ![alt](a.py){#id} -->"
    assert next(parse(text)) == text
