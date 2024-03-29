import os
import pathlib
from contextlib import contextmanager
from stat import S_IREAD, S_IRGRP, S_IROTH
from typing import ContextManager, TextIO, List

from exactly_lib.util import exception


@contextmanager
def open_and_make_read_only_on_close__text(path: pathlib.Path, text_mode: str) -> ContextManager[TextIO]:
    with path.open(mode=text_mode) as f:
        yield f
    make_file_read_only__p(path)


def make_file_read_only(path: str):
    os.chmod(path, S_IREAD | S_IRGRP | S_IROTH)


def make_file_read_only__p(path: pathlib.Path):
    path.chmod(S_IREAD | S_IRGRP | S_IROTH)


def resolved_path(existing_path: str) -> pathlib.Path:
    return pathlib.Path(existing_path).resolve()


def resolved_path_name(existing_path: str) -> str:
    return str(resolved_path(existing_path))


def write_new_text_file(file_path: pathlib.Path,
                        contents: str):
    """
    Fails if the file already exists.
    """
    with file_path.open('x') as f:
        f.write(contents)


def contents_of(file_path: pathlib.Path) -> str:
    with file_path.open() as f:
        return f.read()


class LinesReader:
    def __init__(self, path: pathlib.Path):
        self._path = path

    def read(self) -> List[str]:
        with self._path.open() as f:
            return list(f.readlines())


@contextmanager
def preserved_cwd():
    cwd_to_preserve = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd_to_preserve)


def create_dir_that_is_expected_to_not_exist__impl_error(dir_path: pathlib.Path):
    """
    :raises exception.ImplementationError: In case of OS error.
    """
    try:
        dir_path.mkdir(parents=True)
    except OSError as ex:
        msg = str(ex)
        raise exception.ImplementationError(msg)
