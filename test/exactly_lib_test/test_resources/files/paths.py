import pathlib
import sys


def non_existing_absolute_path(absolute_posix_path: str) -> pathlib.PurePath:
    if sys.platform == 'win32':
        return pathlib.PurePath('c:' + absolute_posix_path)
    else:
        return pathlib.PurePath(absolute_posix_path)
