from __future__ import annotations

import atexit
import base64
import re
import uuid
from pathlib import Path

BASE64_PATTERN = re.compile(r"\{data:image/(?P<ext>.*?);base64,(?P<b64>.*)\}")


def convert(text: str) -> str:
    return BASE64_PATTERN.sub(replace, text)


def replace(match: re.Match) -> str:
    filename = f"{uuid.uuid4()}.{match.group('ext')}"
    data = base64.b64decode(match.group("b64"))
    path = Path(filename)
    path.write_bytes(data)
    atexit.register(lambda: path.unlink(missing_ok=True))
    return f"{{{filename}}}"
