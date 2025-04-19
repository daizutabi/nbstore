# Features

nbstore provides a powerful set of features for working with Jupyter notebooks,
Python scripts, and Markdown files.

## Markdown to Notebook Conversion

Convert Markdown files to Jupyter notebooks with support for custom syntax and
attributes. Use code blocks with language specification and identifiers to create
notebook cells.

```python
# Example: Converting Markdown to a notebook
from pathlib import Path
from nbstore.markdown import new_notebook

# Read the Markdown file
text = Path("document.md").read_text()

notebook = new_notebook(text)
```

## Cell Identification and Access

Access specific cells in notebooks using unique identifiers, supporting both
source code extraction and output retrieval.

```python
# Example: Accessing a cell by ID
from nbstore.notebook import get_source, get_data

# Get source code from cell with ID "plot"
source = get_source(notebook, "plot")

# Get output data from the same cell
data = get_data(notebook, "plot")
```

## Inline Code Execution

Execute Python code within image notation, making it easy to generate and include
dynamic visualizations.
