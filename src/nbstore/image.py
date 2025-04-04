from __future__ import annotations

import atexit
import base64
from pathlib import Path


def decode(data: dict[str, str]) -> tuple[str, str | bytes] | None:
    if text := data.get("application/pdf"):
        return ".pdf", base64.b64decode(text)

    for mime, text in data.items():
        if mime.startswith("image/"):
            ext = mime.split("/")[1]
            return f".{ext}", base64.b64decode(text)

    return None


def create_image_file(
    data: dict[str, str],
    filename: Path | str,
    *,
    delete: bool = False,
) -> Path | None:
    decoded = decode(data)

    if decoded is None:
        return None

    suffix, content = decoded
    file = Path(filename).with_suffix(suffix)

    if isinstance(content, str):
        file.write_text(content)
    else:
        file.write_bytes(content)

    if delete:
        atexit.register(lambda: file.unlink(missing_ok=True))

    return file
