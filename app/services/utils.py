from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from core.settings import settings


def remove_old_file(file_url: str) -> None:
    file_name = urlsplit(file_url).path.split("/")[-1]
    file_path = settings.MEDIA_DIR / file_name
    if file_path.exists():
        file_path.unlink()


def generate_file_name(file_name: Path) -> str:
    new_file_name = f"{file_name.stem}{str(uuid4())}{file_name.suffix}"
    return new_file_name


def write_file(file_name: str, content: bytes) -> None:
    file_path = settings.MEDIA_DIR / file_name
    file_path.write_bytes(content)
