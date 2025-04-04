from __future__ import annotations

import atexit
import base64
import os
import tempfile
from pathlib import Path


def create_image_file(
    data: dict[str, str],
    dir: Path | str | None = None,
    *,
    delete: bool = True,
) -> str | None:
    if text := data.get("application/pdf"):
        return create_image_file_base64(text, ".pdf", dir, delete=delete)

    for mime, text in data.items():
        if mime.startswith("image/"):
            ext = mime.split("/")[1]
            return create_image_file_base64(text, f".{ext}", dir, delete=delete)

    return None


def create_image_file_base64(
    text: str,
    suffix: str,
    dir: Path | str | None = None,
    *,
    delete: bool = True,
) -> str:
    data = base64.b64decode(text)
    path = create_temp_file(data, suffix, dir, delete=delete)
    return path.as_posix()


def create_temp_file(
    data: bytes,
    suffix: str | None = None,
    dir: str | Path | None = None,
    *,
    delete: bool = True,
) -> Path:
    fd, filename = tempfile.mkstemp(suffix, dir=dir, text=False)

    path = Path(filename)
    path.write_bytes(data)

    os.close(fd)

    if delete:
        atexit.register(lambda: path.unlink(missing_ok=True))

    return path
