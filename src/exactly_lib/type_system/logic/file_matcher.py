import pathlib
from typing import Iterator

from exactly_lib.type_system.logic.matcher_base_class import Matcher


class FileMatcher(Matcher[pathlib.Path]):
    """Matches a path of an existing file."""

    def matches(self, path: pathlib.Path) -> bool:
        """
        :param path: The path of an existing file (but may be a broken symbolic link).
        """
        raise NotImplementedError('abstract method')


def matching_files_in_dir(matcher: FileMatcher, dir_path: pathlib.Path) -> Iterator[pathlib.Path]:
    """
    :return: Iterator of :class:`pathlib.Path`
    """
    return filter(matcher.matches, dir_path.iterdir())
