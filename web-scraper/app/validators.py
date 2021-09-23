from pathlib import Path

from click import BadParameter


def check_if_positive(value: int) -> int:
    if value <= 0:
        raise BadParameter('must be positive')
    return value


def check_directory(value: str) -> Path:
    path_to_dir = Path(value)
    if path_to_dir.exists():
        if path_to_dir.is_dir() and any(path_to_dir.iterdir()):
            raise BadParameter('specified directory is not empty')
        if not path_to_dir.is_dir():
            raise BadParameter('specified path is not a directory')
    else:
        path_to_dir.mkdir()
    return path_to_dir
