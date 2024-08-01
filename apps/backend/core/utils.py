from pathlib import Path


def create_dir(path: Path) -> Path:
    path.mkdir(exist_ok=True)
    return path
