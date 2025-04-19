# Markdown Processing

nbstore includes a robust Markdown parser with support for code blocks, images,
and custom attributes for identifying and styling elements.

## Code Blocks

Code blocks in Markdown can be converted to notebook cells by adding an identifier
and language specification.

````markdown
```python .md#plot
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title("Sine Function")
```
````

The `.md#plot` identifier can later be used to access this particular cell or its
outputs.

## Images with Source

nbstore extends the standard Markdown image syntax to support inline code and
attributes:

```markdown
![Plot result](.md){#plot source="on"}
```

Or with inline code:

```markdown
![Plot result](){`plt.plot(x, np.sin(x))`}
```

## Parsing Example

```python
from pathlib import Path
from nbstore.markdown import parse, CodeBlock

# Parse a Markdown file
text = Path("document.md").read_text()

# Iterate through parsed elements
for element in parse(text):
    if isinstance(element, CodeBlock) and element.identifier:
        print(f"Found code block with ID: {element.identifier}")
        print(f"Language: {element.classes[0] if element.classes else 'none'}")
        print(f"Source: {element.source}")
```
