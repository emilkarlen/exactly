import os
import pathlib
import tempfile
from contextlib import contextmanager
from stat import S_IREAD, S_IRGRP, S_IROTH
from typing import List

from exactly_lib.util import exception


@contextmanager
def open_and_make_read_only_on_close(filename: str, mode: str):
    f = open(filename, mode=mode)
    yield f
    f.close()
    make_file_read_only(filename)


def make_file_read_only(path: str):
    os.chmod(path, S_IREAD | S_IRGRP | S_IROTH)


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


def ensure_directory_exists(dir_path: pathlib.Path):
    if not dir_path.exists():
        dir_path.mkdir(parents=True)


def ensure_directory_exists_as_a_directory(dir_path: pathlib.Path) -> str:
    """
    :return: Failure message if cannot ensure, otherwise None.
    """
    try:
        ensure_directory_exists(dir_path)
    except NotADirectoryError as ex:
        return 'Not a directory: {}'.format(dir_path)
    except FileExistsError:
        return 'Part of path exists, but perhaps one in-the-middle-component is not a directory: %s' % str(dir_path)


def ensure_parent_directory_does_exist(dst_file_path: pathlib.Path):
    ensure_directory_exists(dst_file_path.parent)


def ensure_parent_directory_does_exist_and_is_a_directory(dst_file_path: pathlib.Path) -> str:
    """
    :return: Failure message if cannot ensure, otherwise None.
    """
    return ensure_directory_exists_as_a_directory(dst_file_path.parent)


def lines_of(file_path: pathlib.Path) -> List[str]:
    with file_path.open() as f:
        return f.readlines()


def contents_of(file_path: pathlib.Path) -> str:
    with file_path.open() as f:
        return f.read()


def tmp_text_file_containing(contents: str,
                             prefix: str = '',
                             suffix: str = '',
                             directory=None) -> pathlib.Path:
    fd, absolute_file_path = tempfile.mkstemp(prefix=prefix,
                                              suffix=suffix,
                                              dir=directory,
                                              text=True)
    fo = os.fdopen(fd, 'w+')
    fo.write(contents)
    fo.close()
    return pathlib.Path(absolute_file_path)


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


def ensure_directory_exists_as_a_directory__impl_error(dir_path: pathlib.Path):
    """
    :raises exception.ImplementationError: If path cannot be ensured to exist as dir.
    """
    err_msg = ensure_directory_exists_as_a_directory(dir_path)
    if err_msg:
        raise exception.ImplementationError(err_msg)
