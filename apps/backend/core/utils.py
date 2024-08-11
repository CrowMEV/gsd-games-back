from pathlib import Path
from uuid import uuid4

from backend.core.settings import config


def write_file(filename: str, content: bytes) -> str:
    file_name = Path(filename)
    file_path = (
        config.MEDIA_DIR / f"{file_name.stem}{str(uuid4())}{file_name.suffix}"
    )
    file_path.write_bytes(content)
    return str(file_path)
