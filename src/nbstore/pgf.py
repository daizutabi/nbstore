from __future__ import annotations

import atexit
import base64
import shutil
import tempfile
from pathlib import Path

from .formatter import RASTER_BEGIN, RASTER_END


def split(text: str) -> tuple[str, dict[str, str]]:
    if not text.endswith(RASTER_END):
        return text, {}

    text, image = text.split(f"\n{RASTER_BEGIN}\n", maxsplit=1)
    images = image.splitlines()[:-1]

    image_dict = {}
    for image in images:
        name, imagetext = image.split(":", maxsplit=1)
        image_dict[name] = imagetext

    return text, image_dict


def convert(text: str) -> str:
    text, images = split(text)
    if not images:
        return text

    name, _ = next(iter(images.keys())).rsplit("-img", maxsplit=1)
    tempdir = create_temp_dir()
    text = text.replace(name, f"{tempdir.as_posix()}/{name}")

    for name, imagetext in images.items():
        data = base64.b64decode(imagetext)
        path = tempdir / name
        path.write_bytes(data)

    return text


def create_temp_dir() -> Path:
    dirname = tempfile.mkdtemp()
    path = Path(dirname)
    atexit.register(lambda: shutil.rmtree(path))
    return path
