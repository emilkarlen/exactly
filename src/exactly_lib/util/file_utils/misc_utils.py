import os
import pathlib
from contextlib import contextmanager
from stat import S_IREAD, S_IRGRP, S_IROTH
from typing import List, ContextManager, IO

from exactly_lib.util import exception


@contextmanager
def open_and_make_read_only_on_close(filename: str, mode: str) -> ContextManager[IO]:
    with open(filename, mode=mode) as f:
        yield f
    make_file_read_only(filename)


@contextmanager
def open_and_make_read_only_on_close__p(path: pathlib.Path, mode: str) -> ContextManager[IO]:
    with path.open(mode=mode) as f:
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


def lines_of(file_path: pathlib.Path) -> List[str]:
    with file_path.open() as f:
        return f.readlines()


def contents_of(file_path: pathlib.Path) -> str:
    with file_path.open() as f:
        return f.read()


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
