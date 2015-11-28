"""
File services designed to meet the needs of instruction implementations.

For example. Exceptions that are adapted to the instruction infrastructure is thrown, rather than
Python built-in exceptions, in cases when the built-in exceptions are "meaningful".
"""
import pathlib

from shellcheck_lib.general import exception


def create_dir_that_is_expected_to_not_exist(dir_path: pathlib.Path):
    try:
        dir_path.mkdir(parents=True)
    except OSError as ex:
        msg = str(ex)
        raise exception.ImplementationError(msg)
