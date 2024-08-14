from pathlib import Path
from uuid import uuid4

from core.settings import config


def write_file(filename: str, content: bytes) -> str:
    file_name = Path(filename)
    new_file_name = f"{file_name.stem}{str(uuid4())}{file_name.suffix}"
    file_path = config.MEDIA_DIR / new_file_name
    file_path.write_bytes(content)
    return str(new_file_name)
