# nbstore

nbstore is a library for creating, manipulating, and integrating Jupyter notebooks
with Markdown documentation. It serves as the foundation for the MkDocs plugin
[nbsync](https://daizutabi.github.io/nbsync/).

## What is nbstore?

nbstore bridges the gap between Jupyter notebooks, Python scripts, and Markdown
documentation. It solves common challenges that data scientists, researchers, and
technical writers face when working with notebooks:

- **Development happens in notebooks** - ideal for experimentation and visualization
- **Documentation lives in markdown** - perfect for narrative and explanation
- **Traditional integration is challenging** - screenshots break, exports get outdated

With nbstore, you can:

- Generate notebooks from Python scripts and Markdown files
- Extract and manipulate content from notebook cells
- Execute code embedded in image notations

## Key Features

### Notebooks from Python and Markdown

Create Jupyter notebooks directly from Python scripts and Markdown files with
special syntax for code blocks and cell identification.

### Cell Identification

Access notebook cells using `#id` comments, allowing you to get source code or
output results from specific cells.

### Inline Code in Images

Write executable code within image notation, enabling dynamic visualization
placement.

### Notebook Cell Addition

Add new cells to notebooks programmatically.

### Notebook Execution

Execute notebooks and capture their outputs.

## Installation

```bash
pip install nbstore
```
