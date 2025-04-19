# Notebook Operations

nbstore provides comprehensive functions for working with Jupyter notebooks,
including cell access, output extraction, and notebook execution.

## Cell Access

Access specific cells in notebooks using unique identifiers:

```python
from nbstore.notebook import get_cell, get_source

# Get the entire cell
cell = get_cell(notebook, "plot")

# Get just the source code, optionally excluding the identifier line
source = get_source(notebook, "plot", include_identifier=False)
```

## Output Extraction

Extract and work with cell outputs in various formats:

```python
from nbstore.notebook import get_outputs, get_data, get_mime_content, get_stream

# Get all outputs from a cell
outputs = get_outputs(notebook, "plot")

# Get data outputs as a dictionary
data = get_data(notebook, "plot")

# Get content with MIME type information
mime_content = get_mime_content(notebook, "plot")

# Get stream output (stdout/stderr)
stream = get_stream(notebook, "plot")
```

## Notebook Creation

Create new notebooks and add cells:

```python
import nbformat
from nbstore.notebook import new_code_cell

# Create a new notebook
notebook = nbformat.v4.new_notebook()

# Add a cell with an identifier
cell = new_code_cell("plot", """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
""")

notebook["cells"].append(cell)
```

## Notebook Execution

Execute notebooks and capture outputs:

```python
from nbstore.notebook import execute

# Execute the notebook
executed_notebook, execution_info = execute(notebook)

# Now outputs are available
data = get_data(executed_notebook, "plot")
```

## Special Output Handling

nbstore has special handling for various output formats:

```python
# For Matplotlib PGF backend
# Base64-encoded images in outputs are automatically handled
mime_type, content = get_mime_content(notebook, "image_cell")
```

## Notebook Comparison

Compare notebooks to check for equality:

```python
from nbstore.notebook import equals

# Check if two notebooks have the same cells
if equals(notebook1, notebook2):
    print("Notebooks are identical")
```
