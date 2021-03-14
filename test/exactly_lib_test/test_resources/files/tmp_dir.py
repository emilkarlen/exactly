import os
import pathlib
import shutil
import stat
import tempfile
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib import program_info
from exactly_lib.util.file_utils.misc_utils import resolved_path, preserved_cwd
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents, FileSystemElement


@contextmanager
def temp_dir(prefix: str = program_info.PROGRAM_NAME) -> ContextManager[pathlib.Path]:
    dir_str = tempfile.mkdtemp(prefix=prefix)
    yield resolved_path(dir_str)
    shutil.rmtree(dir_str, onerror=_onerror_mk_read_write_and_retry)


@contextmanager
def tmp_dir(contents: DirContents = empty_dir_contents()) -> ContextManager[pathlib.Path]:
    with temp_dir() as dir_path:
        contents.write_to(dir_path)
        yield dir_path


@contextmanager
def tmp_dir_as_cwd(contents: DirContents = empty_dir_contents()) -> ContextManager[pathlib.Path]:
    with temp_dir() as dir_path:
        with preserved_cwd():
            os.chdir(str(dir_path))
            contents.write_to(dir_path)
            yield dir_path


def tmp_dir_with(file_element: FileSystemElement) -> ContextManager[pathlib.Path]:
    return tmp_dir(DirContents([file_element]))


def _onerror_mk_read_write_and_retry(func, path, *args):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise RuntimeError('Failed to remove path ' + path)
