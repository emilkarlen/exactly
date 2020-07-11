import os
import pathlib
import sys
import tempfile
from contextlib import contextmanager
from typing import Sequence

from exactly_lib import program_info
from exactly_lib.util.file_utils.misc_utils import resolved_path
from exactly_lib.util.str_.misc_formatting import lines_content


def write_file(path: pathlib.Path, contents: str):
    with open(str(path), 'w') as f:
        f.write(contents)


@contextmanager
def absolute_path_to_executable_file() -> pathlib.Path:
    yield sys.executable


@contextmanager
def tmp_file_containing(contents: str,
                        suffix: str = '',
                        directory=None) -> pathlib.Path:
    """
    Returns a context manager (used by with tmp_file(...) as file_path) ...
    The context manager takes care of deleting the file.

    :param contents: The contents of the returned file.
    :param suffix: A possible suffix of the file name (a dot does not automatically separate stem, suffix).
    :return: File path of a closed text file with the given contents.
    """
    path = None
    try:
        fd, absolute_file_path = tempfile.mkstemp(prefix=program_info.PROGRAM_NAME + '-test-',
                                                  suffix=suffix,
                                                  dir=directory,
                                                  text=True)
        fo = os.fdopen(fd, 'w+')
        fo.write(contents)
        fo.close()
        path = resolved_path(absolute_file_path)
        yield path
    finally:
        if path:
            path.unlink()


def tmp_file_containing_lines(content_lines: Sequence[str],
                              suffix: str = '') -> pathlib.Path:
    """
    Short cut to tmp_file_containing combined with giving the contents as a string of lines.
    """
    return tmp_file_containing(lines_content(content_lines),
                               suffix=suffix)


def contents_of_file(path: pathlib.Path) -> str:
    with path.open() as f:
        return f.read()


class NullFile(object):
    def write(self, *args, **kwargs):
        return 0

    def flush(self):
        pass


NULL_FILE = NullFile()
