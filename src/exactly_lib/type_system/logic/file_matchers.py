import pathlib
from typing import Iterator

from exactly_lib.type_system.logic.file_matcher import FileMatcher


def matching_files_in_dir(matcher: FileMatcher, dir_path: pathlib.Path) -> Iterator[pathlib.Path]:
    """
    :return: Iterator of :class:`pathlib.Path`
    """
    return filter(matcher.matches, dir_path.iterdir())
