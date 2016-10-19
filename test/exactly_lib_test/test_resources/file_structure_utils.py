import os
import pathlib
import tempfile
from contextlib import contextmanager

from exactly_lib.util.file_utils import resolved_path
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents, FileSystemElement


@contextmanager
def tmp_dir(contents: DirContents = empty_dir_contents()) -> pathlib.Path:
    with tempfile.TemporaryDirectory() as dir_name:
        dir_path = resolved_path(dir_name)
        contents.write_to(dir_path)
        yield dir_path


@contextmanager
def tmp_dir_as_cwd(contents: DirContents = empty_dir_contents()) -> pathlib.Path:
    with preserved_cwd():
        with tempfile.TemporaryDirectory() as dir_name:
            dir_path = resolved_path(dir_name)
            contents.write_to(dir_path)
            os.chdir(str(dir_path))
            yield dir_path
        finally:
            os.chdir(original_cwd)


def tmp_dir_with(file_element: FileSystemElement) -> pathlib.Path:
    return tmp_dir(DirContents([file_element]))


@contextmanager
def preserved_cwd():
    cwd_to_preserve = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd_to_preserve)
