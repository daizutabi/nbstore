"""Extract and manipulate content from Jupyter notebooks.

nbstore provides tools for reading, processing, and storing notebook content,
with support for multiple formats including .ipynb, .py, and .md files.
It facilitates extraction of specific cells, data conversion, and
formatting of visualization outputs.

Main components:
- Store: Main interface for reading and managing notebook files
- Formatter: Controls output format for visualization libraries
- Content parsing for Python and Markdown files
"""

from .formatter import set_formatter
from .store import Store, read

__all__ = ["Store", "read", "set_formatter"]
