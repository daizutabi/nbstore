from __future__ import annotations

import atexit
import base64
import re
import tempfile
from pathlib import Path

BASE64_PATTERN = re.compile(r"\{data:image/(?P<ext>.*?);base64,(?P<b64>.*?)\}")


def convert(text: str) -> str:
    return BASE64_PATTERN.sub(replace, text)


def replace(match: re.Match) -> str:
    ext = match.group("ext")
    data = base64.b64decode(match.group("b64"))

    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        tmp.write(data)
        path = Path(tmp.name)

    atexit.register(lambda p=path: p.unlink(missing_ok=True))

    return f"{{{path.absolute()}}}"
