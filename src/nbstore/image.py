from __future__ import annotations

import atexit
import base64
from pathlib import Path


def get_content(data: dict[str, str]) -> tuple[str | bytes, str] | None:
    if text := data.get("application/pdf"):
        return base64.b64decode(text), ".pdf"

    for mime, text in data.items():
        if mime.startswith("image/"):
            ext = mime.split("/")[1]
            return base64.b64decode(text), f".{ext}"

    return None


def create_image_file(
    data: dict[str, str],
    filename: Path | str,
    *,
    delete: bool = False,
) -> Path | None:
    decoded = get_content(data)

    if decoded is None:
        return None

    content, suffix = decoded
    file = Path(filename).with_suffix(suffix)

    if isinstance(content, str):
        file.write_text(content)
    else:
        file.write_bytes(content)

    if delete:
        atexit.register(lambda: file.unlink(missing_ok=True))

    return file
