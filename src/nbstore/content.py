from __future__ import annotations

import atexit
import base64
from pathlib import Path


def get_mime_content(data: dict[str, str]) -> tuple[str, str | bytes] | None:
    """Get the content of a notebook cell.

    Args:
        data (dict[str, str]): The data of a notebook cell.

    Returns:
        tuple[str, str | bytes] | None: A tuple of the mime type and the content.
    """
    if text := data.get("text/html"):
        return "text/html", text

    if text := data.get("application/pdf"):
        return "application/pdf", base64.b64decode(text)

    for mime, text in data.items():
        if mime.startswith("image/"):
            return mime, base64.b64decode(text)

    return None


def get_suffix(mime: str) -> str:
    """Get the suffix of a mime type.

    Args:
        mime (str): The mime type.

    Returns:
        str: The suffix of the mime type.
    """
    return "." + mime.split("/")[1]


def create_image_file(
    data: dict[str, str],
    filename: Path | str,
    *,
    delete: bool = False,
) -> Path | None:
    """Create an image file from the data of a notebook cell.

    Args:
        data (dict[str, str]): The data of a notebook cell.
        filename (Path | str): The filename of the image file.
        delete (bool): Whether to delete the image file when the program exits.

    Returns:
        Path | None: The path to the image file.
    """
    decoded = get_mime_content(data)

    if decoded is None:
        return None

    mime, content = decoded
    suffix = get_suffix(mime)
    file = Path(filename).with_suffix(suffix)

    if isinstance(content, str):
        file.write_text(content)
    else:
        file.write_bytes(content)

    if delete:
        atexit.register(lambda: file.unlink(missing_ok=True))

    return file
