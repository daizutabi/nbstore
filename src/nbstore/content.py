from __future__ import annotations

import base64


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
