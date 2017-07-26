"""
File services designed to meet the needs of instruction implementations.

For example. Exceptions that are adapted to the instruction infrastructure is thrown, rather than
Python built-in exceptions, in cases when the built-in exceptions are "meaningful".
"""
import pathlib

from exactly_lib.util import exception
from exactly_lib.util import file_utils


def create_dir_that_is_expected_to_not_exist(dir_path: pathlib.Path):
    try:
        dir_path.mkdir(parents=True)
    except OSError as ex:
        msg = str(ex)
        raise exception.ImplementationError(msg)


def ensure_directory_exists_as_a_directory(dir_path: pathlib.Path):
    """
    :raises exception.ImplementationError: If path cannot be ensured to exist as dir.
    """
    err_msg = file_utils.ensure_directory_exists_as_a_directory(dir_path)
    if err_msg:
        raise exception.ImplementationError(err_msg)
