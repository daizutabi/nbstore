from __future__ import annotations

import atexit
import base64
from pathlib import Path


def create_image_file(
    data: dict[str, str],
    filename: Path | str,
    *,
    delete: bool = False,
) -> Path | None:
    file = None

    if text := data.get("application/pdf"):
        file = Path(filename).with_suffix(".pdf")
        file.write_bytes(base64.b64decode(text))

    else:
        for mime, text in data.items():
            if mime.startswith("image/"):
                ext = mime.split("/")[1]
                file = Path(filename).with_suffix(f".{ext}")
                file.write_bytes(base64.b64decode(text))

    if file and delete:
        atexit.register(lambda: file.unlink(missing_ok=True))

    return file
