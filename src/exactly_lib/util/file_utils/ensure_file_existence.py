import pathlib
from typing import Optional

from exactly_lib.util import exception


def ensure_directory_exists(dir_path: pathlib.Path):
    dir_path.mkdir(parents=True, exist_ok=True)


def ensure_directory_exists_as_a_directory(dir_path: pathlib.Path) -> Optional[str]:
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


def ensure_directory_exists_as_a_directory__impl_error(dir_path: pathlib.Path):
    """
    :raises exception.ImplementationError: If path cannot be ensured to exist as dir.
    """
    err_msg = ensure_directory_exists_as_a_directory(dir_path)
    if err_msg:
        raise exception.ImplementationError(err_msg)
