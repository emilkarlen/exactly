from contextlib import contextmanager
import pathlib
import tempfile

from shellcheck_lib_test.util.file_structure import DirContents, empty_dir_contents, FileSystemElement


@contextmanager
def tmp_dir(contents: DirContents=empty_dir_contents()) -> pathlib.Path:
    with tempfile.TemporaryDirectory() as dir_name:
        dir_path = pathlib.Path(dir_name)
        contents.write_to(dir_path)
        yield dir_path


def tmp_dir_with(file_element: FileSystemElement) -> pathlib.Path:
    return tmp_dir(DirContents([file_element]))
