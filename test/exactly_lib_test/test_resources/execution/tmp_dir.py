import os
import pathlib
import tempfile
from contextlib import contextmanager

from exactly_lib.util.file_utils import resolved_path, preserved_cwd
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents, FileSystemElement


@contextmanager
def tmp_dir(contents: DirContents = empty_dir_contents()) -> pathlib.Path:
    with tempfile.TemporaryDirectory() as dir_name:
        dir_path = resolved_path(dir_name)
        contents.write_to(dir_path)
        yield dir_path


@contextmanager
def tmp_dir_as_cwd(contents: DirContents = empty_dir_contents()) -> pathlib.Path:
    with tempfile.TemporaryDirectory() as dir_name:
        with preserved_cwd():
            dir_path = resolved_path(dir_name)
            os.chdir(str(dir_path))
            contents.write_to(dir_path)
            yield dir_path


def tmp_dir_with(file_element: FileSystemElement) -> pathlib.Path:
    return tmp_dir(DirContents([file_element]))
